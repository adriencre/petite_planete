extends Node3D
## Les roues restent sur leur support jusqu'à ce que le robot choisisse un axe.

const SONS := preload("res://scripts/sons.gd")
const INTERFACE := preload("res://scripts/ui/interface_engrenages.gd")
const DENTS := [12.0, 16.0, 10.0]
const PHASES := [-0.03, 0.232, -0.106]
const DETENTES := TAU / 3.0
const DEPORT_CHARIOT := 0.33
const PIED_VIS := 0.26

@onready var _roues: Array[Node3D] = [$Roues/Menante, $Roues/Intermediaire, $Roues/Menee]
@onready var _repos: Array[Node3D] = [$Rangements/Menante, $Rangements/Intermediaire, $Rangements/Menee]
@onready var _axes: Array[Node3D] = [$Axes/Gauche, $Axes/Centre, $Axes/Droite]
@onready var _touche: Label3D = $Touche
@onready var _inspection: Marker3D = $Inspection
@onready var _interface: INTERFACE = $Interface
@onready var _chariot: Node3D = $Chariot
@onready var _sellette: Node3D = $Chariot/Sellette
@onready var _manivelle_cric: Node3D = $Chariot/Manivelle
@onready var _vis: MeshInstance3D = $Chariot/Vis
@onready var _garage: Vector3 = _chariot.position
@onready var _repos_sellette: float = _sellette.position.y

var repare := false
var _places := [-1, -1, -1]
var _crans := [1, 2, 1]
var _souris_avant := Input.MOUSE_MODE_CAPTURED
var _occupe := false
var _rotation := 0.0
var _angle_lentille := 0.0
var _tension := 0.0
var _robot: CharacterBody3D
var _chaine: Array[Node3D] = []
var _positions_chaine: Array[Vector3] = []


func _ready() -> void:
	add_to_group("sauvegarde")
	_interface.placer.connect(_monter)
	_interface.tourner.connect(_tourner)
	_interface.retirer.connect(_retirer)
	_interface.fermer.connect(_fermer)
	var etat := Sauvegarde.donnees(cle_sauvegarde(), self)
	var places: Array = etat.get("places", _places)
	var crans: Array = etat.get("crans", _crans)
	var axes_utilises: Array[int] = []
	for i in _roues.size():
		var place := clampi(int(places[i]), -1, 2)
		if place >= 0 and place not in axes_utilises:
			_places[i] = place
			axes_utilises.append(place)
		_crans[i] = posmod(int(crans[i]), 3)
		_reposer(i)
	repare = _assemble()
	_tension = 1.0 if repare else 0.0
	var modele := get_parent().get_node("Modele")
	for motif: String in ["Axe d’une roue démontable*", "Roue du schéma peint*", "Rayon du relevé*",
			"Trace circulaire d'usure*", "Marque d'appui*"]:
		for ancien in modele.find_children(motif, "Node3D", true, false):
			(ancien as Node3D).hide()
	for maillon in modele.find_children("Maillon de la chaîne*", "MeshInstance3D", true, false):
		_chaine.append(maillon as Node3D)
		_positions_chaine.append((maillon as Node3D).position)
	_actualiser_chaine()


func cle_sauvegarde() -> String:
	return "engrenages_phare"


func sauver() -> Dictionary:
	return {"places": _places.duplicate(), "crans": _crans.duplicate()}


func suivre_lentille(angle: float) -> void:
	if repare:
		_rotation += angle_difference(_angle_lentille, angle) * 8.0
	_angle_lentille = angle


func _assemble() -> bool:
	return _places == [0, 1, 2] and _crans == [0, 0, 0]


func _reposer(roue: int) -> void:
	var axe: int = _places[roue]
	var point := _repos[roue] if axe < 0 else _axes[axe]
	_roues[roue].position = point.position
	_roues[roue].rotation.z = 0.0 if axe < 0 else PHASES[axe] + _crans[roue] * DETENTES


func _process(_delta: float) -> void:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	_touche.visible = _inspection_accessible()
	if repare:
		for i in _roues.size():
			var sens := -1.0 if i == 1 else 1.0
			_roues[i].rotation.z = PHASES[i] + sens * _rotation * DENTS[0] / DENTS[i]
	if repare or _tension > 0.0:
		_actualiser_chaine()


func _actualiser_chaine() -> void:
	for i in _chaine.size():
		var repos := _positions_chaine[i]
		var ventre := sin(clampf((repos.y - 2.45) / 5.6, 0.0, 1.0) * PI)
		_chaine[i].position = repos + Vector3(-0.24 * ventre * (1.0 - _tension),
			fposmod(_rotation * 0.35, 0.448), 0.0)


func _inspection_accessible() -> bool:
	if _robot == null or _occupe or repare or not is_visible_in_tree() or bool(_robot.get("cinematique")):
		return false
	var ecart := _robot.global_position - _inspection.global_position
	return absf(ecart.y) < 0.9 and Vector2(ecart.x, ecart.z).length() < 2.4


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E:
		return
	if not _inspection_accessible():
		return
	get_viewport().set_input_as_handled()
	_souris_avant = Input.mouse_mode
	_robot.set("regard_cible", _touche.global_position)
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_interface.ouvrir(_places, _crans, PHASES)
	SONS.jouer("clic", _inspection.global_position, -6.0, 0.77)


func _fermer() -> void:
	if _interface.visible:
		_interface.hide()
		_robot.set("cinematique", false)
		Input.mouse_mode = _souris_avant


func _monter(roue: int, axe: int) -> void:
	if _occupe or repare or _places[roue] >= 0 or _places.has(axe):
		return
	_commencer_action()
	await _deplacer(roue, _axes[axe], PHASES[axe] + _crans[roue] * DETENTES)
	_places[roue] = axe
	await _terminer_action(axe)


func _retirer(axe: int) -> void:
	var roue := _places.find(axe)
	if _occupe or repare or roue < 0:
		return
	_commencer_action()
	await _deplacer(roue, _repos[roue], 0.0)
	_places[roue] = -1
	await _terminer_action(axe)


func _tourner(axe: int) -> void:
	var roue := _places.find(axe)
	if _occupe or repare or roue < 0:
		return
	_commencer_action()
	var etape := create_tween().set_trans(Tween.TRANS_SINE)
	var depart := _roues[roue].rotation.z
	etape.tween_method(_pivoter.bind(roue, axe), depart, depart + DETENTES, 0.65)
	await etape.finished
	_crans[roue] = (_crans[roue] + 1) % 3
	_reposer(roue)
	await _terminer_action(axe)


func _pivoter(angle: float, roue: int, axe: int) -> void:
	_roues[roue].rotation.z = angle
	if _interface.visible:
		_interface.dessiner_axe(axe, roue, angle)


func _commencer_action() -> void:
	_occupe = true
	if _interface.visible:
		_interface.actualiser(_places, _crans, true)


func _terminer_action(axe: int) -> void:
	SONS.jouer("clic", _axes[axe].global_position, -3.0, 0.78)
	if _assemble():
		_fermer()
		await _debloquer()
	_occupe = false
	if _interface.visible:
		_interface.actualiser(_places, _crans, false)


func _deplacer(roue: int, cible: Node3D, angle: float) -> void:
	var piece := _roues[roue]
	var depart := piece.position
	var passage := cible.position + Vector3.BACK * 0.24
	var trajet := create_tween().set_trans(Tween.TRANS_SINE)
	trajet.tween_property(_chariot, "position", _sous_roue(depart), 0.58)
	trajet.parallel().tween_method(_regler_cric, _sellette.position.y, _hauteur_sellette(depart), 0.58)
	trajet.tween_method(_rouler.bind(piece, depart, passage), 0.0, 1.0, 1.25)
	trajet.parallel().tween_property(piece, "rotation:z", angle, 1.25)
	trajet.tween_property(piece, "position", cible.position, 0.32)
	trajet.tween_property(_chariot, "position", _garage, 0.62)
	trajet.parallel().tween_method(_regler_cric, _hauteur_sellette(passage), _repos_sellette, 0.55)
	await trajet.finished


func _rouler(t: float, piece: Node3D, depart: Vector3, arrivee: Vector3) -> void:
	var point := depart.lerp(arrivee, t)
	piece.position = point
	_chariot.position = _sous_roue(point)
	_regler_cric(_hauteur_sellette(point))


func _sous_roue(point: Vector3) -> Vector3:
	return Vector3(point.x, _garage.y, point.z + DEPORT_CHARIOT)


func _hauteur_sellette(point: Vector3) -> float:
	return maxf(_repos_sellette, point.y - _garage.y - 0.132)


func _regler_cric(hauteur: float) -> void:
	_sellette.position.y = hauteur
	_vis.scale.y = hauteur - PIED_VIS
	_vis.position.y = (hauteur + PIED_VIS) * 0.5
	_manivelle_cric.rotation.x = (hauteur - _repos_sellette) * TAU / 0.125


func _debloquer() -> void:
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	var cible := to_global(Vector3(-0.85, 1.48, -1.25))
	_robot.set("regard_cible", cible)
	_robot.set("cine_cible", cible)
	_robot.set("cine_position", to_global(Vector3(1.25, 2.72, 3.1)))
	var plan := create_tween().set_trans(Tween.TRANS_SINE)
	plan.tween_property(_robot, "cine_melange", 1.0, 0.6)
	plan.tween_callback(SONS.jouer.bind("clic", cible, 1.0, 0.54))
	plan.tween_property(self, "_tension", 1.0, 0.85)
	plan.tween_callback(func() -> void: repare = true)
	plan.tween_property(_robot, "cine_cible", to_global(Vector3(0.1, 2.45, -1.1)), 1.1)
	plan.tween_interval(0.5)
	plan.tween_property(_robot, "cine_melange", 0.0, 0.65)
	await plan.finished
	_robot.set("cinematique", false)
