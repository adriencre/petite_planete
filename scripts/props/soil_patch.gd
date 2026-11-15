class_name SoilPatch
extends Node3D
## Carré de terreau gravé d'un symbole. Le robot y plante la graine qu'il porte,
## et la plante liée (`grows`) se met à pousser.

@export var grows: RootStairs

var planted := false

@onready var _interactable: Interactable = $Interactable


func _ready() -> void:
	_interactable.enabled = false
	_interactable.interacted.connect(_on_plant)


func _process(_delta: float) -> void:
	# on ne propose de planter que si le robot porte une graine
	if planted:
		return
	var player := get_tree().get_first_node_in_group(&"player")
	_interactable.enabled = player != null and player.holds(&"seed")


func _on_plant(robot: Node3D) -> void:
	if planted or not robot.holds(&"seed"):
		return
	planted = true
	_interactable.enabled = false
	set_process(false)
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"planting", 6.0, 30.0, 0.8, global_position + Vector3(0, 0.4, 0))
	await robot.face_toward(global_position)
	# la graine descend doucement dans la terre en brillant
	var seed: Node3D = robot.give_held()
	seed.reparent(self)
	var glow := OmniLight3D.new()
	glow.light_color = Color(1.0, 0.85, 0.55)
	glow.omni_range = 1.6
	glow.light_energy = 0.0
	glow.position = Vector3(0, 0.15, 0)
	add_child(glow)
	Audio.play("seed_plant", null, -4.0)
	var tween := create_tween()
	tween.tween_property(seed, "position", Vector3(0, 0.25, 0), 1.0).set_trans(Tween.TRANS_SINE)
	tween.tween_property(seed, "position", Vector3(0, 0.02, 0), 0.8).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tween.parallel().tween_property(seed, "scale", Vector3.ONE * 0.4, 0.8)
	tween.parallel().tween_property(glow, "light_energy", 2.5, 0.8)
	await tween.finished
	seed.queue_free()
	robot.busy = false
	await robot.pulse_toward(global_position + Vector3.UP * 0.1)
	robot.busy = true
	# la terre s'illumine par en dessous… puis les racines jaillissent
	var pulse := create_tween()
	pulse.tween_property(glow, "light_energy", 4.0, 0.4)
	pulse.tween_property(glow, "light_energy", 1.5, 0.6)
	await pulse.finished
	if grows:
		if cam:
			cam.push_override(&"planting", 10.0, 24.0, 0.6, grows.global_position + Vector3(0, 1.2, -2.0))
		robot.face.set_expression(&"surprised")
		Audio.play("roots_grow", null, -3.0)
		create_tween().tween_property(glow, "light_energy", 0.0, 3.0)
		await grows.grow()
		if cam:
			cam.pop_override(&"planting")
		robot.busy = false
		robot.emote(&"happy", &"happy")
	else:
		robot.busy = false


## Accompli quand la graine est plantée.
func is_done() -> bool:
	return planted
