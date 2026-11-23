extends Node
## La voûte d'une grotte vue de près (2026-11-22) : en 1re et en 3e personne, la roche referme la galerie
## au-dessus du robot ; en vue de dessus, la grotte est coupée à plat comme les maisons, et la voûte ne
## sert plus qu'à faire de l'ombre (elle reste invisible).

## Le nom de la voûte dans le modèle (tools/blender/grotte_aube.py).
@export var nom_voute: String = "Voute_grotte_aube"

var _voute: GeometryInstance3D
var _joueur: Node


func _ready() -> void:
	await get_tree().process_frame
	_voute = get_tree().current_scene.find_child(nom_voute, true, false) as GeometryInstance3D
	_joueur = get_tree().get_first_node_in_group("joueur")


func _process(_delta: float) -> void:
	if _voute == null or _joueur == null:
		return
	var dessus: bool = bool(_joueur.get("vue_dessus"))
	_voute.cast_shadow = (
		GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY if dessus
		else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	)
