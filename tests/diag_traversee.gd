extends SceneTree
## Diagnostic de la navigation entre les îles : chaque île a-t-elle son Large (brume du large,
## silhouettes, arrivée), la barque le trouve-t-elle, et vise-t-on bien l'île voulue depuis le large ?
## godot --headless --path . -s res://tests/diag_traversee.gd

const ILES := {
	"res://scenes/ile_01_maquette.tscn": ["reveil", ["phare", "colonie"]],
	"res://scenes/ile_02_maquette.tscn": ["phare", ["reveil", "colonie"]],
	"res://scenes/ile_03_maquette.tscn": ["colonie", ["reveil", "phare"]],
}


func _initialize() -> void:
	_tester.call_deferred()


func _tester() -> void:
	var erreurs := 0
	for chemin: String in ILES:
		var attendu: Array = ILES[chemin]
		var paquet: PackedScene = load(chemin)
		if paquet == null:
			print("ÉCHEC chargement ", chemin)
			erreurs += 1
			continue
		var scene := paquet.instantiate()
		root.add_child(scene)
		for i in 6:
			await process_frame
		var large := scene.get_node_or_null("Large") as Node3D
		if large == null:
			print("ÉCHEC pas de Large dans ", chemin)
			erreurs += 1
		else:
			print(chemin, " : île=", large.get("ile"), " rayon=", large.get("rayon_depart"), " arrivée=", (large.call("arrivee") as Transform3D).origin)
			if String(large.get("ile")) != String(attendu[0]):
				print("  ÉCHEC île attendue ", attendu[0])
				erreurs += 1
			for nom: String in attendu[1]:
				var s := large.get_node_or_null("Silhouettes/" + nom) as Node3D
				if s == null:
					print("  ÉCHEC silhouette manquante ", nom)
					erreurs += 1
					continue
				# depuis le bord du large, proue vers la silhouette : c'est elle qu'on vise
				var dir := Vector3(s.global_position.x - large.global_position.x, 0, s.global_position.z - large.global_position.z).normalized()
				var bord: Vector3 = large.global_position + dir * (float(large.get("rayon_depart")) + 5.0)
				var avant := Vector3(s.global_position.x - bord.x, 0, s.global_position.z - bord.z).normalized()
				var vise: String = large.call("destination", bord, avant)
				print("  ", nom, " à ", s.global_position.round(), " échelle ", snappedf(s.scale.x, 0.01), " → visée : '", vise, "'")
				if vise != nom and not bool(large.get("apres_fin_ile_1")):
					print("  ÉCHEC visée")
					erreurs += 1
		var barque := get_first_node_in_group("barque_qui_flotte")
		print("  barque trouvée : ", barque != null, " ; large de la barque : ", barque != null and barque.get("_large") != null)
		if barque == null or barque.get("_large") == null:
			erreurs += 1
		scene.queue_free()
		await process_frame
		await process_frame
	print("FIN, erreurs : ", erreurs)
	quit(1 if erreurs > 0 else 0)

