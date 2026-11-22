extends Node
## Le cadrage de la vue de dessus par quartiers (décidé le 2026-11-22, après l'essai d'une caméra qui
## tournait à chaque pas). Le joueur a besoin d'un cadre stable pour s'orienter : la caméra ne change que
## lorsqu'il passe d'un quartier à un autre (zone_camera.gd), lentement, puis ne bouge plus.
## Hors de toute zone : le cadrage de la scène (ville basse, quai, Coin noir).
## Les commandes gardent leur sens pendant la transition tant qu'on tient les touches (joueur.gd).

@export var joueur: Node3D
## Durée d'une transition entre deux cadrages (secondes).
@export var duree: float = 2.6
## Temps passé dans une nouvelle zone avant d'y basculer : pas d'aller-retour en longeant une frontière.
@export var delai: float = 0.45

var _zones: Array[Area3D] = []
var _actuelle: Area3D = null
var _candidate: Area3D = null
var _attente: float = 0.0
var _transition: Tween
var _orientation_scene: float = 45.0
var _distance_scene: float = 9.0
var _angle_scene: float = 40.0


func _ready() -> void:
	if joueur == null:
		return
	_orientation_scene = float(joueur.get("orientation_dessus"))
	_distance_scene = float(joueur.get("distance_dessus"))
	_angle_scene = float(joueur.get("angle_dessus"))
	await get_tree().process_frame
	for z in get_tree().get_nodes_in_group("zones_camera"):
		_zones.append(z as Area3D)


func _physics_process(delta: float) -> void:
	if joueur == null or not bool(joueur.get("vue_dessus")):
		return
	var meilleure: Area3D = null
	for z in _zones:
		if z.overlaps_body(joueur) and (meilleure == null or int(z.get("priorite")) > int(meilleure.get("priorite"))):
			meilleure = z
	if meilleure == _actuelle:
		_candidate = null
		return
	if meilleure != _candidate:
		_candidate = meilleure
		_attente = 0.0
	_attente += delta
	if _attente < delai:
		return
	_actuelle = meilleure
	_candidate = null
	_cadrer(_actuelle)


func _cadrer(zone: Area3D) -> void:
	var o1: float = _orientation_scene
	var d1: float = _distance_scene
	var a1: float = _angle_scene
	if zone:
		o1 = float(zone.get("orientation"))
		if float(zone.get("distance")) > 0.0:
			d1 = float(zone.get("distance"))
		if float(zone.get("angle")) > 0.0:
			a1 = float(zone.get("angle"))
	var o0: float = float(joueur.get("orientation_dessus"))
	var d0: float = float(joueur.get("distance_dessus"))
	var a0: float = float(joueur.get("angle_dessus"))
	var passer := func(t: float) -> void:
		joueur.set("orientation_dessus", rad_to_deg(lerp_angle(deg_to_rad(o0), deg_to_rad(o1), t)))
		joueur.set("distance_dessus", lerpf(d0, d1, t))
		joueur.set("angle_dessus", lerpf(a0, a1, t))
	if _transition:
		_transition.kill()
	_transition = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_transition.tween_method(passer, 0.0, 1.0, duree)
