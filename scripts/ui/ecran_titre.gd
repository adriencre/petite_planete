extends Control
## Accueil au-dessus du Réveil. Les changements de scène passent par Sauvegarde.

@export var duree_fondu: float = 1.2
## Volume de la musique de l'écran titre (dB, avant le réglage « Musique »).
@export var volume_musique: float = -6.0
## Dev seulement (bouton caché dans le jeu exporté) : nom affiché -> scène de l'île.
## L'île 1 reprend la partie sauvegardée, sans l'effacer.
@export var iles_dev: Dictionary = {
	"Île 1 — Le Réveil": "res://scenes/ile_01_maquette.tscn",
	"Île 2 — Le Phare": "res://scenes/ile_02_maquette.tscn",
}

@onready var _pollen: CPUParticles2D = $Pollen
@onready var _menu: Control = $Menu
@onready var _confirmation: Control = $Confirmation
@onready var _reglages: Control = $Reglages
@onready var _noir: ColorRect = $Noir
@onready var _continuer: Button = %Continuer
@onready var _nouvelle: Button = %NouvellePartie

var _part := false
var _clic_actif := false
var _fondu_musique: Tween


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
	%FermerEchec.pressed.connect(_cacher_echec)
	Sauvegarde.chargement_echoue.connect(_montrer_echec)
	for noeud in find_children("*", "Button", true, false):
		var bouton := noeud as Button
		bouton.focus_entered.connect(_jouer_clic)
		bouton.mouse_entered.connect(func() -> void:
			if not bouton.has_focus():
				_jouer_clic())
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
	_fondre_musique(volume_musique, duree_fondu * 2.5)
	(_continuer if _continuer.visible else _nouvelle).grab_focus()
	_noir.color.a = 1.0
	create_tween().set_trans(Tween.TRANS_SINE).tween_property(_noir, "color:a", 0.0, duree_fondu)

	_clic_actif = true


func _jouer_clic() -> void:
	if _clic_actif and not _part:
		$Clic.play()


func _unhandled_input(event: InputEvent) -> void:
	if _part:
		return
	if $Echec.visible and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_cacher_echec()
		return
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
	$ChoixIle.hide()
	_fondre_musique(-60.0, 0.65)
	Sauvegarde.aller_dev(scene)


func _placer() -> void:
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


func _lancer(nouvelle: bool) -> void:
	if _part:
		return
	_part = true
	_menu.hide()
	_confirmation.hide()
	_fondre_musique(-60.0, 0.65)
	if nouvelle:
		Sauvegarde.nouvelle_partie()
	else:
		Sauvegarde.continuer()


func _montrer_echec() -> void:
	_part = false
	_fondre_musique(volume_musique, 0.65)
	$Echec.show()
	%FermerEchec.grab_focus()


func _cacher_echec() -> void:
	$Echec.hide()
	_menu.show()
	(_continuer if _continuer.visible else _nouvelle).grab_focus()


func _quitter() -> void:
	if _part:
		return
	_part = true
	_menu.hide()
	_fondre_musique(-60.0, duree_fondu)
	var tween := create_tween().set_trans(Tween.TRANS_SINE)
	tween.tween_property(_noir, "color:a", 1.0, duree_fondu)
	await tween.finished
	get_tree().quit()


func _fondre_musique(volume: float, duree: float) -> void:
	if _fondu_musique and _fondu_musique.is_valid():
		_fondu_musique.kill()
	_fondu_musique = create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	for lecteur in [$Musique1, $Musique2]:
		_fondu_musique.tween_property(lecteur, "volume_db", volume, duree)
