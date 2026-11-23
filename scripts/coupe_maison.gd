extends Area3D
## Dégage la vue sur l'intérieur quand le robot franchit le seuil.

@export var toit: GeometryInstance3D
@export var murs_hauts: GeometryInstance3D
## Pièces supplémentaires à effacer (étage du dessus, plancher, couvercle d'un tuyau…).
@export var autres: Array[NodePath] = []

var _fondu: Tween
var _dedans := false


func _robot_entre(corps: Node3D) -> void:
	if corps.is_in_group("joueur"):
		_dedans = true


func _robot_sort(corps: Node3D) -> void:
	if corps.is_in_group("joueur"):
		_dedans = false


func _pieces() -> Array[GeometryInstance3D]:
	var pieces: Array[GeometryInstance3D] = []
	for piece: GeometryInstance3D in [toit, murs_hauts]:
		if piece:
			pieces.append(piece)
	for chemin in autres:
		var piece := get_node_or_null(chemin) as GeometryInstance3D
		if piece:
			pieces.append(piece)
	return pieces


func _devoiler(interieur_visible: bool) -> void:
	var pieces := _pieces()
	if pieces.is_empty():
		return
	if _fondu:
		_fondu.kill()
	_fondu = create_tween().set_parallel()
	for piece in pieces:
		piece.cast_shadow = (
			GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if interieur_visible
			else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		)
		_fondu.tween_property(piece, "transparency", 1.0 if interieur_visible else 0.0, 0.35)

## La coupe (toit, haut des murs) n'est utile que si l'on voit le robot de l'extérieur : en 1re personne,
## le toit reste en place (décidé le 2026-11-22). Changer de caméra dedans (touche V) la met à jour.
var _coupe := false


func _process(_delta: float) -> void:
	var j := get_tree().get_first_node_in_group("joueur")
	var couper: bool = _dedans and (j == null or bool(j.call("troisieme_personne")))
	if couper != _coupe:
		_coupe = couper
		_devoiler(couper)
