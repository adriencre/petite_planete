extends Control
## La carte de l'île dans le carnet, dessinée à l'encre : seulement les cases que le robot a vues,
## plus foncées à mesure qu'elles montent (terrasses), l'eau en bleu pâle, un trait d'encre le long des
## falaises et des côtes ; les lieux découverts avec leur nom ; les lanternes allumées en or ; le robot.

const ENCRE := Color(0.33, 0.24, 0.17)
const PAPIER := Color(0.97, 0.93, 0.84)
const OR := Color(0.93, 0.68, 0.25)
const EAU := Color(0.55, 0.74, 0.78, 0.55)
const POLICE := preload("res://assets/fonts/Caveat.ttf")

var grille: Array = []          # [ligne][colonne] = {niv, suf, centre}
var taille_case: float = 6.0
var vu: Dictionary = {}         # Vector2i(colonne, ligne) -> true
var lieux: Array = []           # [{nom, pos}]
var lanternes: Array = []       # [{pos, allumee}]
var robot := Vector3.ZERO


func _cellule(c: int, r: int) -> Dictionary:
	if r < 0 or r >= grille.size() or c < 0 or c >= grille[r].size():
		return {"niv": -1, "suf": ""}
	return grille[r][c]


func _draw() -> void:
	if grille.is_empty():
		return
	var lignes := grille.size()
	var colonnes: int = grille[0].size()
	var cote: float = minf(size.x / colonnes, size.y / lignes)
	var origine := (size - Vector2(colonnes, lignes) * cote) * 0.5
	var vers_carte := func(p: Vector3) -> Vector2:
		return origine + Vector2(p.x / taille_case + colonnes * 0.5, p.z / taille_case + lignes * 0.5) * cote
	# les cases vues
	for r in lignes:
		for c in colonnes:
			var k := _cellule(c, r)
			if k.niv < 0 or not vu.has(Vector2i(c, r)):
				continue
			var rect := Rect2(origine + Vector2(c, r) * cote, Vector2(cote, cote))
			draw_rect(rect, PAPIER.lerp(ENCRE, 0.07 + k.niv * 0.06))
			if "w" in str(k.suf):
				draw_rect(rect.grow(-cote * 0.18), EAU)
	# le trait d'encre : là où le niveau change (falaise, côte), légèrement tremblé
	for r in lignes:
		for c in colonnes:
			var k := _cellule(c, r)
			if k.niv < 0 or not vu.has(Vector2i(c, r)):
				continue
			var p0 := origine + Vector2(c, r) * cote
			for d in [[Vector2i(1, 0), Vector2(cote, 0), Vector2(cote, cote)], [Vector2i(-1, 0), Vector2(0, 0), Vector2(0, cote)],
					[Vector2i(0, 1), Vector2(0, cote), Vector2(cote, cote)], [Vector2i(0, -1), Vector2(0, 0), Vector2(cote, 0)]]:
				var voisin := _cellule(c + d[0].x, r + d[0].y)
				if voisin.niv != k.niv:
					var a: Vector2 = p0 + d[1]
					var b: Vector2 = p0 + d[2]
					var tremble := Vector2(sin(a.x * 0.9 + a.y * 1.3), cos(b.x * 1.1 - b.y * 0.7)) * 1.2
					draw_line(a + tremble, b - tremble, ENCRE, 2.0 if voisin.niv < 0 else 1.4, true)
	# les lanternes allumées : un point d'or
	for l in lanternes:
		if l.allumee:
			var m: Vector2 = vers_carte.call(l.pos)
			draw_circle(m, cote * 0.16, OR)
			draw_arc(m, cote * 0.16, 0, TAU, 16, ENCRE, 1.2, true)
	# les lieux découverts : un petit rond d'encre et le nom
	for l in lieux:
		var m: Vector2 = vers_carte.call(l.pos)
		draw_arc(m, cote * 0.09, 0, TAU, 10, ENCRE, 1.6, true)
		draw_string(POLICE, m + Vector2(cote * 0.15, -cote * 0.08), str(l.nom), HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(20, int(cote * 0.5)), ENCRE)
	# le robot : une petite croix
	var ici: Vector2 = vers_carte.call(robot)
	var s := cote * 0.12
	draw_line(ici - Vector2(s, s), ici + Vector2(s, s), ENCRE, 2.0, true)
	draw_line(ici - Vector2(s, -s), ici + Vector2(s, -s), ENCRE, 2.0, true)
