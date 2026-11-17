extends SceneTree
## Vérification sans fenêtre : le robot ne traverse plus le bassin de la grande lanterne.

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	for i in 10:
		await physics_frame
	var corps := racine.get_node("Maquette").get_node_or_null("CollisionGrandeLanterne") as Node3D
	print("collision : ", corps != null)
	var j := racine.get_node("Joueur") as CharacterBody3D
	racine.get_node("Reveil").set("premier_reveil", false)
	j.set("cinematique", false)
	j.global_position = corps.global_position + Vector3(4.0, 0.3, 0)
	for i in 30:
		await physics_frame
	# on pousse le robot droit vers le centre pendant 3 s
	for i in 180:
		j.set("cinematique", false)
		j.velocity = Vector3(-3.0, j.velocity.y, 0)
		j.move_and_slide()
		await physics_frame
	var d := Vector2(j.global_position.x - corps.global_position.x, j.global_position.z - corps.global_position.z).length()
	print("distance au centre apres 3 s de poussee : %.2f m" % d)
	quit()
