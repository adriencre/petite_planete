extends Node
## Essai du branchement en 1re personne : l'île 1 sans le réveil, le robot devant une petite
## lanterne-fleur, dans ses yeux. Lancer res://tests/essai_branchement.tscn depuis l'éditeur (F6).
## E : brancher (la vraie séquence, longue la 1re fois) · R : éteindre la lanterne et se replacer
## (séquence longue à nouveau) · G : rejouer seulement le geste des mains (tirer la fiche).

var _joueur: CharacterBody3D
var _lanterne: Node3D


func _ready() -> void:
	var ile := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	ile.get_node("Reveil").set("premier_reveil", false)
	add_child(ile)
	_joueur = ile.get_node("Joueur") as CharacterBody3D
	await get_tree().create_timer(0.5).timeout
	for l in get_tree().get_nodes_in_group("lanternes"):
		if int(l.get("rang")) == 0 and (_lanterne == null or l.global_position.distance_to(_joueur.global_position) < _lanterne.global_position.distance_to(_joueur.global_position)):
			_lanterne = l
	_replacer()


func _replacer() -> void:
	var prise: Vector3 = _lanterne.call("_prise_position")
	var normale: Vector3 = _lanterne.call("_prise_normale")
	_joueur.vue_dessus = false
	_joueur.premiere_personne = true
	_joueur.set("_blend", 1.0)
	_joueur.global_position = Vector3(prise.x, _joueur.global_position.y, prise.z) + normale * 2.2
	_joueur.velocity = Vector3.ZERO
	_joueur.set("_yaw", atan2(normale.x, normale.z))
	_joueur.set("_pitch", -0.25)
	print("Essai : devant la lanterne ", _lanterne.name, " — E brancher, R recommencer, G geste seul")


func _unhandled_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or _joueur.cinematique:
		return
	if k.physical_keycode == KEY_R:
		_lanterne.call("eteindre")
		_lanterne.set("premiere_fois", true)
		_replacer()
	elif k.physical_keycode == KEY_G:
		_geste_seul()


func _geste_seul() -> void:
	_joueur.cinematique = true
	await _joueur.lever_mains(true, 0.8).finished
	await _joueur.tirer_fiche()
	await get_tree().create_timer(0.8).timeout
	_joueur.lacher_fiche()
	_joueur.lever_mains(true, 0.4)
	await _joueur.ranger_fiche(0.55).finished
	await _joueur.lever_mains(false, 0.6).finished
	_joueur.cinematique = false
