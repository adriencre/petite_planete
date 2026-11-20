extends Node3D
## La lunette de la galerie est indépendante de la grande lentille du Phare.

const SONS := preload("res://scripts/sons.gd")
const ANGLE_DU_MODELE := 210.17

@export var noms: PackedStringArray
@export var orientations: PackedFloat32Array
@export var vues: Array[Texture2D]

var commande_lentille_prioritaire: Callable

@onready var _touche: Label3D = $Touche
@onready var _pivot: Marker3D = $Pivot
@onready var _oculaire: CanvasLayer = $Oculaire
@onready var _fond: Control = $Oculaire/Fond
@onready var _image: TextureRect = %Vue
@onready var _nom: Label = %Nom

var _robot: CharacterBody3D
var _cran := 0
var _ouvert := false
var _transition: Tween
var _pieces: Array[Node3D] = []
var _repose: Array[Transform3D] = []


func _ready() -> void:
	var modele := get_parent().get_node("Modele")
	for motif: String in ["Fût de la lunette*", "Bague de l’objectif*", "Verre de la lunette*"]:
		var matches := modele.find_children(motif, "MeshInstance3D", true, false)
		for piece: Node3D in matches:
			_pieces.append(piece)
			_repose.append(_pivot.global_transform.affine_inverse() * piece.global_transform)
	_orienter(_angle_du_cran())


func _process(_delta: float) -> void:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	_touche.visible = _a_portee()
	var taille := _fond.size
	var diametre := minf(taille.x * 0.84, taille.y * 0.80)
	_image.size = Vector2(diametre, diametre)
	_image.position = (taille - _image.size) * 0.5


func _a_portee() -> bool:
	return a_portee(_robot) and (
		not commande_lentille_prioritaire.is_valid() or not bool(commande_lentille_prioritaire.call())
	)


func a_portee(robot: CharacterBody3D) -> bool:
	if not is_instance_valid(robot) or _ouvert or bool(robot.get("cinematique")):
		return false
	var ecart := robot.global_position - global_position
	return absf(ecart.y) < 0.65 and Vector2(ecart.x, ecart.z).length() < 1.05


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo:
		return
	if not _a_portee() or touche.physical_keycode != KEY_E:
		return
	get_viewport().set_input_as_handled()
	_ouvrir()


func _input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not _ouvert or not touche or not touche.pressed:
		return
	get_viewport().set_input_as_handled()
	if touche.echo:
		return
	match touche.physical_keycode:
		KEY_ESCAPE, KEY_E:
			_fermer()
		KEY_LEFT, KEY_A:
			_changer_cran(-1)
		KEY_RIGHT, KEY_D:
			_changer_cran(1)


func _ouvrir() -> void:
	_ouvert = true
	_robot.set("regard_cible", _pivot.global_position)
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	_fond.modulate.a = 0.0
	_image.modulate.a = 1.0
	_oculaire.show()
	_actualiser_vue()
	_transition = create_tween()
	_transition.tween_property(_fond, "modulate:a", 1.0, 0.65)
	_transition.tween_callback(_noter_vue)


func _fermer() -> void:
	if _transition and _transition.is_running():
		_transition.kill()
	_orienter(_angle_du_cran())
	_oculaire.hide()
	_ouvert = false
	if is_instance_valid(_robot):
		_robot.set("cinematique", false)


func _changer_cran(sens: int) -> void:
	if _transition and _transition.is_running():
		return
	var depart := _pivot.rotation.y
	_cran = posmod(_cran + sens, vues.size())
	var arrivee := depart + angle_difference(depart, _angle_du_cran())
	SONS.jouer("clic", _pivot.global_position, -6.0, 0.70)
	_transition = create_tween().set_trans(Tween.TRANS_SINE)
	_transition.tween_property(_image, "modulate:a", 0.0, 0.20)
	_transition.parallel().tween_method(_orienter, depart, arrivee, 0.40)
	_transition.tween_callback(_actualiser_vue)
	_transition.tween_property(_image, "modulate:a", 1.0, 0.26)
	_transition.tween_callback(_noter_vue)


func _angle_du_cran() -> float:
	return deg_to_rad(ANGLE_DU_MODELE - orientations[_cran])


func _orienter(angle: float) -> void:
	_pivot.rotation.y = angle
	for i in _pieces.size():
		_pieces[i].global_transform = _pivot.global_transform * _repose[i]


func _actualiser_vue() -> void:
	_image.texture = vues[_cran]
	_nom.text = noms[_cran] if not noms[_cran].is_empty() else "⌂"


func _noter_vue() -> void:
	var carnet := get_tree().get_first_node_in_group("carnet")
	if carnet:
		var titre := noms[_cran] if not noms[_cran].is_empty() else "La mer, au nord-ouest"
		carnet.noter_croquis("À la lunette · " + titre, vues[_cran])
