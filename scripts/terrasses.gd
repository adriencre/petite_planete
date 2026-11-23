@tool
extends MeshInstance3D
## Terrain « maquette » en terrasses, généré depuis une carte texte : falaises droites, angles nets.
## Un jeton par case, séparés par des espaces. Chiffre = niveau du plateau, "." = mer.
## Suffixes : ^ v < > = marches qui montent vers cette direction (^ = nord), t = arbres en cônes.

@export_multiline var carte: String = "":
	set(v): carte = v; _construire()
@export var taille_case: float = 4.0:
	set(v): taille_case = v; _construire()
@export var hauteur_niveau: float = 2.5:
	set(v): hauteur_niveau = v; _construire()
@export var fond_mer: float = -3.0
@export var materiau_terrain: Material:
	set(v): materiau_terrain = v; _construire()
@export var couleur_marches: Color = Color(0.93, 0.80, 0.72)
## Palier plat au pied de chaque escalier (m) : les marches ne commencent pas au bord de la case, là où il
## peut y avoir la mer (2026-11-22 : l'escalier de la pierre-soleil, île 1, finissait dans l'eau).
@export var palier_bas: float = 1.8:
	set(v): palier_bas = v; _construire()
@export var couleur_arbres: Color = Color(0.33, 0.50, 0.42)
## Découpe les parois en pans décalés, avec corniches en surplomb (style maquette).
@export var ebrecher: bool = true:
	set(v): ebrecher = v; _construire()
@export var graine: int = 1:
	set(v): graine = v; _construire()

const DIRS := {"^": Vector2(0, -1), "v": Vector2(0, 1), "<": Vector2(-1, 0), ">": Vector2(1, 0)}

var _niv: Array = []   # niveaux par [ligne][colonne], -1 = mer
var _suf: Array = []
var _col := PackedVector3Array()
var _colonnes: Array[AABB] = []
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_construire()


func hauteur(niveau: int) -> float:
	return 0.6 + niveau * hauteur_niveau


func _construire() -> void:
	if not is_inside_tree() or carte.strip_edges() == "":
		return
	_lire_carte()
	_rng.seed = graine
	_col = PackedVector3Array()
	_colonnes.clear()
	var sol := SurfaceTool.new()
	var marches := SurfaceTool.new()
	var arbres := SurfaceTool.new()
	for s in [sol, marches, arbres]:
		s.begin(Mesh.PRIMITIVE_TRIANGLES)
	var demi := taille_case * 0.5
	for r in _niv.size():
		for c in _niv[r].size():
			var n: int = _niv[r][c]
			if n < 0:
				continue
			var h := hauteur(n)
			var ctr := Vector3((c - _niv[r].size() * 0.5 + 0.5) * taille_case, 0, (r - _niv.size() * 0.5 + 0.5) * taille_case)
			# colonne pleine : ses faces font les falaises ; collision en boîte (plus fiable qu'un mesh concave)
			var mn := ctr + Vector3(-demi, fond_mer, -demi)
			_boite(sol, mn, ctr + Vector3(demi, h, demi), false)
			_colonnes.append(AABB(mn, Vector3(taille_case, h - fond_mer, taille_case)))
			for d: Vector2 in DIRS.values():
				var hn := _haut(r + int(d.y), c + int(d.x))
				if hn >= h:
					continue
				var dv := Vector3(d.x, 0, d.y)
				var perp := Vector3(-d.y, 0, d.x)
				if ebrecher:
					_ebrecher(sol, ctr, dv, perp, maxf(hn, -0.4), h)
				# blocs cubiques au pied et sur le rebord, pour casser les lignes
				if _rng.randf() < 0.45:
					var t := _rng.randf() * (taille_case - 1.6) - demi + 0.8
					var y0 := maxf(hn, -0.4)
					_bloc(sol, ctr + dv * demi + perp * t, dv, y0, _rng.randf_range(0.6, 1.5), 1.0)
				if _rng.randf() < 0.25:
					var t2 := _rng.randf() * (taille_case - 1.6) - demi + 0.8
					_bloc(sol, ctr + dv * demi + perp * t2, -dv, h, _rng.randf_range(0.4, 0.9), 0.5)
			for ch in _suf[r][c]:
				if DIRS.has(ch):
					_escalier(marches, ctr, DIRS[ch], h)
				elif ch == "t":
					for k in 3:
						var p := ctr + Vector3(_rng.randf_range(-1.3, 1.3), h, _rng.randf_range(-1.3, 1.3))
						_cone(arbres, p, _rng.randf_range(0.6, 1.2), _rng.randf_range(2.2, 4.5))
	var m := ArrayMesh.new()
	# une surface vide (pas de marches, pas d'arbres) n'est pas ajoutée : on pose le matériau seulement si elle existe
	for paire in [[sol, materiau_terrain], [marches, _mat(couleur_marches)], [arbres, _mat(couleur_arbres)]]:
		var avant := m.get_surface_count()
		(paire[0] as SurfaceTool).commit(m)
		if m.get_surface_count() > avant:
			m.surface_set_material(avant, paire[1])
	mesh = m
	if not Engine.is_editor_hint():
		_collisions()


func _lire_carte() -> void:
	_niv = []
	_suf = []
	for ligne in carte.strip_edges().split("\n"):
		var niv: Array = []
		var suf: Array = []
		for jeton in ligne.split(" ", false):
			niv.append(-1 if jeton[0] == "." else int(jeton[0]))
			suf.append(jeton.substr(1))
		_niv.append(niv)
		_suf.append(suf)


func _haut(r: int, c: int) -> float:
	if r < 0 or r >= _niv.size() or c < 0 or c >= _niv[r].size() or _niv[r][c] < 0:
		return fond_mer
	return hauteur(_niv[r][c])


## Marches pleine largeur qui montent d'un niveau vers d ; la collision est une rampe lisse.
func _escalier(st: SurfaceTool, ctr: Vector3, d: Vector2, h: float) -> void:
	var dv := Vector3(d.x, 0, d.y)
	var perp := Vector3(-d.y, 0, d.x)
	var demi := taille_case * 0.5
	var palier := clampf(palier_bas, 0.0, taille_case * 0.5)
	var longueur := taille_case - palier
	var nb := maxi(1, roundi(hauteur_niveau / 0.3))
	for i in nb:
		var p0 := ctr + dv * (-demi + palier + i * longueur / nb) - perp * (demi - 0.2)
		var p1 := ctr + dv * (-demi + palier + (i + 1) * longueur / nb) + perp * (demi - 0.2)
		var y1 := h + hauteur_niveau * (i + 1) / nb
		_boite(st, Vector3(minf(p0.x, p1.x), h, minf(p0.z, p1.z)), Vector3(maxf(p0.x, p1.x), y1, maxf(p0.z, p1.z)), false)
	var a := ctr + dv * (-demi + palier) - perp * demi + Vector3.UP * h
	var b := ctr + dv * (-demi + palier) + perp * demi + Vector3.UP * h
	var up := Vector3.UP * hauteur_niveau
	_quad(null, a, b, b + dv * longueur + up, a + dv * longueur + up, Vector3.UP, true)


## Bloc cubique collé à un bord (côté dv), posé à y0.
func _bloc(st: SurfaceTool, bord: Vector3, dv: Vector3, y0: float, s: float, ratio_h: float) -> void:
	var c := bord + dv * s * 0.5
	_boite(st, Vector3(c.x - s * 0.5, y0, c.z - s * 0.5), Vector3(c.x + s * 0.5, y0 + s * ratio_h * _rng.randf_range(0.7, 1.3), c.z + s * 0.5), true)


func _boite(st: SurfaceTool, mn: Vector3, mx: Vector3, col: bool) -> void:
	var p := func(x: float, y: float, z: float) -> Vector3: return Vector3(lerpf(mn.x, mx.x, x), lerpf(mn.y, mx.y, y), lerpf(mn.z, mx.z, z))
	_quad(st, p.call(0, 1, 0), p.call(1, 1, 0), p.call(1, 1, 1), p.call(0, 1, 1), Vector3.UP, col)
	_quad(st, p.call(1, 0, 0), p.call(1, 0, 1), p.call(1, 1, 1), p.call(1, 1, 0), Vector3.RIGHT, col)
	_quad(st, p.call(0, 0, 0), p.call(0, 0, 1), p.call(0, 1, 1), p.call(0, 1, 0), Vector3.LEFT, col)
	_quad(st, p.call(0, 0, 1), p.call(1, 0, 1), p.call(1, 1, 1), p.call(0, 1, 1), Vector3.BACK, col)
	_quad(st, p.call(0, 0, 0), p.call(1, 0, 0), p.call(1, 1, 0), p.call(0, 1, 0), Vector3.FORWARD, col)


func _cone(st: SurfaceTool, base: Vector3, rayon: float, haut: float) -> void:
	var cotes := 5
	var a0 := _rng.randf() * TAU
	var sommet := base + Vector3.UP * haut
	for k in cotes:
		var a := base + Vector3(cos(a0 + TAU * k / cotes), 0, sin(a0 + TAU * k / cotes)) * rayon
		var b := base + Vector3(cos(a0 + TAU * (k + 1) / cotes), 0, sin(a0 + TAU * (k + 1) / cotes)) * rayon
		_tri(st, a, b, sommet, ((a + b) * 0.5 - base).normalized(), true)


func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, n: Vector3, col: bool) -> void:
	_tri(st, a, b, c, n, col)
	_tri(st, a, c, d, n, col)


## Triangle à facette plate ; l'ordre est corrigé pour que la face avant regarde vers `vers`.
func _tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, vers: Vector3, col: bool) -> void:
	var n := (b - a).cross(c - a).normalized()
	if n.dot(vers) > 0.0:  # Godot : face avant = sens horaire, donc normale opposée au produit vectoriel
		var tmp := b
		b = c
		c = tmp
	else:
		n = -n
	if st:
		for p in [a, b, c]:
			st.set_normal(n)
			st.add_vertex(p)
	if col:
		_col.append_array([a, b, c])


func _mat(couleur: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = couleur
	m.roughness = 1.0
	return m


func _collisions() -> void:
	var ancien := get_node_or_null("Collision")
	if ancien:
		ancien.free()
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	var forme := ConcavePolygonShape3D.new()
	forme.set_faces(_col)
	var cs := CollisionShape3D.new()
	cs.shape = forme
	corps.add_child(cs)
	for b in _colonnes:
		var boite := BoxShape3D.new()
		boite.size = b.size
		var cb := CollisionShape3D.new()
		cb.shape = boite
		cb.position = b.get_center()
		corps.add_child(cb)
	add_child(corps)


## Paroi cassée : 3 pans qui avancent plus ou moins et s'arrêtent à des hauteurs différentes,
## parfois une corniche en surplomb sur le rebord.
func _ebrecher(st: SurfaceTool, ctr: Vector3, dv: Vector3, perp: Vector3, y0: float, h: float) -> void:
	var demi := taille_case * 0.5
	var nb := 3
	for i in nb:
		var a := -demi + i * taille_case / nb + _rng.randf_range(0.0, 0.3)
		var b := -demi + (i + 1) * taille_case / nb - _rng.randf_range(0.0, 0.3)
		var avance := _rng.randf_range(0.08, 0.4)
		var haut := h - _rng.randf_range(0.15, 0.9)
		var bas := y0 + _rng.randf_range(0.0, 0.6)
		if haut - bas < 0.4:
			continue
		var p0 := ctr + dv * demi + perp * a
		var p1 := ctr + dv * (demi + avance) + perp * b
		_boite(st, Vector3(minf(p0.x, p1.x), bas, minf(p0.z, p1.z)), Vector3(maxf(p0.x, p1.x), haut, maxf(p0.z, p1.z)), false)
	if _rng.randf() < 0.35:
		var a2 := _rng.randf_range(-demi, demi * 0.2)
		var b2 := a2 + _rng.randf_range(1.0, demi)
		var c0 := ctr + dv * (demi - 0.2) + perp * a2
		var c1 := ctr + dv * (demi + _rng.randf_range(0.25, 0.5)) + perp * minf(b2, demi)
		_boite(st, Vector3(minf(c0.x, c1.x), h - 0.4, minf(c0.z, c1.z)), Vector3(maxf(c0.x, c1.x), h + 0.03, maxf(c0.z, c1.z)), true)
