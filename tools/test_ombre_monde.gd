extends SceneTree
# La ville de l'ombre de l'île 1 : transformation, collisions, habitants, conversations (E), cicatrices.
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(200.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
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


func rob() -> Node:
	return isl().get_node("Robot")


func nb() -> Node:
	return root.get_node("Notebook")


func loop() -> Node:
	return root.get_node("Loop")


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


func _run() -> void:
	await wait(0.5)
	await wait_free()
	nb().unlock()
	loop().set_flag(&"first_bribe")  # pas de scène de la première bribe dans ce test
	var m1 = isl().get_node("Ombre/Hameau/Maison1")
	var anc = isl().get_node("Ombre/Village/Ancienne")
	var bat = rob().get_node("Battery")
	bat.level = 90.0

	# 1. antenne allumée : rien
	rob().global_position = ground(-15.6, -0.2)
	await wait(1.5)
	check("antenne allumée : la ville est invisible", m1._reveal < 0.05)
	check("antenne allumée : pas de collision", m1.collision_layer == 0)

	# 2. antenne éteinte : l'île se transforme
	await press_n()
	await wait(1.0)
	await wait_free()
	await wait(4.0)
	check("dans le noir : la ville apparaît", m1._reveal > 0.95)
	check("dans le noir : ses collisions existent", m1.collision_layer != 0)
	var env := (isl().get_node("WorldEnvironment") as WorldEnvironment).environment
	check("dans le noir : le ciel passe à la nuit", env.background_color.v < 0.25)
	await shot("o01_ville_nuit.png")

	# 3. parler à l'ancienne : on reste immobile et éteint, elle ressort, on appuie sur E
	rob().velocity = Vector3.ZERO
	var spoke := false
	var tour := isl().get_node("Ombre/Village/TourAncienne") as Node3D
	var devant: Vector3 = tour.global_transform * Vector3(0, 0, 2.6)
	rob().global_position = ground(devant.x, devant.z)
	for i in 80:
		await wait(0.2)
		rob().velocity = Vector3.ZERO
		if anc._talk_spot.enabled:
			spoke = true
			break
	check("l'ancienne accepte de parler (robot immobile, éteint)", spoke)
	if spoke:
		await wait_free()
		anc._talk_spot.interact(rob())
		await wait(0.5)
		await wait_free()
	check("conversation : « Tu restes éteint… » (carnet)", nb().has_parole(&"anc_eteint"))
	check("conversation : l'info sur les cendres est notée", loop().has_flag(&"sait_cicatrices"))
	await shot("o02_conversation.png")
	check("conversation suivante choisie", anc._pick() != null and anc._pick().id == &"ancienne_2")

	# 4. après la bascule, elle parle de la Pouponnière
	loop().set_flag(&"bascule")
	check("après la bascule : elle parle de la veilleuse", anc._pick() != null and anc._pick().id == &"ancienne_3")
	loop().flags.erase(&"bascule")

	# 5. cicatrices : la grande lanterne réduit la maison en cendre
	isl().get_node("Blockout/GrandeLanterne").light_up()
	await wait(5.0)
	check("grande lanterne : la maison du hameau est en cendre", m1.collapsed and m1._ash > 0.9)
	await shot("o03_cendres.png")

	# 6. on rallume : la ville disparaît
	await wait_free()
	await press_n()
	await wait(1.0)
	await wait_free()
	await wait(2.0)
	check("antenne rallumée : la ville disparaît", m1._reveal < 0.05 and m1.collision_layer == 0)
	quit()
