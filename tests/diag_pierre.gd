extends SceneTree
## Vérification sans fenêtre : premier réveil, puis recharge à la pierre-soleil devant l'abri.

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	var j := racine.get_node("Joueur") as CharacterBody3D
	var t := 0
	await physics_frame
	while t < 60 * 45:
		await physics_frame
		t += 1
		if t > 120 and not bool(j.get("cinematique")):
			break
	print("REVEIL fini apres %.1f s, cinematique=%s" % [t / 60.0, j.get("cinematique")])
	for i in 150:
		await physics_frame
	var vision := (racine.get_node("Vision/Ecran") as ColorRect).material as ShaderMaterial
	print("BATTERIE apres reveil=%.2f  trouble=%.2f" % [j.get("batterie"), vision.get_shader_parameter("trouble")])
	var pierre: Node3D = null
	for n in racine.get_node("Maquette").get_children():
		if n.scene_file_path.ends_with("pierre_soleil_meshy.glb") and (n as Node3D).global_position.z > 10.0:
			pierre = n
	j.global_position = pierre.global_position + Vector3(3.2, 0.3, 0)
	for i in 10:
		await physics_frame
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_E
	ev.pressed = true
	Input.parse_input_event(ev)
	var anim := j.get_node("Modele").find_child("AnimationPlayer", true, false) as AnimationPlayer
	for i in 60 * 4:
		await physics_frame
	print("PENDANT : en_cours=%s anim=%s vitesse=%.1f batterie=%.2f" % [pierre.get("_en_cours"), anim.current_animation, anim.speed_scale, j.get("batterie")])
	for i in 60 * 12:
		await physics_frame
	print("APRES : en_cours=%s cinematique=%s batterie=%.2f anim=%s" % [pierre.get("_en_cours"), j.get("cinematique"), j.get("batterie"), anim.current_animation])
	quit()
