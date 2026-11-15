@tool
class_name LueurDweller
extends Node3D
## Un habitant du monde de l'ombre (le petit peuple de lumière), visible seulement dans le noir.
## Il marche au sol, avec ses animations : il vaque à ses occupations (sa `routine`, ou autour de chez lui).
## Tant qu'il a peur du robot (`shy`), il rentre chez lui dès que le robot approche en bougeant ou antenne
## allumée ; mais si le robot reste éteint et immobile un moment, il ressort, s'approche… et on peut lui
## parler (E). Une fois la confiance gagnée (`shy = false`), il vient près du robot (si `follows`).
## Si sa maison est en cendre (zone éclairée), il reste caché.
## Les scripts de l'histoire le pilotent avec `scripted_target` / `scripted_hide`.

enum Form { PETITE, ENFANT, HERON, ANCIENNE, PECHEUR, JARDINIERE, TISSERAND }
const FORMS := ["Petite", "Enfant", "Heron", "Ancienne", "Pecheur", "Jardiniere", "Tisserand"]
const FORM_SCENES := [
	"res://assets/ombre/peuple/petite.tscn", "res://assets/ombre/peuple/enfant.tscn",
	"res://assets/ombre/peuple/compteur.tscn", "res://assets/ombre/peuple/ancienne.tscn",
	"res://assets/ombre/peuple/pecheur.tscn", "res://assets/ombre/peuple/jardiniere.tscn",
	"res://assets/ombre/peuple/tisserand.tscn",
]

@export var form := Form.PETITE:
	set(value):
		form = value
		_apply_form()
@export var size := 1.0:
	set(value):
		size = value
		if Engine.is_editor_hint() and is_inside_tree():
			scale = Vector3.ONE * size
@export var home: Node3D ## sa maison (il y rentre par la porte) ; sinon il se cache sur place
@export var door_distance := 1.25 ## distance de la porte devant le centre de la maison
@export var routine: Array[Node3D] = [] ## endroits où il va tour à tour (puits, marché…)
@export var pause := Vector2(4.0, 9.0) ## temps passé à chaque endroit
@export var shy := true ## a peur du robot (1re moitié du jeu)
@export var trust_flag: StringName ## dès que ce flag de boucle est posé, il n'a plus peur (ex. &"bascule")
@export var follows := true ## en confiance, il vient près du robot
@export var wander_radius := 1.2
@export var speed := 0.9 ## vitesse de marche (m/s)
@export var flee_distance := 3.2 ## distance où il rentre se cacher
@export var peek_time := 3.5 ## temps immobile et éteint avant qu'il ressorte
@export var follow_distance := 1.3 ## en confiance : distance à laquelle il reste du robot
@export var snap_to_ground := true
@export_group("Parler")
@export var dialogues: Array[Dialogue] = []
@export var talk_height := 1.7 ## hauteur des mots au-dessus de lui
@export var chatter: PackedStringArray = [] ## répliques d'ambiance quand il n'a rien d'autre à dire

var _home_pos := Vector3.ZERO
var _seed := 0.0
var _hidden := 0.0 ## 0 = dehors, 1 = rentré chez lui
var _crouch := false
var _still := 0.0
var _peeking := false
var _goal := Vector3.ZERO
var _goal_timer := 0.0
var _routine_i := 0
var _ground_timer := 0.0
var _ground_y := 0.0
var _talking := false
var _moving := false
var _anim: AnimationPlayer
var _conv: LueurSpeech
var _talk_spot: Interactable
## Mise en scène : s'il est défini, il va là (et ne se cache pas), quoi qu'il arrive.
var scripted_target: Variant = null
var scripted_hide := false


func _ready() -> void:
	_apply_form()
	scale = Vector3.ONE * size
	if Engine.is_editor_hint():
		return
	_home_pos = global_position
	_goal = global_position
	_ground_y = global_position.y
	_seed = randf() * 100.0
	_goal_timer = randf() * 3.0
	if trust_flag != &"" and Loop.has_flag(trust_flag):
		shy = false
	_conv = LueurSpeech.new()
	_conv.name = "Conversation"
	_conv.auto = false
	_conv.height = talk_height
	add_child(_conv)
	_talk_spot = get_node_or_null("Parler") as Interactable
	if _talk_spot:
		_talk_spot.interacted.connect(talk)


## Pour LueurSpeech : il ne parle que s'il est dehors.
func can_speak() -> bool:
	return _hidden < 0.3 and not _crouch


func is_hidden() -> bool:
	return _hidden > 0.7 or _crouch


func _home() -> Vector3:
	return home.global_position if home else _home_pos


func _door() -> Vector3:
	if home == null:
		return _home_pos
	return home.global_transform * Vector3(0, 0, door_distance)


func _model() -> Node3D:
	return get_node_or_null("Forme") as Node3D


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if trust_flag != &"" and shy and Loop.has_flag(trust_flag):
		shy = false
	var target := _wander_target(delta)
	var hide := home is LueurHabitat and (home as LueurHabitat).collapsed
	var face_robot := false
	_crouch = false
	if scripted_target != null:
		target = scripted_target
		hide = scripted_hide
	elif _talking:
		target = global_position
		face_robot = true
	elif robot and not hide:
		var d := robot.global_position.distance_to(global_position)
		var lit: bool = not robot.night_mode
		var moving := (robot as CharacterBody3D).velocity.length() > 0.3
		if shy:
			if d < flee_distance and (lit or moving):
				hide = true
				_still = 0.0
				_peeking = false
			elif d < flee_distance:
				_still += delta
				_peeking = _still > peek_time
				hide = not _peeking
				if _peeking:
					target = _door().lerp(robot.global_position, 0.35)  # il ressort, prudemment
					face_robot = true
			else:
				_still = 0.0
				_peeking = false
		elif follows and d < 6.0 and not lit:
			var away := global_position - robot.global_position
			away.y = 0.0
			target = robot.global_position + away.normalized() * follow_distance
			face_robot = d < follow_distance + 0.6
	if hide:
		if home:
			target = _door()  # il court jusqu'à sa porte, puis il rentre
		else:
			_crouch = true    # pas de maison : il se recroqueville sur place
			target = global_position
	_walk(target, delta, 1.8 if hide else 1.0)
	var at_door := Vector2(global_position.x - _door().x, global_position.z - _door().z).length() < 0.35
	_hidden = move_toward(_hidden, 1.0 if (hide and home and at_door) else 0.0, delta * (2.5 if hide else 0.8))
	scale = Vector3.ONE * size * lerpf(1.0, 0.02, _hidden)
	if face_robot and robot:
		_turn_to(robot.global_position - global_position, delta)
	_animate()
	if _talk_spot:
		_talk_spot.enabled = _can_talk(robot)


# Vaquer : sa routine (puits, marché…), sinon des petits tours autour de chez lui.
func _wander_target(delta: float) -> Vector3:
	_goal_timer -= delta
	if _goal_timer <= 0.0:
		if not routine.is_empty():
			var spot := routine[_routine_i % routine.size()]
			_routine_i += 1
			_goal = spot.global_position + Vector3(randf_range(-0.6, 0.6), 0, randf_range(-0.6, 0.6)) if spot else _home()
			_goal_timer = randf_range(pause.x, pause.y) + 4.0
		else:
			var a := randf() * TAU
			var base := _door() if home else _home_pos
			_goal = base + Vector3(cos(a), 0, sin(a)) * randf_range(0.3, wander_radius)
			_goal_timer = randf_range(3.0, 7.0)
	return _goal


func _walk(target: Vector3, delta: float, hurry: float) -> void:
	var to := Vector3(target.x - global_position.x, 0.0, target.z - global_position.z)
	var dist := to.length()
	_moving = dist > 0.12
	if _moving:
		var step := minf(dist, speed * hurry * delta)
		global_position += to / dist * step
		_turn_to(to, delta)
	# les pieds sur le sol
	_ground_timer -= delta
	if snap_to_ground and _ground_timer <= 0.0:
		_ground_timer = 0.15
		_ground_y = _floor_at(global_position)
	global_position.y = lerpf(global_position.y, _ground_y, 1.0 - exp(-12.0 * delta))


func _floor_at(pos: Vector3) -> float:
	var q := PhysicsRayQueryParameters3D.create(pos + Vector3.UP * 0.9, pos + Vector3.DOWN * 4.0)
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	return hit.position.y if hit else pos.y


func _turn_to(dir: Vector3, delta: float) -> void:
	if Vector2(dir.x, dir.z).length() < 0.01:
		return
	rotation.y = lerp_angle(rotation.y, atan2(dir.x, dir.z), 1.0 - exp(-6.0 * delta))


func _animate() -> void:
	if _anim == null:
		var m := _model()
		_anim = m.get_node_or_null("Animation") as AnimationPlayer if m else null
		if _anim == null:
			return
	var want := &"idle"
	if _crouch or (_hidden > 0.3):
		want = &"cache"
	elif _speaking():
		want = &"parle"
	elif _moving:
		want = &"marche"
	if _anim.current_animation != want and _anim.has_animation(want):
		_anim.play(want, 0.25)


func _speaking() -> bool:
	for c in get_children():
		if c is LueurSpeech and c._speaking:
			return true
	return false


# ---------- parler (E) ----------
func _can_talk(robot: Node3D) -> bool:
	if robot == null or _talking or scripted_target != null or not can_speak():
		return false
	if robot.busy:
		return false  # une autre scène est en cours
	if not robot.night_mode and robot.battery.vision() < 0.3:
		return false  # antenne allumée : il ne te voit que comme une brûlure
	if shy and not _peeking:
		return false
	return _pick() != null


func _pick() -> Dialogue:
	for d in dialogues:
		if d and d.available():
			return d
	if not chatter.is_empty():
		var c := Dialogue.new()
		c.lines = PackedStringArray([chatter[randi() % chatter.size()]])
		return c
	return null


## Conversation : les répliques s'enchaînent en mots de lumière ; le robot écoute.
func talk(robot: Node3D) -> void:
	var d := _pick()
	if d == null or _talking or robot.busy:
		return
	_talking = true
	robot.busy = true
	robot.velocity = Vector3.ZERO
	await robot.face_toward(global_position, 0.5)
	robot.face.set_expression(&"curious", 0.4)
	var complete := true
	for i in d.lines.size():
		_conv.text = d.lines[i]
		_conv.id = d.paroles[i] if i < d.paroles.size() else &""
		_conv.height = talk_height
		if _conv.clarity() < 0.3:
			complete = false
			break
		if _conv.clarity() < 0.95:
			complete = false
		await _conv.say()
		await get_tree().create_timer(0.3).timeout
	if complete and d.id != &"":
		Loop.set_flag(StringName("dlg_" + d.id))
		if d.sets_flag != &"":
			Loop.set_flag(d.sets_flag)
	robot.face.set_expression(&"neutral", 0.6)
	robot.busy = false
	_talking = false


# Le modèle de la forme choisie est créé à la volée (ni sauvegardé dans la scène, ni chargé pour rien).
func _apply_form() -> void:
	if not is_inside_tree():
		return
	var old := get_node_or_null("Forme")
	if old:
		remove_child(old)
		old.free()
	var scene := load(FORM_SCENES[form]) as PackedScene
	if scene == null:
		return
	var m := scene.instantiate()
	m.name = "Forme"
	if m is LueurHabitat:
		m.snap_to_ground = false
		m.follow_wake = false
	add_child(m)
	move_child(m, 0)
	_anim = null
