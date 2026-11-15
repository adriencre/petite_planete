extends SceneTree
# Carte vue de dessus de l'île 1 (tools/carte_ile1.png) + positions des repères importants.
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(40.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func _run() -> void:
	await create_timer(1.5).timeout
	var isl := current_scene
	for z in get_nodes_in_group(&"wake_zone"):
		print("ZONE ", z.name, " ", (z as Node3D).global_position, " r=", z.get("radius"))
	for n in ["Abri", "Ombre/Hameau", "Ombre/Compteur", "Blockout/Lanterne1", "Blockout/Lanterne2", "Blockout/Lanterne3",
			"Blockout/GrandeLanterne", "Blockout/LanterneSommet", "Blockout/Cascade", "Blockout/Barque", "Blockout/Coeur",
			"Blockout/Terreau", "Blockout/ArbreRose", "Robot", "Ombre/VeilleuseAbri", "Blockout/NicheCachee", "Blockout/RacinesEscalier"]:
		var nd := isl.get_node_or_null(n) as Node3D
		if nd:
			print("NODE ", n, " ", nd.global_position)
	var gm := isl.get_node("Island") as GridMap
	var cells := gm.get_used_cells()
	var mn := Vector3i(999, 999, 999)
	var mx := Vector3i(-999, -999, -999)
	for c in cells:
		mn = Vector3i(mini(mn.x, c.x), mini(mn.y, c.y), mini(mn.z, c.z))
		mx = Vector3i(maxi(mx.x, c.x), maxi(mx.y, c.y), maxi(mx.z, c.z))
	print("GRID ", mn, " ", mx, " cell=", gm.cell_size)
	# hauteur du sol par case (1 m), en texte, pour placer les maisons
	var rows := []
	for z in range(mn.z, mx.z + 1):
		var line := ""
		for x in range(mn.x, mx.x + 1):
			var top := -1
			for y in range(mx.y, mn.y - 1, -1):
				if gm.get_cell_item(Vector3i(x, y, z)) != -1:
					top = y
					break
			line += "." if top < 0 else str(clampi(top, 0, 9))
		rows.append(line)
	print("HMAP x=", mn.x, ".. z=", mn.z, "..")
	for r in rows:
		print("H ", r)
	var cam := Camera3D.new()
	isl.add_child(cam)
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 52.0
	cam.global_position = Vector3(0, 40, 0)
	cam.look_at(Vector3(0, 0, 0.001), Vector3.FORWARD)
	cam.current = true
	for i in 8:
		await process_frame
	root.get_texture().get_image().save_png(OUT + "carte_ile1.png")
	quit()
