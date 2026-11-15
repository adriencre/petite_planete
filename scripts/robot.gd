extends CharacterBody3D
## Petit robot qui se promène tranquillement. ZQSD / flèches, E pour agir.
## N (jamais indiqué à l'écran) : éteindre / rallumer l'antenne → le monde des Lueurs.
## Il ne tombe ni dans l'eau ni du haut des falaises : il faut prendre les escaliers.

const PULSE := preload("res://scenes/fx/energy_pulse.tscn")
const GLYPH_CAST := preload("res://scenes/fx/glyph_cast.tscn")
const ANTENNA_SENSE := 4.0 ## distance où l'antenne commence à grésiller (mètres)

@export var speed := 2.0
@export var acceleration := 5.0
@export var turn_speed := 7.0

@onready var model: Node3D = $Model
@onready var anim: AnimationPlayer = $AnimationPlayer
@onready var carry_point: Node3D = $Model/CarryPoint
@onready var antenna_tip: Node3D = $Model/Rig/LookPivot/Head/Antenna/Tip
@onready var face: Node3D = $Model/Rig/LookPivot/Head
@onready var _look_pivot: Node3D = $Model/Rig/LookPivot

## Vrai pendant une action (impulsion, embarquement…) : le joueur ne contrôle plus le robot.
var busy := false
## Antenne éteinte (touche N) : la brume ne le vide plus et il voit les Lueurs, mais plus aucune lumière.
var night_mode := false
## Objet porté au-dessus de la tête (ex. une graine).
var held: Node3D
## Batterie : la brume la vide, la lumière la recharge (voir scripts/robot/robot_battery.gd).
@onready var battery: RobotBattery = $Battery
## Assez d'énergie pour agir (allumer une lanterne coûte au moins ça).
var has_energy: bool:
	get:
		return battery != null and battery.level >= 15.0

var _step_timer := 0.0
var _glance_target := Vector3.ZERO
var _glance_time := 0.0
var _antenna_material: ShaderMaterial
var _sparks: CPUParticles3D
var _flicker := 0.0

var _nearby: Array[Interactable] = []
var _focus: Interactable
var _time := 0.0


func _ready() -> void:
	add_to_group(&"player")
	var tip := antenna_tip as MeshInstance3D
	_antenna_material = (tip.get_surface_override_material(0) as ShaderMaterial).duplicate()
	tip.set_surface_override_material(0, _antenna_material)
	_sparks = _make_sparks()
	antenna_tip.add_child(_sparks)
	battery.depleted.connect(_on_battery_depleted)
	_set_antenna(battery.antenna_glow())


# ---------- énergie de l'antenne ----------
## Remplit la batterie d'un coup (pierre-soleil), avec un éclat de l'antenne.
func recharge_full() -> void:
	battery.fill(2.0)
	var t := create_tween()
	t.tween_method(_set_antenna, 3.0, 1.0, 0.8)
	Audio.play("power_on", null, -8.0, 1.6)


## Batterie vide : le robot s'affaisse et s'éteint sur place. Son corps restera là ;
## sa conscience retourne au berceau (voir scripts/loop/loop_state.gd).
func _on_battery_depleted() -> void:
	busy = true
	velocity = Vector3.ZERO
	if Notebook.is_open:
		Notebook.close()
	anim.speed_scale = 1.0
	anim.play(&"sad", 0.4)
	face.set_expression(&"sad", 0.6)
	_sparks.emitting = false
	Audio.play("power_on", null, -6.0, 0.45)
	await get_tree().create_timer(1.4).timeout
	face.set_expression(&"off", 0.8)
	_set_antenna(0.0)
	Loop.end_loop(self)


func _set_antenna(level: float) -> void:
	var off := Color(0.45, 0.45, 0.5)
	var on := Color(1.0, 0.81, 0.54)
	_antenna_material.set_shader_parameter("albedo", off.lerp(on, clampf(level, 0.0, 1.0)))
	_antenna_material.set_shader_parameter("emission_strength", level * 1.2)


## Près d'une chose qui s'intéresse à l'énergie (pierre-soleil, lanterne…), l'antenne grésille.
func _update_antenna(delta: float) -> void:
	var best := INF
	for point in get_tree().get_nodes_in_group(&"energy_point"):
		if point.has_method("antenna_interest") and point.antenna_interest(self):
			best = minf(best, global_position.distance_to(point.global_position))
	var intensity := clampf(1.0 - best / ANTENNA_SENSE, 0.0, 1.0) if best < INF and not night_mode else 0.0
	_sparks.emitting = intensity > 0.05 and not busy
	_sparks.speed_scale = 0.4 + intensity
	((_sparks.mesh as SphereMesh).material as StandardMaterial3D).albedo_color = Color(1.0, 0.85, 0.55) if has_energy else Color(0.75, 0.82, 1.0)
	if busy:
		return
	var base := battery.antenna_glow()
	if intensity <= 0.05 and _flicker <= 0.0:
		_set_antenna(base)
	_flicker -= delta
	if intensity > 0.05 and _flicker <= 0.0:
		_flicker = randf_range(0.05, 0.6) / (0.3 + intensity)
		var spike := randf_range(0.6, 1.6) * intensity
		if randf() < 0.6:
			Audio.play("antenna_crackle", null, lerpf(-26.0, -14.0, intensity), randf_range(0.85, 1.2))
		var t := create_tween()
		t.tween_method(_set_antenna, base + spike, base, 0.12)


# Bruits de pas, au rythme de la marche (bois dans l'abri, herbe dehors).
func _footsteps(delta: float, moving: bool, speed_now: float) -> void:
	if not moving or busy:
		_step_timer = 0.15
		return
	_step_timer -= delta * clampf(speed_now / speed, 0.5, 1.2)
	if _step_timer <= 0.0:
		_step_timer = 0.4
		var wood := InteriorZone.inside_amount() > 0.5
		Audio.play_random("step_wood" if wood else "step_grass", 4, null, -14.0 if wood else -16.0)


## Tente d'agir sans énergie : l'antenne crachote, le robot penche la tête.
func fizzle() -> void:
	busy = true
	velocity = Vector3.ZERO
	anim.speed_scale = 1.0
	anim.play(&"fizzle", 0.15)
	Audio.play("fizzle", null, -6.0)
	face.set_expression(&"curious")
	var t := create_tween()
	for v in [0.6, 0.0, 0.3, 0.0, 0.15, 0.0]:
		t.tween_method(_set_antenna, v, v, 0.09)
	await anim.animation_finished
	face.set_expression(&"sad", 0.4)
	busy = false
	await get_tree().create_timer(1.5).timeout
	if face.expression == &"sad":
		face.set_expression(&"neutral")


## Trace un glyphe de lumière dans l'air avec l'antenne, puis l'envoie en filaments vers la cible.
## `slow` = version longue (première fois). Se termine quand les filaments arrivent.
func cast_glyph(glyph: StringName, target: Vector3, slow := false) -> void:
	busy = true
	velocity = Vector3.ZERO
	await face_toward(target, 0.35)
	anim.speed_scale = 1.0
	anim.play(&"cast", 0.25)
	face.set_expression(&"curious" if slow else &"neutral", 0.3)
	var cast: Node3D = GLYPH_CAST.instantiate()
	get_tree().current_scene.add_child(cast)
	var to := (target - global_position)
	to.y = 0.0
	cast.global_position = antenna_tip.global_position + Vector3.UP * (0.55 if slow else 0.45) + to.normalized() * 0.25
	await cast.play(glyph, antenna_tip, target, slow)
	anim.play(&"idle", 0.4)
	busy = false


func _make_sparks() -> CPUParticles3D:
	var p := CPUParticles3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.012
	mesh.height = 0.024
	mesh.radial_segments = 4
	mesh.rings = 2
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(1.0, 0.85, 0.55)
	mesh.material = mat
	p.mesh = mesh
	p.amount = 14
	p.lifetime = 0.45
	p.emitting = false
	p.local_coords = false
	p.direction = Vector3.UP
	p.spread = 80.0
	p.initial_velocity_min = 0.4
	p.initial_velocity_max = 1.1
	p.gravity = Vector3(0, -1.5, 0)
	p.scale_amount_min = 0.5
	p.scale_amount_max = 1.3
	return p


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and _focus and not busy:
		_focus.interact(self)
	elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_N and not busy:
		toggle_night()


# ---------- mode nuit ----------
## Éteint ou rallume l'antenne. La toute première fois, c'est un moment lent et silencieux.
func toggle_night() -> void:
	if busy or battery.level <= 0.0:
		return
	if night_mode:
		await _night_off()
	else:
		await _night_on()


func _night_on() -> void:
	var first := not Loop.has_flag(&"night_known")
	Loop.set_flag(&"night_known")
	night_mode = true
	battery.night = true
	busy = true
	velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if first and cam:
		cam.push_override(&"night", 5.0, 24.0, 0.6, self)
	face.set_expression(&"curious", 0.4)
	anim.speed_scale = 1.0
	anim.play(&"sad", 0.4)  # il baisse la tête…
	await get_tree().create_timer(1.0 if first else 0.3).timeout
	# …l'antenne vacille et s'éteint
	Audio.play("power_on", null, -10.0, 0.5)
	var flicker := create_tween()
	for v in ([0.8, 0.15, 0.6, 0.05, 0.3, 0.0] if first else [0.4, 0.0]):
		flicker.tween_method(_set_antenna, v, v, 0.14 if first else 0.08)
	await flicker.finished
	_sparks.emitting = false
	var dark := create_tween()
	dark.tween_property(battery, "night_amount", 1.0, 3.5 if first else 0.8).set_trans(Tween.TRANS_SINE)
	if first:
		await get_tree().create_timer(1.5).timeout
		anim.play(&"idle", 0.8)  # il relève la tête : tout brille autour de lui
		face.set_expression(&"surprised", 0.6)
		await get_tree().create_timer(2.5).timeout
		await emote(&"curious", &"look_around", 0.0)
		if cam:
			cam.pop_override(&"night")
	else:
		anim.play(&"idle", 0.4)
		face.set_expression(&"neutral", 0.6)
	busy = false


func _night_off() -> void:
	busy = true
	velocity = Vector3.ZERO
	var light := create_tween()
	light.tween_property(battery, "night_amount", 0.0, 0.8).set_trans(Tween.TRANS_SINE)
	await get_tree().create_timer(0.3).timeout
	night_mode = false
	battery.night = false
	Audio.play("power_on", null, -10.0, 1.2)
	var t := create_tween()
	t.tween_method(_set_antenna, 0.0, battery.antenna_glow() + 0.8, 0.25)
	t.tween_method(_set_antenna, battery.antenna_glow() + 0.8, battery.antenna_glow(), 0.4)
	await t.finished
	busy = false


# ---------- actions ----------
## Lève l'antenne et envoie une impulsion d'énergie vers la cible ; se termine à l'arrivée.
func pulse_toward(target: Vector3) -> void:
	busy = true
	velocity = Vector3.ZERO
	var to := target - global_position
	var turn := create_tween()
	turn.tween_property(model, "rotation:y", model.rotation.y + angle_difference(model.rotation.y, atan2(to.x, to.z)), 0.2)
	anim.speed_scale = 1.0
	anim.play(&"pulse", 0.15)
	await get_tree().create_timer(0.3).timeout
	var orb: Node3D = PULSE.instantiate()
	get_tree().current_scene.add_child(orb)
	orb.global_position = antenna_tip.global_position
	await orb.fly_to(target)
	busy = false


func pick_up(item: Node3D) -> void:
	held = item
	item.reparent(carry_point)
	create_tween().tween_property(item, "position", Vector3.ZERO, 0.4).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


## Vrai si le robot porte un objet de ce groupe (ex. &"seed").
func holds(group: StringName) -> bool:
	return held != null and held.is_in_group(group)


## Lâche l'objet porté et le renvoie.
func give_held() -> Node3D:
	var item := held
	held = null
	return item


## Exprime une émotion : forme des yeux + geste éventuel (wake_up, look_around, sad, happy).
## Le robot ne bouge pas pendant le geste ; ses yeux reviennent au neutre après `hold` secondes.
func emote(expression: StringName, gesture: StringName = &"", hold := 2.0) -> void:
	face.set_expression(expression)
	if gesture != &"":
		# pendant une mise en scène, le robot était déjà occupé : on ne lui rend pas la main trop tôt
		var was_busy := busy
		busy = true
		velocity = Vector3.ZERO
		anim.speed_scale = 1.0
		anim.play(gesture, 0.2)
		await anim.animation_finished
		busy = was_busy
	if hold > 0.0:
		await get_tree().create_timer(hold).timeout
		if face.expression == expression:
			face.set_expression(&"neutral")


## Jette un coup d'œil vers un point (un lieu remarquable) pendant quelques secondes.
func glance_at(point: Vector3, duration := 1.8) -> void:
	_glance_target = point
	_glance_time = duration
	if not busy and face.expression == &"neutral":
		face.set_expression(&"curious")
		get_tree().create_timer(duration).timeout.connect(func() -> void:
			if face.expression == &"curious":
				face.set_expression(&"neutral"))


## Tourne le corps vers un point.
func face_toward(target: Vector3, duration := 0.3) -> void:
	var to := target - global_position
	var tween := create_tween()
	tween.tween_property(model, "rotation:y", model.rotation.y + angle_difference(model.rotation.y, atan2(to.x, to.z)), duration)
	await tween.finished


# ---------- interaction : l'objet utilisable le plus proche ----------
func register_interactable(item: Interactable) -> void:
	if item not in _nearby:
		_nearby.append(item)


func unregister_interactable(item: Interactable) -> void:
	_nearby.erase(item)


func _update_focus() -> void:
	var best: Interactable = null
	var best_dist := INF
	if not busy:
		for item in _nearby:
			var d := global_position.distance_squared_to(item.global_position)
			if item.enabled and d < best_dist:
				best = item
				best_dist = d
	if best != _focus:
		if is_instance_valid(_focus):
			_focus.show_prompt(false)
		_focus = best
		if _focus:
			_focus.show_prompt(true)


# ---------- déplacement ----------
func _physics_process(delta: float) -> void:
	_update_focus()
	_update_look(delta)
	_update_antenna(delta)
	_time += delta
	carry_point.position.y = 1.95 + sin(_time * 2.2) * 0.05

	var input := Vector2.ZERO if busy else Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var dir := Vector3(input.x, 0.0, input.y)
	var cam := get_viewport().get_camera_3d()
	if cam:
		dir = dir.rotated(Vector3.UP, cam.global_rotation.y)

	var flat := Vector3(velocity.x, 0.0, velocity.z).lerp(dir * speed, 1.0 - exp(-acceleration * delta))
	flat = _keep_on_ground(flat)
	velocity.x = flat.x
	velocity.z = flat.z
	velocity.y = 0.0 if is_on_floor() else velocity.y - 9.8 * delta
	move_and_slide()

	var moving := flat.length() > 0.25
	_footsteps(delta, moving, flat.length())
	if moving:
		model.rotation.y = lerp_angle(model.rotation.y, atan2(flat.x, flat.z), 1.0 - exp(-turn_speed * delta))

	if busy:
		return  # l'animation de l'action en cours garde la main
	var wanted := &"walk" if moving else &"idle"
	if anim.current_animation != wanted:
		anim.play(wanted, 0.35)
	anim.speed_scale = clampf(flat.length() / speed, 0.6, 1.1) if moving else 1.0


# La tête se tourne doucement vers l'objet utilisable le plus proche.
func _update_look(delta: float) -> void:
	var yaw := 0.0
	var pitch := 0.0
	_glance_time -= delta
	var look_point: Variant = null
	if _focus:
		look_point = _focus.global_position
	elif _glance_time > 0.0:
		look_point = _glance_target
	if look_point != null and not busy:
		var local := model.global_transform.basis.inverse() * ((look_point as Vector3) - _look_pivot.global_position)
		yaw = clampf(atan2(local.x, local.z), -0.75, 0.75)
		pitch = clampf(-atan2(local.y + 0.6, Vector2(local.x, local.z).length()) * 0.5, -0.3, 0.3)
	var k := 1.0 - exp(-5.0 * delta)
	_look_pivot.rotation.y = lerp_angle(_look_pivot.rotation.y, yaw, k)
	_look_pivot.rotation.x = lerpf(_look_pivot.rotation.x, pitch, k)


# Annule le mouvement s'il n'y a pas de sol juste devant (en glissant le long des bords).
func _keep_on_ground(flat: Vector3) -> Vector3:
	if flat.length() < 0.01:
		return flat
	for candidate in [flat, Vector3(flat.x, 0, 0), Vector3(0, 0, flat.z)]:
		if candidate.length() > 0.01 and _ground_at(global_position + candidate.normalized() * 0.4):
			return candidate
	return Vector3.ZERO


func _ground_at(point: Vector3) -> bool:
	var query := PhysicsRayQueryParameters3D.create(point + Vector3.UP * 0.6, point + Vector3.DOWN * 0.6)
	query.exclude = [get_rid()]
	return not get_world_3d().direct_space_state.intersect_ray(query).is_empty()
