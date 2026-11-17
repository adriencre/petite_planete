extends SceneTree
## Vérification sans fenêtre : depuis le rebord caché, le robot entre dans l'atelier par la porte
## (les murs le bloquent ailleurs), et le haut de la salle s'efface quand il est dedans.

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	racine.get_node("Reveil").set("premier_reveil", false)
	for i in 60 * 8:
		await physics_frame
	var a := racine.get_node("Maquette").get_node_or_null("Atelier") as Node3D
	var j := racine.get_node("Joueur") as CharacterBody3D
	var toit := a.find_child("Toit", true, false) as Node3D
	var entree := a.find_child("Entree", true, false) as Node3D
	print("ATELIER a %s, sol y=%.2f, porte a x=%.2f" % [a.global_position, a.global_position.y, entree.global_position.x])
	# 1) on pousse le robot vers le nord à côté de la porte : le mur doit l'arrêter
	j.set("cinematique", false)
	j.global_position = a.global_position + Vector3(-2.0, 0.3, 5.0)
	for i in 120:
		j.velocity = Vector3(0, j.velocity.y, -2.5)
		j.move_and_slide()
		await physics_frame
	print("A COTE DE LA PORTE : arrete a z=%.2f (mur sud a z=%.2f)" % [j.global_position.z - a.global_position.z, 3.0 - 1.2])
	# 2) devant la porte : il entre
	j.global_position = Vector3(entree.global_position.x, a.global_position.y + 0.3, a.global_position.z + 5.0)
	for i in 150:
		j.velocity = Vector3(0, j.velocity.y, -2.5)
		j.move_and_slide()
		await physics_frame
	for i in 60:
		await physics_frame
	print("PAR LA PORTE : robot a z=%.2f (dedans si < 1.8), toit visible=%s" % [j.global_position.z - a.global_position.z, toit.visible])
	quit()
