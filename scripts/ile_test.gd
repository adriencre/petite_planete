extends Node3D
## Île de test DA : collisions automatiques, robot posé sur le sol, vision trouble selon la batterie.

## Batterie sous laquelle la vision commence à se brouiller (trouble maximal à 0).
@export var seuil_trouble: float = 0.45

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


## Collisions pour ce qui est posé dans `Monde`. Une scène instanciée qui a déjà ses propres collisions
## (la maison du quai : « -col » du .glb) est laissée telle quelle : sinon son toit devient solide (une
## lanterne s'y pose), ses cirés et ses papiers bloquent le robot…
func _ajouter_collisions(n: Node) -> void:
	if n != monde and n.scene_file_path != "" and not n.find_children("*", "StaticBody3D", true, false).is_empty():
		return
	var mi := n as MeshInstance3D
	if mi and mi.mesh and not mi.mesh.get_faces().is_empty():   # (un mesh sans face : pas de collision possible)
		mi.create_trimesh_collision()
	for c in n.get_children():
		_ajouter_collisions(c)


func _process(_delta: float) -> void:
	var b: float = joueur.batterie
	vision.set_shader_parameter("trouble", clampf((seuil_trouble - b) / maxf(seuil_trouble, 0.01), 0.0, 1.0))
