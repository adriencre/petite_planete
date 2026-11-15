@tool
class_name LueurHabitat
extends Node3D
## Un décor des Lueurs (maison-cocon, jardin, place…), visible seulement dans le noir.
## Deux versions dans la scène : « Vivant » (tissé de lumière) et « Effondre » (cendre grise).
## Cicatrices : si `follow_wake`, le décor s'effondre quand une lanterne allumée réveille sa zone
## (un désert gris où personne ne peut vivre), et se RETISSE lentement quand la lumière est reprise.
## Dans l'éditeur, cocher `collapsed` montre la version effondrée.

signal collapsed_changed(is_collapsed: bool)

@export var collapsed := false:
	set(value):
		collapsed = value
		_apply()
@export var follow_wake := true ## s'effondre dans les zones éclairées, se retisse dans le noir
@export var snap_to_ground := true ## au lancement, se pose sur le sol (pratique pour placer vite)
@export var rebuild_time := 7.0 ## durée pour se retisser (secondes)

var _check := 0.0
var _snapped := false
var _tween: Tween


func _ready() -> void:
	_apply()


func _physics_process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	if snap_to_ground and not _snapped:
		_snapped = true
		global_position.y = ground_y(self, global_position)
	if not follow_wake:
		return
	_check -= delta
	if _check > 0.0:
		return
	_check = 0.5
	var lit := WakeZone.awake_at(get_tree(), global_position) > 0.5
	if lit != collapsed:
		_change(lit)


## Hauteur du sol sous un point (rayon vers le bas), ou la hauteur actuelle si rien n'est touché.
static func ground_y(node: Node3D, pos: Vector3) -> float:
	var q := PhysicsRayQueryParameters3D.create(pos + Vector3.UP * 3.0, pos + Vector3.DOWN * 6.0)
	var hit := node.get_world_3d().direct_space_state.intersect_ray(q)
	return hit.position.y if hit else pos.y


# Effondrement rapide (la lumière brûle), reconstruction lente (on retisse fil à fil).
func _change(to_collapsed: bool) -> void:
	collapsed = to_collapsed
	collapsed_changed.emit(to_collapsed)
	var alive := get_node_or_null("Vivant") as Node3D
	var dead := get_node_or_null("Effondre") as Node3D
	if _tween:
		_tween.kill()
	_tween = create_tween()
	if to_collapsed:
		if dead:
			dead.scale = Vector3(1.0, 1.6, 1.0)
			_tween.tween_property(dead, "scale", Vector3.ONE, 0.6).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	elif alive:
		alive.scale = Vector3(0.6, 0.05, 0.6)
		_tween.tween_property(alive, "scale", Vector3.ONE, rebuild_time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _apply() -> void:
	if not is_inside_tree():
		return
	var alive := get_node_or_null("Vivant") as Node3D
	var dead := get_node_or_null("Effondre") as Node3D
	if alive:
		alive.visible = not collapsed
	if dead:
		dead.visible = collapsed
