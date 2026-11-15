@tool
extends Node3D
## Visage du robot : la forme de ses yeux lumineux exprime ce qu'il ressent.
## Expressions : neutral, happy, surprised, curious, sad, off. Il cligne des yeux de temps en temps.

const EXPRESSIONS := {
	# [échelle, position y, rotation z] pour l'œil gauche puis l'œil droit
	&"neutral": [Vector3(1, 1, 1), 0.01, 0.0, Vector3(1, 1, 1), 0.01, 0.0],
	&"happy": [Vector3(1.15, 0.35, 1), 0.045, 0.3, Vector3(1.15, 0.35, 1), 0.045, -0.3],
	&"surprised": [Vector3(1.3, 1.3, 1), 0.015, 0.0, Vector3(1.3, 1.3, 1), 0.015, 0.0],
	&"curious": [Vector3(1.25, 1.2, 1), 0.02, 0.0, Vector3(0.9, 0.65, 1), 0.0, 0.15],
	&"sad": [Vector3(1, 0.55, 1), -0.025, -0.35, Vector3(1, 0.55, 1), -0.025, 0.35],
	&"off": [Vector3(1, 0.12, 1), -0.01, 0.0, Vector3(1, 0.12, 1), -0.01, 0.0],
}

@export_enum("neutral", "happy", "surprised", "curious", "sad", "off") var preview := "neutral":
	set(value):
		preview = value
		if is_inside_tree():
			set_expression(StringName(value), 0.0)

var expression := &"neutral"
var _mat_l: ShaderMaterial
var _mat_r: ShaderMaterial
var _tween: Tween
var _blink_timer := 3.0

@onready var _eye_l: MeshInstance3D = $EyeL
@onready var _eye_r: MeshInstance3D = $EyeR


func _ready() -> void:
	# un matériau par œil : ils peuvent s'allumer l'un après l'autre
	var base := _eye_l.get_surface_override_material(0) as ShaderMaterial
	_mat_l = base.duplicate()
	_mat_r = base.duplicate()
	_eye_l.set_surface_override_material(0, _mat_l)
	_eye_r.set_surface_override_material(0, _mat_r)
	set_expression(StringName(preview) if Engine.is_editor_hint() else &"neutral", 0.0)


func set_expression(name: StringName, duration := 0.25) -> void:
	if not EXPRESSIONS.has(name):
		return
	expression = name
	var e: Array = EXPRESSIONS[name]
	if _tween:
		_tween.kill()
	var glow := 0.0 if name == &"off" else 1.5
	if duration <= 0.0:
		_apply(_eye_l, e[0], e[1], e[2])
		_apply(_eye_r, e[3], e[4], e[5])
		_set_glow(glow, glow)
		return
	_tween = create_tween().set_parallel().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	for pair in [[_eye_l, 0], [_eye_r, 3]]:
		var eye: MeshInstance3D = pair[0]
		var i: int = pair[1]
		_tween.tween_property(eye, "scale", e[i], duration)
		_tween.tween_property(eye, "position:y", e[i + 1], duration)
		_tween.tween_property(eye, "rotation:z", e[i + 2], duration)
	_tween.tween_method(func(v: float) -> void: _set_glow(v, v),
		_mat_l.get_shader_parameter("emission_strength"), glow, duration)


## Les yeux s'allument en vacillant (réveil) : l'œil gauche hésite, puis le droit le suit.
func power_on() -> void:
	expression = &"waking"
	var tween := create_tween()
	# [gauche, droit, durée] : vacillements irréguliers, comme un vieux circuit qui repart
	var steps := [[0.5, 0.0, 0.08], [0.0, 0.0, 0.5], [0.9, 0.0, 0.06], [0.1, 0.0, 0.12], [1.2, 0.0, 1.1],
		[1.2, 0.4, 0.07], [1.2, 0.0, 0.25], [1.2, 0.8, 0.05], [1.2, 0.0, 0.08], [1.5, 1.5, 0.9]]
	tween.tween_callback(func() -> void: Audio.play("power_on", null, -10.0))
	for s in steps:
		tween.tween_callback(_set_glow.bind(s[0], s[1]))
		if s[0] + s[1] > 0.3:
			tween.tween_callback(func() -> void: Audio.play_random("eye_blip", 3, null, -12.0))
		tween.tween_interval(s[2])
	# les yeux s'ouvrent doucement (de fendus à ronds)
	tween.tween_callback(func() -> void: set_expression(&"sad", 0.0))
	tween.tween_interval(0.6)
	await tween.finished
	set_expression(&"surprised", 0.5)


func _process(delta: float) -> void:
	if Engine.is_editor_hint() or expression in [&"off", &"happy", &"waking"]:
		return
	_blink_timer -= delta
	if _blink_timer <= 0.0:
		_blink_timer = randf_range(2.5, 5.5)
		_blink()


func _blink() -> void:
	for eye in [_eye_l, _eye_r]:
		var base_y: float = eye.scale.y
		var t := create_tween()
		t.tween_property(eye, "scale:y", base_y * 0.1, 0.06)
		t.tween_property(eye, "scale:y", base_y, 0.08)


func _set_glow(left: float, right: float) -> void:
	_mat_l.set_shader_parameter("emission_strength", left)
	_mat_r.set_shader_parameter("emission_strength", right)


func _apply(eye: MeshInstance3D, s: Vector3, y: float, rz: float) -> void:
	eye.scale = s
	eye.position.y = y
	eye.rotation.z = rz
