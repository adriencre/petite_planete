extends SceneTree
# Rendu de la ville de l'ombre dans l'île 1 (images w01..w08 dans tools/).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(120.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func isl() -> Node:
	return root.get_node_or_null("Island01")


func rob() -> Node:
	return isl().get_node("Robot")


func press_n() -> void:
	var e := InputEventKey.new(); e.keycode = KEY_N; e.pressed = true; Input.parse_input_event(e)
	await process_frame
	var r := InputEventKey.new(); r.keycode = KEY_N; r.pressed = false; Input.parse_input_event(r)
	await process_frame


func wait_free() -> void:
	for i in 600:
		if isl() and rob() and not rob().busy:
			return
		await wait(0.1)


func shot(name: String) -> void:
	await process_frame
	await process_frame
	root.get_texture().get_image().save_png(OUT + name)
	print("rendu ", name)


func ground(x: float, z: float) -> Vector3:
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, 12, z), Vector3(x, -5, z))
	var hit: Dictionary = (isl() as Node3D).get_world_3d().direct_space_state.intersect_ray(q)
	return (hit.position if hit else Vector3(x, 0.5, z)) + Vector3.UP * 0.05


func free_cam(from: Vector3, to: Vector3, fov := 40.0) -> Camera3D:
	var cam := Camera3D.new()
	isl().add_child(cam)
	cam.fov = fov
	cam.global_position = from
	cam.look_at(to)
	cam.current = true
	return cam


func _run() -> void:
	await wait(0.5)
	await wait_free()
	root.get_node("Notebook").unlock()
	rob().global_position = ground(-12.6, 2.6)
	rob().get_node("Battery").level = 90.0
	await wait(2.0)
	await shot("w01_jour.png")
	await press_n()
	await wait(1.5)
	await wait_free()
	await wait(5.0)
	await shot("w02_nuit_robot.png")
	print("vision ", rob().get_node("Battery").vision())
	var hameau := isl().get_node("Ombre/Hameau") as Node3D
	var m1 := isl().get_node("Ombre/Hameau/Maison1")
	print("Maison1 reveal ", m1._reveal, " collision ", (m1 as CollisionObject3D).collision_layer)
	var anc := isl().get_node("Ombre/Village/Ancienne") as Node3D
	print("Ancienne ", anc.global_position, " cachee ", anc.is_hidden())
	await wait(3.0)
	print("Ancienne ensuite ", anc.global_position)
	# vues libres
	var game_cam := root.get_viewport().get_camera_3d()
	var c := free_cam(Vector3(-2.0, 15.0, 13.0), Vector3(-12.5, 0.5, 0.0), 45.0)
	await wait(0.3)
	await shot("w03_ville_haut.png")
	c.global_position = Vector3(-8.0, 4.5, 7.5)
	c.look_at(Vector3(-12.0, 1.0, -0.5))
	await wait(0.3)
	await shot("w04_place.png")
	c.global_position = Vector3(-12.5, 4.0, 4.0)
	c.look_at(Vector3(-17.0, 1.5, -2.0))
	await wait(0.3)
	await shot("w05_tour_ancienne.png")
	c.global_position = Vector3(-12.0, 4.5, -1.5)
	c.look_at(Vector3(-16.5, 1.0, -6.5))
	await wait(0.3)
	await shot("w06_crique.png")
	c.global_position = Vector3(-6.0, 9.0, 13.0)
	c.look_at(Vector3(-11.0, 0.5, 5.0))
	await wait(0.3)
	await shot("w07_sud.png")
	c.queue_free()
	if game_cam:
		game_cam.current = true
	# retour à la lumière : le village disparaît
	await wait_free()
	await press_n()
	await wait(1.0)
	await wait_free()
	await wait(2.0)
	print("après rallumage : Maison1 reveal ", m1._reveal, " collision ", (m1 as CollisionObject3D).collision_layer)
	await shot("w08_rallume.png")
	quit()
