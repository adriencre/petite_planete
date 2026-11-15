@tool
class_name WakeZone
extends Node3D
## Une zone de l'île qui peut se réveiller : la couleur se répand en cercle depuis ce point.
## Dans l'éditeur, le cercle montre la taille de la zone.

signal woke_up

@export var radius := 6.0:
	set(value):
		radius = maxf(value, 0.1)
		_update_gizmo()
@export var grow_time := 2.5 ## durée de la vague, en secondes
@export var start_awake := false

var current_radius := 0.0
var is_awake := false

var _gizmo: MeshInstance3D
var _tween: Tween


func _enter_tree() -> void:
	add_to_group(&"wake_zone")


func _ready() -> void:
	if start_awake:
		is_awake = true
		current_radius = radius
	if Engine.is_editor_hint():
		_update_gizmo()


func wake() -> void:
	if is_awake:
		return
	is_awake = true
	if radius > 3.0 and radius < 40.0:
		Audio.play("wake_wave", null, -10.0, randf_range(0.9, 1.05))
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "current_radius", radius, grow_time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_tween.tween_callback(woke_up.emit)


## L'île est-elle réveillée à cet endroit ? (0 = endormie, 1 = éveillée)
static func awake_at(tree: SceneTree, pos: Vector3) -> float:
	var best := 0.0
	for zone in tree.get_nodes_in_group(&"wake_zone"):
		var d := Vector2(pos.x - zone.global_position.x, pos.z - zone.global_position.z).length()
		var r: float = zone.current_radius
		if r > 0.01:
			best = maxf(best, clampf((r - d) / 2.5 + 0.5, 0.0, 1.0))
	return best


## La zone se rendort doucement (la couleur reflue vers son centre).
func fall_asleep(duration := 3.0) -> void:
	if not is_awake and current_radius <= 0.01:
		return
	is_awake = false
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "current_radius", 0.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func sleep() -> void:
	if _tween:
		_tween.kill()
	is_awake = false
	current_radius = 0.0


# ---------- cercle visible dans l'éditeur ----------
func _update_gizmo() -> void:
	if not Engine.is_editor_hint() or not is_inside_tree():
		return
	if _gizmo == null:
		_gizmo = MeshInstance3D.new()
		add_child(_gizmo, false, Node.INTERNAL_MODE_FRONT)
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color(1.0, 0.85, 0.5)
		mat.no_depth_test = true
		_gizmo.material_override = mat
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for i in 65:
		var a := TAU * i / 64.0
		mesh.surface_add_vertex(Vector3(cos(a) * radius, 0.05, sin(a) * radius))
	mesh.surface_end()
	_gizmo.mesh = mesh
