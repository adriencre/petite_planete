extends SceneTree
# Phase F : île 1 côté ombre, 1re moitié (hameau + 1re bribe, cicatrices, Pouponnière, Compteur).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(150.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
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
	var bat = rob().get_node("Battery")
	var hamlet = isl().get_node("Ombre/Hameau")

	# 1. le hameau : batterie basse → la première bribe (un moment)
	rob().global_position = ground(-9.6, 1.6)
	bat.level = 8.0
	var started := false
	for i in 30:
		await wait(0.2)
		bat.level = 8.0
		if rob().busy:
			started = true
			break
	check("1re bribe : le moment se déclenche près du hameau", started)
	await wait(5.5)
	await shot("f01_premiere_bribe.png")
	await wait_free()
	check("1re bribe : mémorisée", loop().has_flag(&"first_bribe"))
	bat.level = 80.0

	# 2. cicatrices : la grande lanterne éteint le hameau, la reprendre le retisse
	var big = isl().get_node("Blockout/GrandeLanterne")
	big.light_up()
	await wait(4.0)
	var house = hamlet.get_node("Maison1")
	check("grande lanterne allumée : la maison s'effondre", house.collapsed)
	await press_n()
	await wait(1.0)
	await wait_free()
	await shot("f02_cicatrice.png")
	big.wake_zone.fall_asleep(1.0)
	await wait(2.5)
	check("lumière reprise : la maison se retisse", not house.collapsed)
	await wait(3.0)
	await shot("f03_retisse.png")

	# 3. la Pouponnière : dans l'abri, éteint et immobile → une petite ressort et parle
	rob().global_position = isl().get_node("Abri/RobotStart").global_position
	rob().velocity = Vector3.ZERO
	var heard := false
	for i in 80:
		await wait(0.2)
		if nb().has_parole(&"pouponniere_bouche"):
			heard = true
			break
	check("Pouponnière : « La Bouche est chaude… » (carnet)", heard)
	await shot("f04_pouponniere.png")

	# 4. le Compteur : après une mort, il pose une pierre et dit « Encore un. »
	loop().count += 1
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	await wait(1.0)
	await wait_free()
	bat = rob().get_node("Battery")
	var counter = isl().get_node("Ombre/Compteur")
	check("le Compteur a une pierre dans le bec", counter._pending != null)
	rob().global_position = ground(-17.4, -4.2)
	bat.level = 60.0
	await press_n()
	await wait(1.0)
	await wait_free()
	var said := false
	for i in 60:
		await wait(0.2)
		if nb().has_parole(&"compteur_encore_un"):
			said = true
			break
	check("Compteur : la pierre est posée", counter._pending == null)
	check("Compteur : « Encore un. »", said)
	await shot("f05_compteur.png")
	quit()
