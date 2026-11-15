extends Node3D
## Le Compteur : une vieille Lueur en forme de héron, sur la crique, près de l'ancien corps.
## À ses pieds, un tas de petites pierres lumineuses : une par corps du robot tombé.
## Les vieilles pierres (avant le premier réveil) sont pâles ; celles des morts du joueur brillent davantage.
## 1re moitié : après chaque mort, il pose une pierre de plus et dit seulement « Encore un. »
## 2e moitié (après la bascule) : il dit enfin la vérité (« Tu es revenu deux cent quatorze fois… »),
## puis, quand la Pouponnière est libre, il donne au robot la toute première pierre.
## (Visible seulement dans le noir.)

const PEBBLE_MAT := preload("res://assets/lueurs/materials/lueur_plein.tres")
const NEW_MAT := preload("res://assets/lueurs/materials/lueur_tisse.tres")
const BEFORE := 213 ## corps tombés avant le premier réveil du joueur

@export var old_pebbles := 46 ## pierres visibles pour les corps d'avant (le tas n'en montre qu'une partie)
@export var max_new := 40
@export var notice_distance := 5.0
@export var snap_to_ground := true

var _snapped := false
var _new_shown := 0
var _pending: MeshInstance3D
var _busy := false

@onready var _pile: Node3D = $Tas
@onready var _heron: Node3D = $Heron
@onready var _encore: LueurSpeech = $Heron/Parole
@onready var _truth: LueurSpeech = $Heron/Verite
@onready var _gift_words: LueurSpeech = $Heron/Cadeau


func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 214
	for i in old_pebbles:
		_add_pebble(_cairn_pos(i, rng), PEBBLE_MAT, 1.0)
	var seen: int = Loop.flags.get(&"compteur_vu", 0)
	_new_shown = mini(seen, max_new)
	for i in _new_shown:
		_add_pebble(_cairn_pos(old_pebbles + i, rng), NEW_MAT, 1.15)
	if Loop.count > seen and _new_shown < max_new:
		# une nouvelle mort : la pierre attend dans le bec du héron
		_pending = _add_pebble(Vector3.ZERO, NEW_MAT, 1.15)
		_pending.reparent(_heron.find_child("Tete_Compteur", true, false), false)
		_pending.position = Vector3(0, -0.02, 0.12)
	# la vérité : le nombre suit les vraies morts du joueur
	_truth.text = "Tu es revenu %s fois, Petit-Jour. Tu tombes toujours au même endroit, près de l'eau. Tu regardais la mer." % number_words(BEFORE + 1 + Loop.count)
	if Loop.has_flag(&"premiere_pierre"):
		_attach_first_pebble.call_deferred()


func _physics_process(_delta: float) -> void:
	if not _snapped:
		_snapped = true
		if snap_to_ground:
			var dy := LueurHabitat.ground_y(self, global_position) - global_position.y
			global_position.y += dy
			_heron._home_pos.y += dy  # le héron se repère sur sa place de départ
	if _busy:
		return
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if robot == null or robot.busy or robot.global_position.distance_to(global_position) > notice_distance:
		return
	var vision: float = robot.battery.vision()
	if vision < 0.3:
		return
	if _pending:
		_place_pending()
	elif Loop.has_flag(&"bascule") and vision >= 0.95 and not Notebook.has_parole(_truth.id):
		_reveal(robot)
	elif Loop.has_flag(&"pouponniere_libre") and vision >= 0.95 and not Loop.has_flag(&"premiere_pierre") \
			and Notebook.has_parole(_truth.id):
		_give_first_pebble(robot)


# 1re moitié : le héron baisse le bec et pose la pierre sur le tas.
func _place_pending() -> void:
	_busy = true
	var pebble := _pending
	_pending = null
	Loop.flags[&"compteur_vu"] = Loop.count
	var rng := RandomNumberGenerator.new()
	rng.seed = 214 + Loop.count
	var dest := _pile.global_transform * _cairn_pos(old_pebbles + _new_shown, rng)
	_new_shown += 1
	pebble.reparent(_pile, true)
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_interval(1.2)
	t.tween_property(pebble, "global_position", dest + Vector3.UP * 0.25, 1.2)
	t.tween_property(pebble, "global_position", dest, 0.5).set_ease(Tween.EASE_IN)
	await t.finished
	await _encore.say()
	_busy = false


# 2e moitié : la vérité, lentement. Le robot s'arrête, la caméra se rapproche.
func _reveal(robot: Node3D) -> void:
	_busy = true
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"compteur", 5.0, 22.0, 0.5, _heron)
	await robot.face_toward(_heron.global_position, 0.8)
	robot.face.set_expression(&"curious", 0.6)
	await get_tree().create_timer(1.5).timeout
	_truth.word_time = 0.42
	await _truth.say()
	robot.face.set_expression(&"sad", 1.5)
	# il regarde le tas de pierres, puis la mer
	robot.glance_at(_pile.global_position, 2.5)
	await get_tree().create_timer(3.0).timeout
	if cam:
		cam.pop_override(&"compteur")
	robot.face.set_expression(&"neutral", 1.0)
	robot.busy = false
	_busy = false


# 2e moitié, Pouponnière libre : il donne la toute première pierre (elle tournera autour du robot).
func _give_first_pebble(robot: Node3D) -> void:
	_busy = true
	Loop.set_flag(&"premiere_pierre")
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"compteur", 5.0, 24.0, 0.6, _heron)
	await robot.face_toward(_heron.global_position, 0.6)
	var first := _pile.get_child(0) as Node3D
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(first, "global_position", robot.global_position + Vector3(0, 1.4, 0), 1.8)
	await t.finished
	first.queue_free()
	_attach_first_pebble()
	robot.face.set_expression(&"surprised", 0.4)
	await _gift_words.say()
	robot.emote(&"happy", &"happy", 1.5)
	await get_tree().create_timer(1.5).timeout
	if cam:
		cam.pop_override(&"compteur")
	robot.busy = false
	_busy = false


func _attach_first_pebble() -> void:
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if robot == null or robot.has_node("PremierePierre"):
		return
	var pivot := Node3D.new()
	pivot.name = "PremierePierre"
	robot.add_child(pivot)
	pivot.position = Vector3(0, 1.25, 0)
	var p := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.05
	mesh.height = 0.07
	mesh.radial_segments = 6
	mesh.rings = 3
	mesh.material = NEW_MAT
	p.mesh = mesh
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	pivot.add_child(p)
	p.position = Vector3(0.45, 0, 0)
	var spin := pivot.create_tween().set_loops()
	spin.tween_property(pivot, "rotation:y", TAU, 5.0).from(0.0)


# Un petit cairn : des couches de plus en plus étroites.
func _cairn_pos(i: int, rng: RandomNumberGenerator) -> Vector3:
	var layer := 0
	var left := i
	var per := 14
	while left >= per and per > 1:
		left -= per
		layer += 1
		per = maxi(per - 4, 1)
	var a := TAU * left / maxf(per, 1.0) + layer * 0.7 + rng.randf_range(-0.15, 0.15)
	var r := maxf(0.34 - layer * 0.09, 0.0) * rng.randf_range(0.85, 1.05)
	return Vector3(cos(a) * r, 0.03 + layer * 0.06, sin(a) * r)


func _add_pebble(pos: Vector3, mat: Material, k: float) -> MeshInstance3D:
	var p := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.045 * k
	mesh.height = 0.06 * k
	mesh.radial_segments = 6
	mesh.rings = 3
	mesh.material = mat
	p.mesh = mesh
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_pile.add_child(p)
	p.position = pos
	return p


## Un nombre en toutes lettres, en français (0 à 999).
static func number_words(n: int) -> String:
	var units := ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
		"onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
	var tens := ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante", "quatre-vingt", "quatre-vingt"]
	if n < 20:
		return units[n]
	if n < 100:
		var t := n / 10
		var u := n % 10
		if t == 7 or t == 9:
			u += 10
		var word: String = tens[t]
		if u == 0:
			return word + ("s" if t == 8 else "")
		if (u == 1 or u == 11) and t != 8 and t != 9:
			return word + " et " + units[u]
		return word + "-" + units[u]
	var h := n / 100
	var rest := n % 100
	var head: String = "cent" if h == 1 else units[h] + " cent"
	if rest == 0:
		return head + ("s" if h > 1 else "")
	return head + " " + number_words(rest)
