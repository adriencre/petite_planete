extends Node3D
## Bouée de recharge. Le flotteur suit la mer tandis que son ancrage reste fixe.

const BARQUE := preload("res://scripts/barque.gd")
const SONS := preload("res://scripts/sons.gd")
const MIROIR := preload("res://scripts/miroir_cap.gd")

@export var portee := 3.6
@export var miroir_quai: MIROIR

@onready var _flotteur: Node3D = $Flotteur
@onready var _niveau_repos := _flotteur.position.y
@onready var _prise: Marker3D = $Flotteur/Prise
@onready var _touche: Label3D = $Flotteur/Touche
@onready var _lueur: OmniLight3D = $Flotteur/Lueur

var _temps := 0.0
var allumee := false
var _en_cours := false
var _robot: CharacterBody3D
var _verre: StandardMaterial3D


func _ready() -> void:
	add_to_group("sauvegarde")
	var cristal := _flotteur.find_child("Cristal de la bouée", true, false) as MeshInstance3D
	if cristal:
		_verre = cristal.get_active_material(0).duplicate() as StandardMaterial3D
		cristal.set_surface_override_material(0, _verre)
	var etat := Sauvegarde.donnees(cle_sauvegarde(), self)
	allumee = bool(etat.get("allumee", false))
	_regler_feu(1.0 if allumee else 0.0)


func cle_sauvegarde() -> String:
	return "bouee_quai"


func sauver() -> Dictionary:
	return {"allumee": allumee}


func _process(delta: float) -> void:
	_temps += delta
	_flotteur.global_position.y = HorlogeMonde.niveau_mer() + _niveau_repos + sin(_temps * 1.65) * 0.045
	_flotteur.rotation.z = sin(_temps * 1.31) * 0.038
	_flotteur.rotation.x = cos(_temps * 0.91) * 0.028
	if not is_instance_valid(_robot):
		_robot = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	_touche.visible = _barque_a_portee() != null
	_touche.text = "E · Recharger" if allumee else "E · Brancher la bouée"


func _barque_a_portee() -> BARQUE:
	if _en_cours or not is_instance_valid(_robot):
		return null
	if allumee and float(_robot.get("batterie")) >= 0.995:
		return null
	var barque := _robot.get("embarque") as BARQUE
	if not is_instance_valid(barque) or not barque.peut_recharger():
		return null
	# La prise est sur le flanc qui fait face au quai.
	var ecart := _prise.global_position - _robot.global_position
	if ecart.x < -0.30 or ecart.length_squared() > portee * portee:
		return null
	return barque


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E:
		return
	var barque := _barque_a_portee()
	if barque == null:
		return
	get_viewport().set_input_as_handled()
	_recharger(barque)


func _recharger(barque: BARQUE) -> void:
	_en_cours = true
	var premier_branchement := not allumee
	await barque.brancher_recharge(_prise)
	if premier_branchement:
		_robot.set("cinematique", true)
		var cible := (_robot.global_position + _prise.global_position) * 0.5
		var travers := (_prise.global_position - _robot.global_position).cross(Vector3.UP).normalized()
		_robot.set("cine_cible", cible + Vector3.UP * 0.25)
		_robot.set("cine_position", cible + travers * 3.7 + Vector3.UP * 2.9)
		var plan := create_tween().set_trans(Tween.TRANS_SINE)
		plan.tween_property(_robot, "cine_melange", 1.0, 0.60)
		barque.flux_recharge(1.0, 0.55)
		plan.tween_method(_regler_feu, 0.0, 1.0, 1.05)
		await plan.finished
		if miroir_quai:
			miroir_quai.progression_incidente = 0.0
		allumee = true
		SONS.jouer("clic", _prise.global_position, -6.0, 0.78)
		if miroir_quai:
			await _suivre_rayon()

	barque.flux_recharge(-1.0, 1.0)
	var charge := create_tween().set_trans(Tween.TRANS_SINE)
	charge.tween_property(_robot, "batterie", 1.0, 2.10 if premier_branchement else 1.50)
	if premier_branchement:
		charge.tween_property(_robot, "cine_melange", 0.0, 0.58)
	await charge.finished
	await barque.reprendre_navigation()
	if premier_branchement:
		_robot.set("cinematique", false)
	_en_cours = false


func _suivre_rayon() -> void:
	var miroir := miroir_quai.get_node("PivotMiroir") as Node3D
	var depart := miroir_quai.sortie_lanterne.global_position
	var arrivee := miroir.global_position
	var ecart_camera := Vector3(6.0, 5.0, 2.0)
	var plan := create_tween().set_trans(Tween.TRANS_SINE)
	plan.tween_property(_robot, "cine_position", depart + ecart_camera, 0.55)
	plan.parallel().tween_property(_robot, "cine_cible", depart, 0.55)
	plan.tween_property(miroir_quai, "progression_incidente", 1.0, 1.35)
	plan.parallel().tween_property(_robot, "cine_cible", arrivee, 1.35)
	plan.parallel().tween_property(_robot, "cine_position", arrivee + ecart_camera, 1.35)
	plan.tween_interval(0.20)
	await plan.finished
	var impact := miroir_quai.bout_reflet
	if impact == Vector3.ZERO:
		impact = miroir_quai.reception.global_position
	var facade := create_tween().set_trans(Tween.TRANS_SINE)
	facade.tween_property(_robot, "cine_cible", impact.lerp(miroir_quai.reception.global_position, 0.42), 0.8)
	facade.tween_interval(0.85)
	await facade.finished


func _regler_feu(proportion: float) -> void:
	_lueur.light_energy = proportion * 1.6
	if _verre:
		_verre.emission_energy_multiplier = proportion * 2.2
