extends Node3D
## La porte de l'étage d'Aube, sur le palier de l'escalier de pierre (ILE_03_COLONIE.md). Elle est barrée
## de l'intérieur. Du palier, E : le robot pousse, la porte bouge à peine et cogne contre la barre.
## De l'intérieur (après le chemin d'Aube), E près de la barre : il la soulève de ses crochets, la pose
## contre le mur, et la porte s'ouvre. Elle reste ouverte : c'est un raccourci.

const SONS := preload("res://scripts/sons.gd")

@export var charniere: Node3D
@export var barre: Node3D
## Où le robot se tient pour pousser la porte (sur le palier).
@export var point_dehors: Node3D
## Où le robot se tient pour soulever la barre (dans la pièce commune).
@export var point_dedans: Node3D
## Où la barre est posée, debout contre le mur.
@export var pose_barre: Node3D
@export var distance: float = 1.4
## Angle d'ouverture du battant (degrés, autour de la charnière).
@export var angle_ouverte: float = -90.0

var ouverte: bool = false
var essayee: bool = false
var _joueur: CharacterBody3D
var _en_cours: bool = false


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	var d: Dictionary = Sauvegarde.donnees(cle_sauvegarde(), self)
	ouverte = bool(d.get("ouverte", false))
	essayee = bool(d.get("essayee", false))
	if ouverte:
		charniere.rotation.y = deg_to_rad(angle_ouverte)
		barre.global_transform = pose_barre.global_transform
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "porte:" + str(name)


func sauver() -> Dictionary:
	return {"ouverte": ouverte, "essayee": essayee}


## Pour guidage.gd : 2 = E possible, 1 = à découvrir, 0 = rien.
func etat_interaction() -> int:
	if _joueur == null or ouverte or _en_cours or bool(_joueur.get("cinematique")):
		return 0
	if _pres(point_dehors) or _pres(point_dedans):
		return 2
	return 0 if essayee else 1


func point_appel() -> Vector3:
	if _joueur and _distance(point_dedans) < _distance(point_dehors):
		return barre.global_position
	return charniere.global_position + Vector3.UP * 1.3


func _distance(point: Node3D) -> float:
	var a := _joueur.global_position
	var p := point.global_position
	if absf(a.y - p.y) > 1.2:
		return INF
	return Vector2(a.x - p.x, a.z - p.z).length()


func _pres(point: Node3D) -> bool:
	return _distance(point) < distance


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null or ouverte or _en_cours:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E or bool(_joueur.get("cinematique")):
		return
	if _pres(point_dedans):
		get_viewport().set_input_as_handled()
		_debarrer()
	elif _pres(point_dehors):
		get_viewport().set_input_as_handled()
		_pousser()


## Il pousse : la porte bouge à peine, cogne deux fois contre la barre et retombe.
func _pousser() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", charniere.global_position + Vector3.UP * 1.3)
	await get_tree().create_timer(0.35, false).timeout
	SONS.jouer("porte_bloquee", charniere.global_position + Vector3.UP * 1.3)
	var a := deg_to_rad(-2.5)
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(charniere, "rotation:y", a, 0.08)
	t.tween_property(charniere, "rotation:y", 0.0, 0.16)
	t.tween_property(charniere, "rotation:y", a * 0.6, 0.08)
	t.tween_property(charniere, "rotation:y", 0.0, 0.2)
	await t.finished
	await get_tree().create_timer(0.8, false).timeout
	essayee = true
	_joueur.set("cinematique", false)
	_en_cours = false


## De l'intérieur : il soulève la barre, la pose contre le mur ; la porte s'ouvre lentement.
func _debarrer() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", barre.global_position)
	await get_tree().create_timer(0.4, false).timeout
	SONS.jouer("barre", barre.global_position)
	var depart: Transform3D = barre.global_transform
	var leve: Transform3D = depart.translated(Vector3.UP * 0.18)
	var arrivee: Transform3D = pose_barre.global_transform
	var soulever := func(x: float) -> void:
		barre.global_transform = depart.interpolate_with(leve, x)
	var poser := func(x: float) -> void:
		barre.global_transform = leve.interpolate_with(arrivee, x)
	var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_method(soulever, 0.0, 1.0, 0.5)
	t.tween_method(poser, 0.0, 1.0, 1.0)
	await t.finished
	await get_tree().create_timer(0.5, false).timeout
	ouverte = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	SONS.jouer("porte_bloquee", charniere.global_position + Vector3.UP * 1.3, -10.0, 0.7)
	var o := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	o.tween_property(charniere, "rotation:y", deg_to_rad(angle_ouverte), 1.8)
	await o.finished
	_joueur.set("cinematique", false)
	_en_cours = false
