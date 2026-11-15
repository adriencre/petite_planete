class_name Landmark
extends Area3D
## Lieu remarquable de l'île. La première fois que le robot passe près, il le regarde
## et le dessine dans son carnet (croquis + icône sur la carte).
## Si `done_when` est renseigné (un nœud avec is_done()), le lieu est coché sur la carte une fois accompli.

@export var place_id: StringName
@export var sketch: Texture2D
@export_enum("eye", "lantern", "sun", "soil", "cascade", "house", "boat", "seed", "body", "page") var map_icon := "eye"
@export_enum("none", "lantern_lit", "sun", "seed") var done_icon := "none" ## icône une fois accompli
@export var done_when: Node

var _seen := false


func _ready() -> void:
	collision_layer = 0
	body_entered.connect(_on_enter)
	set_process(done_when != null)


func _on_enter(body: Node3D) -> void:
	if _seen or not body.is_in_group(&"player"):
		return
	_seen = true
	if body.has_method("glance_at"):
		body.glance_at(global_position)
	Notebook.add_place(place_id, sketch, global_position, StringName(map_icon), &"" if done_icon == "none" else StringName(done_icon))


func _process(_delta: float) -> void:
	if done_when and done_when.has_method("is_done") and done_when.is_done():
		Notebook.set_place_done(place_id)
		set_process(false)
