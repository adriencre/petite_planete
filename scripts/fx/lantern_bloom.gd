extends Node3D
## Éclosion d'une lanterne : flash de lumière, anneau d'onde au sol qui s'élargit,
## et petites lumières qui montent. `big` = version de la première lumière.


func play(big := false) -> void:
	var ring: MeshInstance3D = $Ring
	var mat := ring.material_override as StandardMaterial3D
	var flash: OmniLight3D = $Flash
	var motes: CPUParticles3D = $Motes
	motes.amount = 60 if big else 30
	motes.emitting = true
	var reach := 9.0 if big else 4.5
	var t := create_tween().set_parallel()
	ring.scale = Vector3.ONE * 0.2
	t.tween_property(ring, "scale", Vector3(reach, 1, reach), 1.8 if big else 1.1).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	t.tween_property(mat, "albedo_color", Color(0, 0, 0), 1.8 if big else 1.1)
	flash.light_energy = 7.0 if big else 3.5
	t.tween_property(flash, "light_energy", 0.0, 1.2 if big else 0.7).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	await get_tree().create_timer(3.5).timeout
	queue_free()
