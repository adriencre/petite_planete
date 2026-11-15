class_name Interactable
extends Area3D
## À poser comme enfant de n'importe quel objet utilisable.
## Quand le robot est proche, l'icône de touche apparaît ; `E` émet `interacted`.

signal interacted(robot: Node3D)

@export var enabled := true:
	set(value):
		enabled = value
		if not enabled:
			show_prompt(false)

@onready var _prompt: Node3D = $Prompt


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	show_prompt(false)


func interact(robot: Node3D) -> void:
	if enabled:
		interacted.emit(robot)


func show_prompt(visible_now: bool) -> void:
	if _prompt:
		_prompt.visible = visible_now and enabled


func _on_body_entered(body: Node3D) -> void:
	if body.has_method("register_interactable"):
		body.register_interactable(self)


func _on_body_exited(body: Node3D) -> void:
	if body.has_method("unregister_interactable"):
		body.unregister_interactable(self)
