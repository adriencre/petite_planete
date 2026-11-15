extends SceneTree
# Étape 14 : île 1 adaptée au design v3.
const PATH := "res://scenes/islands/island_01.tscn"
const GRASS := 0
const PATH_ITEM := 1
const STONE := 2

var scene_root: Node3D
var grid: GridMap


func _initialize() -> void:
	scene_root = (load(PATH) as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_MAIN)
	grid = scene_root.get_node("Island")
	_upgrade()
	var out := PackedScene.new()
	print("pack: ", out.pack(scene_root))
	print("save: ", ResourceSaver.save(out, PATH))
	scene_root.free()
	quit()


func _own(node: Node) -> void:
	node.owner = scene_root
	for c in node.get_children():
		if c.owner == null:
			_own(c)


func _instance(path: String, parent: Node, name: String, pos: Vector3, yaw := 0.0) -> Node3D:
	var n: Node3D = (load(path) as PackedScene).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	n.name = name
	parent.add_child(n)
	n.owner = scene_root
	n.position = pos
	n.rotation.y = yaw
	return n


func _land(x: int, z: int, path := false) -> void:
	if grid.get_cell_item(Vector3i(x, 0, z)) != -1:
		return
	for y in range(-3, 1):
		grid.set_cell_item(Vector3i(x, y, z), PATH_ITEM if (path and y == 0) else GRASS)


func _top_at(x: float, z: float) -> float:
	for y in range(14, -4, -1):
		var item := grid.get_cell_item(Vector3i(floori(x), y, floori(z)))
		if item == 3:
			return y * 0.5 + 0.25
		if item != -1:
			return (y + 1) * 0.5
	return 0.0


func _upgrade() -> void:
	var blockout := scene_root.get_node("Blockout")

	# 1. la langue de terre cachée (nord-ouest), qui s'avance dans la mer jusqu'à une petite crique
	var a := Vector2(-17.5, -4.5)
	var b := Vector2(-23.5, -11.5)
	for i in 41:
		var p := a.lerp(b, i / 40.0)
		for dx in [-1, 0, 1]:
			for dz in [-1, 0, 1]:
				var c := Vector2(p.x + dx * 0.55, p.y + dz * 0.55)
				_land(floori(c.x), floori(c.y), absf(dx) + absf(dz) == 0)
	for x in range(-21, -18):  # petit replat au milieu (la pierre secrète)
		for z in range(-9, -6):
			_land(x, z)
	for x in range(-25, -22):  # replat au bout (la barque)
		for z in range(-13, -10):
			_land(x, z)

	# 2. la barque, cachée au bout, déjà à flot
	var boat: Node3D = blockout.get_node("Barque")
	boat.position = Vector3(-24.0, 0.12, -13.9)
	boat.rotation.y = 0.6
	boat.set("start_floating", true)
	var flow := scene_root.get_node("Deroulement")
	flow.set("sail_offset", Vector3(-6, 0, -5))
	for l in scene_root.get_node("Lieux").get_children():
		if String(l.name) == "Lieu_barque":
			l.position = Vector3(-23.5, 1.3, -12.0)

	# 3. brume épaisse sur tout le chemin
	var zone := Area3D.new()
	zone.name = "BrumeEpaisse"
	zone.set_script(load("res://scripts/world/fog_density_zone.gd"))
	zone.position = Vector3(-21.5, 1.0, -8.8)
	var col := CollisionShape3D.new()
	col.name = "Shape"
	var shape := BoxShape3D.new()
	shape.size = Vector3(6.0, 3.0, 12.0)
	col.shape = shape
	col.rotation.y = deg_to_rad(35)
	zone.add_child(col)
	scene_root.add_child(zone)
	_own(zone)

	# 4. la pierre-soleil secrète, au milieu, dans la brume épaisse
	var hidden := _instance("res://assets/props/sun_stone.tscn", blockout, "PierreSoleilCachee",
		Vector3(-18.7, _top_at(-18.7, -8.4), -8.4), -1.57)
	hidden.set("flag_id", &"sunstone_hidden")
	var beam: Node3D = hidden.get_node("Beam")
	beam.position.y = 2.0
	beam.scale = Vector3(0.7, 0.4, 0.7)
	hidden.get_node("LightPool").set("radius", 1.1)

	# 5. une traînée de Lueurs y mène depuis l'entrée de la langue de terre
	var trail := Path3D.new()
	trail.name = "TraineePierreCachee"
	trail.set_script(load("res://scripts/lueurs/lueur_trail.gd"))
	var curve := Curve3D.new()
	for q in [Vector2(-16.0, -3.8), Vector2(-17.3, -4.8), Vector2(-18.2, -6.0), Vector2(-18.9, -6.9), Vector2(-19.3, -7.8)]:
		curve.add_point(Vector3(q.x, _top_at(q.x, q.y) + 0.04, q.y))
	trail.curve = curve
	scene_root.get_node("Lueurs").add_child(trail)
	_own(trail)

	# 6. un « autre jardinier » éteint à l'entrée de la langue de terre, tourné vers la mer
	var bodies := scene_root.get_node("AnciensCorps")
	bodies.set("initial_bodies", PackedVector3Array([Vector3(-18.6, _top_at(-18.6, -5.6), -5.6)]))
	bodies.set("initial_yaws", PackedFloat32Array([deg_to_rad(-135)]))

	# 7. au loin, le phare de l'île 2 (sa lumière « répond » quand l'île s'éveille)
	var far: Node3D = scene_root.get_node("IleLointaine")
	far.position = Vector3(-36, 0, -30)
	var tower := MeshInstance3D.new()
	tower.name = "Phare"
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.8
	cyl.bottom_radius = 1.2
	cyl.height = 7.0
	cyl.radial_segments = 10
	tower.mesh = cyl
	tower.material_override = load("res://assets/materials/wall_plaster.tres")
	tower.position = Vector3(1, 3.9, 0.5)
	far.add_child(tower)
	var cap := MeshInstance3D.new()
	cap.name = "Toit"
	var cone := CylinderMesh.new()
	cone.top_radius = 0.0
	cone.bottom_radius = 1.1
	cone.height = 1.2
	cone.radial_segments = 10
	cap.mesh = cone
	cap.material_override = load("res://assets/materials/roof.tres")
	cap.position = Vector3(1, 8.3, 0.5)
	far.add_child(cap)
	_own(tower)
	_own(cap)
	var light: Node3D = far.get_node("Lumiere")
	light.position = Vector3(1, 6.6, 0.5)
