@tool
class_name RootTube
extends Path3D
## Racine en forme de tube le long de ce chemin (modifiable dans l'éditeur en déplaçant les points).
## `growth` (0 → 1) la fait pousser depuis le premier point, avec une pointe lumineuse.

@export var base_radius := 0.09
@export var tip_radius := 0.02
@export_range(0, 1) var growth := 1.0:
	set(value):
		growth = value
		if _material:
			_material.set_shader_parameter("growth", value)
@export_range(0, 1) var glow := 0.0:
	set(value):
		glow = value
		if _material:
			_material.set_shader_parameter("glow", value)

var _mesh_instance: MeshInstance3D
var _material: ShaderMaterial


func _ready() -> void:
	_material = ShaderMaterial.new()
	_material.shader = preload("res://assets/shaders/root_grow.gdshader")
	_mesh_instance = MeshInstance3D.new()
	_mesh_instance.material_override = _material
	add_child(_mesh_instance, false, Node.INTERNAL_MODE_FRONT)
	if not curve_changed.is_connected(_rebuild):
		curve_changed.connect(_rebuild)
	_rebuild()
	growth = growth
	glow = glow


## Fait pousser la racine en `duration` secondes.
func grow(duration := 2.5, delay := 0.0) -> void:
	growth = 0.0
	glow = 1.0
	var t := create_tween()
	t.tween_interval(delay)
	t.tween_property(self, "growth", 1.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await t.finished


func fade_glow(duration := 1.5) -> void:
	create_tween().tween_property(self, "glow", 0.0, duration)


func _rebuild() -> void:
	if _mesh_instance == null:
		return
	if curve == null or curve.point_count < 2:
		_mesh_instance.mesh = null
		return
	var length := curve.get_baked_length()
	var rings := maxi(4, int(length / 0.06))
	const SIDES := 7
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var prev: Array = []
	for i in rings + 1:
		var k := float(i) / rings
		var d := k * length
		var p := curve.sample_baked(d, true)
		var ahead := curve.sample_baked(minf(d + 0.05, length), true)
		var behind := curve.sample_baked(maxf(d - 0.05, 0.0), true)
		var tangent := (ahead - behind).normalized()
		if tangent.length() < 0.001:
			tangent = Vector3.UP
		var side := tangent.cross(Vector3.UP if absf(tangent.y) < 0.95 else Vector3.RIGHT).normalized()
		var up := side.cross(tangent).normalized()
		var radius := lerpf(base_radius, tip_radius, k) * (1.0 + 0.15 * sin(d * 9.0))
		var ring: Array = []
		for j in SIDES + 1:
			var a := TAU * j / SIDES
			var n := (side * cos(a) + up * sin(a)).normalized()
			ring.append([p + n * radius, n, Vector2(k, float(j) / SIDES), radius])
		if i > 0:
			for j in SIDES:
				for v in [prev[j], ring[j], ring[j + 1], prev[j], ring[j + 1], prev[j + 1]]:
					st.set_normal(v[1])
					st.set_uv(v[2])
					st.set_uv2(Vector2(v[3], 0))
					st.add_vertex(v[0])
		prev = ring
	_mesh_instance.mesh = st.commit()
