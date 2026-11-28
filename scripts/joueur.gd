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
## Recharge passive (mise à 0 par reveil.gd : seules la lumière et les pierres-soleil rechargent).
@export var recharge: float = 0.05
@export var energie_lumiere: float = 4.0
@export var couleur_lumiere: Color = Color(1.0, 0.8, 0.5)
@export_group("Animation")
@export var rebond: float = 0.04
@export var cadence_pas: float = 8.5
## Rebond et penché ajoutés par code. À décocher quand le modèle a ses propres animations de marche.
@export var balancement_procedural: bool = true

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
## En 1re personne, chaque cinématique commence par un recul doux jusqu'à la 3e personne (on voit le
## robot faire son geste), puis la caméra revient dans ses yeux à la fin (décidé le 2026-11-22).
var cinematique := false:
	set(v):
		if v == cinematique:
			return
		cinematique = v
		if v:
			_cine_3e = premiere_personne and not vue_dessus and not sur_echelle and embarque == null and not cine_sur_place
		elif _cine_3e:
			_cine_3e = false
		_transition_lente = true
## À mettre AVANT `cinematique = true` : la cinématique reste dans les yeux du robot (lire, ramasser un papier).
var cine_sur_place := false
## Vrai pendant une cinématique jouée en 3e personne alors que le joueur était en 1re.
var _cine_3e := false
## La caméra passe lentement entre 1re et 3e personne (recul de cinématique, puis retour).
var _transition_lente := false
## Durée du recul 1re → 3e personne et du retour (secondes).
@export var duree_recul_cinematique: float = 1.1
## Sur l’échelle, la scène place le robot au rythme des barreaux.
var sur_echelle := false
## Le banc place le corps et oriente le modèle pendant l’assise.
var sur_banc := false
var regard_cible := Vector3.ZERO
## Caméra de mise en scène quand on voit le robot (vue de dessus, 3e personne) :
## 0 = caméra de jeu, 1 = plan imposé depuis `cine_position` vers `cine_cible`.
var cine_melange := 0.0
var cine_position := Vector3.ZERO
var cine_cible := Vector3.ZERO
## Le véhicule qui porte le robot (la barque) : tant qu'il est là, c'est lui qui place le robot,
## son modèle et la caméra ; le joueur ne gère plus que la batterie (voir barque.gd).
var embarque: Node3D = null
var _pos_prec := Vector3.ZERO
var fov_normal := 60.0
## Mains articulées (tools/blender/mains_robot.py) : sortie du câble sur la bobine du poignet droit,
## et la fiche dans la main gauche qui la tient (point de pince et angle, repère de la main gauche ;
## mêmes valeurs que tools/godot/gestes_mains.py). Poses des mains levées et au repos (repère caméra).
const SORTIE_CABLE := Vector3(0.0, 0.040, 0.046)
## Centre de la fiche tenue par la main gauche, dans l'axe des doigts (reperes_mains.json).
const PINCE_G := Vector3(0.02213, -0.04817, -0.08333)
const MAIN_D_REPOS := Vector3(0.2, -0.62, -0.38)
const MAIN_G_REPOS := Vector3(-0.22, -0.62, -0.38)
const MAIN_D_LEVEE := Vector3(0.16, -0.19, -0.42)
const MAIN_G_LEVEE := Vector3(-0.19, -0.23, -0.4)
var _index_cible = null  # Vector3 monde ou null
## Vers où pointent les broches de la fiche quand on la porte à une prise (monde) ; ZERO = sans contrainte.
var _index_direction := Vector3.ZERO
## La main gauche tient la fiche : elle suit la fiche à chaque image (fiche décrochée par « tirer_fiche »).
var main_gauche_tient := false
var _fiche_repos: Transform3D
var _rot_main_d: Quaternion
var _rot_main_g: Quaternion
@onready var gestes: AnimationPlayer = $Camera/Mains/Gestes
@onready var _doigts_d: AnimationPlayer = $Camera/Mains/MainDroite/Modele/AnimationPlayer
@onready var _doigts_g: AnimationPlayer = $Camera/Mains/MainGauche/Modele/AnimationPlayer
const SILHOUETTE := preload("res://shaders/silhouette_robot.gdshader")
@onready var fiche: Node3D = $Camera/Mains/MainDroite/Fiche

## 0..1 ; lue par la scène pour la vision trouble et les créatures.
var batterie := 1.0
## false en mode N (piloté par la scène).
var antenne_allumee := true
var _allumage := 1.0
## Baisse la lampe de l'antenne quand les mains travaillent de près (sinon tout sature à 60 cm).
var _lampe_pres := 1.0
var _ampoule_mat := StandardMaterial3D.new()
var _retard := Vector2.ZERO

var _yaw := 0.0
## Vue de dessus : l'orientation des commandes. Quand la caméra tourne (zones de cadrage, camera_zones.gd),
## les touches gardent leur sens tant qu'on les tient ; elles suivent la nouvelle vue au relâchement.
var _yaw_commandes := 0.0
var _entree_precedente := Vector2.ZERO
var _pitch := -0.15
var _phase := 0.0
var _vitesse_lissee := 0.0
var _blend := 0.0  # 0 = 3e personne, 1 = 1re personne
var _gravite: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var _depart: Vector3
## Sous cette altitude, le robot est tombé de l'île : il revient au départ. Abaissée dans la grotte
## d'Aube, construite sous l'île (passage_grotte.gd).
var altitude_chute: float = -2.0


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
	lumiere.omni_attenuation = 0.8
	lumiere.light_volumetric_fog_energy = 2.5   # un halo dans la brume autour du robot
	_preparer_lueur()
	_fiche_repos = fiche.transform
	_rot_main_d = main_droite.quaternion
	_rot_main_g = main_gauche.quaternion
	for m in mains.find_children("*", "MeshInstance3D", true, false):
		(m as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_doigts_d.play("repos")
	_doigts_g.play("repos")



## La lueur de l'antenne : accrochée en haut de la tête du modèle (os « head_end »), elle suit la tête
## même pendant les animations ; un halo doux toujours tourné vers la caméra, et la lumière part de là.
var _lueur: Node3D
var _halo_mat := StandardMaterial3D.new()
var _coeur_mat := StandardMaterial3D.new()
## Centre de l'ampoule dans le modèle (m, au repos), mesuré sur les sommets jaunes de robot_meshy.glb.
@export var centre_ampoule: Vector3 = Vector3(0.028, 1.63, 0.26)
## Rayon du cœur lumineux de l'ampoule (m) et sa force (> 1 : il déclenche le glow).
@export var rayon_coeur: float = 0.07
@export var eclat_coeur: float = 3.0


## Quand une maison ou un toit cache le robot (vue de dessus), sa silhouette dorée se voit à travers
## (shaders/silhouette_robot.gdshader, en calque sur ses maillages).
func _preparer_silhouette() -> void:
	var calque := ShaderMaterial.new()
	calque.shader = SILHOUETTE
	for m in modele.find_children("*", "MeshInstance3D", true, false):
		var maillage := m as MeshInstance3D
		if maillage.material_overlay == null:
			maillage.material_overlay = calque


func _preparer_lueur() -> void:
	var squelettes := modele.find_children("*", "Skeleton3D", true, false)
	if squelettes.is_empty():
		return
	var sk := squelettes[0] as Skeleton3D
	# l'ampoule est portée par la tête : on s'accroche à l'os « Head » (celui qui déforme la tête)
	var b := sk.find_bone("Head")
	if b < 0:
		return
	var accroche := BoneAttachment3D.new()
	accroche.bone_name = "Head"
	sk.add_child(accroche)
	_lueur = Node3D.new()
	accroche.add_child(_lueur)
	# Le squelette Meshy est à l'échelle 0,01 : sans compensation, le halo faisait 9 mm. On place la
	# lueur sur l'ampoule : `centre_ampoule` est dans l'espace du maillage (pose de liaison du skin),
	# ramené dans le repère de l'os par sa pose de liaison ; puis on rend l'échelle 1.
	var bind := Transform3D.IDENTITY
	var maillage := sk.find_children("*", "MeshInstance3D", true, false)
	for mi in maillage:
		var skin := (mi as MeshInstance3D).skin
		if skin == null:
			continue
		for k in skin.get_bind_count():
			if skin.get_bind_name(k) == &"Head" or skin.get_bind_bone(k) == b:
				bind = skin.get_bind_pose(k)
		break
	_lueur.position = bind * centre_ampoule
	_lueur.scale = Vector3.ONE / (sk.global_transform * sk.get_bone_global_pose(b)).basis.get_scale()
	# le cœur de l'ampoule : une petite sphère additive, plus vive que le seuil du glow (> 1) : elle rayonne
	var coeur := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = rayon_coeur
	sphere.height = rayon_coeur * 2.0
	sphere.radial_segments = 12
	sphere.rings = 6
	_coeur_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_coeur_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_coeur_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	sphere.material = _coeur_mat
	coeur.mesh = sphere
	coeur.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_lueur.add_child(coeur)
	var q := QuadMesh.new()
	q.size = Vector2(0.9, 0.9)
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = degrade
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5, 0.0)
	_halo_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_halo_mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	_halo_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_halo_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_halo_mat.albedo_texture = tex
	q.material = _halo_mat
	var halo := MeshInstance3D.new()
	halo.mesh = q
	halo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_lueur.add_child(halo)


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
		if k.physical_keycode == KEY_V and not sur_echelle and not cinematique:   # (Échap : le menu pause, menu_pause.gd)
			# DEV : V fait le tour des caméras, sur toutes les îles :
			# vue de dessus → 1re personne → 3e personne → vue de dessus.
			if vue_dessus:
				vue_dessus = false
				premiere_personne = true
				_blend = 1.0
			elif premiere_personne:
				premiere_personne = false
			else:
				vue_dessus = true
			print("Caméra : ", "vue de dessus" if vue_dessus else ("1re personne" if premiere_personne else "3e personne"))


func _physics_process(delta: float) -> void:
	if embarque:
		velocity = Vector3.ZERO
		_gerer_batterie(delta)
		return
	if sur_banc:
		velocity = Vector3.ZERO
		_pos_prec = global_position
		_placer_camera(delta)
		_appliquer_cine()
		_gerer_batterie(delta)
		return
	if sur_echelle:
		_pos_prec = global_position
		var vers := regard_cible - global_position
		modele.rotation.y = lerp_angle(modele.rotation.y, atan2(vers.x, vers.z), 1.0 - exp(-8.0 * delta))
		_placer_camera(delta)
		_appliquer_cine()
		_gerer_batterie(delta)
		return
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
	var yaw_commandes := _yaw
	if vue_dessus and not cinematique:
		if dir_input != _entree_precedente or dir_input == Vector2.ZERO:
			_yaw_commandes = _yaw
		yaw_commandes = _yaw_commandes
	_entree_precedente = dir_input
	var basis_cam := Basis(Vector3.UP, yaw_commandes)
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
	if global_position.y < altitude_chute:
		global_position = _depart
		velocity = Vector3.ZERO
	_animer(delta, dir)
	_placer_camera(delta)
	_appliquer_cine()
	_gerer_batterie(delta)
	_placer_index()


func _animer(delta: float, dir: Vector3) -> void:
	var vh := Vector2(velocity.x, velocity.z).length()
	_vitesse_lissee = lerpf(_vitesse_lissee, vh, 1.0 - exp(-8.0 * delta))
	# en 3e personne le corps se tourne vers la marche ; en 1re il suit le regard
	var cible_yaw := modele.rotation.y
	var souplesse := 10.0
	if _blend > 0.5:
		cible_yaw = _yaw + PI
	elif cinematique:
		# mise en scène vue de l'extérieur : il regarde où il va, puis ce qu'on lui montre
		var dep := Vector2(global_position.x - _pos_prec.x, global_position.z - _pos_prec.z)
		var vers := Vector2(regard_cible.x - global_position.x, regard_cible.z - global_position.z)
		if dep.length() > 0.5 * delta:
			cible_yaw = atan2(dep.x, dep.y)
		elif vers.length() > 0.05:
			cible_yaw = atan2(vers.x, vers.y)
		souplesse = 6.0
	elif dir.length() > 0.1:
		cible_yaw = atan2(dir.x, dir.z)
	_pos_prec = global_position
	modele.rotation.y = lerp_angle(modele.rotation.y, cible_yaw, 1.0 - exp(-souplesse * delta))
	# petits pas rebondis et un peu maladroits
	_phase += delta * cadence_pas * clampf(_vitesse_lissee / vitesse, 0.0, 1.6)
	var force := clampf(_vitesse_lissee / vitesse, 0.0, 1.0)
	if not balancement_procedural:
		modele.position.y = 0.0
		modele.rotation.x = 0.0
		modele.rotation.z = 0.0
		return
	modele.position.y = absf(sin(_phase)) * rebond * force
	modele.rotation.z = sin(_phase) * 0.03 * force
	modele.rotation.x = -0.12 * force if is_on_floor() else 0.1


## Le cadrage de la vue de dessus autour de `centre` (sert aussi à la barque pour y revenir en douceur).
func transform_vue_dessus(centre: Vector3) -> Transform3D:
	var b := Basis.from_euler(Vector3(-deg_to_rad(angle_dessus), deg_to_rad(orientation_dessus), 0))
	return Transform3D(b, centre + Vector3.UP + b * Vector3(0, 0, distance_dessus))


func _placer_camera(delta: float) -> void:
	if vue_dessus:
		_pitch = -deg_to_rad(angle_dessus)
		_yaw = deg_to_rad(orientation_dessus)
		camera.global_transform = transform_vue_dessus(global_position)
		modele.visible = true
		antenne_vue.visible = false
		lumiere.global_position = global_position + Vector3(0, 2.0 + modele.position.y, 0)
		return
	var blend_cible := 1.0 if premiere_personne and not _cine_3e else 0.0
	var vitesse_blend := 1.0 / maxf(0.1, duree_recul_cinematique) if _transition_lente else 2.5
	_blend = move_toward(_blend, blend_cible, delta * vitesse_blend)
	if is_equal_approx(_blend, blend_cible):
		_transition_lente = false
	if _cine_3e:
		mains.visible = false
	var t := _blend * _blend * (3.0 - 2.0 * _blend)
	pivot.position = Vector3(0, hauteur_pivot, 0)
	pivot.rotation = Vector3(_pitch, _yaw, 0)
	bras.spring_length = distance_camera
	var vue_3e: Transform3D = bras.global_transform * Transform3D(Basis(), Vector3(0, 0, bras.get_hit_length()))
	var tete := global_position + Vector3(0, hauteur_yeux + modele.position.y, 0)
	var vue_1re := Transform3D(Basis.from_euler(Vector3(_pitch, _yaw, 0)), tete + Basis(Vector3.UP, _yaw) * Vector3(0, 0, -0.36))
	camera.global_transform = vue_3e.interpolate_with(vue_1re, t)
	# le corps disparaît dès que la caméra arrive près de la tête (pas de plan à travers le robot)
	modele.visible = t < 0.6 and camera.global_position.distance_to(tete) > 0.75
	antenne_vue.visible = t > 0.5
	# l'antenne ballotte au rythme des pas et traîne derrière le regard
	_retard = _retard.lerp(Vector2.ZERO, 1.0 - exp(-6.0 * delta))
	var force := clampf(_vitesse_lissee / vitesse, 0.0, 1.0)
	antenne_vue.rotation = Vector3(sin(_phase * 2.0) * 0.025 * force - _retard.y * 0.5, _retard.x, sin(_phase) * 0.04 * force)
	# la lumière vient de l'ampoule visible (1re) ou du sommet de l'antenne (3e)
	var haut_3e := global_position + Vector3(0, 2.0 + modele.position.y, 0)
	lumiere.global_position = haut_3e.lerp(ampoule_vue.global_position, t)


## Porte la fiche en `p` (monde), broches tournées vers `direction` si elle est donnée ; null = fiche libre.
## En 1re personne, la fiche est tenue par la main gauche (après `tirer_fiche`), qui la suit.
func poser_index(p, direction := Vector3.ZERO) -> void:
	_index_cible = p
	_index_direction = direction


## Pose des doigts (clips de main_robot_*.glb : repos, ouverte, pincer), avec un fondu.
func pose_doigts(gauche: bool, pose: StringName, fondu: float = 0.2) -> void:
	(_doigts_g if gauche else _doigts_d).play(pose, fondu)


## Geste 1re personne : la main gauche décroche la fiche du poignet droit et tire le câble jusque devant
## soi (clip « tirer_fiche », assets/animations/gestes_mains.tres). Ensuite, la main gauche tient la fiche.
func tirer_fiche(vitesse: float = 1.0) -> void:
	main_gauche_tient = false
	gestes.play("tirer_fiche", 0.0, vitesse)
	await gestes.animation_finished
	main_gauche_tient = true


## La main gauche vient reprendre la fiche là où elle est (branchée dans une prise).
func prendre_fiche(duree: float) -> Tween:
	var prise := _main_gauche_sur_fiche()
	pose_doigts(true, &"ouverte", 0.15)
	var tw := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(main_gauche, "position", prise.origin, duree)
	tw.tween_property(main_gauche, "quaternion", prise.basis.get_rotation_quaternion(), duree)
	tw.tween_callback(pose_doigts.bind(true, &"pincer", 0.15)).set_delay(duree * 0.7)
	tw.chain().tween_callback(func() -> void: main_gauche_tient = true)
	return tw


## La main gauche ouvre les doigts et lâche la fiche (elle reste où elle est : prise, ou en l'air).
func lacher_fiche() -> void:
	main_gauche_tient = false
	pose_doigts(true, &"ouverte", 0.15)


## La fiche file se ranger dans son agrafe, sur la bobine du poignet : le câble s'enroule derrière elle.
func ranger_fiche(duree: float) -> Tween:
	var tw := create_tween().set_parallel().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tw.tween_property(fiche, "position", _fiche_repos.origin, duree)
	tw.tween_property(fiche, "quaternion", _fiche_repos.basis.get_rotation_quaternion(), duree)
	return tw


## Où mettre la main gauche (repère de Mains) pour que sa pince tienne la fiche.
func _main_gauche_sur_fiche() -> Transform3D:
	var pince := Transform3D(Basis(), PINCE_G)
	return main_droite.transform * fiche.transform * pince.affine_inverse()


func lever_mains(levees: bool, duree: float = 0.8) -> Tween:
	var tw := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT if levees else Tween.EASE_IN)
	if levees:
		mains.visible = premiere_personne
	if not main_gauche_tient:
		tw.tween_property(main_gauche, "position", MAIN_G_LEVEE if levees else MAIN_G_REPOS, duree)
		tw.tween_property(main_gauche, "quaternion", _rot_main_g, duree)
		pose_doigts(true, &"repos", duree * 0.5)
	if _index_cible == null:
		tw.tween_property(main_droite, "position", MAIN_D_LEVEE if levees else MAIN_D_REPOS, duree)
		tw.tween_property(main_droite, "quaternion", _rot_main_d, duree)
	tw.tween_property(camera, "fov", fov_normal - 8.0 if levees else fov_normal, duree * 1.5)
	if not levees:
		tw.chain().tween_callback(func() -> void: mains.visible = false)
	return tw


## Vrai quand on voit le robot de l'extérieur (vue de dessus ou caméra 3e personne).
func troisieme_personne() -> bool:
	return vue_dessus or _cine_3e or embarque != null or _blend < 0.5


## Où serait la caméra du joueur en ce moment, hors cinématique (vue de dessus, 1re ou 3e personne).
## Sert aux véhicules (barque.gd) pour partir de la vue du joueur et y revenir sans saut.
func transform_vue_libre() -> Transform3D:
	if vue_dessus:
		return transform_vue_dessus(global_position)
	var b := Basis.from_euler(Vector3(_pitch, _yaw, 0))
	if premiere_personne:
		var tete := global_position + Vector3(0, hauteur_yeux, 0)
		return Transform3D(b, tete + Basis(Vector3.UP, _yaw) * Vector3(0, 0, -0.36))
	return Transform3D(b, global_position + Vector3(0, hauteur_pivot, 0) + b * Vector3(0, 0, distance_camera))


## Tourne le regard (1re et 3e personne) vers une direction horizontale, la tête un peu baissée.
func regarder_vers(direction: Vector3, inclinaison: float = -0.12) -> void:
	_yaw = atan2(-direction.x, -direction.z)
	_pitch = inclinaison


## Pour cadrer une cinématique : direction (unitaire) où reculer la caméra depuis `depuis`.
## Vue de dessus : celle de la caméra de jeu. Sinon (3e personne, ou recul depuis la 1re) : derrière le
## robot par rapport à `depuis` (derrière son regard si `depuis` est le robot), un peu en hauteur.
func recul_cinematique(depuis: Vector3) -> Vector3:
	if vue_dessus:
		return (camera.global_position - depuis).normalized()
	var d := global_position - depuis
	d.y = 0.0
	if d.length() < 0.3:
		d = Basis(Vector3.UP, _yaw) * Vector3(0, 0, 1)
	return (d.normalized() + Vector3.UP * 0.75).normalized()


func _appliquer_cine() -> void:
	if cine_melange <= 0.001 or not troisieme_personne():
		return
	if cine_position.distance_to(cine_cible) < 0.01:
		return
	var plan := Transform3D(Basis.IDENTITY, cine_position).looking_at(cine_cible, Vector3.UP)
	var t := cine_melange * cine_melange * (3.0 - 2.0 * cine_melange)
	camera.global_transform = camera.global_transform.interpolate_with(plan, t)


func bout_index_monde() -> Vector3:
	if troisieme_personne() and modele.has_method("main_droite_monde"):
		var p: Vector3 = modele.call("main_droite_monde")
		return p
	return fiche.global_position


func poignet_droit_monde() -> Vector3:
	if troisieme_personne() and modele.has_method("main_droite_monde"):
		var p: Vector3 = modele.call("main_droite_monde")
		return p
	return main_droite.global_transform * SORTIE_CABLE


func position_ampoule() -> Vector3:
	return ampoule_vue.global_position if antenne_vue.visible else lumiere.global_position


func _placer_index() -> void:
	if _index_cible != null:
		# la fiche (repère de la main droite) glisse vers sa cible ; la main droite ne bouge pas
		var repere := main_droite.global_transform.affine_inverse()
		fiche.position = fiche.position.lerp(repere * (_index_cible as Vector3), 0.35)
		if _index_direction != Vector3.ZERO:
			var dir := (repere.basis * _index_direction).normalized()
			var voulu := Basis.looking_at(dir, repere.basis * Vector3.UP).get_rotation_quaternion()
			fiche.quaternion = fiche.quaternion.slerp(voulu, 0.25)
	if main_gauche_tient:
		main_gauche.transform = _main_gauche_sur_fiche()


func _gerer_batterie(delta: float) -> void:
	if antenne_allumee:  # la brume, elle, est gérée par brume_batterie.gd
		batterie += recharge * delta
	batterie = clampf(batterie, 0.02, 1.0)
	_allumage = move_toward(_allumage, 1.0 if antenne_allumee else 0.0, delta * 1.5)
	var niveau := batterie * _allumage
	if batterie < 0.3:
		niveau *= 0.55 + 0.45 * float(randf() > 0.25 - batterie * 0.5)
	_lampe_pres = move_toward(_lampe_pres, 0.3 if mains.visible else 1.0, delta * 1.2)
	lumiere.light_energy = energie_lumiere * niveau * _lampe_pres
	lumiere.omni_range = 3.0 + 4.5 * batterie
	if _lueur:
		_halo_mat.albedo_color = Color(couleur_lumiere.r, couleur_lumiere.g, couleur_lumiere.b, 0.75 * niveau)
		var c := couleur_lumiere.lerp(Color.WHITE, 0.35) * (eclat_coeur * niveau)
		_coeur_mat.albedo_color = Color(c.r, c.g, c.b, clampf(niveau * 1.5, 0.0, 1.0))
		if modele.visible:
			lumiere.global_position = _lueur.global_position
	_ampoule_mat.emission_energy_multiplier = 6.0 * niveau
	_ampoule_mat.albedo_color = Color(0.25, 0.25, 0.3).lerp(Color(1.0, 0.95, 0.8), niveau)
