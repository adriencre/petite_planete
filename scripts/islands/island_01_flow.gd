extends Node
## Déroulement de la fin de l'île 1 :
## lanterne du sommet → toute l'île s'éveille, coucher de soleil, la mer monte,
## le phare de l'île 2 s'allume au loin → le robot embarque → fondu.
## (La barque est aussi atteignable dès le début par la langue de terre noyée de brume :
## dans ce cas, le phare s'allume au moment du départ.)

@export var summit_lantern: WakeLantern
@export var final_zone: WakeZone
@export var sky: SkyController
@export var water: Node3D
@export var boat: Boat
@export var distant_light: Node3D
@export var water_rise := 0.12 ## de combien la mer monte (mètres)
@export var sail_offset := Vector3(6, 0, 9) ## où la barque part, depuis sa place

@onready var _fade: ColorRect = $Fondu/Noir


func _ready() -> void:
	_fade.color.a = 0.0
	if summit_lantern:
		summit_lantern.lit_up.connect(_island_awakens)
	if boat:
		boat.boarded.connect(_depart)


func _island_awakens() -> void:
	await get_tree().create_timer(1.5).timeout
	if final_zone:
		final_zone.wake()
	var player := get_tree().get_first_node_in_group(&"player")
	if player:
		player.emote(&"happy", &"happy", 3.0)
	if sky:
		sky.go_to_sunset(12.0)
	if water:
		create_tween().tween_property(water, "position:y", water.position.y + water_rise, 6.0).set_trans(Tween.TRANS_SINE)
	await get_tree().create_timer(3.0).timeout
	if boat:
		boat.float_up()
	await get_tree().create_timer(4.0).timeout
	if distant_light:
		distant_light.answer()


func _depart(robot: Node3D) -> void:
	robot.busy = true
	robot.velocity = Vector3.ZERO
	robot.set_physics_process(false)
	# le robot rejoint le banc de la barque
	var hop := create_tween().set_trans(Tween.TRANS_SINE)
	hop.tween_property(robot, "global_position", boat.seat.global_position + Vector3.UP * 0.05, 0.8)
	await hop.finished
	robot.reparent(boat.seat)
	robot.model.rotation.y = 0.0
	robot.anim.play(&"idle")
	await get_tree().create_timer(1.0).timeout
	# un dernier regard vers l'île, puis on part
	create_tween().tween_property(robot.model, "rotation:y", PI, 1.2).set_trans(Tween.TRANS_SINE)
	robot.face.set_expression(&"sad", 0.6)
	await get_tree().create_timer(2.2).timeout
	robot.face.set_expression(&"neutral", 0.6)
	create_tween().tween_property(robot.model, "rotation:y", 0.0, 1.0).set_trans(Tween.TRANS_SINE)
	# au large, le phare de l'île 2 répond (s'il ne l'a pas déjà fait)
	# la caméra s'éloigne et s'abaisse pour montrer, au loin, le phare de l'île 2
	var cam := get_viewport().get_camera_3d()
	if cam and distant_light:
		var far := boat.global_position.lerp(distant_light.global_position, 0.5)
		cam.push_override(&"depart", 26.0, 16.0, 0.35, Vector3(far.x, 2.0, far.z))
	await get_tree().create_timer(1.5).timeout
	if distant_light and not distant_light.answered:
		distant_light.answer()
		robot.face.set_expression(&"surprised", 0.4)
	boat.sail_to(boat.global_position + sail_offset, 9.0)
	Audio.stinger("stinger_departure")
	await get_tree().create_timer(4.0).timeout
	Audio.fade_all(6.0)
	var fade := create_tween()
	fade.tween_property(_fade, "color:a", 1.0, 3.5)
	await fade.finished
	await get_tree().create_timer(2.0).timeout
	# Fin de l'île 1 (provisoire : on recommence en attendant l'île 2)
	get_tree().reload_current_scene()
