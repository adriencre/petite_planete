@tool
class_name WakeLantern
extends Node3D
## Lanterne à rallumer avec l'antenne du robot : il trace le symbole « lumière » dans l'air,
## qui vole en filaments jusqu'à elle. Allumée, elle éclôt, réveille sa zone
## et peut envoyer une racine lumineuse vers une autre lanterne.
## Allumée, le robot peut aussi REPRENDRE sa lumière (E) : elle descend en spirale dans son antenne,
## la batterie remonte, la lanterne s'éteint et sa zone se rendort. On peut la rallumer ensuite.
## `first_light` = la toute première lanterne du jeu : version longue, caméra rapprochée.

const BLOOM := preload("res://scenes/fx/lantern_bloom.tscn")

signal lit_up
signal went_out

@export var wake_zone: WakeZone ## zone réveillée quand on l'allume
@export var needs: Array[WakeLantern] = [] ## lanternes à allumer avant celle-ci
@export var vine: EnergyVine ## racine lumineuse qui part d'ici une fois allumée
@export var start_lit := false
@export var first_light := false ## première lumière du jeu : un vrai moment
@export var energy_cost := 20.0 ## batterie dépensée pour l'allumer
@export var recharge := 15.0 ## recharge par seconde près d'elle une fois allumée
@export var recharge_radius := 3.5
@export_range(-1, 5) var music_layer := -1 ## couche de musique ajoutée quand on l'allume (-1 = aucune)
@export var light_energy := 0.9
@export var can_take_back := true ## le robot peut reprendre sa lumière

var is_lit := false
var is_ready := false

@onready var _glow: MeshInstance3D = $Model/Glow
@onready var _light: OmniLight3D = $Model/Light
@onready var _interactable: Interactable = $Interactable

var _glow_material: ShaderMaterial
var _off_color := Color(0.42, 0.42, 0.46)
var _on_color := Color(1.0, 0.81, 0.54)
var _time := 0.0


func _ready() -> void:
	if not Engine.is_editor_hint():
		add_to_group(&"energy_point")
	# matériau propre à cette lanterne, non grisé par le sommeil
	_glow_material = (_glow.get_surface_override_material(0) as ShaderMaterial).duplicate()
	_glow_material.set_shader_parameter("wake_affected", false)
	_glow.set_surface_override_material(0, _glow_material)
	if Engine.is_editor_hint():
		_set_glow(1.0)
		return
	_interactable.interacted.connect(_on_interacted)
	if start_lit:
		is_lit = true
		_interactable.enabled = can_take_back
		_set_glow(1.0)
		return
	_set_glow(0.0)
	for lantern in needs:
		lantern.lit_up.connect(_check_ready)
		lantern.went_out.connect(_check_ready)
	_check_ready()


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	# prête mais éteinte : elle « respire » doucement pour attirer l'œil
	if is_ready and not is_lit:
		_time += delta
		_set_glow(0.12 + 0.1 * sin(_time * 3.0))


## L'antenne du robot grésille près d'une lanterne prête à être rallumée.
func antenna_interest(_robot: Node3D) -> bool:
	return is_ready and not is_lit


func is_done() -> bool:
	return is_lit


## Allumée, elle recharge la batterie du robot à proximité.
func recharge_rate(pos: Vector3) -> float:
	if not is_lit:
		return 0.0
	var d := Vector2(pos.x - global_position.x, pos.z - global_position.z).length()
	return recharge if d < recharge_radius else 0.0


# Prête quand toutes les lanternes dont elle dépend sont allumées (et plus prête si l'une s'éteint).
func _check_ready() -> void:
	if is_lit:
		return
	var ok := true
	for lantern in needs:
		if not lantern.is_lit:
			ok = false
	is_ready = ok
	_interactable.enabled = ok
	if not ok:
		_set_glow(0.0)


func _on_interacted(robot: Node3D) -> void:
	if robot.night_mode:
		robot.fizzle()  # antenne éteinte : ni allumer, ni reprendre
		return
	if is_lit:
		if can_take_back:
			_take_back(robot)
		return
	if not is_ready:
		return
	if not robot.battery.can_spend(energy_cost):
		robot.fizzle()  # pas assez d'énergie : il faut d'abord trouver de la lumière
		return
	is_ready = false
	_interactable.enabled = false
	var cam := get_viewport().get_camera_3d()
	if first_light and cam:
		var middle := (robot.global_position + global_position) * 0.5 + Vector3(0, 1.0, 0)
		cam.push_override(&"first_light", 6.5, 20.0, 0.7, middle)
	robot.battery.spend(energy_cost, 2.5 if first_light else 1.0)
	await robot.cast_glyph(&"lumiere", _glow.global_position, first_light)
	light_up()
	if first_light:
		robot.face.set_expression(&"surprised", 0.3)
		await get_tree().create_timer(1.6).timeout
		if cam:
			cam.push_override(&"first_light", 13.0, 34.0, 0.5, global_position)
		await get_tree().create_timer(2.2).timeout
		robot.emote(&"happy", &"happy", 2.5)
		await get_tree().create_timer(1.2).timeout
		if cam:
			cam.pop_override(&"first_light")
	else:
		robot.emote(&"happy", &"happy")


## Allume la lanterne (aussi utilisable sans le robot).
func light_up() -> void:
	if is_lit:
		return
	is_lit = true
	var bloom: Node3D = BLOOM.instantiate()
	get_tree().current_scene.add_child(bloom)
	bloom.global_position = global_position
	bloom.play(first_light)
	Audio.play("lantern_bloom", null, -2.0 if first_light else -7.0)
	if first_light:
		Audio.stinger("stinger_first_light")
	if music_layer > 0:
		Audio.music_add_layer(music_layer, 10.0 if first_light else 6.0)
	var tween := create_tween()
	tween.tween_method(_set_glow, 3.0, 1.0, 1.2 if first_light else 0.7).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	if wake_zone:
		wake_zone.wake()
	if vine:
		await vine.play()
	lit_up.emit()
	_interactable.enabled = can_take_back


## Autorise (ou non) le robot à reprendre sa lumière, en cours de partie (ex. après la bascule).
func allow_take_back(on: bool) -> void:
	can_take_back = on
	if is_lit:
		_interactable.enabled = on


## Éteinte d'avance, sans mise en scène (ex. une veilleuse déjà reprise dans une boucle précédente).
func put_out_silently() -> void:
	if not is_lit:
		return
	is_lit = false
	_interactable.enabled = false
	_set_glow(0.0)
	if wake_zone:
		wake_zone.fall_asleep(0.01)
	went_out.emit()
	_check_ready()


## Le robot reprend la lumière : elle descend en spirale dans son antenne, la lanterne s'éteint,
## sa zone se rendort. La première fois du jeu, c'est un vrai moment (lent, caméra rapprochée).
func _take_back(robot: Node3D) -> void:
	_interactable.enabled = false
	var first := not Loop.has_flag(&"take_back_known")
	Loop.set_flag(&"take_back_known")
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		var middle := (robot.global_position + global_position) * 0.5 + Vector3(0, 0.8, 0)
		cam.push_override(&"take_back", 6.0 if first else 9.0, 22.0, 0.7 if first else 1.2, middle)
	await robot.face_toward(global_position, 0.4)
	robot.face.set_expression(&"curious", 0.5)
	if first:
		await get_tree().create_timer(1.0).timeout
	robot.anim.play(&"recharge", 0.3)
	await get_tree().create_timer(0.6).timeout
	var duration := 3.2 if first else 1.6
	var spiral := LightSpiral.play(self, _glow.global_position, robot.antenna_tip, 16 if first else 10, duration, 0.6)
	Audio.play("recharge", null, -4.0, 0.85)
	create_tween().tween_method(_set_glow, 1.0, 0.0, duration).set_trans(Tween.TRANS_SINE)
	robot.battery.gain(energy_cost, duration)
	await spiral
	is_lit = false
	if wake_zone:
		wake_zone.fall_asleep(5.0 if first else 3.0)
		Audio.play("wake_wave", null, -12.0, 0.7)
	if vine:
		vine.fade_out(2.0)
	went_out.emit()
	robot.anim.play(&"idle", 0.4)
	if first:
		# il regarde le monde se rendormir autour de lui
		robot.face.set_expression(&"surprised", 0.3)
		await get_tree().create_timer(2.0).timeout
		robot.face.set_expression(&"sad", 1.0)
		await get_tree().create_timer(2.2).timeout
	if cam:
		cam.pop_override(&"take_back")
	robot.face.set_expression(&"neutral", 0.8)
	robot.busy = false
	_check_ready()


func _set_glow(amount: float) -> void:
	_glow_material.set_shader_parameter("albedo", _off_color.lerp(_on_color, clampf(amount, 0.0, 1.0)))
	_glow_material.set_shader_parameter("emission_strength", amount * 2.0)
	_light.light_energy = amount * light_energy
	_light.visible = amount > 0.01
