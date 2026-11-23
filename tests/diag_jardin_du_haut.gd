extends SceneTree
## Diagnostic G3 : les pièces du jardin du haut sont-elles dans le modèle de la Colonie, et la scène se charge-t-elle ?
## godot --headless --path . -s res://tests/diag_jardin_du_haut.gd

func _init() -> void:
	var glb: PackedScene = load("res://assets/models/ile03/colonie_du_lagon.glb")
	var colonie: Node = glb.instantiate()
	var noms := ["Vanne_sas_0", "Vanne_sas_3", "Eau_sas_1", "Eau_sas_4", "Ponton_ecluse", "Levier_ecluse",
		"Socle_du_levier", "Flotteur_ecluse", "Verrou_ecluse", "Coeur_lampe_mere", "Disque_lampe_mere",
		"Cylindre_musique", "Verriere_09", "Mur_du_jardin", "Seuil_porte_jardin"]
	var manque := 0
	for n in noms:
		var o := colonie.find_child(n, true, false) as Node3D
		if o == null:
			print("MANQUE ", n)
			manque += 1
		else:
			print("ok ", n, " ", o.global_transform.origin if o.is_inside_tree() else o.position, " enfants=", o.get_child_count())
	var scene: PackedScene = load("res://scenes/ile_03_maquette.tscn")
	print("scène Colonie chargée : ", scene != null and scene.can_instantiate())
	var porte: PackedScene = load("res://scenes/ile03/porte_jardin.tscn")
	print("porte du jardin : ", porte != null and porte.can_instantiate())
	colonie.free()
	print("FIN, manquants : ", manque)
	quit(1 if manque > 0 else 0)
