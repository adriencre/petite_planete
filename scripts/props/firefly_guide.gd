class_name FireflyGuide
extends Node3D
## Petite luciole, dernier reste d'énergie de l'île. Elle sort de la brume après la sortie de l'abri
## et flotte doucement vers le prochain endroit important, sans jamais presser :
## elle attend le robot quand il traîne. À la première lumière, elle se fond dans la lanterne.
## Ensuite elle ne revient qu'en indice, si le joueur n'avance plus pendant un moment.

@export var targets: Array[Node3D] = [] ## objectifs dans l'ordre (chacun avec is_done())
@export var lead_until := 2 ## guide activement les N premiers objectifs, puis seulement en indice
@export var hint_after := 45.0 ## secondes sans progrès avant de revenir en indice
@export var speed := 1.6

enum Mode { HIDDEN, LEADING, HINT }
var mode := Mode.HIDDEN
var _done_count := 0
var _idle := 0.0
var _time := 0.0

@onready var _light: OmniLight3D = $Light


func _ready() -> void:
	visible = false


## Apparition (après le recul de caméra à la sortie de l'abri).
func appear(near: Vector3) -> void:
	global_position = near + Vector3(2.5, 1.6, 2.5)
	visible = true
	scale = Vector3.ONE * 0.01
	create_tween().tween_property(self, "scale", Vector3.ONE, 1.2).set_trans(Tween.TRANS_SINE)
	mode = Mode.LEADING


func _process(delta: float) -> void:
	_time += delta
	var target := _current_target()
	var done_now := _count_done()
	if done_now != _done_count:
		_done_count = done_now
		_idle = 0.0
		if mode == Mode.LEADING and _done_count >= lead_until:
			_merge_into(targets[lead_until - 1])
			return
		if mode == Mode.HINT:
			_vanish()
	if mode == Mode.HIDDEN:
		if _done_count >= lead_until and target:
			var player := get_tree().get_first_node_in_group(&"player")
			_idle += 0.0 if (player and player.busy) else delta
			if _idle > hint_after:
				_idle = 0.0
				appear(player.global_position if player else global_position)
				mode = Mode.HINT
		return
	if target == null:
		_vanish()
		return
	_move_toward_goal(target, delta)


func _current_target() -> Node3D:
	for t in targets:
		if is_instance_valid(t) and not t.is_done():
			return t
	return null


func _count_done() -> int:
	var n := 0
	for t in targets:
		if is_instance_valid(t) and t.is_done():
			n += 1
	return n


func _move_toward_goal(target: Node3D, delta: float) -> void:
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	var goal := target.global_position + Vector3(0, 1.7, 0)
	if player:
		var to_target := goal - player.global_position
		var dist := Vector2(to_target.x, to_target.z).length()
		if dist > 4.0:
			# quelques mètres devant le robot, sur le chemin de l'objectif
			var dir := Vector3(to_target.x, 0, to_target.z).normalized()
			goal = player.global_position + dir * 2.6 + Vector3(0, 1.5, 0)
	var wander := Vector3(sin(_time * 1.3), sin(_time * 2.1) * 0.6, cos(_time * 1.1)) * 0.35
	global_position = global_position.lerp(goal + wander, 1.0 - exp(-speed * delta))
	_light.light_energy = 0.9 + sin(_time * 4.0) * 0.25


# Se fond dans la lanterne qu'on vient de rallumer.
func _merge_into(lantern: Node3D) -> void:
	mode = Mode.HIDDEN
	var t := create_tween()
	t.tween_property(self, "global_position", lantern.global_position + Vector3(0, 0.9, 0), 1.2).set_trans(Tween.TRANS_SINE)
	t.tween_property(self, "scale", Vector3.ONE * 0.01, 0.4)
	t.tween_callback(set.bind("visible", false))


func _vanish() -> void:
	mode = Mode.HIDDEN
	var t := create_tween()
	t.tween_property(self, "scale", Vector3.ONE * 0.01, 0.8)
	t.tween_callback(set.bind("visible", false))
