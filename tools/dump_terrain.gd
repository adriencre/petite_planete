extends SceneTree
# Relève l'île 1 pour placer le monde de l'ombre : hauteur et type de chaque case, et tout ce qui
# occupe déjà le sol (décors, bâtiments, lanternes…), en rectangles vus de dessus → tools/ile1_terrain.json
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/ile1_terrain.json"
const SKIP := ["Ombre", "Water", "Ciel", "IleLointaine", "Camera", "Robot", "WakeZones", "CameraZones", "Deroulement",
		"WorldEnvironment", "Sun", "Island", "RacinesLumineuses", "Luciole"]


func _initialize() -> void:
	create_timer(30.0).timeout.connect(quit)
	var scene := (load("res://scenes/islands/island_01.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	_run(scene)


func _run(isl: Node3D) -> void:
	await process_frame
	var gm := isl.get_node("Island") as GridMap
	var names := {}
	for id in gm.mesh_library.get_item_list():
		names[id] = gm.mesh_library.get_item_name(id)
	var cols := {}
	for c in gm.get_used_cells():
		var key := "%d,%d" % [c.x, c.z]
		if not cols.has(key) or cols[key][0] < c.y:
			cols[key] = [c.y, names.get(gm.get_cell_item(c), "?")]
	var cells := []
	for key in cols:
		var p: PackedStringArray = key.split(",")
		var top: Vector3 = gm.to_global(gm.map_to_local(Vector3i(int(p[0]), cols[key][0], int(p[1]))))
		cells.append({"x": int(p[0]), "z": int(p[1]), "top": top.y + gm.cell_size.y * 0.5, "item": cols[key][1],
				"cx": top.x, "cz": top.z})
	var obstacles := []
	for child in isl.get_children():
		if child.name in SKIP:
			continue
		_collect(child, obstacles)
	var data := {"cells": cells, "obstacles": obstacles, "cell_size": [gm.cell_size.x, gm.cell_size.y, gm.cell_size.z]}
	var f := FileAccess.open(OUT, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
	print("ok ", cells.size(), " cases, ", obstacles.size(), " obstacles")
	quit()


func _collect(node: Node, out: Array) -> void:
	if node is MeshInstance3D and (node as MeshInstance3D).visible:
		var mi := node as MeshInstance3D
		var box := mi.global_transform * mi.get_aabb()
		if box.size.x < 40.0 and box.size.z < 40.0:
			out.append({"name": str(mi.get_path()).get_slice("Island01/", 1), "x0": box.position.x, "z0": box.position.z,
					"x1": box.end.x, "z1": box.end.z, "y0": box.position.y, "y1": box.end.y})
	for c in node.get_children():
		_collect(c, out)
