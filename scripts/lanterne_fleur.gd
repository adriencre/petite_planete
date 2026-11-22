extends Node3D
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## Lanterne-fleur des Semeurs. Éteinte, sa zone est endormie (grise).
## Le robot s'en approche, la regarde et appuie sur E : il s'accroupit, branche le câble de son
## poignet dans la prise, la lumière passe en pulsations, la lanterne se charge et s'ouvre en
## trois crans, la zone se réveille, puis il débranche. Rien de magique : c'est une machine.
## La première fois est longue (cinématique) ; les suivantes sont plus courtes.

const CABLE := preload("res://scripts/cable.gd")

@export var premiere_fois: bool = true
## Ordre d'allumage : une lanterne ne s'allume qu'une fois toutes celles de rang inférieur allumées
## (petites : 0, grande lanterne : 1, lanterne du sommet : 2).
@export var rang: int = 0
@export var index_zone: int = 0
@export var rayon_zone: float = 11.0
@export var cout_batterie: float = 0.2
@export var distance_activation: float = 5.0
## Distance à laquelle le cœur éteint commence à scintiller quand on le regarde.
@export var distance_appel: float = 9.0
@export var couleur_or: Color = Color(1.0, 0.78, 0.4)
## Pour se poser au sol, la lanterne cherche le sol en partant de cette hauteur au-dessus d'elle.
## Sous un toit (maison du quai) : petite valeur, sinon elle se pose sur ce qui est au-dessus.
@export var hauteur_recherche_sol: float = 30.0
@export var energie_lumiere: float = 2.4

## Batterie rendue au robot quand il reprend la lumière (`E` sur la lanterne allumée).
@export var gain_reprise: float = 0.5

## Geste « recharger » du robot (même clip qu'à la pierre-soleil) : instant où il est penché, l'antenne
## en avant (on l'y fige pendant la spirale), et instant où il est de nouveau droit.
const INSTANT_PENCHE := 2.07
const INSTANT_DEBOUT := 5.0

## Partagé par toutes les lanternes : la première reprise de lumière est longue et filmée.
static var reprise_faite: bool = false

var allumee := false
var _en_cours := false
var _coeur_albedo := Color.WHITE
var _petales: Array[Node3D] = []
var _bases: Array[Basis] = []
var _coeur: MeshInstance3D
var _coeur_mat := StandardMaterial3D.new()
var _prise: Node3D
var _prise_mat := StandardMaterial3D.new()
var _lumiere := OmniLight3D.new()
var _pollen := CPUParticles3D.new()
var _cable
var _fiche_posee := false
## -1 = rien ; 0..1 = le bout du câble revient de la prise vers le poignet.
var _retrait := -1.0
var _joueur
var _zone


var decor_seul := false
var ouverture_decor := false


func _ready() -> void:
	if decor_seul:
		set_process(false)
		set_physics_process(false)
		set_process_unhandled_input(false)
	else:
		add_to_group("lanternes")
		add_to_group("interactif")
		add_to_group("sauvegarde")
	for n in find_children("Petale*", "Node3D", true, false):
		_petales.append(n)
		_bases.append((n as Node3D).basis)
	_coeur = find_child("Coeur", true, false) as MeshInstance3D
	_prise = find_child("Prise", true, false) as Node3D
	# cœur texturé (lanterne-tulipe de Meshy) : on garde sa texture et on y ajoute la lueur ;
	# cœur sans texture (ancienne lanterne-fleur) : verre pâle uni.
	var texture: StandardMaterial3D = null
	if _coeur and _coeur.mesh and _coeur.mesh.get_surface_count() > 0:
		texture = _coeur.mesh.surface_get_material(0) as StandardMaterial3D
	if texture and texture.albedo_texture:
		_coeur_mat = texture.duplicate() as StandardMaterial3D
	else:
		_coeur_mat.albedo_color = Color(0.9, 0.89, 0.93)
		_coeur_mat.roughness = 0.15
	_coeur_mat.emission_enabled = true
	_coeur_mat.emission = couleur_or
	_coeur_mat.emission_energy_multiplier = 0.0
	_coeur_albedo = _coeur_mat.albedo_color
	if _coeur:
		_coeur.material_override = _coeur_mat
	_prise_mat.albedo_color = Color(0.85, 0.72, 0.48)
	_prise_mat.emission_enabled = true
	_prise_mat.emission = couleur_or
	_prise_mat.emission_energy_multiplier = 0.0
	var pc := find_child("PriseCoeur", true, false) as MeshInstance3D
	if pc:
		pc.material_override = _prise_mat
	_lumiere.light_color = couleur_or
	_lumiere.light_energy = 0.0
	_lumiere.omni_range = 7.0
	_lumiere.position = _pos_coeur()
	add_child(_lumiere)
	_preparer_pollen()
	if decor_seul:
		if ouverture_decor:
			allumer_tout_de_suite()
		return
	_cable = CABLE.new()
	_cable.visible = false
	add_child(_cable)
	await get_tree().physics_frame
	await get_tree().physics_frame
	_poser_au_sol()
	_joueur = get_tree().get_first_node_in_group("joueur")
	_zone = get_tree().get_first_node_in_group("zone_endormie") if index_zone >= 0 else null
	if _zone:
		_zone.definir_zone(index_zone, global_position, rayon_zone)
		_zone.definir_eveil(index_zone, 0.0)
	var sauve: Dictionary = Sauvegarde.donnees(cle_sauvegarde())
	if not sauve.is_empty():
		premiere_fois = bool(sauve.get("premiere_fois", premiere_fois))
		if bool(sauve.get("allumee", false)):
			allumer_tout_de_suite()


# ---------------------------------------------------------------- sauvegarde (sauvegarde.gd)

## Clé stable : la position au sol (les nœuds des lanternes ont des noms générés).
func cle_sauvegarde() -> String:
	return "lanterne:%d,%d" % [roundi(global_position.x), roundi(global_position.z)]


func sauver() -> Dictionary:
	return {"allumee": allumee, "premiere_fois": premiere_fois}


## « Continuer » : la lanterne est déjà allumée (sans son, sans geste), sa zone déjà réveillée.
func allumer_tout_de_suite() -> void:
	if allumee:
		return
	allumee = true
	premiere_fois = false
	_coeur_mat.emission_energy_multiplier = 7.0
	_coeur_mat.albedo_color = Color(1.0, 0.93, 0.75)
	_lumiere.light_energy = energie_lumiere
	_prise_mat.emission_energy_multiplier = 0.6
	if _coeur:
		_coeur.scale = Vector3.ONE * 1.5
	_ouvrir(1.0)
	_eveil(rayon_zone + 2.0)
	_pollen.one_shot = false
	_pollen.amount = 12
	_pollen.explosiveness = 0.0
	_pollen.emitting = true


## Le cœur dans le repère de la lanterne : la lumière et le pollen partent de là.
func _pos_coeur() -> Vector3:
	if _coeur:
		return to_local(_coeur.global_position)
	return Vector3(0, 1.6, 0)


## Pose la lanterne sur le terrain, en ignorant ses propres collisions (socle, bassin).
func _poser_au_sol() -> void:
	var p := global_position
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * hauteur_recherche_sol, p + Vector3.DOWN * 30.0)
	var exclus: Array[RID] = []
	for c in find_children("*", "CollisionObject3D", true, false):
		exclus.append((c as CollisionObject3D).get_rid())
	q.exclude = exclus
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	if hit:
		global_position = hit.position


func _preparer_pollen() -> void:
	var quad := QuadMesh.new()
	quad.size = Vector2(0.025, 0.025)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.vertex_color_use_as_albedo = true
	quad.material = m
	_pollen.mesh = quad
	_pollen.position = _pos_coeur()
	_pollen.emitting = false
	_pollen.amount = 60
	_pollen.lifetime = 3.5
	_pollen.one_shot = true
	_pollen.explosiveness = 0.8
	_pollen.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	_pollen.emission_sphere_radius = 0.15
	_pollen.direction = Vector3.UP
	_pollen.spread = 180.0
	_pollen.initial_velocity_min = 0.15
	_pollen.initial_velocity_max = 0.6
	_pollen.gravity = Vector3(0, 0.1, 0)
	_pollen.damping_min = 0.4
	_pollen.damping_max = 0.8
	var g := Gradient.new()
	g.set_color(0, Color(1, 0.9, 0.6, 1))
	g.set_color(1, Color(1, 0.75, 0.4, 0))
	_pollen.color_ramp = g
	add_child(_pollen)


func _process(_delta: float) -> void:
	if _cable and _cable.visible and _joueur:
		_cable.debut = _joueur.poignet_droit_monde()
		if _retrait >= 0.0:  # la fiche vient de sauter : le câble file se rembobiner dans le poignet
			_cable.fin = _prise_position().lerp(_cable.debut, _retrait)
		else:
			_cable.fin = _prise_position() if _fiche_posee else _joueur.bout_index_monde()
	if allumee or _en_cours or _joueur == null or not _prete():
		return
	# l'appel : le cœur éteint scintille quand on regarde la lanterne
	var onde := 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.004)
	var force := 0.0
	if _proche_et_regarde(distance_activation):
		force = 0.9
	elif _proche_et_regarde(distance_appel):
		force = 0.35
	_coeur_mat.emission_energy_multiplier = force * onde
	_prise_mat.emission_energy_multiplier = force * onde * 0.6


## Pour guidage.gd : 2 = E possible (l'allumer), 1 = à allumer, 0 = rien (allumée, ou pas encore prête).
## Reprendre la lumière d'une lanterne allumée reste une découverte : pas d'indication (guidage.gd).
func etat_interaction() -> int:
	if _joueur == null or _en_cours or allumee or not _prete():
		return 0
	if not bool(_joueur.get("cinematique")) and _proche_et_regarde(distance_activation) and _assez_de_lumiere():
		return 2
	return 1


## Allumer coûte `cout_batterie` : avec moins que ça (l'antenne presque vide du premier réveil),
## la lanterne refuse. Il faut d'abord aller à la pierre-soleil.
func _assez_de_lumiere() -> bool:
	return _joueur != null and float(_joueur.get("batterie")) >= cout_batterie


## Pas assez de lumière : la prise clignote deux fois, faiblement, et grésille. Rien ne s'allume.
func _refuser() -> void:
	_en_cours = true
	SONS.jouer("extinction", _prise_position(), -14.0, 1.5)
	var t := create_tween()
	for i in 2:
		t.tween_property(_prise_mat, "emission_energy_multiplier", 0.5, 0.08)
		t.tween_property(_prise_mat, "emission_energy_multiplier", 0.0, 0.25)
	await t.finished
	_en_cours = false


func point_appel() -> Vector3:
	return _prise_position()


## Vrai si on peut l'allumer : toutes les lanternes de rang inférieur sont allumées.
func _prete() -> bool:
	for l in get_tree().get_nodes_in_group("lanternes"):
		if l != self and int(l.get("rang")) < rang and not bool(l.get("allumee")):
			return false
	return true


func _proche_et_regarde(distance: float) -> bool:
	if _joueur.vue_dessus:  # vue de dessus : on ne vise pas avec la caméra, la proximité suffit
		var d: float = _joueur.global_position.distance_to(global_position)
		if d >= distance:
			return false
		# Plusieurs lanternes à portée (le parvis des Trois-Soleils) : seule la plus proche répond.
		for l in get_tree().get_nodes_in_group("lanternes"):
			if l != self and (l as Node3D).is_visible_in_tree() \
					and _joueur.global_position.distance_to((l as Node3D).global_position) < d:
				return false
		return true
	var cam: Camera3D = _joueur.camera
	var vers := (global_position + Vector3.UP * 1.2) - cam.global_position
	if vers.length() > distance:
		return false
	return (-cam.global_basis.z).dot(vers.normalized()) > 0.7


func _prise_position() -> Vector3:
	return _prise.global_position if _prise else global_position + Vector3.UP * 0.95


func _prise_normale() -> Vector3:
	var n := global_basis.z
	n.y = 0.0
	return n.normalized()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and (event as InputEventKey).physical_keycode == KEY_E:
		if _en_cours or _joueur == null or _joueur.cinematique or not _proche_et_regarde(distance_activation):
			return
		if not allumee and _prete():
			get_viewport().set_input_as_handled()
			if _assez_de_lumiere():
				_allumer()
			else:
				_refuser()
		elif allumee:
			get_viewport().set_input_as_handled()
			_reprendre()


# ---------------------------------------------------------------- la séquence

func _allumer() -> void:
	# on voit le robot (vue de dessus, 3e personne) et il sait jouer le geste : mise en scène extérieure
	var robot: Node = _joueur.modele
	if _joueur.troisieme_personne() and robot.has_method("jouer_action") and robot.call("a_animation", "brancher"):
		_allumer_3e(robot)
	else:
		_allumer_1re()


# ---------------------------------------------------------------- vue de l'extérieur

## Distance entre la prise et les pieds du robot : là où sa main touche le sol dans « brancher ».
const RECUL_GENOU := 0.62
## Moment de « brancher » (0..1) où la main arrive sur la prise.
const INSTANT_FICHE := 0.93
## Moment de « debrancher » (0..1) où il est debout, bras au ciel.
const INSTANT_BRAS_LEVES := 0.6


func _allumer_3e(robot: Node) -> void:
	_en_cours = true
	var k := 1.0 if premiere_fois else 0.45  # facteur de durée
	var v_geste := 1.0 / maxf(k, 0.55)        # les fois suivantes, les gestes sont plus vifs
	var ech := scale.x                         # la grande lanterne est plus haute : on recule le plan
	var prise := _prise_position()
	var normale := _prise_normale()
	_joueur.cinematique = true
	_joueur.regard_cible = prise

	# 1) il vient se placer devant la prise ; la caméra descend se poser de côté
	var place: Vector3 = prise + normale * RECUL_GENOU
	place.y = _joueur.global_position.y
	var depart: Vector3 = _joueur.global_position
	var trajet := Vector2(place.x - depart.x, place.z - depart.z).length()
	var centre := prise + normale * (RECUL_GENOU * 0.5)
	var cible_basse := centre + Vector3.UP * 0.8 * ech
	var cible_haute := centre + Vector3.UP * 1.3 * ech
	_joueur.cine_position = _plan_de_cote(cible_basse, normale, ech)
	_joueur.cine_cible = cible_basse
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, clampf(trajet / 1.3, 0.5, 3.5))
	approche.tween_property(_joueur, "cine_melange", 1.0, 1.4 + 1.2 * k)
	await approche.finished
	await get_tree().create_timer(0.45, false).timeout  # le temps de se tourner vers la prise

	# 2) il tire le câble de son poignet, pose un genou à terre et enfonce la fiche
	robot.call("jouer_action", "brancher", v_geste)
	var d_brancher: float = robot.call("duree", "brancher") / v_geste
	await get_tree().create_timer(d_brancher * INSTANT_FICHE, false).timeout
	# clic : la fiche est branchée, la prise s'allume
	_fiche_posee = true
	SONS.jouer("clic", _prise_position())
	_retrait = -1.0
	_cable.visible = true
	_cable.materiau.set_shader_parameter("flux", 0.0)
	var clic := create_tween()
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 3.0, 0.08)
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 1.2, 0.4)
	await get_tree().create_timer(d_brancher * (1.0 - INSTANT_FICHE) + 0.35 * k, false).timeout

	# 3) la lumière passe du robot à la lanterne ; il relève lentement la tête, la caméra suit
	var d_charge := 3.2 * k
	var d_tete: float = robot.call("duree", "brancher_lever_tete")
	robot.call("jouer_action", "brancher_lever_tete", d_tete / d_charge, 0.2)
	var charge := create_tween().set_parallel()
	charge.tween_method(_flux, 0.0, 1.0, 0.6 * k)
	charge.tween_property(_joueur, "batterie", maxf(0.05, _joueur.batterie - cout_batterie), d_charge)
	charge.tween_property(_coeur_mat, "emission_energy_multiplier", 3.0, d_charge).set_trans(Tween.TRANS_SINE)
	charge.tween_property(_coeur_mat, "albedo_color", Color(1.0, 0.93, 0.75), d_charge)
	charge.tween_property(_lumiere, "light_energy", energie_lumiere * 0.5, d_charge)
	charge.tween_property(_joueur, "cine_cible", cible_haute, d_charge).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await charge.finished

	# 4) la lanterne s'ouvre en trois crans mécaniques ; à genoux, il regarde
	SONS.jouer("allumage", to_global(_pos_coeur()))
	robot.call("jouer_action", "brancher_attente", 0.6, 0.4)
	for cran in 3:
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_method(_ouvrir, cran / 3.0, (cran + 1) / 3.0, 0.45 * k)
		await t.finished
		await get_tree().create_timer(0.3 * k, false).timeout
	_pollen.restart()
	_pollen.emitting = true
	var plein := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	plein.tween_property(_coeur_mat, "emission_energy_multiplier", 7.0, 0.8 * k)
	plein.tween_property(_lumiere, "light_energy", energie_lumiere, 0.8 * k)
	if _coeur:
		plein.tween_property(_coeur, "scale", Vector3.ONE * 1.5, 0.8 * k)
	plein.tween_method(_flux, 1.0, 0.0, 0.8 * k)

	# 5) la zone se réveille ; il se relève, bras au ciel, encore branché : le câble se tend
	var vague := create_tween()
	vague.tween_method(_eveil, 0.01, rayon_zone + 2.0, 4.5 * maxf(k, 0.55)).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await get_tree().create_timer(1.0 * k, false).timeout
	robot.call("jouer_action", "debrancher", v_geste, 0.25)
	var d_debrancher: float = robot.call("duree", "debrancher") / v_geste
	await get_tree().create_timer(d_debrancher * INSTANT_BRAS_LEVES, false).timeout

	# 6) la fiche saute et le câble file se rembobiner dans le poignet ; la caméra remonte
	_fiche_posee = false
	_prise_mat.emission_energy_multiplier = 0.6
	_retrait = 0.0
	var rembobine := create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	rembobine.tween_property(self, "_retrait", 1.0, 0.35)
	rembobine.tween_callback(_ranger_cable)
	var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 2.6 * maxf(k, 0.6))
	await get_tree().create_timer(d_debrancher * (1.0 - INSTANT_BRAS_LEVES), false).timeout
	robot.call("fin_action")
	_joueur.cinematique = false
	await vague.finished
	allumee = true
	premiere_fois = false   # on la rallumera (après une mort, une reprise) : la séquence sera courte
	_en_cours = false
	_pollen.one_shot = false
	_pollen.amount = 12
	_pollen.explosiveness = 0.0
	_pollen.emitting = true


func _ranger_cable() -> void:
	_cable.visible = false
	_retrait = -1.0


## Où poser la caméra : de côté, à hauteur du robot, pour voir à la fois son geste et la fleur.
## On préfère sa droite (le bras qui branche) ; si le relief bouche la vue, on essaie l'autre côté, puis plus haut.
func _plan_de_cote(cible: Vector3, normale: Vector3, ech: float) -> Vector3:
	var droite := (-normale).cross(Vector3.UP).normalized()
	var recul := 3.6 + 1.8 * (ech - 1.0)
	var essais: Array[Vector3] = [
		cible + droite * recul - normale * 0.3 + Vector3.UP * 0.45,
		cible - droite * recul - normale * 0.3 + Vector3.UP * 0.45,
		cible + droite * recul * 0.8 + normale * 1.2 + Vector3.UP * 2.2,
		cible - droite * recul * 0.8 + normale * 1.2 + Vector3.UP * 2.2,
	]
	var espace := get_world_3d().direct_space_state
	var corps_joueur: RID = _joueur.get_rid()
	var exclus: Array[RID] = [corps_joueur]
	for p: Vector3 in essais:
		var q := PhysicsRayQueryParameters3D.create(cible, p)
		q.exclude = exclus
		if espace.intersect_ray(q).is_empty():
			return p
	return cible + normale * recul + Vector3.UP * 3.0


# ---------------------------------------------------------------- à travers ses yeux (1re personne)

func _allumer_1re() -> void:
	_en_cours = true
	var k := 1.0 if premiere_fois else 0.4  # facteur de durée
	var prise := _prise_position()
	var normale := _prise_normale()
	_joueur.cinematique = true
	_joueur.regard_cible = prise + Vector3.UP * 0.15

	# 1) il s'approche et s'accroupit devant la prise
	var yeux_debout: float = _joueur.hauteur_yeux
	var place: Vector3 = prise + normale * 0.8
	place.y = _joueur.global_position.y
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, 1.6 * k)
	approche.tween_property(_joueur, "hauteur_yeux", 1.15, 1.2 * k).set_delay(0.8 * k)
	await approche.finished

	# 2) la fiche sort du poignet, la main la porte jusqu'à la prise
	_joueur.fiche.visible = true
	_cable.visible = true
	_cable.materiau.set_shader_parameter("flux", 0.0)
	await _joueur.lever_mains(true, 0.8 * k).finished
	await _poser_index_vers(prise + normale * 0.22, 0.9 * k)
	await get_tree().create_timer(0.25 * k, false).timeout
	await _poser_index_vers(prise + normale * 0.02, 0.35 * k)
	# clic : la fiche est branchée, la prise s'allume
	_fiche_posee = true
	SONS.jouer("clic", _prise_position())
	_joueur.fiche.visible = false
	var clic := create_tween()
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 3.0, 0.08)
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 1.2, 0.4)
	await get_tree().create_timer(0.35 * k, false).timeout
	_joueur.poser_index(null)
	_joueur.lever_mains(true, 0.6 * k)

	# 3) la lumière passe : pulsations dorées du robot vers la lanterne
	var charge := create_tween().set_parallel()
	charge.tween_method(_flux, 0.0, 1.0, 0.6 * k)
	charge.tween_property(_joueur, "batterie", maxf(0.05, _joueur.batterie - cout_batterie), 3.2 * k)
	charge.tween_property(_coeur_mat, "emission_energy_multiplier", 3.0, 3.2 * k).set_trans(Tween.TRANS_SINE)
	charge.tween_property(_coeur_mat, "albedo_color", Color(1.0, 0.93, 0.75), 3.2 * k)
	charge.tween_property(_lumiere, "light_energy", energie_lumiere * 0.5, 3.2 * k)
	await charge.finished

	# 4) la lanterne s'ouvre en trois crans mécaniques
	SONS.jouer("allumage", to_global(_pos_coeur()))
	for cran in 3:
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_method(_ouvrir, cran / 3.0, (cran + 1) / 3.0, 0.45 * k)
		await t.finished
		await get_tree().create_timer(0.3 * k, false).timeout
	_pollen.restart()
	_pollen.emitting = true
	var plein := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	plein.tween_property(_coeur_mat, "emission_energy_multiplier", 7.0, 0.8 * k)
	plein.tween_property(_lumiere, "light_energy", energie_lumiere, 0.8 * k)
	if _coeur:
		plein.tween_property(_coeur, "scale", Vector3.ONE * 1.5, 0.8 * k)
	plein.tween_method(_flux, 1.0, 0.0, 0.8 * k)

	# 5) la zone se réveille
	var vague := create_tween()
	vague.tween_method(_eveil, 0.01, rayon_zone + 2.0, 4.5 * maxf(k, 0.55)).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await get_tree().create_timer(1.6 * k, false).timeout

	# 6) il débranche, le câble s'enroule dans le poignet, il se relève
	await _poser_index_vers(prise + normale * 0.02, 0.5 * k)
	_fiche_posee = false
	_joueur.fiche.visible = true
	_prise_mat.emission_energy_multiplier = 0.6
	await _poser_index_vers(prise + normale * 0.3, 0.4 * k)
	_joueur.poser_index(null)
	_joueur.fiche.visible = false
	_cable.visible = false
	var fin := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	fin.tween_property(_joueur, "hauteur_yeux", yeux_debout, 1.0 * k)
	_joueur.lever_mains(false, 0.8 * k)
	await fin.finished
	_joueur.cinematique = false
	await vague.finished
	allumee = true
	premiere_fois = false   # on la rallumera (après une mort, une reprise) : la séquence sera courte
	_en_cours = false
	_pollen.one_shot = false
	_pollen.amount = 12
	_pollen.explosiveness = 0.0
	_pollen.emitting = true


# ---------------------------------------------------------------- reprendre la lumière

## E sur une lanterne allumée : le robot se place sous la fleur, la lumière quitte le cœur et
## descend en spirale dans l'ampoule de son antenne, la batterie remonte ; la fleur se referme
## en trois crans et sa zone se rendort. La première fois est longue et filmée.
func _reprendre() -> void:
	_en_cours = true
	var longue: bool = not reprise_faite
	reprise_faite = true
	var k := 1.0 if longue else 0.45
	var ech := scale.x
	var coeur := to_global(_pos_coeur())
	var normale := _prise_normale()
	_joueur.cinematique = true
	_joueur.regard_cible = coeur

	# 1) il vient se placer devant la fleur et lève les yeux vers le cœur
	var place: Vector3 = global_position + normale * (1.3 * ech)
	place.y = _joueur.global_position.y
	var trajet := Vector2(place.x - _joueur.global_position.x, place.z - _joueur.global_position.z).length()
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, clampf(trajet / 1.3, 0.4, 2.5))
	if longue and _joueur.troisieme_personne():
		var cible := (coeur + place + Vector3.UP * 1.2) * 0.5
		_joueur.cine_cible = cible
		_joueur.cine_position = _plan_de_cote(cible, normale, ech)
		approche.tween_property(_joueur, "cine_melange", 1.0, 2.0)
	await approche.finished
	await get_tree().create_timer(0.8 * k, false).timeout

	# il se penche vers le cœur, l'antenne tendue (le geste « recharger » de la pierre-soleil), et reste penché
	var robot: Node = _joueur.modele
	var geste: bool = _joueur.troisieme_personne() and robot.has_method("figer") and bool(robot.call("a_animation", "recharger"))
	var v_geste := 1.0 if longue else 1.6
	if geste:
		robot.call("jouer_action", "recharger", v_geste, 0.3)
		await get_tree().create_timer(INSTANT_PENCHE / v_geste, false).timeout
		robot.call("figer", true)

	# 2) la lumière descend en spirale dans l'antenne ; le cœur pâlit, la batterie remonte
	SONS.jouer("recharge", coeur, -2.0, 0.85)
	var duree := maxf(3.6 * k, 1.4)
	_pollen.emitting = false
	var vide := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	vide.tween_property(_joueur, "batterie", minf(1.0, _joueur.batterie + gain_reprise), duree)
	vide.tween_property(_coeur_mat, "emission_energy_multiplier", 0.0, duree)
	vide.tween_property(_coeur_mat, "albedo_color", _coeur_albedo, duree)
	vide.tween_property(_lumiere, "light_energy", 0.0, duree)
	if _coeur:
		vide.tween_property(_coeur, "scale", Vector3.ONE, duree)
	var nb := int(duree / 0.12)
	for i in nb:
		_spirale(coeur, i * 0.9, 1.1 if longue else 0.7)
		await get_tree().create_timer(duree / nb, false).timeout
	if vide.is_running():
		await vide.finished
	# rechargé, il se redresse (la fin du geste se joue pendant que la fleur se referme)
	var fin_geste := 0.0
	if geste:
		robot.call("figer", false)
		fin_geste = Time.get_ticks_msec() / 1000.0 + (INSTANT_DEBOUT - INSTANT_PENCHE) / v_geste

	# 3) la fleur se referme en trois crans ; sa zone se rendort autour d'eux
	var sommeil := create_tween()
	sommeil.tween_method(_eveil, rayon_zone + 2.0, 0.0, 4.0 * maxf(k, 0.55)).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	for cran in 3:
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_method(_ouvrir, 1.0 - cran / 3.0, 1.0 - (cran + 1) / 3.0, 0.45 * k)
		await t.finished
		await get_tree().create_timer(0.3 * k, false).timeout

	if geste:
		var reste := fin_geste - Time.get_ticks_msec() / 1000.0
		if reste > 0.0:
			await get_tree().create_timer(reste, false).timeout
		robot.call("fin_action")

	# 4) la caméra remonte, on rend la main
	if _joueur.cine_melange > 0.0:
		var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		retour.tween_property(_joueur, "cine_melange", 0.0, 2.2)
		await get_tree().create_timer(0.8, false).timeout
	_joueur.cinematique = false
	allumee = false
	if sommeil.is_running():
		await sommeil.finished
	_remettre_pollen()
	_en_cours = false


## Une petite boule dorée qui quitte le cœur et tourne en spirale jusqu'à l'ampoule de l'antenne.
func _spirale(depuis: Vector3, phase: float, duree: float) -> void:
	var boule := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.04
	sphere.height = 0.08
	sphere.radial_segments = 8
	sphere.rings = 4
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(1.0, 0.88, 0.55)
	m.emission_enabled = true
	m.emission = couleur_or
	m.emission_energy_multiplier = 4.0
	sphere.material = m
	boule.mesh = sphere
	boule.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	boule.top_level = true
	add_child(boule)
	boule.global_position = depuis
	var t := create_tween()
	t.tween_method(func(x: float) -> void:
		if not is_instance_valid(boule) or _joueur == null:
			return
		var fin: Vector3 = _joueur.position_ampoule()
		var axe := (fin - depuis).normalized()
		var u := axe.cross(Vector3.UP).normalized() if absf(axe.y) < 0.99 else Vector3.RIGHT
		var v := axe.cross(u)
		var a := phase + x * TAU * 2.0
		var r := 0.4 * (1.0 - x)          # la spirale se resserre en arrivant
		boule.global_position = depuis.lerp(fin, x) + (u * cos(a) + v * sin(a)) * r
		boule.scale = Vector3.ONE * (1.0 - 0.5 * x), 0.0, 1.0, duree).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(boule.queue_free)


## Allumée sans le robot (la cascade de la fin, quand la lanterne du sommet s'allume) : le cœur
## s'éclaire, la fleur s'ouvre, le pollen s'envole et la zone se réveille en vague.
func allumer_seule(duree: float = 1.6) -> void:
	if allumee or _en_cours:
		return
	_en_cours = true
	SONS.jouer("allumage", to_global(_pos_coeur()), -4.0, randf_range(0.95, 1.08))
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	t.tween_property(_coeur_mat, "emission_energy_multiplier", 7.0, duree)
	t.tween_property(_coeur_mat, "albedo_color", Color(1.0, 0.93, 0.75), duree)
	t.tween_property(_lumiere, "light_energy", energie_lumiere, duree)
	t.tween_property(_prise_mat, "emission_energy_multiplier", 0.6, duree)
	if _coeur:
		t.tween_property(_coeur, "scale", Vector3.ONE * 1.5, duree)
	t.tween_method(_ouvrir, 0.0, 1.0, duree).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	t.tween_method(_eveil, 0.01, rayon_zone + 2.0, duree * 2.8).set_ease(Tween.EASE_IN_OUT)
	_pollen.restart()
	_pollen.emitting = true
	await t.finished
	allumee = true
	premiere_fois = false
	_en_cours = false
	_pollen.one_shot = false
	_pollen.amount = 12
	_pollen.explosiveness = 0.0
	_pollen.emitting = true


## Éteinte d'un coup (le robot est mort, l'écran est noir) : fleur fermée, zone endormie.
func eteindre() -> void:
	if not allumee:
		return
	allumee = false
	_ouvrir(0.0)
	_coeur_mat.emission_energy_multiplier = 0.0
	_coeur_mat.albedo_color = _coeur_albedo
	_prise_mat.emission_energy_multiplier = 0.0
	_lumiere.light_energy = 0.0
	if _coeur:
		_coeur.scale = Vector3.ONE
	_eveil(0.0)
	_remettre_pollen()


## Le pollen redevient une bouffée unique, prête pour le prochain allumage.
func _remettre_pollen() -> void:
	_pollen.emitting = false
	_pollen.one_shot = true
	_pollen.amount = 60
	_pollen.explosiveness = 0.8


## Amène le bout de l'index (qui tient la fiche) jusqu'à `cible`, en douceur.
func _poser_index_vers(cible: Vector3, duree: float) -> Signal:
	var depart: Vector3 = _joueur.bout_index_monde()
	var tw := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_method(_index_entre.bind(depart, cible), 0.0, 1.0, duree)
	return tw.finished


func _index_entre(t: float, a: Vector3, b: Vector3) -> void:
	_joueur.poser_index(a.lerp(b, t))


func _flux(v: float) -> void:
	_cable.materiau.set_shader_parameter("flux", v)


func _eveil(v: float) -> void:
	if _zone:
		_zone.definir_eveil(index_zone, v)


func _ouvrir(v: float) -> void:
	for i in _petales.size():
		_petales[i].basis = _bases[i] * Basis(Vector3.RIGHT, -1.15 * v)
