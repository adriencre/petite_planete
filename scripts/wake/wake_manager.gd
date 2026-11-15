@tool
class_name WakeManager
extends Node
## Dessine, vu de dessus, toutes les WakeZone de la scène dans une petite texture
## (blanc = éveillé) que lisent les shaders du monde (assets/shaders/wake.gdshaderinc).

@export var world_rect := Rect2(-20, -16, 40, 32) ## zone du monde couverte par le masque (x, z)
@export var resolution := 512
@export_group("Brume du sommeil")
@export var mist_start := 3.5 ## distance au robot où la brume commence (mètres)
@export var mist_end := 8.0 ## distance où elle cache tout
@export_range(0, 1) var mist_strength := 1.0
@export var mist_color := Color(0.69, 0.73, 0.79)
@export_group("")
@export var preview_in_editor := false: ## voir l'île endormie dans l'éditeur
	set(value):
		preview_in_editor = value
		_publish()

var _viewport: SubViewport
var _painter: Node2D


func _ready() -> void:
	_viewport = SubViewport.new()
	_viewport.size = Vector2i(resolution, resolution)
	_viewport.disable_3d = true
	_viewport.transparent_bg = false
	_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(_viewport, false, Node.INTERNAL_MODE_FRONT)

	var background := ColorRect.new()
	background.color = Color.BLACK
	background.size = Vector2(resolution, resolution)
	_viewport.add_child(background)

	_painter = Node2D.new()
	_painter.set_script(preload("res://scripts/wake/wake_painter.gd"))
	_painter.manager = self
	_viewport.add_child(_painter)
	_publish()


func _process(_delta: float) -> void:
	if _painter:
		_painter.queue_redraw()
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	if player:
		_set_global(&"player_pos", player.global_position)


func _exit_tree() -> void:
	_set_global(&"wake_enabled", 0.0)


func _publish() -> void:
	if _viewport == null:
		return
	var active := preview_in_editor or not Engine.is_editor_hint()
	_set_global(&"wake_mask", _viewport.get_texture().get_rid())
	_set_global(&"wake_rect",
		Vector4(world_rect.position.x, world_rect.position.y, world_rect.size.x, world_rect.size.y))
	_set_global(&"wake_enabled", 1.0 if active else 0.0)
	_set_global(&"mist_params", Vector4(mist_start, mist_end, mist_strength, 0.0))
	_set_global(&"mist_color", Vector3(mist_color.r, mist_color.g, mist_color.b))


## Convertit une position du monde en pixels du masque.
func to_mask(world: Vector3) -> Vector2:
	return (Vector2(world.x, world.z) - world_rect.position) / world_rect.size * resolution


func to_mask_size(meters: float) -> Vector2:
	return Vector2(meters, meters) / world_rect.size * resolution


# Ne publie que les uniformes globaux déclarés dans project.godot (section [shader_globals]),
# pour éviter des erreurs en boucle si l'éditeur n'a pas encore rechargé le projet.
func _set_global(param: StringName, value: Variant) -> void:
	if Engine.is_editor_hint() and param not in RenderingServer.global_shader_parameter_get_list():
		return
	RenderingServer.global_shader_parameter_set(param, value)
