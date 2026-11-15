extends SceneTree
# Étape 15 : carnet v3 (carte + anciens corps, bestiaire, journal de la Gardienne).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(90.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
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


func nb() -> Node:
	return root.get_node("Notebook")


func wait_free() -> void:
	for i in 600:
		if isl() and not rob().busy:
			return
		await wait(0.1)


func shot(name: String) -> void:
	await process_frame
	await process_frame
	root.get_texture().get_image().save_png(OUT + name)


func _run() -> void:
	await wait(0.5)
	await wait_free()
	nb().unlock()
	var bat = rob().get_node("Battery")

	# 1. l'ancien corps devient un lieu du carnet (croix sur la carte)
	var body_pos: Vector3 = isl().get_node("AnciensCorps").initial_bodies[0]
	rob().global_position = body_pos + Vector3(1.2, 0.05, 1.2)
	bat.level = 100.0
	await wait(1.0)
	var has_body := false
	for id in nb().places:
		if String(id).begins_with("corps_"):
			has_body = true
	check("l'ancien corps est noté sur la carte", has_body)

	# 2. une créature vue de près dans le noir → bestiaire, avec une petite scène
	var creature = isl().get_node("Lueurs/Creature1")
	rob().global_position = Vector3(creature.global_position.x + 1.0, 0.55, creature.global_position.z + 1.0)
	bat.level = 6.0
	var seen := false
	for i in 40:
		await wait(0.1)
		if nb().has_creature(&"meduse"):
			seen = true
			break
		bat.level = 6.0
	check("la méduse entre dans le bestiaire", seen)
	check("le robot s'arrête pour la regarder", rob().busy)
	await wait(1.5)
	await shot("n01_meduse.png")
	await wait_free()
	check("puis il repart", not rob().busy)
	bat.level = 100.0

	# 3. une page normale du journal : ramassée, le carnet s'ouvre dessus
	var page_scene: PackedScene = load("res://assets/props/journal_page.tscn")
	var p1 = page_scene.instantiate()
	p1.page = load("res://assets/notebook/journal/page_01.tres")
	isl().add_child(p1)
	p1.global_position = rob().global_position + Vector3(0.6, -0.05, 0.0)
	await wait(0.4)
	await press("interact")
	await wait(3.0)
	check("page 1 dans le carnet", nb().has_journal_page(1))
	check("le carnet s'ouvre sur le journal", nb().is_open)
	await wait(0.5)
	await shot("n02_journal.png")
	await press("move_left")
	await wait(0.4)
	await shot("n03_bestiaire.png")
	nb()._spread = 0
	nb()._build_spread()
	await wait(0.5)
	await shot("n04_carte.png")
	nb().close()
	await wait(0.6)

	# 4. une page lumineuse : blanche en pleine lumière, lisible dans le noir
	var lum := JournalPage.new()
	lum.number = 6
	lum.luminous = true
	lum.text = "(page de test) Si tu lis ceci, c'est que tu es dans le noir.\nElles sont là. Elles l'ont toujours été."
	var p6 = page_scene.instantiate()
	p6.page = lum
	isl().add_child(p6)
	p6.global_position = rob().global_position + Vector3(-0.6, -0.05, 0.0)
	bat.level = 100.0
	await wait(0.4)
	await press("interact")
	await wait(2.5)
	check("page lumineuse illisible batterie pleine", not nb().has_journal_page(6))
	bat.level = 6.0
	await wait(0.3)
	await press("interact")
	await wait(3.0)
	check("page lumineuse ramassée dans le noir", nb().has_journal_page(6))
	await wait(0.5)
	await shot("n05_page_lumineuse.png")
	print("   pages du carnet : ", nb()._pages().size())
	quit()
