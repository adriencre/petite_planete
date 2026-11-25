extends Node
## Essai visuel : le vrai robot monte le Phare en 1re personne (touche Z/W simulée, regard guidé)
## et enregistre des captures en chemin. Lancer la scène res://tests/essai_phare.tscn depuis l'éditeur.
## Dossier des captures : variable d'environnement CAPTURES_PHARE, sinon user://essai_phare.

var _joueur: CharacterBody3D
var _phare: Node3D
var _points: Array[Vector3] = []
var _captures := {}
var _dossier := ""


func _ready() -> void:
	_dossier = OS.get_environment("CAPTURES_PHARE")
	if _dossier == "":
		_dossier = ProjectSettings.globalize_path("user://essai_phare")
	DirAccess.make_dir_recursive_absolute(_dossier)
	var ile := (load("res://scenes/ile_02_maquette.tscn") as PackedScene).instantiate()
	add_child(ile)
	_joueur = ile.get_node("Joueur") as CharacterBody3D
	_phare = ile.get_node("Monde/Phare") as Node3D
	_preparer_parcours()
	await get_tree().create_timer(1.5).timeout
	_joueur.vue_dessus = false
	_joueur.premiere_personne = true
	_joueur.set("_blend", 1.0)
	_joueur.global_position = _monde(_points[0]) + Vector3.UP * 0.1
	_joueur.velocity = Vector3.ZERO
	await get_tree().create_timer(1.0).timeout
	await _marcher()
	print("ESSAI TERMINÉ")
	get_tree().quit()


func _polaire(r: float, angle: float, z: float) -> Vector3:
	return Vector3(r * cos(deg_to_rad(angle)), r * sin(deg_to_rad(angle)), z)


func _arc(r: float, a0: float, a1: float, z0: float, z1: float, nom := "") -> void:
	var n := maxi(1, int(absf(a1 - a0) / 10.0))
	for i in range(1, n + 1):
		var t := float(i) / n
		_points.append(_polaire(r, lerpf(a0, a1, t), lerpf(z0, z1, t)))
		if nom != "" and i == n / 2:
			_captures[_points.size() - 1] = nom


## Mêmes points que tests/diag_phare.gd (coordonnées Blender du Phare).
func _preparer_parcours() -> void:
	_points = [Vector3(0, -1.5, .35), Vector3(1.0, 0.9, .35), _polaire(2.45, 46, .35)]
	_captures = {0: "01_rez", 2: "02_pied_volee"}
	_arc(2.55, 44, -76, .35, 4.10, "03_volee_rez")
	_arc(2.50, -80, -90, 4.10, 4.10)
	_captures[_points.size() - 1] = "04_palier_bureau"
	_points.append(Vector3(0.3, -0.6, 4.10))
	_captures[_points.size() - 1] = "05_bureau"
	_points.append(_polaire(2.5, -72, 4.10))
	_arc(2.40, -90, -260, 4.10, 8.95, "06_volee_bureau")
	_captures[_points.size() - 1] = "07_arrivee_cartes"
	_arc(2.30, -262, -310, 8.95, 8.95)
	_arc(2.1, 50, -128.5, 8.95, 13.62, "08_volee_cartes")
	_points.append_array([_polaire(2.3, -135, 13.62), _polaire(3.2, -175, 13.62)])
	_captures[_points.size() - 1] = "09_galerie"


func _monde(b: Vector3) -> Vector3:
	return _phare.to_global(Vector3(b.x, b.z, -b.y))


func _touche(pressee: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = KEY_W
	e.pressed = pressee
	Input.parse_input_event(e)


func _marcher() -> void:
	for i in _points.size():
		var cible := _monde(_points[i])
		var t := 0.0
		_touche(true)
		while t < 4.0:
			await get_tree().physics_frame
			t += get_physics_process_delta_time()
			var ecart := Vector2(cible.x - _joueur.global_position.x, cible.z - _joueur.global_position.z)
			if ecart.length() < 0.35:
				break
			_joueur.set("_yaw", atan2(-ecart.x, -ecart.y))
			_joueur.set("_pitch", 0.12 if _points[i].z > _points[maxi(i - 1, 0)].z else -0.15)
		if t >= 4.0:
			var ici := _phare.to_local(_joueur.global_position)
			print("BLOQUÉ au point %d : robot à blender (%.2f, %.2f, z %.2f)" % [i, ici.x, -ici.z, ici.y])
		if _captures.has(i):
			_touche(false)
			await get_tree().create_timer(0.6).timeout
			_capturer(_captures[i])
			# vue de dessus au même endroit, pour la coupe
			_joueur.vue_dessus = true
			await get_tree().create_timer(0.8).timeout
			_capturer(_captures[i] + "_dessus")
			_joueur.vue_dessus = false
			_joueur.set("_blend", 1.0)
			await get_tree().create_timer(0.3).timeout
	_touche(false)


func _capturer(nom: String) -> void:
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	image.save_png(_dossier.path_join(nom + ".png"))
	print("CAPTURE ", nom)
