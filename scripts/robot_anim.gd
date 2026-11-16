extends Node3D
## Animation procédurale du robot : marche un peu maladroite, respiration, tête curieuse.
## Applique aussi le métal patiné sur les pièces « robot_metal ».

const PATINE := preload("res://shaders/metal_patine.gdshader")

@export var amplitude_pas: float = 0.45
@export var cadence: float = 7.5
@export var vitesse_reference: float = 3.6

var _os := {}
var _phase := 0.0
var _t := 0.0
var _vitesse := 0.0
var _prec := Vector3.ZERO
var _trebuche := 0.0
var _prochain_trebuche := 8.0


func _ready() -> void:
	for n in ["Bassin", "Torse", "Tete", "Epaule_D", "Coude_D", "Poignet_D", "Epaule_G", "Coude_G", "Poignet_G",
			"Hanche_D", "Genou_D", "Cheville_D", "Hanche_G", "Genou_G", "Cheville_G"]:
		var o := find_child(n, true, false) as Node3D
		if o:
			_os[n] = o
	var m := ShaderMaterial.new()
	m.shader = PATINE
	for mi in find_children("*", "MeshInstance3D", true, false):
		var inst := mi as MeshInstance3D
		for s in inst.mesh.get_surface_count():
			var mat := inst.mesh.surface_get_material(s)
			if mat and mat.resource_name.begins_with("robot_metal"):
				inst.set_surface_override_material(s, m)
	_prec = global_position


func _rx(n: String, v: float) -> void:
	if _os.has(n):
		(_os[n] as Node3D).rotation.x = v


func _process(delta: float) -> void:
	_t += delta
	var dp := global_position - _prec
	_prec = global_position
	var v := Vector2(dp.x, dp.z).length() / maxf(delta, 0.0001)
	_vitesse = lerpf(_vitesse, v, 1.0 - exp(-8.0 * delta))
	var f := clampf(_vitesse / vitesse_reference, 0.0, 1.6)
	_phase += delta * cadence * clampf(f, 0.0, 1.3)
	var s := sin(_phase)
	# petit trébuchement de temps en temps quand il marche (maladroit)
	if f > 0.4:
		_prochain_trebuche -= delta
		if _prochain_trebuche <= 0.0:
			_trebuche = 1.0
			_prochain_trebuche = randf_range(7.0, 14.0)
	_trebuche = move_toward(_trebuche, 0.0, delta * 2.2)
	var tr := sin(_trebuche * PI) * _trebuche
	# jambes
	_rx("Hanche_D", -s * amplitude_pas * f)
	_rx("Hanche_G", s * amplitude_pas * f)
	_rx("Genou_D", maxf(0.0, sin(_phase + 1.3)) * 0.8 * f)
	_rx("Genou_G", maxf(0.0, sin(_phase + PI + 1.3)) * 0.8 * f)
	_rx("Cheville_D", -maxf(0.0, sin(_phase + 2.2)) * 0.3 * f)
	_rx("Cheville_G", -maxf(0.0, sin(_phase + PI + 2.2)) * 0.3 * f)
	# bras : balancement opposé, coudes souples, bras qui s'écartent quand il trébuche
	_rx("Epaule_D", s * 0.38 * f - tr * 0.6)
	_rx("Epaule_G", -s * 0.38 * f - tr * 0.6)
	_rx("Coude_D", -0.2 - 0.25 * f - tr * 0.5)
	_rx("Coude_G", -0.2 - 0.25 * f - tr * 0.5)
	if _os.has("Epaule_D"):
		(_os["Epaule_D"] as Node3D).rotation.z = 0.06 + tr * 0.5
		(_os["Epaule_G"] as Node3D).rotation.z = -0.06 - tr * 0.5
	# torse : roulis, respiration, penché quand il trébuche
	if _os.has("Torse"):
		var t := _os["Torse"] as Node3D
		t.rotation = Vector3(0.05 * f + tr * 0.35, sin(_phase) * 0.08 * f, sin(_phase) * 0.05 * f)
		t.scale = Vector3(1, 1.0 + 0.012 * sin(_t * 1.6), 1)
	# tête : curieuse, regarde autour à l'arrêt, dodeline en marchant
	if _os.has("Tete"):
		var h := _os["Tete"] as Node3D
		var calme := 1.0 - clampf(f, 0.0, 1.0)
		h.rotation = Vector3(-0.05 + sin(_t * 0.5) * 0.08 * calme - tr * 0.3,
				sin(_t * 0.31) * 0.45 * calme,
				sin(_t * 0.7) * 0.07 + sin(_phase * 2.0) * 0.03 * f)
