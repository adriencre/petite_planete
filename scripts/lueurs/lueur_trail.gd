@tool
class_name LueurTrail
extends Path3D
## Traînée de Lueurs posée au sol : un chemin lumineux invisible, sauf quand l'antenne faiblit.
## Sert à cacher des chemins et des secrets. Le tracé se modifie en déplaçant les points du chemin.
## Dans l'éditeur, une ligne turquoise montre le tracé.

@export var width := 0.32

var _mesh_instance: MeshInstance3D
var _material: ShaderMaterial
var _gizmo: MeshInstance3D


func _ready() -> void:
	_material = ShaderMaterial.new()
	_material.shader = preload("res://assets/shaders/lueur.gdshader")
	_material.set_shader_parameter("billboard", false)
	_material.set_shader_parameter("round_sprite", false)
	_material.set_shader_parameter("flow", 3.0)
	_material.set_shader_parameter("intensity", 2.0)
	_mesh_instance = MeshInstance3D.new()
	_mesh_instance.material_override = _material
	_mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_mesh_instance, false, Node.INTERNAL_MODE_FRONT)
	if not curve_changed.is_connected(_rebuild):
		curve_changed.connect(_rebuild)
	_rebuild()


func _rebuild() -> void:
	if _mesh_instance == null or curve == null or curve.point_count < 2:
		return
	var length := curve.get_baked_length()
	var steps := maxi(2, int(length / 0.1))
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_normal(Vector3.UP)
	var prev := []
	for i in steps + 1:
		var d := length * i / steps
		var p := curve.sample_baked(d, true)
		var dir := curve.sample_baked(minf(d + 0.1, length), true) - curve.sample_baked(maxf(d - 0.1, 0.0), true)
		dir.y = 0.0
		if dir.length() < 0.001:
			dir = Vector3.FORWARD
		var side := dir.normalized().cross(Vector3.UP) * width * 0.5 * (0.7 + 0.3 * sin(d * 5.0))
		var u := d / length * length * 0.25
		var cur := [p + side, p - side, u]
		if i > 0:
			for v in [[prev[0], Vector2(prev[2], 0)], [prev[1], Vector2(prev[2], 1)], [cur[1], Vector2(u, 1)],
					[prev[0], Vector2(prev[2], 0)], [cur[1], Vector2(u, 1)], [cur[0], Vector2(u, 0)]]:
				st.set_uv(v[1])
				st.add_vertex(v[0])
		prev = cur
	_mesh_instance.mesh = st.commit()
	if Engine.is_editor_hint():
		_draw_gizmo(steps, length)


func _draw_gizmo(steps: int, length: float) -> void:
	if _gizmo == null:
		_gizmo = MeshInstance3D.new()
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color(0.4, 1.0, 0.85)
		_gizmo.material_override = mat
		add_child(_gizmo, false, Node.INTERNAL_MODE_FRONT)
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for i in steps + 1:
		mesh.surface_add_vertex(curve.sample_baked(length * i / steps, true) + Vector3.UP * 0.05)
	mesh.surface_end()
	_gizmo.mesh = mesh
