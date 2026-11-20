extends Area3D
## Dégage la vue sur l'intérieur quand le robot franchit le seuil.

@export var toit: GeometryInstance3D
@export var murs_hauts: GeometryInstance3D

var _fondu: Tween


func _robot_entre(corps: Node3D) -> void:
	if corps.is_in_group("joueur"):
		_devoiler(true)


func _robot_sort(corps: Node3D) -> void:
	if corps.is_in_group("joueur"):
		_devoiler(false)


func _devoiler(interieur_visible: bool) -> void:
	if _fondu:
		_fondu.kill()
	_fondu = create_tween().set_parallel()
	var pieces: Array[GeometryInstance3D] = [toit, murs_hauts]
	for piece in pieces:
		piece.cast_shadow = (
			GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if interieur_visible
			else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		)
		_fondu.tween_property(piece, "transparency", 1.0 if interieur_visible else 0.0, 0.35)
