extends Node
## L'estran et la marée (île 2, G1 « Atteindre le Phare ») : les cases « _ » (chaussée, gué, flaque,
## épave) ne se traversent qu'à marée basse. Dans la brume épaisse on ne voit pas la mer monter : on la
## SENT, sur le robot lui-même (effets dans l'enfant `EffetsMaree`, scenes/ile02/effets_maree.tscn) :
## - les pieds dans l'eau : un anneau d'écume autour des jambes, des éclaboussures quand il marche,
##   le bruit des vagues, et il ralentit à mesure que l'eau monte ;
## - l'eau aux genoux (`profondeur_emporte`) : la mer l'emporte. Un voile d'écume couvre l'écran, puis il
##   se retrouve au dernier endroit sec (au sec même à marée haute), la batterie a pris l'eau.
## Le niveau de la mer vient de l'autoload HorlogeMonde.

const SONS := preload("res://scripts/sons.gd")
const EFFETS := preload("res://scenes/ile02/effets_maree.tscn")

@export var maquette: Node3D
## Hauteur d'eau (m) au-dessus des pieds à partir de laquelle la mer emporte le robot.
@export var profondeur_emporte: float = 0.3
## Batterie perdue quand la mer l'emporte.
@export var perte_batterie: float = 0.3
## Vitesse gardée quand l'eau arrive presque aux genoux (1 = pas ralenti).
@export_range(0.1, 1.0) var vitesse_dans_l_eau: float = 0.4

var _joueur: CharacterBody3D
var _horloge: Node
var _dernier_sec := Vector3.ZERO
var _chrono_sec := 0.0
var _repit := 0.0          # après avoir été emporté : quelques secondes sans nouvelle vérification
var _son_eau := 0.0        # délai avant de rejouer le bruit des vagues
var _vitesse_base := 0.0
var _course_base := 0.0
var _ecume: MeshInstance3D
var _gouttes: CPUParticles3D
var _voile: ColorRect


func _ready() -> void:
	if get_node_or_null("EffetsMaree") == null:   # les effets (modifiables dans leur scène) : posés s'ils manquent
		add_child(EFFETS.instantiate())
	_ecume = get_node_or_null("EffetsMaree/Ecume") as MeshInstance3D
	_gouttes = get_node_or_null("EffetsMaree/Eclaboussures") as CPUParticles3D
	_voile = get_node_or_null("EffetsMaree/Voile/Ecran") as ColorRect
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	_horloge = get_node_or_null("/root/HorlogeMonde")
	if _joueur:
		_dernier_sec = _joueur.global_position
		_vitesse_base = float(_joueur.get("vitesse"))
		_course_base = float(_joueur.get("vitesse_course"))


func _physics_process(delta: float) -> void:
	if _joueur == null or _horloge == null or maquette == null:
		return
	_repit = maxf(0.0, _repit - delta)
	_son_eau = maxf(0.0, _son_eau - delta)
	# « embarque » est la barque à bord de laquelle il est (un nœud, ou null), pas un booléen
	if bool(_joueur.get("cinematique")) or _joueur.get("embarque") != null:
		_montrer_eau(-1.0, 0.0)
		return
	var p := _joueur.global_position
	var mer: float = _horloge.call("niveau_mer")
	var eau := mer - p.y
	var k: Dictionary = maquette.call("_case_a", p)
	# mémoriser le dernier endroit sûr : au sol, sur une case de terre, et au sec MÊME à marée haute
	# (sinon un point « sec à marée basse » devient un piège quand la mer remonte : boucle sans fin)
	_chrono_sec += delta
	var toujours_sec: bool = p.y > float(_horloge.get("mer_haute")) + 0.05
	if _chrono_sec > 0.5 and _joueur.is_on_floor() and toujours_sec and int(k.get("niv", -1)) >= 0:
		_chrono_sec = 0.0
		_dernier_sec = p
	_montrer_eau(eau, mer)
	if eau > profondeur_emporte and _repit <= 0.0:
		_emporte()


## Les pieds dans l'eau : écume, éclaboussures, vagues, et le robot ralentit. eau < 0 : au sec.
func _montrer_eau(eau: float, mer: float) -> void:
	var dedans := eau > 0.02
	var p := _joueur.global_position
	var f := clampf(eau / profondeur_emporte, 0.0, 1.0)
	if _ecume:
		_ecume.visible = dedans
		if dedans:
			_ecume.global_position = Vector3(p.x, mer + 0.02, p.z)
			var s := lerpf(0.8, 1.3, f)
			_ecume.scale = Vector3(s, 0.18, s)
	var vh := Vector2(_joueur.velocity.x, _joueur.velocity.z).length()
	if _gouttes:
		_gouttes.global_position = Vector3(p.x, mer + 0.05, p.z)
		_gouttes.emitting = dedans and vh > 0.6
	if dedans and _son_eau <= 0.0:
		SONS.jouer("vagues", p, -10.0 + 8.0 * f, 1.2 - 0.3 * f)
		_son_eau = 3.0
	# ralenti à mesure que l'eau monte (et rendu entier au sec)
	var k := lerpf(1.0, vitesse_dans_l_eau, f) if dedans else 1.0
	if _vitesse_base > 0.0:
		_joueur.set("vitesse", _vitesse_base * k)
		_joueur.set("vitesse_course", _course_base * k)


## La mer l'emporte : un voile d'écume couvre l'écran, il se retrouve au sec, le voile se lève.
func _emporte() -> void:
	_repit = 4.0
	var cible := _dernier_sec
	if cible.y <= float(_horloge.get("mer_haute")) + 0.05:   # par sécurité : jamais renvoyé dans l'eau
		cible = _joueur.get("_depart")
	_joueur.set("cinematique", true)
	_joueur.velocity = Vector3.ZERO
	SONS.jouer("vagues", null, 2.0, 0.75)
	var t := create_tween()
	if _voile:
		t.tween_property(_voile, "color:a", 0.95, 0.7).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(_deposer.bind(cible))
	t.tween_interval(0.6)
	if _voile:
		t.tween_property(_voile, "color:a", 0.0, 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	t.tween_callback(_joueur.set.bind("cinematique", false))
	print("La mer a emporté le robot : retour au sec.")


## Sous le voile : le robot est posé au sec, la batterie a pris l'eau.
func _deposer(cible: Vector3) -> void:
	_joueur.global_position = cible + Vector3.UP * 0.2
	_joueur.velocity = Vector3.ZERO
	for barque in get_tree().get_nodes_in_group("barque_qui_flotte"):
		barque.call("revenir_au_port")
	var b: float = _joueur.get("batterie")
	_joueur.set("batterie", maxf(0.05, b - perte_batterie))
