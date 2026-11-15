extends Node3D
## Orbe d'énergie lancé par l'antenne du robot : vole en arc jusqu'à la cible puis éclate.


func fly_to(target: Vector3) -> void:
	var start := global_position
	var duration := clampf(start.distance_to(target) / 6.0, 0.35, 1.0)
	var tween := create_tween()
	tween.tween_method(func(t: float) -> void:
		global_position = start.lerp(target, t) + Vector3.UP * sin(t * PI) * 0.8,
		0.0, 1.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	await tween.finished
	_burst()


func _burst() -> void:
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "scale", Vector3.ONE * 3.0, 0.35)
	tween.tween_property($Light, "light_energy", 0.0, 0.35)
	tween.tween_property($Orb, "transparency", 1.0, 0.35)
	tween.chain().tween_callback(queue_free)
