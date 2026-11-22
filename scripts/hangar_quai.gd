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


## Le premier allumage du miroir d'essai, filmé lentement (retour du 2026-11-22 : on ne comprenait pas
## à quoi servait le hangar). 1) la caméra suit le rayon jusqu'au capteur, qui s'allume ; 2) elle glisse
## vers la porte, qui s'ouvre lentement sur son rail ; 3) elle entre regarder l'établi, où attend la
## fiche d'atelier des miroirs ; 4) on rend la main.
func _ouvrir(robot: CharacterBody3D) -> void:
	var capteur := to_global(Vector3(4.83, 1.66, 2.59))
	var porte := to_global(Vector3(0.0, 1.6, 4.25))
	var etabli := to_global(Vector3(-2.4, 1.2, -3.5))
	robot.set("regard_cible", capteur)
	robot.set("cinematique", true)
	robot.velocity = Vector3.ZERO
	robot.set("cine_position", to_global(Vector3(9.5, 4.6, 8.5)))
	robot.set("cine_cible", capteur)
	var plan := create_tween().set_process_mode(Tween.TWEEN_PROCESS_PHYSICS).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	# 1) le rayon touche le capteur
	plan.tween_property(robot, "cine_melange", 1.0, 0.9)
	plan.tween_interval(1.4)
	plan.tween_callback(SONS.jouer.bind("clic", capteur, -4.0, 1.1))
	plan.tween_interval(0.8)
	# 2) vers la porte : le verrou claque, les vantaux glissent
	plan.tween_callback(robot.set.bind("regard_cible", porte))
	plan.set_parallel(true)
	plan.tween_property(robot, "cine_position", to_global(Vector3(3.5, 3.8, 10.5)), 1.6)
	plan.tween_property(robot, "cine_cible", porte, 1.6)
	plan.set_parallel(false)
	plan.tween_callback(SONS.jouer.bind("clic", porte, -2.0, 0.68))
	plan.tween_method(_ecarter, 0.0, COURSE, 2.6)
	plan.tween_callback(SONS.jouer.bind("clic", porte, -7.0, 0.84))
	# 3) la caméra regarde à l'intérieur, vers l'établi
	plan.set_parallel(true)
	plan.tween_property(robot, "cine_position", to_global(Vector3(0.6, 3.6, 7.5)), 2.0)
	plan.tween_property(robot, "cine_cible", etabli, 2.0)
	plan.set_parallel(false)
	plan.tween_interval(1.6)
	# 4) retour au robot
	plan.tween_property(robot, "cine_melange", 0.0, 1.2)
	await plan.finished
	if is_instance_valid(robot):
		robot.set("cinematique", false)
