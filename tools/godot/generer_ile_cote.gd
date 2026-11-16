extends SceneTree
## Génère le terrain de la map test « côte découpée » -> res://assets/models/ile_cote.res
## Lancer : godot --headless --path . --script res://tools/godot/generer_ile_cote.gd
## GEO=1 : version géométrique (facettes, terrasses, roches taillées) -> fichiers *_geo.res
## Forme : île allongée, falaise au nord (-Z), plage douce au sud, une baie, une crique, une pointe à l'est.

const TAILLE := Vector2(180.0, 130.0) # emprise en mètres (x, z)
var GEO := OS.get_environment("GEO") == "1"
var RES := 70 if GEO else 260 # sommets par côté en x
var SUFFIXE := "_geo" if GEO else ""
const MARCHE := 2.2 # hauteur d'une terrasse (GEO)
const FOND := -5.0 # profondeur sous la mer
const ALT := 9.0 # hauteur du plateau

var bruit := FastNoiseLite.new()


func _init() -> void:
	bruit.seed = 11
	bruit.frequency = 0.02
	var nx: int = RES
	var nz := int(RES * TAILLE.y / TAILLE.x)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts: Array[Vector3] = []
	for j in nz:
		for i in nx:
			var x := (float(i) / (nx - 1) - 0.5) * TAILLE.x
			var z := (float(j) / (nz - 1) - 0.5) * TAILLE.y
			pts.append(Vector3(x, hauteur(x, z), z))
	for j in nz - 1:
		for i in nx - 1:
			var a := j * nx + i
			for k in [a, a + 1, a + nx, a + 1, a + nx + 1, a + nx]:
				st.add_vertex(pts[k])
	st.generate_normals()
	var mesh := st.commit()
	var err := ResourceSaver.save(mesh, "res://assets/models/ile_cote%s.res" % SUFFIXE)
	assert(err == OK)
	# auto-contrôle : la mer entoure l'île, le plateau est bien au-dessus de l'eau
	assert(hauteur(-TAILLE.x * 0.5, 0.0) < 0.0 and hauteur(0.0, TAILLE.y * 0.5) < 0.0)
	assert(hauteur(-10.0, -15.0) > ALT * 0.7)
	assert(hauteur(0.0, 40.0) < 0.0) # la baie est bien sous l'eau
	print("ile_cote.res : ", pts.size(), " sommets")
	generer_formes()
	quit()


## Ce qu'une carte de hauteur ne sait pas faire : arche, piliers en mer, surplomb de falaise.
## -> res://assets/models/ile_cote_formes.res (déjà placé en coordonnées monde)
func generer_formes() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	# arche au bout de la pointe est : un tore debout à moitié noyé
	var tore := TorusMesh.new()
	tore.inner_radius = 6.0
	tore.outer_radius = 12.0
	tore.rings = 10 if GEO else 48
	tore.ring_segments = 5 if GEO else 20
	var b := Basis.from_euler(Vector3(PI / 2.0, 0.0, 0.0)).scaled(Vector3(1.0, 1.0, 1.5))
	ajouter(st, tore, Transform3D(b, Vector3(98.0, -1.0, 4.0)), 1.6)
	# piliers au pied de la falaise nord
	var cyl := CylinderMesh.new()
	cyl.height = 1.0
	cyl.radial_segments = 6 if GEO else 40 # GEO : colonnes hexagonales
	cyl.rings = 2 if GEO else 30
	for p: Vector3 in [Vector3(-22.0, 13.0, 3.6), Vector3(18.0, 17.0, 4.4), Vector3(32.0, 8.0, 2.4)]: # x, hauteur, rayon
		var z := bord_nord(p.x) - 10.0 - p.z
		ajouter(st, cyl, Transform3D(Basis().scaled(Vector3(p.z, p.y, p.z)), Vector3(p.x, p.y * 0.5 - 4.0, z)), 1.3, true)
	# surplomb : une dalle de roche qui dépasse du haut de la falaise
	var sph := SphereMesh.new()
	sph.radial_segments = 7 if GEO else 48
	sph.rings = 3 if GEO else 24
	var zb := bord_nord(-2.0)
	ajouter(st, sph, Transform3D(Basis().scaled(Vector3(16.0, 2.6, 10.0)), Vector3(-2.0, hauteur(-2.0, zb + 6.0) - 1.2, zb + 1.0)), 1.2)
	st.generate_normals()
	var err := ResourceSaver.save(st.commit(), "res://assets/models/ile_cote_formes%s.res" % SUFFIXE)
	assert(err == OK)
	assert(zb < -25.0 and zb > -50.0) # la falaise nord est bien trouvée
	print("ile_cote_formes.res ok")


## Ajoute une primitive déformée par le bruit (déplacement radial : pas de fissure aux coutures).
func ajouter(st: SurfaceTool, m: PrimitiveMesh, xf: Transform3D, ampl: float, effile := false) -> void:
	var a := m.get_mesh_arrays()
	var v: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
	var idx: PackedInt32Array = a[Mesh.ARRAY_INDEX]
	for i in idx:
		var p := v[i]
		if effile: # piliers : plus fins en haut, avec des « marches » de strates
			p = Vector3(p.x, 0.0, p.z) * lerpf(1.1, 0.65, p.y + 0.5) + Vector3(0.0, p.y, 0.0)
		var w := xf * p
		var dir := (w - xf * Vector3(0.0, p.y if effile else 0.0, 0.0)).normalized()
		if GEO: # grandes facettes : bruit basse fréquence seulement
			w += dir * bruit.get_noise_3dv(w * 1.5) * ampl * 0.8
		else:
			w += dir * (bruit.get_noise_3dv(w * 3.0) * ampl + bruit.get_noise_3dv(w * 9.0) * ampl * 0.3)
		st.add_vertex(w)


## z du bord de la falaise nord pour un x donné (premier point de terre en venant du large).
func bord_nord(x: float) -> float:
	var z := -TAILLE.y * 0.5
	while terre(x, z) <= 0.0 and z < 0.0:
		z += 0.25
	return z


## « Terre » signée : > 0 sur l'île, < 0 en mer.
func terre(x: float, z: float) -> float:
	var w := bruit.get_noise_2d(x, z) * 0.22 + bruit.get_noise_2d(x * 3.1, z * 3.1) * 0.06
	var corps := 1.0 - Vector2(x / 62.0, z / 38.0).length() # ellipse allongée
	var pointe := 1.0 - Vector2((x - 62.0) / 30.0, (z - 4.0) / 8.0).length() # langue de roche à l'est
	var t := maxf(corps, pointe * 0.8) + w
	t -= maxf(0.0, 1.0 - Vector2((x - 2.0) / 16.0, (z - 40.0) / 20.0).length()) * 1.4 # baie au sud
	t -= maxf(0.0, 1.0 - Vector2((x + 38.0) / 9.0, (z - 26.0) / 9.0).length()) * 1.2 # crique au sud-ouest
	return t


func hauteur(x: float, z: float) -> float:
	var t := terre(x, z)
	if t <= 0.0:
		return lerpf(0.0, FOND, clampf(-t * 6.0, 0.0, 1.0))
	var nord := smoothstep(5.0, -20.0, z) # 1 côté falaise, 0 côté plage
	var bord_falaise := smoothstep(0.0, 0.05, t) # mur quasi vertical
	var bord_plage := smoothstep(0.0, 0.45, t) # pente douce
	var h := ALT * lerpf(bord_plage, bord_falaise, nord)
	h += bruit.get_noise_2d(x * 1.7 + 50.0, z * 1.7) * 1.5 * smoothstep(0.1, 0.3, t) # bosses de prairie
	h += smoothstep(0.25, 0.6, t) * 4.0 * maxf(0.0, bruit.get_noise_2d(x * 0.6, z * 0.6 + 90.0)) # collines
	if GEO and h > 1.5: # terrasses nettes
		h = 1.5 + ceilf((h - 1.5) / MARCHE) * MARCHE
	return h
