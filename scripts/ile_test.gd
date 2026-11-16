extends Node3D
## Île de test DA : collisions automatiques, robot posé sur le sol, vision trouble selon la batterie.

@onready var monde: Node3D = $Monde
@onready var joueur = $Joueur  # joueur.gd
@onready var vision: ShaderMaterial = ($Vision/Ecran as ColorRect).material


func _ready() -> void:
	_ajouter_collisions(monde)
	await get_tree().physics_frame
	var espace := get_world_3d().direct_space_state
	var p: Vector3 = joueur.global_position
	var q := PhysicsRayQueryParameters3D.create(Vector3(p.x, 60.0, p.z), Vector3(p.x, -10.0, p.z))
	var hit := espace.intersect_ray(q)
	if hit:
		joueur.global_position = (hit.position as Vector3) + Vector3.UP * 0.1
		joueur.set("_depart", joueur.global_position)


func _ajouter_collisions(n: Node) -> void:
	if n is MeshInstance3D and not (n is MultiMeshInstance3D):
		(n as MeshInstance3D).create_trimesh_collision()
	for c in n.get_children():
		_ajouter_collisions(c)


func _process(_delta: float) -> void:
	var b: float = joueur.batterie
	vision.set_shader_parameter("trouble", clampf((0.45 - b) / 0.4, 0.0, 1.0))
