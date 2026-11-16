@tool
extends Node3D
## Fait tourner ce nœud sur lui-même (oiseaux qui tournent au loin, etc.).

@export var vitesse: float = 0.08


func _process(delta: float) -> void:
	rotate_y(vitesse * delta)
