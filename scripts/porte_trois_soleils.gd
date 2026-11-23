extends Node3D
## Le parvis des Trois-Soleils et la grande porte de la maison commune (ILE_03_COLONIE.md, G2).
## Neuf lanternes en grille ; chacune est reliée par un câble à son voyant, sur le pupitre près de la porte.
## Quand exactement les lanternes du motif sont allumées (et aucune autre), la serrure se met en route :
## les voyants battent ensemble, les trois crans dorés tournent un par un, le verrou remonte sous le
## linteau, puis les deux vantaux s'ouvrent lentement vers l'intérieur. Rien de magique : du courant, des crans.
## Les pièces animées (voyants, crans, verrou, vantaux) sont dans le modèle de la Colonie
## (tools/blender/ville_haute.py), chacune avec son origine sur son pivot.

const SONS := preload("res://scripts/sons.gd")

@export var colonie: Node3D
## Dans l'ordre du plan : rangée contre la porte d'abord, chaque rangée de gauche à droite (face à la porte).
@export var lanternes: Array[Node3D] = []
## « 1 » = allumée dans le motif. Même ordre que `lanternes`.
@export var motif: String = "101000010"
## La collision des vantaux fermés, retirée à l'ouverture.
@export var battants_fermes: CollisionShape3D
## L'affiche clouée sur le vantail gauche : elle suit le vantail quand il s'ouvre.
@export var affiche_porte: Node3D
## Angle d'ouverture de chaque vantail (degrés).
@export var angle_ouverture: float = 100.0
## Hauteur dont remonte le verrou (il va se loger sous le linteau).
@export var levee_verrou: float = 3.1
@export var couleur_voyant: Color = Color(1.0, 0.74, 0.34)

var ouverte: bool = false
var _voyants: Array[StandardMaterial3D] = []
var _crans: Array[Node3D] = []
var _verrou: Node3D
var _gauche: Node3D
var _droite: Node3D
var _base_gauche: float = 0.0
var _base_droite: float = 0.0
var _joueur: CharacterBody3D
var _en_cours: bool = false


func _ready() -> void:
	add_to_group("sauvegarde")
	for i in 9:
		_voyants.append(_preparer_voyant(colonie.find_child("Voyant_commune_%d" % (i + 1), true, false) as MeshInstance3D))
	for i in 3:
		var cran := colonie.find_child("Cran_commune_%d" % (i + 1), true, false) as Node3D
		if cran:
			_crans.append(cran)
	_verrou = colonie.find_child("Verrou_commune", true, false) as Node3D
	_gauche = colonie.find_child("Porte_commune_gauche", true, false) as Node3D
	_droite = colonie.find_child("Porte_commune_droite", true, false) as Node3D
	if _gauche:
		_base_gauche = _gauche.rotation.y
	if _droite:
		_base_droite = _droite.rotation.y
	if affiche_porte and _gauche:
		affiche_porte.reparent.call_deferred(_gauche, true)
	var d: Dictionary = Sauvegarde.donnees(cle_sauvegarde(), self)
	ouverte = bool(d.get("ouverte", false))
	if ouverte:
		_poser_ouverte()
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "porte:" + str(name)


func sauver() -> Dictionary:
	return {"ouverte": ouverte}


## Le verre du voyant reçoit son propre matériau, éteint : il s'allume avec sa lanterne.
func _preparer_voyant(voyant: MeshInstance3D) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.64, 0.82, 0.8)
	m.roughness = 0.2
	m.emission_enabled = true
	m.emission = couleur_voyant
	m.emission_energy_multiplier = 0.0
	if voyant and voyant.mesh:
		for s in voyant.mesh.get_surface_count():
			var origine := voyant.mesh.surface_get_material(s)
			if origine and origine.resource_name.begins_with("verre"):
				voyant.set_surface_override_material(s, m)
	return m


func _etat() -> String:
	var etat := ""
	for l in lanternes:
		etat += "1" if bool(l.get("allumee")) else "0"
	return etat


func _une_lanterne_occupee() -> bool:
	for l in lanternes:
		if bool(l.get("_en_cours")):
			return true
	return false


func _process(delta: float) -> void:
	if ouverte or _en_cours or _joueur == null:
		return
	var etat := _etat()
	for i in mini(_voyants.size(), etat.length()):
		var cible: float = 3.5 if etat[i] == "1" else 0.0
		_voyants[i].emission_energy_multiplier = lerpf(_voyants[i].emission_energy_multiplier, cible, minf(1.0, delta * 3.0))
		_voyants[i].albedo_color = Color(1.0, 0.86, 0.6) if etat[i] == "1" else Color(0.64, 0.82, 0.8)
	if etat == motif and not _une_lanterne_occupee() and not bool(_joueur.get("cinematique")):
		_ouvrir()


## Le motif est juste : la serrure se met en route, la caméra vient sur la porte.
func _ouvrir() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	var centre: Vector3 = (_gauche.global_position + _droite.global_position) * 0.5 + Vector3.UP * 2.0
	_joueur.set("regard_cible", centre)
	var recul: Vector3 = _joueur.call("recul_cinematique", centre)
	_joueur.set("cine_cible", centre)
	_joueur.set("cine_position", centre + recul * 8.5)
	var approche := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "cine_melange", 1.0, 2.2)
	await approche.finished
	await get_tree().create_timer(0.4, false).timeout

	# 1) les voyants allumés battent ensemble : le courant arrive à la serrure
	for k in 2:
		var bat := create_tween().set_parallel()
		for i in motif.length():
			if motif[i] == "1":
				bat.tween_property(_voyants[i], "emission_energy_multiplier", 8.0, 0.25)
		await bat.finished
		var retombe := create_tween().set_parallel()
		for i in motif.length():
			if motif[i] == "1":
				retombe.tween_property(_voyants[i], "emission_energy_multiplier", 3.5, 0.35)
		await retombe.finished
	await get_tree().create_timer(0.3, false).timeout

	# 2) les trois crans tournent, un par un, de haut en bas
	for i in range(_crans.size() - 1, -1, -1):
		var cran := _crans[i]
		SONS.jouer("clic", cran.global_position, -2.0, 0.8)
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_property(cran, "rotation:z", cran.rotation.z - TAU / 3.0, 0.9)
		await t.finished
		await get_tree().create_timer(0.35, false).timeout

	# 3) le verrou remonte et se loge sous le linteau
	if _verrou:
		SONS.jouer("barre", _verrou.global_position)
		var v := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		v.tween_property(_verrou, "position:y", _verrou.position.y + levee_verrou, 1.6)
		await v.finished
	await get_tree().create_timer(0.5, false).timeout

	# 4) les vantaux s'ouvrent lentement vers l'intérieur
	ouverte = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	if battants_fermes:
		battants_fermes.set_deferred("disabled", true)
	SONS.jouer("porte_bloquee", centre, -8.0, 0.6)
	var o := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	o.tween_property(_gauche, "rotation:y", _base_gauche + deg_to_rad(angle_ouverture), 2.8)
	o.tween_property(_droite, "rotation:y", _base_droite - deg_to_rad(angle_ouverture), 2.8)
	await o.finished
	await get_tree().create_timer(0.6, false).timeout

	var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 2.0)
	await get_tree().create_timer(1.2, false).timeout
	_joueur.set("cinematique", false)
	_en_cours = false


## Partie reprise après l'ouverture : tout est déjà dans sa position finale.
func _poser_ouverte() -> void:
	for m in _voyants:
		m.emission_energy_multiplier = 0.0
	for i in motif.length():
		if motif[i] == "1" and i < _voyants.size():
			_voyants[i].emission_energy_multiplier = 3.5
	for cran in _crans:
		cran.rotation.z -= TAU / 3.0
	if _verrou:
		_verrou.position.y += levee_verrou
	if _gauche:
		_gauche.rotation.y = _base_gauche + deg_to_rad(angle_ouverture)
	if _droite:
		_droite.rotation.y = _base_droite - deg_to_rad(angle_ouverture)
	if battants_fermes:
		battants_fermes.disabled = true
