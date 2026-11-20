extends Node3D
## Le robot s’assoit face à la mer. E ou Échap le remet sur le sentier.

const CLE := "banc_iris"

@onready var _assise: Marker3D = $Assise
@onready var _vue: Marker3D = $VueDuBanc
@onready var _appui: Marker3D = $AppuiDebout
var _joueur: CharacterBody3D
var _modele: Node3D
var _premiere_vue := true
var _occupe := false
var _transition := false
var _retour := Vector3.ZERO


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	_premiere_vue = not bool(Sauvegarde.donnees(CLE, self).get("vue", false))
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return CLE


func sauver() -> Dictionary:
	return {"vue": not _premiere_vue}


func etat_interaction() -> int:
	if not is_instance_valid(_joueur) or _occupe or bool(_joueur.get("cinematique")):
		return 0
	var ecart := _joueur.global_position - _appui.global_position
	return 2 if absf(ecart.y) < 0.32 and Vector2(ecart.x, ecart.z).length() < 0.72 else 0


func point_appel() -> Vector3:
	return _assise.global_position + Vector3.UP * 0.38


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if touche == null or not touche.pressed or touche.echo or _transition:
		return
	if _occupe and touche.physical_keycode in [KEY_E, KEY_ESCAPE]:
		get_viewport().set_input_as_handled()
		_se_lever()
	elif touche.physical_keycode == KEY_E and etat_interaction() == 2:
		get_viewport().set_input_as_handled()
		_s_asseoir()


func _s_asseoir() -> void:
	_modele = _joueur.get_node("Modele") as Node3D
	if not _modele.call("a_animation", "assis"):
		return
	_occupe = true
	_transition = true
	_joueur.set("cinematique", true)
	_joueur.set("sur_banc", true)
	_joueur.velocity = Vector3.ZERO
	var cap := -_vue.global_basis.z.normalized()
	var angle := atan2(cap.x, cap.z)
	_retour = _appui.global_position
	var pose := _assise.global_position + cap * 0.37 - Basis(Vector3.UP, angle).x * 0.124
	pose.y -= 0.35 # L’origine du clip assis est sous le bassin.
	var camera := _vue.global_position - cap * 2.75 + Vector3.UP * 0.46
	_joueur.set("cine_position", camera)
	_joueur.set("cine_cible", camera + cap * 60.0)
	var approche := _mouvement()
	approche.tween_property(_joueur, "global_position", _retour, 0.5)
	approche.parallel().tween_property(_modele, "rotation:y", _modele.rotation.y + angle_difference(_modele.rotation.y, angle), 0.5)
	await approche.finished
	_modele.call("jouer_action", "assis", 1.0, 0.7)
	var assise := _mouvement()
	assise.tween_property(_joueur, "global_position", pose, 0.72)
	assise.parallel().tween_property(_joueur, "cine_melange", 1.0, 2.15 if _premiere_vue else 0.9)
	await assise.finished
	_premiere_vue = false
	_transition = false


func _se_lever() -> void:
	_transition = true
	_modele.call("jouer_action", "attente", 1.0, 0.58)
	var sortie := _mouvement()
	sortie.tween_property(_joueur, "global_position", _retour, 0.68)
	sortie.parallel().tween_property(_joueur, "cine_melange", 0.0, 0.9)
	await sortie.finished
	_liberer()


func _mouvement() -> Tween:
	return create_tween().set_process_mode(Tween.TWEEN_PROCESS_PHYSICS).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _liberer() -> void:
	if is_instance_valid(_modele):
		_modele.call("fin_action")
	if is_instance_valid(_joueur):
		_joueur.set("cine_melange", 0.0)
		_joueur.set("sur_banc", false)
		_joueur.set("cinematique", false)
	_occupe = false
	_transition = false


func _exit_tree() -> void:
	if _occupe and is_instance_valid(_joueur) and _joueur.is_inside_tree():
		_joueur.global_position = _retour
		_liberer()
