@tool
class_name OmbreObjet
extends LueurHabitat
## Racine de tout objet du monde de l'ombre modélisé dans Blender (maison, décor, habitant).
## - remplace chaque matériau du modèle par celui du jeu du même nom (assets/ombre/materials/) ;
## - apparaît quand le robot est dans le noir : il « pousse » du sol, d'abord près du robot (une vague) ;
## - sa collision n'existe que dans l'ombre (et pas tant que le robot est dedans) ;
## - cicatrice : dans une zone éclairée par une lanterne, il devient cendre grise (`collapsed`),
##   et se retisse lentement quand la lumière est reprise.
## Dans l'éditeur, il est toujours visible ; cocher `collapsed` montre la version en cendre.

const DIR := "res://assets/ombre/materials/%s.tres"

## Vision du robot (0 = antenne allumée, 1 = dans le noir). Réglée par la batterie du robot.
## -1 = tout visible (maquette, planche : voir ombre_tout_visible.gd).
static var vision := 0.0

@export var footprint := 1.2 ## rayon au sol : la collision attend que le robot en sorte
@export var grow := true ## pousse du sol en apparaissant (sinon simple fondu)

var _reveal := 1.0
var _ash := 0.0
var _wait := 0.0
var _meshes: Array[GeometryInstance3D] = []
var _lights: Array[OmniLight3D] = []
var _light_energy: Array[float] = []
var _layer := -1
var _sent_reveal := -1.0
var _sent_ash := -1.0
var _ash_tween: Tween


func _ready() -> void:
	# pas de recalage au sol au lancement : l'objet est posé à la bonne hauteur dans la scène
	# (le rayon touchait son propre toit, ou celui d'un voisin, et la maison se retrouvait en l'air)
	snap_to_ground = false
	_meshes.clear()
	_lights.clear()
	_light_energy.clear()
	_collect(self)
	var me: Node = self
	if me is CollisionObject3D:
		_layer = (me as CollisionObject3D).collision_layer
	if Engine.is_editor_hint():
		_reveal = 1.0
		_ash = 1.0 if collapsed else 0.0
		_push()
		return
	_reveal = 1.0 if vision < 0.0 else 0.0
	_ash = 1.0 if collapsed else 0.0
	_push()
	super._ready()


func _collect(node: Node) -> void:
	if node is MeshInstance3D and (node as MeshInstance3D).mesh:
		var mi := node as MeshInstance3D
		for i in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(i)
			if m and ResourceLoader.exists(DIR % m.resource_name):
				mi.set_surface_override_material(i, load(DIR % m.resource_name))
		_meshes.append(mi)
	elif node is OmniLight3D:
		_lights.append(node)
		_light_energy.append((node as OmniLight3D).light_energy)
	for c in node.get_children():
		# un habitant posé dans un objet garde son propre réglage
		if c is OmbreObjet:
			continue
		_collect(c)


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	var target := 1.0 if vision < 0.0 else smoothstep(0.3, 0.85, vision)
	if target > _reveal + 0.001:
		# la vague part du robot : plus on est loin, plus on attend
		_wait += delta
		var d := robot.global_position.distance_to(global_position) if robot else 0.0
		if _wait >= d * 0.045:
			_reveal = move_toward(_reveal, target, delta * 1.1)
	else:
		_wait = 0.0
		_reveal = move_toward(_reveal, target, delta * 2.5)
	_push()
	_update_collision(robot)


func _update_collision(robot: Node3D) -> void:
	if _layer < 0:
		return
	var me: Node = self
	var body := me as CollisionObject3D
	var want := _reveal > 0.6
	if want and body.collision_layer == 0 and robot:
		var flat := Vector2(robot.global_position.x - global_position.x, robot.global_position.z - global_position.z)
		if flat.length() < footprint * maxf(scale.x, scale.z):
			want = false  # le robot est dedans : on attend qu'il sorte
	# on ne retire jamais le sol sous les pieds du robot (pont, îlot…) : il reste tant qu'il est dessus
	if not want and body.collision_layer != 0 and robot and _standing_on(robot):
		want = true
	body.collision_layer = _layer if want else 0


func _standing_on(robot: Node3D) -> bool:
	var q := PhysicsRayQueryParameters3D.create(robot.global_position + Vector3.UP * 0.3, robot.global_position + Vector3.DOWN * 0.6)
	q.exclude = [robot.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	return not hit.is_empty() and hit.collider == self


## Envoie l'apparition et la cendre aux matériaux, aux lumières et à la forme.
func _push() -> void:
	if absf(_reveal - _sent_reveal) > 0.004 or absf(_ash - _sent_ash) > 0.004:
		_sent_reveal = _reveal
		_sent_ash = _ash
		for m in _meshes:
			if is_instance_valid(m):
				m.set_instance_shader_parameter(&"reveal", _reveal)
				m.set_instance_shader_parameter(&"ash", _ash)
		for i in _lights.size():
			_lights[i].light_energy = _light_energy[i] * _reveal * (1.0 - _ash)
			_lights[i].visible = _reveal > 0.02 and _ash < 0.98
		var model := get_node_or_null("Modele") as Node3D
		if model and grow:
			var k := 1.0 - pow(1.0 - _reveal, 3.0)
			var sag := 1.0 - 0.22 * _ash
			model.scale = Vector3(lerpf(0.8, 1.0, k), lerpf(0.15, 1.0, k) * sag, lerpf(0.8, 1.0, k))
			model.rotation.z = 0.07 * _ash


func is_shown() -> bool:
	return _reveal > 0.5


# ---- cicatrices (remplace la version « Vivant / Effondre » de LueurHabitat)
func _apply() -> void:
	if not is_inside_tree():
		return
	if Engine.is_editor_hint():
		_ash = 1.0 if collapsed else 0.0
		_sent_ash = -1.0
		_push()


func _change(to_collapsed: bool) -> void:
	collapsed = to_collapsed
	collapsed_changed.emit(to_collapsed)
	if _ash_tween:
		_ash_tween.kill()
	_ash_tween = create_tween()
	# la lumière brûle vite ; on retisse lentement
	_ash_tween.tween_property(self, "_ash", 1.0 if to_collapsed else 0.0, 0.7 if to_collapsed else rebuild_time) \
			.set_trans(Tween.TRANS_SINE)
