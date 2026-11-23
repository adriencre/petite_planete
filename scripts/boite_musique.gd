extends Node3D
## La boîte à musique d'Aube (ILE_03_COLONIE.md) : sa prise est au pied du bureau, reliée à la boîte par
## un cordon de cuivre. Le robot s'agenouille et y branche son câble, comme pour une lanterne. La boîte
## joue le thème d'Aube ; la caméra se pose sur la chambre et la lanterne de chevet s'éclaire doucement
## sous son tissu. Un moment d'émotion, sans conséquence de jeu. E pendant la musique : il débranche.
## Ce nœud est posé sur la prise, son axe +Z tourné vers la chambre.

const SONS := preload("res://scripts/sons.gd")
const CABLE := preload("res://scripts/cable.gd")

## Le thème d'Aube (provisoire : tools/audio/theme_aube.py).
@export var theme: AudioStream
## La lanterne de chevet recouverte d'un tissu : une lumière chaude s'y allume pendant la musique.
@export var lanterne: Node3D
## Le centre de la chambre, que la caméra regarde pendant la musique.
@export var centre_chambre: Node3D
@export var distance_activation: float = 1.7
@export var energie_lanterne: float = 1.1
@export var couleur_lanterne: Color = Color(1.0, 0.68, 0.55)

## Distance entre la prise et les pieds du robot dans le geste « brancher » (lanterne_fleur.gd).
const RECUL_GENOU := 0.62
const INSTANT_FICHE := 0.93
const INSTANT_BRAS_LEVES := 0.6

var ecoutee: bool = false
var _joueur: CharacterBody3D
var _en_cours: bool = false
var _arret_demande: bool = false
var _cable
var _fiche_posee: bool = false
var _retrait: float = -1.0
var _lumiere := OmniLight3D.new()
var _son := AudioStreamPlayer3D.new()


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	ecoutee = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("ecoutee", false))
	_cable = CABLE.new()
	_cable.visible = false
	add_child(_cable)
	_lumiere.light_color = couleur_lanterne
	_lumiere.light_energy = 0.0
	_lumiere.omni_range = 3.2
	_lumiere.shadow_enabled = true
	add_child(_lumiere)
	_son.stream = theme
	_son.bus = &"Musique"
	_son.unit_size = 6.0
	add_child(_son)
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if lanterne:
		_lumiere.global_position = lanterne.global_position + Vector3.UP * 0.1


func cle_sauvegarde() -> String:
	return "boite_musique:" + str(name)


func sauver() -> Dictionary:
	return {"ecoutee": ecoutee}


## Pour guidage.gd : 2 = E possible, 1 = à découvrir, 0 = rien.
func etat_interaction() -> int:
	if _joueur == null or _en_cours or bool(_joueur.get("cinematique")):
		return 0
	if _a_portee():
		return 2
	return 0 if ecoutee else 1


func point_appel() -> Vector3:
	return global_position + Vector3.UP * 0.6


func _a_portee() -> bool:
	var a := _joueur.global_position
	var p := global_position
	var d := Vector2(a.x - p.x, a.z - p.z).length()
	if d >= distance_activation or absf(a.y - p.y) >= 1.2:
		return false
	# le carnet d'Aube est posé sur le même bureau : la plus proche des deux répond à E
	for page in get_tree().get_nodes_in_group("pages_lisibles"):
		var dp: float = float(page.call("_distance"))
		if dp < d and dp < float(page.get("distance_lecture")):
			return false
	return true


func _normale() -> Vector3:
	var n := global_basis.z
	n.y = 0.0
	return n.normalized()


func _process(_delta: float) -> void:
	if _joueur == null or not _cable.visible:
		return
	_cable.debut = _joueur.call("poignet_droit_monde")
	if _retrait >= 0.0:
		_cable.fin = global_position.lerp(_cable.debut, _retrait)
	else:
		_cable.fin = global_position if _fiche_posee else _joueur.call("bout_index_monde")


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E:
		return
	if _en_cours:
		# pendant la musique : il débranche
		if _son.playing:
			get_viewport().set_input_as_handled()
			_arret_demande = true
		return
	if bool(_joueur.get("cinematique")) or not _a_portee():
		return
	get_viewport().set_input_as_handled()
	_ecouter()


func _ecouter() -> void:
	_en_cours = true
	_arret_demande = false
	var premiere: bool = not ecoutee
	# d'abord la cinématique : en 1re personne, la caméra recule en 3e et on voit le geste
	_joueur.set("cinematique", true)
	var robot: Node = _joueur.get("modele")
	var geste: bool = bool(_joueur.call("troisieme_personne")) and robot != null and robot.has_method("jouer_action") and bool(robot.call("a_animation", "brancher"))
	var normale := _normale()
	_joueur.set("regard_cible", global_position)

	# 1) il vient se placer devant la prise
	var place: Vector3 = global_position + normale * RECUL_GENOU
	place.y = _joueur.global_position.y
	var trajet := Vector2(place.x - _joueur.global_position.x, place.z - _joueur.global_position.z).length()
	var centre: Vector3 = centre_chambre.global_position if centre_chambre else global_position + normale * 1.2 + Vector3.UP * 0.8
	# la caméra garde l'angle du jeu (vue de dessus), un peu plus près de la chambre
	var recul: Vector3 = _joueur.call("recul_cinematique", _joueur.global_position)
	# d'abord un plan de côté sur la prise, pour bien voir le geste ; la chambre viendra avec la musique
	var cible_basse: Vector3 = global_position + normale * (RECUL_GENOU * 0.5) + Vector3.UP * 0.6
	_joueur.set("cine_cible", cible_basse)
	_joueur.set("cine_position", _plan_de_cote(cible_basse, normale))
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, clampf(trajet / 1.3, 0.4, 2.5))
	approche.tween_property(_joueur, "cine_melange", 1.0, 2.2 if premiere else 1.2)
	await approche.finished
	await get_tree().create_timer(0.4, false).timeout

	# 2) il s'agenouille et branche la fiche
	var d_brancher := 1.0
	if geste:
		robot.call("jouer_action", "brancher", 1.0)
		d_brancher = float(robot.call("duree", "brancher"))
	_cable.visible = true
	_retrait = -1.0
	_cable.materiau.set_shader_parameter("flux", 0.0)
	await get_tree().create_timer(d_brancher * INSTANT_FICHE, false).timeout
	_fiche_posee = true
	SONS.jouer("clic", global_position)
	var courant := create_tween()
	courant.tween_method(func(v: float) -> void: _cable.materiau.set_shader_parameter("flux", v), 0.0, 1.0, 0.8)
	await get_tree().create_timer(d_brancher * (1.0 - INSTANT_FICHE) + 0.4, false).timeout
	if geste:
		robot.call("jouer_action", "brancher_attente", 0.6, 0.4)

	# 3) la boîte joue ; la caméra se pose sur la chambre ; la lanterne de chevet s'éclaire sous son tissu
	_son.play()
	var vers_chambre := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	vers_chambre.tween_property(_joueur, "cine_cible", centre, 2.8)
	vers_chambre.tween_property(_joueur, "cine_position", centre + recul * (5.5 if premiere else 6.5), 2.8)
	var lueur := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	lueur.tween_property(_lumiere, "light_energy", energie_lanterne, 4.0)
	while _son.playing and not _arret_demande:
		await get_tree().process_frame
	ecoutee = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	if _son.playing:
		var fin_son := create_tween()
		fin_son.tween_property(_son, "volume_db", -40.0, 1.2)
		fin_son.tween_callback(_son.stop)
		fin_son.tween_property(_son, "volume_db", 0.0, 0.0)

	# 4) il débranche ; le câble se rembobine, la lumière s'éteint lentement, la caméra revient
	var d_debrancher := 1.0
	if geste:
		robot.call("jouer_action", "debrancher", 1.0, 0.25)
		d_debrancher = float(robot.call("duree", "debrancher"))
	await get_tree().create_timer(d_debrancher * INSTANT_BRAS_LEVES, false).timeout
	_fiche_posee = false
	_retrait = 0.0
	var rembobine := create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	rembobine.tween_property(self, "_retrait", 1.0, 0.35)
	rembobine.tween_callback(_ranger_cable)
	var retour := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 2.4)
	retour.tween_property(_lumiere, "light_energy", 0.0, 3.5)
	await get_tree().create_timer(d_debrancher * (1.0 - INSTANT_BRAS_LEVES), false).timeout
	if geste:
		robot.call("fin_action")
	_joueur.set("cinematique", false)
	_en_cours = false


## Plan de côté sur la prise : le premier point d'où l'on voit le geste sans mur entre la caméra et le robot.
func _plan_de_cote(cible: Vector3, normale: Vector3) -> Vector3:
	var droite := (-normale).cross(Vector3.UP).normalized()
	var essais: Array[Vector3] = [
		cible + droite * 2.4 + normale * 0.5 + Vector3.UP * 0.5,
		cible - droite * 2.4 + normale * 0.5 + Vector3.UP * 0.5,
		cible + normale * 2.4 + Vector3.UP * 1.4,
		cible + droite * 1.6 + normale * 1.6 + Vector3.UP * 1.8,
	]
	var espace := get_world_3d().direct_space_state
	for p: Vector3 in essais:
		var q := PhysicsRayQueryParameters3D.create(cible, p)
		q.exclude = [_joueur.get_rid()]
		if espace.intersect_ray(q).is_empty():
			return p
	return cible + normale * 2.0 + Vector3.UP * 1.8


func _ranger_cable() -> void:
	_cable.visible = false
	_retrait = -1.0
