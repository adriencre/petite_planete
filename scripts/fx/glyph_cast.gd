extends Node3D
## Le robot trace un symbole de la langue des Semeurs dans l'air avec son antenne :
## une plume de lumière dessine le glyphe trait par trait (reliée à l'antenne par un fil),
## le glyphe brille, puis se défait en filaments qui volent en arcs jusqu'à la cible.

const STROKES_PATH := "res://assets/ui/glyphs/strokes.json"
const COLOR := Color(1.0, 0.82, 0.5)

static var _strokes_cache := {}

var _strokes: Array = []      # polylignes en mètres (plan local XY)
var _lengths: Array = []
var _total := 0.0
var _drawn := 0.0
var _brightness := 1.0
var _tip: Node3D

@onready var _glyph_mesh: MeshInstance3D = $Glyph
@onready var _link_mesh: MeshInstance3D = $Link
@onready var _pen: Node3D = $Pen
@onready var _pen_light: OmniLight3D = $Pen/Light


func play(glyph: StringName, tip: Node3D, target: Vector3, slow := false) -> void:
	_tip = tip
	var size := 0.8 if slow else 0.55
	_load(glyph, size)
	_face_camera()
	# 1. tracer
	Audio.start_loop(&"glyph", "glyph_draw", -10.0 if slow else -14.0)
	var draw_time := 2.8 if slow else 1.0
	var t := create_tween()
	t.tween_method(_set_drawn, 0.0, _total, draw_time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await t.finished
	_pen.visible = false
	_link_mesh.visible = false
	# 2. le glyphe brille
	var hold := create_tween()
	hold.tween_method(_set_brightness, 1.0, 2.2, 0.35 if slow else 0.15)
	hold.tween_method(_set_brightness, 2.2, 1.4, 0.8 if slow else 0.25)
	await hold.finished
	Audio.stop_loop(&"glyph", 0.5)
	Audio.play("glyph_release", null, -6.0 if slow else -10.0)
	# 3. il se défait en filaments vers la cible
	var count := 14 if slow else 9
	var flight := 1.4 if slow else 0.8
	var last: Signal
	for i in count:
		var p := _point_at(_total * (i + 0.5) / count)
		last = _launch_filament(to_global(p), target, flight, i * (0.07 if slow else 0.035))
	var fade := create_tween()
	fade.tween_method(_set_brightness, 1.4, 0.0, flight * 0.8)
	await last
	get_tree().create_timer(1.2).timeout.connect(queue_free)


func _process(_delta: float) -> void:
	_face_camera()
	if _link_mesh.visible and _tip:
		_draw_link()


# ---------- géométrie du glyphe ----------
func _load(glyph: StringName, size: float) -> void:
	if _strokes_cache.is_empty():
		_strokes_cache = JSON.parse_string(FileAccess.get_file_as_string(STROKES_PATH))
	_strokes.clear()
	_lengths.clear()
	_total = 0.0
	for stroke in _strokes_cache.get(String(glyph), []):
		var pts: Array[Vector3] = []
		for uv in stroke:
			pts.append(Vector3((uv[0] - 0.5) * size, (0.5 - uv[1]) * size, 0.0))
		var length := 0.0
		for i in range(1, pts.size()):
			length += pts[i].distance_to(pts[i - 1])
		_strokes.append(pts)
		_lengths.append(length)
		_total += length


func _point_at(dist: float) -> Vector3:
	var d := dist
	for s in _strokes.size():
		var pts: Array = _strokes[s]
		if d <= _lengths[s]:
			for i in range(1, pts.size()):
				var seg: float = pts[i].distance_to(pts[i - 1])
				if d <= seg:
					return pts[i - 1].lerp(pts[i], d / maxf(seg, 0.0001))
				d -= seg
			return pts[-1]
		d -= _lengths[s]
	return _strokes[-1][-1] if _strokes.size() > 0 else Vector3.ZERO


func _set_drawn(value: float) -> void:
	_drawn = value
	_rebuild()
	_pen.position = _point_at(value)
	_pen_light.light_energy = 1.2 + randf() * 0.4


func _set_brightness(value: float) -> void:
	_brightness = value
	_rebuild()


func _rebuild() -> void:
	var mesh := ImmediateMesh.new()
	var width := 0.035
	var remaining := _drawn
	var col := COLOR * _brightness
	col.a = 1.0
	for s in _strokes.size():
		if remaining <= 0.0:
			break
		var pts: Array = _strokes[s]
		mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
		mesh.surface_set_color(col)
		var acc := 0.0
		for i in pts.size():
			var p: Vector3 = pts[i]
			if i > 0:
				var seg: float = p.distance_to(pts[i - 1])
				if acc + seg > remaining:
					p = pts[i - 1].lerp(p, (remaining - acc) / maxf(seg, 0.0001))
					_strip_point(mesh, pts, i, p, width)
					break
				acc += seg
			_strip_point(mesh, pts, i, p, width)
		mesh.surface_end()
		remaining -= _lengths[s]
	_glyph_mesh.mesh = mesh


func _strip_point(mesh: ImmediateMesh, pts: Array, i: int, p: Vector3, width: float) -> void:
	var a: Vector3 = pts[maxi(i - 1, 0)]
	var b: Vector3 = pts[mini(i + 1, pts.size() - 1)]
	var dir := (b - a).normalized()
	if dir.length() < 0.001:
		dir = Vector3.RIGHT
	var side := Vector3(-dir.y, dir.x, 0.0) * width * 0.5
	mesh.surface_add_vertex(p + side)
	mesh.surface_add_vertex(p - side)


# Fil de lumière entre l'antenne et la plume qui dessine.
func _draw_link() -> void:
	var mesh := ImmediateMesh.new()
	var a := to_local(_tip.global_position)
	var b := _pen.position
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	mesh.surface_set_color(COLOR * 0.7)
	for i in 13:
		var k := i / 12.0
		var p := a.lerp(b, k) + Vector3(0, -sin(k * PI) * 0.06, 0)
		mesh.surface_add_vertex(p + Vector3(0, 0.006, 0))
		mesh.surface_add_vertex(p - Vector3(0, 0.006, 0))
	mesh.surface_end()
	_link_mesh.mesh = mesh


func _face_camera() -> void:
	var cam := get_viewport().get_camera_3d()
	if cam:
		look_at(cam.global_position, Vector3.UP)
		rotate_object_local(Vector3.UP, PI)


# ---------- filaments ----------
func _launch_filament(from: Vector3, to: Vector3, duration: float, delay: float) -> Signal:
	var orb: Node3D = $FilamentTemplate.duplicate()
	get_tree().current_scene.add_child(orb)
	orb.global_position = from
	orb.visible = false
	var side := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)).normalized() * randf_range(0.3, 0.9)
	var lift := randf_range(0.6, 1.4)
	var t := orb.create_tween()
	t.tween_interval(delay)
	t.tween_callback(func() -> void:
		orb.visible = true
		(orb.get_node("Trail") as CPUParticles3D).emitting = true)
	t.tween_method(func(k: float) -> void:
		orb.global_position = from.lerp(to, k) + Vector3.UP * sin(k * PI) * lift + side * sin(k * PI),
		0.0, 1.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_callback(func() -> void:
		(orb.get_node("Trail") as CPUParticles3D).emitting = false
		(orb.get_node("Orb") as Node3D).visible = false)
	t.tween_interval(0.8)
	t.tween_callback(orb.queue_free)
	# renvoie un signal émis à l'arrivée du filament (avant la disparition de sa traînée)
	return get_tree().create_timer(delay + duration).timeout
