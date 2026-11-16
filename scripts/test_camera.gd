extends Node3D
## Test caméra + lumière : réutilise le décor du test DA.
## N : le robot éteint son antenne -> paupière, noir, puis le monde revient en nuit bleue
##     et le peuple de la brume apparaît. N à nouveau pour rallumer.
## B (maintenu) : la brume vide la batterie -> vision trouble ; presque vide, des formes apparaissent.

@export var duree_fermeture: float = 0.7
@export var duree_noir: float = 0.9
@export var duree_ouverture: float = 1.6
# TODO DA (2026-11-16) : la version nuit n'est pas encore ça — beaucoup trop éclairée,
# couleurs trop vives, pas assez pastel. À retravailler dans un 2e temps (voir DA.md).
@export_group("Nuit")
@export var ciel_haut_nuit: Color = Color(0.03, 0.04, 0.14)
@export var ciel_milieu_nuit: Color = Color(0.07, 0.09, 0.26)
@export var ciel_horizon_nuit: Color = Color(0.16, 0.2, 0.42)
@export var ciel_bas_nuit: Color = Color(0.04, 0.07, 0.17)
@export var nuage_lumiere_nuit: Color = Color(0.22, 0.28, 0.52)
@export var nuage_ombre_nuit: Color = Color(0.07, 0.09, 0.24)
@export var lune_couleur: Color = Color(0.55, 0.65, 1.0)
@export var lune_energie: float = 0.35
@export var ambiance_nuit: Color = Color(0.25, 0.35, 0.7)
@export var brouillard_nuit: Color = Color(0.06, 0.12, 0.25)
@export var brume_lueur_nuit: Color = Color(0.05, 0.55, 0.5)

@onready var decor: Node3D = $Decor
@onready var joueur = $Joueur  # joueur.gd (batterie, antenne_allumee)
@onready var vision: ShaderMaterial = ($Vision/Ecran as ColorRect).material

var nuit := 0.0:
	set(v):
		nuit = v
		_appliquer_nuit()
var _en_transition := false
var _jour := {}
var _env: Environment
var _ciel: ShaderMaterial
var _soleil: DirectionalLight3D
var _brume: FogMaterial
var _mats_nuit: Array[ShaderMaterial] = []


func _ready() -> void:
	decor.get_node("Robot").visible = false
	(decor.get_node("Camera") as Camera3D).current = false
	for chemin in ["Falaise", "Ruine", "Rochers", "TourSemeurs"]:
		_ajouter_collisions(decor.get_node(chemin))
	_env = (decor.get_node("Environnement") as WorldEnvironment).environment
	_ciel = _env.sky.sky_material as ShaderMaterial
	_soleil = decor.get_node("Soleil")
	_brume = (decor.get_node("Brume") as FogVolume).material as FogMaterial
	for chemin in ["Falaise/Falaise", "Herbe", "Mer"]:
		var mi := decor.get_node(chemin) as GeometryInstance3D
		var m := mi.material_override as ShaderMaterial
		if m == null and mi is MeshInstance3D:
			m = (mi as MeshInstance3D).mesh.surface_get_material(0) as ShaderMaterial
		if m and not _mats_nuit.has(m):
			_mats_nuit.append(m)
	_jour = {
		"haut": _param_couleur(_ciel, "couleur_haut"),
		"milieu": _param_couleur(_ciel, "couleur_milieu"),
		"horizon": _param_couleur(_ciel, "couleur_horizon"),
		"bas": _param_couleur(_ciel, "couleur_bas"),
		"nl": _param_couleur(_ciel, "nuage_lumiere"),
		"no": _param_couleur(_ciel, "nuage_ombre"),
		"soleil_c": _soleil.light_color, "soleil_e": _soleil.light_energy,
		"amb": _env.ambient_light_color, "amb_e": _env.ambient_light_energy,
		"fog": _env.fog_light_color, "brume_em": _brume.emission,
		"vol_em": _env.volumetric_fog_emission,
	}
	_appliquer_nuit()


## Valeur d'un paramètre couleur du shader (sa valeur par défaut s'il n'a jamais été réglé).
func _param_couleur(m: ShaderMaterial, nom: String) -> Color:
	var v: Variant = m.get_shader_parameter(nom)
	if v == null:
		v = RenderingServer.shader_get_parameter_default(m.shader.get_rid(), nom)
	if v is Vector3:
		var w: Vector3 = v
		return Color(w.x, w.y, w.z)
	if v is Color:
		return v
	return Color.WHITE


func _ajouter_collisions(n: Node) -> void:
	if n is MeshInstance3D:
		(n as MeshInstance3D).create_trimesh_collision()
	for c in n.get_children():
		_ajouter_collisions(c)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if (event as InputEventKey).physical_keycode == KEY_N and not _en_transition:
			_basculer()


func _basculer() -> void:
	_en_transition = true
	var vers_nuit := nuit < 0.5
	if vers_nuit:
		joueur.antenne_allumee = false
	var tw := create_tween()
	tw.tween_method(_set_paupiere, 0.0, 1.0, duree_fermeture).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.tween_property(self, "nuit", 1.0 if vers_nuit else 0.0, duree_noir)
	tw.tween_method(_set_paupiere, 1.0, 0.0, duree_ouverture).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_callback(_fin_transition.bind(vers_nuit))


func _fin_transition(vers_nuit: bool) -> void:
	_en_transition = false
	if not vers_nuit:
		joueur.antenne_allumee = true


func _set_paupiere(v: float) -> void:
	vision.set_shader_parameter("paupiere", v)


func _process(_delta: float) -> void:
	var b: float = joueur.batterie
	var trouble := clampf((0.45 - b) / 0.4, 0.0, 1.0)
	vision.set_shader_parameter("trouble", trouble * (1.0 - nuit))
	# le peuple de la brume : visible la nuit, ou à peine quand la batterie est presque vide
	var accident := clampf((0.18 - b) / 0.15, 0.0, 1.0) * 0.5
	for c in get_tree().get_nodes_in_group("peuple_brume"):
		c.set("apparition", maxf(nuit, accident))


func _appliquer_nuit() -> void:
	if _ciel == null:
		return
	var t := nuit
	_ciel.set_shader_parameter("couleur_haut", (_jour.haut as Color).lerp(ciel_haut_nuit, t))
	_ciel.set_shader_parameter("couleur_milieu", (_jour.milieu as Color).lerp(ciel_milieu_nuit, t))
	_ciel.set_shader_parameter("couleur_horizon", (_jour.horizon as Color).lerp(ciel_horizon_nuit, t))
	_ciel.set_shader_parameter("couleur_bas", (_jour.bas as Color).lerp(ciel_bas_nuit, t))
	_ciel.set_shader_parameter("nuage_lumiere", (_jour.nl as Color).lerp(nuage_lumiere_nuit, t))
	_ciel.set_shader_parameter("nuage_ombre", (_jour.no as Color).lerp(nuage_ombre_nuit, t))
	_ciel.set_shader_parameter("etoiles", t)
	_soleil.light_color = (_jour.soleil_c as Color).lerp(lune_couleur, t)
	_soleil.light_energy = lerpf(_jour.soleil_e, lune_energie, t)
	_env.ambient_light_color = (_jour.amb as Color).lerp(ambiance_nuit, t)
	_env.ambient_light_energy = lerpf(_jour.amb_e, 0.45, t)
	_env.fog_light_color = (_jour.fog as Color).lerp(brouillard_nuit, t)
	_brume.emission = (_jour.brume_em as Color).lerp(brume_lueur_nuit, t)
	_env.volumetric_fog_emission = (_jour.vol_em as Color).lerp(Color(0.02, 0.12, 0.16), t)
	for m in _mats_nuit:
		m.set_shader_parameter("nuit", t)
