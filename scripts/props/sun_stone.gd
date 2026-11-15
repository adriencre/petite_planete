class_name SunStone
extends Node3D
## Vieille pierre gravée du symbole « lumière », baignée par le dernier rayon de soleil.
## Le robot y recharge son antenne : c'est là qu'il apprend le symbole qu'il tracera ensuite.

signal charged

@export var flag_id := &"sunstone_used" ## mémorisé d'une boucle à l'autre

var is_used := false

@onready var _interactable: Interactable = $Interactable
@onready var _beam: MeshInstance3D = $Beam
@onready var _glyph_top: Sprite3D = $Stone/GlyphTop
@onready var _glyph_front: Sprite3D = $Stone/GlyphFront
@onready var _focus: Node3D = $CameraFocus


func _ready() -> void:
	add_to_group(&"energy_point")
	_interactable.interacted.connect(_on_use)
	if Loop.has_flag(flag_id):
		# déjà découverte dans une boucle précédente : il suffit de se tenir dans le rayon
		is_used = true
		_interactable.enabled = false
		for g in [_glyph_top, _glyph_front]:
			g.modulate = Color(1.0, 0.86, 0.55)


func antenna_interest(robot: Node3D) -> bool:
	return not is_used and robot.battery.fraction() < 0.9


## Une fois découverte, son rayon recharge vite la batterie.
func recharge_rate(pos: Vector3) -> float:
	if not is_used:
		return 0.0
	var d := Vector2(pos.x - global_position.x, pos.z - global_position.z).length()
	return 30.0 if d < 2.2 else 0.0


func is_done() -> bool:
	return is_used


func _on_use(robot: Node3D) -> void:
	if is_used:
		return
	if robot.night_mode:
		robot.fizzle()  # antenne éteinte : elle ne peut rien recevoir
		return
	is_used = true
	Loop.set_flag(flag_id)
	_interactable.enabled = false
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"sunstone", 6.0, 24.0, 0.8, _focus)
	await robot.face_toward(global_position, 0.4)
	robot.face.set_expression(&"curious", 0.5)
	await get_tree().create_timer(0.6).timeout
	# il lève les bras vers le rayon…
	robot.anim.play(&"recharge", 0.3)
	await get_tree().create_timer(0.7).timeout
	# …la lumière descend en spirale dans son antenne
	var spiral := LightSpiral.play(self, global_position + Vector3(0, 4.0, 0), robot.antenna_tip, 14, 2.6)
	Audio.play("recharge", null, -4.0)
	var glow := create_tween().set_parallel()
	for g in [_glyph_top, _glyph_front]:
		glow.tween_property(g, "modulate", Color(1.0, 0.86, 0.55), 2.0)
	await spiral
	robot.recharge_full()
	robot.face.set_expression(&"surprised", 0.3)
	_flash(robot.antenna_tip.global_position)
	await get_tree().create_timer(1.2).timeout
	var beam := _beam.material_override as ShaderMaterial
	create_tween().tween_method(func(v: float) -> void: beam.set_shader_parameter("intensity", v), 0.55, 0.3, 2.0)
	if cam:
		cam.pop_override(&"sunstone")
	robot.anim.play(&"idle", 0.4)
	await robot.emote(&"happy", &"happy", 1.5)
	robot.busy = false
	charged.emit()


func _flash(at: Vector3) -> void:
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.85, 0.6)
	light.omni_range = 4.0
	light.light_energy = 4.0
	get_tree().current_scene.add_child(light)
	light.global_position = at
	var t := create_tween()
	t.tween_property(light, "light_energy", 0.0, 0.9)
	t.tween_callback(light.queue_free)
