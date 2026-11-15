extends Node3D
## Le monde de l'ombre d'une île (à mettre sur le nœud « Ombre » de l'île).
## Quand le robot est dans le noir, l'île passe à la nuit : ciel profond, lumière de lune froide,
## ambiance bleutée. (Les maisons, décors et habitants apparaissent d'eux-mêmes : voir OmbreObjet.)

@export var environment: WorldEnvironment
@export var sun: DirectionalLight3D
@export_group("Nuit")
@export var night_sky := Color(0.04, 0.06, 0.13)
@export var night_ambient := Color(0.35, 0.42, 0.7)
@export var night_ambient_energy := 0.6
@export var moon_color := Color(0.62, 0.72, 1.0)
@export var moon_energy := 0.55
@export var night_glow := 0.85

var _day_sky: Color
var _day_ambient: Color
var _day_ambient_energy: float
var _day_sun_color: Color
var _day_sun_energy: float
var _day_glow: float
var _amount := -1.0


func _ready() -> void:
	if environment and environment.environment:
		var env := environment.environment
		_day_sky = env.background_color
		_day_ambient = env.ambient_light_color
		_day_ambient_energy = env.ambient_light_energy
		_day_glow = env.glow_intensity
	if sun:
		_day_sun_color = sun.light_color
		_day_sun_energy = sun.light_energy


func _process(_delta: float) -> void:
	var k := smoothstep(0.25, 0.9, maxf(OmbreObjet.vision, 0.0))
	if absf(k - _amount) < 0.002:
		return
	_amount = k
	if environment and environment.environment:
		var env := environment.environment
		env.background_color = _day_sky.lerp(night_sky, k)
		env.ambient_light_color = _day_ambient.lerp(night_ambient, k)
		env.ambient_light_energy = lerpf(_day_ambient_energy, night_ambient_energy, k)
		env.glow_intensity = lerpf(_day_glow, night_glow, k)
	if sun:
		sun.light_color = _day_sun_color.lerp(moon_color, k)
		sun.light_energy = lerpf(_day_sun_energy, moon_energy, k)
