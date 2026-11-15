class_name FogDensityZone
extends Area3D
## Brume épaisse : à l'intérieur, la batterie se vide beaucoup plus vite…
## mais les Lueurs y sont si denses qu'on les devine même avec de l'énergie.
## (Une fois la zone réveillée par la lumière, elle n'a plus d'effet.)

@export var drain_multiplier := 25.0 ## vitesse de vidage par rapport à la brume normale
@export_range(0, 1) var vision := 0.55 ## Lueurs visibles à l'intérieur, même batterie pleine

var has_player := false


func _enter_tree() -> void:
	add_to_group(&"fog_density_zone")


func _ready() -> void:
	collision_layer = 0
	body_entered.connect(func(b: Node3D) -> void: if b.is_in_group(&"player"): has_player = true)
	body_exited.connect(func(b: Node3D) -> void: if b.is_in_group(&"player"): has_player = false)


## La zone où se trouve le robot (la plus épaisse), ou null.
static func current(tree: SceneTree) -> FogDensityZone:
	var best: FogDensityZone = null
	for z in tree.get_nodes_in_group(&"fog_density_zone"):
		if z.has_player and (best == null or z.drain_multiplier > best.drain_multiplier):
			best = z
	return best
