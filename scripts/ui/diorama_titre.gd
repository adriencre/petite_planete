extends Node3D
## Dérive lente de la caméra au-dessus de l'île du titre.

@export_range(1.0, 120.0, 0.5) var periode: float = 28.0
@export var derive: Vector3 = Vector3(0.8, 0.36, 0.55)

@onready var _camera: Camera3D = $Camera
@onready var _origine: Vector3 = _camera.position

var _phase := 0.0


func _process(delta: float) -> void:
	_phase = fposmod(_phase + delta * TAU / periode, TAU)
	var balancement := Vector3(sin(_phase), 1.0 - cos(_phase), sin(_phase))
	_camera.position = _origine + derive * balancement
