extends Control
## Vue de face de l'engrenage et de son empreinte, à la même échelle.

const LAITON := Color("#e5bc79")
const TRACE := Color("#78908a")
const VIDE := Color("#203032")
const DENTS := [12, 16, 10]

var _roue := -1
var _axe := -1
var _phase := 0.0
var _angle := 0.0


func afficher(roue: int, axe: int, phase: float, angle: float) -> void:
	_roue = roue
	_axe = axe
	_phase = phase
	_angle = angle
	queue_redraw()


func _draw() -> void:
	var centre := size * 0.5
	var unite := minf(size.x, size.y) * 0.40
	if _roue < 0:
		if _axe >= 0:
			draw_circle(centre, unite * 0.16, VIDE.lightened(0.18), true, -1.0, true)
			draw_arc(centre, unite * 0.16, 0.0, TAU, 24, TRACE, 1.5, true)
	else:
		_dessiner_roue(centre, unite)
	if _axe >= 0:
		var empreinte := unite * float(DENTS[_axe]) / 16.0
		for segment in 24:
			var debut := TAU * segment / 24.0
			draw_arc(centre, empreinte + 4.0, debut, debut + TAU * 0.63 / 24.0, 4, TRACE, 1.5, true)
		_trait(centre, -_phase, empreinte + 8.0, empreinte + 15.0)


func _dessiner_roue(centre: Vector2, unite: float) -> void:
	var rayon := unite * float(DENTS[_roue]) / 16.0
	var points := PackedVector2Array()
	var dents: int = DENTS[_roue]
	for dent in dents:
		for coin in 4:
			var angle := -_angle + TAU * (dent + (coin + 0.5) / 4.0) / dents
			var relief := 1.0 if coin == 1 or coin == 2 else 0.83
			points.append(centre + Vector2.from_angle(angle) * rayon * relief)
	draw_colored_polygon(points, Color("#789b91"))
	points.append(points[0])
	draw_polyline(points, Color("#a8c1aa"), 1.1, true)
	draw_circle(centre, rayon * 0.69, VIDE, true, -1.0, true)
	draw_arc(centre, rayon * 0.71, 0.0, TAU, 50, Color("#9cb8a4"), 1.5, true)
	for rayon_de_roue in 4:
		var direction := Vector2.from_angle(-_angle + PI * rayon_de_roue * 0.5)
		draw_line(centre, centre + direction * rayon * 0.72, Color("#789b91"), maxf(3.0, rayon * 0.15), true)
	draw_circle(centre, rayon * 0.23, LAITON.darkened(0.13), true, -1.0, true)
	draw_circle(centre, rayon * 0.13, VIDE, true, -1.0, true)
	_trait(centre, -_angle, rayon * 0.72, rayon * 0.92)


func _trait(centre: Vector2, angle: float, debut: float, fin: float) -> void:
	var direction := Vector2.from_angle(angle)
	draw_line(centre + direction * debut, centre + direction * fin, LAITON, 3.0, true)
