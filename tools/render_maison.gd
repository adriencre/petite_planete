extends SceneTree
# Rendu de la maison-champignon (modèle Blender) dans la maquette.
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"


func _initialize() -> void:
	create_timer(60.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/mockups/ombre_mockup.tscn")
	_run()


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
	var cam := s.get_node("Camera") as Camera3D
	var h: Vector3 = s.get_node("MaisonChampignon").global_position
	# l'enfant vient devant la porte, pour l'échelle
	var e := s.get_node("Enfant") as Node3D
	var front: Vector3 = (s.get_node("MaisonChampignon") as Node3D).global_transform.basis.z
	e.global_position = h + front * 1.9 + Vector3(0.5, -0.5, 0)
	e.look_at(e.global_position + front, Vector3.UP)
	e.rotate_y(PI)
	await shot(cam, "h01_maison_face.png", h + front * 6.0 + Vector3(1.5, 2.6, 0), h + Vector3(0, 1.2, 0) + front * 0.8)
	await shot(cam, "h02_maison_jeu.png", h + Vector3(7.5, 7.5, 7.5), h + Vector3(0, 0.8, 0), 32.0)
	quit()
