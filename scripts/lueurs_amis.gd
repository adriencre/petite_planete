extends Node3D
## Les amis d'Aube, au coin noir (ILE_03_COLONIE.md §6 et §8). On ne les voit vraiment qu'à la fin :
## ici, seulement quand la batterie du robot est presque vide, quelques lueurs floues très pâles
## tournent lentement autour d'elle, comme sur son dessin. Version simple, à remplacer par l'effet d'ombre.

## En dessous de cette batterie (0..1), les lueurs apparaissent.
@export var seuil_batterie: float = 0.15
## Distance (m) du robot à partir de laquelle on peut les deviner.
@export var distance: float = 6.0
@export var nombre: int = 6
@export var rayon: float = 0.75
@export var couleur: Color = Color(1.0, 0.92, 0.72)
## Opacité maximale : elles restent à peine visibles.
@export_range(0.0, 1.0) var opacite: float = 0.35

var _joueur: CharacterBody3D
var _lueurs: Array[MeshInstance3D] = []
var _mat := StandardMaterial3D.new()
var _force: float = 0.0
var _t: float = 0.0


func _ready() -> void:
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = degrade
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	_mat.albedo_texture = tex
	_mat.albedo_color = Color(couleur, 0.0)
	var quad := QuadMesh.new()
	quad.size = Vector2(0.4, 0.4)
	for i in nombre:
		var l := MeshInstance3D.new()
		l.mesh = quad
		l.material_override = _mat
		l.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		l.visible = false
		add_child(l)
		_lueurs.append(l)
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func _process(delta: float) -> void:
	if _joueur == null:
		return
	var a := _joueur.global_position
	var proche: bool = Vector2(a.x - global_position.x, a.z - global_position.z).length() < distance
	var faible: bool = float(_joueur.get("batterie")) < seuil_batterie
	_force = move_toward(_force, 1.0 if (proche and faible) else 0.0, delta * 0.35)
	for l in _lueurs:
		l.visible = _force > 0.01
	if _force <= 0.01:
		return
	_t += delta
	# elles dansent en rond autour d'elle, sans se presser
	for i in _lueurs.size():
		var phase: float = i * TAU / _lueurs.size()
		var ang: float = _t * 0.35 + phase
		var r: float = rayon + 0.15 * sin(_t * 0.8 + i)
		var h: float = 0.45 + 0.35 * sin(_t * 0.6 + i * 1.7)
		_lueurs[i].position = Vector3(cos(ang) * r, h, sin(ang) * r)
	_mat.albedo_color = Color(couleur, _force * opacite * (0.75 + 0.25 * sin(_t * 1.7)))
