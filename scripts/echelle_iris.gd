extends Node3D
## Traversée mise en scène dans les deux sens, entre deux paliers sûrs.

const POSE_ECHELLE := preload("res://scripts/pose_echelle.gd")
const CLIP_PRISE := "echelle_prise"
const CLIP_CYCLE := "echelle_cycle"
const CLIP_SORTIE := "echelle_sortie"
const DISTANCE_CYCLE := 0.31
const DUREE_CYCLE := 0.66
const HAUTEUR_PRISE := 0.36
const HAUTEUR_SORTIE := 0.76

@onready var _haut: Marker3D = $Galerie
@onready var _bas: Marker3D = $Toit
@onready var _barreaux: Marker3D = $Barreaux
var _robot: CharacterBody3D
var _modele: Node3D
var _avec_clips := false
var _pose: SkeletonModifier3D
var _trajet: Tween
var _depart: Vector3
var _occupee := false


func _ready() -> void:
	add_to_group("interactif")


func _point_proche() -> Marker3D:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if _robot == null:
		return null
	for repere: Marker3D in [_haut, _bas]:
		var ecart := _robot.global_position - repere.global_position
		if absf(ecart.y) < 0.18 and Vector2(ecart.x, ecart.z).length() < 0.63:
			return repere
	return null


func etat_interaction() -> int:
	return 2 if not _occupee and _point_proche() and not bool(_robot.get("cinematique")) else 0


func point_appel() -> Vector3:
	var proche := _point_proche()
	return proche.global_position + Vector3.UP * 1.0 if proche else global_position


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if touche and touche.pressed and not touche.echo and touche.physical_keycode == KEY_E and etat_interaction() == 2:
		get_viewport().set_input_as_handled()
		_traverser(_point_proche())


func _traverser(entree: Marker3D) -> void:
	_occupee = true
	_depart = _robot.global_position
	var sortie := _bas if entree == _haut else _haut
	var monter := entree == _bas
	_robot.set("cinematique", true)
	_robot.set("sur_echelle", true)
	_robot.velocity = Vector3.ZERO
	_modele = _robot.get_node("Modele") as Node3D
	_avec_clips = (
		_modele.has_method("a_animation")
		and bool(_modele.call("a_animation", CLIP_PRISE))
		and bool(_modele.call("a_animation", CLIP_CYCLE))
		and bool(_modele.call("a_animation", CLIP_SORTIE))
	)
	var squelette := _modele.find_children("*", "Skeleton3D", true, false)
	if not squelette.is_empty():
		_pose = POSE_ECHELLE.new()
		_pose.set("barreau", _barreaux.global_position)
		_pose.set("hauteur_depart", entree.global_position.y)
		_pose.set("sens", 1.0 if monter else -1.0)
		_pose.set("suivre_animation", _avec_clips)
		squelette[0].add_child(_pose)

	var recul := 0.49 if _avec_clips else 0.33
	var axe := _barreaux.global_position + global_transform.basis.x * recul
	var prise := Vector3(axe.x, entree.global_position.y, axe.z)
	var arrivee := Vector3(axe.x, sortie.global_position.y, axe.z)
	if _avec_clips:
		prise.y += HAUTEUR_PRISE if monter else -HAUTEUR_SORTIE
		arrivee.y += -HAUTEUR_SORTIE if monter else HAUTEUR_PRISE
	_cadrer()
	_trajet = create_tween().set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	_trajet.tween_property(_robot, "cine_melange", 1.0, 0.48)
	var debut := CLIP_PRISE if monter else CLIP_SORTIE
	var fin := CLIP_SORTIE if monter else CLIP_PRISE
	var duree_debut := 0.78
	var duree_fin := 0.70
	if _avec_clips:
		duree_debut = 1.52 if monter else 2.05
		duree_fin = 2.05 if monter else 1.52
	if _avec_clips:
		_trajet.tween_callback(_jouer_clip.bind(debut, duree_debut, monter, 1))
	_trajet.tween_method(_avancer.bind(_depart, prise, 0.0, 1.0, 0.0, not monter),
		0.0, 1.0, duree_debut).set_trans(Tween.TRANS_SINE)
	var distance := prise.distance_to(arrivee)
	var duree := distance * (0.95 if monter else 0.88)
	if _avec_clips:
		var repetitions := maxi(1, roundi(distance / DISTANCE_CYCLE))
		duree = repetitions * DUREE_CYCLE
		_trajet.tween_callback(_jouer_clip.bind(CLIP_CYCLE, duree, monter, repetitions))
	_trajet.tween_method(_grimper.bind(prise, arrivee, distance), 0.0, 1.0, duree)
	if _avec_clips:
		_trajet.tween_callback(_jouer_clip.bind(fin, duree_fin, monter, 1))
	_trajet.tween_method(_avancer.bind(arrivee, sortie.global_position, 1.0, 0.0, distance, monter),
		0.0, 1.0, duree_fin).set_trans(Tween.TRANS_SINE)
	_trajet.tween_property(_robot, "cine_melange", 0.0, 0.48)
	await _trajet.finished
	_liberer()


func _jouer_clip(nom: String, duree: float, monter: bool, repetitions: int) -> void:
	var vitesse := float(_modele.call("duree", nom)) * repetitions / duree
	_modele.call("jouer_action", nom, vitesse if monter else -vitesse, 0.18)


func _grimper(t: float, a: Vector3, b: Vector3, distance: float) -> void:
	var phase := sin(fposmod(t * distance / 0.31, 1.0) * TAU)
	var progression := t if _avec_clips else t - phase * (0.31 / distance) * 0.07
	_avancer(clampf(progression, 0.0, 1.0), a, b, 1.0, 1.0, t * distance)


func _avancer(t: float, a: Vector3, b: Vector3, poids_a: float, poids_b: float,
		distance: float, palier_haut: bool = false) -> void:
	var position := a.lerp(b, t)
	if palier_haut and _avec_clips:
		# Le robot finit de se hisser avant de passer au-dessus du rebord.
		var monter := b.y > a.y
		var horizontal := smoothstep(0.55, 1.0, t) if monter else smoothstep(0.0, 0.45, t)
		var vertical := smoothstep(0.0, 0.60, t) if monter else smoothstep(0.45, 1.0, t)
		position = a.lerp(b, horizontal)
		position.y = lerpf(a.y, b.y, vertical)
	_robot.global_position = position
	if is_instance_valid(_pose):
		_pose.set("poids", lerpf(poids_a, poids_b, t))
		_pose.set("distance_parcourue", distance)
	_cadrer()


func _cadrer() -> void:
	var cible := _robot.global_position + Vector3.UP * 1.05
	_robot.set("regard_cible", cible - global_transform.basis.x)
	_robot.set("cine_cible", cible)
	_robot.set("cine_position", cible + global_transform.basis * Vector3(4.7, 1.25, 3.1))


func _liberer() -> void:
	if _avec_clips and is_instance_valid(_modele):
		_modele.call("fin_action")
	if is_instance_valid(_pose):
		_pose.queue_free()
	if is_instance_valid(_robot):
		_robot.velocity = Vector3.ZERO
		_robot.set("cine_melange", 0.0)
		_robot.set("sur_echelle", false)
		_robot.set("cinematique", false)
	_occupee = false


func _exit_tree() -> void:
	if _occupee and is_instance_valid(_robot) and _robot.is_inside_tree():
		_robot.global_position = _depart
		_liberer()
