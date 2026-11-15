class_name RobotBattery
extends Node
## Batterie du robot (enfant du nœud Robot).
## - La brume la vide (plus elle est épaisse, plus vite) ; à l'intérieur ou dans une zone éveillée, rien ne se perd.
## - Près d'une lanterne allumée ou dans le rayon d'une pierre-soleil, elle se recharge.
## - Allumer une lanterne coûte de l'énergie (spend()).
## - Elle se lit sur la jauge à 5 crans au dos de la tête du robot, et à l'éclat de son antenne. Aucun texte.

signal changed(level: float)
signal depleted

@export var capacity := 100.0
@export var start_level := 18.0 ## au réveil (pas assez pour allumer une lanterne)
@export var fog_drain := 0.8 ## par seconde, en pleine brume
@export var low_threshold := 25.0 ## en dessous : l'antenne clignote, l'écran s'assombrit sur les bords
@export var vision_start := 12.0 ## en dessous : les Lueurs commencent à apparaître dans la brume
@export var vision_full := 3.0 ## en dessous : on les voit pleinement

var level := 0.0
## Mode nuit : l'antenne est éteinte. La brume ne vide plus rien (elle se nourrit de lumière),
## la lumière ne recharge plus rien, et les Lueurs sont pleinement visibles.
var night := false
## Passage progressif vers la vision de nuit (0 → 1), réglé par le robot.
var night_amount := 0.0
var _empty := false
var _cells: Array[ShaderMaterial] = []
var _blink := 0.0

@onready var robot: CharacterBody3D = get_parent()
@onready var _vignette: ColorRect = $Vignette/Rect


func _exit_tree() -> void:
	RenderingServer.global_shader_parameter_set(&"lueur_vision", 0.0)
	OmbreObjet.vision = 0.0


func _ready() -> void:
	level = start_level
	var gauge := robot.get_node("Model/Rig/LookPivot/Head/Gauge")
	for cell in gauge.get_children():
		if not String(cell.name).begins_with("Cell"):
			continue
		var mat := ((cell as MeshInstance3D).get_surface_override_material(0) as ShaderMaterial).duplicate()
		(cell as MeshInstance3D).set_surface_override_material(0, mat)
		_cells.append(mat)
	_refresh(0.0)


## Fraction de 0 à 1.
func fraction() -> float:
	return level / capacity


func can_spend(amount: float) -> bool:
	return level >= amount


## Dépense de l'énergie, progressivement sur `duration` secondes (pour voir la jauge descendre).
func spend(amount: float, duration := 1.2) -> void:
	var target := maxf(level - amount, 0.0)
	var t := create_tween()
	t.tween_method(_set_level, level, target, duration)


## Ajoute de l'énergie progressivement (lumière reprise à une lanterne).
func gain(amount: float, duration := 1.5) -> void:
	_empty = false
	var t := create_tween()
	t.tween_method(_set_level, level, minf(level + amount, capacity), duration).set_trans(Tween.TRANS_SINE)


## Remplit la batterie (pierre-soleil).
func fill(duration := 2.0) -> void:
	_empty = false
	var t := create_tween()
	t.tween_method(_set_level, level, capacity, duration).set_trans(Tween.TRANS_SINE)


func reset(to := -1.0) -> void:
	_empty = false
	_set_level(start_level if to < 0.0 else to)


func _physics_process(delta: float) -> void:
	if _empty:
		return
	if night:
		_refresh(delta)  # dans le noir, plus rien ne bouge
		return
	var rate := 0.0
	# recharge auprès des sources de lumière
	for point in get_tree().get_nodes_in_group(&"energy_point"):
		if point.has_method("recharge_rate"):
			rate += point.recharge_rate(robot.global_position)
	# la brume vide (sauf pendant les scènes, à l'intérieur, ou dans une zone éveillée)
	if rate <= 0.0 and not robot.busy and InteriorZone.inside_amount() < 0.5:
		var awake := WakeZone.awake_at(get_tree(), robot.global_position)
		var thick := FogDensityZone.current(get_tree())
		var mult := thick.drain_multiplier if thick else 1.0
		rate -= fog_drain * mult * (1.0 - awake)
	if rate != 0.0:
		_set_level(clampf(level + rate * delta, 0.0, capacity))
	_refresh(delta)


func _set_level(value: float) -> void:
	level = value
	changed.emit(level)
	if level <= 0.0 and not _empty:
		_empty = true
		depleted.emit()


# Jauge (5 crans), lueur de l'antenne, assombrissement de l'écran quand il en reste peu.
func _refresh(delta: float) -> void:
	var f := fraction()
	for i in _cells.size():
		var cell_fill := clampf(f * _cells.size() - i, 0.0, 1.0)
		var on := Color(1.0, 0.81, 0.54) if f > low_threshold / capacity else Color(1.0, 0.55, 0.42)
		_cells[i].set_shader_parameter("albedo", Color(0.25, 0.27, 0.32).lerp(on, cell_fill))
		_cells[i].set_shader_parameter("emission_strength", cell_fill * 1.6)
	var low := clampf(1.0 - level / low_threshold, 0.0, 1.0) * (1.0 - night_amount)
	_blink += delta * (2.0 + low * 4.0)
	var pulse := 0.75 + 0.25 * sin(_blink)
	(_vignette.material as ShaderMaterial).set_shader_parameter("strength", low * pulse * (1.0 - 0.6 * vision()))
	RenderingServer.global_shader_parameter_set(&"lueur_vision", vision())
	OmbreObjet.vision = vision()  # le monde de l'ombre apparaît dans le noir


## Les Lueurs sont-elles visibles ? (0 à 1, monte quand la batterie est presque vide)
func vision() -> float:
	var v := clampf((vision_start - level) / (vision_start - vision_full), 0.0, 1.0)
	v = maxf(v, night_amount)
	var thick := FogDensityZone.current(get_tree()) if is_inside_tree() else null
	if thick:
		v = maxf(v, thick.vision * (1.0 - WakeZone.awake_at(get_tree(), robot.global_position)))
	return v


## Lueur de base de l'antenne (0 = éteinte), qui clignote quand la batterie est faible.
func antenna_glow() -> float:
	if night:
		return 0.0
	var f := fraction()
	if level < low_threshold:
		return f * (0.6 + 0.4 * sin(_blink * 1.5))
	return 0.25 + f * 0.75
