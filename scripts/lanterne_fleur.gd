extends Node3D
## Lanterne-fleur des Semeurs. Éteinte, sa zone est endormie (grise).
## Le robot s'en approche, la regarde et appuie sur E : il s'accroupit, branche le câble de son
## poignet dans la prise, la lumière passe en pulsations, la lanterne se charge et s'ouvre en
## trois crans, la zone se réveille, puis il débranche. Rien de magique : c'est une machine.
## La première fois est longue (cinématique) ; les suivantes sont plus courtes.

const CABLE := preload("res://scripts/cable.gd")

@export var premiere_fois: bool = true
@export var index_zone: int = 0
@export var rayon_zone: float = 11.0
@export var cout_batterie: float = 0.2
@export var distance_activation: float = 5.0
## Distance à laquelle le cœur éteint commence à scintiller quand on le regarde.
@export var distance_appel: float = 9.0
@export var couleur_or: Color = Color(1.0, 0.78, 0.4)
@export var energie_lumiere: float = 2.4

var allumee := false
var _en_cours := false
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
var _joueur
var _zone


func _ready() -> void:
	for n in find_children("Petale*", "Node3D", true, false):
		_petales.append(n)
		_bases.append((n as Node3D).basis)
	_coeur = find_child("Coeur", true, false) as MeshInstance3D
	_prise = find_child("Prise", true, false) as Node3D
	_coeur_mat.albedo_color = Color(0.9, 0.89, 0.93)
	_coeur_mat.roughness = 0.15
	_coeur_mat.emission_enabled = true
	_coeur_mat.emission = couleur_or
	_coeur_mat.emission_energy_multiplier = 0.0
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
	_lumiere.position = Vector3(0, 1.6, 0)
	add_child(_lumiere)
	_preparer_pollen()
	_cable = CABLE.new()
	_cable.visible = false
	add_child(_cable)
	await get_tree().physics_frame
	await get_tree().physics_frame
	_poser_au_sol()
	_joueur = get_tree().get_first_node_in_group("joueur")
	_zone = get_tree().get_first_node_in_group("zone_endormie")
	if _zone:
		_zone.definir_zone(index_zone, global_position, rayon_zone)
		_zone.definir_eveil(index_zone, 0.0)


func _poser_au_sol() -> void:
	var p := global_position
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 30.0, p + Vector3.DOWN * 30.0)
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
	_pollen.position = Vector3(0, 1.6, 0)
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
		_cable.fin = _prise_position() if _fiche_posee else _joueur.bout_index_monde()
	if allumee or _en_cours or _joueur == null:
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


func _proche_et_regarde(distance: float) -> bool:
	if _joueur.vue_dessus:  # vue de dessus : on ne vise pas avec la caméra, la proximité suffit
		return _joueur.global_position.distance_to(global_position) < distance
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
		if not allumee and not _en_cours and _joueur and _proche_et_regarde(distance_activation):
			_allumer()


# ---------------------------------------------------------------- la séquence

func _allumer() -> void:
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
	await get_tree().create_timer(0.25 * k).timeout
	await _poser_index_vers(prise + normale * 0.02, 0.35 * k)
	# clic : la fiche est branchée, la prise s'allume
	_fiche_posee = true
	_joueur.fiche.visible = false
	var clic := create_tween()
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 3.0, 0.08)
	clic.tween_property(_prise_mat, "emission_energy_multiplier", 1.2, 0.4)
	await get_tree().create_timer(0.35 * k).timeout
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
	for cran in 3:
		var t := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		t.tween_method(_ouvrir, cran / 3.0, (cran + 1) / 3.0, 0.45 * k)
		await t.finished
		await get_tree().create_timer(0.3 * k).timeout
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
	await get_tree().create_timer(1.6 * k).timeout

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
	_en_cours = false
	_pollen.one_shot = false
	_pollen.amount = 12
	_pollen.explosiveness = 0.0
	_pollen.emitting = true


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
