extends "res://scripts/batiment_coupe.gd"
## Le miroir du quai déverrouille les deux vantaux sur leur rail.

const SONS := preload("res://scripts/sons.gd")
const COURSE := 1.86

@export var miroir: Node3D

@onready var _gauche: AnimatableBody3D = $VantailGauche
@onready var _droite: AnimatableBody3D = $VantailDroit
@onready var _repos_gauche := _gauche.position.x
@onready var _repos_droit := _droite.position.x

var _ouvert := false


func _ready() -> void:
	super._ready()
	add_to_group("sauvegarde")
	var etat := Sauvegarde.donnees(cle_sauvegarde(), self)
	_ouvert = bool(etat.get("ouvert", false))
	if _ouvert:
		_ecarter(COURSE)


func cle_sauvegarde() -> String:
	return "hangar_quai"


func sauver() -> Dictionary:
	return {"ouvert": _ouvert}


func _physics_process(_delta: float) -> void:
	if _ouvert or miroir == null or not miroir.transmet():
		return
	var robot := get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if robot == null or bool(robot.get("cinematique")):
		return
	_ouvert = true
	_ouvrir(robot)


func _ecarter(distance: float) -> void:
	_gauche.position.x = _repos_gauche - distance
	_droite.position.x = _repos_droit + distance


func _ouvrir(robot: CharacterBody3D) -> void:
	var cible := to_global(Vector3(0.0, 1.6, 4.25))
	robot.set("regard_cible", cible)
	robot.set("cinematique", true)
	robot.velocity = Vector3.ZERO
	robot.set("cine_position", to_global(Vector3(4.5, 4.1, 10.0)))
	robot.set("cine_cible", cible)
	var plan := create_tween().set_process_mode(Tween.TWEEN_PROCESS_PHYSICS).set_trans(Tween.TRANS_SINE)
	plan.tween_property(robot, "cine_melange", 1.0, 0.52)
	plan.tween_callback(SONS.jouer.bind("clic", cible, -2.0, 0.68))
	plan.tween_method(_ecarter, 0.0, COURSE, 1.28)
	plan.tween_callback(SONS.jouer.bind("clic", cible, -7.0, 0.84))
	plan.tween_interval(0.32)
	plan.tween_property(robot, "cine_melange", 0.0, 0.60)
	await plan.finished
	if is_instance_valid(robot):
		robot.set("cinematique", false)
