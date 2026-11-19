extends CanvasLayer
## L'atelier choisit les pièces. L'état de l'assemblage reste dans la scène du Phare.

signal placer(roue: int, axe: int)
signal tourner(axe: int)
signal retirer(axe: int)
signal fermer

const NOMS := ["Roue moyenne", "Grande roue", "Petite roue"]
const AXES := ["Axe gauche", "Axe central", "Axe droit"]

@onready var _logements: Array[Button] = [%AxeGauche, %AxeCentral, %AxeDroit]
@onready var _rangement: Array[Button] = [%RoueMoyenne, %GrandeRoue, %PetiteRoue]
@onready var _instruction: Label = %Instruction
@onready var _tourner: Button = %Tourner
@onready var _retirer: Button = %Retirer
@onready var _fermer: Button = %Fermer

var _places: Array
var _crans: Array
var _phases: Array
var _occupe := false
var _roue := -1
var _axe := -1


func _ready() -> void:
	for i in _logements.size():
		_logements[i].pressed.connect(_choisir_axe.bind(i))
		_rangement[i].pressed.connect(_choisir_roue.bind(i))
		(_logements[i].get_node("Contenu/Titre") as Label).text = AXES[i]
		(_rangement[i].get_node("Contenu/Titre") as Label).text = NOMS[i]
	_fermer.pressed.connect(func() -> void: fermer.emit())
	_tourner.pressed.connect(func() -> void: tourner.emit(_axe))
	_retirer.pressed.connect(func() -> void: retirer.emit(_axe))


func ouvrir(places: Array, crans: Array, phases: Array) -> void:
	_axe = -1
	_roue = -1
	_phases = phases
	show()
	actualiser(places, crans, false)
	for bouton in _rangement:
		if not bouton.disabled:
			bouton.grab_focus()
			return
	_logements[0].grab_focus()


func actualiser(places: Array, crans: Array, occupe: bool) -> void:
	_places = places
	_crans = crans
	_occupe = occupe
	if _roue >= 0 and _places[_roue] >= 0:
		_roue = -1
	for i in _logements.size():
		var roue := _places.find(i)
		var phase: float = _phases[i]
		var angle := phase if roue < 0 else phase + int(_crans[roue]) * TAU / 3.0
		var logement := _logements[i]
		logement.set_pressed_no_signal(i == _axe)
		logement.disabled = _occupe
		dessiner_axe(i, roue, angle)
		(logement.get_node("Contenu/Etat") as Label).text = "Axe libre" if roue < 0 else NOMS[roue]
		var rangement := _rangement[i]
		var montee := int(_places[i]) >= 0
		rangement.disabled = _occupe or montee
		rangement.set_pressed_no_signal(i == _roue)
		rangement.get_node("Contenu/Dessin").call("afficher", i, -1, 0.0, 0.0)
		(rangement.get_node("Contenu/Dessin") as Control).modulate.a = 0.35 if montee else 1.0
		(rangement.get_node("Contenu/Etat") as Label).text = "Montée" if montee else ("Sélectionnée" if i == _roue else "Disponible")
	var sur_axe := _axe >= 0 and _places.has(_axe)
	_tourner.disabled = _occupe or not sur_axe
	_retirer.disabled = _occupe or not sur_axe
	_fermer.disabled = _occupe
	if _occupe:
		_instruction.text = "Le mécanisme est en mouvement…"
	elif _roue >= 0:
		_instruction.text = "Clique sur un axe libre pour monter la roue."
	elif sur_axe:
		_instruction.text = "Compare la roue à l’empreinte, puis aligne les deux repères dorés."
	else:
		_instruction.text = "Choisis une roue dans le râtelier ou sélectionne un axe occupé."


func dessiner_axe(axe: int, roue: int, angle: float) -> void:
	_logements[axe].get_node("Contenu/Dessin").call("afficher", roue, axe, _phases[axe], angle)


func _choisir_roue(roue: int) -> void:
	if _occupe or int(_places[roue]) >= 0:
		return
	_roue = -1 if _roue == roue else roue
	_axe = -1
	actualiser(_places, _crans, false)


func _choisir_axe(axe: int) -> void:
	if _occupe:
		return
	_axe = axe
	if _roue >= 0 and not _places.has(axe):
		var roue := _roue
		_roue = -1
		placer.emit(roue, axe)
	else:
		_roue = -1
		actualiser(_places, _crans, false)


func _input(event: InputEvent) -> void:
	if not visible or not event is InputEventKey or not event.is_pressed() or event.is_echo():
		return
	var touche := (event as InputEventKey).physical_keycode
	if touche == KEY_E or touche == KEY_ESCAPE:
		get_viewport().set_input_as_handled()
		if not _occupe:
			fermer.emit()
