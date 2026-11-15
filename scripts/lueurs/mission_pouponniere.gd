extends Node
## Mission de la 2e moitié, île 1 : « Laisser sortir les petits ».
## La veilleuse de la porte de l'abri brûle le seuil : la Pouponnière ne peut pas sortir.
## Après la bascule, on peut reprendre sa lumière. Ensuite, si le robot reste ÉTEINT, les petites
## le suivent ; s'il rallume, elles s'éparpillent et rentrent. Quand assez d'entre elles arrivent
## au hameau des pins, c'est un moment : elles s'installent, le hameau s'étend, l'essaim est né.

@export var pouponniere: Node3D
@export var door_lantern: WakeLantern
@export var hamlet: LueurHamlet
@export var new_homes: Array[Node3D] = [] ## où les petites s'installent (maisons de l'extension)
@export var arrive_radius := 3.0
@export var needed := 3 ## combien de petites doivent arriver

var _done := false
var _playing := false


func _ready() -> void:
	_setup.call_deferred()


func _setup() -> void:
	_done = Loop.has_flag(&"pouponniere_libre")
	if door_lantern:
		door_lantern.allow_take_back(Loop.has_flag(&"bascule"))
	if _done:
		# la veilleuse a été reprise pour de bon : le seuil reste libre d'une boucle à l'autre
		if door_lantern:
			door_lantern.put_out_silently()
		_settle(false)


func _petites() -> Array[LueurDweller]:
	var out: Array[LueurDweller] = []
	if pouponniere:
		for c in pouponniere.get_children():
			if c is LueurDweller:
				out.append(c)
	return out


func _process(_delta: float) -> void:
	if _done or _playing or not Loop.has_flag(&"bascule"):
		return
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if robot == null:
		return
	var free_to_go := door_lantern == null or not door_lantern.is_lit
	var i := 0
	for p in _petites():
		# seuil brûlé : elles restent cachées ; seuil libre et robot éteint : elles le suivent
		p.shy = not free_to_go
		p.follows = free_to_go
		p.follow_distance = 0.8 + i * 0.3
		p.flee_distance = 1.2
		i += 1
	if not free_to_go:
		return
	var arrived := 0
	for p in _petites():
		if p.global_position.distance_to(hamlet.global_position) < arrive_radius:
			arrived += 1
	# une autre scène en cours (ex. la première bribe du hameau) : on attend qu'elle finisse
	if arrived >= needed and not robot.busy:
		_success(robot)


func _success(robot: Node3D) -> void:
	_playing = true
	_done = true
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"pouponniere", 9.0, 30.0, 0.5, hamlet)
	# elles tournent un moment au-dessus du hameau, de joie…
	var petites := _petites()
	for k in petites.size():
		var a := TAU * k / petites.size()
		petites[k].scripted_hide = false
		petites[k].scripted_target = hamlet.global_position + Vector3(cos(a), 0.8, sin(a)) * 1.2
	robot.face.set_expression(&"surprised", 0.4)
	await get_tree().create_timer(2.5).timeout
	Loop.set_flag(&"pouponniere_libre")
	# …le hameau s'étend dans l'ancien désert gris, et elles s'y installent
	hamlet.grow_extension()
	_settle(true)
	await get_tree().create_timer(1.5).timeout
	var enfant := hamlet.first_dweller
	enfant.shy = false
	enfant.scripted_hide = false
	enfant.scripted_target = robot.global_position.lerp(enfant.global_position, 0.6) + Vector3.UP * 0.4
	for i in 30:
		if enfant.can_speak():
			break
		await get_tree().create_timer(0.1).timeout
	var merci := enfant.get_node_or_null("Merci") as LueurSpeech
	if merci:
		await merci.say()
	enfant.scripted_target = null
	robot.emote(&"happy", &"happy", 2.0)
	await get_tree().create_timer(2.0).timeout
	if cam:
		cam.pop_override(&"pouponniere")
	robot.busy = false
	_playing = false


# Les petites quittent l'abri pour de bon : chacune rejoint une maison neuve du hameau.
func _settle(animated: bool) -> void:
	var petites := _petites()
	for k in petites.size():
		var p := petites[k]
		p.scripted_target = null
		p.scripted_hide = false
		p.shy = false
		p.follows = false
		p.home = new_homes[k % new_homes.size()] if not new_homes.is_empty() else hamlet
		p.wander_radius = 0.7
		if not animated:
			p.global_position = p.home.global_position + Vector3.UP * 0.3
	# tout le hameau a désormais confiance
	for c in hamlet.get_children():
		if c is LueurDweller:
			c.shy = false
			c.follows = false
