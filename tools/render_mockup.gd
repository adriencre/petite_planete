extends SceneTree
# Rend la maquette du monde de l'ombre sous plusieurs angles (images dans tools/).
const OUT := "C:/Users/adrie/OneDrive/Bureau/petite-planete/tools/"

var views := [
	["m01_vue_ensemble.png", Vector3(11.5, 11.5, 11.5), Vector3(0, 0, 0), 32.0],
	["m02_village_proche.png", Vector3(5.5, 4.2, 7.5), Vector3(0.0, 0.8, 1.0), 40.0],
	["m03_habitants.png", Vector3(2.0, 2.1, 5.2), Vector3(0.0, 0.7, 1.8), 38.0],
	["m04_maisons.png", Vector3(-1.0, 3.2, 3.6), Vector3(-2.8, 1.2, -2.6), 45.0],
]


func _initialize() -> void:
	create_timer(60.0).timeout.connect(quit)
	change_scene_to_file("res://scenes/mockups/ombre_mockup.tscn")
	_run()


func _run() -> void:
	await create_timer(1.5).timeout
	var cam := current_scene.get_node("Camera") as Camera3D
	for v in views:
		cam.fov = v[3]
		cam.global_position = v[1]
		cam.look_at(v[2])
		for i in 8:
			await process_frame
		await create_timer(0.3).timeout
		root.get_texture().get_image().save_png(OUT + v[0])
		print("rendu ", v[0])
	quit()
