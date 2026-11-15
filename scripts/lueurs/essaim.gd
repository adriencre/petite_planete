extends Node3D
## L'essaim de la Pouponnière (aide n°1 des peuples, voir MONDE_OMBRE.md 3 bis).
## Une fois les petites libérées, elles accompagnent le robot dans le noir (antenne éteinte),
## sur toutes les îles : une petite nuée qui brille juste assez pour voir le relief et lire.
## Antenne allumée, elles s'écartent et s'éteignent.

const HALO := preload("res://assets/lueurs/materials/lueur_halo.tres")

@export var flag_id := &"pouponniere_libre"
@export var light_energy := 0.8
@export var light_range := 3.6

var _amount := 0.0
var _particles: CPUParticles3D
var _light: OmniLight3D


func _ready() -> void:
	_particles = CPUParticles3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(0.14, 0.14)
	quad.material = HALO
	_particles.mesh = quad
	_particles.amount = 26
	_particles.lifetime = 2.6
	_particles.local_coords = false
	_particles.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	_particles.emission_sphere_radius = 0.55
	_particles.gravity = Vector3.ZERO
	_particles.initial_velocity_min = 0.05
	_particles.initial_velocity_max = 0.2
	_particles.spread = 180.0
	_particles.scale_amount_min = 0.5
	_particles.scale_amount_max = 1.3
	_particles.emitting = false
	add_child(_particles)
	_light = OmniLight3D.new()
	_light.light_color = Color(0.55, 1.0, 0.88)
	_light.omni_range = light_range
	_light.light_energy = 0.0
	_light.shadow_enabled = false
	add_child(_light)


func _process(delta: float) -> void:
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	var on: bool = robot != null and Loop.has_flag(flag_id) and robot.night_mode
	_amount = move_toward(_amount, 1.0 if on else 0.0, delta * (0.6 if on else 1.5))
	_particles.emitting = _amount > 0.2
	_light.light_energy = _amount * light_energy
	_light.visible = _amount > 0.01
	if robot:
		# elle flotte un peu au-dessus et derrière le robot, en traînant doucement
		var behind: Vector3 = -robot.model.global_transform.basis.z * 0.5
		var goal: Vector3 = robot.global_position + Vector3.UP * 1.6 + behind
		global_position = global_position.lerp(goal, 1.0 - exp(-2.5 * delta))
