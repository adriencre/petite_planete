extends Node3D
## La cabine s'ouvre en coupe lorsque le robot monte à bord. La clé reste dans sa sauvegarde.

const SONS := preload("res://scripts/sons.gd")
const PAGE := preload("res://scripts/page_lisible.gd")

@export var reseau: Node3D

@onready var _cle: Node3D = $Cle
@onready var _touche: Label3D = $Cle/Touche
@onready var _journal: PAGE = $JournalDeQuart

var cle_recuperee := false
var _robot: CharacterBody3D
var _coupe: Array[GeometryInstance3D] = []
var _transparence := 0.0


func _ready() -> void:
	add_to_group("sauvegarde")
	add_to_group("epave_ravitailleur")
	add_to_group("interactif")
	add_to_group("a_ramasser")
	cle_recuperee = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("cle_recuperee", false))
	_cle.visible = not cle_recuperee
	_journal.lecture_autorisee = _peut_lire_journal
	var toiture := $Modele.find_child("CoupeCabine", true, false)
	if toiture:
		for maillage in toiture.find_children("*", "GeometryInstance3D", true, false):
			_coupe.append(maillage as GeometryInstance3D)


func cle_sauvegarde() -> String:
	return "ravitailleur"


func sauver() -> Dictionary:
	return {"cle_recuperee": cle_recuperee}


func condition_acces() -> String:
	if HorlogeMonde.niveau_mer() > 0.02:
		return "Le banc est sous l’eau"
	if reseau == null or not bool(reseau.get("allume")):
		return "Le banc disparaît dans la brume"
	return ""


func _process(delta: float) -> void:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if _robot == null:
		return
	var cible := 1.0 if _dans_cabine() else 0.0
	var transparence := move_toward(_transparence, cible, delta * 2.4)
	if not is_equal_approx(transparence, _transparence):
		_transparence = transparence
		for maillage in _coupe:
			maillage.transparency = transparence
			maillage.visible = transparence < 0.999
	_touche.visible = _cle_a_portee()


func _dans_cabine() -> bool:
	var pied := to_local(_robot.global_position)
	return absf(pied.x) < 1.79 and pied.z > 1.1 and pied.z < 5.35 and pied.y > 0.20 and pied.y < 2.4


func _cle_a_portee() -> bool:
	return _cle_a_portee_brute() and not _journal._a_portee()


func _cle_a_portee_brute() -> bool:
	if cle_recuperee or _robot == null or bool(_robot.get("cinematique")) or not _dans_cabine() or not condition_acces().is_empty():
		return false
	var ecart := _robot.global_position - _cle.global_position
	return absf(ecart.y) < 1.45 and Vector2(ecart.x, ecart.z).length() < 0.93


func _peut_lire_journal() -> bool:
	if _robot == null or not _dans_cabine() or not condition_acces().is_empty():
		return false
	if not _cle_a_portee_brute():
		return true
	var pied := Vector2(_robot.global_position.x, _robot.global_position.z)
	var cle := Vector2(_cle.global_position.x, _cle.global_position.z)
	var journal := Vector2(_journal.global_position.x, _journal.global_position.z)
	return pied.distance_squared_to(journal) < pied.distance_squared_to(cle)


func etat_interaction() -> int:
	if cle_recuperee or _robot == null or not _dans_cabine() or not condition_acces().is_empty():
		return 0
	return 2 if _cle_a_portee() else 1


func point_appel() -> Vector3:
	return _cle.global_position


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E or not _cle_a_portee():
		return
	get_viewport().set_input_as_handled()
	_prendre_cle()


func _prendre_cle() -> void:
	var table := _cle.global_position
	cle_recuperee = true
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	_robot.set("regard_cible", table)
	_robot.set("cine_cible", table)
	_robot.set("cine_position", to_global(Vector3(0.53, 1.98, 2.84)))
	var plan := create_tween().set_trans(Tween.TRANS_SINE)
	plan.tween_property(_robot, "cine_melange", 1.0, 0.68)
	plan.tween_interval(0.45)
	plan.tween_callback(SONS.jouer.bind("clic", table, -6.0, 1.26))
	var main: Vector3 = _robot.call("poignet_droit_monde")
	plan.tween_property(_cle, "global_position", main, 0.78)
	plan.tween_callback(_cle.hide)
	plan.tween_property(_robot, "cine_melange", 0.0, 0.55)
	await plan.finished
	_robot.set("cinematique", false)
	var carnet := get_tree().get_first_node_in_group("carnet")
	if carnet:
		carnet.call("noter_texte", "La clé de la salle des cartes était sur le bureau du ravitailleur.", "")
