extends SceneTree
## Vérification sans fenêtre : la page 7 est sur l'établi de l'atelier ; E près d'elle l'ouvre
## (première lecture : cinématique + texte qui s'écrit), E la referme et rend la main.

func _touche(code: Key) -> void:
	for appui in [true, false]:
		var ev := InputEventKey.new()
		ev.physical_keycode = code
		ev.pressed = appui
		Input.parse_input_event(ev)


func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	racine.get_node("Reveil").set("premier_reveil", false)
	for i in 60 * 8:
		await physics_frame
	var a := racine.get_node("Maquette").get_node_or_null("Atelier") as Node3D
	var page := a.find_child("Page7", true, false) as Node3D
	var j := racine.get_node("Joueur") as CharacterBody3D
	print("PAGE : trouvee=%s a %s (sol de l'atelier y=%.2f)" % [page != null, page.global_position if page else Vector3.ZERO, a.global_position.y])
	j.set("cinematique", false)
	j.global_position = page.global_position + Vector3(0, -1.3, 1.2)
	for i in 30:
		await physics_frame
	_touche(KEY_E)
	for i in 60 * 3:
		await physics_frame
	print("OUVERTE : ouverte=%s cinematique=%s camera=%.2f" % [page.get("_ouverte"), j.get("cinematique"), j.get("cine_melange")])
	for i in 60 * 14:
		await physics_frame
	var txt := page.get("_texte") as RichTextLabel
	print("TEXTE : %.0f %% ecrit, %d caracteres" % [txt.visible_ratio * 100.0, txt.get_total_character_count()])
	_touche(KEY_E)
	for i in 60 * 3:
		await physics_frame
	print("FERMEE : ouverte=%s cinematique=%s camera=%.2f deja_lue=%s" % [page.get("_ouverte"), j.get("cinematique"), j.get("cine_melange"), page.get("deja_lue")])
	quit()
