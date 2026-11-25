extends SceneTree
## Vérification sans fenêtre : un corps de la taille du robot (capsule 0,4 × 1,9 m) monte le colimaçon
## du Phare du rez jusqu'à la galerie (pente max 50° comme le robot), puis redescend, en suivant des points de passage.
## Chaque point bloqué est signalé avec sa position (repère local du Phare).
## Lancer : godot --headless --path . -s res://tests/diag_phare.gd

const VITESSE := 3.6            # = joueur.gd
const DELAI := 3.0              # secondes max pour atteindre un point


## Points de passage en coordonnées Blender du Phare (x, y = plan, z = hauteur du sol attendue).
func _parcours() -> Array[Vector3]:
	var p: Array[Vector3] = [Vector3(0, -1.5, .35), Vector3(1.0, 0.9, .35), _polaire(2.45, 46, .35)]
	p.append_array(_arc(2.55, 44, -76, .35, 4.10))
	p.append_array(_arc(2.50, -80, -90, 4.10, 4.10))
	# du palier au milieu du bureau et retour
	p.append_array([Vector3(0.3, -0.6, 4.10), _polaire(2.5, -72, 4.10), _polaire(2.5, -86, 4.10)])
	p.append_array(_arc(2.40, -90, -260, 4.10, 8.95))
	p.append_array(_arc(2.30, -262, -310, 8.95, 8.95))
	p.append_array(_arc(2.1, 50, -128.5, 8.95, 13.62))
	p.append_array([_polaire(2.3, -135, 13.62), _polaire(3.2, -175, 13.62)])
	return p


func _polaire(r: float, angle: float, z: float) -> Vector3:
	return Vector3(r * cos(deg_to_rad(angle)), r * sin(deg_to_rad(angle)), z)


func _arc(r: float, a0: float, a1: float, z0: float, z1: float) -> Array[Vector3]:
	var points: Array[Vector3] = []
	var n := maxi(1, int(absf(a1 - a0) / 10.0))
	for i in range(1, n + 1):
		var t := float(i) / n
		points.append(_polaire(r, lerpf(a0, a1, t), lerpf(z0, z1, t)))
	return points


func _init() -> void:
	var racine := (load("res://scenes/ile_02_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	var j := racine.get_node("Joueur") as Node3D
	j.process_mode = Node.PROCESS_MODE_DISABLED
	j.position = Vector3(0, -500, 0)
	var phare := racine.get_node("Monde/Phare") as Node3D
	for i in 10:
		await physics_frame
	var corps := CharacterBody3D.new()
	corps.floor_snap_length = 0.3
	corps.floor_max_angle = deg_to_rad(50.0)   # = joueur.tscn : les rampes en colimaçon ont des plis à ~45°
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.4
	cap.height = 1.9
	cs.shape = cap
	cs.position = Vector3.UP * 0.95
	corps.add_child(cs)
	racine.add_child(corps)

	var points := _parcours()
	var monde: Array[Vector3] = []
	for b in points:
		monde.append(phare.to_global(Vector3(b.x, b.z, -b.y)))
	corps.global_position = monde[0] + Vector3.UP * 0.05
	var echecs := 0
	print("— Montée")
	echecs += await _suivre(corps, phare, monde, points)
	print("— Descente")
	var retour := monde.duplicate()
	retour.reverse()
	var retour_b := points.duplicate()
	retour_b.reverse()
	echecs += await _suivre(corps, phare, retour, retour_b)
	print("RÉSULTAT : %d point(s) bloqué(s)" % echecs)
	quit(1 if echecs > 0 else 0)


func _suivre(corps: CharacterBody3D, phare: Node3D, monde: Array[Vector3], blender: Array[Vector3]) -> int:
	var g: float = ProjectSettings.get_setting("physics/3d/default_gravity")
	var dt := 1.0 / Engine.physics_ticks_per_second
	var echecs := 0
	for i in monde.size():
		var cible := monde[i]
		var t := 0.0
		var atteint := false
		while t < DELAI:
			await physics_frame
			var ecart := Vector2(cible.x - corps.global_position.x, cible.z - corps.global_position.z)
			if ecart.length() < 0.35:
				atteint = true
				break
			var d := ecart.normalized() * VITESSE
			corps.velocity.x = d.x
			corps.velocity.z = d.y
			if not corps.is_on_floor():
				corps.velocity.y -= g * dt
			corps.move_and_slide()
			t += dt
		var ici := phare.to_local(corps.global_position)
		var b := blender[i]
		var hauteur_ok := absf(ici.y - b.z) < 0.45
		if not atteint or not hauteur_ok:
			echecs += 1
			var heurt := ""
			for k in corps.get_slide_collision_count():
				var c := corps.get_slide_collision(k)
				var pl := phare.to_local(c.get_position())
				var nl := phare.global_basis.inverse() * c.get_normal()
				heurt += " | %s en blender (%.2f, %.2f, z %.2f) normale (%.2f, %.2f, %.2f)" % [(c.get_collider() as Node).name, pl.x, -pl.z, pl.y, nl.x, -nl.z, nl.y]
			print("BLOQUÉ vers le point %d (blender %.2f, %.2f, z %.2f) : robot à blender (%.2f, %.2f, z %.2f)%s [sol %s mur %s plafond %s]"
				% [i, b.x, b.y, b.z, ici.x, -ici.z, ici.y, heurt, corps.is_on_floor(), corps.is_on_wall(), corps.is_on_ceiling()])
			# on replace le corps sur le point pour tester la suite
			corps.global_position = cible + Vector3.UP * 0.1
			corps.velocity = Vector3.ZERO
	return echecs
