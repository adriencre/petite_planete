extends Node3D
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## Pierre-soleil des Semeurs (assets/models/pierre_soleil_meshy.glb) : le robot y recharge son antenne.
## On s'approche, le cristal appelle (il pulse) ; E : le robot vient se placer face au cristal,
## des pulsations dorées passent du cristal à l'ampoule de l'antenne, la batterie remonte.
## La première fois (sur n'importe quelle pierre) est longue et filmée ; les suivantes sont courtes.

@export var distance_activation: float = 4.0
@export var distance_appel: float = 7.0
@export var couleur_or: Color = Color(1.0, 0.72, 0.32)
@export var energie_lumiere: float = 3.5
## Hauteur du rayon de lumière qui monte du cristal (on le voit de loin, à travers la brume).
@export var hauteur_rayon: float = 9.0
## Éclat du cristal au repos, et en plus quand il appelle le robot.
@export var eclat_repos: float = 5.0
@export var eclat_appel: float = 4.0
@export var duree_premiere: float = 4.0
@export var duree_suivantes: float = 1.6

## Clip « recharger » (révérence) : instant où l'ampoule arrive au cristal (on y fige le robot),
## et instant où il est de nouveau droit.
const INSTANT_PENCHE := 2.07
const INSTANT_DEBOUT := 5.0

## Partagé par toutes les pierres : le geste n'est mis en scène longuement qu'une fois.
static var deja_fait: bool = false

var _cristal: MeshInstance3D
var _mat: BaseMaterial3D
var _lumiere := OmniLight3D.new()
var _joueur: CharacterBody3D
var _en_cours: bool = false
var _centre: Vector3 = Vector3(0, 1.1, 0)


func _ready() -> void:
	_cristal = find_child("Cristal", true, false) as MeshInstance3D
	if _cristal and _cristal.mesh:
		var m := _cristal.mesh.surface_get_material(0)
		_mat = (m.duplicate() as BaseMaterial3D) if m is BaseMaterial3D else StandardMaterial3D.new()
		_mat.emission_enabled = true
		_mat.emission = couleur_or
		_mat.emission_energy_multiplier = eclat_repos
		_cristal.material_override = _mat
		_centre = to_local(_cristal.global_position)
	add_to_group("pierres_soleil")
	add_to_group("interactif")
	_lumiere.light_color = couleur_or
	_lumiere.light_energy = energie_lumiere
	_lumiere.omni_range = 7.0
	_lumiere.light_volumetric_fog_energy = 2.5   # un halo doré dans la brume autour de la pierre
	_lumiere.position = _centre + Vector3.UP * 0.2
	add_child(_lumiere)
	# le rayon qui monte du cristal : un repère qu'on voit de loin, même dans la brume
	var rayon := MeshInstance3D.new()
	rayon.name = "Rayon"
	var cone := CylinderMesh.new()
	cone.top_radius = 0.9
	cone.bottom_radius = 0.18
	cone.height = hauteur_rayon
	cone.radial_segments = 16
	cone.cap_top = false
	cone.cap_bottom = false
	var mat_rayon := ShaderMaterial.new()
	mat_rayon.shader = preload("res://shaders/rayon_lumiere.gdshader")
	mat_rayon.set_shader_parameter("couleur", couleur_or)
	mat_rayon.set_shader_parameter("hauteur", hauteur_rayon)
	cone.material = mat_rayon
	rayon.mesh = cone
	rayon.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	rayon.position = _centre + Vector3.UP * (hauteur_rayon * 0.5 - 0.1)
	add_child(rayon)
	if Engine.is_editor_hint():
		return
	var corps := StaticBody3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 0.45
	cyl.height = 1.6
	var cs := CollisionShape3D.new()
	cs.shape = cyl
	cs.position = Vector3.UP * 0.8
	corps.add_child(cs)
	add_child(corps)
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func _process(_delta: float) -> void:
	if _en_cours or _joueur == null or _mat == null:
		return
	# l'appel : le cristal pulse quand le robot approche, plus fort si sa batterie est basse
	var d: float = _distance()
	var b: float = _joueur.get("batterie")
	var onde: float = 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.004)
	var force: float = 0.0
	if d < distance_activation:
		force = 1.0
	elif d < distance_appel:
		force = 0.4
	force *= 0.4 + 0.6 * (1.0 - b)
	_mat.emission_energy_multiplier = eclat_repos + eclat_appel * force * onde
	_lumiere.light_energy = energie_lumiere * (1.0 + 0.6 * force * onde)


## Pour guidage.gd : 2 = E possible maintenant, 1 = utile (batterie pas pleine), 0 = rien.
## (`point_appel` : où se pose la lueur dorée.)
func etat_interaction() -> int:
	if _joueur == null or _en_cours:
		return 0
	if _distance() < distance_activation and not bool(_joueur.get("cinematique")):
		return 2
	return 1 if float(_joueur.get("batterie")) < 0.9 else 0


func point_appel() -> Vector3:
	return to_global(_centre)


func _distance() -> float:
	var a: Vector3 = _joueur.global_position
	return Vector2(a.x - global_position.x, a.z - global_position.z).length()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and (event as InputEventKey).physical_keycode == KEY_E:
		if not _en_cours and _joueur and not bool(_joueur.get("cinematique")) and _distance() < distance_activation:
			get_viewport().set_input_as_handled()
			_recharger()


# ---------------------------------------------------------------- la recharge

func _recharger() -> void:
	_en_cours = true
	var longue: bool = not deja_fait
	deja_fait = true
	var duree: float = duree_premiere if longue else duree_suivantes
	var centre: Vector3 = to_global(_centre)
	var vers_robot: Vector3 = _joueur.global_position - global_position
	vers_robot.y = 0.0
	vers_robot = vers_robot.normalized() if vers_robot.length() > 0.01 else Vector3.BACK
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", centre)

	# 1) il vient se placer face au cristal, l'antenne tendue vers lui
	var place: Vector3 = global_position + vers_robot * 0.95
	place.y = _joueur.global_position.y
	var approche := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	approche.tween_property(_joueur, "global_position", place, clampf(_distance() / 1.4, 0.4, 1.8))
	if longue:
		var cote: Vector3 = vers_robot.cross(Vector3.UP).normalized()
		var cible: Vector3 = (centre + place) * 0.5 + Vector3.UP * 0.5
		_joueur.set("cine_cible", cible)
		_joueur.set("cine_position", cible + cote * 2.8 + vers_robot * 0.8 + Vector3.UP * 0.7)
		approche.tween_property(_joueur, "cine_melange", 1.0, 1.8)
	await approche.finished
	await get_tree().create_timer(0.6 if longue else 0.15, false).timeout
	# il se penche vers le cristal, l'ampoule de l'antenne en avant, et reste penché
	var robot: Node = _joueur.get("modele")
	var geste: bool = robot != null and robot.has_method("figer") and bool(robot.call("a_animation", "recharger"))
	var v: float = 1.0 if longue else 1.8
	if geste:
		robot.call("jouer_action", "recharger", v, 0.3)
		await get_tree().create_timer(INSTANT_PENCHE / v, false).timeout
		robot.call("figer", true)

	# 2) les pulsations dorées passent du cristal à l'ampoule ; la batterie remonte
	SONS.jouer("recharge", centre)
	var depart: float = _joueur.get("batterie")
	var charge := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	charge.tween_property(_joueur, "batterie", 1.0, duree)
	charge.tween_property(_mat, "emission_energy_multiplier", eclat_repos + eclat_appel * 2.0, duree * 0.3)
	charge.tween_property(_lumiere, "light_energy", energie_lumiere * 2.2, duree * 0.3)
	var nb: int = int(duree / 0.22)
	for i in nb:
		_pulsation(centre, 0.55 if longue else 0.35)
		await get_tree().create_timer(duree / nb, false).timeout
	if charge.is_running():   # la charge a pu finir pendant les pulsations : on n'attend pas un signal déjà passé
		await charge.finished

	# 3) l'ampoule est pleine ; il se redresse, le cristal se calme
	if geste:
		robot.call("figer", false)
	var calme := create_tween().set_parallel()
	calme.tween_property(_mat, "emission_energy_multiplier", eclat_repos, 1.0)
	calme.tween_property(_lumiere, "light_energy", energie_lumiere, 1.0)
	if longue:
		await get_tree().create_timer(0.8, false).timeout
		var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		retour.tween_property(_joueur, "cine_melange", 0.0, 2.0)
		await get_tree().create_timer(0.6, false).timeout
	if geste:
		await get_tree().create_timer((INSTANT_DEBOUT - INSTANT_PENCHE) / v, false).timeout
		robot.call("fin_action")
	_joueur.set("cinematique", false)
	_en_cours = false
	print("pierre-soleil : batterie %.2f -> 1.00" % depart)


## Une petite boule dorée qui file du cristal à l'ampoule de l'antenne.
func _pulsation(depuis: Vector3, duree: float) -> void:
	var boule := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.045
	sphere.height = 0.09
	sphere.radial_segments = 8
	sphere.rings = 4
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(1.0, 0.85, 0.5)
	m.emission_enabled = true
	m.emission = couleur_or
	m.emission_energy_multiplier = 4.0
	sphere.material = m
	boule.mesh = sphere
	boule.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	boule.top_level = true   # accrochée à la pierre, mais placée en coordonnées monde
	add_child(boule)
	boule.global_position = depuis
	var t := create_tween()
	t.tween_method(func(x: float) -> void:
		if not is_instance_valid(boule):
			return
		var fin: Vector3 = _joueur.call("position_ampoule")
		var p: Vector3 = depuis.lerp(fin, x)
		p.y += sin(x * PI) * 0.25   # petite courbe, comme une étincelle qui saute
		boule.global_position = p
		boule.scale = Vector3.ONE * (1.0 - 0.5 * x), 0.0, 1.0, duree).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(boule.queue_free)
