extends SceneTree
# Rendu de l'enfant (modèle Blender) dans la maquette, avec ses animations.
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(60.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/mockups/ombre_mockup.tscn")
	_run()


func _tree(n: Node, depth := 0) -> void:
	if depth > 3:
		return
	print("  ".repeat(depth), n.name, " (", n.get_class(), ")")
	for c in n.get_children():
		_tree(c, depth + 1)


func shot(cam: Camera3D, name: String, from: Vector3, to: Vector3, fov := 35.0) -> void:
	cam.fov = fov
	cam.global_position = from
	cam.look_at(to)
	for i in 6:
		await process_frame
	root.get_texture().get_image().save_png(OUT + name)
	print("rendu ", name)


func _run() -> void:
	await create_timer(1.0).timeout
	var s := current_scene
	var enfant := s.get_node("Enfant")
	_tree(enfant.get_node("Modele"))
	var anim := enfant.get_node("Animation") as AnimationPlayer
	print("animations : ", anim.get_animation_list())
	var cam := s.get_node("Camera") as Camera3D
	var p: Vector3 = enfant.global_position
	await shot(cam, "e01_enfant_idle.png", p + Vector3(0.6, 1.0, 2.2), p + Vector3(0, 0.6, 0))
	anim.play(&"salut")
	await create_timer(0.35).timeout
	await shot(cam, "e02_enfant_salut.png", p + Vector3(0.6, 1.0, 2.2), p + Vector3(0, 0.6, 0))
	var e2 := s.get_node("Enfant2")
	(e2.get_node("Animation") as AnimationPlayer).play(&"cache")
	(enfant.get_node("Animation") as AnimationPlayer).play(&"marche")
	await create_timer(0.6).timeout
	var q: Vector3 = e2.global_position
	await shot(cam, "e03_enfant_cache.png", q + Vector3(0.9, 1.0, 1.8), q + Vector3(0, 0.5, 0))
	await shot(cam, "e04_vue_jeu.png", Vector3(11.5, 11.5, 11.5), Vector3.ZERO, 32.0)
	quit()
