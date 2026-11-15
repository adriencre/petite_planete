extends Control
## Carte de l'île dessinée à l'encre dans le carnet : côtes, falaises, et les lieux découverts
## (icône vide = à faire, icône dorée = fait). Un petit cercle montre où est le robot.

const INK := Color(0.31, 0.25, 0.22, 0.9)
const GOLD := Color(0.78, 0.55, 0.22, 1.0)

var heights := {}            # Vector2i -> hauteur (étage du GridMap)
var cell := Vector2.ONE
var origin := Vector2.ZERO
var places := {}             # id -> {pos, icon, done_icon, done}
var player_pos := Vector3.ZERO
var _bounds := Rect2i()


func refresh() -> void:
	_place_icons()
	if heights.is_empty():
		return
	var lo := Vector2i(1 << 20, 1 << 20)
	var hi := -lo
	for k in heights:
		lo = Vector2i(mini(lo.x, k.x), mini(lo.y, k.y))
		hi = Vector2i(maxi(hi.x, k.x), maxi(hi.y, k.y))
	_bounds = Rect2i(lo - Vector2i(2, 2), hi - lo + Vector2i(5, 5))
	queue_redraw()


func _to_map(world: Vector2) -> Vector2:
	var cells := (world - origin) / cell
	var scale := minf(size.x / _bounds.size.x, size.y / _bounds.size.y)
	var offset := (size - Vector2(_bounds.size) * scale) / 2.0
	return offset + (cells - Vector2(_bounds.position)) * scale


func _draw() -> void:
	if heights.is_empty() or size.x < 20.0 or size.y < 20.0 or _bounds.size.x <= 0:
		return
	var scale := minf(size.x / _bounds.size.x, size.y / _bounds.size.y)
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	# côtes (trait épais) et falaises (trait fin + petites hachures côté bas)
	for k in heights:
		var h: int = heights[k]
		for dir in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = k + dir
			var a := Vector2(k) + Vector2(0.5, 0.5) + Vector2(dir) * 0.5 + Vector2(dir.y, dir.x) * 0.5
			var b := Vector2(k) + Vector2(0.5, 0.5) + Vector2(dir) * 0.5 - Vector2(dir.y, dir.x) * 0.5
			var pa := _cell_to_map(a, scale) + Vector2(rng.randf_range(-0.6, 0.6), rng.randf_range(-0.6, 0.6))
			var pb := _cell_to_map(b, scale) + Vector2(rng.randf_range(-0.6, 0.6), rng.randf_range(-0.6, 0.6))
			if not heights.has(n):
				draw_line(pa, pb, INK, 2.6, true)
				# petites vagues au large
				var off := Vector2(dir) * scale * 0.9
				if rng.randf() < 0.35:
					draw_line(pa + off, pa.lerp(pb, 0.5) + off * 1.1, Color(INK, 0.35), 1.2, true)
			elif heights[n] < h - 1:
				draw_line(pa, pb, Color(INK, 0.75), 1.4, true)
				var mid := pa.lerp(pb, 0.5)
				draw_line(mid, mid + Vector2(dir) * scale * 0.35, Color(INK, 0.45), 1.0, true)
	_place_icons()
	# le robot
	var me := _to_map(Vector2(player_pos.x, player_pos.z))
	draw_arc(me, 6.0, 0, TAU, 20, GOLD, 2.0, true)
	draw_circle(me, 2.2, GOLD)


func _cell_to_map(c: Vector2, scale: float) -> Vector2:
	var offset := (size - Vector2(_bounds.size) * scale) / 2.0
	return offset + (c - Vector2(_bounds.position)) * scale


# Icônes des lieux découverts (vide = à faire, doré = fait), posées comme petites images sur la carte.
func _place_icons() -> void:
	for child in get_children():
		child.queue_free()
	if heights.is_empty() or size.x < 20.0 or _bounds.size.x <= 0:
		return
	for id in places:
		var p: Dictionary = places[id]
		var icon: StringName = p["done_icon"] if p["done"] and p["done_icon"] != &"" else p["icon"]
		var rect := TextureRect.new()
		rect.texture = load("res://assets/ui/map_icons/%s.png" % icon)
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		rect.size = Vector2(30, 30)
		rect.position = _to_map(Vector2(p["pos"].x, p["pos"].z)) - rect.size / 2.0
		rect.modulate = GOLD if p["done"] else INK
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(rect)
