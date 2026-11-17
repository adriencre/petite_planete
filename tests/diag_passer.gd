extends SceneTree
## Vérification sans fenêtre : Entrée pendant le premier réveil rend la main tout de suite.

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	var j := racine.get_node("Joueur") as CharacterBody3D
	for i in 180:
		await physics_frame
	print("AVANT : cinematique=%s" % j.get("cinematique"))
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_ENTER
	ev.pressed = true
	Input.parse_input_event(ev)
	for i in 30:
		await physics_frame
	var reveil := racine.get_node("Reveil")
	print("APRES 0,5 s : cinematique=%s reveil=%s cine_melange=%.2f" % [j.get("cinematique"), reveil.get("_reveil"), j.get("cine_melange")])
	var p0 := j.global_position
	for i in 60 * 30:   # 30 s : plus rien de l'ancienne séquence ne doit bouger le robot
		await physics_frame
	print("APRES 30 s : cinematique=%s batterie=%.2f deplacement=%.2f m" % [j.get("cinematique"), j.get("batterie"), j.global_position.distance_to(p0)])
	quit()
