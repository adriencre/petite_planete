extends Node3D
## Robot Meshy (squelette + animations du .glb) : joue « attente », « marche » ou « course »
## selon la vitesse réelle du joueur, avec un fondu entre les trois.
## Les scènes (lanternes…) peuvent imposer une animation avec `jouer_action()` puis `fin_action()`.

@export_group("Seuils (m/s)")
## Au-dessus : le robot marche. En dessous : il attend.
@export var seuil_marche: float = 0.35
## Au-dessus : le robot court.
@export var seuil_course: float = 4.8
@export_group("Cadence")
## Vitesse au sol pour laquelle « marche » est jouée à 1× (mesurée sur l'animation : ~1 m/s).
@export var vitesse_naturelle_marche: float = 1.0
## Idem pour « course » (~1,7 m/s).
@export var vitesse_naturelle_course: float = 1.7
## Accélération maximale des animations : plus haut = moins de pieds qui glissent, mais des pas plus frénétiques.
@export var acceleration_max: float = 1.7
## Durée du fondu entre deux animations (s).
@export var fondu: float = 0.25

const EN_BOUCLE: Array[String] = ["attente", "marche", "course", "assis", "ramer"]
## Boucles en aller-retour : poses tenues (à genoux devant la lanterne).
const EN_ALLER_RETOUR: Array[String] = ["brancher_attente"]
const OS_MAIN_DROITE := "RightHand"

var _anim: AnimationPlayer = null
var _squelette: Skeleton3D = null
var _os_main: int = -1
var _prec: Vector3 = Vector3.ZERO
var _vitesse: float = 0.0
var _actuelle: String = ""
var _action: bool = false


func _ready() -> void:
	_anim = find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _anim == null:
		push_warning("robot_meshy_anim : aucun AnimationPlayer dans le modèle.")
		return
	for nom: String in EN_BOUCLE:
		if _anim.has_animation(nom):
			_anim.get_animation(nom).loop_mode = Animation.LOOP_LINEAR
		else:
			push_warning("robot_meshy_anim : animation « %s » absente." % nom)
	if _anim.has_animation("echelle_cycle"):
		_anim.get_animation("echelle_cycle").loop_mode = Animation.LOOP_LINEAR
	for nom: String in EN_ALLER_RETOUR:
		if _anim.has_animation(nom):
			_anim.get_animation(nom).loop_mode = Animation.LOOP_PINGPONG
	for n: Node in find_children("*", "Skeleton3D", true, false):
		_squelette = n as Skeleton3D
		_os_main = _squelette.find_bone(OS_MAIN_DROITE)
		break
	_prec = global_position
	_jouer("attente")


func _physics_process(delta: float) -> void:
	if _anim == null:
		return
	var dp: Vector3 = global_position - _prec
	_prec = global_position
	var v: float = Vector2(dp.x, dp.z).length() / maxf(delta, 0.0001)
	_vitesse = lerpf(_vitesse, v, 1.0 - exp(-10.0 * delta))
	if _action:
		return
	# petite marge pour ne pas clignoter entre deux animations autour d'un seuil
	var marge: float = 0.4 if _actuelle == "course" else 0.0
	if _vitesse > seuil_course - marge:
		_jouer("course")
		_anim.speed_scale = clampf(_vitesse / vitesse_naturelle_course, 0.8, acceleration_max)
	elif _vitesse > seuil_marche:
		_jouer("marche")
		_anim.speed_scale = clampf(_vitesse / vitesse_naturelle_marche, 0.6, acceleration_max)
	else:
		_jouer("attente")
		_anim.speed_scale = 1.0


func _jouer(nom: String) -> void:
	if nom == _actuelle or not _anim.has_animation(nom):
		return
	_actuelle = nom
	_anim.play(nom, fondu)


# ---------------------------------------------------------------- pour les scènes

## Vrai si le modèle possède l'animation `nom`.
func a_animation(nom: String) -> bool:
	return _anim != null and _anim.has_animation(nom)


## Durée de l'animation `nom` à vitesse 1 (0 si elle n'existe pas).
func duree(nom: String) -> float:
	if not a_animation(nom):
		return 0.0
	return _anim.get_animation(nom).length


## Joue une animation imposée ; la marche automatique est suspendue jusqu'à `fin_action()`.
func jouer_action(nom: String, vitesse: float = 1.0, fondu_action: float = 0.3) -> void:
	if not a_animation(nom):
		return
	_action = true
	_actuelle = nom
	_anim.speed_scale = 1.0
	_anim.play(nom, fondu_action, vitesse, vitesse < 0.0)


## Rend la main à la marche automatique.
func fin_action() -> void:
	_action = false
	if _anim:
		_anim.speed_scale = 1.0


## Vitesse de l'animation imposée en cours (ex. ramer plus ou moins vite).
func regler_vitesse(v: float) -> void:
	if _anim:
		_anim.speed_scale = v


## Avancement (0..1) de l'animation en cours : pour caler un objet dessus (les rames).
func avancement() -> float:
	if _anim == null or _anim.current_animation == "":
		return 0.0
	return _anim.current_animation_position / maxf(_anim.current_animation_length, 0.001)


## Fige l'animation en cours sur sa pose actuelle (ou la relance).
func figer(oui: bool) -> void:
	if _anim:
		_anim.speed_scale = 0.0 if oui else 1.0


## Position (monde) du poignet droit, d'où sort le câble.
func main_droite_monde() -> Vector3:
	if _squelette == null or _os_main < 0:
		return global_position + Vector3.UP
	return _squelette.global_transform * _squelette.get_bone_global_pose(_os_main).origin
