extends Node
## La marée de la Colonie (G3, ILE_03_COLONIE.md) : la mer du lagon suit l'horloge du monde (HorlogeMonde),
## comme au Phare. Basse à -0,6 m, haute à +0,5 m ; c'est la marée haute qui met le lagon au niveau du
## premier sas de l'écluse.

## La surface de la mer de la scène.
@export var mer: Node3D
## Hauteur de la mer quand il n'y a pas d'horloge (dans l'éditeur).
@export var niveau_editeur: float = 0.0


func _process(_delta: float) -> void:
	if mer == null:
		return
	var horloge := get_node_or_null("/root/HorlogeMonde")
	mer.position.y = float(horloge.call("niveau_mer")) if horloge else niveau_editeur
