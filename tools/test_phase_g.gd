extends SceneTree
# Phase G + H : île 1 côté ombre, 2e moitié (bascule, Compteur qui parle, mission de la Pouponnière,
# hameau qui s'étend, essaim) et le son de l'ombre.
# Lancement : godot --headless --import, puis godot --path . -s tools/test_phase_g.gd
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


func rob() -> Node:
	return isl().get_node("Robot")


func nb() -> Node:
	return root.get_node("Notebook")


func loop() -> Node:
	return root.get_node("Loop")


func audio() -> Node:
	return root.get_node("Audio")


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


func night_on() -> void:
	if not rob().night_mode:
		await press_n()
		await wait(1.0)
		await wait_free()


func night_off() -> void:
	if rob().night_mode:
		await press_n()
		await wait(1.0)
		await wait_free()


func _run() -> void:
	await wait(0.5)
	await wait_free()
	nb().unlock()

	# 0. le son de l'ombre : la couche 1 monte quand on éteint, celle de la lumière baisse
	var music_before: float = audio()._music.volume_db
	await night_on()
	await wait(6.0)
	check("son : la musique de l'ombre monte dans le noir", audio()._ombre_mix[0] > 0.5)
	check("son : la 3e couche (le peuple) reste muette avant la mission", audio()._ombre_mix[2] < 0.05)
	check("son : la musique de la lumière s'efface", audio()._music.volume_db < music_before - 5.0)
	await night_off()

	# 1. bascule (touche F9) puis le Compteur parle
	loop().set_flag(&"bascule")
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	await wait(1.0)
	await wait_free()
	nb().unlock()
	rob().global_position = ground(-17.4, -4.2)
	await night_on()
	var told := false
	for i in 120:
		await wait(0.2)
		if nb().has_parole(&"compteur_214"):
			told = true
			break
	await wait_free()
	check("Compteur : « Tu es revenu deux cent quatorze fois… »", told)
	await shot("g01_compteur_parle.png")
	await night_off()

	# 2. la veilleuse de la porte : on peut reprendre sa lumière
	var lamp = isl().get_node("Ombre/VeilleuseAbri")
	check("veilleuse de l'abri allumée au départ", lamp.is_lit)
	check("après la bascule, on peut la reprendre", lamp.can_take_back)
	rob().global_position = lamp.global_position + Vector3(0, 0, 1.2)
	await wait(0.3)
	lamp._take_back(rob())
	await wait(1.0)
	await wait_free()
	check("veilleuse reprise : le seuil est libre", not lamp.is_lit)

	# 3. guider les petites dans le noir jusqu'aux pins
	await night_on()
	var hamlet = isl().get_node("Ombre/Hameau")
	var mission = isl().get_node("Ombre/MissionPouponniere")
	var petites: Array = mission._petites()
	await wait(2.0)
	check("les petites suivent le robot éteint", petites.size() > 0 and petites[0].follows)
	await shot("g02_petites_suivent.png")
	# le robot marche (téléporté par petits pas) de l'abri jusqu'au hameau
	var from: Vector3 = rob().global_position
	var to: Vector3 = hamlet.global_position
	for k in 40:
		var p := from.lerp(to, (k + 1) / 40.0)
		rob().global_position = ground(p.x, p.z)
		await wait(0.25)
		if loop().has_flag(&"pouponniere_libre"):
			break
	for i in 60:
		if loop().has_flag(&"pouponniere_libre"):
			break
		await wait(0.25)
	check("mission : la Pouponnière est libre", loop().has_flag(&"pouponniere_libre"))
	await wait(3.0)
	await shot("g03_hameau_s_etend.png")
	await wait_free()
	check("le hameau s'étend dans l'ancien désert", hamlet.get_node("Extension").visible)
	check("« Merci » dans le carnet", nb().has_parole(&"hameau_merci"))

	# 4. l'essaim suit le robot dans le noir, et la 3e couche (le peuple) arrive
	var swarm = isl().get_node("Ombre/Essaim")
	await wait(4.0)
	check("essaim : il brille près du robot", swarm._amount > 0.8 and swarm.global_position.distance_to(rob().global_position) < 3.0)
	check("son : la couche du peuple arrive", audio()._ombre_mix[2] > 0.3)
	await shot("g04_essaim.png")

	# 5. le Compteur donne la première pierre
	rob().global_position = ground(-17.4, -4.2)
	for i in 120:
		await wait(0.2)
		if loop().has_flag(&"premiere_pierre"):
			break
	await wait(4.0)
	await wait_free()
	check("Compteur : la première pierre est donnée", loop().has_flag(&"premiere_pierre"))
	await shot("g05_premiere_pierre.png")
	await night_off()

	# 6. ça reste d'une boucle à l'autre
	loop().count += 1
	change_scene_to_file("res://scenes/islands/island_01.tscn")
	await wait(1.0)
	await wait_free()
	check("boucle suivante : le hameau est toujours agrandi", isl().get_node("Ombre/Hameau/Extension").visible)
	check("boucle suivante : la veilleuse reste libre (pas de nouvelle mission)", isl().get_node("Ombre/MissionPouponniere")._done)
	quit()
