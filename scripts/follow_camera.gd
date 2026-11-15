@tool
extends Camera3D
## Caméra vue de haut, façon maquette, qui suit la cible en douceur.
## Les CameraZone de la scène peuvent changer sa distance et son inclinaison.
## Les séquences (réveil, première lumière…) peuvent poser un plan temporaire avec push_override().

@export var target: Node3D
@export_range(0, 360) var yaw_degrees := 45.0
@export_range(10, 89) var pitch_degrees := 42.0
@export var distance := 14.0
@export var look_height := 0.6
@export var smoothing := 2.5
@export var zone_blend := 1.2 ## vitesse de transition entre zones de caméra

var _distance := 0.0
var _pitch := 0.0
var _focus := Vector3.ZERO
var _overrides: Array[Dictionary] = []


func _ready() -> void:
	_distance = distance
	_pitch = pitch_degrees
	_snap()


## Plan temporaire (le dernier posé gagne) : distance, inclinaison, vitesse de transition,
## et éventuellement un point à regarder (Node3D ou Vector3) au lieu du robot.
func push_override(id: StringName, dist: float, pitch: float, blend := 1.0, look_at_target: Variant = null) -> void:
	pop_override(id)
	_overrides.append({"id": id, "distance": dist, "pitch": pitch, "blend": blend, "focus": look_at_target})


func pop_override(id: StringName) -> void:
	for i in range(_overrides.size() - 1, -1, -1):
		if _overrides[i]["id"] == id:
			_overrides.remove_at(i)


## Place la caméra immédiatement à sa position voulue (sans transition).
func snap_now() -> void:
	if _overrides.size() > 0:
		_distance = _overrides[-1]["distance"]
		_pitch = _overrides[-1]["pitch"]
	_focus = _wanted_focus()
	look_at_from_position(_focus + _offset(), _focus)


func _process(delta: float) -> void:
	if not target:
		return
	if Engine.is_editor_hint():
		_distance = distance
		_pitch = pitch_degrees
		_snap()
		return
	var want_distance := distance
	var want_pitch := pitch_degrees
	var best_priority := -INF
	for zone in get_tree().get_nodes_in_group(&"camera_zone"):
		if zone.has_player and zone.zone_priority > best_priority:
			best_priority = zone.zone_priority
			want_distance = zone.distance
			want_pitch = zone.pitch_degrees
	var blend := zone_blend
	if _overrides.size() > 0:
		want_distance = _overrides[-1]["distance"]
		want_pitch = _overrides[-1]["pitch"]
		blend = _overrides[-1]["blend"]
	var k := 1.0 - exp(-blend * delta)
	_distance = lerpf(_distance, want_distance, k)
	_pitch = lerpf(_pitch, want_pitch, k)

	_focus = _focus.lerp(_wanted_focus(), 1.0 - exp(-smoothing * delta))
	look_at_from_position(_focus + _offset(), _focus)
	_update_focus_blur()


func _wanted_focus() -> Vector3:
	if _overrides.size() > 0:
		var f: Variant = _overrides[-1]["focus"]
		if f is Node3D and is_instance_valid(f):
			return (f as Node3D).global_position
		if f is Vector3:
			return f
	return target.global_position + Vector3.UP * look_height


func _offset() -> Vector3:
	var yaw := deg_to_rad(yaw_degrees)
	var pitch := deg_to_rad(_pitch)
	return Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * _distance


func _snap() -> void:
	if target and is_inside_tree():
		_focus = target.global_position + Vector3.UP * look_height
		look_at_from_position(_focus + _offset(), _focus)
		_update_focus_blur()


# Le flou « maquette » reste net autour du robot quelle que soit la distance.
func _update_focus_blur() -> void:
	var attr := attributes as CameraAttributesPractical
	if attr:
		attr.dof_blur_near_distance = maxf(_distance - 4.0, 0.5)
		attr.dof_blur_far_distance = _distance + 5.0
