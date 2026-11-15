extends SceneTree
# Étapes 16–17 : reprendre la lumière, mode nuit (N), page lumineuse de l'atelier.
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize():
	create_timer(120.0).timeout.connect(func() -> void: print("ARRET FORCE"); quit())
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	_run()


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func press(action: String) -> void:
	var e := InputEventAction.new(); e.action = action; e.pressed = true; Input.parse_input_event(e)
	await process_frame
	var r := InputEventAction.new(); r.action = action; r.pressed = false; Input.parse_input_event(r)
	await process_frame


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


func wait_free() -> void:
	for i in 600:
		if isl() and not rob().busy:
			return
		await wait(0.1)


func shot(name: String) -> void:
	await process_frame
	root.get_texture().get_image().save_png(OUT + name)


func _run() -> void:
	await wait(0.5)
	await wait_free()
	var bat = rob().get_node("Battery")

	# 1. reprendre la lumière de la Lanterne1
	var l1 = isl().get_node("Blockout/Lanterne1")
	l1.light_up()
	await wait(3.5)
	check("Lanterne1 allumée", l1.is_lit)
	rob().global_position = l1.global_position + Vector3(1.0, 0.05, 0.6)
	bat.level = 30.0
	await wait(0.4)
	await press("interact")
	await wait(3.0)
	await shot("t01_reprise.png")
	await wait_free()
	check("la lanterne est éteinte", not l1.is_lit)
	check("la batterie est remontée (%.0f)" % bat.level, bat.level > 40.0)
	await wait(5.0)
	check("sa zone s'est rendormie", l1.wake_zone.current_radius < 0.2)
	check("on peut la rallumer", l1.is_ready)

	# 2. mode nuit
	bat.level = 50.0
	await press_n()
	await wait(2.5)
	await shot("t02_nuit_premiere.png")
	await wait_free()
	check("mode nuit actif", rob().night_mode)
	check("vision pleine (%.2f)" % bat.vision(), bat.vision() > 0.95)
	# dans la brume épaisse, plus de vidage
	rob().global_position = Vector3(-20.6, 0.55, -7.6) + Vector3(-1.4, 0, -2.3)
	var before: float = bat.level
	await wait(2.0)
	check("la brume épaisse ne vide plus (%.0f → %.0f)" % [before, bat.level], absf(bat.level - before) < 0.5)
	await shot("t03_nuit_brume.png")
	# pas de lumière en nuit
	rob().global_position = l1.global_position + Vector3(1.0, 0.05, 0.6)
	await wait(0.4)
	await press("interact")
	await wait(1.5)
	await wait_free()
	check("impossible d'allumer en nuit", not l1.is_lit)
	await press_n()
	await wait(1.5)
	await wait_free()
	check("N rallume l'antenne", not rob().night_mode and bat.vision() < 0.5)

	# 3. page lumineuse de l'atelier : lanterne allumée → blanche ; reprise + nuit → lisible
	var lantern = isl().get_node("Atelier/LanterneAtelier")
	var page = isl().get_node_or_null("PageGardienne7")
	check("la page 7 est dans l'atelier", page != null)
	lantern.light_up()
	await wait(2.0)
	bat.level = 60.0
	rob().global_position = page.global_position + Vector3(0.5, -0.8, 0.5)
	await wait(0.4)
	await press_n()
	await wait(1.5)
	await wait_free()
	await press("interact")
	await wait(2.0)
	await wait_free()
	check("lanterne allumée : la page reste illisible", not root.get_node("Notebook").has_journal_page(7))
	await press_n()
	await wait(1.5)
	await wait_free()
	rob().global_position = lantern.global_position + Vector3(0.6, 0.05, 0.6)
	await wait(0.4)
	await press("interact")  # reprendre la lumière de l'atelier
	await wait(2.0)
	await wait_free()
	await wait(4.0)
	rob().global_position = page.global_position + Vector3(0.5, -0.8, 0.5)
	await press_n()
	await wait(1.5)
	await wait_free()
	await press("interact")
	await wait(3.5)
	check("reprise + nuit : la page 7 est lue", root.get_node("Notebook").has_journal_page(7))
	await shot("t04_page7.png")
	quit()
