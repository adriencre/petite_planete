extends SceneTree
## Vérification sans fenêtre : chaque lanterne est posée sur le terrain (pas sur sa propre collision).

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	for i in 10:
		await physics_frame
	var maquette := racine.get_node("Maquette") as Node3D
	for l in get_nodes_in_group("lanternes"):
		var n := l as Node3D
		# hauteur du terrain sous la lanterne = le haut de sa case
		var sol: float = 0.6 + 2.5 * floorf((n.global_position.y - 0.6) / 2.5 + 0.5)
		print("%s rang %d : posee a y=%.2f, terrain attendu y=%.2f, ecart %.2f m" % [n.name, l.get("rang"), n.global_position.y, sol, n.global_position.y - sol])
	quit()
