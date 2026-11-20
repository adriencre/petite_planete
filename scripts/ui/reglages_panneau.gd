extends PanelContainer
## Le panneau des réglages (scenes/ui/reglages.tscn), sur une feuille du carnet.
## Utilisé par l'écran titre et par le menu pause. Les valeurs vivent dans l'autoload Reglages.
## Chaque curseur a une méta « bus » (Master, Musique, Ambiance, Effets) : on l'édite dans l'inspecteur.

signal ferme

@onready var _curseurs: Array[Node] = find_children("*", "HSlider", true, false)
@onready var _plein_ecran: Button = %PleinEcran
@onready var _retour: Button = %Retour


func _ready() -> void:
	for c in _curseurs:
		var s := c as HSlider
		var bus := str(s.get_meta("bus", "Master"))
		s.min_value = 0.0
		s.max_value = 1.0
		s.step = 0.05
		s.value = float(Reglages.volumes.get(bus, 0.8))
		s.value_changed.connect(func(v: float) -> void: Reglages.regler_volume(bus, v))
	_plein_ecran.toggle_mode = true
	_plein_ecran.button_pressed = Reglages.plein_ecran
	_ecrire_plein_ecran()
	_plein_ecran.toggled.connect(func(oui: bool) -> void:
		Reglages.regler_plein_ecran(oui)
		_ecrire_plein_ecran())
	_retour.pressed.connect(fermer)
	visibility_changed.connect(func() -> void:
		if is_visible_in_tree() and _curseurs.size() > 0:
			(_curseurs[0] as Control).grab_focus())


func _unhandled_input(event: InputEvent) -> void:
	if is_visible_in_tree() and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		fermer()


func fermer() -> void:
	Reglages.enregistrer()
	ferme.emit()


func _ecrire_plein_ecran() -> void:
	_plein_ecran.text = "Plein écran : oui" if _plein_ecran.button_pressed else "Plein écran : non"
