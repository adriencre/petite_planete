extends Node3D
## Le carnet posé sur l'établi : le robot le ramasse, puis il s'ouvre une première fois.


@onready var _interactable: Interactable = $Interactable


func _ready() -> void:
	if Notebook.is_unlocked:
		queue_free()  # le carnet a déjà été pris lors d'une boucle précédente
		return
	_interactable.interacted.connect(_on_take)


func _on_take(robot: Node3D) -> void:
	_interactable.enabled = false
	robot.face.set_expression(&"curious")
	await robot.face_toward(global_position)
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "global_position", robot.carry_point.global_position, 0.5).set_trans(Tween.TRANS_SINE)
	tween.tween_property(self, "scale", Vector3.ONE * 0.2, 0.5)
	await tween.finished
	visible = false
	Notebook.unlock()
	await get_tree().create_timer(0.3).timeout
	Notebook.open(0)
	queue_free()
