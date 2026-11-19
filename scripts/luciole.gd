extends Node3D
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## La luciole du premier réveil (ILE_01_REVEIL.md §5, « La sortie »). Quand on prend la main pour la
## première fois, elle s'allume doucement devant la porte de l'abri, puis guide le robot dans la brume :
## d'abord vers la pierre-soleil (l'antenne est vide), puis vers la lanterne 1. Elle reste quelques
## mètres devant lui et l'attend s'il traîne. Une fois la lanterne allumée, elle monte et s'éteint.
## Rien de magique : c'est une petite bête lumineuse, rien de plus.

@export var couleur: Color = Color(1.0, 0.9, 0.55)
## Distance à laquelle elle se tient devant le robot.
@export var avance: float = 3.0
## Hauteur à laquelle elle vole au-dessus du sol.
@export var hauteur_vol: float = 1.3
@export var energie_lumiere: float = 1.6
## Devant le but, au bout de combien de secondes sans rien faire elle dessine la touche E.
@export var delai_aide: float = 4.0
## Distance au but sous laquelle on considère que le robot est « devant ».
@export var distance_aide: float = 3.5

var _attente: float = 0.0
var _dessin: String = ""       # "" = rien ; "trace" = elle dessine ; "affiche" = la touche est allumée
var _touche: Node3D
var _touche_mat := StandardMaterial3D.new()
var _touche_tween: Tween

var _joueur: CharacterBody3D
var _etape: int = -1          # -1 = attend le réveil ; 0 = pierre-soleil ; 1 = lanterne 1 ; 2 = départ
var _cible: Node3D
var _t: float = 0.0
var _calme: float = 0.0        # temps passé avec le robot libre de ses mouvements
var _lumiere := OmniLight3D.new()
var _corps := MeshInstance3D.new()
var _mat := StandardMaterial3D.new()
var _halo_mat := StandardMaterial3D.new()
var _trainee := CPUParticles3D.new()
var _eclat: float = 0.0        # 0 = éteinte, 1 = allumée


func _ready() -> void:
	add_to_group("sauvegarde")
	_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mat.albedo_color = couleur
	var boule := SphereMesh.new()
	boule.radius = 0.08
	boule.height = 0.16
	boule.radial_segments = 10
	boule.rings = 5
	boule.material = _mat
	_corps.mesh = boule
	_corps.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_corps)
	# le halo : un disque doux toujours tourné vers la caméra, pour la voir de haut et dans la brume
	var halo := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(0.7, 0.7)
	var degrade := Gradient.new()
	degrade.set_color(0, Color(1, 1, 1, 1))
	degrade.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = degrade
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5, 0.0)
	_halo_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_halo_mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	_halo_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_halo_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_halo_mat.albedo_texture = tex
	_halo_mat.no_depth_test = true
	q.material = _halo_mat
	halo.mesh = q
	halo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_corps.add_child(halo)
	_lumiere.light_color = couleur
	_lumiere.omni_range = 3.5
	_lumiere.light_volumetric_fog_energy = 3.0   # un petit halo dans la brume
	add_child(_lumiere)
	_preparer_trainee()
	visible = false
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	# « Continuer » : elle a déjà guidé le robot jusqu'à la lanterne 1, elle ne revient pas
	if int(Sauvegarde.donnees(cle_sauvegarde()).get("etape", -1)) >= 2:
		_etape = 2
		visible = false


func cle_sauvegarde() -> String:
	return "luciole"


func sauver() -> Dictionary:
	return {"etape": _etape}


func _preparer_trainee() -> void:
	var quad := QuadMesh.new()
	quad.size = Vector2(0.03, 0.03)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.vertex_color_use_as_albedo = true
	quad.material = m
	_trainee.mesh = quad
	_trainee.local_coords = false   # la traînée reste derrière elle quand elle vole
	_trainee.amount = 40
	_trainee.lifetime = 1.4
	_trainee.direction = Vector3.DOWN
	_trainee.spread = 180.0
	_trainee.initial_velocity_min = 0.02
	_trainee.initial_velocity_max = 0.1
	_trainee.gravity = Vector3(0, -0.05, 0)
	var g := Gradient.new()
	g.set_color(0, Color(couleur.r, couleur.g, couleur.b, 0.9))
	g.set_color(1, Color(couleur.r, couleur.g, couleur.b, 0.0))
	_trainee.color_ramp = g
	add_child(_trainee)


func _process(delta: float) -> void:
	if _joueur == null:
		return
	_t += delta
	match _etape:
		-1:
			_attendre_reveil(delta)
		0, 1:
			_surveiller_attente(delta)
			if _dessin == "":
				_guider(delta)
			_verifier_etape()
		2:
			pass
	# éclat : elle respire doucement
	var souffle := 0.75 + 0.25 * sin(_t * 2.6)
	_lumiere.light_energy = energie_lumiere * _eclat * souffle
	_mat.albedo_color = couleur * (1.0 + 2.0 * _eclat * souffle)   # > 1 : le halo de lumière (glow) prend
	_halo_mat.albedo_color = Color(couleur.r, couleur.g, couleur.b, 0.55 * _eclat * souffle)
	_corps.scale = Vector3.ONE * maxf(_eclat, 0.01)


## Elle apparaît la première fois qu'on a la main (fin du premier réveil, ou réveil passé).
func _attendre_reveil(delta: float) -> void:
	_calme = _calme + delta if not bool(_joueur.get("cinematique")) else 0.0
	if _calme < 1.2:
		return
	var abri := get_tree().get_first_node_in_group("abri") as Node3D
	var porte: Node3D = abri.find_child("Porte", true, false) as Node3D if abri else null
	var depart: Vector3 = porte.global_position if porte else _joueur.global_position
	global_position = depart + Vector3.UP * 1.6
	visible = true
	SONS.jouer("luciole", global_position)
	_etape = 0
	_cible = _pierre_la_plus_proche(depart)
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(self, "_eclat", 1.0, 2.5)


func _guider(delta: float) -> void:
	if _cible == null:
		return
	var moi: Vector3 = _joueur.global_position
	var but: Vector3 = _cible.global_position
	var vers := Vector3(but.x - moi.x, 0, but.z - moi.z)
	var reste := vers.length()
	# un peu devant le robot, sur le chemin du but ; au but, elle tourne autour
	var p: Vector3
	if reste < avance + 0.8:
		var a := _t * 1.1
		p = but + Vector3(cos(a), 0, sin(a)) * 1.1
	else:
		p = moi + vers / reste * avance
	p.y = _sol(p) + hauteur_vol
	# elle volette : petits écarts, jamais une ligne droite
	p += Vector3(sin(_t * 1.7) * 0.25, sin(_t * 2.3) * 0.15, cos(_t * 1.3) * 0.25)
	global_position = global_position.lerp(p, 1.0 - exp(-delta * 1.4))


# ---------------------------------------------------------------- la touche E dessinée en lumière

## Le robot est devant le but (pierre-soleil, lanterne) mais ne fait rien : au bout de quelques
## secondes, la luciole dessine dans l'air le contour d'une touche, et un « E » doré s'y allume.
## Tout s'efface dès qu'il agit (cinématique) ou s'éloigne.
func _surveiller_attente(delta: float) -> void:
	if _cible == null:
		return
	var moi: Vector3 = _joueur.global_position
	var but: Vector3 = _cible.global_position
	var proche := Vector2(moi.x - but.x, moi.z - but.z).length() < distance_aide
	var agit := bool(_joueur.get("cinematique"))
	var immobile := Vector2(_joueur.velocity.x, _joueur.velocity.z).length() < 0.2
	if _dessin != "":
		if agit or not proche:
			_effacer_touche()
		return
	# la touche du guidage (guidage.gd) est déjà là : pas besoin de la dessiner en plus
	var guidage := get_tree().get_first_node_in_group("guidage")
	if guidage and bool(guidage.call("touche_visible")):
		_attente = 0.0
		return
	_attente = _attente + delta if proche and immobile and not agit else 0.0
	if _attente >= delai_aide:
		_attente = 0.0
		_dessiner_touche()


func _dessiner_touche() -> void:
	SONS.jouer("luciole", global_position, -3.0)
	_dessin = "trace"
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		_dessin = ""
		return
	# la touche flotte au-dessus du but, tournée vers la caméra
	var but: Vector3 = _cible.global_position
	var vers_cam := cam.global_position - but
	vers_cam.y = 0.0
	_touche = Node3D.new()
	_touche.name = "ToucheE"
	get_tree().current_scene.add_child(_touche)
	_touche.global_position = but + Vector3.UP * 2.1 + vers_cam.normalized() * 0.6
	_touche.global_basis = cam.global_basis
	var cote := 0.5
	var coins: Array[Vector3] = [Vector3(-1, 1, 0), Vector3(1, 1, 0), Vector3(1, -1, 0), Vector3(-1, -1, 0)]
	_touche_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_touche_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_touche_mat.albedo_color = Color(couleur.r * 2.2, couleur.g * 2.0, couleur.b * 1.6, 1.0)
	# la luciole rejoint le premier coin, puis trace les quatre côtés ; chaque côté s'allume derrière elle
	var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(self, "global_position", _touche.to_global(coins[0] * cote * 0.5), 1.0)
	for i in 4:
		var a: Vector3 = coins[i] * cote * 0.5
		var b: Vector3 = coins[(i + 1) % 4] * cote * 0.5
		var barre := MeshInstance3D.new()
		var m := BoxMesh.new()
		m.size = Vector3(cote + 0.03, 0.03, 0.01) if i % 2 == 0 else Vector3(0.03, cote + 0.03, 0.01)
		m.material = _touche_mat
		barre.mesh = m
		barre.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		barre.position = (a + b) * 0.5
		barre.scale = Vector3(0.001, 1, 1) if i % 2 == 0 else Vector3(1, 0.001, 1)
		_touche.add_child(barre)
		t.tween_property(self, "global_position", _touche.to_global(b), 0.45)
		t.parallel().tween_property(barre, "scale", Vector3.ONE, 0.45)
	# puis elle trace le « E » au milieu, trait par trait : haut (de droite à gauche), la hampe
	# (de haut en bas), le bas (de gauche à droite), et enfin la barre du milieu
	var l := 0.1    # demi-largeur du E
	var hh := 0.14  # demi-hauteur du E
	var traits: Array = [
		[Vector3(l, hh, 0), Vector3(-l, hh, 0)],
		[Vector3(-l, hh, 0), Vector3(-l, -hh, 0)],
		[Vector3(-l, -hh, 0), Vector3(l, -hh, 0)],
		[Vector3(-l, 0, 0), Vector3(l * 0.7, 0, 0)],
	]
	t.tween_property(self, "global_position", _touche.to_global(traits[0][0]), 0.5)
	for i in traits.size():
		var a: Vector3 = traits[i][0]
		var b: Vector3 = traits[i][1]
		if i == 3:   # la barre du milieu : elle saute au départ du trait
			t.tween_property(self, "global_position", _touche.to_global(a), 0.3)
		var barre := MeshInstance3D.new()
		var m := BoxMesh.new()
		var horizontal := absf(b.y - a.y) < 0.001
		m.size = Vector3(absf(b.x - a.x) + 0.035, 0.035, 0.01) if horizontal else Vector3(0.035, absf(b.y - a.y) + 0.035, 0.01)
		m.material = _touche_mat
		barre.mesh = m
		barre.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		barre.position = (a + b) * 0.5
		barre.scale = Vector3(0.001, 1, 1) if horizontal else Vector3(1, 0.001, 1)
		_touche.add_child(barre)
		t.tween_property(self, "global_position", _touche.to_global(b), 0.4)
		t.parallel().tween_property(barre, "scale", Vector3.ONE, 0.4)
	# la luciole se pose à côté de la touche
	t.tween_property(self, "global_position", _touche.to_global(Vector3(cote * 0.85, 0.1, 0)), 0.8)
	t.tween_callback(func() -> void: _dessin = "affiche")
	_touche_tween = t


func _effacer_touche() -> void:
	_dessin = ""
	if _touche_tween:
		_touche_tween.kill()
	if _touche == null:
		return
	var vieux := _touche
	_touche = null
	var t := create_tween()
	t.tween_property(_touche_mat, "albedo_color:a", 0.0, 0.6)
	for c in vieux.get_children():
		if c is Label3D:
			t.parallel().tween_property(c, "modulate:a", 0.0, 0.6)
	t.tween_callback(func() -> void:
		vieux.queue_free()
		_touche_mat = StandardMaterial3D.new())


func _verifier_etape() -> void:
	if _etape == 0 and float(_joueur.get("batterie")) >= 0.95:
		_etape = 1
		_cible = _premiere_lanterne()
		if _cible == null:
			_partir()
	elif _etape == 1 and _cible and bool(_cible.get("allumee")):
		_partir()


## La lanterne allumée, elle monte dans la lumière et s'éteint doucement.
func _partir() -> void:
	_effacer_touche()
	_etape = 2
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	t.tween_property(self, "global_position", global_position + Vector3(0.6, 4.0, -0.4), 4.0)
	t.tween_property(self, "_eclat", 0.0, 4.0).set_delay(1.0)
	t.chain().tween_callback(queue_free)


func _pierre_la_plus_proche(depuis: Vector3) -> Node3D:
	var meilleure: Node3D = null
	var d_min := INF
	for p in get_tree().get_nodes_in_group("pierres_soleil"):
		var d := depuis.distance_to((p as Node3D).global_position)
		if d < d_min:
			d_min = d
			meilleure = p
	return meilleure


func _premiere_lanterne() -> Node3D:
	for l in get_tree().get_nodes_in_group("lanternes"):
		if int(l.get("index_zone")) == 0:
			return l
	return null


## Le sol sous `p`, cherché depuis un peu au-dessus du robot (une terrasse de plus au maximum) :
## partir de plus haut ferait toucher le toit de l'abri.
func _sol(p: Vector3) -> float:
	var y0: float = _joueur.global_position.y
	var haut := Vector3(p.x, y0 + 3.0, p.z)
	var q := PhysicsRayQueryParameters3D.create(haut, haut + Vector3.DOWN * 12.0)
	q.exclude = [_joueur.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	return hit.position.y if hit else y0
