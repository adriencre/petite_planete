extends SceneTree
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"
var t0 := 0


func _initialize():
	create_timer(60.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func press(action: String) -> void:
	var e := InputEventAction.new(); e.action = action; e.pressed = true; Input.parse_input_event(e)
	await process_frame
	var r := InputEventAction.new(); r.action = action; r.pressed = false; Input.parse_input_event(r)
	await process_frame


func check(label: String, ok: bool) -> void:
	print(("OK    " if ok else "ECHEC ") + label)


func isl() -> Node:
	return root.get_node_or_null("Island01")


func rob() -> Node:
	return isl().get_node("Robot")


func wait_free() -> void:
	for i in 600:
		if isl() and not rob().busy:
			return
		await wait(0.1)


# marche vers un point (caméra alignée sur les axes)
func walk_to(target: Vector2) -> void:
	var cam = isl().get_node("Camera")
	cam.yaw_degrees = 0.0
	for i in 300:
		var p: Vector3 = rob().global_position
		var d := target - Vector2(p.x, p.z)
		if d.length() < 0.3:
			break
		for a in ["move_left", "move_right", "move_forward", "move_back"]:
			Input.action_release(a)
		if d.x < -0.15: Input.action_press("move_left")
		if d.x > 0.15: Input.action_press("move_right")
		if d.y < -0.15: Input.action_press("move_forward")
		if d.y > 0.15: Input.action_press("move_back")
		await wait(0.05)
	for a in ["move_left", "move_right", "move_forward", "move_back"]:
		Input.action_release(a)
	cam.yaw_degrees = 45.0


# marche en diagonale vers le nord-ouest (caméra alignée)
func walk_nw(sec: float) -> void:
	var cam = isl().get_node("Camera")
	cam.yaw_degrees = 0.0
	Input.action_press("move_forward")
	Input.action_press("move_left")
	await wait(sec)
	Input.action_release("move_forward")
	Input.action_release("move_left")
	cam.yaw_degrees = 45.0


func _run() -> void:
	await wait(0.5)
	await wait_free()
	var bodies = isl().get_node("AnciensCorps")
	check("un ancien corps est déjà là au premier réveil (%d)" % bodies.get_child_count(), bodies.get_child_count() == 1)
	check("l'atelier n'a plus de dessin d'enfant", isl().get_node_or_null("Atelier/DessinEnfant") == null)
	check("l'atelier a son étagère de corps", isl().get_node_or_null("Atelier/Etagere") != null)
	# A. batterie pleine, sans la pierre cachée : la brume épaisse l'emporte
	var bat = rob().get_node("Battery")
	rob().global_position = Vector3(-15.5, 0.55, -3.2)
	bat.level = 100.0
	await wait(0.4)
	root.get_texture().get_image().save_png(OUT + "i01_entree.png")
	await walk_to(Vector2(-20.6, -7.6))
	await wait(0.6)
	root.get_texture().get_image().save_png(OUT + "i02_brume_epaisse.png")
	print("   vision %.2f, batterie %.0f" % [bat.vision(), bat.level])
	for z in get_nodes_in_group(&"wake_zone"):
		if z.current_radius > 0.01: print("      zone éveillée ", z.get_path(), " r=", z.current_radius)
	check("la brume épaisse vide vite la batterie", bat.level < 85.0)
	# loin du halo de la pierre cachée
	rob().global_position = Vector3(-22.0, 0.55, -9.9)
	bat.level = 100.0
	await wait(0.4)
	check("on devine les Lueurs dans la brume épaisse (%.2f)" % bat.vision(), bat.vision() > 0.3)
	# B. la pierre cachée
	var hidden = isl().get_node("Blockout/PierreSoleilCachee")
	rob().global_position = hidden.global_position + Vector3(-0.9, 0.05, 0.3)
	bat.level = 60.0
	await wait(0.6)
	await press("interact")
	await wait(1.0)
	await wait_free()
	await wait(0.5)
	check("pierre cachée : batterie pleine (%.0f)" % bat.level, bat.level > 95.0)
	root.get_texture().get_image().save_png(OUT + "i03_pierre_cachee.png")
	# C. jusqu'à la barque
	for wp in [Vector2(-20.6, -8.6), Vector2(-21.5, -9.5), Vector2(-23.0, -11.2), Vector2(-23.8, -12.6)]:
		await walk_to(wp)
	print("   arrivé en %s, batterie %.0f" % [str(rob().global_position.snapped(Vector3.ONE * 0.1)), bat.level])
	var boat = isl().get_node("Blockout/Barque")
	check("la barque est à flot", boat.floating)
	root.get_texture().get_image().save_png(OUT + "i04_barque.png")
	await press("interact")
	await wait(1.5)
	check("le robot monte dans la barque", boat.seat.get_child_count() > 0)
	await wait(4.0)
	check("le phare de l'île 2 s'allume au départ", isl().get_node("IleLointaine/Lumiere").answered)
	root.get_texture().get_image().save_png(OUT + "i05_depart_phare.png")
	await wait(3.0)
	root.get_texture().get_image().save_png(OUT + "i06_depart_large.png")
	quit()
