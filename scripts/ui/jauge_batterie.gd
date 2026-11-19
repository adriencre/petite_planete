@tool
extends Control
## La jauge de batterie, en haut à gauche (scenes/ui/hud_batterie.tscn) — décidé le 2026-11-18 : le
## seul élément d'interface du jeu. Dessinée comme le carnet : une petite ampoule à l'encre et un trait
## doré qui se vide. Elle s'efface pendant les cinématiques et clignote doucement quand il reste peu.
## La batterie est lue sur le joueur (groupe « joueur », propriété `batterie`, 0..1).

@export var largeur: float = 170.0:
	set(v):
		largeur = v
		queue_redraw()
@export var epaisseur: float = 12.0:
	set(v):
		epaisseur = v
		queue_redraw()
@export var encre: Color = Color(0.33, 0.24, 0.17)
@export var papier: Color = Color(0.97, 0.93, 0.84, 0.85)
@export var or_plein: Color = Color(1.0, 0.8, 0.42)
@export var or_faible: Color = Color(0.95, 0.5, 0.3)
## En dessous, la jauge vire à l'orange et clignote.
@export_range(0.0, 1.0) var seuil_faible: float = 0.25
## Aperçu dans l'éditeur.
@export_range(0.0, 1.0) var apercu: float = 0.7:
	set(v):
		apercu = v
		queue_redraw()

var _joueur: Node
var _affiche: float = 1.0
var _t: float = 0.0


func _ready() -> void:
	custom_minimum_size = Vector2(largeur + 44.0, 34.0)
	if Engine.is_editor_hint():
		_affiche = apercu
		return
	modulate.a = 0.0


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	if _joueur == null:
		_joueur = get_tree().get_first_node_in_group("joueur")
		if _joueur == null:
			return
	_t += delta
	var b: float = float(_joueur.get("batterie"))
	_affiche = lerpf(_affiche, b, 1.0 - exp(-delta * 6.0))
	# visible quand on a la main, effacée pendant les cinématiques (réveil, lanternes, fin)
	var cible := 0.0 if bool(_joueur.get("cinematique")) else 1.0
	modulate.a = move_toward(modulate.a, cible, delta * 1.5)
	queue_redraw()


func _draw() -> void:
	var niveau := clampf(_affiche if not Engine.is_editor_hint() else apercu, 0.0, 1.0)
	var faible := niveau < seuil_faible
	var pouls := 0.5 + 0.5 * sin(_t * 6.0) if faible else 1.0
	var teinte := or_faible.lerp(or_plein, clampf(niveau / maxf(seuil_faible, 0.01), 0.0, 1.0))
	# l'ampoule : un rond à l'encre, rempli d'or selon la batterie, sur une petite tige
	var c := Vector2(14, 15)
	draw_line(c + Vector2(0, 10), c + Vector2(0, 18), encre, 2.0, true)
	draw_circle(c, 11.0, papier)
	draw_circle(c, 9.0 * (0.35 + 0.65 * niveau), Color(teinte, 0.35 + 0.65 * pouls))
	draw_arc(c, 11.0, 0.0, TAU, 24, encre, 2.0, true)
	# le trait : une gouttière de papier bordée d'encre, remplie d'or
	var x0 := 34.0
	var y0 := c.y - epaisseur * 0.5
	var fond := StyleBoxFlat.new()
	fond.bg_color = papier
	fond.border_color = Color(encre, 0.7)
	fond.set_border_width_all(2)
	fond.set_corner_radius_all(int(epaisseur * 0.5) + 2)
	draw_style_box(fond, Rect2(x0, y0, largeur, epaisseur))
	if niveau > 0.005:
		var plein := StyleBoxFlat.new()
		plein.bg_color = Color(teinte, 0.55 + 0.45 * pouls)
		plein.set_corner_radius_all(int(epaisseur * 0.5))
		var w := maxf((largeur - 6.0) * niveau, epaisseur - 6.0)
		draw_style_box(plein, Rect2(x0 + 3.0, y0 + 3.0, w, epaisseur - 6.0))
