extends Node
## Ouverture de l'île 1, lente et silencieuse :
## noir → le robot est couché sur le flanc dans son abri, caméra toute proche →
## un œil vacille, puis l'autre → il se redresse, regarde ses mains, se lève en titubant →
## il regarde autour de lui → on prend la main.
## En sortant de l'abri : la caméra recule lentement sur l'île grise (sans contrôle), puis la luciole apparaît.

signal player_free ## le joueur prend la main dans l'abri
signal island_revealed ## fin du recul de caméra à la sortie de l'abri

@export var robot: Node3D
@export var start_marker: Node3D ## où le robot est couché (dans l'abri)
@export var exit_area: Area3D ## passage de la porte de l'abri
@export var guide: Node3D ## la luciole, qui apparaît après le recul de caméra
@export var cradle_light: OmniLight3D ## lumière du berceau, qui s'allume quand un corps se réveille
@export var skip_intro := false ## pour tester plus vite

var _revealed := false

@onready var _black: ColorRect = $Noir/Ecran


func _ready() -> void:
	Audio.start_island.call_deferred()
	if exit_area:
		exit_area.body_entered.connect(_on_exit)
	if skip_intro or robot == null:
		_black.visible = false
		player_free.emit.call_deferred()
		return
	_black.visible = true
	_black.color.a = 1.0
	if Loop.count > 0:
		_revealed = true  # l'île a déjà été découverte
		_play_again.call_deferred()
	else:
		_play.call_deferred()


func _camera() -> Node:
	return get_viewport().get_camera_3d()


func _play() -> void:
	var cam := _camera()
	robot.busy = true
	if start_marker:
		robot.global_position = start_marker.global_position
		robot.model.rotation.y = start_marker.global_rotation.y
	robot.anim.play(&"lying")
	robot.face.set_expression(&"off", 0.0)
	var lying_focus := robot.global_position + Vector3(0, 0.35, 0)
	if cam:
		cam.push_override(&"intro", 4.2, 28.0, 0.6, lying_focus)
		cam.snap_now()

	await _wait(2.0)
	_cradle_pulse()
	var fade := create_tween()
	fade.tween_property(_black, "color:a", 0.0, 3.0).set_trans(Tween.TRANS_SINE)
	await fade.finished
	_black.visible = false

	# un long moment de silence, puis les yeux
	await _wait(1.8)
	await robot.face.power_on()
	await _wait(0.8)

	# il se relève
	robot.anim.play(&"get_up", 0.2)
	Audio.play("get_up", null, -6.0)
	if cam:
		cam.push_override(&"intro", 5.5, 32.0, 0.5, robot.global_position + Vector3(0, 0.7, 0))
	await _wait(3.2)
	_dust_puff(robot.global_position + Vector3(0, 0.3, 0))
	Audio.play("dust_puff", null, -8.0)
	robot.face.set_expression(&"curious", 0.6)
	await _wait(2.0)
	robot.face.set_expression(&"sad", 0.8)  # il regarde ses mains, perdu
	await _wait(1.6)
	robot.face.set_expression(&"surprised", 0.4)
	await robot.anim.animation_finished
	await robot.emote(&"curious", &"look_around", 0.0)

	if cam:
		cam.pop_override(&"intro")
	await _wait(0.6)
	robot.busy = false
	player_free.emit()


# Boucles suivantes : réveil plus court, dans le berceau qui s'illumine.
func _play_again() -> void:
	var cam := _camera()
	robot.busy = true
	if start_marker:
		robot.global_position = start_marker.global_position
		robot.model.rotation.y = start_marker.global_rotation.y
	robot.anim.play(&"lying")
	robot.face.set_expression(&"off", 0.0)
	if cam:
		cam.push_override(&"intro", 4.6, 30.0, 0.8, robot.global_position + Vector3(0, 0.35, 0))
		cam.snap_now()
	_cradle_pulse()
	await _wait(0.6)
	var fade := create_tween()
	fade.tween_property(_black, "color:a", 0.0, 1.4).set_trans(Tween.TRANS_SINE)
	await fade.finished
	_black.visible = false
	await robot.face.power_on()
	robot.anim.play(&"get_up", 0.2)
	robot.anim.speed_scale = 1.8
	Audio.play("get_up", null, -6.0)
	await robot.anim.animation_finished
	robot.anim.speed_scale = 1.0
	robot.face.set_expression(&"curious", 0.4)
	if cam:
		cam.pop_override(&"intro")
	await _wait(0.4)
	robot.busy = false
	player_free.emit()
	if guide:
		guide.appear(robot.global_position)


func _cradle_pulse() -> void:
	if cradle_light == null:
		return
	var t := create_tween()
	t.tween_property(cradle_light, "light_energy", 3.0, 0.8)
	t.tween_property(cradle_light, "light_energy", 0.4, 2.5)


# Première sortie de l'abri : on découvre l'île endormie.
func _on_exit(body: Node3D) -> void:
	if _revealed or body != robot or robot.busy:
		return
	_revealed = true
	var cam := _camera()
	robot.busy = true
	robot.velocity = Vector3.ZERO
	robot.face.set_expression(&"curious", 0.6)
	if cam:
		cam.push_override(&"reveal", 24.0, 40.0, 0.35)
	await _wait(3.0)
	robot.anim.play(&"look_around", 0.3)
	await _wait(3.0)
	robot.face.set_expression(&"sad", 1.0)
	await _wait(1.5)
	if cam:
		cam.pop_override(&"reveal")
	robot.face.set_expression(&"neutral", 1.0)
	await _wait(1.0)
	robot.busy = false
	if guide:
		guide.appear(robot.global_position)
	island_revealed.emit()


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _dust_puff(at: Vector3) -> void:
	var p := CPUParticles3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.03
	mesh.height = 0.06
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.82, 0.8, 0.76, 0.8)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mesh.material = mat
	p.mesh = mesh
	p.amount = 40
	p.one_shot = true
	p.explosiveness = 0.6
	p.lifetime = 2.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 0.45
	p.direction = Vector3.UP
	p.spread = 70.0
	p.initial_velocity_min = 0.2
	p.initial_velocity_max = 0.6
	p.gravity = Vector3(0, -0.6, 0)
	p.scale_amount_min = 0.6
	p.scale_amount_max = 1.4
	get_tree().current_scene.add_child(p)
	p.global_position = at
	p.emitting = true
	get_tree().create_timer(3.0).timeout.connect(p.queue_free)
