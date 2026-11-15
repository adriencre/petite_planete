@tool
extends MeshInstance3D
## Calcule la distance à la côte à partir du GridMap de l'île,
## pour que l'écume de l'eau suive les rives. Visible aussi dans l'éditeur.
## Après avoir repeint l'île : clique sur « Recalculer l'écume ».

@export var island: GridMap
@export var pixels_per_cell := 8
@export var margin_cells := 6
@export var max_distance := 8.0
@export_tool_button("Recalculer l'écume") var rebuild_button := rebuild

var _texture: ImageTexture # gardée ici pour ne pas être sauvegardée dans la scène


func _ready() -> void:
	rebuild()


func rebuild() -> void:
	if island == null or material_override == null:
		return
	# une case est « terre » si un bloc touche la ligne d'eau (étage 0 ou plus)
	var land := {}
	var lo := Vector2i(1 << 20, 1 << 20)
	var hi := -lo
	for c in island.get_used_cells():
		if c.y >= 0:
			land[Vector2i(c.x, c.z)] = true
			lo = Vector2i(mini(lo.x, c.x), mini(lo.y, c.z))
			hi = Vector2i(maxi(hi.x, c.x), maxi(hi.y, c.z))
	if land.is_empty():
		return
	lo -= Vector2i.ONE * margin_cells
	hi += Vector2i.ONE * margin_cells
	var px := pixels_per_cell
	var w := (hi.x - lo.x + 1) * px
	var h := (hi.y - lo.y + 1) * px

	var dist := PackedFloat32Array()
	dist.resize(w * h)
	for y in h:
		for x in w:
			var cell := Vector2i(lo.x + floori(float(x) / px), lo.y + floori(float(y) / px))
			dist[y * w + x] = 0.0 if land.has(cell) else 1e6
	_chamfer(dist, w, h)

	var img := Image.create(w, h, false, Image.FORMAT_RF)
	var to_unit := 1.0 / (px * max_distance)
	for y in h:
		for x in w:
			img.set_pixel(x, y, Color(minf(dist[y * w + x] * to_unit, 1.0), 0, 0))
	_texture = ImageTexture.create_from_image(img)

	var cs := island.cell_size
	var origin := island.global_position + Vector3(lo.x * cs.x, 0, lo.y * cs.z)
	var rid := material_override.get_rid()
	RenderingServer.material_set_param(rid, "dist_tex", _texture.get_rid())
	RenderingServer.material_set_param(rid, "rect", Vector4(origin.x, origin.z, w / float(px) * cs.x, h / float(px) * cs.z))
	RenderingServer.material_set_param(rid, "max_dist", max_distance)


# Distance approchée au pixel de terre le plus proche (deux passes).
func _chamfer(d: PackedFloat32Array, w: int, h: int) -> void:
	const D := 1.4142
	for y in h:
		for x in w:
			var i := y * w + x
			var v := d[i]
			if x > 0: v = minf(v, d[i - 1] + 1.0)
			if y > 0:
				v = minf(v, d[i - w] + 1.0)
				if x > 0: v = minf(v, d[i - w - 1] + D)
				if x < w - 1: v = minf(v, d[i - w + 1] + D)
			d[i] = v
	for y in range(h - 1, -1, -1):
		for x in range(w - 1, -1, -1):
			var i := y * w + x
			var v := d[i]
			if x < w - 1: v = minf(v, d[i + 1] + 1.0)
			if y < h - 1:
				v = minf(v, d[i + w] + 1.0)
				if x < w - 1: v = minf(v, d[i + w + 1] + D)
				if x > 0: v = minf(v, d[i + w - 1] + D)
			d[i] = v
