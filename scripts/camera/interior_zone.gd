class_name InteriorZone
extends Area3D
## Volume d'un intérieur (abri, grotte…). Quand le robot y entre, les murs et le toit
## entre la caméra et lui s'effacent (vue en coupe), puis reviennent quand il sort.

@export var fade_time := 0.4

static var _inside_count := 0
static var _strength := 0.0
var _tween: Tween


func _ready() -> void:
	collision_layer = 0
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group(&"player"):
		_inside_count += 1
		_fade_to(1.0)


func _on_body_exited(body: Node3D) -> void:
	if body.is_in_group(&"player"):
		_inside_count = maxi(_inside_count - 1, 0)
		if _inside_count == 0:
			_fade_to(0.0)


func _exit_tree() -> void:
	_inside_count = 0
	_strength = 0.0
	RenderingServer.global_shader_parameter_set(&"reveal_strength", 0.0)


func _fade_to(target: float) -> void:
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_method(_set_strength, _strength, target, fade_time)


## 0 = dehors, 1 = à l'intérieur (pour étouffer l'ambiance).
static func inside_amount() -> float:
	return _strength


static func _set_strength(value: float) -> void:
	_strength = value
	RenderingServer.global_shader_parameter_set(&"reveal_strength", value)
