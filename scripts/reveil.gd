extends Node
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## Le réveil dans le berceau et la mort de batterie.
## - Premier réveil (une fois) : cinématique lente, ~24 s, sans contrôle.
## - Après chaque mort : réveil court (~6 s), dans un corps neuf.
## - Mort : batterie vide -> le robot s'effondre sur place ; son corps reste là (l'« ancien corps »).
## Clips du robot (assets/models/robot_meshy.glb) : dormir, reveil, se_lever, regarder_autour, effondrement.
## Entrée : passe le réveil en cours (long ou court) et rend la main tout de suite.

@export var joueur: CharacterBody3D
## Décoché : on saute directement au réveil court (pour tester).
@export var premier_reveil: bool = true
## Seuil de batterie sous lequel le robot s'éteint.
@export var seuil_mort: float = 0.03
## Batterie à la fin du premier réveil : l'antenne est presque vide, il faut aller à la pierre-soleil.
@export var batterie_premier_reveil: float = 0.15
## La batterie ne remonte plus toute seule : seulement à la pierre-soleil (et plus tard à la lumière).
@export var sans_recharge_passive: bool = true
@export_group("Rythme")
@export var vitesse_se_lever: float = 1.3
@export var vitesse_se_lever_court: float = 1.8
@export var duree_regarder: float = 4.5

## Entre la fin de « reveil » et le début de « se_lever », le corps est décalé dans les clips Meshy :
## on décale le modèle d'autant vers ses pieds pendant « se_lever » (mesuré dans Blender, en m).
const DECALAGE_SE_LEVER := 0.44
## Centre du corps couché (repère du modèle, +Z = vers les pieds).
const CENTRE_COUCHE := -0.17

var morts: int = 0
var _en_cours: bool = false
## Réveil en cours : "long", "court" ou "" ; `_seq` change quand on le passe (les étapes en attente s'arrêtent).
var _reveil: String = ""
var _seq: int = 0
var _tweens: Array[Tween] = []
var _lueur_max: float = 0.0
var _noir: ColorRect
var _robot: Node3D
var _couche: Node3D
var _tete: Node3D
var _porte: Node3D
var _lueur: OmniLight3D


func _ready() -> void:
	var calque := CanvasLayer.new()
	calque.layer = 20
	add_child(calque)
	_noir = ColorRect.new()
	_noir.color = Color.BLACK
	_noir.set_anchors_preset(Control.PRESET_FULL_RECT)
	_noir.mouse_filter = Control.MOUSE_FILTER_IGNORE
	calque.add_child(_noir)
	# l'île se construit dans son _ready : on attend qu'abri et berceau existent
	await get_tree().process_frame
	await get_tree().process_frame
	if joueur == null:
		joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	var abri := get_tree().get_first_node_in_group("abri") as Node3D
	if joueur == null or abri == null:
		push_warning("reveil.gd : joueur ou abri introuvable")
		_noir.visible = false
		return
	_robot = joueur.get("modele") as Node3D
	if sans_recharge_passive:
		joueur.set("recharge", 0.0)
	_couche = abri.find_child("Couche", true, false) as Node3D
	_tete = abri.find_child("Tete", true, false) as Node3D
	_porte = abri.find_child("Porte", true, false) as Node3D
	_lueur = abri.find_child("LueurBerceau", true, false) as OmniLight3D
	if _lueur:
		_lueur_max = _lueur.light_energy
	if _couche == null or _tete == null:
		push_warning("reveil.gd : repères du berceau introuvables")
		_noir.visible = false
		return
	if premier_reveil:
		_reveil_long()
	else:
		_reveil_court()


func _unhandled_input(event: InputEvent) -> void:
	if _reveil == "" or not (event is InputEventKey):
		return
	var k := event as InputEventKey
	if k.pressed and not k.echo and (k.physical_keycode == KEY_ENTER or k.physical_keycode == KEY_KP_ENTER):
		get_viewport().set_input_as_handled()
		_passer()


func _physics_process(_delta: float) -> void:
	if _en_cours or joueur == null or _couche == null:
		return
	var b: float = joueur.get("batterie")
	if b <= seuil_mort:
		_mourir()


# ---------------------------------------------------------------- outils

## Couche le robot dans le berceau : tête vers la tête du berceau, origine sur le matelas.
func _coucher() -> void:
	var vers_pieds: Vector3 = _couche.global_position - _tete.global_position
	vers_pieds.y = 0.0
	vers_pieds = vers_pieds.normalized()
	joueur.velocity = Vector3.ZERO
	joueur.global_position = _couche.global_position - vers_pieds * CENTRE_COUCHE
	_robot.rotation.y = atan2(vers_pieds.x, vers_pieds.z)
	_robot.position = Vector3.ZERO
	joueur.set("regard_cible", joueur.global_position + vers_pieds * 5.0)
	joueur.set("batterie", 1.0)


func _vers_pieds() -> Vector3:
	return _robot.global_basis.z.normalized()


## Plan rapproché du berceau, côté porte, un peu en hauteur.
func _plan_berceau(recul: float, hauteur: float) -> void:
	var cible: Vector3 = _couche.global_position + Vector3.UP * 0.35
	var dehors: Vector3 = Vector3.FORWARD
	if _porte:
		dehors = _porte.global_position - _couche.global_position
		dehors.y = 0.0
		dehors = dehors.normalized()
	var cote: Vector3 = dehors.cross(Vector3.UP).normalized()
	joueur.set("cine_cible", cible)
	joueur.set("cine_position", cible + dehors * recul + cote * recul * 0.35 + Vector3.UP * hauteur)


## Tween suivi : il sera arrêté si on passe le réveil.
func _tw() -> Tween:
	var t := create_tween()
	_tweens.append(t)
	return t


func _attendre(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _fondu_noir(alpha: float, duree: float) -> void:
	_noir.visible = true
	var id := _seq
	var t := _tw()
	t.tween_property(_noir, "color:a", alpha, duree)
	await t.finished
	if id == _seq and alpha <= 0.0:
		_noir.visible = false


func _action(nom: String, vitesse: float = 1.0, fondu: float = 0.3) -> void:
	_robot.call("jouer_action", nom, vitesse, fondu)


func _duree(nom: String) -> float:
	var d: float = _robot.call("duree", nom)
	return d


## « se_lever » : le modèle est décalé pendant le clip, puis le joueur avance d'autant à la fin.
func _se_lever(vitesse: float) -> void:
	var avant: Vector3 = _vers_pieds() * DECALAGE_SE_LEVER
	_robot.position = joueur.global_basis.inverse() * avant
	_action("se_lever", vitesse, 0.0)
	var id := _seq
	await _attendre(_duree("se_lever") / vitesse)
	if id != _seq:
		return
	joueur.global_position += avant
	_robot.position = Vector3.ZERO


## Antenne qui grésille avant de s'allumer (la batterie revient).
func _gresiller(fois: int) -> void:
	var id := _seq
	for i in fois:
		joueur.set("antenne_allumee", true)
		await _attendre(0.12 + 0.08 * i)
		if id != _seq:
			return
		joueur.set("antenne_allumee", false)
		await _attendre(0.35 - 0.05 * i)
		if id != _seq:
			return
	joueur.set("antenne_allumee", true)


# ---------------------------------------------------------------- le premier réveil

func _reveil_long() -> void:
	_en_cours = true
	_reveil = "long"
	var id := _seq
	joueur.set("cinematique", true)
	joueur.set("antenne_allumee", false)
	_coucher()
	_action("dormir", 1.0, 0.0)
	_plan_berceau(2.4, 1.6)
	joueur.set("cine_melange", 1.0)
	if _lueur:
		_lueur.light_energy = 0.0
	_noir.color.a = 1.0
	await _attendre(1.5)
	if id != _seq: return
	# 1) noir -> le robot couché, immobile
	await _fondu_noir(0.0, 2.5)
	if id != _seq: return
	await _attendre(1.5)
	if id != _seq: return
	# 2) l'antenne grésille, puis la lampe du berceau s'allume doucement
	await _gresiller(3)
	if id != _seq: return
	if _lueur:
		_tw().tween_property(_lueur, "light_energy", _lueur_max, 2.0)
	await _attendre(1.2)
	if id != _seq: return
	# 3) il se redresse un peu et lève la tête
	_action("reveil", 1.0, 0.6)
	await _attendre(_duree("reveil") - 0.3)
	if id != _seq: return
	# 4) il se lève en titubant ; la caméra recule un peu
	var recul := _tw().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	recul.tween_method(func(t: float) -> void: _plan_berceau(lerpf(2.4, 3.4, t), lerpf(1.6, 2.2, t)), 0.0, 1.0, 5.0)
	await _se_lever(vitesse_se_lever)
	if id != _seq: return
	# 5) il sort du berceau par l'encoche, vers la porte
	_robot.call("fin_action")
	var sortie: Vector3 = _sortie()
	joueur.set("regard_cible", sortie + (sortie - joueur.global_position) * 3.0)
	var pas := _tw().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pas.tween_property(joueur, "global_position", sortie, 1.8)
	await pas.finished
	if id != _seq: return
	# 6) il regarde autour de lui ; la caméra remonte en vue de dessus, on prend la main
	_action("regarder_autour", 1.0, 0.4)
	await _attendre(duree_regarder * 0.5)
	if id != _seq: return
	_tw().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT).tween_property(joueur, "cine_melange", 0.0, 2.5)
	await _attendre(duree_regarder * 0.5)
	if id != _seq: return
	_finir_long()


## Fin du premier réveil (normale ou passée) : on rend la main, l'antenne se vide.
func _finir_long() -> void:
	_robot.call("fin_action")
	joueur.set("cinematique", false)
	_en_cours = false
	_reveil = ""
	# l'antenne est presque vide : elle grésille, le cristal de la pierre-soleil appelle
	create_tween().tween_property(joueur, "batterie", batterie_premier_reveil, 2.0)


## Juste devant le berceau, côté porte (là où le robot finit le premier réveil).
func _sortie() -> Vector3:
	if _porte == null:
		return joueur.global_position
	var dehors: Vector3 = _porte.global_position - _couche.global_position
	dehors.y = 0.0
	var sortie: Vector3 = _couche.global_position + dehors.normalized() * 1.25
	sortie.y = _porte.global_position.y
	return sortie


## Entrée pendant un réveil : tout s'arrête, le robot est debout, on a la main.
func _passer() -> void:
	var type := _reveil
	_seq += 1
	for t in _tweens:
		if t and t.is_valid():
			t.kill()
	_tweens.clear()
	_noir.color.a = 0.0
	_noir.visible = false
	_robot.position = Vector3.ZERO
	if _lueur:
		_lueur.light_energy = _lueur_max
	joueur.set("antenne_allumee", true)
	joueur.set("cine_melange", 0.0)
	joueur.velocity = Vector3.ZERO
	var dehors: Vector3 = Vector3.BACK
	if _porte:
		dehors = _porte.global_position - _couche.global_position
	dehors.y = 0.0
	dehors = dehors.normalized()
	if type == "long":
		joueur.global_position = _sortie() + Vector3.UP * 0.1
	else:
		joueur.global_position = _couche.global_position + Vector3.UP * 0.1
	_robot.rotation.y = atan2(dehors.x, dehors.z)
	joueur.set("regard_cible", joueur.global_position + dehors * 5.0)
	if type == "long":
		_finir_long()
	else:
		_finir_court()


# ---------------------------------------------------------------- les réveils suivants

func _reveil_court() -> void:
	_en_cours = true
	_reveil = "court"
	var id := _seq
	joueur.set("cinematique", true)
	joueur.set("antenne_allumee", false)
	_coucher()
	_action("dormir", 1.0, 0.0)
	_plan_berceau(2.8, 1.9)
	joueur.set("cine_melange", 1.0)
	_noir.color.a = 1.0
	await _fondu_noir(0.0, 0.8)
	if id != _seq: return
	joueur.set("antenne_allumee", true)   # d'un coup, sans grésiller
	await _attendre(0.4)
	if id != _seq: return
	var retour := _tw().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_interval(_duree("se_lever") / vitesse_se_lever_court * 0.6)
	retour.tween_property(joueur, "cine_melange", 0.0, 1.5)
	await _se_lever(vitesse_se_lever_court)
	if id != _seq: return
	_finir_court()


func _finir_court() -> void:
	_robot.call("fin_action")
	joueur.set("cinematique", false)
	_en_cours = false
	_reveil = ""


# ---------------------------------------------------------------- la mort

func _mourir() -> void:
	_en_cours = true
	morts += 1
	joueur.set("cinematique", true)
	joueur.set("antenne_allumee", false)   # l'ampoule s'éteint
	joueur.velocity = Vector3.ZERO
	_action("effondrement", 1.0, 0.3)
	SONS.jouer("extinction", joueur.global_position)
	var d: float = _duree("effondrement")
	await _attendre(d * 0.85)
	# le corps reste là, dans la pose où il est tombé
	_laisser_corps()
	await _fondu_noir(1.0, 1.2)
	# les lanternes allumées avec cette batterie s'éteignent : l'île se rendort
	for l in get_tree().get_nodes_in_group("lanternes"):
		if l.has_method("eteindre"):
			l.call("eteindre")
	# la barque revient au port d'attache, toujours à flot (ILE_01_REVEIL.md §13.2)
	for b in get_tree().get_nodes_in_group("barque_qui_flotte"):
		if b.has_method("revenir_au_port"):
			b.call("revenir_au_port")
	await _attendre(0.8)
	_robot.call("fin_action")
	_reveil_court()


func _laisser_corps() -> void:
	var scene := load(_robot.scene_file_path) as PackedScene
	if scene == null:
		return
	var corps: Node3D = scene.instantiate()
	corps.name = "AncienCorps%d" % morts
	corps.add_to_group("anciens_corps")
	get_tree().current_scene.add_child(corps)
	corps.global_transform = _robot.global_transform
	var anim := corps.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if anim and anim.has_animation("effondrement"):
		anim.play("effondrement")
		anim.seek(anim.get_animation("effondrement").length, true)
		anim.pause()
