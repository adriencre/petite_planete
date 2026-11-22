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
## Terrain modélisé dans Blender (ex. tools/blender/terrain_ile_02.py) à la place des terrasses en cubes.
## Il doit suivre la même grille ; ses collisions viennent des suffixes « -col » / « -colonly » du .glb.
## L'herbe pousse sur son mesh « plateaux ».
@export var terrain_modele: PackedScene:
	set(v): terrain_modele = v; _construire()
@export var taille_case: float = 4.0:
	set(v): taille_case = v; _construire()
@export var hauteur_niveau: float = 2.5:
	set(v): hauteur_niveau = v; _construire()
## Hauteur du sol des cases d'estran (« _ »), découvertes seulement à marée basse. = Z_ESTRAN de terrain_ile_02.py.
@export var hauteur_estran: float = 0.1:
	set(v): hauteur_estran = v; _construire()
## Île 1 : la brume « endormie » couvre toute l'île (chassée par les lanternes). Décoché (île 2) :
## pas de grand volume, les nappes et bancs de brume ne sont que sur les cases « b ».
@export var brume_partout: bool = true:
	set(v): brume_partout = v; _construire()
## Brouillard de toute l'île (brume_partout) : densité et hauteur. Décidé le 2026-11-22 : un vrai brouillard,
## épais, qu'on ne traverse pas du regard ; seul le rond de lumière du robot y voit clair.
@export var densite_brume_ile: float = 0.6
@export var hauteur_brume_ile: float = 2.6
## Opacité des nappes au ras du sol (brume_partout).
@export var opacite_nappes: float = 0.5
@export_group("Brume épaisse (cases « b », sans brume_partout)")
## Opacité, couleur et hauteur des nappes de la brume épaisse.
@export_range(0.0, 1.0) var epaisse_opacite: float = 0.78:
	set(v): epaisse_opacite = v; _construire()
@export var epaisse_couleur: Color = Color(0.84, 0.88, 0.95):
	set(v): epaisse_couleur = v; _construire()
@export var epaisse_hauteur: float = 4.0:
	set(v): epaisse_hauteur = v; _construire()
@export_range(2, 12) var epaisse_couches: int = 8:
	set(v): epaisse_couches = v; _construire()
## Voile sur la mer autour (0 à 1) : la brume déborde des cases « b » sur l'eau voisine.
@export_range(0.0, 1.0) var epaisse_debord: float = 0.6:
	set(v): epaisse_debord = v; _construire()
## Jusqu'où (en cases) la brume déborde autour des cases « b », en s'éclaircissant.
@export_range(1, 4) var epaisse_rayon: int = 2:
	set(v): epaisse_rayon = v; _construire()
## Densité des bancs de brume volumétriques (cases « b »). 0 = aucun. Attention : le rond de lumière du robot
## n'écarte pas ce brouillard en volume (seulement les nappes) : trop dense, il noie l'eau et le sol.
@export var densite_bancs: float = 0.07:
	set(v): densite_bancs = v; _construire()
@export_group("")
## Affiche le nom des objets provisoires (en attendant Meshy).
@export var etiquettes: bool = false:
	set(v): etiquettes = v; _construire()
@export var graine: int = 3:
	set(v): graine = v; _construire()
## Pose les objets propres à l'île 1 (lanternes, abri, atelier, barque…) selon les lettres des repères.
## À décocher pour une autre île : les repères ne donnent alors que leur étiquette (et le carnet).
@export var objets_ile_1: bool = true:
	set(v): objets_ile_1 = v; _construire()
## Le titre réutilise les décors de l’île en laissant ses interactions et sa sauvegarde de côté.
@export var decor_seul: bool = false:
	set(v): decor_seul = v; _construire()
@export_group("Nature")
@export var herbe: int = 30000
@export var fleurs: int = 2000
@export_range(0.0, 1.0) var proba_buisson: float = 0.3
@export_range(0.0, 1.0) var proba_rocher: float = 0.25
@export_group("Détails")
## Suite de repères reliés par des dalles (le trajet du joueur), ex. "AP1G2RHNJES".
@export var chemin: String = ""
## Les pas de géants (ILE_01_REVEIL.md §13, 2026-11-18) : suite de repères, ex. "EW". De grandes dalles
## moussues, espacées d'une enjambée de Semeur, en gué sur la rivière : le seul indice de l'atelier.
@export var chemin_geants: String = ""
## Ponts en plus de ceux du chemin : cases de rivière (x = ligne, y = colonne de la carte).
@export var ponts_supplementaires: PackedVector2Array = PackedVector2Array():
	set(v): ponts_supplementaires = v; _construire()
## Enjambée d'un Semeur (2,5 à 3 m de haut), en m.
@export var enjambee: float = 2.4
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
	if not decor_seul:
		_brume()
	var exclus := _nature()
	_vegetation(terrain, exclus)
	_lanternes_ch.clear()
	_reperes()
	_racines()
	_details()
	_vie()
	_ponts()
	_pas_de_geants()   # en dernier : le tirage au sort des autres détails ne change pas


func _lire() -> void:
	_grille = []
	var lignes := carte.strip_edges().split("\n")
	for r in lignes.size():
		var jetons := lignes[r].split(" ", false)
		var rang := []
		for c in jetons.size():
			var j: String = jetons[c]
			var niv := -1 if j[0] in ".~" else int(j[0])
			var y := hauteur_estran if j[0] == "_" else 0.6 + niv * hauteur_niveau  # « _ » : estran (int("_") vaut 0)
			var centre := Vector3((c - jetons.size() * 0.5 + 0.5) * taille_case, y, (r - lignes.size() * 0.5 + 0.5) * taille_case)
			rang.append({"niv": niv, "suf": j.substr(1), "centre": centre})
		_grille.append(rang)


func _case(r: int, c: int) -> Dictionary:
	if r < 0 or r >= _grille.size() or c < 0 or c >= _grille[r].size():
		return {"niv": -1, "suf": "", "centre": Vector3.ZERO}
	return _grille[r][c]


func _terrain() -> MeshInstance3D:
	if terrain_modele != null:
		var modele := terrain_modele.instantiate()
		modele.name = "Terrain"
		add_child(modele)
		return modele.find_child("plateaux*", true, false) as MeshInstance3D
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
## Île 2 : en jeu, la mer monte et descend avec la marée de l'autoload HorlogeMonde.
@export var suit_la_maree: bool = false
## Rectangle local X/Z abrité derrière le seuil maçonné des grottes.
@export var abri_maree := Rect2()
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
	mat.set_shader_parameter("abri_maree", Vector4(abri_maree.position.x, abri_maree.position.y,
			abri_maree.end.x, abri_maree.end.y))
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


func est_abrite_maree(point: Vector3) -> bool:
	var local := to_local(point)
	return abri_maree.has_point(Vector2(local.x, local.z))


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
	if brume_partout:
		_brume_ile()
		_nappes()
	else:
		_brume_epaisse()
	_bancs_de_brume()


## La brume de toute l'île : un grand volume, chassé par les lanternes (shaders/brume_ile.gdshader).
func _brume_ile() -> void:
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
	sm.set_shader_parameter("densite", densite_brume_ile)
	sm.set_shader_parameter("hauteur", hauteur_brume_ile)
	ile.material = sm
	add_child(ile)


## La brume épaisse (cases « b ») : des bancs denses en plus.
func _bancs_de_brume() -> void:
	if densite_bancs <= 0.0:   # île 2 : pas de bancs volumétriques (le rond de lumière du robot ne les écarte pas)
		return
	var mat := FogMaterial.new()
	mat.density = densite_bancs
	mat.albedo = Color(1, 0.93, 0.95)
	mat.edge_fade = 0.4
	for rang in _grille:
		for k in rang:
			if "b" in k.suf:
				var fv := FogVolume.new()
				fv.add_to_group("brume_qui_derive")
				fv.set_meta("origine", k.centre + Vector3.UP * 1.2)
				fv.size = Vector3(taille_case * 1.3, 4.0, taille_case * 1.3) * (1.0 if brume_partout else 1.5)
				fv.material = mat
				fv.position = k.centre + Vector3.UP * 1.2
				add_child(fv)


## La brume épaisse (île 2) : sur chaque case « b », des nappes plus nombreuses, plus hautes et plus
## opaques que les nappes ordinaires (même shader). Elle déborde sur la mer voisine en voile plus léger
## (alpha du sommet = force, lu par le shader). Le robot y creuse son rond de lumière (brume_batterie.gd).
func _brume_epaisse() -> void:
	var force := {}   # Vector2i(ligne, colonne) -> [force, hauteur du sol]
	for r in _grille.size():
		for c in _grille[r].size():
			var k: Dictionary = _grille[r][c]
			if not "b" in str(k.suf):
				continue
			force[Vector2i(r, c)] = [1.0, k.centre.y]
			for dr in range(-epaisse_rayon, epaisse_rayon + 1):
				for dc in range(-epaisse_rayon, epaisse_rayon + 1):
					var v := Vector2i(r + dr, c + dc)
					var kv := _case(v.x, v.y)
					if "b" in str(kv.suf) or epaisse_debord <= 0.0:
						continue
					var sol: float = kv.centre.y
					if kv.niv < 0:
						sol = 0.0                     # la mer
					elif sol > hauteur_estran + 0.2:
						continue                      # la brume ne monte pas sur les plateaux voisins
					var dist := maxi(absi(dr), absi(dc))
					var f := epaisse_debord * (1.0 - float(dist - 1) / float(epaisse_rayon))
					if not force.has(v) or force[v][0] < f:
						force[v] = [f, sol]
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var d := taille_case * 0.85
	var lignes := _grille.size()
	var colonnes: int = _grille[0].size() if lignes > 0 else 0
	for v: Vector2i in force:
		var f: float = force[v][0]
		var sol: float = force[v][1]
		var centre := Vector3((v.y - colonnes * 0.5 + 0.5) * taille_case, sol, (v.x - lignes * 0.5 + 0.5) * taille_case)
		for i in epaisse_couches:
			var t := i / float(epaisse_couches - 1)
			st.set_color(Color(t, 0, 0, f))
			var p := centre + Vector3.UP * lerpf(0.2, epaisse_hauteur, t * t)
			_quad_uv(st, p + Vector3(-d, 0, -d), p + Vector3(d, 0, -d), p + Vector3(d, 0, d), p + Vector3(-d, 0, d))
	var m := MeshInstance3D.new()
	m.name = "BrumeEpaisse"
	m.mesh = st.commit()
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := ShaderMaterial.new()
	mat.shader = BRUME_NAPPES
	mat.set_shader_parameter("opacite", epaisse_opacite)
	mat.set_shader_parameter("couleur", epaisse_couleur)
	mat.set_shader_parameter("echelle", 0.16)
	mat.set_shader_parameter("seuil_bas", 0.34)
	mat.set_shader_parameter("seuil_haut", 0.62)
	m.material_override = mat
	m.add_to_group("brume_ile")
	add_child(m)


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
	mat.set_shader_parameter("opacite", opacite_nappes)
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
			if "w" in k.suf or "^" in k.suf or "v" in k.suf or "<" in k.suf or ">" in k.suf or "X" in k.suf:  # X : le sol de l'atelier
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
				if not objets_ile_1:
					pass
				elif ch in LANTERNES_ZONE:
					var modele_l: PackedScene = LANTERNE
					if ch == "G" and ResourceLoader.exists(LANTERNE_GRANDE):
						modele_l = load(LANTERNE_GRANDE) as PackedScene
					var l: Node3D = modele_l.instantiate()
					l.set_script(LANTERNE_SCRIPT)
					l.decor_seul = decor_seul
					l.ouverture_decor = decor_seul and ch == "G"
					l.premiere_fois = ch == "1"
					l.index_zone = LANTERNES_ZONE.find(ch)
					l.rayon_zone = taille_case * 1.6
					l.position = p
					_lanternes_ch[ch] = l
					if ch == "G":
						l.scale = Vector3.ONE * 1.6
						l.rang = 1
					add_child(l)
					if ch == "G" and not decor_seul:
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
					abri.set_script(ABRI_SCRIPT)
					abri.decor_seul = decor_seul
					abri.position = p
					abri.rotation.y = deg_to_rad(-90)  # la porte (+Z du modèle) regarde l'ouest
					add_child(abri)
				elif ch == "B":
					_barque(p)
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
		if not Engine.is_editor_hint() and not decor_seul:
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
	if not decor_seul:
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
	l.decor_seul = decor_seul
	l.premiere_fois = false
	l.index_zone = -1
	l.rang = 2
	l.position = p
	l.scale = Vector3.ONE * 1.6
	add_child(l)
	# socle : 1,4 m de rayon, 0,8 m de haut en jeu (la prise, à ~1,4 m de l'axe, reste accessible)
	if not decor_seul:
		_collision_cylindres(l, "CollisionLanterneSommet", [Vector3(1.4, 0.8, 0.0)])


func _mat_simple(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 1.0
	return m


## L'atelier des robots : la salle occupe toute sa case, porte au sud (vers le rebord caché).
func _atelier(p: Vector3) -> void:
	if not ResourceLoader.exists(ATELIER):
		_bloc(p + Vector3.UP * 1.2, Vector3(3, 2.4, 3), Color(0.96, 0.9, 0.8))
		return
	var a: Node3D = (load(ATELIER) as PackedScene).instantiate()
	a.name = "Atelier"
	if not decor_seul:
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
	if not decor_seul:
		b.set_script(BARQUE_SCRIPT)
		b.set("maquette", self)
	var pos := p + vers_mer * (taille_case * 0.5 + 1.0)
	pos.y = 0.0   # niveau de la mer : l'origine du modèle est sur sa ligne de flottaison
	b.position = pos
	if vers_mer != Vector3.ZERO:
		var long := vers_mer.cross(Vector3.UP)   # parallèle au rivage
		b.rotation.y = atan2(long.x, long.z)
	if not decor_seul:
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



## Les pas de géants : une dalle par enjambée, à gauche puis à droite comme des pieds, posées
## aussi dans la rivière (elles dépassent de l'eau). Pas sur les marches. Sans collision : le sol
## est déjà marchable dessous.
func _pas_de_geants() -> void:
	if chemin_geants.length() < 2:
		return
	var pos := {}
	for r in _grille.size():
		for c in _grille[r].size():
			for ch in str(_grille[r][c].suf):
				pos[ch] = _grille[r][c].centre
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pied := 0
	for i in chemin_geants.length() - 1:
		if not pos.has(chemin_geants[i]) or not pos.has(chemin_geants[i + 1]):
			continue
		var a: Vector3 = pos[chemin_geants[i]]
		var b: Vector3 = pos[chemin_geants[i + 1]]
		var plat := Vector3(b.x - a.x, 0, b.z - a.z)
		var cote := plat.normalized().cross(Vector3.UP)
		var n := maxi(1, roundi(plat.length() / enjambee))
		for k in n + 1:
			var p := a.lerp(b, float(k) / n) + cote * (0.35 if pied % 2 == 0 else -0.35)
			pied += 1
			var cel := _case_a(p)
			if cel.niv < 0 or "^" in cel.suf or "v" in cel.suf or "<" in cel.suf or ">" in cel.suf:
				continue
			p.y = cel.centre.y - (0.0 if "w" in cel.suf else 0.06)
			_polyedre(st, p, Vector3(_rng.randf_range(1.1, 1.4), 0.22, _rng.randf_range(0.85, 1.05)))
	_ajouter_mesh("PasDeGeants", st, materiau_terrain)


## Les ponts (décidé le 2026-11-22 : on marchait sur la rivière). Un pont de bois (scenes/pont.tscn)
## sur chaque case de rivière que traverse le chemin ; ailleurs, l'eau ne se traverse plus (collision
## invisible), sauf au gué des pas de géants, qui reste le passage secret vers l'atelier.
const PONT := preload("res://scenes/pont.tscn")

func _ponts() -> void:
	var pos := {}
	for r in _grille.size():
		for c in _grille[r].size():
			for ch in str(_grille[r][c].suf):
				pos[ch] = _grille[r][c].centre
	var lignes := _grille.size()
	var colonnes: int = _grille[0].size() if lignes > 0 else 0
	var cle := func(p: Vector3) -> Vector2i:
		return Vector2i(int(floor(p.z / taille_case + lignes * 0.5)), int(floor(p.x / taille_case + colonnes * 0.5)))
	var ponts := {}
	for i in chemin.length() - 1:
		if not pos.has(chemin[i]) or not pos.has(chemin[i + 1]):
			continue
		var a: Vector3 = pos[chemin[i]]
		var b: Vector3 = pos[chemin[i + 1]]
		var n := int(Vector2(b.x - a.x, b.z - a.z).length() / 0.3)
		for k in range(1, n):
			var p := a.lerp(b, float(k) / n)
			if "w" in str(_case_a(p).suf):
				ponts[cle.call(p)] = true
	for v in ponts_supplementaires:
		ponts[Vector2i(int(v.x), int(v.y))] = true
	var gue := {}
	for i in chemin_geants.length() - 1:
		if not pos.has(chemin_geants[i]) or not pos.has(chemin_geants[i + 1]):
			continue
		var a: Vector3 = pos[chemin_geants[i]]
		var b: Vector3 = pos[chemin_geants[i + 1]]
		var n := int(Vector2(b.x - a.x, b.z - a.z).length() / 0.3)
		for k in range(0, n + 1):
			gue[cle.call(a.lerp(b, float(k) / n))] = true
	var d := taille_case * 0.5
	var l := d * 0.7   # demi-largeur de la rivière (comme _eau)
	var barrage := StaticBody3D.new()
	barrage.name = "BergesDeLaRiviere"
	for r in lignes:
		for c in colonnes:
			var k: Dictionary = _grille[r][c]
			if k.niv < 0 or not "w" in str(k.suf):
				continue
			var v := Vector2i(r, c)
			if ponts.has(v):
				var pont: Node3D = PONT.instantiate()
				pont.name = "Pont_%d_%d" % [r, c]
				pont.position = k.centre
				pont.set("longueur", l * 2.0 + 1.4)
				add_child(pont)
				# de part et d'autre du pont, l'eau reste infranchissable
				var largeur_pont: float = float(pont.get("largeur"))
				var reste := (taille_case - largeur_pont) * 0.5
				for sens in [-1.0, 1.0]:
					_bloc_eau(barrage, k.centre + Vector3(0, 0, sens * (largeur_pont * 0.5 + reste * 0.5)), Vector3(l * 2.0, 2.0, reste))
			elif not gue.has(v):
				_bloc_eau(barrage, k.centre, Vector3(l * 2.0, 2.0, taille_case))
	if not Engine.is_editor_hint():
		add_child(barrage)
	else:
		barrage.free()


func _bloc_eau(corps: StaticBody3D, centre: Vector3, taille: Vector3) -> void:
	var boite := BoxShape3D.new()
	boite.size = taille
	var cs := CollisionShape3D.new()
	cs.shape = boite
	cs.position = centre + Vector3.UP * (taille.y * 0.5)
	corps.add_child(cs)


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
	if suit_la_maree and not Engine.is_editor_hint():
		var horloge := get_node_or_null("/root/HorlogeMonde")
		var mer := get_node_or_null("Mer") as Node3D
		if horloge and mer:
			mer.position.y = float(horloge.call("niveau_mer"))
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
