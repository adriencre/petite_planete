@tool
class_name RootStairs
extends StaticBody3D
## Escalier de racines : des racines lumineuses sortent du terreau, serpentent et grimpent
## la falaise en s'entortillant, puis les marches gonflent, les feuilles se déplient
## et de petites fleurs éclosent. Ensuite on peut y marcher.
## Dans l'éditeur, il est montré entièrement poussé.

signal grown

@export var start_grown := false

@onready var _tubes: Node3D = $Tubes
@onready var _steps: Node3D = $Steps
@onready var _leaves: Node3D = $Leaves
@onready var _flowers: Node3D = $Flowers
@onready var _collision: CollisionShape3D = $Collision


func _ready() -> void:
	if Engine.is_editor_hint() or start_grown:
		return
	_collision.disabled = true
	for tube in _tubes.get_children():
		tube.growth = 0.0
	for group in [_steps, _leaves, _flowers]:
		for n in group.get_children():
			n.set_meta(&"final_scale", n.scale)
			n.scale = n.scale * 0.01
			n.visible = false


func grow() -> void:
	# 1. les racines sortent et grimpent (décalées les unes des autres)
	var i := 0
	for tube in _tubes.get_children():
		tube.grow(randf_range(2.6, 3.4), i * 0.18)
		i += 1
	# 2. les marches gonflent, du bas vers le haut
	var steps := create_tween()
	steps.tween_interval(2.2)
	for step in _steps.get_children():
		steps.tween_callback(step.set.bind("visible", true))
		steps.tween_property(step, "scale", step.get_meta(&"final_scale", Vector3.ONE), 0.6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		steps.tween_interval(0.05)
	steps.tween_callback(func() -> void: _collision.disabled = false)
	# 3. les feuilles se déplient, 4. les fleurs éclosent
	_pop_all(_leaves, 4.2, 0.12, 0.7)
	get_tree().create_timer(4.2).timeout.connect(func() -> void: Audio.play("leaves_pop", null, -6.0))
	_pop_all(_flowers, 5.4, 0.15, 0.5)
	await get_tree().create_timer(6.4).timeout
	for tube in _tubes.get_children():
		tube.fade_glow(1.8)
	await get_tree().create_timer(1.0).timeout
	grown.emit()


func _pop_all(group: Node3D, start: float, gap: float, duration: float) -> void:
	var k := 0
	for n in group.get_children():
		var final_rot: Vector3 = n.rotation
		n.rotation = final_rot + Vector3(-1.2, 0, 0)
		var t := create_tween()
		t.tween_interval(start + k * gap)
		t.tween_callback(n.set.bind("visible", true))
		t.tween_property(n, "scale", n.get_meta(&"final_scale", Vector3.ONE), duration).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.parallel().tween_property(n, "rotation", final_rot, duration * 1.2).set_trans(Tween.TRANS_SINE)
		k += 1
