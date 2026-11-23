extends Node
## L'horloge du monde (autoload « HorlogeMonde », ROADMAP J4) : le temps qui passe pour tout l'archipel.
## Pour l'instant : la marée (DESIGN.md / ILE_02_PHARE.md §4) — un cycle de 8 min, la mer reste basse
## « six tours du faisceau » (4 min), puis haute 4 min. Les transitions sont lentes : la mer ne prévient
## pas, mais elle ne saute pas non plus. Plus tard : la lune (24 min).
## Les îles lisent `niveau_mer()` (maquette.gd fait monter la mer, maree_estran.gd noie l'estran).

signal maree_basse_commence
signal maree_haute_commence

## Durée d'un cycle complet de marée (s).
@export var duree_maree: float = 480.0
## Durée de la montée et de la descente (s), comprises dans le cycle.
@export var duree_transition: float = 40.0
## Niveau de la mer (m) à marée basse et à marée haute (ILE_02_PHARE.md §3 : -0,6 / +0,5).
@export var mer_basse: float = -0.6
@export var mer_haute: float = 0.5
## Accélère le temps (tests : 8 = un cycle par minute). Réglable aussi en jeu (Page↓ / Page↑ ;
## pas F8 : c'est le raccourci de Godot qui arrête le jeu).
@export var vitesse: float = 1.0
## Où commence le cycle (0 ≈ début de la marée basse ; 0,5 ≈ début de la haute). 0,85 : on arrive à
## marée haute et la mer se retire moins d'une minute plus tard (on la voit découvrir la chaussée).
@export_range(0.0, 1.0) var phase_depart: float = 0.85

var temps := 0.0
var _etait_basse := false


func _ready() -> void:
	temps = phase_depart * duree_maree
	_etait_basse = est_basse()


func _process(delta: float) -> void:
	temps += delta * vitesse
	var basse := est_basse()
	if basse != _etait_basse:
		_etait_basse = basse
		if basse:
			maree_basse_commence.emit()
		else:
			maree_haute_commence.emit()


func _unhandled_key_input(event: InputEvent) -> void:
	# raccourcis de test : Page↓ ralentit, Page↑ accélère la marée
	if event.is_pressed() and not event.is_echo() and event is InputEventKey:
		var k := (event as InputEventKey).physical_keycode
		if k == KEY_PAGEDOWN:
			vitesse = maxf(1.0, vitesse / 4.0)
			print("Marée : vitesse x%.0f" % vitesse)
		elif k == KEY_PAGEUP:
			vitesse = minf(64.0, vitesse * 4.0)
			print("Marée : vitesse x%.0f" % vitesse)
		elif (event as InputEventKey).keycode == KEY_M:
			# touche logique (le M d'un clavier AZERTY n'est pas au même endroit qu'en QWERTY)
			_test_saut_maree()


# --- TEST, À RETIRER : la touche M saute au moment suivant de la marée (2026-11-22, essais de G3). ---
const _TEST_MOMENTS := [[0.25, "marée basse"], [0.5, "début de la montée"],
	[0.745, "marée haute, le carillon sonne dans 2 s"], [0.96, "début de la descente"]]
var _test_moment: int = -1


func _test_saut_maree() -> void:
	_test_moment = (_test_moment + 1) % _TEST_MOMENTS.size()
	var cible: float = float(_TEST_MOMENTS[_test_moment][0])
	temps = floorf(temps / duree_maree) * duree_maree + cible * duree_maree
	vitesse = 1.0
	print("Marée (test) : ", _TEST_MOMENTS[_test_moment][1])
# --- fin du TEST ---


## Où on en est dans le cycle, de 0 à 1 (0 = la mer commence à être basse).
func phase() -> float:
	return fposmod(temps, duree_maree) / duree_maree


## 0 = marée basse, 1 = marée haute, entre les deux pendant les transitions (adouci).
func hauteur_maree() -> float:
	# u = 0 au début de la descente ; la mer est à mi-hauteur en u = trans/2 (début de la basse mer « officielle »)
	var trans := duree_transition
	var demi := duree_maree * 0.5
	var u := fposmod(temps + trans * 0.5, duree_maree)
	var h: float
	if u < trans:
		h = 1.0 - u / trans                          # descente
	elif u < demi:
		h = 0.0                                   # basse
	elif u < demi + trans:
		h = (u - demi) / trans                       # montée
	else:
		h = 1.0                                   # haute
	return h * h * (3.0 - 2.0 * h)


## Le niveau de la mer en m (y du monde).
func niveau_mer() -> float:
	return lerpf(mer_basse, mer_haute, hauteur_maree())


func est_basse() -> bool:
	return hauteur_maree() < 0.5
