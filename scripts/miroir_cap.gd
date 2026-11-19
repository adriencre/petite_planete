extends Node3D
## La tête renvoie le rayon reçu selon la normale de sa surface réfléchissante.

const SONS := preload("res://scripts/sons.gd")
const CRANS := [-32.0, 0.0, 32.0]

@export var identifiant: String
@export var lanterne: Node3D
@export var miroir_amont: Node3D
@export var reception: Node3D
@export var voyant_reception: Node3D
@export_range(0, 2) var cran_initial: int = 0
@export var filmer_premier_alignement := true

@onready var _tete: Node3D = $PivotMiroir
@onready var _manivelle: Node3D = $Manivelle
@onready var _faisceau: Node3D = $Faisceau
@onready var _incident: Node3D = $FaisceauIncident
@onready var _eclat: Sprite3D = $PivotMiroir/Eclat
@onready var _touche: Label3D = $Touche

var _robot: CharacterBody3D
var _source: Node3D
var _cran := 0
var _angle_cran := 0.0
var _en_rotation := false
var _deja_filme := false
var _progression := 1.0
var _transmet := false


func _ready() -> void:
	add_to_group("sauvegarde")
	var etat: Dictionary = Sauvegarde.donnees(cle_sauvegarde(), self)
	_cran = clampi(int(etat.get("cran", cran_initial)), 0, CRANS.size() - 1)
	_deja_filme = bool(etat.get("deja_filme", false))
	_angle_cran = CRANS[_cran]
	if miroir_amont:
		_source = miroir_amont.get_node("PivotMiroir") as Node3D
	elif lanterne:
		_source = lanterne.get_node("SortieOptique") as Node3D
	if _source and reception:
		_orienter_miroir()


func cle_sauvegarde() -> String:
	return "miroir_cap:" + identifiant


func sauver() -> Dictionary:
	return {"cran": _cran, "deja_filme": _deja_filme}


## Le rayon réfléchi a atteint l'optique suivante.
func transmet() -> bool:
	return _transmet


func _recoit() -> bool:
	if miroir_amont:
		return bool(miroir_amont.call("transmet"))
	return lanterne != null and bool(lanterne.get("allumee"))


func _orienter_miroir() -> void:
	var centre := _tete.global_position
	var entree := _source.global_position.direction_to(centre)
	var sortie := centre.direction_to(reception.global_position)
	# Le cran central bissecte les directions vers l'origine du rayon et vers la destination.
	var normale := global_basis.inverse() * (sortie - entree).normalized()
	_tete.rotation.y = atan2(-normale.x, -normale.z) + deg_to_rad(_angle_cran)
	_tete.rotation.x = asin(clampf(normale.y, -1.0, 1.0))


func _a_portee() -> bool:
	if not is_instance_valid(_robot) or bool(_robot.get("cinematique")) or _en_rotation:
		return false
	var ecart := _manivelle.global_position - _robot.global_position
	return absf(ecart.y) < 1.25 and Vector2(ecart.x, ecart.z).length() < 1.2


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E or not _a_portee():
		return
	get_viewport().set_input_as_handled()
	_en_rotation = true
	var cran_precedent := _cran
	_cran = (_cran + 1) % CRANS.size()
	var ecart_crans := _cran - cran_precedent
	var duree := 0.9 * absf(ecart_crans)
	var rotation_roues := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	rotation_roues.tween_property(_manivelle, "rotation:z", TAU * ecart_crans, duree)
	rotation_roues.tween_property(self, "_angle_cran", CRANS[_cran], duree)
	SONS.jouer("clic", _manivelle.global_position, -6.0, 0.72)
	await rotation_roues.finished
	_manivelle.rotation.z = 0.0
	SONS.jouer("clic", _tete.global_position, -4.0, 0.92)
	_en_rotation = false


func _physics_process(_delta: float) -> void:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	_touche.visible = _a_portee()
	_transmet = false
	if _source and reception:
		_orienter_miroir()
	if _source and reception and _recoit():
		_transmet = _reflechir()
	else:
		_incident.hide()
		_faisceau.hide()
		_eclat.hide()
	if voyant_reception:
		voyant_reception.visible = _transmet


func _reflechir() -> bool:
	var origine := _tete.global_position
	var incidence := _source.global_position.direction_to(origine)
	if lanterne:
		_placer_faisceau(_incident, _source.global_position, origine)
	var normale := -_tete.global_basis.z
	if incidence.dot(normale) >= -0.01:
		_faisceau.hide()
		_eclat.hide()
		return false  # le rayon arrive par le dos
	_eclat.show()
	var direction := incidence.bounce(normale)
	var cible := reception.global_position
	var bout := origine + direction * origine.distance_to(cible)
	var aligne := not _en_rotation and bout.distance_to(cible) < 0.17
	if aligne:
		bout = cible
	var rayon := PhysicsRayQueryParameters3D.create(origine + direction * 0.025, bout, 1)
	if is_instance_valid(_robot):
		rayon.exclude = [_robot.get_rid()]
	var obstacle := get_world_3d().direct_space_state.intersect_ray(rayon)
	if not obstacle.is_empty():
		bout = obstacle.position
		aligne = aligne and bout.distance_to(cible) < 0.17
	if aligne and filmer_premier_alignement and not _deja_filme and is_instance_valid(_robot) and not bool(_robot.get("cinematique")):
		_filmer_alignement()
	_placer_faisceau(_faisceau, origine, bout, _progression)
	return aligne and _progression >= 0.995


func _placer_faisceau(faisceau: Node3D, origine: Vector3, bout: Vector3, progression: float = 1.0) -> void:
	var distance := origine.distance_to(bout)
	if distance <= 0.01:
		faisceau.hide()
		return
	faisceau.global_position = origine
	faisceau.look_at(bout)
	var longueur := faisceau.get_node("Longueur") as Node3D
	longueur.scale.z = maxf(0.001, distance * progression)
	faisceau.show()


func _filmer_alignement() -> void:
	_deja_filme = true
	_progression = 0.02
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	var origine := _tete.global_position
	var direction := origine.direction_to(reception.global_position)
	_robot.set("regard_cible", origine)
	_robot.set("cine_position", origine + global_basis * Vector3(2.6, 2.0, 5.0))
	_robot.set("cine_cible", origine + direction * 3.0)
	var plan := create_tween().set_trans(Tween.TRANS_SINE)
	plan.tween_property(_robot, "cine_melange", 1.0, 0.55)
	plan.tween_property(self, "_progression", 1.0, 1.8)
	plan.parallel().tween_property(_robot, "cine_cible", origine + direction * 12.0, 1.8)
	plan.tween_interval(0.48)
	plan.tween_property(_robot, "cine_melange", 0.0, 0.6)
	await plan.finished
	_robot.set("cinematique", false)
