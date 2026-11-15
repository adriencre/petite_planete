extends GPUParticles3D
## Nuée de Lueurs qui flotte dans la brume autour du robot.
## Toujours présente, mais invisible tant que l'antenne a de l'énergie (voir assets/shaders/lueur.gdshader).


func _process(_delta: float) -> void:
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	if player:
		global_position = player.global_position
