extends Node3D
## Phare de l'île 2, au loin, éteinte au début. answer() l'allume en vacillant,
## comme si quelqu'un répondait.

@export var energy := 3.0

var answered := false

@onready var _light: OmniLight3D = $Light
@onready var _glow: MeshInstance3D = $Glow


func _ready() -> void:
	_light.light_energy = 0.0
	_glow.visible = false


func answer() -> void:
	if answered:
		return
	answered = true
	var tween := create_tween()
	for e in [0.6, 0.0, 1.0, 0.2, 1.0]:
		tween.tween_callback(_glow.set.bind("visible", e > 0.1))
		tween.tween_property(_light, "light_energy", energy * e, 0.18)
		tween.tween_interval(0.12)
