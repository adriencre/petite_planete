extends Node3D
## Un bâtiment qu'on visite en vue de dessus (ex. scenes/ile02/maison_quai.tscn) : quand le robot entre
## dans la zone `Interieur` (Area3D enfant), les pièces nommées dans `a_effacer` (le toit, le haut du mur
## côté caméra…) s'effacent en fondu, et reviennent quand il sort. Leurs collisions restent.

## Noms des nœuds à effacer (cherchés dans tout le bâtiment, ex. le .glb importé).
@export var a_effacer: PackedStringArray = ["Toit", "Coupe"]
@export var duree_fondu: float = 0.6
## Pièces de terrain importées hors du bâtiment, s'il est creusé dans la falaise.
@export var racine_coupe_exterieure: NodePath
@export var motif_coupe_exterieure: String

var _pieces: Array[GeometryInstance3D] = []
var _fondu: Tween
var _dedans := 0


func _ready() -> void:
	for nom in a_effacer:
		var n := find_child(nom, true, false)
		if n is GeometryInstance3D:
			_pieces.append(n as GeometryInstance3D)
		elif n:
			for g in n.find_children("*", "GeometryInstance3D", true, false):
				_pieces.append(g as GeometryInstance3D)
	if not racine_coupe_exterieure.is_empty() and not motif_coupe_exterieure.is_empty():
		var racine := get_node_or_null(racine_coupe_exterieure)
		if racine:
			for g in racine.find_children(motif_coupe_exterieure, "GeometryInstance3D", true, false):
				_pieces.append(g as GeometryInstance3D)
	var zone := get_node_or_null("Interieur") as Area3D
	if zone:
		zone.body_entered.connect(_entre)
		zone.body_exited.connect(_sort)


func _entre(corps: Node3D) -> void:
	if corps is CharacterBody3D:
		_dedans += 1


func _sort(corps: Node3D) -> void:
	if corps is CharacterBody3D:
		_dedans = maxi(0, _dedans - 1)


func _montrer(visible_: bool) -> void:
	if _fondu:
		_fondu.kill()
	_fondu = create_tween().set_parallel()
	for g in _pieces:
		if visible_:
			g.visible = true
		# pendant le fondu, plus d'ombre : l'intérieur s'éclaire tout de suite
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if visible_ else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_fondu.tween_property(g, "transparency", 0.0 if visible_ else 1.0, duree_fondu)
	if not visible_:
		_fondu.chain().tween_callback(_cacher)


func _cacher() -> void:
	for g in _pieces:
		g.visible = false

## La coupe (toit, haut des murs) n'est utile que si l'on voit le robot de l'extérieur : en 1re personne,
## le toit reste en place (décidé le 2026-11-22). Changer de caméra dedans (touche V) la met à jour.
var _coupe := false


func _process(_delta: float) -> void:
	var j := get_tree().get_first_node_in_group("joueur")
	var couper: bool = _dedans > 0 and (j == null or bool(j.call("troisieme_personne")))
	if couper != _coupe:
		_coupe = couper
		_montrer(not couper)
