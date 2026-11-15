extends Node
## Donne au carnet la forme de l'île (lue dans le GridMap) pour qu'il en dessine la carte à l'encre.

@export var island: GridMap


func _ready() -> void:
	if island == null:
		return
	var heights := {}
	for c in island.get_used_cells():
		if c.y < 0:
			continue
		var key := Vector2i(c.x, c.z)
		heights[key] = maxi(heights.get(key, -1), c.y)
	Notebook.set_map(heights, Vector2(island.cell_size.x, island.cell_size.z), Vector2(island.global_position.x, island.global_position.z))
