extends SceneTree
var SPEECH: GDScript
# Phase E : paroles de lumière, kit d'habitat, habitantes. Pose le kit sur l'île 1 (sans l'enregistrer).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(100.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
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


func wait_free() -> void:
	for i in 600:
		if isl() and not rob().busy:
			return
		await wait(0.1)


func shot(name: String) -> void:
	await process_frame
	root.get_texture().get_image().save_png(OUT + name)


func ground(x: float, z: float) -> Vector3:
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, 12, z), Vector3(x, -5, z))
	var hit: Dictionary = (isl() as Node3D).get_world_3d().direct_space_state.intersect_ray(q)
	return hit.position if hit else Vector3(x, 0.5, z)


func put(path: String, x: float, z: float) -> Node3D:
	var n: Node3D = (load(path) as PackedScene).instantiate()
	isl().add_child(n)
	n.global_position = ground(x, z)
	return n


func _run() -> void:
	SPEECH = load("res://scripts/lueurs/lueur_speech.gd")
	await wait(0.5)
	await wait_free()
	nb().unlock()
	var bat = rob().get_node("Battery")

	# le kit, posé près de la première lanterne (éteinte)
	var house := put("res://assets/ombre/maisons/maison_champignon.tscn", -8.0, 10.6)
	put("res://assets/ombre/decor/potager.tscn", -6.6, 11.3)
	put("res://assets/ombre/decor/puits.tscn", -9.2, 8.2)
	var threads := put("res://assets/ombre/decor/corde_linge.tscn", -9.6, 11.6)
	threads.rotation.y = 0.4
	# une maison effondrée dans le halo de la pierre-soleil (zone éveillée = désert gris)
	var dead := put("res://assets/ombre/maisons/maison_champignon.tscn", -13.2, 7.8)
	dead.collapsed = true
	# une petite habitante peureuse, qui parle
	var petite: Node3D = (load("res://assets/lueurs/habitant.tscn") as PackedScene).instantiate()
	petite.home = house
	isl().add_child(petite)
	petite.global_position = house.global_position + Vector3(0.8, 0.6, 0.4)
	var speech: Node3D = SPEECH.new()
	speech.text = "Il revient. Il revient toujours."
	speech.id = &"test_revient"
	speech.height = 0.5
	petite.add_child(speech)
	# un héron (sans peur), pour voir la forme
	var heron: Node3D = (load("res://assets/lueurs/habitant.tscn") as PackedScene).instantiate()
	heron.form = 2
	heron.shy = false
	heron.wander_radius = 0.3
	isl().add_child(heron)
	heron.global_position = ground(-5.4, 9.6)
	# une parole seule (sans habitante), pour les bribes
	var lone: Node3D = SPEECH.new()
	lone.text = "Trop de lumière sur toi. Va-t'en, Petit-Jour."
	lone.id = &"test_bribes"
	isl().add_child(lone)
	lone.global_position = ground(-11.0, 11.5) + Vector3.UP * 0.3

	# 1. antenne allumée, batterie pleine : on ne voit rien
	rob().global_position = ground(-6.0, 8.6) + Vector3.UP * 0.05
	bat.level = 100.0
	await wait(1.0)
	await shot("e01_lumiere.png")
	check("antenne allumée : la petite ne parle pas", not nb().has_parole(&"test_revient"))

	# 2. batterie basse, près de la parole seule : des bribes, pas recopiées
	rob().global_position = ground(-10.2, 10.8) + Vector3.UP * 0.05
	bat.level = 7.0
	var heard := []
	lone.said.connect(func(full: bool) -> void: heard.append(full))
	for i in 30:
		await wait(0.2)
		bat.level = 7.0
		if not heard.is_empty():
			break
	await wait(0.6)
	await shot("e02_bribes.png")
	check("batterie basse : bribes entendues", heard.size() > 0 and heard[0] == false)
	check("les bribes ne vont pas dans le carnet", not nb().has_parole(&"test_bribes"))

	# 3. mode nuit près de la maison, immobile : la petite se cache, puis ressort et parle
	bat.level = 60.0
	rob().global_position = ground(-6.0, 9.4) + Vector3.UP * 0.05
	await wait(0.3)
	await wait_free()
	await press_n()
	await wait(1.0)
	await wait_free()
	check("mode nuit", rob().night_mode)
	await wait(0.3)
	await shot("e03_nuit_kit.png")
	var spoke := false
	for i in 120:
		await wait(0.2)
		if nb().has_parole(&"test_revient"):
			spoke = true
			break
	check("immobile dans le noir : elle ressort et parle (recopié au carnet)", spoke)
	await wait(0.3)
	await shot("e04_parole.png")

	# 4. on bouge : elle rentre se cacher
	rob().velocity = Vector3(1.0, 0, 0)
	Input.action_press("move_left")
	await wait(1.0)
	Input.action_release("move_left")
	check("en bougeant, elle se cache (%.2f)" % petite._hidden, petite._hidden > 0.5)

	# 5. le carnet : section Paroles
	nb().open()
	await wait(0.4)
	var pages: Array = nb()._pages()
	for i in pages.size():
		if pages[i].has("paroles"):
			nb()._spread = i / 2
	nb()._build_spread()
	await wait(0.4)
	await shot("e05_carnet_paroles.png")
	quit()
