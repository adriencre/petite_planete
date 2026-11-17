extends SceneTree
## Vérification sans fenêtre : la barque est dans la mer ; E pour monter (le câble se branche), Z pour
## avancer à la lumière (lanterne, câble, sillage, batterie), limite au large ; E pour redescendre à terre.

func _touche(code: Key, appui: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.keycode = code
	ev.pressed = appui
	Input.parse_input_event(ev)


func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	racine.get_node("Reveil").set("premier_reveil", false)
	for i in 30:
		await physics_frame
	var m := racine.get_node("Maquette")
	var b := m.get_node_or_null("Barque") as Node3D
	var j := racine.get_node("Joueur") as CharacterBody3D
	var sous: Dictionary = m.call("_case_a", b.global_position)
	print("BARQUE a %s, case dessous niv=%d (mer = -1)" % [b.global_position, sous.niv])
	for i in 60 * 8:   # fin du réveil court
		await physics_frame
	j.set("cinematique", false)
	j.global_position = b.global_position + Vector3(3.0, 1.0, 0)
	for i in 30:
		await physics_frame
	_touche(KEY_E, true)
	await physics_frame
	_touche(KEY_E, false)
	for i in 150:
		await physics_frame
	print("MONTE : pilotee=%s robot dans la barque=%.2f m" % [b.get("pilotee"), Vector2(j.global_position.x - b.global_position.x, j.global_position.z - b.global_position.z).length()])
	var p0 := b.global_position
	_touche(KEY_W, true)   # Z en AZERTY
	for i in 60 * 3:
		await physics_frame
	var anim := j.get_node("Modele").find_child("AnimationPlayer", true, false) as AnimationPlayer
	var cable = b.get("_cable")
	print("AVANCE 3 s : deplacement=%.2f m vitesse=%.2f anim=%s cable branche=%.1f flux=%.2f lanterne=%.1f sillage=%s batterie=%.3f rames=%s" % [b.global_position.distance_to(p0), b.get("_vitesse"), anim.current_animation, b.get("_branche"), cable.materiau.get_shader_parameter("flux"), (b.get("_lanterne_mat") as BaseMaterial3D).emission_energy_multiplier, (b.get("_sillage") as CPUParticles3D).emitting, j.get("batterie"), b.find_child("RameG", true, false) != null])
	for i in 60 * 25:
		await physics_frame
	var devant: Dictionary = m.call("_case_a", b.global_position)
	print("APRES 28 s : distance au centre de l'ile=%.1f m (max 60) vitesse=%.2f case sous la barque niv=%d" % [Vector2(b.global_position.x, b.global_position.z).length(), b.get("_vitesse"), devant.niv])
	_touche(KEY_W, false)
	for i in 60 * 2:
		await physics_frame
	# retour au point de départ, contre la plage, pour redescendre
	b.global_position = p0
	b.set("_vitesse", 0.0)
	for i in 10:
		await physics_frame
	_touche(KEY_E, true)
	await physics_frame
	_touche(KEY_E, false)
	for i in 150:
		await physics_frame
	var sol: Dictionary = m.call("_case_a", j.global_position)
	print("DESCENDU : pilotee=%s cinematique=%s robot sur une case niv=%d" % [b.get("pilotee"), j.get("cinematique"), sol.niv])
	quit()
