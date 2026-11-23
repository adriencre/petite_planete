extends Node3D
## La lampe-mère du jardin du haut (ILE_03_COLONIE.md, G3) : la grande lanterne vers laquelle penchent tous
## les arbres roses. Le robot la rallume comme une lanterne : il s'agenouille au pied du socle, branche son
## câble dans la prise. Le cœur se remplit de lumière ; dans la tête, le disque de verre peint se met à
## tourner (une lanterne magique) et projette sur le mur blanc les silhouettes d'un souvenir : des Semeurs
## plantent le premier arbre rose en chantant. Le chant vient du cylindre musical du socle, un écho de
## la boîte à musique d'Aube. Ensuite la lampe reste allumée. E pendant le souvenir : il débranche.
## Ce nœud est posé sur la prise, son axe +Z tourné vers le robot (à l'opposé du mur).

const SONS := preload("res://scripts/sons.gd")
const CABLE := preload("res://scripts/cable.gd")
const RECUL_GENOU := 0.62
const INSTANT_FICHE := 0.93
const INSTANT_BRAS_LEVES := 0.6

@export var colonie: Node3D
## L'écran du souvenir, plaqué sur le mur blanc (shaders/souvenir_projete.gdshader).
@export var ecran: MeshInstance3D
## Les tableaux du disque de verre peint, dans l'ordre (tools/affiches/souvenir_arbre_rose.py).
@export var images: Array[Texture2D] = []
## Le chant des Semeurs (provisoire : tools/audio/chant_semeurs.py).
@export var chant: AudioStream
## Ce que la caméra regarde pendant le souvenir (entre la lampe et le mur).
@export var centre_vue: Node3D
@export var distance_activation: float = 1.8
@export var cout_batterie: float = 0.2
@export var couleur: Color = Color(1.0, 0.76, 0.45)
@export var energie_lumiere: float = 3.2
## Durée d'un fondu entre deux tableaux (secondes).
@export var fondu: float = 1.4
@export_multiline var note_carnet: String = "La lampe-mère du jardin du haut. Son disque de verre peint montre des Semeurs qui plantent le premier arbre rose, en chantant un chant de chez eux.\n\nLes arbres roses viennent de leur planète. Ils ne pouvaient pas les laisser mourir."

var allumee: bool = false
var _joueur: CharacterBody3D
var _en_cours: bool = false
var _arret_demande: bool = false
var _cable
var _fiche_posee: bool = false
var _retrait: float = -1.0
var _coeur: MeshInstance3D
var _coeur_mat := StandardMaterial3D.new()
var _disque: Node3D
var _cylindre: Node3D
var _lumiere := OmniLight3D.new()
var _son := AudioStreamPlayer3D.new()
var _ecran_mat: ShaderMaterial
var _tourne: bool = false
## Petite lueur dorée sur la prise quand la fiche y entre.
var _lueur_prise := OmniLight3D.new()


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	allumee = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("allumee", false))
	_cable = CABLE.new()
	_cable.visible = false
	add_child(_cable)
	_coeur = colonie.find_child("Coeur_lampe_mere", true, false) as MeshInstance3D
	_disque = colonie.find_child("Disque_lampe_mere", true, false) as Node3D
	_cylindre = colonie.find_child("Cylindre_musique", true, false) as Node3D
	_coeur_mat.albedo_color = Color(0.95, 0.85, 0.62)
	_coeur_mat.roughness = 0.3
	_coeur_mat.emission_enabled = true
	_coeur_mat.emission = couleur
	_coeur_mat.emission_energy_multiplier = 0.0
	if _coeur:
		_coeur.material_override = _coeur_mat
	_lumiere.light_color = couleur
	_lumiere.light_energy = 0.0
	_lumiere.omni_range = 9.0
	_lumiere.shadow_enabled = true
	add_child(_lumiere)
	_lueur_prise.light_color = couleur
	_lueur_prise.light_energy = 0.0
	_lueur_prise.omni_range = 1.2
	add_child(_lueur_prise)
	_son.stream = chant
	_son.bus = &"Musique"
	_son.unit_size = 8.0
	add_child(_son)
	if ecran:
		_ecran_mat = ecran.material_override as ShaderMaterial
		ecran.visible = false
	if allumee:
		_coeur_mat.emission_energy_multiplier = 4.0
		_lumiere.light_energy = energie_lumiere
	await get_tree().process_frame
	if _coeur:
		_lumiere.global_position = _coeur.global_position
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "lampe_mere:" + str(name)


func sauver() -> Dictionary:
	return {"allumee": allumee}


## Pour guidage.gd : 2 = E possible, 1 = à découvrir, 0 = rien.
func etat_interaction() -> int:
	if _joueur == null or _en_cours or bool(_joueur.get("cinematique")):
		return 0
	if _a_portee():
		return 2
	return 0 if allumee else 1


func point_appel() -> Vector3:
	return global_position + Vector3.UP * 0.6


func _a_portee() -> bool:
	var a := _joueur.global_position
	var p := global_position
	return Vector2(a.x - p.x, a.z - p.z).length() < distance_activation and absf(a.y - p.y) < 1.4


func _normale() -> Vector3:
	var n := global_basis.z
	n.y = 0.0
	return n.normalized()


func _process(delta: float) -> void:
	if _tourne:
		if _disque:
			_disque.rotate_object_local(Vector3.FORWARD, delta * 0.5)
		if _cylindre:
			_cylindre.rotate_object_local(Vector3.UP, delta * 0.9)
	if _joueur == null or not _cable.visible:
		return
	_cable.debut = _joueur.call("poignet_droit_monde")
	if _retrait >= 0.0:
		_cable.fin = global_position.lerp(_cable.debut, _retrait)
	else:
		_cable.fin = global_position if _fiche_posee else _joueur.call("bout_index_monde")


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E:
		return
	if _en_cours:
		if _son.playing:
			get_viewport().set_input_as_handled()
			_arret_demande = true
		return
	if bool(_joueur.get("cinematique")) or not _a_portee():
		return
	get_viewport().set_input_as_handled()
	_rallumer()


func _rallumer() -> void:
	_en_cours = true
	_arret_demande = false
	var premiere: bool = not allumee
	# d'abord la cinématique : en 1re personne, la caméra recule en 3e et on voit le geste
	_joueur.set("cinematique", true)
	var robot: Node = _joueur.get("modele")
	var geste: bool = bool(_joueur.call("troisieme_personne")) and robot != null and robot.has_method("jouer_action") and bool(robot.call("a_animation", "brancher"))
	var normale := _normale()
	_joueur.set("regard_cible", global_position)

	# 1) il vient se placer devant la prise ; la caméra descend se poser de côté, à hauteur de genou
	var place: Vector3 = global_position + normale * RECUL_GENOU
	place.y = _joueur.global_position.y
	var trajet := Vector2(place.x - _joueur.global_position.x, place.z - _joueur.global_position.z).length()
	var pied := global_position + normale * (RECUL_GENOU * 0.5)
	var cible_basse := pied + Vector3.UP * 0.7
	_joueur.set("cine_cible", cible_basse)
	_joueur.set("cine_position", _plan_de_cote(cible_basse, normale))
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, clampf(trajet / 1.3, 0.5, 3.0))
	approche.tween_property(_joueur, "cine_melange", 1.0, 2.4 if premiere else 1.4)
	await approche.finished
	await get_tree().create_timer(0.45, false).timeout  # le temps de se tourner vers la prise

	# 2) il tire le câble de son poignet, pose un genou à terre et enfonce la fiche : clic, la prise luit
	var d_brancher := 1.0
	if geste:
		robot.call("jouer_action", "brancher", 1.0)
		d_brancher = float(robot.call("duree", "brancher"))
	_cable.visible = true
	_retrait = -1.0
	_cable.materiau.set_shader_parameter("flux", 0.0)
	await get_tree().create_timer(d_brancher * INSTANT_FICHE, false).timeout
	_fiche_posee = true
	SONS.jouer("clic", global_position)
	var eclair := create_tween()
	eclair.tween_property(_lueur_prise, "light_energy", 1.6, 0.08)
	eclair.tween_property(_lueur_prise, "light_energy", 0.5, 0.5)
	await get_tree().create_timer(d_brancher * (1.0 - INSTANT_FICHE) + 0.4, false).timeout

	# 3) le courant court le long du câble et monte dans le mât ; il lève la tête, la caméra la suit
	var d_charge := 3.6 if premiere else 1.8
	if geste and bool(robot.call("a_animation", "brancher_lever_tete")):
		var d_tete: float = robot.call("duree", "brancher_lever_tete")
		robot.call("jouer_action", "brancher_lever_tete", d_tete / d_charge, 0.2)
	elif geste:
		robot.call("jouer_action", "brancher_attente", 0.6, 0.4)
	var tete_lampe: Vector3 = _coeur.global_position if _coeur else global_position + Vector3.UP * 4.0
	var charge := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	charge.tween_method(_flux, 0.0, 1.0, 0.8)
	charge.tween_property(_joueur, "cine_cible", (cible_basse + tete_lampe) * 0.5, d_charge)
	charge.tween_property(_joueur, "cine_position", _plan_de_cote(cible_basse, normale) + Vector3.UP * 1.6 + normale * 1.2, d_charge)
	if premiere:
		SONS.jouer("allumage", tete_lampe)
		charge.tween_property(_coeur_mat, "emission_energy_multiplier", 4.0, d_charge)
		charge.tween_property(_lumiere, "light_energy", energie_lumiere, d_charge)
		charge.tween_property(_joueur, "batterie", maxf(0.05, float(_joueur.get("batterie")) - cout_batterie), d_charge)
	await charge.finished
	if premiere:
		allumee = true
		Sauvegarde.noter(cle_sauvegarde(), sauver())
	if geste:
		robot.call("jouer_action", "brancher_attente", 0.6, 0.4)
	await get_tree().create_timer(0.5, false).timeout

	# 3 bis) à genoux, il regarde : la caméra recule lentement pour montrer la lampe et le mur blanc
	var centre: Vector3 = centre_vue.global_position if centre_vue else global_position + Vector3.UP * 3.0
	var recul: Vector3 = (normale + Vector3.UP * 0.75).normalized()
	var vers_mur := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	vers_mur.tween_property(_joueur, "cine_cible", centre, 3.0)
	vers_mur.tween_property(_joueur, "cine_position", centre + recul * (11.0 if premiere else 12.0), 3.0)
	await vers_mur.finished

	# 4) le disque tourne, le cylindre joue le chant ; le souvenir apparaît sur le mur
	_tourne = true
	_son.play()
	await _projeter()
	_tourne = false
	if premiere:
		var carnet := get_tree().get_first_node_in_group("carnet")
		if carnet:
			carnet.call("noter_texte", note_carnet, "", images[images.size() - 1] if images.size() > 0 else null)

	# 5) il débranche ; la lampe reste allumée ; la caméra revient
	var d_debrancher := 1.0
	if geste:
		robot.call("jouer_action", "debrancher", 1.0, 0.25)
		d_debrancher = float(robot.call("duree", "debrancher"))
	await get_tree().create_timer(d_debrancher * INSTANT_BRAS_LEVES, false).timeout
	_fiche_posee = false
	_retrait = 0.0
	var rembobine := create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	rembobine.tween_property(self, "_retrait", 1.0, 0.35)
	rembobine.tween_callback(_ranger_cable)
	var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 2.4)
	retour.parallel().tween_property(_lueur_prise, "light_energy", 0.0, 0.6)
	await get_tree().create_timer(d_debrancher * (1.0 - INSTANT_BRAS_LEVES), false).timeout
	if geste:
		robot.call("fin_action")
	_joueur.set("cinematique", false)
	_en_cours = false


## Les tableaux défilent sur le mur, en fondu, au rythme du chant ; puis l'écran s'éteint.
func _projeter() -> void:
	if ecran == null or _ecran_mat == null or images.is_empty():
		while _son.playing and not _arret_demande:
			await get_tree().process_frame
		_son.stop()
		return
	var duree_chant: float = chant.get_length() if chant else 30.0
	var par_image: float = maxf(fondu * 2.0, duree_chant / float(images.size()))
	_ecran_mat.set_shader_parameter("image_a", images[0])
	_ecran_mat.set_shader_parameter("image_b", images[0])
	_ecran_mat.set_shader_parameter("melange", 0.0)
	_ecran_mat.set_shader_parameter("force", 0.0)
	ecran.visible = true
	var allume := create_tween().set_trans(Tween.TRANS_SINE)
	allume.tween_method(_force, 0.0, 1.0, 2.0)
	for i in range(1, images.size() + 1):
		var fin: float = Time.get_ticks_msec() / 1000.0 + par_image - fondu
		while Time.get_ticks_msec() / 1000.0 < fin and not _arret_demande:
			await get_tree().process_frame
		if _arret_demande or i >= images.size():
			break
		_ecran_mat.set_shader_parameter("image_b", images[i])
		var passe := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		passe.tween_method(_melange, 0.0, 1.0, fondu)
		await passe.finished
		_ecran_mat.set_shader_parameter("image_a", images[i])
		_ecran_mat.set_shader_parameter("melange", 0.0)
	# le dernier tableau reste jusqu'à la fin du chant
	while _son.playing and not _arret_demande:
		await get_tree().process_frame
	if _son.playing:
		var fin_son := create_tween()
		fin_son.tween_property(_son, "volume_db", -40.0, 1.2)
		fin_son.tween_callback(_son.stop)
		fin_son.tween_property(_son, "volume_db", 0.0, 0.0)
	var eteint := create_tween().set_trans(Tween.TRANS_SINE)
	eteint.tween_method(_force, 1.0, 0.0, 2.0)
	await eteint.finished
	ecran.visible = false


## Plan de côté sur la prise (comme pour les lanternes) : le premier point d'où l'on voit le geste sans mur
## entre la caméra et le robot.
func _plan_de_cote(cible: Vector3, normale: Vector3) -> Vector3:
	var droite := (-normale).cross(Vector3.UP).normalized()
	var essais: Array[Vector3] = [
		cible + droite * 3.4 + normale * 0.6 + Vector3.UP * 0.6,
		cible - droite * 3.4 + normale * 0.6 + Vector3.UP * 0.6,
		cible + droite * 2.6 + normale * 1.8 + Vector3.UP * 2.2,
		cible - droite * 2.6 + normale * 1.8 + Vector3.UP * 2.2,
	]
	var espace := get_world_3d().direct_space_state
	for p: Vector3 in essais:
		var q := PhysicsRayQueryParameters3D.create(cible, p)
		q.exclude = [_joueur.get_rid()]
		if espace.intersect_ray(q).is_empty():
			return p
	return cible + normale * 3.4 + Vector3.UP * 2.5


func _flux(v: float) -> void:
	_cable.materiau.set_shader_parameter("flux", v)


func _force(v: float) -> void:
	_ecran_mat.set_shader_parameter("force", v)


func _melange(v: float) -> void:
	_ecran_mat.set_shader_parameter("melange", v)


func _ranger_cable() -> void:
	_cable.visible = false
	_retrait = -1.0
