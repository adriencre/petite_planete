extends MeshInstance3D
## Câble souple entre deux points (monde), qui pend un peu. Ruban toujours face caméra.

const SHADER := preload("res://shaders/cable.gdshader")

var debut := Vector3.ZERO
var fin := Vector3.ZERO
var affaissement := 0.22
var epaisseur := 0.011
var segments := 32
var materiau := ShaderMaterial.new()

var _im := ImmediateMesh.new()


func _init() -> void:
	mesh = _im
	top_level = true
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	materiau.shader = SHADER
	material_override = materiau
	extra_cull_margin = 20.0


func _process(_delta: float) -> void:
	_im.clear_surfaces()
	global_transform = Transform3D.IDENTITY
	if not visible or debut.distance_to(fin) < 0.005:
		return
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var milieu := (debut + fin) * 0.5 + Vector3.DOWN * affaissement * debut.distance_to(fin)
	_im.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	var prec := debut
	for i in segments + 1:
		var t := float(i) / segments
		var u := 1.0 - t
		var p := debut * u * u + milieu * 2.0 * u * t + fin * t * t
		var tg := (p - prec).normalized() if i > 0 else (milieu - debut).normalized()
		var cote := tg.cross((cam.global_position - p).normalized()).normalized() * epaisseur
		_im.surface_set_uv(Vector2(0, t))
		_im.surface_add_vertex(p - cote)
		_im.surface_set_uv(Vector2(1, t))
		_im.surface_add_vertex(p + cote)
		prec = p
	_im.surface_end()
