extends CharacterBody3D
## Robot jouable pour le test caméra : 3e personne et 1re personne (touche V).
## Touches par position physique : ZQSD en AZERTY, WASD en QWERTY.

@export var vitesse: float = 3.6
@export var vitesse_course: float = 6.2
@export var saut: float = 4.6
@export var sensibilite_souris: float = 0.0025
@export var premiere_personne: bool = false
@export_group("3e personne")
@export var distance_camera: float = 4.2
@export var hauteur_pivot: float = 1.5
@export_group("Vue de dessus")
## Caméra haute et fixe (DA v6) : la souris ne tourne plus la vue, ZQSD suit l'écran.
@export var vue_dessus: bool = false
@export var distance_dessus: float = 20.0
@export_range(20.0, 89.0) var angle_dessus: float = 50.0
@export var orientation_dessus: float = 45.0
@export_group("1re personne")
@export var hauteur_yeux: float = 1.74
@export_group("Batterie")
## Touche B maintenue : simule la brume qui vide la batterie.
@export var vidage_brume: float = 0.12
@export var recharge: float = 0.05
@export var energie_lumiere: float = 1.6
@export var couleur_lumiere: Color = Color(1.0, 0.8, 0.5)
@export_group("Animation")
@export var rebond: float = 0.04
@export var cadence_pas: float = 8.5

@onready var modele: Node3D = $Modele
@onready var pivot: Node3D = $Pivot
@onready var bras: SpringArm3D = $Pivot/Bras
@onready var camera: Camera3D = $Camera
@onready var antenne_vue: Node3D = $Camera/AntenneVue
@onready var ampoule_vue: MeshInstance3D = $Camera/AntenneVue/Ampoule
@onready var lumiere: OmniLight3D = $Lumiere
@onready var mains: Node3D = $Camera/Mains
@onready var main_droite: Node3D = $Camera/Mains/MainDroite
@onready var main_gauche: Node3D = $Camera/Mains/MainGauche

## Mode cinématique : plus de contrôle, le regard est guidé vers `regard_cible`.
var cinematique := false
var regard_cible := Vector3.ZERO
var fov_normal := 60.0
## Position du bout de l'index droit (repère de la main) et poses des mains (repère caméra).
const BOUT_INDEX := Vector3(0.0, 0.012, -0.13)
const MAIN_D_REPOS := Vector3(0.2, -0.62, -0.38)
const MAIN_G_REPOS := Vector3(-0.22, -0.62, -0.38)
const MAIN_D_LEVEE := Vector3(0.16, -0.19, -0.42)
const MAIN_G_LEVEE := Vector3(-0.19, -0.23, -0.4)
var _index_cible = null  # Vector3 monde ou null
## Épaules (repère caméra) et longueurs des segments du bras.
const EPAULE_D := Vector3(0.25, -0.36, 0.12)
const EPAULE_G := Vector3(-0.25, -0.36, 0.12)
const LONG_BRAS := 0.34
@onready var bras_droit: Node3D = $Camera/Mains/BrasDroit
@onready var bras_gauche: Node3D = $Camera/Mains/BrasGauche
@onready var fiche: Node3D = $Camera/Mains/MainDroite/Fiche

## 0..1 ; lue par la scène pour la vision trouble et les créatures.
var batterie := 1.0
## false en mode N (piloté par la scène).
var antenne_allumee := true
var _allumage := 1.0
var _ampoule_mat := StandardMaterial3D.new()
var _retard := Vector2.ZERO

var _yaw := 0.0
var _pitch := -0.15
var _phase := 0.0
var _vitesse_lissee := 0.0
var _blend := 0.0  # 0 = 3e personne, 1 = 1re personne
var _gravite: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var _depart: Vector3


func _ready() -> void:
	# le modèle importé peut contenir des collisions (nœud « col ») : le robot se cognerait à lui-même
	for corps in modele.find_children("*", "CollisionObject3D", true, false):
		corps.queue_free()
	_depart = global_position
	_yaw = rotation.y
	rotation.y = 0.0
	_blend = 1.0 if premiere_personne else 0.0
	camera.current = true
	bras.add_excluded_object(get_rid())
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_ampoule_mat.albedo_color = Color(1.0, 0.95, 0.8)
	_ampoule_mat.emission_enabled = true
	_ampoule_mat.emission = couleur_lumiere
	ampoule_vue.material_override = _ampoule_mat
	lumiere.light_color = couleur_lumiere


func _unhandled_input(event: InputEvent) -> void:
	if (cinematique or vue_dessus) and event is InputEventMouseMotion:
		return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var m := event as InputEventMouseMotion
		_yaw -= m.relative.x * sensibilite_souris
		_pitch = clampf(_pitch - m.relative.y * sensibilite_souris, -1.3, 1.2)
		_retard += m.relative * 0.0006
	elif event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.physical_keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		elif k.physical_keycode == KEY_V:
			premiere_personne = not premiere_personne


func _physics_process(delta: float) -> void:
	var dir_input := Vector2(
		float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
		float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
	var course := Input.is_physical_key_pressed(KEY_SHIFT)
	if cinematique:
		dir_input = Vector2.ZERO
		var vers := regard_cible - camera.global_position
		var yaw_c := atan2(-vers.x, -vers.z)
		var pitch_c := atan2(vers.y, Vector2(vers.x, vers.z).length())
		_yaw = lerp_angle(_yaw, yaw_c, 1.0 - exp(-2.5 * delta))
		_pitch = lerpf(_pitch, pitch_c, 1.0 - exp(-2.5 * delta))
	var basis_cam := Basis(Vector3.UP, _yaw)
	var dir := basis_cam * Vector3(dir_input.x, 0.0, dir_input.y)
	if dir.length() > 1.0:
		dir = dir.normalized()
	var v := vitesse_course if course else vitesse
	velocity.x = lerpf(velocity.x, dir.x * v, 1.0 - exp(-10.0 * delta))
	velocity.z = lerpf(velocity.z, dir.z * v, 1.0 - exp(-10.0 * delta))
	if is_on_floor():
		if Input.is_physical_key_pressed(KEY_SPACE) and not cinematique:
			velocity.y = saut
	else:
		velocity.y -= _gravite * delta
	move_and_slide()
	if global_position.y < -2.0:
		global_position = _depart
		velocity = Vector3.ZERO
	_animer(delta, dir)
	_placer_camera(delta)
	_gerer_batterie(delta)
	_placer_index()
	if mains.visible:
		_bras(bras_droit, EPAULE_D, main_droite.position + main_droite.basis * Vector3(0, 0, 0.1), Vector3(1.0, -1.0, 0.3))
		_bras(bras_gauche, EPAULE_G, main_gauche.position + main_gauche.basis * Vector3(0, 0, 0.1), Vector3(-1.0, -1.0, 0.3))


func _animer(delta: float, dir: Vector3) -> void:
	var vh := Vector2(velocity.x, velocity.z).length()
	_vitesse_lissee = lerpf(_vitesse_lissee, vh, 1.0 - exp(-8.0 * delta))
	# en 3e personne le corps se tourne vers la marche ; en 1re il suit le regard
	var cible_yaw := modele.rotation.y
	if _blend > 0.5:
		cible_yaw = _yaw + PI
	elif dir.length() > 0.1:
		cible_yaw = atan2(dir.x, dir.z)
	modele.rotation.y = lerp_angle(modele.rotation.y, cible_yaw, 1.0 - exp(-10.0 * delta))
	# petits pas rebondis et un peu maladroits
	_phase += delta * cadence_pas * clampf(_vitesse_lissee / vitesse, 0.0, 1.6)
	var force := clampf(_vitesse_lissee / vitesse, 0.0, 1.0)
	modele.position.y = absf(sin(_phase)) * rebond * force
	modele.rotation.z = sin(_phase) * 0.03 * force
	modele.rotation.x = -0.12 * force if is_on_floor() else 0.1


func _placer_camera(delta: float) -> void:
	if vue_dessus:
		_pitch = -deg_to_rad(angle_dessus)
		_yaw = deg_to_rad(orientation_dessus)
		var b := Basis.from_euler(Vector3(_pitch, _yaw, 0))
		camera.global_transform = Transform3D(b, global_position + Vector3.UP + b * Vector3(0, 0, distance_dessus))
		modele.visible = true
		antenne_vue.visible = false
		lumiere.global_position = global_position + Vector3(0, 2.0 + modele.position.y, 0)
		return
	_blend = move_toward(_blend, 1.0 if premiere_personne else 0.0, delta * 2.5)
	var t := _blend * _blend * (3.0 - 2.0 * _blend)
	pivot.position = Vector3(0, hauteur_pivot, 0)
	pivot.rotation = Vector3(_pitch, _yaw, 0)
	bras.spring_length = distance_camera
	var vue_3e: Transform3D = bras.global_transform * Transform3D(Basis(), Vector3(0, 0, bras.get_hit_length()))
	var tete := global_position + Vector3(0, hauteur_yeux + modele.position.y, 0)
	var vue_1re := Transform3D(Basis.from_euler(Vector3(_pitch, _yaw, 0)), tete + Basis(Vector3.UP, _yaw) * Vector3(0, 0, -0.36))
	camera.global_transform = vue_3e.interpolate_with(vue_1re, t)
	modele.visible = t < 0.6
	antenne_vue.visible = t > 0.5
	# l'antenne ballotte au rythme des pas et traîne derrière le regard
	_retard = _retard.lerp(Vector2.ZERO, 1.0 - exp(-6.0 * delta))
	var force := clampf(_vitesse_lissee / vitesse, 0.0, 1.0)
	antenne_vue.rotation = Vector3(sin(_phase * 2.0) * 0.025 * force - _retard.y * 0.5, _retard.x, sin(_phase) * 0.04 * force)
	# la lumière vient de l'ampoule visible (1re) ou du sommet de l'antenne (3e)
	var haut_3e := global_position + Vector3(0, 2.0 + modele.position.y, 0)
	lumiere.global_position = haut_3e.lerp(ampoule_vue.global_position, t)


## Pose la main droite pour que le bout de l'index touche `p` (monde) ; null = main libre.
func poser_index(p) -> void:
	_index_cible = p


func lever_mains(levees: bool, duree: float = 0.8) -> Tween:
	var tw := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT if levees else Tween.EASE_IN)
	if levees:
		mains.visible = premiere_personne
	tw.tween_property(main_gauche, "position", MAIN_G_LEVEE if levees else MAIN_G_REPOS, duree)
	if _index_cible == null:
		tw.tween_property(main_droite, "position", MAIN_D_LEVEE if levees else MAIN_D_REPOS, duree)
	tw.tween_property(camera, "fov", fov_normal - 8.0 if levees else fov_normal, duree * 1.5)
	if not levees:
		tw.chain().tween_callback(func() -> void: mains.visible = false)
	return tw


func bout_index_monde() -> Vector3:
	return main_droite.global_transform * BOUT_INDEX


func poignet_droit_monde() -> Vector3:
	return main_droite.global_transform * Vector3(0, 0, 0.09)


## Bras à deux segments (épaule -> coude -> poignet), coude poussé vers `pole`.
func _bras(b: Node3D, epaule: Vector3, poignet: Vector3, pole: Vector3) -> void:
	var v := poignet - epaule
	var d := clampf(v.length(), 0.05, LONG_BRAS * 2.0 - 0.001)
	var dir := v.normalized()
	var a := d * 0.5
	var h := sqrt(maxf(LONG_BRAS * LONG_BRAS - a * a, 0.0))
	var p := (pole - dir * pole.dot(dir)).normalized()
	var coude := epaule + dir * a + p * h
	var main := epaule + dir * d
	(b.get_node("Epaule") as Node3D).position = epaule
	(b.get_node("Coude") as Node3D).position = coude
	_segment(b.get_node("Haut"), epaule, coude)
	_segment(b.get_node("Avant"), coude, main)


func _segment(n: Node3D, a: Vector3, b: Vector3) -> void:
	var y := b - a
	var l := y.length()
	if l < 0.001:
		return
	y /= l
	var x := y.cross(Vector3.BACK)
	if x.length() < 0.01:
		x = Vector3.RIGHT
	x = x.normalized()
	var z := x.cross(y)
	n.transform = Transform3D(Basis(x, y * l, z), (a + b) * 0.5)


func position_ampoule() -> Vector3:
	return ampoule_vue.global_position if antenne_vue.visible else lumiere.global_position


func _placer_index() -> void:
	if _index_cible == null:
		return
	var cible: Vector3 = camera.global_transform.affine_inverse() * (_index_cible as Vector3)
	var voulu := cible - main_droite.basis * BOUT_INDEX
	main_droite.position = main_droite.position.lerp(voulu, 0.35)


func _gerer_batterie(delta: float) -> void:
	if Input.is_physical_key_pressed(KEY_B):
		batterie -= vidage_brume * delta
	elif antenne_allumee:
		batterie += recharge * delta
	batterie = clampf(batterie, 0.02, 1.0)
	_allumage = move_toward(_allumage, 1.0 if antenne_allumee else 0.0, delta * 1.5)
	var niveau := batterie * _allumage
	if batterie < 0.3:
		niveau *= 0.55 + 0.45 * float(randf() > 0.25 - batterie * 0.5)
	lumiere.light_energy = energie_lumiere * niveau
	lumiere.omni_range = 2.0 + 3.5 * batterie
	_ampoule_mat.emission_energy_multiplier = 6.0 * niveau
	_ampoule_mat.albedo_color = Color(0.25, 0.25, 0.3).lerp(Color(1.0, 0.95, 0.8), niveau)
