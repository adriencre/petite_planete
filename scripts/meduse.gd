@tool
extends Node3D
## Créature de la brume (méduse du ciel) : flotte, pulse, dérive en rond.
## Invisible le jour : `apparition` (0..1) est piloté par la scène (mode N, batterie basse).

const SHADER := preload("res://shaders/creature.gdshader")

@export var taille: float = 1.0:
	set(v): taille = v; _construire()
@export var rayon_derive: float = 1.5
@export var vitesse_derive: float = 0.12
@export_range(0.0, 1.0) var apparition: float = 0.0:
	set(v):
		apparition = v
		if _mat:
			_mat.set_shader_parameter("apparition", v)
		visible = v > 0.01 or Engine.is_editor_hint()

var _mat: ShaderMaterial
var _centre: Vector3
var _t := 0.0
var _tentacules: Array[MeshInstance3D] = []
var _dome: MeshInstance3D


func _ready() -> void:
	_centre = position
	_t = randf() * 10.0
	_construire()
	apparition = apparition


func _construire() -> void:
	if not is_inside_tree():
		return
	for c in get_children():
		c.queue_free()
	_tentacules.clear()
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter("apparition", 1.0 if Engine.is_editor_hint() else apparition)
	var dome := SphereMesh.new()
	dome.radius = 0.6 * taille
	dome.height = 0.55 * taille
	dome.is_hemisphere = true
	_dome = MeshInstance3D.new()
	_dome.mesh = dome
	_dome.material_override = _mat
	add_child(_dome)
	for i in 7:
		var a := TAU * i / 7.0
		var tube := CylinderMesh.new()
		tube.top_radius = 0.025 * taille
		tube.bottom_radius = 0.005 * taille
		tube.height = randf_range(1.2, 2.2) * taille
		var m := MeshInstance3D.new()
		m.mesh = tube
		m.material_override = _mat
		m.position = Vector3(cos(a) * 0.35 * taille, -tube.height * 0.5, sin(a) * 0.35 * taille)
		add_child(m)
		_tentacules.append(m)


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_t += delta
	var pulse := 1.0 + 0.12 * sin(_t * 1.8)
	if _dome:
		_dome.scale = Vector3(pulse, 2.0 - pulse, pulse)
	position = _centre + Vector3(cos(_t * vitesse_derive) * rayon_derive, sin(_t * 0.7) * 0.3, sin(_t * vitesse_derive) * rayon_derive)
	for i in _tentacules.size():
		_tentacules[i].rotation.x = sin(_t * 1.3 + i) * 0.15
		_tentacules[i].rotation.z = cos(_t * 1.1 + i * 0.7) * 0.15
