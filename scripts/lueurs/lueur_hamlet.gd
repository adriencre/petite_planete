class_name LueurHamlet
extends Node3D
## Un hameau de Lueurs (maisons, jardins, habitantes), visible seulement dans le noir.
## La toute première fois que le robot y arrive dans le noir (batterie basse ou antenne éteinte),
## c'est un moment : une petite sort de sa maison, le regarde, dit « …il… revient… » et s'enfuit.

@export var first_dweller: LueurDweller ## celle qui ose sortir la première fois
@export var first_words := "…il… revient…"
@export var radius := 5.0 ## distance au centre du hameau où le moment se déclenche
@export var flag_id := &"first_bribe" ## mémorisé d'une boucle à l'autre

@export var extension: Node3D ## maisons qui poussent quand le peuple est prêt (2e moitié)

var _check := 0.0
var _playing := false


func _ready() -> void:
	if extension:
		extension.visible = Loop.has_flag(&"pouponniere_libre")


## Le peuple est prêt : de nouvelles maisons se tissent dans l'ancien désert gris.
func grow_extension() -> void:
	if extension == null:
		return
	extension.visible = true
	extension.scale = Vector3(1.0, 0.02, 1.0)
	create_tween().tween_property(extension, "scale", Vector3.ONE, 6.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _process(delta: float) -> void:
	if _playing or first_dweller == null or Loop.has_flag(flag_id):
		return
	_check -= delta
	if _check > 0.0:
		return
	_check = 0.3
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if robot == null or robot.busy or Notebook.is_open:
		return
	if robot.global_position.distance_to(global_position) > radius:
		return
	if robot.battery.vision() < 0.3 or WakeZone.awake_at(get_tree(), first_dweller.global_position) > 0.5:
		return
	_first_bribe(robot)


func _first_bribe(robot: Node3D) -> void:
	_playing = true
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"first_bribe", 5.5, 26.0, 0.6, first_dweller)
	# elle sort de sa maison et s'avance vers lui, prudemment
	var to_robot := robot.global_position - first_dweller.global_position
	to_robot.y = 0.0
	var stop := robot.global_position - to_robot.normalized() * 1.4
	first_dweller.scripted_hide = false
	first_dweller.scripted_target = Vector3(stop.x, first_dweller.global_position.y, stop.z)
	robot.face.set_expression(&"curious", 0.6)
	await get_tree().create_timer(2.0).timeout
	await robot.face_toward(first_dweller.global_position, 0.6)
	await get_tree().create_timer(1.2).timeout
	var speech := first_dweller.get_node_or_null("PremiereBribe") as LueurSpeech
	if speech:
		speech.say_exact(first_words)
	await get_tree().create_timer(2.6).timeout
	# …puis elle s'enfuit
	robot.face.set_expression(&"surprised", 0.3)
	first_dweller.scripted_target = first_dweller.home.global_position if first_dweller.home else first_dweller.global_position
	first_dweller.scripted_hide = true
	await get_tree().create_timer(2.2).timeout
	first_dweller.scripted_target = null
	first_dweller.scripted_hide = false
	robot.face.set_expression(&"sad", 1.0)
	await get_tree().create_timer(1.2).timeout
	if cam:
		cam.pop_override(&"first_bribe")
	robot.face.set_expression(&"neutral", 0.8)
	robot.busy = false
	Loop.set_flag(flag_id)
	_playing = false
