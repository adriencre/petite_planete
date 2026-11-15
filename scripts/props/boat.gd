class_name Boat
extends Node3D
## Barque ensablée qui se met à flotter quand l'eau monte ; le robot peut alors monter dedans.

signal boarded(robot: Node3D)

@export var start_floating := false ## à flot dès le début (on peut partir dès qu'on la trouve)
@export var stranded_offset := Vector3(0, -0.32, 0)
@export var stranded_tilt := 9.0 ## inclinaison quand elle est ensablée (degrés)

var floating := false
var _time := 0.0

@onready var _hull: Node3D = $Hull
@onready var _interactable: Interactable = $Interactable
@onready var seat: Node3D = $Hull/Seat


func _ready() -> void:
	_interactable.enabled = false
	_interactable.interacted.connect(_on_board)
	if start_floating:
		floating = true
		_interactable.enabled = true
		return
	_hull.position = stranded_offset
	_hull.rotation_degrees.z = stranded_tilt


func float_up(duration := 3.0) -> void:
	if floating:
		return
	Audio.play("boat_float", global_position, -2.0)
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	tween.tween_property(_hull, "position", Vector3.ZERO, duration)
	tween.tween_property(_hull, "rotation_degrees:z", 0.0, duration)
	await tween.finished
	floating = true
	_interactable.enabled = true


func _process(delta: float) -> void:
	if not floating:
		return
	_time += delta
	_hull.position.y = sin(_time * 1.3) * 0.04
	_hull.rotation_degrees.z = sin(_time * 0.9) * 1.8


func _on_board(robot: Node3D) -> void:
	if not floating:
		return
	_interactable.enabled = false
	Audio.play("boat_creak", global_position, -4.0)
	boarded.emit(robot)


## Fait avancer la barque vers une position (le robot assis suit).
func sail_to(target: Vector3, duration: float) -> void:
	var tween := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "global_position", target, duration)
	await tween.finished
