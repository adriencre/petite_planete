extends SceneTree
## Vérification sans fenêtre : chaque escalier de l'île 2 se monte ET se descend.
## Un corps de test (même capsule que le robot : rayon 0,4 m, hauteur 1,9 m, accroche au sol 0,3 m)
## marche tout droit à la vitesse du robot depuis le pied de chaque escalier jusqu'au palier, puis redescend.
## Lancer : <godot> --headless --path . -s res://tests/diag_escaliers_ile_02.gd

const LONGUEUR_MARCHES := 4.6   # = terrain_ile_02.py
const PALIER := 1.8
const VITESSE := 3.6            # = joueur.gd
const DIRS := {"^": Vector2i(-1, 0), "v": Vector2i(1, 0), "<": Vector2i(0, -1), ">": Vector2i(0, 1)}


func _init() -> void:
	var racine := (load("res://scenes/ile_02_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	var j := racine.get_node("Joueur") as Node3D
	j.process_mode = Node.PROCESS_MODE_DISABLED
	j.position = Vector3(0, -500, 0)
	var maquette := racine.get_node("Maquette")
	for i in 10:
		await physics_frame
	var corps := CharacterBody3D.new()
	corps.floor_snap_length = 0.3
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.4
	cap.height = 1.9
	cs.shape = cap
	cs.position = Vector3.UP * 0.95
	corps.add_child(cs)
	racine.add_child(corps)
	var echecs := 0
	for e in _escaliers(maquette):
		var d: Vector3 = e.d
		var depart: Vector3 = e.bord - d * (LONGUEUR_MARCHES + 1.5)
		var ok_m := await _marcher(corps, depart + Vector3.UP * (e.zb + 0.05), d, LONGUEUR_MARCHES + PALIER + 2.5, e.zh)
		var ok_d := await _marcher(corps, e.bord + d * (PALIER - 0.3) + Vector3.UP * (e.zh + 0.05), -d, LONGUEUR_MARCHES + PALIER + 1.0, e.zb)
		print("%s escalier %s (%.1f -> %.1f m) : montée %s, descente %s" % ["OK " if ok_m and ok_d else "ÉCHEC", e.nom, e.zb, e.zh, "ok" if ok_m else "BLOQUÉ", "ok" if ok_d else "BLOQUÉ"])
		if not (ok_m and ok_d):
			echecs += 1
	print("RÉSULTAT : %d escalier(s) en échec" % echecs)
	quit(1 if echecs > 0 else 0)


## Fait marcher le corps tout droit sur `distance` m ; vrai s'il arrive à la hauteur `z_cible` (±0,25 m)
## et a parcouru au moins 85 % de la distance.
func _marcher(corps: CharacterBody3D, depart: Vector3, d: Vector3, distance: float, z_cible: float) -> bool:
	corps.global_position = depart
	corps.velocity = Vector3.ZERO
	var g: float = ProjectSettings.get_setting("physics/3d/default_gravity")
	var duree := distance / VITESSE
	var t := 0.0
	while t < duree:
		await physics_frame
		var dt := 1.0 / Engine.physics_ticks_per_second
		corps.velocity.x = d.x * VITESSE
		corps.velocity.z = d.z * VITESSE
		if not corps.is_on_floor():
			corps.velocity.y -= g * dt
		corps.move_and_slide()
		t += dt
	var parcouru := Vector2(corps.global_position.x - depart.x, corps.global_position.z - depart.z).length()
	var ok := absf(corps.global_position.y - z_cible) < 0.25 and parcouru > distance * 0.85
	if not ok:
		print("    arrivé à %s (hauteur visée %.2f, parcouru %.1f / %.1f m)" % [corps.global_position, z_cible, parcouru, distance])
	return ok


## Les escaliers lus dans la carte, comme tools/blender/terrain_ile_02.py.
func _escaliers(maquette: Node) -> Array:
	var lignes: PackedStringArray = str(maquette.carte).strip_edges().split("\n")
	var t: float = maquette.taille_case
	var grille := {}
	for r in lignes.size():
		var jetons := lignes[r].split(" ", false)
		for c in jetons.size():
			var jt: String = jetons[c]
			if jt[0] in ".~":
				continue
			var y: float = maquette.hauteur_estran if jt[0] == "_" else 0.6 + int(jt[0]) * maquette.hauteur_niveau
			grille[Vector2i(r, c)] = {"y": y, "suf": jt.substr(1), "p": Vector3((c - jetons.size() * 0.5 + 0.5) * t, 0, (r - lignes.size() * 0.5 + 0.5) * t)}
	var out := []
	for rc: Vector2i in grille:
		var k: Dictionary = grille[rc]
		for ch in str(k.suf):
			if not DIRS.has(ch):
				continue
			var v: Vector2i = rc + DIRS[ch]
			if not grille.has(v) or grille[v].y <= k.y:
				continue
			var d := Vector3(DIRS[ch].y, 0, DIRS[ch].x)
			out.append({"nom": "%s%d,%d" % [ch, rc.x, rc.y], "d": d, "bord": k.p + d * t * 0.5, "zb": k.y, "zh": grille[v].y})
	return out
