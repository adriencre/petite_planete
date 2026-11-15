extends SceneTree
# Les chemins de l'ombre de l'île 1 : le robot les emprunte vraiment (pilotage comme un joueur).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(220.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func press_n() -> void:
	var e := InputEventKey.new(); e.keycode = KEY_N; e.pressed = true; Input.parse_input_event(e)
	await process_frame
	var r := InputEventKey.new(); r.keycode = KEY_N; r.pressed = false; Input.parse_input_event(r)
	await process_frame


func check(label: String, ok: bool) -> void:
	print(("OK    " if ok else "ECHEC ") + label)


func isl() -> Node:
	return root.get_node_or_null("Island01")


func rob() -> CharacterBody3D:
	return isl().get_node("Robot") as CharacterBody3D


func wait_free() -> void:
	for i in 600:
		if isl() and rob() and not rob().busy:
			return
		await wait(0.1)


func shot(name: String) -> void:
	await process_frame
	root.get_texture().get_image().save_png(OUT + name)


func ground(x: float, z: float) -> Vector3:
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, 12, z), Vector3(x, -5, z))
	var hit: Dictionary = (isl() as Node3D).get_world_3d().direct_space_state.intersect_ray(q)
	return (hit.position if hit else Vector3(x, 0.5, z)) + Vector3.UP * 0.05


func release() -> void:
	for a in ["move_left", "move_right", "move_forward", "move_back"]:
		Input.action_release(a)


## Marche vers un point (comme au clavier, relatif à la caméra) pendant au plus `limit` secondes.
func walk_to(target: Vector3, limit: float) -> void:
	var t := 0.0
	while t < limit:
		var to := target - rob().global_position
		to.y = 0.0
		if to.length() < 0.35:
			break
		var cam := root.get_viewport().get_camera_3d()
		var d := to.normalized().rotated(Vector3.UP, -cam.global_rotation.y)
		release()
		if d.x > 0.0: Input.action_press("move_right", d.x)
		else: Input.action_press("move_left", -d.x)
		if d.z > 0.0: Input.action_press("move_back", d.z)
		else: Input.action_press("move_forward", -d.z)
		await physics_frame
		t += 1.0 / 60.0
	release()


func night(on: bool) -> void:
	if rob().night_mode != on:
		await wait_free()
		await press_n()
		await wait(1.0)
		await wait_free()
		await wait(3.0 if on else 2.0)


func _run() -> void:
	await wait(0.5)
	await wait_free()
	root.get_node("Notebook").unlock()
	var loop := root.get_node("Loop")
	loop.set_flag(&"first_bribe")
	loop.set_flag(&"night_known")
	rob().get_node("Battery").level = 100.0

	# 0. antenne allumée : pas de pont (le robot s'arrête au bout du ponton… qui n'existe pas non plus)
	rob().global_position = ground(-18.2, 0.9)
	await wait(1.0)
	await walk_to(Vector3(-27.0, 0.5, 0.9), 4.0)
	await wait(0.5)
	check("antenne allumée : on ne part pas en mer", rob().global_position.x > -19.5)

	# 1. l'escalier des géants
	await night(true)
	rob().global_position = ground(-20.0, -7.4)
	await wait(0.5)
	await walk_to(Vector3(-14.0, 3.5, -7.4), 14.0)
	await wait(0.3)
	print("escalier : robot à ", rob().global_position)
	check("escalier des géants : le robot arrive sur le plateau", rob().global_position.y > 3.2 and rob().global_position.x > -15.0)
	await shot("c01_escalier.png")
	await walk_to(Vector3(-13.4, 3.5, -8.0), 5.0)
	var veilleur = isl().get_node("Ombre/Chemins/Belvedere/Veilleur")
	check("belvédère : le veilleur est là", veilleur.global_position.distance_to(rob().global_position) < 4.0)

	# 2. le pont des pêcheurs, jusqu'à l'îlot
	rob().global_position = ground(-18.2, 0.9)
	await wait(0.5)
	await walk_to(Vector3(-21.0, 0.5, 0.9), 6.0)
	await walk_to(Vector3(-26.8, 0.5, 0.9), 14.0)
	await wait(0.3)
	print("pont : robot à ", rob().global_position)
	check("pont des pêcheurs : le robot arrive sur l'îlot", rob().global_position.x < -25.6 and rob().global_position.y > 0.3)
	await shot("c02_ilot.png")
	var guet = isl().get_node("Ombre/Chemins/Guetteur")
	var talked := false
	for i in 40:
		await wait(0.2)
		if guet._talk_spot.enabled and guet.global_position.distance_to(rob().global_position) < 2.5:
			guet._talk_spot.interact(rob())
			talked = true
			break
		await walk_to(guet.global_position, 0.3)
	await wait(0.5)
	await wait_free()
	check("îlot : le guetteur parle du Phare (carnet)", talked and root.get_node("Notebook").has_parole(&"guet_phare"))

	# 3. on rallume sur l'îlot : il reste sous les pieds tant qu'on ne l'a pas quitté
	await night(false)
	await wait(2.0)
	check("rallumé sur l'îlot : le robot ne tombe pas", rob().global_position.y > 0.3)
	var ilot = isl().get_node("Ombre/Chemins/IlotCorail")
	check("l'îlot est invisible mais tient encore", ilot._reveal < 0.05 and ilot.collision_layer != 0)
	await shot("c03_rallume_ilot.png")
	quit()
