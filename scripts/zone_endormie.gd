extends MeshInstance3D
## Post-effet plein écran des zones endormies (jusqu'à 4). Les lanternes s'y inscrivent.

var _zones: Array[Vector4] = [Vector4.ZERO, Vector4.ZERO, Vector4.ZERO, Vector4.ZERO]
var _eveils: Array[float] = [0.0, 0.0, 0.0, 0.0]
var _nombre := 0
## Combien de fois plus loin on voit quand toutes les zones sont réveillées.
@export var recul_max: float = 3.5
var _env: Environment
var _debut0 := -1.0
var _fin0 := -1.0


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
	var mats: Array[ShaderMaterial] = []
	if material_override is ShaderMaterial:
		mats.append(material_override)
	# la vraie brume (maquette.gd : BrumeIle) se retire en même temps que la zone se réveille
	if is_inside_tree():
		for v in get_tree().get_nodes_in_group("brume_ile"):
			var mat: Material = (v as FogVolume).material if v is FogVolume else (v as GeometryInstance3D).material_override
			if mat is ShaderMaterial:
				mats.append(mat)
	for m in mats:
		m.set_shader_parameter("zones", PackedVector4Array(_zones))
		m.set_shader_parameter("eveils", PackedFloat32Array(_eveils))
		m.set_shader_parameter("nombre_zones", _nombre)
	_reculer_brouillard()


## Le brouillard de distance (Environment, mode profondeur) recule à mesure que l'île se réveille :
## île endormie = on voit à ~25 m ; toutes les zones réveillées = on voit `recul_max` fois plus loin.
func _reculer_brouillard() -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	if _env == null:
		for n in get_tree().current_scene.find_children("*", "WorldEnvironment", true, false):
			_env = (n as WorldEnvironment).environment
			break
		if _env == null:
			return
		_debut0 = _env.fog_depth_begin
		_fin0 = _env.fog_depth_end
	var f := 0.0
	for i in _nombre:
		if _zones[i].w > 0.0:
			f += clampf(_eveils[i] / _zones[i].w, 0.0, 1.0)
	f /= maxf(_nombre, 1)
	_env.fog_depth_begin = _debut0 * lerpf(1.0, recul_max, f)
	_env.fog_depth_end = _fin0 * lerpf(1.0, recul_max, f)
