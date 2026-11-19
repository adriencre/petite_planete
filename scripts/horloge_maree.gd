@tool
extends Node
## L'horloge de marée de la maison du quai : une seule aiguille, qui suit la vraie marée (HorlogeMonde).
## Cadran : moitié basse claire = basse mer, moitié haute foncée = haute mer. L'aiguille fait un tour par
## cycle, dans le sens inverse des aiguilles d'une montre : à gauche au début de la basse mer, en bas au
## milieu, à droite à la fin, en haut à marée haute (comme les petites horloges du cahier des passages).
## Elle tourne autour de son axe Z local (perpendiculaire au mur), pivot = centre du cadran.

@export var aiguille: Node3D
## Dans l'éditeur (pas d'HorlogeMonde) : où on en est dans le cycle (0 = début de la basse mer, 0,5 = début de la haute).
@export_range(0.0, 1.0) var apercu: float = 0.1


func _process(_delta: float) -> void:
	if aiguille == null:
		return
	var f := apercu
	var horloge := get_node_or_null("/root/HorlogeMonde")
	if horloge and not Engine.is_editor_hint():
		f = float(horloge.call("phase"))
	# pointe en haut = 0 ; +PI/2 = vers la gauche (vu de face) ; puis en bas, à droite, en haut
	aiguille.rotation.z = PI * 0.5 + TAU * f
