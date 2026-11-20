extends CanvasLayer
## Charge une scène derrière un voile, puis la révèle après son installation.

@onready var _voile: ColorRect = $Voile
@onready var _contenu: Control = $Voile/Contenu
@onready var _progression: ProgressBar = %Progression
@onready var _gauche: Polygon2D = %PetaleGauche
@onready var _droite: Polygon2D = %PetaleDroit

var active := false


func changer(chemin: String, preparer: Callable, message: String) -> bool:
	if active:
		return false
	active = true
	visible = true
	_voile.modulate.a = 0.0
	_contenu.modulate.a = 0.0
	%Message.text = message
	_actualiser(0.0)

	var erreur := ResourceLoader.load_threaded_request(chemin, "PackedScene")
	await _fondre(_voile, 1.0, 0.48)
	var reussi := false
	if erreur == OK:
		await _fondre(_contenu, 1.0, 0.25)
		var mesures: Array = []
		var statut := ResourceLoader.load_threaded_get_status(chemin, mesures)
		while statut == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			if not mesures.is_empty():
				_actualiser(float(mesures[0]))
			await get_tree().process_frame
			statut = ResourceLoader.load_threaded_get_status(chemin, mesures)
		if statut != ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			var paquet := ResourceLoader.load_threaded_get(chemin) as PackedScene
			if paquet != null and paquet.can_instantiate():
				_actualiser(1.0)
				await get_tree().create_timer(0.25).timeout
				var destination := paquet.instantiate()
				if destination != null:
					var arbre := get_tree()
					erreur = arbre.change_scene_to_node(destination)
					if erreur == OK:
						preparer.call()
						await arbre.scene_changed
						reussi = true
					else:
						destination.free()

	await _fondre(_contenu, 0.0, 0.20)
	await _fondre(_voile, 0.0, 0.68)
	visible = false
	active = false
	return reussi


func _input(_event: InputEvent) -> void:
	if active:
		get_viewport().set_input_as_handled()


func _actualiser(fraction: float) -> void:
	_progression.value = clampf(fraction, 0.0, 1.0)
	var cran := floorf(_progression.value * 5.0)
	_gauche.rotation_degrees = -cran * 9.0
	_droite.rotation_degrees = cran * 9.0


func _fondre(element: Control, alpha: float, duree: float) -> Signal:
	var tween := create_tween().set_trans(Tween.TRANS_SINE)
	tween.tween_property(element, "modulate:a", alpha, duree)
	return tween.finished
