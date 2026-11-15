extends Node
## À poser en premier dans une scène de présentation (maquette, planche) : tout le monde de l'ombre
## y est visible, sans robot ni antenne éteinte.


func _enter_tree() -> void:
	OmbreObjet.vision = -1.0


func _exit_tree() -> void:
	OmbreObjet.vision = 0.0
