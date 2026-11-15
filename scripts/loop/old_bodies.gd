extends Node3D
## Fait réapparaître, à chaque boucle, les anciens corps du robot là où ils se sont éteints.
## Ce sont de simples statues : affaissées, yeux éteints, grises dans la brume.
## (Le robot ne sait pas que c'était lui.)

const ROBOT := preload("res://scenes/robot.tscn")
const BODY_SKETCH := preload("res://assets/textures/story/sketch_body.png")
const LUEUR_SHADER := preload("res://assets/shaders/lueur.gdshader")

## Corps déjà présents sur l'île avant même le premier réveil (« d'autres jardiniers »).
## Chaque point : x, y, z = position ; la rotation est donnée dans initial_yaws (radians).
@export var initial_bodies: PackedVector3Array = []
@export var initial_yaws: PackedFloat32Array = []


func _ready() -> void:
	var path := get_tree().current_scene.scene_file_path if get_tree().current_scene else owner.scene_file_path
	for i in initial_bodies.size():
		spawn_body(initial_bodies[i], initial_yaws[i] if i < initial_yaws.size() else 0.0)
	for b in Loop.bodies_for(path):
		spawn_body(b["pos"], b["yaw"])


func spawn_body(pos: Vector3, yaw: float) -> Node3D:
	var body: Node3D = ROBOT.instantiate()
	# ce n'est plus un robot : juste une coque
	body.set_script(null)
	body.get_node("Model/Rig/LookPivot/Head").set_script(null)
	var battery := body.get_node("Battery")
	body.remove_child(battery)
	battery.free()
	add_child(body)
	body.global_position = pos
	body.get_node("Model").rotation.y = yaw
	_make_lifeless(body)
	var anim: AnimationPlayer = body.get_node("AnimationPlayer")
	# assis, affaissé, la tête penchée sur ses mains (pose tirée de l'animation du réveil)
	anim.play(&"get_up")
	anim.seek(5.6, true)
	anim.pause()
	var head: Node3D = body.get_node("Model/Rig/LookPivot/Head")
	head.rotation.x = 0.65
	head.rotation.z = randf_range(-0.2, 0.2)
	body.get_node("Model/Rig/LookPivot/Head/Antenna").rotation.z = randf_range(0.4, 0.9)
	_add_landmark(pos)
	_add_lueurs(body)
	return body


# Des Lueurs posées sur le corps, visibles seulement dans le noir : elles s'en nourrissent.
func _add_lueurs(body: Node3D) -> void:
	var mat := ShaderMaterial.new()
	mat.shader = LUEUR_SHADER
	mat.set_shader_parameter("intensity", 2.6)
	mat.render_priority = 1
	var quad := QuadMesh.new()
	quad.size = Vector2(0.22, 0.22)
	quad.material = mat
	for i in 9:
		var dot := MeshInstance3D.new()
		dot.mesh = quad
		dot.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		body.add_child(dot)
		dot.position = Vector3(randf_range(-0.35, 0.35), randf_range(0.15, 1.1), randf_range(-0.35, 0.35))


# Quand le robot passe près d'un corps, il le croque dans son carnet (une petite croix sur la carte).
func _add_landmark(pos: Vector3) -> void:
	var mark := Landmark.new()
	mark.place_id = StringName("corps_%d_%d" % [roundi(pos.x * 2.0), roundi(pos.z * 2.0)])
	mark.sketch = BODY_SKETCH
	mark.map_icon = "body"
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 2.6
	shape.shape = sphere
	mark.add_child(shape)
	add_child(mark)
	mark.global_position = pos + Vector3.UP * 0.6


# Matériaux sans lumière, et grisés par la brume comme le reste du monde.
func _make_lifeless(node: Node) -> void:
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		mi.material_overlay = null
		var mat := mi.get_surface_override_material(0) as ShaderMaterial
		if mat:
			var dead := mat.duplicate() as ShaderMaterial
			dead.set_shader_parameter("wake_affected", true)
			dead.set_shader_parameter("emission_strength", 0.0)
			var name := String(mi.name)
			if name.begins_with("Eye") or name.begins_with("Cell") or name == "Tip":
				dead.set_shader_parameter("albedo", Color(0.25, 0.26, 0.3))
			mi.set_surface_override_material(0, dead)
	for child in node.get_children():
		_make_lifeless(child)
