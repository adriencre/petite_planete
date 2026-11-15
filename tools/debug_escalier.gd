extends SceneTree
# Trace la montée du robot sur l'escalier des géants (diagnostic).
func _initialize():
	create_timer(60.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()

func _run() -> void:
	await create_timer(0.5).timeout
	var isl := root.get_node("Island01")
	var rob := isl.get_node("Robot") as CharacterBody3D
	for i in 300:
		if not rob.busy: break
		await create_timer(0.1).timeout
	root.get_node("Loop").set_flag(&"first_bribe")
	root.get_node("Loop").set_flag(&"night_known")
	rob.toggle_night()
	await create_timer(5.0).timeout
	rob.global_position = Vector3(-20.0, 0.6, -7.4)
	await create_timer(0.5).timeout
	for i in 400:
		var cam := root.get_viewport().get_camera_3d()
		var d := Vector3(1, 0, 0).rotated(Vector3.UP, -cam.global_rotation.y)
		for a in ["move_left", "move_right", "move_forward", "move_back"]: Input.action_release(a)
		if d.x > 0.0: Input.action_press("move_right", d.x)
		else: Input.action_press("move_left", -d.x)
		if d.z > 0.0: Input.action_press("move_back", d.z)
		else: Input.action_press("move_forward", -d.z)
		await physics_frame
		if i % 25 == 0:
			var col := rob.get_last_slide_collision()
			print(i, " pos ", rob.global_position, " vel ", rob.velocity, " sol ", rob.is_on_floor(), " mur ", rob.is_on_wall(), " touche ", (col.get_collider() as Node).get_path() if col else "-")
	quit()
