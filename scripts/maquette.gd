@tool
extends Node3D
## Construit une île depuis une carte texte (même format que tools/carte_iso.py) :
## terrain (terrasses.gd), eau (rivière + cascades), brume, nature semée, lanternes, pierres-soleil,
## et des blocs provisoires pour les objets qui viendront de Meshy.
## Jeton : chiffre = niveau, "." ou "~" = mer. Suffixes : MAJUSCULES/chiffres = repères (`noms`),
## b = brume, w = eau qui coule (vers le sud), h = bâtiment, ^ v < > = marches, t = arbres.

const TERRASSES := preload("res://scripts/terrasses.gd")
const SEMIS := preload("res://scripts/semis_vegetation.gd")
const LANTERNE := preload("res://assets/models/lanterne_tulipe.glb")  # tulipe Meshy découpée par tools/blender/lanterne_tulipe.py
const LANTERNE_SCRIPT := preload("res://scripts/lanterne_fleur.gd")
const LANTERNE_SOMMET_MESHY := "res://assets/models/lanterne_sommet.glb"  # Meshy, découpée par tools/blender/lanterne_sommet.py
const LANTERNE_GRANDE := "res://assets/models/lanterne_grande.glb"  # Meshy, découpée par tools/blender/grande_lanterne.py
const LANTERNE_SOMMET := preload("res://assets/models/lanterne_semeur.glb")
const ROBOT := preload("res://assets/models/robot_final.glb")
const ABRI := preload("res://assets/models/abri.glb")  # abri Meshy découpé par tools/blender/abri.py (Base, Toit, Veilleuse)
const ABRI_SCRIPT := preload("res://scripts/abri.gd")
const PIERRE_SOLEIL := "res://assets/models/pierre_soleil_meshy.glb"  # découpée par tools/blender/pierre_soleil.py
const PIERRE_SCRIPT := preload("res://scripts/pierre_soleil.gd")  # recharge de l'antenne (E)

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
## Suite de repères reliés par des dalles (le trajet du joueur), ex. "AP1G2RHNJES".
@export var chemin: String = ""
@export var cailloux_par_case: int = 5

const LANTERNES_ZONE := ["1", "2", "3", "G"]  # la zone endormie gère 4 lanternes au plus
const BRUME_ILE := preload("res://shaders/brume_ile.gdshader")
const BRUME_NAPPES := preload("res://shaders/brume_nappes.gdshader")
const MER := preload("res://shaders/mer_facettes.gdshader")
const PROVISOIRES := "HNJ"  # bloc de secours si le modèle Meshy manque
## Accessoires du plateau (Meshy, préparés par tools/blender/accessoire.py, origine au sol, face +Z) :
## repère -> [modèle, boîte de collision (L, H, P) en m, rotation Y en degrés].
const ACCESSOIRES := {
	"H": ["res://assets/models/charrette.glb", Vector3(2.6, 1.4, 1.6), -15.0],
	"N": ["res://assets/models/banc.glb", Vector3(3.3, 1.0, 1.3), 0.0],
	"J": ["res://assets/models/jardin.glb", Vector3(3.2, 0.8, 3.2), 0.0],
}
const ATELIER := "res://assets/models/atelier_salle.glb"  # salle creusée, préparée par tools/blender/atelier_salle.py
const ATELIER_SCRIPT := preload("res://scripts/atelier.gd")
const ANCIEN_CORPS := "res://assets/models/ancien_corps.glb"  # le robot figé dans sa chute (tools/blender/ancien_corps.py)
const MOUSSE_ANCIEN := preload("res://shaders/mousse_ancien.gdshader")
const BARQUE := "res://assets/models/barque.glb"  # Meshy, découpée par tools/blender/barque.py
const BARQUE_SCRIPT := preload("res://scripts/barque.gd")  # monter (E), avancer à la lumière (ZQSD), descendre (E)

var _rng := RandomNumberGenerator.new()
var _lanternes_ch: Dictionary = {}   # repère ("1", "2", "3", "G") -> lanterne
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
	_mer()
	_eau()
	_brume()
	var exclus := _nature()
	_vegetation(terrain, exclus)
	_lanternes_ch.clear()
	_reperes()
	_racines()
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


## La mer : un grand plan découpé en petites cases (pour les facettes qui ondulent), au niveau 0.
## Elle reçoit une carte des côtes : la grille de l'île (terre = 1), avec une marge de mer, floutée
## pour faire un halo d'eau claire et d'écume autour du rivage (shaders/mer_facettes.gdshader).
@export_group("Mer")
@export var taille_mer: float = 520.0
@export var cases_mer: int = 208
## Marge de mer (en cases) autour de la grille, dans la carte des côtes.
@export var marge_cote: int = 4
## Finesse de la carte des côtes (pixels par case) et largeur du flou (pixels).
@export var finesse_cote: int = 6
@export var flou_cote: int = 7


func _mer() -> void:
	var lignes := _grille.size()
	var colonnes: int = _grille[0].size() if lignes > 0 else 0
	var mi := MeshInstance3D.new()
	mi.name = "Mer"
	var plan := PlaneMesh.new()
	plan.size = Vector2(taille_mer, taille_mer)
	plan.subdivide_width = cases_mer
	plan.subdivide_depth = cases_mer
	mi.mesh = plan
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := ShaderMaterial.new()
	mat.shader = MER
	# la carte des côtes
	var w := (colonnes + marge_cote * 2) * finesse_cote
	var h := (lignes + marge_cote * 2) * finesse_cote
	var img := Image.create(w, h, false, Image.FORMAT_RF)
	for r in lignes:
		for c in colonnes:
			if _grille[r][c].niv < 0:
				continue
			var x0 := (c + marge_cote) * finesse_cote
			var y0 := (r + marge_cote) * finesse_cote
			img.fill_rect(Rect2i(x0, y0, finesse_cote, finesse_cote), Color(1, 0, 0))
	img = _flouter(img, flou_cote)
	mat.set_shader_parameter("cote", ImageTexture.create_from_image(img))
	var t := taille_case
	mat.set_shader_parameter("cote_rect", Vector4(-(colonnes * 0.5 + marge_cote) * t, -(lignes * 0.5 + marge_cote) * t, (colonnes + marge_cote * 2) * t, (lignes + marge_cote * 2) * t))
	mi.material_override = mat
	add_child(mi)


## Flou en deux passes (horizontal puis vertical) : la carte des côtes devient un halo doux.
func _flouter(img: Image, rayon: int) -> Image:
	var w := img.get_width()
	var h := img.get_height()
	var src := PackedFloat32Array()
	src.resize(w * h)
	for y in h:
		for x in w:
			src[y * w + x] = img.get_pixel(x, y).r
	var tmp := PackedFloat32Array()
	tmp.resize(w * h)
	var n := float(rayon * 2 + 1)
	for y in h:
		for x in w:
			var s := 0.0
			for k in range(-rayon, rayon + 1):
				s += src[y * w + clampi(x + k, 0, w - 1)]
			tmp[y * w + x] = s / n
	var out := Image.create(w, h, false, Image.FORMAT_RF)
	for y in h:
		for x in w:
			var s := 0.0
			for k in range(-rayon, rayon + 1):
				s += tmp[clampi(y + k, 0, h - 1) * w + x]
			out.set_pixel(x, y, Color(s / n, 0, 0))
	return out


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
			# le lit, découpé en petites facettes (6 × 6 par case)
			_grille_uv(st, p + Vector3(-l, 0, -d), p + Vector3(l, 0, -d), p + Vector3(l, 0, d), p + Vector3(-l, 0, d), 6, 6, 0.0)
			var sud := _case(r + 1, c)
			var bas: float = 0.0 if sud.niv < 0 else sud.centre.y
			if sud.niv < k.niv or sud.niv < 0:
				var z: float = p.z + d + 0.08
				var n := maxi(4, int((p.y - bas) * 2.0))
				# deux voiles : celui du fond, plein ; celui de devant, plus léger et un peu plus étroit
				_grille_uv(chutes, Vector3(p.x - l, p.y, z), Vector3(p.x + l, p.y, z), Vector3(p.x + l, bas, z), Vector3(p.x - l, bas, z), 6, n, 0.0)
				var l2 := l * 0.85
				_grille_uv(chutes, Vector3(p.x - l2, p.y + 0.02, z + 0.18), Vector3(p.x + l2, p.y + 0.02, z + 0.18), Vector3(p.x + l2, bas, z + 0.35), Vector3(p.x - l2, bas, z + 0.35), 6, n, 1.0)
	_ajouter_mesh("Riviere", st, _mat_eau(false, 0.8))
	_ajouter_mesh("Cascades", chutes, _mat_eau(true, 1.0))


## Un quadrilatère (a, b en haut ; e, c en bas) découpé en nx × ny cases, avec ses UV (0..1)
## et une couleur de sommet (COLOR.r, pour distinguer les voiles des cascades).
func _grille_uv(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, e: Vector3, nx: int, ny: int, couche: float) -> void:
	var col := Color(couche, 0, 0)
	for j in ny:
		for i in nx:
			var u0 := float(i) / nx
			var u1 := float(i + 1) / nx
			var v0 := float(j) / ny
			var v1 := float(j + 1) / ny
			var coins := [Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v0), Vector2(u1, v1), Vector2(u0, v1)]
			for uv: Vector2 in coins:
				var haut := a.lerp(b, uv.x)
				var bas := e.lerp(c, uv.x)
				st.set_color(col)
				st.set_uv(uv)
				st.add_vertex(haut.lerp(bas, uv.y))


func _quad_uv(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, e: Vector3) -> void:
	for pv in [[a, Vector2(0, 0)], [b, Vector2(1, 0)], [c, Vector2(1, 1)], [a, Vector2(0, 0)], [c, Vector2(1, 1)], [e, Vector2(0, 1)]]:
		st.set_uv(pv[1])
		st.add_vertex(pv[0])


func _mat_eau(chute: bool, vitesse: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = preload("res://shaders/eau_riviere.gdshader")
	m.set_shader_parameter("chute", chute)
	m.set_shader_parameter("vitesse", vitesse)
	if chute:
		m.set_shader_parameter("frisson", 0.04)
	return m


func _brume() -> void:
	# la brume de toute l'île : un grand volume, chassé par les lanternes (shaders/brume_ile.gdshader)
	var lignes := _grille.size()
	var colonnes: int = _grille[0].size() if lignes > 0 else 0
	var ile := FogVolume.new()
	ile.name = "BrumeIle"
	ile.add_to_group("brume_ile")
	ile.size = Vector3(colonnes * taille_case + 8.0, 16.0, lignes * taille_case + 8.0)
	ile.position = Vector3(0, 6.0, 0)
	var sm := ShaderMaterial.new()
	sm.shader = BRUME_ILE
	# la hauteur du sol de chaque case, pour que la brume colle à chaque terrasse
	var sol_max := 20.0
	var img := Image.create(maxi(colonnes, 1), maxi(lignes, 1), false, Image.FORMAT_RF)
	for r in lignes:
		for c in colonnes:
			var k: Dictionary = _grille[r][c]
			img.set_pixel(c, r, Color((0.0 if k.niv < 0 else k.centre.y) / sol_max, 0, 0))
	sm.set_shader_parameter("sol", ImageTexture.create_from_image(img))
	sm.set_shader_parameter("sol_rect", Vector4(-colonnes * taille_case * 0.5, -lignes * taille_case * 0.5, colonnes * taille_case, lignes * taille_case))
	sm.set_shader_parameter("sol_max", sol_max)
	ile.material = sm
	add_child(ile)
	_nappes()
	# la brume épaisse (cases « b ») : des bancs denses en plus
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


## Nappes de brume au ras du sol : 4 couches horizontales sur chaque case de terre (sauf l'abri et
## l'atelier), un peu plus grandes que la case pour se chevaucher. Un seul mesh, un seul matériau.
func _nappes() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var d := taille_case * 0.65
	var hauteurs := [0.35, 0.9, 1.6, 2.5]
	for rang in _grille:
		for k in rang:
			if k.niv < 0 or "h" in k.suf or "X" in k.suf:
				continue
			for i in hauteurs.size():
				st.set_color(Color(i / float(hauteurs.size() - 1), 0, 0))
				var p: Vector3 = k.centre + Vector3.UP * hauteurs[i]
				_quad_uv(st, p + Vector3(-d, 0, -d), p + Vector3(d, 0, -d), p + Vector3(d, 0, d), p + Vector3(-d, 0, d))
	var m := MeshInstance3D.new()
	m.name = "BrumeNappes"
	m.mesh = st.commit()
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := ShaderMaterial.new()
	mat.shader = BRUME_NAPPES
	m.material_override = mat
	m.add_to_group("brume_ile")
	add_child(m)


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
			if "w" in k.suf or "^" in k.suf or "v" in k.suf or "<" in k.suf or ">" in k.suf or "X" in k.suf or "F" in k.suf:  # X : le sol de l'atelier ; F : le dallage de la place
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
					var modele_l: PackedScene = LANTERNE
					if ch == "G" and ResourceLoader.exists(LANTERNE_GRANDE):
						modele_l = load(LANTERNE_GRANDE) as PackedScene
					var l: Node3D = modele_l.instantiate()
					l.set_script(LANTERNE_SCRIPT)
					l.premiere_fois = ch == "1"
					l.index_zone = LANTERNES_ZONE.find(ch)
					l.rayon_zone = taille_case * 1.6
					l.position = p
					_lanternes_ch[ch] = l
					if ch == "G":
						l.scale = Vector3.ONE * 1.6
						l.rang = 1
					add_child(l)
					if ch == "G":
						_collision_grande_lanterne(l)
				elif ch == "S":
					_lanterne_sommet(p)
				elif ch in "PQ":
					_cristal(p)
				elif ch == "M":
					_ancien_corps(p)
				elif ch == "A":
					var abri: Node3D = ABRI.instantiate()
					abri.name = "Abri"
					abri.set_script(ABRI_SCRIPT)  # collisions, marches, toit qui s'efface
					abri.position = p
					abri.rotation.y = deg_to_rad(-90)  # la porte (+Z du modèle) regarde l'ouest
					add_child(abri)
				elif ch == "B":
					_barque(p)
				elif ch == "F":
					_place(p)
				elif ch == "X":
					_atelier(p)
				elif ACCESSOIRES.has(ch) and ResourceLoader.exists(ACCESSOIRES[ch][0]):
					_accessoire(p, ACCESSOIRES[ch])
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


# --- Les racines lumineuses : de la grande lanterne vers chaque petite (ILE_01_REVEIL.md §3) ---

const RACINE := preload("res://shaders/racine.gdshader")
const RACINE_SCRIPT := preload("res://scripts/racine_lumineuse.gd")
@export_group("Racines")
@export var rayon_racine: float = 0.27
@export var cotes_racine: int = 6


## Une racine par petite lanterne : elle serpente au sol depuis le bassin de la grande lanterne,
## grimpe les falaises à la verticale, fait une arche au-dessus de la rivière, et s'affine jusqu'au
## pied de la petite. Des radicelles plongent dans la terre. Low-poly à facettes, sans collision.
func _racines() -> void:
	if not _lanternes_ch.has("G"):
		return
	var g: Vector3 = (_lanternes_ch["G"] as Node3D).position
	for ch in ["1", "2", "3"]:
		if not _lanternes_ch.has(ch):
			continue
		var petite: Node3D = _lanternes_ch[ch]
		var pts := _chemin_racine(petite.position, g)
		if pts.size() < 2:
			continue
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		st.set_smooth_group(0xFFFFFFFF)   # facettes
		# la racine principale : fine côté petite lanterne (0), épaisse côté grande (1)
		var rayons := PackedFloat32Array()
		for i in pts.size():
			var t := float(i) / (pts.size() - 1)
			rayons.append(lerpf(rayon_racine * 0.3, rayon_racine, pow(t, 0.8)) * (0.9 + 0.2 * _rng.randf()))
		_tube(st, pts, rayons, 0.0, 1.0)
		# les radicelles
		var longueur := 0.0
		for i in range(1, pts.size()):
			longueur += pts[i].distance_to(pts[i - 1])
		var n_rad := int(longueur / 1.3)
		for k in n_rad:
			var i := _rng.randi_range(1, pts.size() - 2)
			var t := float(i) / (pts.size() - 1)
			var a: Vector3 = pts[i]
			var dir := (pts[i + 1] - pts[i - 1]).normalized()
			var cote := dir.cross(Vector3.UP).normalized() * (1.0 if _rng.randf() < 0.5 else -1.0)
			var l := _rng.randf_range(0.5, 1.2)
			var sous := PackedVector3Array()
			var r_sous := PackedFloat32Array()
			for j in 5:
				var u := j / 4.0
				var p := a + (cote * 0.9 + dir * _rng.randf_range(-0.3, 0.3)) * l * u
				p.y = a.y - u * u * 0.35   # elle plonge dans la terre
				sous.append(p)
				r_sous.append(lerpf(rayons[i] * 0.45, 0.015, u))
			_tube(st, sous, r_sous, t, t + 0.02)
		var mi := MeshInstance3D.new()
		mi.name = "Racine" + ch
		mi.mesh = st.commit()
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		var mat := ShaderMaterial.new()
		mat.shader = RACINE
		mi.material_override = mat
		if not Engine.is_editor_hint():
			mi.set_script(RACINE_SCRIPT)
			mi.set("lanterne", petite)
		add_child(mi)


## Le chemin d'une racine, de la petite lanterne `a` à la grande `b` : une courbe en S posée sur le sol
## des cases ; à chaque marche de terrasse, elle grimpe la falaise à la verticale ; sur l'eau, une arche.
func _chemin_racine(a: Vector3, b: Vector3) -> PackedVector3Array:
	var vers := Vector3(b.x - a.x, 0, b.z - a.z)
	var dist := vers.length()
	var dir := vers / dist
	var cote := dir.cross(Vector3.UP)
	var amp := _rng.randf_range(0.9, 1.6) * (1.0 if _rng.randf() < 0.5 else -1.0)
	var depart := a + dir * 0.6            # au pied de la petite lanterne
	var arrivee := b - dir * 1.9           # au bord du bassin de la grande
	var longueur := Vector3(arrivee.x - depart.x, 0, arrivee.z - depart.z).length()
	var n := maxi(8, int(longueur / 0.35))
	var pts := PackedVector3Array()
	var y_prec := INF
	for i in n + 1:
		var t := float(i) / n
		var p := depart.lerp(arrivee, t)
		p += cote * (sin(t * PI) * amp + sin(t * PI * 3.0) * 0.25)
		var k := _case_a(p)
		var sol: float = 0.0 if k.niv < 0 else k.centre.y
		var r := lerpf(rayon_racine * 0.3, rayon_racine, t)
		var y := sol + r * 0.35                # à moitié enterrée
		if "w" in str(k.suf):
			y = sol + 0.45                     # une arche au-dessus de l'eau
		if y_prec != INF and absf(y - y_prec) > 0.5:
			# une marche de terrasse : elle grimpe (ou descend) contre la falaise, à la verticale
			var pr: Vector3 = pts[pts.size() - 1]
			var bas := minf(y, y_prec)
			var haut := maxf(y, y_prec)
			var mur := (pr + p) * 0.5
			var recul := dir * (r * 1.2) * (1.0 if y > y_prec else -1.0)   # collée au pied du mur, côté bas
			pts.append(Vector3(mur.x, y_prec, mur.z) - recul)
			pts.append(Vector3(mur.x, (bas + haut) * 0.5, mur.z) - recul)
			pts.append(Vector3(mur.x, y, mur.z) - recul * 0.2)
		pts.append(Vector3(p.x, y, p.z))
		y_prec = y
	return pts


## Un tube low-poly le long de `pts` (rayon par point), avec UV.x de `u0` à `u1` le long du tube.
func _tube(st: SurfaceTool, pts: PackedVector3Array, rayons: PackedFloat32Array, u0: float, u1: float) -> void:
	var n := pts.size()
	var cotes := cotes_racine
	# repères le long du tube (transport parallèle : pas de torsion)
	var normale := Vector3.UP
	var anneaux: Array = []
	var total := 0.0
	var longs := PackedFloat32Array([0.0])
	for i in range(1, n):
		total += pts[i].distance_to(pts[i - 1])
		longs.append(total)
	for i in n:
		var tangente: Vector3 = (pts[mini(i + 1, n - 1)] - pts[maxi(i - 1, 0)]).normalized()
		normale = (normale - tangente * normale.dot(tangente))
		if normale.length() < 0.01:
			normale = tangente.cross(Vector3.RIGHT)
		normale = normale.normalized()
		var bi := tangente.cross(normale)
		var anneau := []
		for c in cotes:
			var ang := TAU * c / cotes
			anneau.append(pts[i] + (normale * cos(ang) + bi * sin(ang)) * rayons[i])
		anneaux.append(anneau)
	for i in n - 1:
		var ua := lerpf(u0, u1, longs[i] / maxf(total, 0.001))
		var ub := lerpf(u0, u1, longs[i + 1] / maxf(total, 0.001))
		for c in cotes:
			var c2 := (c + 1) % cotes
			var va := float(c) / cotes
			var vb := float(c + 1) / cotes
			var p00: Vector3 = anneaux[i][c]
			var p01: Vector3 = anneaux[i][c2]
			var p10: Vector3 = anneaux[i + 1][c]
			var p11: Vector3 = anneaux[i + 1][c2]
			for pv in [[p00, Vector2(ua, va)], [p10, Vector2(ub, va)], [p11, Vector2(ub, vb)], [p00, Vector2(ua, va)], [p11, Vector2(ub, vb)], [p01, Vector2(ua, vb)]]:
				st.set_uv(pv[1])
				st.add_vertex(pv[0])


## Pierre-soleil (modèle Meshy) : son script fait briller le cristal et recharge l'antenne (E).
func _cristal(p: Vector3) -> void:
	var modele := load(PIERRE_SOLEIL) as PackedScene
	if modele == null:  # pas encore importé par l'éditeur
		return
	var pierre: Node3D = modele.instantiate()
	pierre.name = "PierreSoleil"
	pierre.set_script(PIERRE_SCRIPT)
	pierre.position = p
	pierre.rotation.y = _rng.randf() * TAU
	add_child(pierre)


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


## Accessoire du plateau : posé un peu au nord du centre de sa case, pour que le chemin de dalles
## passe devant lui ; une boîte de collision à sa base (en jeu seulement).
func _accessoire(p: Vector3, def: Array) -> void:
	var obj: Node3D = (load(def[0]) as PackedScene).instantiate()
	obj.name = str(def[0]).get_file().get_basename().capitalize()
	obj.position = p + Vector3.FORWARD * taille_case * 0.25
	obj.rotation.y = deg_to_rad(def[2])
	add_child(obj)
	if Engine.is_editor_hint():
		return
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	var boite := BoxShape3D.new()
	boite.size = def[1]
	var cs := CollisionShape3D.new()
	cs.shape = boite
	cs.position = Vector3.UP * def[1].y * 0.5
	corps.add_child(cs)
	obj.add_child(corps)


## Lanterne du sommet : la dernière à allumer (après la grande), sans zone endormie (l'effet n'en
## gère que quatre). Ancien modèle fait main si le modèle Meshy n'est pas encore importé.
func _lanterne_sommet(p: Vector3) -> void:
	if not ResourceLoader.exists(LANTERNE_SOMMET_MESHY):
		var vieux: Node3D = LANTERNE_SOMMET.instantiate()
		vieux.position = p
		add_child(vieux)
		_lumiere(p + Vector3.UP * 2.0, 2.0, 7.0)
		return
	var l: Node3D = (load(LANTERNE_SOMMET_MESHY) as PackedScene).instantiate()
	l.name = "LanterneSommet"
	l.set_script(LANTERNE_SCRIPT)
	l.premiere_fois = false
	l.index_zone = -1
	l.rang = 2
	l.position = p
	l.scale = Vector3.ONE * 1.6
	add_child(l)
	# socle : 1,4 m de rayon, 0,8 m de haut en jeu (la prise, à ~1,4 m de l'axe, reste accessible)
	_collision_cylindres(l, "CollisionLanterneSommet", [Vector3(1.4, 0.8, 0.0)])


## La place des Semeurs, au centre du niveau 1 (repère « F ») : un dallage octogonal, une fontaine à sec
## (bassin, colonne brisée, mousse) et trois bancs de pierre. Pour le peuple caché, c'est « la grande
## place » (ILE_01_REVEIL.md §8) ; pour le robot, un indice muet qu'il y avait de la vie ici.
func _place(p: Vector3) -> void:
	var n := Node3D.new()
	n.name = "Place"
	n.position = p
	add_child(n)
	var dalle := _mat_simple(Color(0.88, 0.83, 0.76))
	var dalle_sombre := _mat_simple(Color(0.78, 0.72, 0.66))
	var pierre := _mat_simple(Color(0.9, 0.86, 0.8))
	var fond := _mat_simple(Color(0.55, 0.5, 0.47))
	var mousse := _mat_simple(Color(0.5, 0.64, 0.4))
	_piece_place(n, dalle_sombre, 2.75, 2.75, 0.06, Vector3(0, 0.03, 0), 8)
	_piece_place(n, dalle, 2.55, 2.55, 0.08, Vector3(0, 0.04, 0), 8)
	# la fontaine : un bassin octogonal à sec, une colonne brisée au milieu
	_piece_place(n, pierre, 1.2, 1.3, 0.55, Vector3(0, 0.33, 0), 8)
	_piece_place(n, fond, 0.95, 0.95, 0.05, Vector3(0, 0.58, 0), 8)
	var colonne := _piece_place(n, pierre, 0.2, 0.26, 1.1, Vector3(0, 1.05, 0), 6)
	colonne.rotation = Vector3(0.12, 0, -0.08)   # un peu de travers
	_piece_place(n, pierre, 0.22, 0.2, 0.35, Vector3(0.55, 0.72, 0.35), 6).rotation = Vector3(1.4, 0.6, 0)   # le morceau tombé
	for i in 4:   # des plaques de mousse sur le rebord
		var a := TAU * (i + 0.3 * _rng.randf()) / 4.0
		_piece_place(n, mousse, 0.32, 0.38, 0.06, Vector3(cos(a) * 1.15, 0.61, sin(a) * 1.15), 5)
	# trois bancs de pierre tournés vers la fontaine
	for i in 3:
		var a := TAU * i / 3.0 + 0.5
		var b := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(1.4, 0.42, 0.45)
		bm.material = pierre
		b.mesh = bm
		b.position = Vector3(cos(a) * 2.05, 0.29, sin(a) * 2.05)
		b.rotation.y = -a + PI * 0.5
		n.add_child(b)
	if Engine.is_editor_hint():
		return
	var corps := StaticBody3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 1.3
	cyl.height = 0.6
	var cs := CollisionShape3D.new()
	cs.shape = cyl
	cs.position = Vector3.UP * 0.3
	corps.add_child(cs)
	n.add_child(corps)


func _mat_simple(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 1.0
	return m


func _piece_place(parent: Node3D, mat: Material, r_haut: float, r_bas: float, haut: float, pos: Vector3, cotes: int) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var c := CylinderMesh.new()
	c.top_radius = r_haut
	c.bottom_radius = r_bas
	c.height = haut
	c.radial_segments = cotes
	c.rings = 1
	c.material = mat
	mi.mesh = c
	mi.position = pos
	parent.add_child(mi)
	return mi


## L'atelier des robots : la salle occupe toute sa case, porte au sud (vers le rebord caché).
func _atelier(p: Vector3) -> void:
	if not ResourceLoader.exists(ATELIER):
		_bloc(p + Vector3.UP * 1.2, Vector3(3, 2.4, 3), Color(0.96, 0.9, 0.8))
		return
	var a: Node3D = (load(ATELIER) as PackedScene).instantiate()
	a.name = "Atelier"
	a.set_script(ATELIER_SCRIPT)
	a.position = p
	add_child(a)


## L'ancien corps de la crique : le robot lui-même (même écharpe, même nœud), tombé là il y a longtemps,
## dans la pose où il s'effondre quand sa batterie meurt ; la mousse pousse dessus (shader en calque).
func _ancien_corps(p: Vector3) -> void:
	if not ResourceLoader.exists(ANCIEN_CORPS):
		var vieux: Node3D = ROBOT.instantiate()
		vieux.position = p + Vector3.UP * 0.3
		vieux.rotation = Vector3(deg_to_rad(80), _rng.randf() * TAU, 0)
		add_child(vieux)
		return
	var corps: Node3D = (load(ANCIEN_CORPS) as PackedScene).instantiate()
	corps.name = "AncienCorps"
	corps.position = p
	corps.rotation.y = _rng.randf() * TAU
	add_child(corps)
	var mousse := ShaderMaterial.new()
	mousse.shader = MOUSSE_ANCIEN
	for m in corps.find_children("*", "MeshInstance3D", true, false):
		(m as MeshInstance3D).material_overlay = mousse


## La barque : à flot dans la mer, contre la falaise de la case « B » (côté mer), parallèle au rivage.
## Elle tangue doucement ; son script gère la lanterne de proue, le câble et la navigation.
func _barque(p: Vector3) -> void:
	if not ResourceLoader.exists(BARQUE):
		_bloc(p + Vector3.UP * 0.5, Vector3(1.2, 1.0, 1.2), Color(0.96, 0.9, 0.8))
		return
	var vers_mer := Vector3.ZERO
	for d: Vector3 in [Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]:
		if _case_a(p + d * taille_case).niv < 0:
			vers_mer = d
			break
	var b: Node3D = (load(BARQUE) as PackedScene).instantiate()
	b.name = "Barque"
	b.set_script(BARQUE_SCRIPT)
	b.set("maquette", self)
	var pos := p + vers_mer * (taille_case * 0.5 + 1.0)
	pos.y = 0.0   # niveau de la mer : l'origine du modèle est sur sa ligne de flottaison
	b.position = pos
	if vers_mer != Vector3.ZERO:
		var long := vers_mer.cross(Vector3.UP)   # parallèle au rivage
		b.rotation.y = atan2(long.x, long.z)
	b.add_to_group("barque_qui_flotte")
	b.set_meta("origine", pos)
	if not Engine.is_editor_hint():
		var corps := StaticBody3D.new()
		corps.name = "CorpsBarque"
		var boite := BoxShape3D.new()
		boite.size = Vector3(1.2, 0.7, 3.0)
		var cs := CollisionShape3D.new()
		cs.shape = boite
		cs.position = Vector3(0, 0.05, -0.1)
		corps.add_child(cs)
		b.add_child(corps)
	add_child(b)


## Collisions de la grande lanterne : le bassin de la fontaine (0,85 m de haut, on ne le traverse
## pas ; face avant à ~1,6 m de l'axe, la prise reste accessible) et le tronc.
func _collision_grande_lanterne(l: Node3D) -> void:
	_collision_cylindres(l, "CollisionGrandeLanterne", [Vector3(1.6, 0.85, 0.0), Vector3(0.4, 3.2, 0.85)])


## Cylindres de collision accrochés à la lanterne (ils la suivent quand elle se pose au sol, et elle
## les ignore pour se poser). Chaque Vector3 = (rayon, hauteur, bas), en mètres dans le jeu.
func _collision_cylindres(l: Node3D, nom: String, cylindres: Array[Vector3]) -> void:
	if Engine.is_editor_hint():
		return
	var e: float = l.scale.x
	var corps := StaticBody3D.new()
	corps.name = nom
	corps.scale = Vector3.ONE / e   # on garde des mesures en mètres malgré l'échelle de la lanterne
	for c in cylindres:
		var cyl := CylinderShape3D.new()
		cyl.radius = c.x
		cyl.height = c.y
		var cs := CollisionShape3D.new()
		cs.shape = cyl
		cs.position = Vector3.UP * (c.z + c.y * 0.5)
		corps.add_child(cs)
	l.add_child(corps)



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
			# cailloux et débris (pas dans l'atelier)
			if not "w" in k.suf and not "X" in k.suf:
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
## Pour le carnet (carnet.gd) : chaque repère nommé de la carte, avec sa position dans le monde.
func reperes_carnet() -> Array:
	var out: Array = []
	for rang in _grille:
		for k in rang:
			for ch in str(k.suf):
				if noms.has(ch):
					out.append({"ch": ch, "nom": str(noms[ch]), "pos": to_global(k.centre)})
	return out


## Pour le carnet : la grille de l'île (niveaux, suffixes) et la taille d'une case.
func carte_carnet() -> Dictionary:
	return {"grille": _grille, "taille": taille_case}


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
	# (la barque tangue elle-même, et s'amarre aux pontons : barque.gd)


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
