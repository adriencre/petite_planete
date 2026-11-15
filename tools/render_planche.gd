extends SceneTree
# Rendu de la planche de validation du kit de l'ombre (images v01..v06 dans tools/).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(90.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/mockups/ombre_planche.tscn")
	_run()


func shot(name: String, from: Vector3, to: Vector3, fov := 40.0) -> void:
	var cam := current_scene.get_node("Camera") as Camera3D
	cam.fov = fov
	cam.global_position = from
	cam.look_at(to)
	for i in 6:
		await process_frame
	root.get_texture().get_image().save_png(OUT + name)
	print("rendu ", name)


func _run() -> void:
	await create_timer(1.2).timeout
	var s := current_scene
	# quelques habitants font un geste, pour voir les animations
	(s.get_node("Ancienne/Animation") as AnimationPlayer).play(&"parle")
	(s.get_node("Pecheur/Animation") as AnimationPlayer).play(&"salut")
	(s.get_node("Petite/Animation") as AnimationPlayer).play(&"cache")
	await create_timer(0.4).timeout
	await shot("v01_ensemble.png", Vector3(0, 26, 30), Vector3(0, 0, 0), 45.0)
	await shot("v02_maisons_gauche.png", Vector3(-10, 6.5, 2.5), Vector3(-10, 1.5, -8), 50.0)
	await shot("v03_maisons_droite.png", Vector3(8, 6.5, 2.5), Vector3(8, 1.6, -8), 50.0)
	await shot("v04_habitants.png", Vector3(-3.2, 2.6, 7.0), Vector3(-3.2, 0.8, 1.5), 48.0)
	await shot("v05_village.png", Vector3(-6, 6.5, 17.5), Vector3(-6, 0.8, 8.5), 55.0)
	await shot("v06_nature.png", Vector3(10, 6.5, 19.5), Vector3(10, 1.2, 10.5), 55.0)
	quit()
