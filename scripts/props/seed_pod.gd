class_name SeedPod
extends Node3D
## Cosse fermée qui s'ouvre quand une lanterne s'allume ; le robot peut alors prendre la graine.

@export var opened_by: WakeLantern

var is_open := false

@onready var _petals: Node3D = $Petals
@onready var _seed: Node3D = $Seed
@onready var _interactable: Interactable = $Interactable


func _ready() -> void:
	_interactable.enabled = false
	_interactable.interacted.connect(_on_take)
	if opened_by:
		opened_by.lit_up.connect(open)


func open() -> void:
	if is_open:
		return
	is_open = true
	Audio.play("pod_open", global_position, -4.0)
	var tween := create_tween().set_parallel()
	for petal in _petals.get_children():
		tween.tween_property(petal, "rotation:x", 1.15, 1.0).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(_seed, "position:y", 0.45, 1.2).set_trans(Tween.TRANS_SINE)
	await tween.finished
	_interactable.enabled = true


func _on_take(robot: Node3D) -> void:
	if not is_open or _seed == null:
		return
	_interactable.enabled = false
	robot.pick_up(_seed)
	Audio.play("seed_pickup", null, -6.0)
	_seed = null
	robot.emote(&"curious", &"", 2.5)


## Accompli quand le robot a pris la graine.
func is_done() -> bool:
	return is_open and _seed == null
