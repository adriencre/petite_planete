@tool
class_name CameraZone
extends Area3D
## Quand le robot est dans cette zone, la caméra prend ces réglages
## (ex. plus serrée dans une clairière, très reculée au sommet pour un panorama).

@export var distance := 11.0
@export_range(10, 89) var pitch_degrees := 42.0
@export var zone_priority := 0 ## si plusieurs zones se chevauchent, la plus haute gagne

var has_player := false


func _enter_tree() -> void:
	add_to_group(&"camera_zone")


func _ready() -> void:
	collision_layer = 0
	if Engine.is_editor_hint():
		return
	body_entered.connect(func(b: Node3D) -> void: if b.is_in_group(&"player"): has_player = true)
	body_exited.connect(func(b: Node3D) -> void: if b.is_in_group(&"player"): has_player = false)
