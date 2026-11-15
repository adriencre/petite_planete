@tool
class_name EnergyVine
extends Path3D
## Racine lumineuse posée au sol : l'énergie y court quand on appelle play().
## Le tracé se modifie dans l'éditeur en déplaçant les points du chemin (Path3D).

signal arrived

@export var width := 0.14
@export var duration := 2.5 ## temps pour aller d'un bout à l'autre (secondes)
@export var color := Color(1.0, 0.82, 0.5)
@export_range(0, 1) var editor_preview := 1.0: ## remplissage montré dans l'éditeur
	set(value):
		editor_preview = value
		if Engine.is_editor_hint():
			_set_progress(value)

var _mesh_instance: MeshInstance3D
var _material: ShaderMaterial


func _ready() -> void:
	_material = ShaderMaterial.new()
	_material.shader = preload("res://assets/shaders/energy_vine.gdshader")
	_material.set_shader_parameter("color", color)
	_mesh_instance = MeshInstance3D.new()
	_mesh_instance.material_override = _material
	_mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_mesh_instance, false, Node.INTERNAL_MODE_FRONT)
	if not curve_changed.is_connected(_rebuild):
		curve_changed.connect(_rebuild)
	_rebuild()
	_set_progress(editor_preview if Engine.is_editor_hint() else 0.0)


## Fait courir l'énergie jusqu'au bout ; se termine à l'arrivée.
func play() -> void:
	var tween := create_tween()
	tween.tween_method(_set_progress, 0.0, 1.0, duration).set_trans(Tween.TRANS_SINE)
	await tween.finished
	arrived.emit()


## L'énergie se retire de la racine (quand la lanterne d'où elle part s'éteint).
func fade_out(time := 1.5) -> void:
	var tween := create_tween()
	tween.tween_method(_set_progress, 1.0, 0.0, time).set_trans(Tween.TRANS_SINE)
	await tween.finished


func _set_progress(value: float) -> void:
	if _material:
		_material.set_shader_parameter("progress", value)


func _rebuild() -> void:
	if _mesh_instance == null:
		return
	if curve == null or curve.point_count < 2:
		_mesh_instance.mesh = null
		return
	var length := curve.get_baked_length()
	var steps := maxi(2, int(length / 0.12))
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_normal(Vector3.UP)
	var prev_l := Vector3.ZERO
	var prev_r := Vector3.ZERO
	var prev_u := 0.0
	for i in steps + 1:
		var d := length * i / steps
		var p := curve.sample_baked(d, true)
		var dir := curve.sample_baked(minf(d + 0.1, length), true) - curve.sample_baked(maxf(d - 0.1, 0.0), true)
		dir.y = 0.0
		if dir.length() < 0.001:
			dir = Vector3.FORWARD
		var side := dir.normalized().cross(Vector3.UP) * width * 0.5
		var wobble := side.normalized() * sin(d * 6.0) * 0.04
		var l := p + side + wobble
		var r := p - side + wobble
		var u := d / length
		if i > 0:
			for v in [[prev_l, Vector2(prev_u, 0)], [prev_r, Vector2(prev_u, 1)], [r, Vector2(u, 1)],
					[prev_l, Vector2(prev_u, 0)], [r, Vector2(u, 1)], [l, Vector2(u, 0)]]:
				st.set_uv(v[1])
				st.add_vertex(v[0])
		prev_l = l
		prev_r = r
		prev_u = u
	_mesh_instance.mesh = st.commit()
