extends StaticBody3D
## La clé ouvre le vantail une fois. La porte reste accessible au retour.

const SONS := preload("res://scripts/sons.gd")
const ANGLE_OUVERT := -1.62

@onready var _pivot: Node3D = $Pivot
@onready var _cle: Node3D = $CleDansSerrure
@onready var _invite: Label3D = $Invite
@onready var _forme: CollisionShape3D = $Forme

var ouverte := false
var _ouverture := false
var _robot: CharacterBody3D
var _epave: Node3D


func _ready() -> void:
	add_to_group("sauvegarde")
	ouverte = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("ouverte", false))
	_lier_vantail.call_deferred()


func _lier_vantail() -> void:
	var porte := get_parent().get_node("Modele").find_child("PorteCartes", true, false)
	if porte:
		for piece in porte.get_children():
			var nom := String(piece.name)
			if nom.begins_with("Vantail") or nom.begins_with("Plaque de serrure") or nom.begins_with("Cartouche"):
				piece.reparent(_pivot)
	$PlaquePalier.reparent(_pivot)
	$PlaqueInterieure.reparent(_pivot)
	if ouverte:
		_pivot.rotation.y = ANGLE_OUVERT
		_forme.set_deferred("disabled", true)


func cle_sauvegarde() -> String:
	return "porte_salle_cartes"


func sauver() -> Dictionary:
	return {"ouverte": ouverte}


func _process(_delta: float) -> void:
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if not is_instance_valid(_epave):
		_epave = get_tree().get_first_node_in_group("epave_ravitailleur") as Node3D
	_invite.visible = _a_portee()
	if _invite.visible:
		_invite.text = "E   Déverrouiller" if _a_la_cle() else "Fermée à clé"


func _a_portee() -> bool:
	if ouverte or _ouverture or _robot == null or not is_visible_in_tree() or bool(_robot.get("cinematique")):
		return false
	var pied := to_local(_robot.global_position)
	return absf(pied.y + 1.19) < 0.48 and Vector2(pied.x, pied.z).length() < 1.25 and pied.z < 0.10


func _a_la_cle() -> bool:
	return _epave != null and bool(_epave.get("cle_recuperee"))


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E or not _a_portee():
		return
	get_viewport().set_input_as_handled()
	if _a_la_cle():
		_deverrouiller()
	else:
		SONS.jouer("clic", global_position, -13.0, 0.68)


func _deverrouiller() -> void:
	_ouverture = true
	_robot.set("cinematique", true)
	_robot.velocity = Vector3.ZERO
	_robot.set("regard_cible", _cle.global_position)
	_robot.set("cine_cible", _cle.global_position + Vector3.UP * 0.16)
	_robot.set("cine_position", to_global(Vector3(0.95, 0.54, -1.20)))
	var plan := create_tween().set_trans(Tween.TRANS_SINE)
	plan.tween_property(_robot, "cine_melange", 1.0, 0.62)
	plan.tween_callback(_cle.show)
	plan.tween_property(_cle, "position:z", -0.29, 0.52)
	plan.tween_property(_cle, "rotation:z", -0.85, 0.63)
	plan.tween_callback(SONS.jouer.bind("clic", _cle.global_position, -3.0, 0.76))
	plan.tween_property(_cle, "position:z", -0.42, 0.35)
	plan.tween_callback(_cle.hide)
	plan.tween_property(_pivot, "rotation:y", ANGLE_OUVERT, 1.12)
	plan.tween_property(_robot, "cine_melange", 0.0, 0.64)
	await plan.finished
	ouverte = true
	_ouverture = false
	_forme.set_deferred("disabled", true)
	_robot.set("cinematique", false)
