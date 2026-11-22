extends Area3D
## Une zone de cadrage de la vue de dessus (camera_zones.gd). Quand le robot y entre, la caméra prend
## lentement cette orientation (et, si on les donne, cette distance et cet angle), puis ne bouge plus tant
## qu'il y reste. On règle le cadrage d'un quartier en déplaçant ou en redimensionnant ses volumes dans
## l'éditeur. Décidé le 2026-11-22 : un cadre stable par quartier, tourné vers ce qui intéresse le joueur.

## Orientation de la caméra (degrés, comme joueur.orientation_dessus) : direction où elle se place autour
## du robot. 0 = au sud du robot (elle regarde vers le nord), 90 = à l'est, -90 = à l'ouest.
@export var orientation: float = 45.0
## Distance et angle de plongée ; 0 = ceux de la scène.
@export var distance: float = 0.0
@export var angle: float = 0.0
## Quand deux zones se recouvrent (le parvis dans la ville haute), la plus haute l'emporte.
@export var priorite: int = 0


func _ready() -> void:
	add_to_group("zones_camera")
	collision_layer = 0
	monitorable = false
