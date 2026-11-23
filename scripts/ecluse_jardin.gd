extends Node3D
## L'écluse du jardin du haut (ILE_03_COLONIE.md, G3, étape 1 : le temps).
## Le carillon des marées, sur le quai, sonne au plus haut de la marée ; la cloche-relais, au pied de
## l'écluse, sonne avec lui. À ce moment-là seulement, la mer monte encore un peu : le flotteur, dans son
## puits sous le quai, pousse son index doré jusqu'au verrou de la vanne basse et le soulève. Pendant
## `duree_ouverture` secondes, le grand levier à crans du ponton peut ouvrir la vanne ; ensuite le verrou
## retombe et il faut attendre la marée suivante (8 minutes).
## Levier tiré à temps : petite cinématique, le ponton monte sas par sas (vanne qui se lève, le ponton
## avance, la vanne se referme, l'eau de la citerne remplit le sas). En haut, le robot descend dans le
## jardin. L'écluse ne sert qu'une fois : ensuite la porte de service du jardin fait raccourci.
## Les pièces animées sont dans le modèle de la Colonie (tools/blender/jardin_du_haut.py), chacune avec
## son origine sur son pivot. Rien de magique : de l'eau, un flotteur, des chaînes.

const SONS := preload("res://scripts/sons.gd")
## Valeurs de tools/blender/jardin_du_haut.py.
const FRANC_BORD := 1.1
const MONTEE := 2.1
const LEVEE_VANNE := 5.8

@export var colonie: Node3D
## Le carillon des marées (sur le quai) et la cloche-relais (au pied de l'écluse) : d'où viennent les sons.
@export var carillon: Node3D
@export var cloche_relais: Node3D
## Où le robot pose le pied dans le jardin, en haut.
@export var arrivee: Node3D
## Le temps pendant lequel la vanne basse peut s'ouvrir après le carillon (secondes).
@export var duree_ouverture: float = 45.0
## Le plus haut de la marée, dans le cycle de l'horloge du monde (0,75 = milieu de la marée haute).
@export_range(0.0, 1.0) var phase_pic: float = 0.75
## La mer monte encore un peu au plus haut : assez pour que l'index du flotteur touche le verrou.
@export var bosse_pic: float = 0.14
## Levée du verrou quand l'index le pousse.
@export var levee_verrou: float = 0.3
@export var distance_levier: float = 1.8

var montee_faite: bool = false
var essaye: bool = false
var _vannes: Array[Node3D] = []
var _eaux: Array[Node3D] = []
var _ponton: Node3D
var _levier: Node3D
var _flotteur: Node3D
var _verrou: Node3D
var _ponton_y: float = 0.0
var _flotteur_y: float = 0.0
var _verrou_y: float = 0.0
var _ouverture: float = 0.0
var _phase_prec: float = -1.0
var _joueur: CharacterBody3D
var _en_cours: bool = false
var _porte: bool = false
var _decalage := Vector3.ZERO
var _recul := Vector3(0.0, 1.0, 1.0).normalized()


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	for k in 4:
		_vannes.append(colonie.find_child("Vanne_sas_%d" % k, true, false) as Node3D)
		_eaux.append(colonie.find_child("Eau_sas_%d" % (k + 1), true, false) as Node3D)
	_ponton = colonie.find_child("Ponton_ecluse", true, false) as Node3D
	_levier = colonie.find_child("Levier_ecluse", true, false) as Node3D
	_flotteur = colonie.find_child("Flotteur_ecluse", true, false) as Node3D
	_verrou = colonie.find_child("Verrou_ecluse", true, false) as Node3D
	# Le levier et son secteur à crans sont posés sur le ponton : ils le suivent.
	var socle := colonie.find_child("Socle_du_levier", true, false) as Node3D
	for piece in [_levier, socle]:
		if piece and _ponton:
			(piece as Node3D).reparent(_ponton, true)
	if _ponton:
		_ponton_y = _ponton.position.y
	if _flotteur:
		_flotteur_y = _flotteur.position.y
	if _verrou:
		_verrou_y = _verrou.position.y
	var d: Dictionary = Sauvegarde.donnees(cle_sauvegarde(), self)
	montee_faite = bool(d.get("montee", false))
	essaye = bool(d.get("essaye", false))
	if montee_faite:
		_poser_en_haut()
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "ecluse:" + str(name)


func sauver() -> Dictionary:
	return {"montee": montee_faite, "essaye": essaye}


## Vanne basse ouvrable en ce moment (le carillon vient de sonner).
func est_ouvrable() -> bool:
	return _ouverture > 0.0


func _process(delta: float) -> void:
	var niveau: float = float(HorlogeMonde.niveau_mer())
	var phase: float = float(HorlogeMonde.phase())
	if _phase_prec >= 0.0 and _a_franchi(_phase_prec, phase, phase_pic):
		_sonner()
	_phase_prec = phase
	if _ouverture > 0.0:
		_ouverture = maxf(0.0, _ouverture - delta)
	# La bosse du plus haut : elle monte en 2 s quand le carillon sonne et retombe à la fin.
	var ecoule: float = duree_ouverture - _ouverture
	var bosse: float = bosse_pic * clampf(minf(ecoule / 2.0, _ouverture / 2.0), 0.0, 1.0) if _ouverture > 0.0 else 0.0
	if _flotteur:
		_flotteur.position.y = _flotteur_y + niveau + bosse
	if _verrou:
		var cible: float = _verrou_y + levee_verrou * (bosse / bosse_pic if bosse_pic > 0.0 else 0.0)
		_verrou.position.y = cible
	if _ponton and not montee_faite and not _en_cours:
		_ponton.position.y = _ponton_y + niveau
	if _porte and _joueur:
		var centre: Vector3 = _ponton.global_position + Vector3.UP * 1.2
		_joueur.set("cine_cible", centre)
		_joueur.set("cine_position", centre + _recul * 12.0)


func _physics_process(_delta: float) -> void:
	# Pendant la montée, le robot est porté par le ponton.
	if _porte and _joueur and _ponton:
		_joueur.global_position = _ponton.global_position + _decalage
		_joueur.velocity = Vector3.ZERO


## Vrai si la phase est passée par `c` entre `a` et `b` (le cycle revient à 0 après 1).
func _a_franchi(a: float, b: float, c: float) -> bool:
	if b >= a:
		return a < c and c <= b
	return c > a or c <= b


## Le plus haut de la marée : le carillon du quai, puis la cloche-relais ; le verrou se lève.
func _sonner() -> void:
	_ouverture = duree_ouverture
	if carillon:
		SONS.jouer("carillon", carillon.global_position, 2.0)
	await get_tree().create_timer(0.7, false).timeout
	if cloche_relais:
		SONS.jouer("cloche", cloche_relais.global_position, 1.0)


## Pour guidage.gd : 2 = E possible, 1 = à découvrir, 0 = rien.
func etat_interaction() -> int:
	if _joueur == null or montee_faite or _en_cours or bool(_joueur.get("cinematique")):
		return 0
	if _a_portee():
		return 2
	return 0 if essaye else 1


func point_appel() -> Vector3:
	return _levier.global_position + Vector3.UP * 1.4 if _levier else global_position


func _a_portee() -> bool:
	if _levier == null or _ponton == null:
		return false
	var a := _joueur.global_position
	var p := _levier.global_position
	var dy: float = a.y - _ponton.global_position.y
	return Vector2(a.x - p.x, a.z - p.z).length() < distance_levier and dy > -0.5 and dy < 1.6


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null or montee_faite or _en_cours:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E or bool(_joueur.get("cinematique")):
		return
	if not _a_portee():
		return
	get_viewport().set_input_as_handled()
	if est_ouvrable():
		_monter()
	else:
		_tirer_en_vain()


## Hors du plus haut de la marée : le levier bute sur le verrou, la vanne cogne et ne bouge pas.
func _tirer_en_vain() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", _levier.global_position + Vector3.UP * 1.2)
	await get_tree().create_timer(0.3, false).timeout
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(_levier, "rotation:z", -0.16, 0.25)
	t.tween_callback(func() -> void: SONS.jouer("porte_bloquee", _vannes[0].global_position + Vector3.UP * 2.0, -4.0, 0.8))
	t.tween_property(_levier, "rotation:z", 0.0, 0.35)
	await t.finished
	await get_tree().create_timer(0.7, false).timeout
	essaye = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	_joueur.set("cinematique", false)
	_en_cours = false


## Le levier tiré au bon moment : la montée, sas par sas.
func _monter() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", _vannes[0].global_position + Vector3.UP * 2.0)
	_recul = _joueur.call("recul_cinematique", _joueur.global_position)
	_decalage = _joueur.global_position - _ponton.global_position
	_porte = true
	var approche := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "cine_melange", 1.0, 2.2)

	# 1) le levier descend cran par cran
	for n in 3:
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_property(_levier, "rotation:z", -0.2 * (n + 1), 0.35)
		await t.finished
		SONS.jouer("clic", _levier.global_position + Vector3.UP, -2.0, 0.85)
		await get_tree().create_timer(0.25, false).timeout
	await get_tree().create_timer(0.4, false).timeout

	# 2) sas par sas : la vanne se lève, le ponton avance, la vanne retombe, le sas se remplit
	for g in 4:
		var vanne := _vannes[g]
		var eau := _eaux[g]
		_joueur.set("regard_cible", vanne.global_position + Vector3.UP * 3.0)
		SONS.jouer("chaine", vanne.global_position + Vector3.UP * 3.0)
		var leve := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		leve.tween_property(vanne, "position:y", vanne.position.y + LEVEE_VANNE, 3.2)
		await leve.finished
		var cible := Vector3(eau.global_position.x, eau.global_position.y + FRANC_BORD, eau.global_position.z)
		_joueur.set("regard_cible", cible + Vector3.UP)
		var avance := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		avance.tween_property(_ponton, "global_position", cible, 4.0)
		await avance.finished
		SONS.jouer("chaine", vanne.global_position + Vector3.UP * 3.0, -2.0, 0.9)
		var baisse := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		baisse.tween_property(vanne, "position:y", vanne.position.y - LEVEE_VANNE, 2.6)
		await baisse.finished
		SONS.jouer("eau_sas", eau.global_position)
		var remplit := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		remplit.tween_property(eau, "position:y", eau.position.y + MONTEE, 5.5)
		remplit.tween_property(_ponton, "position:y", _ponton.position.y + MONTEE, 5.5)
		await remplit.finished
		await get_tree().create_timer(0.5, false).timeout

	# 3) en haut : le levier remonte, le robot pose le pied dans le jardin
	var relache := create_tween().set_trans(Tween.TRANS_SINE)
	relache.tween_property(_levier, "rotation:z", 0.0, 0.6)
	_porte = false
	montee_faite = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	if arrivee:
		var pied: Vector3 = arrivee.global_position + Vector3.UP * (_decalage.y + 0.05)
		_joueur.set("regard_cible", pied + (pied - _joueur.global_position).normalized() * 3.0)
		var descend := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		descend.tween_property(_joueur, "global_position", pied, 1.8)
		await descend.finished
	var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 2.2)
	await get_tree().create_timer(1.2, false).timeout
	_joueur.set("cinematique", false)
	_en_cours = false


## Partie reprise après la montée : sas pleins, ponton en haut.
func _poser_en_haut() -> void:
	for eau in _eaux:
		if eau:
			eau.position.y += MONTEE
	if _ponton and _eaux[3]:
		var e: Vector3 = _eaux[3].global_position
		_ponton.global_position = Vector3(e.x, e.y + FRANC_BORD, e.z)
