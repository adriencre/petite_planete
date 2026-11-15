@tool
extends Node3D
## Créature des Lueurs : une petite méduse de lumière qui dérive lentement dans la brume,
## autour de son point de départ. Invisible sauf quand l'antenne du robot faiblit.
## La première fois que le robot en voit une de près dans le noir, il s'arrête, la regarde
## et la croque dans le bestiaire de son carnet.
## Dans l'éditeur, un cercle montre la zone où elle se promène.

@export var wander_radius := 2.5
@export var hover_height := 1.2
@export var speed := 0.35
@export var entry: CreatureEntry ## sa page du bestiaire
@export var sketch_distance := 3.5 ## à quelle distance le robot la remarque

var _check := 0.0

var _home := Vector3.ZERO
var _time := 0.0
var _seed := 0.0

@onready var _tentacles: Node3D = $Tentacles


func _ready() -> void:
	_home = position
	_seed = randf() * 100.0
	if Engine.is_editor_hint():
		_draw_gizmo()


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_time += delta * speed
	var t := _time + _seed
	position = _home + Vector3(sin(t * 0.7) * cos(t * 0.31), 0.0, sin(t * 0.53)) * wander_radius \
		+ Vector3.UP * (hover_height + sin(t * 2.3) * 0.15)
	for i in _tentacles.get_child_count():
		var tent: Node3D = _tentacles.get_child(i)
		tent.rotation.x = sin(t * 4.0 + i * 1.3) * 0.35
		tent.rotation.z = cos(t * 3.1 + i) * 0.25
	_check -= delta
	if _check <= 0.0:
		_check = 0.25
		_look_for_robot()


func _look_for_robot() -> void:
	if entry == null or Notebook.has_creature(entry.id):
		return
	var robot := get_tree().get_first_node_in_group(&"player")
	if robot == null or robot.busy or Notebook.is_open:
		return
	if robot.global_position.distance_to(global_position) > sketch_distance:
		return
	# visible seulement dans la brume, quand l'antenne faiblit (ou dans la brume épaisse)
	if robot.battery.vision() < 0.45 or WakeZone.awake_at(get_tree(), global_position) > 0.5:
		return
	_first_sighting(robot)


# Le robot s'arrête, la suit des yeux, puis la croque. (La batterie ne se vide pas pendant ce temps.)
func _first_sighting(robot: Node3D) -> void:
	Notebook.add_creature(entry)  # réservée tout de suite : une seule scène, même si d'autres sont proches
	robot.busy = true
	robot.velocity = Vector3.ZERO
	var cam := get_viewport().get_camera_3d()
	if cam:
		cam.push_override(&"creature", 5.0, 26.0, 0.7, self)
	robot.face.set_expression(&"surprised", 0.3)
	await robot.face_toward(global_position, 0.6)
	await get_tree().create_timer(1.6).timeout
	robot.face.set_expression(&"curious", 0.6)
	robot.glance_at(global_position, 2.5)
	await get_tree().create_timer(2.2).timeout
	Notebook.show_sketch_toast(entry.sketch)
	await get_tree().create_timer(1.4).timeout
	if cam:
		cam.pop_override(&"creature")
	robot.face.set_expression(&"neutral", 0.8)
	robot.busy = false


func _draw_gizmo() -> void:
	var gizmo := MeshInstance3D.new()
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for i in 49:
		var a := TAU * i / 48.0
		mesh.surface_add_vertex(Vector3(cos(a) * wander_radius, 0.05, sin(a) * wander_radius))
	mesh.surface_end()
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(0.4, 1.0, 0.85)
	gizmo.material_override = mat
	gizmo.mesh = mesh
	add_child(gizmo, false, Node.INTERNAL_MODE_FRONT)
