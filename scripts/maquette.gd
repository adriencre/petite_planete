@tool
extends Node3D
## Construit une île depuis une carte texte (même format que tools/carte_iso.py) :
## terrain (terrasses.gd), eau (rivière + cascades), brume, nature semée, lanternes, pierres-soleil,
## et des blocs provisoires pour les objets qui viendront de Meshy.
## Jeton : chiffre = niveau, "." ou "~" = mer. Suffixes : MAJUSCULES/chiffres = repères (`noms`),
## b = brume, w = eau qui coule (vers le sud), h = bâtiment, ^ v < > = marches, t = arbres.

const TERRASSES := preload("res://scripts/terrasses.gd")
const SEMIS := preload("res://scripts/semis_vegetation.gd")
const LANTERNE := preload("res://assets/models/lanterne_fleur.glb")
const LANTERNE_SCRIPT := preload("res://scripts/lanterne_fleur.gd")
const LANTERNE_SOMMET := preload("res://assets/models/lanterne_semeur.glb")
const ROBOT := preload("res://assets/models/robot_final.glb")

@export_multiline var carte: String = "":
	set(v): carte = v; _construire()
## Lettre du repère -> nom affiché.
@export var noms: Dictionary = {}:
	set(v): noms = v; _construire()
@export var materiau_terrain: Material:
	set(v): materiau_terrain = v; _construire()
@export var taille_case: float = 4.0:
	set(v): taille_case = v; _construire()
@export var hauteur_niveau: float = 2.5:
	set(v): hauteur_niveau = v; _construire()
## Affiche le nom des objets provisoires (en attendant Meshy).
@export var etiquettes: bool = false:
	set(v): etiquettes = v; _construire()
@export var graine: int = 3:
	set(v): graine = v; _construire()
@export_group("Nature")
@export var herbe: int = 30000
@export var fleurs: int = 2000
@export_range(0.0, 1.0) var proba_buisson: float = 0.3
@export_range(0.0, 1.0) var proba_rocher: float = 0.25
@export_group("Détails")
## Suite de repères reliés par des dalles (le trajet du joueur), ex. "AP1G2TRHNJES".
@export var chemin: String = ""
@export var cailloux_par_case: int = 5

const LANTERNES_ZONE := ["1", "2", "3", "G"]  # la zone endormie gère 4 lanternes au plus
const PROVISOIRES := "ATHNJXB"  # objets Meshy à venir : un bloc en attendant

var _rng := RandomNumberGenerator.new()
var _grille: Array = []  # [ligne][colonne] = {niv, suf, centre}


func _ready() -> void:
	_construire()


func _construire() -> void:
	if not is_inside_tree() or carte.strip_edges() == "":
		return
	for c in get_children():
		c.free()
	_rng.seed = graine
	if materiau_terrain is ShaderMaterial:
		materiau_terrain.set_shader_parameter("taille_case", taille_case)
		materiau_terrain.set_shader_parameter("hauteur_niveau", hauteur_niveau)
	_lire()
	var terrain := _terrain()
	_eau()
	_brume()
	var exclus := _nature()
	_vegetation(terrain, exclus)
	_reperes()
	_details()
	_vie()


func _lire() -> void:
	_grille = []
	var lignes := carte.strip_edges().split("\n")
	for r in lignes.size():
		var jetons := lignes[r].split(" ", false)
		var rang := []
		for c in jetons.size():
			var j: String = jetons[c]
			var niv := -1 if j[0] in ".~" else int(j[0])
			var centre := Vector3((c - jetons.size() * 0.5 + 0.5) * taille_case, 0.6 + niv * hauteur_niveau, (r - lignes.size() * 0.5 + 0.5) * taille_case)
			rang.append({"niv": niv, "suf": j.substr(1), "centre": centre})
		_grille.append(rang)


func _case(r: int, c: int) -> Dictionary:
	if r < 0 or r >= _grille.size() or c < 0 or c >= _grille[r].size():
		return {"niv": -1, "suf": "", "centre": Vector3.ZERO}
	return _grille[r][c]


func _terrain() -> MeshInstance3D:
	var lignes := PackedStringArray()
	for rang in _grille:
		var l := PackedStringArray()
		for k in rang:
			var garde := "".join(Array(str(k.suf).split("")).filter(func(ch): return ch in "^v<>t"))
			l.append(("." if k.niv < 0 else str(k.niv)) + garde)
		lignes.append(" ".join(l))
	var t := MeshInstance3D.new()
	t.name = "Terrain"
	t.set_script(TERRASSES)
	add_child(t)
	t.taille_case = taille_case
	t.hauteur_niveau = hauteur_niveau
	t.materiau_terrain = materiau_terrain
	t.carte = "\n".join(lignes)
	return t


## Rivière : un plan sur chaque case « w », et une chute d'eau quand la case au sud est plus basse.
func _eau() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var chutes := SurfaceTool.new()
	chutes.begin(Mesh.PRIMITIVE_TRIANGLES)
	var d := taille_case * 0.5
	for r in _grille.size():
		for c in _grille[r].size():
			var k: Dictionary = _grille[r][c]
			if k.niv < 0 or not "w" in k.suf:
				continue
			var p: Vector3 = k.centre + Vector3.UP * 0.06
			var l := d * 0.7  # la rivière est un peu moins large que la case
			_quad_uv(st, p + Vector3(-l, 0, -d), p + Vector3(l, 0, -d), p + Vector3(l, 0, d), p + Vector3(-l, 0, d))
			var sud := _case(r + 1, c)
			var bas: float = 0.0 if sud.niv < 0 else sud.centre.y
			if sud.niv < k.niv or sud.niv < 0:
				var z: float = p.z + d + 0.08
				_quad_uv(chutes, Vector3(p.x - l, p.y, z), Vector3(p.x + l, p.y, z), Vector3(p.x + l, bas, z), Vector3(p.x - l, bas, z))
	_ajouter_mesh("Riviere", st, _mat_eau(0.6, 6.0))
	_ajouter_mesh("Cascades", chutes, _mat_eau(2.2, 3.0))


func _quad_uv(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, e: Vector3) -> void:
	for pv in [[a, Vector2(0, 0)], [b, Vector2(1, 0)], [c, Vector2(1, 1)], [a, Vector2(0, 0)], [c, Vector2(1, 1)], [e, Vector2(0, 1)]]:
		st.set_uv(pv[1])
		st.add_vertex(pv[0])


func _mat_eau(vitesse: float, bandes: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = preload("res://shaders/eau_riviere.gdshader")
	m.set_shader_parameter("vitesse", vitesse)
	m.set_shader_parameter("bandes", bandes)
	return m


func _brume() -> void:
	var mat := FogMaterial.new()
	mat.density = 0.07
	mat.albedo = Color(1, 0.93, 0.95)
	mat.edge_fade = 0.4
	for rang in _grille:
		for k in rang:
			if "b" in k.suf:
				var fv := FogVolume.new()
				fv.add_to_group("brume_qui_derive")
				fv.set_meta("origine", k.centre + Vector3.UP * 1.2)
				fv.size = Vector3(taille_case * 1.3, 4.0, taille_case * 1.3)
				fv.material = mat
				fv.position = k.centre + Vector3.UP * 1.2
				add_child(fv)


## Rochers à facettes (matériau du terrain : mousse dessus, strates sur les côtés) et buissons.
## Renvoie les zones où l'herbe ne doit pas pousser.
func _nature() -> Array[AABB]:
	var rochers := SurfaceTool.new()
	rochers.begin(Mesh.PRIMITIVE_TRIANGLES)
	var buissons := SurfaceTool.new()
	buissons.begin(Mesh.PRIMITIVE_TRIANGLES)
	var exclus: Array[AABB] = []
	var d := taille_case * 0.5
	for rang in _grille:
		for k in rang:
			if k.niv < 0:
				continue
			var libre: bool = true
			for ch in str(k.suf):
				if ch != "b" and ch != "t":
					libre = false
			if "w" in k.suf or "^" in k.suf or "v" in k.suf or "<" in k.suf or ">" in k.suf:
				exclus.append(AABB(k.centre + Vector3(-d, -1, -d), Vector3(taille_case, 3, taille_case)))
			if not libre:
				continue
			var herbe_ici: bool = k.niv > 0
			if _rng.randf() < proba_rocher:
				var p: Vector3 = k.centre + Vector3(_rng.randf_range(-d, d) * 0.7, 0, _rng.randf_range(-d, d) * 0.7)
				_polyedre(rochers, p, Vector3(_rng.randf_range(0.6, 1.4), _rng.randf_range(0.4, 0.9), _rng.randf_range(0.6, 1.4)))
			if herbe_ici and _rng.randf() < proba_buisson:
				for i in _rng.randi_range(1, 3):
					var p: Vector3 = k.centre + Vector3(_rng.randf_range(-d, d) * 0.75, 0.2, _rng.randf_range(-d, d) * 0.75)
					var s := _rng.randf_range(0.5, 0.9)
					_polyedre(buissons, p, Vector3(s, s * 0.8, s))
	_ajouter_mesh("Rochers", rochers, materiau_terrain)
	var vert := StandardMaterial3D.new()
	vert.albedo_color = Color(0.42, 0.66, 0.42)
	vert.roughness = 1.0
	_ajouter_mesh("Buissons", buissons, vert)
	return exclus


## Icosaèdre déformé à facettes plates, posé sur `base`.
func _polyedre(st: SurfaceTool, base: Vector3, echelle: Vector3) -> void:
	var t := (1.0 + sqrt(5.0)) / 2.0
	var v := [Vector3(-1, t, 0), Vector3(1, t, 0), Vector3(-1, -t, 0), Vector3(1, -t, 0), Vector3(0, -1, t), Vector3(0, 1, t),
		Vector3(0, -1, -t), Vector3(0, 1, -t), Vector3(t, 0, -1), Vector3(t, 0, 1), Vector3(-t, 0, -1), Vector3(-t, 0, 1)]
	for i in v.size():
		v[i] = (v[i].normalized() * _rng.randf_range(0.8, 1.15)) * echelle * 0.5 + base + Vector3.UP * echelle.y * 0.35
	var f := [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
		[3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
	var centre := base + Vector3.UP * echelle.y * 0.35
	for tri in f:
		var a: Vector3 = v[tri[0]]
		var b: Vector3 = v[tri[1]]
		var c: Vector3 = v[tri[2]]
		var n := (b - a).cross(c - a).normalized()
		if n.dot((a + b + c) / 3.0 - centre) > 0.0:  # face avant = sens horaire dans Godot
			var x := b
			b = c
			c = x
		else:
			n = -n
		for p in [a, b, c]:  # n regarde vers l'extérieur dans les deux cas
			st.set_normal(n)
			st.add_vertex(p)


func _ajouter_mesh(nom: String, st: SurfaceTool, mat: Material) -> void:
	var m := st.commit()
	if m.get_surface_count() == 0:
		return
	m.surface_set_material(0, mat)
	var mi := MeshInstance3D.new()
	mi.name = nom
	mi.mesh = m
	add_child(mi)


func _vegetation(terrain: MeshInstance3D, exclus: Array[AABB]) -> void:
	var mat := ShaderMaterial.new()
	mat.shader = preload("res://shaders/vegetation.gdshader")
	for forme in [0, 1]:
		var mm := MultiMeshInstance3D.new()
		mm.name = "Herbe" if forme == 0 else "Fleurs"
		mm.set_script(SEMIS)
		mm.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mm.material_override = mat
		add_child(mm)
		mm.forme = forme
		mm.nombre = herbe if forme == 0 else fleurs
		mm.hauteur = Vector2(0.14, 0.32) if forme == 0 else Vector2(0.5, 0.9)
		mm.pente_min = 0.9
		mm.niveau_eau = 0.6 + hauteur_niveau * 0.5  # pas d'herbe sur la plage
		mm.exclusions = exclus
		mm.graine = graine + forme
		mm.cible = terrain


func _reperes() -> void:
	for rang in _grille:
		for k in rang:
			for ch in str(k.suf):
				if not noms.has(ch):
					continue
				var p: Vector3 = k.centre
				if ch in LANTERNES_ZONE:
					var l: Node3D = LANTERNE.instantiate()
					l.set_script(LANTERNE_SCRIPT)
					l.premiere_fois = ch == "1"
					l.index_zone = LANTERNES_ZONE.find(ch)
					l.rayon_zone = taille_case * 1.6
					l.position = p
					if ch == "G":
						l.scale = Vector3.ONE * 1.6
					add_child(l)
				elif ch == "S":
					var s: Node3D = LANTERNE_SOMMET.instantiate()
					s.position = p
					add_child(s)
					_lumiere(p + Vector3.UP * 2.0, 2.0, 7.0)
				elif ch in "PQ":
					_cristal(p)
				elif ch == "M":
					var corps: Node3D = ROBOT.instantiate()
					corps.position = p + Vector3.UP * 0.3
					corps.rotation = Vector3(deg_to_rad(80), _rng.randf() * TAU, 0)  # couché sur le flanc
					add_child(corps)
				elif ch in PROVISOIRES:
					var taille := Vector3(3, 2.4, 3) if "h" in k.suf else Vector3(1.2, 1.0, 1.2)
					_bloc(p + Vector3.UP * taille.y * 0.5, taille, Color(0.96, 0.9, 0.8))
				if etiquettes:
					var lb := Label3D.new()
					lb.text = str(noms[ch])
					lb.billboard = BaseMaterial3D.BILLBOARD_ENABLED
					lb.no_depth_test = true
					lb.font_size = 48
					lb.pixel_size = 0.01
					lb.outline_size = 10
					lb.position = p + Vector3.UP * 3.0
					add_child(lb)


## Pierre-soleil : un cristal doré à facettes (octaèdre) qui éclaire autour de lui.
func _cristal(p: Vector3) -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	_polyedre(st, p, Vector3(0.9, 1.4, 0.9))
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(1.0, 0.82, 0.4)
	m.emission_enabled = true
	m.emission = Color(1.0, 0.7, 0.3)
	m.emission_energy_multiplier = 1.5
	_ajouter_mesh("PierreSoleil", st, m)
	_lumiere(p + Vector3.UP * 1.2, 1.4, 5.0)


func _lumiere(p: Vector3, energie: float, portee: float) -> void:
	var o := OmniLight3D.new()
	o.light_color = Color(1.0, 0.78, 0.45)
	o.light_energy = energie
	o.omni_range = portee
	o.position = p
	add_child(o)


func _bloc(pos: Vector3, taille: Vector3, couleur: Color) -> void:
	var m := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = taille
	var mat := StandardMaterial3D.new()
	mat.albedo_color = couleur
	b.material = mat
	m.mesh = b
	m.position = pos
	add_child(m)


# --- Petits détails : dalles du chemin, cailloux ---

func _details() -> void:
	var dalles := SurfaceTool.new()
	dalles.begin(Mesh.PRIMITIVE_TRIANGLES)
	var cailloux := SurfaceTool.new()
	cailloux.begin(Mesh.PRIMITIVE_TRIANGLES)
	var d := taille_case * 0.5
	# dalles : tous les ~0.9 m le long du trajet, seulement sur le plat (ni eau, ni marches)
	var pos := {}
	for r in _grille.size():
		for c in _grille[r].size():
			for ch in str(_grille[r][c].suf):
				pos[ch] = _grille[r][c].centre
	for i in chemin.length() - 1:
		if not pos.has(chemin[i]) or not pos.has(chemin[i + 1]):
			continue
		var a: Vector3 = pos[chemin[i]]
		var b: Vector3 = pos[chemin[i + 1]]
		var n := int(Vector2(b.x - a.x, b.z - a.z).length() / 0.9)
		for k in range(1, n):
			var p := a.lerp(b, float(k) / n) + Vector3(_rng.randf_range(-0.25, 0.25), 0, _rng.randf_range(-0.25, 0.25))
			var cel := _case_a(p)
			if cel.niv < 0 or "w" in cel.suf or "^" in cel.suf or "v" in cel.suf or "<" in cel.suf or ">" in cel.suf:
				continue
			p.y = cel.centre.y - 0.05
			_polyedre(dalles, p, Vector3(_rng.randf_range(0.55, 0.8), 0.14, _rng.randf_range(0.45, 0.65)))
	for r in _grille.size():
		for c in _grille[r].size():
			var k: Dictionary = _grille[r][c]
			if k.niv < 0:
				continue
			# cailloux et débris
			if not "w" in k.suf:
				for i in cailloux_par_case:
					var p: Vector3 = k.centre + Vector3(_rng.randf_range(-d, d) * 0.9, -0.04, _rng.randf_range(-d, d) * 0.9)
					var t := _rng.randf_range(0.12, 0.35)
					_polyedre(cailloux, p, Vector3(t, t * 0.7, t))
	var pierre := StandardMaterial3D.new()
	pierre.albedo_color = Color(0.93, 0.87, 0.8)
	pierre.roughness = 1.0
	_ajouter_mesh("Dalles", dalles, pierre)
	_ajouter_mesh("Cailloux", cailloux, materiau_terrain)


## Case de la grille sous un point du monde.
func _case_a(p: Vector3) -> Dictionary:
	var lignes := _grille.size()
	var r := int(floor(p.z / taille_case + lignes * 0.5))
	var c := int(floor(p.x / taille_case + (_grille[0].size() if lignes > 0 else 0) * 0.5))
	return _case(r, c)


# --- La vie : pollen, papillons, oiseaux, écume, brume qui dérive ---

func _process(_delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	var i := 0
	for fv in get_tree().get_nodes_in_group("brume_qui_derive"):
		if fv.get_parent() == self:
			fv.position = fv.get_meta("origine") + Vector3(sin(t * 0.13 + i) * 1.4, 0, cos(t * 0.09 + i * 1.7) * 1.1)
			i += 1


func _vie() -> void:
	var lignes := _grille.size()
	var colonnes: int = _grille[0].size() if lignes > 0 else 0
	var etendue := Vector3(colonnes * taille_case * 0.5, 3.0, lignes * taille_case * 0.5)
	# pollen doré qui flotte partout
	_particules("Pollen", Vector3(0, 4, 0), etendue, 260, Color(1.0, 0.85, 0.45), 0.05, 9.0, Vector3(0, 0.12, 0), 0.25, true)
	# papillons : petits éclats pâles qui volettent près du sol
	_particules("Papillons", Vector3(0, 2.2, 0), Vector3(etendue.x, 1.0, etendue.z), 40, Color(1.0, 0.92, 0.96), 0.12, 6.0, Vector3(0.3, 0.05, 0.2), 0.8, false)
	# écume au pied de chaque cascade
	for r in lignes:
		for c in colonnes:
			var k: Dictionary = _grille[r][c]
			if k.niv < 0 or not "w" in k.suf:
				continue
			var sud := _case(r + 1, c)
			if sud.niv < k.niv or sud.niv < 0:
				var bas: float = 0.0 if sud.niv < 0 else sud.centre.y
				_particules("Ecume", Vector3(k.centre.x, bas + 0.2, k.centre.z + taille_case * 0.5 + 0.4), Vector3(taille_case * 0.3, 0.1, 0.3), 30, Color(1, 1, 1), 0.14, 1.2, Vector3(0, 1.2, 0.6), 0.5, false)
	# oiseaux qui tournent au loin
	var ronde := Node3D.new()
	ronde.name = "Oiseaux"
	ronde.position = Vector3(0, 18, 0)
	ronde.set_script(preload("res://scripts/tourne.gd"))
	add_child(ronde)
	var noir := StandardMaterial3D.new()
	noir.albedo_color = Color(0.35, 0.3, 0.4)
	noir.cull_mode = BaseMaterial3D.CULL_DISABLED
	for i in 4:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for cote in [-1.0, 1.0]:  # deux ailes en V
			st.add_vertex(Vector3.ZERO)
			st.add_vertex(Vector3(cote * 0.7, 0.25, -0.15))
			st.add_vertex(Vector3(cote * 0.7, 0.25, 0.15))
		var o := MeshInstance3D.new()
		o.mesh = st.commit()
		o.material_override = noir
		var angle := i * 0.5
		o.position = Vector3(cos(angle), randf_range(-0.5, 0.5), sin(angle)) * (etendue.x * 1.3 + i * 1.5)
		o.rotation.y = -angle
		ronde.add_child(o)


func _particules(nom: String, centre: Vector3, etendue: Vector3, nombre: int, couleur: Color, taille: float, vie: float, vitesse: Vector3, alea: float, lumineux: bool) -> void:
	var gp := GPUParticles3D.new()
	gp.name = nom
	gp.amount = nombre
	gp.lifetime = vie
	gp.preprocess = vie
	gp.position = centre
	gp.visibility_aabb = AABB(-etendue - Vector3.ONE * 4, etendue * 2 + Vector3.ONE * 8)
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = etendue
	pm.direction = vitesse.normalized() if vitesse.length() > 0.0 else Vector3.UP
	pm.initial_velocity_min = vitesse.length() * 0.5
	pm.initial_velocity_max = vitesse.length()
	pm.spread = 180.0 * alea
	pm.gravity = Vector3(0, -2.0, 0) if nom == "Ecume" else Vector3.ZERO
	pm.turbulence_enabled = nom != "Ecume"
	pm.turbulence_noise_strength = alea
	var fondu := Gradient.new()
	fondu.set_color(0, Color(1, 1, 1, 0))
	fondu.set_color(1, Color(1, 1, 1, 0))
	fondu.add_point(0.2, Color(1, 1, 1, 1))
	fondu.add_point(0.8, Color(1, 1, 1, 1))
	var gt := GradientTexture1D.new()
	gt.gradient = fondu
	pm.color_ramp = gt
	gp.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(taille, taille)
	var m := StandardMaterial3D.new()
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.vertex_color_use_as_albedo = true
	m.albedo_color = couleur
	if lumineux:
		m.emission_enabled = true
		m.emission = couleur
		m.emission_energy_multiplier = 2.0
	q.material = m
	gp.draw_pass_1 = q
	add_child(gp)
