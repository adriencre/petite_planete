extends SceneTree
# Vues de l'île 1 entière dans le noir, quartier par quartier (images i01..i08 dans tools/).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(120.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func isl() -> Node3D:
	return root.get_node_or_null("Island01") as Node3D


func _run() -> void:
	await wait(0.5)
	var rob := isl().get_node("Robot")
	for i in 600:
		if not rob.busy:
			break
		await wait(0.1)
	var loop := root.get_node("Loop")
	loop.set_flag(&"first_bribe")
	loop.set_flag(&"night_known")
	rob.global_position = Vector3(-3.0, 1.6, -2.0)  # au milieu de l'île : la vague part d'ici
	rob.toggle_night()
	await wait(7.0)
	# combien d'objets de l'ombre sont posés en l'air ou enterrés ?
	var bad := 0
	for o in _ombre_objects(isl().get_node("Ombre")):
		var q := PhysicsRayQueryParameters3D.create(o.global_position + Vector3.UP * 2.0, o.global_position + Vector3.DOWN * 3.0)
		q.collision_mask = 1
		q.exclude = [o.get_rid()] if o is CollisionObject3D else []
		var hit := isl().get_world_3d().direct_space_state.intersect_ray(q)
		if hit and absf(hit.position.y - o.global_position.y) > 0.15 and not (o.name in ["CabanePilotis", "Ponton", "PontPecheurs", "IlotCorail", "EscalierGeants"]):
			bad += 1
			print("mal posé : ", o.get_path(), " à ", o.global_position, " sol ", hit.position.y)
	print("objets mal posés : ", bad)
	var cam := Camera3D.new()
	isl().add_child(cam)
	cam.current = true
	var views := [
		["i01_ile_entiere.png", Vector3(0, 40, 30), Vector3(-1, 0, 0), 50.0],
		["i02_village_pins.png", Vector3(-6, 9, 4), Vector3(-12, 0.5, -3), 50.0],
		["i03_grand_place.png", Vector3(1.5, 10, 10), Vector3(1.5, 1.5, 0), 50.0],
		["i04_champs.png", Vector3(4, 10, 20), Vector3(4, 0.5, 8), 50.0],
		["i05_levant.png", Vector3(8, 9, 6), Vector3(14, 0.5, 0), 50.0],
		["i06_hauts.png", Vector3(0, 13, -1), Vector3(0, 3.5, -10), 50.0],
		["i07_ouest.png", Vector3(-12, 10, 8), Vector3(-19, 0.5, -3), 50.0],
	]
	for v in views:
		cam.fov = v[3]
		cam.global_position = v[1]
		cam.look_at(v[2])
		await wait(0.4)
		root.get_texture().get_image().save_png(OUT + v[0])
		print("rendu ", v[0])
	quit()


func _is(n: Node, script_name: String) -> bool:
	var sc: Script = n.get_script()
	return sc != null and sc.resource_path.ends_with(script_name)


func _ombre_objects(n: Node) -> Array:
	var out := []
	for c in n.get_children():
		if _is(c, "ombre_objet.gd"):
			out.append(c)
		elif not _is(c, "lueur_dweller.gd"):
			out.append_array(_ombre_objects(c))
	return out
