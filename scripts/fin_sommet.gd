extends Node3D
## La fin de l'île 1 (ILE_01_REVEIL.md §5, étape 6) : quand la grande lanterne du sommet s'allume, toutes les
## lanternes s'allument en cascade, la brume recule, le soleil se couche ; la caméra s'élève sur l'île
## illuminée, passe par la barque, puis revient au robot tourné vers le Phare éteint et sa bouée.
## Pas de fondu : après le plan, on reprend la main (la barque attend dans la crique).
## Le Phare au loin existe toujours (il est seulement caché par la brume) : on le bâtit ici.

@export var soleil: DirectionalLight3D
@export var environnement: WorldEnvironment
## Direction du Phare depuis l'île (l'abri lui tourne le dos : il est à l'est).
@export var direction_phare: Vector3 = Vector3(1.0, 0.0, -0.12)
@export var distance_phare: float = 170.0
## Test : au lancement, place le robot au sommet et joue la fin tout de suite (passer le réveil avec Entrée).
@export var tester_au_demarrage: bool = false
@export_group("Cinématique")
## Écart (s) entre deux lanternes qui s'allument d'elles-mêmes, en cascade depuis le sommet.
@export var cascade: float = 0.7
## Durée de la montée de la caméra jusqu'au plan de toute l'île.
@export var duree_montee: float = 8.0
## Durée du glissé vers la barque, puis du retour vers le Phare.
@export var duree_barque: float = 5.0
@export var duree_phare: float = 6.0
## Combien de temps on regarde le Phare.
@export var duree_plan: float = 8.0
@export_group("Coucher de soleil")
## Combien de fois plus loin on voit, une fois l'île entière réveillée.
@export var recul_final: float = 22.0
@export var couleur_soleil: Color = Color(1.0, 0.6, 0.42)
@export var couleur_brume: Color = Color(1.0, 0.76, 0.72)
@export var couleur_ambiance: Color = Color(1.0, 0.74, 0.76)

var _fait := false
var _joueur: CharacterBody3D
var _sommet: Node
var _bouee_mat := StandardMaterial3D.new()
var _bouee_lumiere := OmniLight3D.new()
var _t := 0.0
var _flou_initial := 11.0


func _ready() -> void:
	_batir_phare()
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	# la lanterne de la fin : la dernière à allumer (le rang le plus haut), la grande lanterne du sommet
	for l in get_tree().get_nodes_in_group("lanternes"):
		if _sommet == null or int(l.get("rang")) > int(_sommet.get("rang")):
			_sommet = l
	if tester_au_demarrage and _sommet and _joueur:
		while bool(_joueur.get("cinematique")):
			await get_tree().process_frame
		await get_tree().create_timer(0.5).timeout
		var s: Vector3 = (_sommet as Node3D).global_position
		_joueur.global_position = s + Vector3(2.5, 0.3, 0.5)
		await get_tree().create_timer(1.0).timeout
		_fait = true
		_fin()


func _process(delta: float) -> void:
	_t += delta
	# la bouée du port du Phare : une lueur qui bat lentement, toujours
	var battement := pow(0.5 + 0.5 * sin(_t * 2.2), 3.0)
	_bouee_mat.albedo_color = Color(1.0, 0.55, 0.3) * (0.6 + 3.0 * battement)
	_bouee_lumiere.light_energy = 0.5 + 2.5 * battement
	if not _fait and _sommet and bool(_sommet.get("allumee")) and _joueur and not bool(_joueur.get("cinematique")):
		_fait = true
		_fin()


# ---------------------------------------------------------------- la cinématique de fin

## 1) tout s'allume en cascade depuis le sommet ; 2) la caméra s'élève jusqu'au plan de toute l'île
## illuminée ; 3) elle glisse vers la barque dans la crique ; 4) elle revient au robot, au bord du
## sommet, tourné vers le Phare au couchant ; 5) on reprend la main.
func _fin() -> void:
	_joueur.set("cinematique", true)
	var dir := Vector3(direction_phare.x, 0, direction_phare.z).normalized()
	var cote := dir.cross(Vector3.UP).normalized()
	var phare: Vector3 = _position_phare()
	var sommet: Vector3 = (_sommet as Node3D).global_position

	# --- 1) tout s'allume : chaque lanterne éteinte, de la plus proche du sommet à la plus loin
	var eteintes: Array = []
	for l in get_tree().get_nodes_in_group("lanternes"):
		if not bool(l.get("allumee")) and l.has_method("allumer_seule"):
			eteintes.append(l)
	eteintes.sort_custom(func(a, b): return sommet.distance_to(a.global_position) < sommet.distance_to(b.global_position))
	for i in eteintes.size():
		get_tree().create_timer(0.8 + i * cascade).timeout.connect(eteintes[i].allumer_seule.bind(1.8))

	# l'île entière s'éveille : la brume recule loin, ce qui en reste s'éclaircit, le soleil se couche
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	var zone := get_tree().get_first_node_in_group("zone_endormie")
	if zone:
		var depart: float = zone.get("recul_max")
		t.tween_method(func(v: float) -> void:
			zone.set("recul_max", v)
			zone.call("_reculer_brouillard"), depart, recul_final, duree_montee + 2.0)
	for v in get_tree().get_nodes_in_group("brume_ile"):
		var m: Material = (v as FogVolume).material if v is FogVolume else (v as GeometryInstance3D).material_override
		if m is ShaderMaterial:
			var nom := "densite" if v is FogVolume else "opacite"
			var avant = (m as ShaderMaterial).get_shader_parameter(nom)
			if avant == null:
				avant = 0.2 if v is FogVolume else 0.7
			t.tween_method(func(x: float) -> void: (m as ShaderMaterial).set_shader_parameter(nom, x), float(avant), float(avant) * 0.2, duree_montee + 2.0)
	var d_soleil := duree_montee + duree_barque + 4.0
	if soleil:
		var vise := Basis.looking_at(Vector3(-dir.x, -0.09, -dir.z).normalized())   # bas sur l'horizon, côté Phare
		t.tween_property(soleil, "quaternion", vise.get_rotation_quaternion(), d_soleil)
		t.tween_property(soleil, "light_color", couleur_soleil, d_soleil)
		t.tween_property(soleil, "light_energy", 1.7, d_soleil)
	if environnement and environnement.environment:
		var env := environnement.environment
		t.tween_property(env, "fog_light_color", couleur_brume, d_soleil)
		t.tween_property(env, "ambient_light_color", couleur_ambiance, d_soleil)
		var ciel := env.sky.sky_material as ShaderMaterial if env.sky else null
		if ciel:
			_teinte_ciel(t, ciel, "couleur_horizon", Color(1.0, 0.6, 0.42), d_soleil)
			_teinte_ciel(t, ciel, "couleur_milieu", Color(0.96, 0.56, 0.62), d_soleil)
			_teinte_ciel(t, ciel, "couleur_haut", Color(0.46, 0.4, 0.74), d_soleil)
		# le flou de lointain empêcherait les grands plans : on l'écarte pendant la cinématique
		var attr := environnement.camera_attributes as CameraAttributesPractical
		if attr:
			_flou_initial = attr.dof_blur_far_distance
			t.tween_property(attr, "dof_blur_far_distance", 400.0, 2.0)

	# le robot lève la tête vers sa lanterne, puis s'avance vers le bord, face au Phare
	_joueur.set("regard_cible", sommet + Vector3.UP * 3.0)
	var bord: Vector3 = sommet + dir * 4.5
	bord.y = _joueur.global_position.y
	var marche := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	marche.tween_interval(2.0)
	marche.tween_callback(func() -> void: _joueur.set("regard_cible", phare + Vector3.UP * 15.0))
	marche.tween_property(_joueur, "global_position", bord, clampf(_joueur.global_position.distance_to(bord), 1.5, 4.5))

	# --- 2) la caméra quitte le robot et s'élève : toute l'île illuminée
	var centre := _centre_ile()
	_joueur.set("cine_position", centre + Vector3(-4.0, 27.0, 34.0))
	_joueur.set("cine_cible", centre + Vector3.UP * 2.0)
	var monte := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	monte.tween_interval(1.2)
	monte.tween_property(_joueur, "cine_melange", 1.0, duree_montee)
	await monte.finished
	await get_tree().create_timer(2.5).timeout

	# --- 3) elle glisse vers la crique : la barque attend
	var barque := get_tree().get_first_node_in_group("barque_qui_flotte") as Node3D
	if barque:
		var b: Vector3 = barque.global_position
		var depuis_ile := Vector3(b.x - centre.x, 0, b.z - centre.z).normalized()
		var vers_b := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		vers_b.tween_property(_joueur, "cine_position", b + depuis_ile * 9.0 + Vector3.UP * 7.0 + depuis_ile.cross(Vector3.UP) * 5.0, duree_barque)
		vers_b.tween_property(_joueur, "cine_cible", b + Vector3.UP * 0.5, duree_barque)
		await vers_b.finished
		await get_tree().create_timer(3.0).timeout

	# --- 4) retour au sommet : derrière le robot, au bord, tourné vers le Phare
	var p: Vector3 = _joueur.global_position
	var vers_phare := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	vers_phare.tween_property(_joueur, "cine_position", p - dir * 2.2 + cote * 1.6 + Vector3.UP * 1.9, duree_phare)
	vers_phare.tween_property(_joueur, "cine_cible", p + dir * 40.0 + Vector3.UP * 4.0, duree_phare)
	await vers_phare.finished
	# le robot le dessine dans son carnet
	var carnet := get_tree().get_first_node_in_group("carnet")
	if carnet:
		carnet.call("noter_dessin", "Le Phare, vu du sommet")
	await get_tree().create_timer(duree_plan).timeout

	# --- 5) la caméra revient ; on reprend la main, au coucher du soleil
	var retour := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	retour.tween_property(_joueur, "cine_melange", 0.0, 3.5)
	if environnement and environnement.camera_attributes is CameraAttributesPractical:
		retour.parallel().tween_property(environnement.camera_attributes, "dof_blur_far_distance", _flou_initial, 3.5)
	await retour.finished
	_joueur.set("cinematique", false)


## Le centre de l'île : la moyenne des lanternes (on ne vise pas la mer).
func _centre_ile() -> Vector3:
	var somme := Vector3.ZERO
	var n := 0
	for l in get_tree().get_nodes_in_group("lanternes"):
		somme += (l as Node3D).global_position
		n += 1
	return somme / n if n > 0 else Vector3.ZERO


func _teinte_ciel(t: Tween, ciel: ShaderMaterial, nom: String, vers: Color, duree: float) -> void:
	var v = ciel.get_shader_parameter(nom)
	var depuis: Color = Color(v.x, v.y, v.z) if v is Vector3 else (v as Color if v is Color else vers)
	t.tween_method(func(c: Color) -> void: ciel.set_shader_parameter(nom, Vector3(c.r, c.g, c.b)), depuis, vers, duree)


# ---------------------------------------------------------------- le Phare au loin

func _position_phare() -> Vector3:
	return Vector3(direction_phare.x, 0, direction_phare.z).normalized() * distance_phare


## Une silhouette simple : un rocher, la tour, la salle de la lentille (éteinte), le toit.
## Couleur sombre et mate : à contre-jour du couchant, on n'en voit que la forme.
func _batir_phare() -> void:
	var racine := Node3D.new()
	racine.name = "PhareAuLoin"
	racine.position = _position_phare()
	add_child(racine)
	var sombre := StandardMaterial3D.new()
	sombre.albedo_color = Color(0.3, 0.26, 0.38)
	sombre.roughness = 1.0
	var pierre := StandardMaterial3D.new()
	pierre.albedo_color = Color(0.36, 0.32, 0.42)
	pierre.roughness = 1.0
	_piece(racine, pierre, 26.0, 34.0, 8.0, Vector3(0, -1.0, 0), 7)       # le rocher
	_piece(racine, pierre, 12.0, 18.0, 5.0, Vector3(-6, 5.0, 4), 6)
	_piece(racine, sombre, 2.6, 3.6, 24.0, Vector3(0, 15.0, 0), 8)        # la tour
	_piece(racine, sombre, 3.4, 3.4, 0.8, Vector3(0, 27.4, 0), 8)         # la galerie
	_piece(racine, sombre, 2.4, 2.4, 3.2, Vector3(0, 29.4, 0), 8)         # la salle de la lentille, éteinte
	_piece(racine, sombre, 0.0, 3.0, 3.0, Vector3(0, 32.5, 0), 8)         # le toit
	# la bouée de son port : une petite lueur orange qui bat, qu'on voit à travers la brume
	var bouee := MeshInstance3D.new()
	var s := SphereMesh.new()
	s.radius = 1.6
	s.height = 3.2
	_bouee_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_bouee_mat.disable_fog = true
	s.material = _bouee_mat
	bouee.mesh = s
	bouee.position = Vector3(-50, 2.0, 16)   # devant le rocher, côté île
	racine.add_child(bouee)
	_bouee_lumiere.light_color = Color(1.0, 0.55, 0.3)
	_bouee_lumiere.omni_range = 14.0
	_bouee_lumiere.position = bouee.position + Vector3.UP * 1.5
	racine.add_child(_bouee_lumiere)


func _piece(parent: Node3D, mat: Material, r_haut: float, r_bas: float, haut: float, pos: Vector3, cotes: int) -> void:
	var mi := MeshInstance3D.new()
	var c := CylinderMesh.new()
	c.top_radius = r_haut
	c.bottom_radius = r_bas
	c.height = haut
	c.radial_segments = cotes
	c.rings = 1
	c.material = mat
	mi.mesh = c
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
