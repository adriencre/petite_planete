extends MeshInstance3D
## Post-effet plein écran des zones endormies (jusqu'à 4). Les lanternes s'y inscrivent.

var _zones: Array[Vector4] = [Vector4.ZERO, Vector4.ZERO, Vector4.ZERO, Vector4.ZERO]
var _eveils: Array[float] = [0.0, 0.0, 0.0, 0.0]
var _nombre := 0


func _ready() -> void:
	add_to_group("zone_endormie")
	var q := QuadMesh.new()
	q.size = Vector2(2, 2)
	mesh = q
	custom_aabb = AABB(Vector3(-1e5, -1e5, -1e5), Vector3(2e5, 2e5, 2e5))
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_maj()


func definir_zone(i: int, centre: Vector3, rayon: float) -> void:
	_zones[i] = Vector4(centre.x, centre.y, centre.z, rayon)
	_nombre = maxi(_nombre, i + 1)
	_maj()


func definir_eveil(i: int, rayon_eveille: float) -> void:
	_eveils[i] = rayon_eveille
	_maj()


func _maj() -> void:
	var m := material_override as ShaderMaterial
	if m == null:
		return
	m.set_shader_parameter("zones", PackedVector4Array(_zones))
	m.set_shader_parameter("eveils", PackedFloat32Array(_eveils))
	m.set_shader_parameter("nombre_zones", _nombre)
