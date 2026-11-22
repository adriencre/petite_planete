extends Node3D
## Les amis d'Aube, au coin noir (ILE_03_COLONIE.md §6 et §8) : « Là où mes amis dansent ».
## Décidé le 2026-11-22 : près d'Aube, E éteint la lampe du robot. Dans le noir, ses amis apparaissent
## et dansent en rond autour d'elle : de petites méduses de lumière turquoise (DA.md, le peuple de la
## brume), qui pulsent en nageant. E les fait s'effacer et rallume la lampe. Écho de la page 7 de l'île 1 :
## « Chaque fois que je souffle ma lanterne, elles s'allument tout autour de moi. »
## Sans éteindre, à batterie presque vide, on les devine encore, très pâles.

const SONS := preload("res://scripts/sons.gd")

## Distance (m) du robot à Aube pour pouvoir éteindre sa lampe.
@export var distance_activation: float = 2.6
## En dessous de cette batterie (0..1), on les devine sans éteindre.
@export var seuil_batterie: float = 0.15
@export var distance_batterie: float = 6.0
@export var nombre: int = 7
@export var rayon: float = 1.15
@export var couleur: Color = Color(0.45, 1.0, 0.92)
## Opacité quand la lampe est éteinte, et quand on les devine à batterie faible.
@export_range(0.0, 1.0) var opacite_noir: float = 0.95
@export_range(0.0, 1.0) var opacite_faible: float = 0.25

var vues: bool = false
var _joueur: CharacterBody3D
var _amis: Array[Node3D] = []
var _cloches: Array[MeshInstance3D] = []
var _mat_cloche := StandardMaterial3D.new()
var _mat_halo := StandardMaterial3D.new()
var _lumiere := OmniLight3D.new()
var _force: float = 0.0
var _t: float = 0.0
## "" = rien ; "extinction" ; "noir" (ils dansent) ; "rallumage".
var _etat: String = ""


func _ready() -> void:
	add_to_group("interactif")
	add_to_group("sauvegarde")
	vues = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("vues", false))
	_construire()
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "amis_aube"


func sauver() -> Dictionary:
	return {"vues": vues}


## Pour guidage.gd : 2 = E possible, 1 = à découvrir, 0 = rien.
func etat_interaction() -> int:
	if _joueur == null or _etat == "extinction" or _etat == "rallumage":
		return 0
	if _etat == "noir":
		return 2
	if bool(_joueur.get("cinematique")):
		return 0
	if _a_portee():
		return 2
	return 0 if vues else 1


func point_appel() -> Vector3:
	return global_position + Vector3.UP * 0.9


# ---------------------------------------------------------------- les amis

## Chaque ami : une cloche de méduse aplatie (émissive), quelques filaments et un halo doux.
func _construire() -> void:
	_mat_cloche.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mat_cloche.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mat_cloche.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_mat_cloche.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mat_cloche.albedo_color = Color(couleur, 0.0)
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = degrade
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	_mat_halo.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mat_halo.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mat_halo.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_mat_halo.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	_mat_halo.albedo_texture = tex
	_mat_halo.albedo_color = Color(couleur, 0.0)
	var cloche := SphereMesh.new()
	cloche.radius = 0.16
	cloche.height = 0.2
	cloche.is_hemisphere = true
	cloche.radial_segments = 8
	cloche.rings = 3
	var filament := CylinderMesh.new()
	filament.top_radius = 0.012
	filament.bottom_radius = 0.003
	filament.height = 0.32
	filament.radial_segments = 4
	filament.rings = 1
	var halo := QuadMesh.new()
	halo.size = Vector2(0.75, 0.75)
	for i in nombre:
		var ami := Node3D.new()
		ami.visible = false
		add_child(ami)
		var c := MeshInstance3D.new()
		c.mesh = cloche
		c.material_override = _mat_cloche
		c.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		ami.add_child(c)
		for k in 4:
			var f := MeshInstance3D.new()
			f.mesh = filament
			f.material_override = _mat_cloche
			f.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var a: float = TAU * k / 4.0 + 0.4
			f.position = Vector3(cos(a) * 0.08, -0.16, sin(a) * 0.08)
			c.add_child(f)
		var h := MeshInstance3D.new()
		h.mesh = halo
		h.material_override = _mat_halo
		h.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		ami.add_child(h)
		_amis.append(ami)
		_cloches.append(c)
	# une lumière turquoise douce sur Aube pendant la danse
	_lumiere.light_color = couleur
	_lumiere.light_energy = 0.0
	_lumiere.omni_range = 3.5
	_lumiere.position = Vector3.UP * 0.8
	add_child(_lumiere)


func _process(delta: float) -> void:
	if _joueur == null:
		return
	var cible: float = 0.0
	var opacite: float = opacite_faible
	if _etat == "noir":
		cible = 1.0
		opacite = opacite_noir
	elif _etat == "":
		var a := _joueur.global_position
		var proche: bool = Vector2(a.x - global_position.x, a.z - global_position.z).length() < distance_batterie
		if proche and float(_joueur.get("batterie")) < seuil_batterie:
			cible = 1.0
	var vitesse: float = 0.45 if _etat == "noir" else 0.6
	_force = move_toward(_force, cible, delta * vitesse)
	for ami in _amis:
		ami.visible = _force > 0.01
	_lumiere.light_energy = _force * (0.9 if opacite > 0.5 else 0.0)
	if _force <= 0.01:
		return
	_t += delta
	# une ronde lente autour d'elle : chacun nage en pulsant, monte et descend, tourne sur lui-même
	for i in _amis.size():
		var phase: float = i * TAU / _amis.size()
		var ang: float = _t * 0.42 + phase
		var r: float = rayon + 0.2 * sin(_t * 0.7 + i * 1.3)
		var h: float = 0.75 + 0.4 * sin(_t * 0.9 + i * 1.7)
		_amis[i].position = Vector3(cos(ang) * r, h, sin(ang) * r)
		_amis[i].rotation.y = -ang
		var pouls: float = 0.5 + 0.5 * sin(_t * 2.4 + i * 0.9)
		_cloches[i].scale = Vector3(1.0 + 0.18 * pouls, 1.0 - 0.22 * pouls, 1.0 + 0.18 * pouls)
		_cloches[i].rotation.z = 0.25 * sin(_t * 1.2 + i)
	var scintille: float = 0.85 + 0.15 * sin(_t * 1.7)
	_mat_cloche.albedo_color = Color(couleur, _force * opacite * 0.55 * scintille)
	_mat_halo.albedo_color = Color(couleur, _force * opacite * 0.5 * scintille)


# ---------------------------------------------------------------- éteindre, rallumer

func _a_portee() -> bool:
	var a := _joueur.global_position
	var p := global_position
	return Vector2(a.x - p.x, a.z - p.z).length() < distance_activation and absf(a.y - p.y) < 1.5


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E:
		return
	if _etat == "noir":
		get_viewport().set_input_as_handled()
		_rallumer()
		return
	if _etat != "" or bool(_joueur.get("cinematique")) or not _a_portee():
		return
	get_viewport().set_input_as_handled()
	_eteindre()


## Le robot regarde Aube et souffle sa lampe : l'antenne s'éteint doucement, puis ils arrivent.
func _eteindre() -> void:
	_etat = "extinction"
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", global_position)
	await get_tree().create_timer(0.8).timeout
	_joueur.set("antenne_allumee", false)
	SONS.jouer("extinction", _joueur.global_position, -6.0)
	await get_tree().create_timer(1.6).timeout
	_etat = "noir"
	vues = true


## E dans le noir : ils s'effacent, la lampe se rallume, on reprend la main.
func _rallumer() -> void:
	_etat = "rallumage"
	await get_tree().create_timer(1.8).timeout
	_joueur.set("antenne_allumee", true)
	SONS.jouer("allumage", _joueur.global_position, -6.0)
	await get_tree().create_timer(0.6).timeout
	_joueur.set("cinematique", false)
	_etat = ""
