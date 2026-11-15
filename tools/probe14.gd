extends SceneTree
func _initialize():
	var s = (load("res://scenes/islands/island_01.tscn") as PackedScene).instantiate()
	var g: GridMap = s.get_node("Island")
	for z in range(-15, -1):
		var row := "%4d " % z
		for x in range(-27, -12):
			row += "#" if g.get_cell_item(Vector3i(x, 0, z)) != -1 else "."
		print(row)
	s.free()
	quit()
