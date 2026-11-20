extends CanvasLayer
## Le menu pause (autoload « MenuPause », scenes/ui/menu_pause.tscn).
## Échap pendant la partie : tout s'arrête (cinématiques comprises), la musique continue doucement.
## Le carnet et les feuilles se ferment d'abord avec Échap : ils l'attrapent avant nous.
## Le jeu se met aussi en pause quand la fenêtre perd le focus.

@onready var _voile: ColorRect = $Voile
@onready var _feuille: Control = $Feuille
@onready var _reglages: Control = $Reglages
@onready var _reprendre: Button = %Reprendre

var ouvert := false
var _transition_en_cours := false
var _souris_avant: Input.MouseMode = Input.MOUSE_MODE_CAPTURED


func _ready() -> void:
	visible = false
	_reglages.visible = false
	_reprendre.pressed.connect(fermer)
	%BoutonReglages.pressed.connect(_montrer_reglages)
	%RetourTitre.pressed.connect(_retour_titre)
	%Quitter.pressed.connect(Sauvegarde.quitter)
	_reglages.ferme.connect(_cacher_reglages)
	get_tree().scene_changed.connect(_sur_changement_scene)


func _unhandled_input(event: InputEvent) -> void:
	if _transition_en_cours or _reglages.is_visible_in_tree() or not Sauvegarde.en_partie():
		return
	if not event.is_action_pressed("ui_cancel"):
		return
	get_viewport().set_input_as_handled()
	if ouvert:
		fermer()
	else:
		ouvrir()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and not ouvert and not _transition_en_cours and Sauvegarde.en_partie():
		ouvrir()


func ouvrir() -> void:
	if ouvert:
		return
	ouvert = true
	get_tree().paused = true
	_souris_avant = Input.mouse_mode
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	visible = true
	_feuille.visible = true
	%ErreurRetour.hide()
	_reglages.visible = false
	_voile.color.a = 0.0
	_feuille.modulate.a = 0.0
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	t.tween_property(_voile, "color:a", 0.5, 0.35)
	t.tween_property(_feuille, "modulate:a", 1.0, 0.35)
	_reprendre.grab_focus()


func fermer() -> void:
	if not ouvert:
		return
	ouvert = false
	Input.mouse_mode = _souris_avant
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_property(_voile, "color:a", 0.0, 0.25)
	t.tween_property(_feuille, "modulate:a", 0.0, 0.25)
	await t.finished
	if not ouvert:
		visible = false
		get_tree().paused = false


func _retour_titre() -> void:
	if _transition_en_cours:
		return
	_transition_en_cours = true
	%ErreurRetour.hide()
	if await Sauvegarde.retour_au_titre():
		ouvert = false
		visible = false
	else:
		%ErreurRetour.show()
		%RetourTitre.grab_focus()
	_transition_en_cours = false


func _montrer_reglages() -> void:
	_feuille.visible = false
	_reglages.visible = true


func _cacher_reglages() -> void:
	_reglages.visible = false
	_feuille.visible = true
	%BoutonReglages.grab_focus()



func _sur_changement_scene() -> void:
	if _transition_en_cours:
		ouvert = false
		visible = false
