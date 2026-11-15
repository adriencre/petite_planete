@tool
extends Node2D
## Utilisé par WakeManager : dessine chaque zone éveillée comme un disque doux.

var manager: Node
var _disc := _make_disc()


func _ready() -> void:
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	material = mat


func _draw() -> void:
	if manager == null:
		return
	for zone in get_tree().get_nodes_in_group(&"wake_zone"):
		var r: float = zone.current_radius
		if r <= 0.01:
			continue
		var size: Vector2 = manager.to_mask_size(r * 2.0)
		var center: Vector2 = manager.to_mask(zone.global_position)
		draw_texture_rect(_disc, Rect2(center - size * 0.5, size), false)


static func _make_disc() -> GradientTexture2D:
	var g := Gradient.new()
	g.set_offset(0, 0.0)
	g.set_color(0, Color.WHITE)
	g.set_offset(1, 1.0)
	g.set_color(1, Color.BLACK)
	g.add_point(0.7, Color.WHITE)
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5, 0.0)
	tex.width = 128
	tex.height = 128
	return tex
