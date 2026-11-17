extends Node3D
## Ce qui guide le joueur sans HUD (DA.md, « Interface et effets ») :
## - LA LUEUR : tout ce qu'on peut utiliser (groupe « interactif ») scintille en doré : quelques grains de
##   lumière qui montent et un halo doux. Légère quand on approche, franche quand E est possible.
## - LA TOUCHE E : à portée d'un objet, une petite touche dorée flotte au-dessus (le même dessin que celui
##   de la luciole). Une fois le geste appris (quelques utilisations), elle ne revient que si on reste
##   planté devant un objet sans rien faire.
## Chaque objet dit lui-même où il en est : `etat_interaction()` (0 = rien, 1 = à découvrir,
## 2 = E possible maintenant) et `point_appel()` ; ou une méta « etat_interaction » (un Callable),
## pour un objet sans script (le carnet sur l'étagère). Le mode d'emploi du jardinier, sur le tapis de l'abri : abri.gd (_notice).

@export var couleur: Color = Color(1.0, 0.82, 0.45)
## Distance (m) à partir de laquelle un objet « à découvrir » commence à scintiller.
@export var distance_appel: float = 9.0
## Au-dessus de l'objet, hauteur de la touche E (m).
@export var hauteur_touche: float = 0.95
## Après autant d'utilisations de E, la touche ne s'affiche plus d'elle-même.
@export var utilisations_pour_apprendre: int = 4
## Une fois appris : planté devant un objet sans rien faire, la touche revient au bout de (s).
@export var delai_rappel: float = 7.0

var _joueur: CharacterBody3D
var _effets: Dictionary = {}      # objet -> {racine, halo, mat, grains, force}
var _t: float = 0.0
var _utilisations: int = 0
var _attente: float = 0.0
var _touche: Node3D
var _touche_mat := StandardMaterial3D.new()
var _touche_force: float = 0.0
var _touche_cible: Node3D = null
var _halo_tex: GradientTexture2D


func _ready() -> void:
	add_to_group("guidage")
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	_halo_tex = GradientTexture2D.new()
	_halo_tex.gradient = degrade
	_halo_tex.fill = GradientTexture2D.FILL_RADIAL
	_halo_tex.fill_from = Vector2(0.5, 0.5)
	_halo_tex.fill_to = Vector2(0.5, 0.0)
	_construire_touche()
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


## Pour la luciole : elle ne dessine pas sa touche si la nôtre est déjà là.
func touche_visible() -> bool:
	return _touche_force > 0.3


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and (event as InputEventKey).physical_keycode == KEY_E:
		if _touche_cible:
			_utilisations += 1
			_attente = 0.0


func _etat(o: Node) -> int:
	if o.has_method("etat_interaction"):
		return int(o.call("etat_interaction"))
	if o.has_meta("etat_interaction"):
		return int((o.get_meta("etat_interaction") as Callable).call())
	return 0


func _point(o: Node) -> Vector3:
	if o.has_method("point_appel"):
		return o.call("point_appel")
	return (o as Node3D).global_position


func _process(delta: float) -> void:
	if _joueur == null:
		return
	_t += delta
	var moi := _joueur.global_position
	var meilleur: Node3D = null
	var d_meilleur := INF
	var vus := {}
	for o in get_tree().get_nodes_in_group("interactif"):
		if not (o is Node3D) or not o.is_inside_tree():
			continue
		vus[o] = true
		var etat := _etat(o)
		var p := _point(o)
		var d := Vector2(p.x - moi.x, p.z - moi.z).length()
		var cible := 0.0
		if etat == 2:
			cible = 1.0
			if d < d_meilleur:
				d_meilleur = d
				meilleur = o
		elif etat == 1:
			cible = 0.4 * clampf(inverse_lerp(distance_appel, distance_appel * 0.4, d), 0.0, 1.0)
		_lueur(o, p, cible, delta)
	# les objets disparus
	for o in _effets.keys():
		if not vus.has(o):
			var e: Dictionary = _effets[o]
			if is_instance_valid(e.racine):
				(e.racine as Node).queue_free()
			_effets.erase(o)
	_placer_touche(meilleur, delta)


# ---------------------------------------------------------------- la lueur

func _lueur(o: Node3D, p: Vector3, cible: float, delta: float) -> void:
	if not _effets.has(o):
		if cible <= 0.0:
			return
		_effets[o] = _creer_lueur()
	var e: Dictionary = _effets[o]
	var f: float = move_toward(float(e.force), cible, delta * 1.5)
	e.force = f
	var racine := e.racine as Node3D
	racine.global_position = p
	var souffle := 0.7 + 0.3 * sin(_t * 2.4 + float(o.get_instance_id() % 7))
	(e.mat as StandardMaterial3D).albedo_color = Color(couleur.r, couleur.g, couleur.b, 0.5 * f * souffle)
	(e.halo as Node3D).scale = Vector3.ONE * (0.8 + 0.4 * f)
	var grains := e.grains as CPUParticles3D
	grains.emitting = f > 0.08
	(e.grains_mat as StandardMaterial3D).albedo_color = Color(1, 1, 1, clampf(f * 1.3, 0.2, 1.0))
	racine.visible = f > 0.01


func _creer_lueur() -> Dictionary:
	var racine := Node3D.new()
	add_child(racine)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_texture = _halo_tex
	mat.no_depth_test = true
	var q := QuadMesh.new()
	q.size = Vector2(0.9, 0.9)
	q.material = mat
	var halo := MeshInstance3D.new()
	halo.mesh = q
	halo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	racine.add_child(halo)
	# des grains de lumière qui montent doucement
	var grains := CPUParticles3D.new()
	var gq := QuadMesh.new()
	gq.size = Vector2(0.05, 0.05)
	var gm := StandardMaterial3D.new()
	gm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	gm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	gm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	gm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	gm.vertex_color_use_as_albedo = true
	gq.material = gm
	grains.mesh = gq
	grains.amount = 16
	grains.lifetime = 1.8
	grains.emitting = false
	grains.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	grains.emission_sphere_radius = 0.35
	grains.direction = Vector3.UP
	grains.spread = 25.0
	grains.initial_velocity_min = 0.15
	grains.initial_velocity_max = 0.4
	grains.gravity = Vector3.ZERO
	var g := Gradient.new()
	g.set_color(0, Color(couleur.r, couleur.g, couleur.b, 0.0))
	g.add_point(0.25, Color(1.0, 0.92, 0.7, 1.0))
	g.set_color(g.get_point_count() - 1, Color(couleur.r, couleur.g, couleur.b, 0.0))
	grains.color_ramp = g
	racine.add_child(grains)
	return {"racine": racine, "halo": halo, "mat": mat, "grains": grains, "grains_mat": gm, "force": 0.0}


# ---------------------------------------------------------------- la touche E

func _placer_touche(cible: Node3D, delta: float) -> void:
	var appris := _utilisations >= utilisations_pour_apprendre
	var montrer := cible != null
	if montrer and appris:
		var immobile := Vector2(_joueur.velocity.x, _joueur.velocity.z).length() < 0.2
		_attente = _attente + delta if immobile else 0.0
		montrer = _attente >= delai_rappel
	elif not montrer:
		_attente = 0.0
	if montrer:
		_touche_cible = cible
	_touche_force = move_toward(_touche_force, 1.0 if montrer else 0.0, delta * 3.0)
	if _touche_force <= 0.0:
		_touche.visible = false
		_touche_cible = null
		return
	_touche.visible = true
	var cam := get_viewport().get_camera_3d()
	if cam and _touche_cible and is_instance_valid(_touche_cible):
		var p := _point(_touche_cible) + Vector3.UP * (hauteur_touche + 0.06 * sin(_t * 2.2))
		_touche.global_transform = Transform3D(cam.global_basis.scaled(Vector3.ONE * (0.75 + 0.25 * _touche_force)), p)
	_touche_mat.albedo_color.a = _touche_force


## La touche : un carré doré et un « E » au milieu, en barres fines (comme celle que trace la luciole).
func _construire_touche() -> void:
	_touche = Node3D.new()
	_touche.name = "ToucheGuidage"
	_touche.visible = false
	add_child(_touche)
	_touche_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_touche_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_touche_mat.no_depth_test = true
	_touche_mat.render_priority = 2
	_touche_mat.albedo_color = Color(couleur.r * 2.2, couleur.g * 2.0, couleur.b * 1.6, 0.0)
	var c := 0.25
	_barre(Vector3(0, c, 0), Vector3(c * 2 + 0.03, 0.03, 0.01))
	_barre(Vector3(0, -c, 0), Vector3(c * 2 + 0.03, 0.03, 0.01))
	_barre(Vector3(c, 0, 0), Vector3(0.03, c * 2 + 0.03, 0.01))
	_barre(Vector3(-c, 0, 0), Vector3(0.03, c * 2 + 0.03, 0.01))
	var l := 0.1
	var hh := 0.14
	_barre(Vector3(0, hh, 0), Vector3(l * 2 + 0.035, 0.035, 0.01))
	_barre(Vector3(0, -hh, 0), Vector3(l * 2 + 0.035, 0.035, 0.01))
	_barre(Vector3(-l, 0, 0), Vector3(0.035, hh * 2 + 0.035, 0.01))
	_barre(Vector3(-l * 0.15, 0, 0), Vector3(l * 1.7, 0.035, 0.01))


func _barre(pos: Vector3, taille: Vector3) -> void:
	var b := MeshInstance3D.new()
	var m := BoxMesh.new()
	m.size = taille
	m.material = _touche_mat
	b.mesh = m
	b.position = pos
	b.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_touche.add_child(b)
