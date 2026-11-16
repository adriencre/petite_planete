@tool
extends MultiMeshInstance3D
## Sème des touffes d'herbe ou des fleurs sur les faces plates d'un mesh cible.
## Visible dans l'éditeur : changer un réglage régénère.

@export var cible: MeshInstance3D:
	set(v): cible = v; _regenerer()
@export_enum("Herbe", "Fleurs") var forme: int = 0:
	set(v): forme = v; _regenerer()
@export var nombre: int = 5000:
	set(v): nombre = v; _regenerer()
@export_range(0.0, 1.0) var pente_min: float = 0.85:
	set(v): pente_min = v; _regenerer()
@export var hauteur: Vector2 = Vector2(0.2, 0.45):
	set(v): hauteur = v; _regenerer()
@export var couleurs_fleurs: PackedColorArray = PackedColorArray([Color("ffffff"), Color("ff7fa6"), Color("ffc93c"), Color("a98bff"), Color("ff9a6b")]):
	set(v): couleurs_fleurs = v; _regenerer()
@export var graine: int = 1:
	set(v): graine = v; _regenerer()
@export var niveau_eau: float = 0.5
## Boîtes (repère monde) où rien ne pousse : rivière, marches…
@export var exclusions: Array[AABB] = []


func _ready() -> void:
	_regenerer()


func _regenerer() -> void:
	if not is_inside_tree() or cible == null or cible.mesh == null:
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = graine
	var vers_local: Transform3D = global_transform.affine_inverse() * cible.global_transform
	var faces: PackedVector3Array = cible.mesh.get_faces()
	var tris: Array[PackedVector3Array] = []
	var cumul: PackedFloat32Array = []
	var total := 0.0
	for i in range(0, faces.size(), 3):
		var a: Vector3 = vers_local * faces[i]
		var b: Vector3 = vers_local * faces[i + 1]
		var c: Vector3 = vers_local * faces[i + 2]
		var n: Vector3 = (b - a).cross(c - a)
		var aire := n.length() * 0.5
		if aire <= 0.0 or absf(n.normalized().y) < pente_min:
			continue
		total += aire
		tris.append(PackedVector3Array([a, b, c]))
		cumul.append(total)
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = _mesh_touffe() if forme == 0 else _mesh_fleur()
	if tris.is_empty():
		multimesh = mm
		return
	mm.instance_count = nombre
	for k in nombre:
		var idx := cumul.bsearch(rng.randf() * total)
		idx = mini(idx, tris.size() - 1)
		var t := tris[idx]
		var u := rng.randf()
		var v := rng.randf()
		if u + v > 1.0:
			u = 1.0 - u
			v = 1.0 - v
		var pos: Vector3 = t[0] + (t[1] - t[0]) * u + (t[2] - t[0]) * v
		var s := rng.randf_range(hauteur.x, hauteur.y)
		var base_rot := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(s, s, s))
		var gp: Vector3 = global_transform * pos
		if gp.y < niveau_eau or exclusions.any(func(b: AABB) -> bool: return b.has_point(gp)):
			base_rot = base_rot.scaled(Vector3.ZERO)
		mm.set_instance_transform(k, Transform3D(base_rot, pos))
		var col := Color.WHITE
		if forme == 1 and not couleurs_fleurs.is_empty():
			col = couleurs_fleurs[rng.randi() % couleurs_fleurs.size()]
		mm.set_instance_color(k, col)
	multimesh = mm


## Touffe de 7 brins répartis dans un petit disque (UV.y = hauteur, alpha 0 = herbe).
func _mesh_touffe() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var r := RandomNumberGenerator.new()
	r.seed = 42
	for i in 7:
		var ang := r.randf() * TAU
		var dist := sqrt(r.randf()) * 0.16
		var base := Vector3(cos(ang), 0, sin(ang)) * dist
		var a2 := r.randf() * TAU
		var pench := Vector3(cos(a2), 0, sin(a2)) * r.randf_range(0.1, 0.3)
		_brin(st, base, r.randf_range(0.03, 0.05), pench, r.randf_range(0.6, 1.0))
	return st.commit()


func _brin(st: SurfaceTool, base: Vector3, larg: float, pench: Vector3, haut: float) -> void:
	var cote := Vector3(pench.z, 0, -pench.x).normalized() * larg if pench.length() > 0.0 else Vector3.RIGHT * larg
	var segs := 2
	var prev_l := base - cote
	var prev_r := base + cote
	for s in range(1, segs + 1):
		var f := float(s) / segs
		var centre := base + pench * f * f + Vector3.UP * haut * f
		var w := 1.0 - f
		var l := centre - cote * w
		var r := centre + cote * w
		var f0 := float(s - 1) / segs
		for p in [[prev_l, f0], [prev_r, f0], [r, f], [prev_l, f0], [r, f], [l, f]]:
			st.set_color(Color(1, 1, 1, 0))
			st.set_uv(Vector2(0, p[1]))
			st.add_vertex(p[0])
		prev_l = l
		prev_r = r


## Tige (herbe) + tête en petite étoile (alpha 1 = couleur de l'instance).
func _mesh_fleur() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	_brin(st, Vector3.ZERO, 0.012, Vector3(0.03, 0, 0), 0.55)
	var c := Vector3(0.03, 0.56, 0)
	var n := 6
	for i in n:
		var a0 := TAU * i / n
		var a1 := TAU * (i + 0.5) / n
		var a2 := TAU * (i + 1) / n
		var pts := [c, c + Vector3(cos(a0), 0.02, sin(a0)) * 0.07, c + Vector3(cos(a1), 0.0, sin(a1)) * 0.13, c + Vector3(cos(a2), 0.02, sin(a2)) * 0.07]
		for p in [pts[0], pts[1], pts[2], pts[0], pts[2], pts[3]]:
			st.set_color(Color(1, 1, 1, 1))
			st.set_uv(Vector2(0, 1))
			st.add_vertex(p)
	for i in n:
		var a0 := TAU * i / n
		var a1 := TAU * (i + 1) / n
		for p in [c + Vector3(0, 0.03, 0), c + Vector3(cos(a0), 0.25, sin(a0)) * 0.03, c + Vector3(cos(a1), 0.25, sin(a1)) * 0.03]:
			st.set_color(Color(1, 1, 1, 1))
			st.set_uv(Vector2(0, 1))
			st.add_vertex(p)
	return st.commit()
