extends Control
## L'écran titre (scenes/ecran_titre.tscn) : l'aquarelle de la grande lanterne, qui respire doucement,
## du pollen doré qui monte, le piano de l'île. Tout se règle dans l'éditeur (textes, couleurs, dessin).
## - Continuer : seulement s'il y a une partie sauvegardée (on se réveille dans le berceau).
## - Nouvelle partie : si une partie existe, on demande avant de l'effacer.
## On entre et on sort lentement, par le noir (pas d'action instantanée).

## Durée du fondu d'entrée et de sortie (s).
@export var duree_fondu: float = 1.6
## Agrandissement lent du dessin (respiration), et sa période (s).
@export var respiration: float = 0.035
@export var periode_respiration: float = 24.0
## Volume de la musique de l'écran titre (dB, avant le réglage « Musique »).
@export var volume_musique: float = -6.0
## Dev seulement (bouton caché dans le jeu exporté) : nom affiché -> scène de l'île.
## L'île 1 reprend la partie sauvegardée, sans l'effacer.
@export var iles_dev: Dictionary = {
	"Île 1 — Le Réveil": "res://scenes/ile_01_maquette.tscn",
	"Île 2 — Le Phare (maquette grise)": "res://scenes/ile_02_maquette.tscn",
}

@onready var _fond: TextureRect = $Fond
@onready var _pollen: CPUParticles2D = $Pollen
@onready var _menu: Control = $Menu
@onready var _confirmation: Control = $Confirmation
@onready var _reglages: Control = $Reglages
@onready var _noir: ColorRect = $Noir
@onready var _continuer: Button = %Continuer
@onready var _nouvelle: Button = %NouvellePartie

var _part := false
var _t := 0.0


func _ready() -> void:
	get_tree().paused = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_continuer.visible = Sauvegarde.existe()
	_confirmation.visible = false
	_reglages.visible = false
	_continuer.pressed.connect(_lancer.bind(false))
	_nouvelle.pressed.connect(_demander_nouvelle)
	%BoutonReglages.pressed.connect(_montrer_reglages)
	%Quitter.pressed.connect(_quitter)
	%Oui.pressed.connect(_lancer.bind(true))
	%Non.pressed.connect(_cacher_confirmation)
	_reglages.ferme.connect(_cacher_reglages)
	_preparer_dev()
	resized.connect(_placer)
	_placer()
	for p in [$Musique1, $Musique2]:
		var lecteur := p as AudioStreamPlayer
		if lecteur.stream is AudioStreamWAV:
			var s := (lecteur.stream as AudioStreamWAV).duplicate() as AudioStreamWAV
			s.loop_mode = AudioStreamWAV.LOOP_FORWARD
			s.loop_begin = 0
			s.loop_end = int(s.get_length() * s.mix_rate)
			lecteur.stream = s
		lecteur.volume_db = -60.0
		lecteur.play()
		create_tween().tween_property(lecteur, "volume_db", volume_musique, duree_fondu * 2.5)
	(_continuer if _continuer.visible else _nouvelle).grab_focus()
	_noir.color.a = 1.0
	create_tween().set_trans(Tween.TRANS_SINE).tween_property(_noir, "color:a", 0.0, duree_fondu)


func _process(delta: float) -> void:
	_t += delta
	_fond.scale = Vector2.ONE * (1.0 + respiration * (0.5 - 0.5 * cos(_t * TAU / periode_respiration)))


func _unhandled_input(event: InputEvent) -> void:
	if _confirmation.visible and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_cacher_confirmation()
	elif $ChoixIle.visible and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_cacher_dev()


# --- Dev : aller directement sur une île ---

func _preparer_dev() -> void:
	$ChoixIle.visible = false
	%BoutonDev.visible = OS.is_debug_build()
	if not OS.is_debug_build():
		return
	%BoutonDev.pressed.connect(_montrer_dev)
	%RetourDev.pressed.connect(_cacher_dev)
	for nom in iles_dev:
		var b := Button.new()
		b.text = str(nom)
		b.pressed.connect(_aller_dev.bind(str(iles_dev[nom])))
		%ListeIles.add_child(b)


func _montrer_dev() -> void:
	_menu.visible = false
	$ChoixIle.visible = true
	if %ListeIles.get_child_count() > 0:
		(%ListeIles.get_child(0) as Button).grab_focus()


func _cacher_dev() -> void:
	$ChoixIle.visible = false
	_menu.visible = true
	%BoutonDev.grab_focus()


func _aller_dev(scene: String) -> void:
	if _part:
		return
	_part = true
	await _sortir()
	Sauvegarde.aller_dev(scene)


func _placer() -> void:
	_fond.pivot_offset = _fond.size * 0.5
	_pollen.position = Vector2(size.x * 0.5, size.y)
	_pollen.emission_rect_extents = Vector2(size.x * 0.5, 10.0)


func _demander_nouvelle() -> void:
	if not Sauvegarde.existe():
		_lancer(true)
		return
	_menu.visible = false
	_confirmation.visible = true
	%Non.grab_focus()


func _cacher_confirmation() -> void:
	_confirmation.visible = false
	_menu.visible = true
	_nouvelle.grab_focus()


func _montrer_reglages() -> void:
	_menu.visible = false
	_reglages.visible = true


func _cacher_reglages() -> void:
	_reglages.visible = false
	_menu.visible = true
	%BoutonReglages.grab_focus()


## Fondu au noir, la musique s'éteint, puis on part sur l'île.
func _lancer(nouvelle: bool) -> void:
	if _part:
		return
	_part = true
	await _sortir()
	if nouvelle:
		Sauvegarde.nouvelle_partie()
	else:
		Sauvegarde.continuer()


func _quitter() -> void:
	if _part:
		return
	_part = true
	await _sortir()
	get_tree().quit()


func _sortir() -> void:
	_menu.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	t.tween_property(_noir, "color:a", 1.0, duree_fondu)
	for p in [$Musique1, $Musique2]:
		t.tween_property(p, "volume_db", -60.0, duree_fondu)
	await t.finished
