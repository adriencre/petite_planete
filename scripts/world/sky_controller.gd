class_name SkyController
extends Node
## Fait passer la lumière de l'île d'une ambiance à une autre (ex. vers le coucher de soleil).
## Les couleurs du coucher se règlent ici dans l'Inspecteur.

@export var sun: DirectionalLight3D
@export var world_environment: WorldEnvironment
@export var water_material: ShaderMaterial

@export_group("Coucher de soleil")
@export var sunset_sun_rotation := Vector3(-26, -65, 0) ## en degrés
@export var sunset_sun_color := Color("ffdcc0")
@export var sunset_sun_energy := 1.25
@export var sunset_ambient := Color("f0d8e0")
@export var sunset_background := Color("a9a6cc")
@export var sunset_water_deep := Color("7f95bf")
@export var sunset_water_shallow := Color("dcbcc6")


var _water_start := {}


func _ready() -> void:
	# l'environnement et l'eau sont des ressources partagées : on travaille sur des copies
	# (ou on remet les couleurs d'origine en partant) pour que rien ne reste « coucher de soleil »
	if world_environment:
		world_environment.environment = world_environment.environment.duplicate()
	if water_material:
		for p in ["deep", "shallow"]:
			_water_start[p] = water_material.get_shader_parameter(p)


func _exit_tree() -> void:
	for p in _water_start:
		water_material.set_shader_parameter(p, _water_start[p])


func go_to_sunset(duration := 12.0) -> void:
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	if sun:
		tween.tween_property(sun, "rotation_degrees", sunset_sun_rotation, duration)
		tween.tween_property(sun, "light_color", sunset_sun_color, duration)
		tween.tween_property(sun, "light_energy", sunset_sun_energy, duration)
	if world_environment:
		var env := world_environment.environment
		tween.tween_property(env, "ambient_light_color", sunset_ambient, duration)
		tween.tween_property(env, "background_color", sunset_background, duration)
	if water_material:
		tween.tween_method(func(c: Color) -> void: water_material.set_shader_parameter("deep", c),
			_water_color("deep"), sunset_water_deep, duration)
		tween.tween_method(func(c: Color) -> void: water_material.set_shader_parameter("shallow", c),
			_water_color("shallow"), sunset_water_shallow, duration)
	await tween.finished


# Couleur actuelle d'un paramètre de l'eau (ou sa valeur par défaut dans le shader).
func _water_color(param: String) -> Color:
	var v: Variant = water_material.get_shader_parameter(param)
	if v == null:
		v = RenderingServer.shader_get_parameter_default(water_material.shader.get_rid(), param)
	if v is Vector3:
		return Color(v.x, v.y, v.z)
	if v is Color:
		return v
	return Color.WHITE
