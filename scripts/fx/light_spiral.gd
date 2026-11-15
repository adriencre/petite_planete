class_name LightSpiral
extends RefCounted
## Petites lumières qui tournent en spirale d'un point jusqu'à une cible (l'antenne du robot).
## Utilisé par la pierre-soleil (le rayon descend dans l'antenne)
## et par les lanternes quand le robot reprend leur lumière.


## Lance la spirale ; renvoie un signal émis quand la dernière lumière arrive.
## `parent` porte les lumières et leurs tweens (il doit rester vivant jusqu'à la fin).
static func play(parent: Node, start: Vector3, target: Node3D, count := 14, duration := 2.6,
		radius := 0.9, turns := 2.2, color := Color(1.0, 0.82, 0.5)) -> Signal:
	var last: Tween
	for i in count:
		var orb := _orb(color)
		parent.add_child(orb)
		orb.global_position = start
		orb.visible = false
		var phase := TAU * i / count
		var delay := i * duration * 0.04
		var t := parent.create_tween()
		t.tween_interval(delay)
		t.tween_callback(orb.set.bind("visible", true))
		t.tween_method(func(k: float) -> void:
			var center := start.lerp(target.global_position, k)
			var a := phase + k * TAU * turns
			orb.global_position = center + Vector3(cos(a), 0, sin(a)) * (1.0 - k) * radius,
			0.0, 1.0, duration - delay).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		t.tween_callback(orb.queue_free)
		last = t
	return last.finished


static func _orb(color: Color) -> MeshInstance3D:
	var orb := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.035
	mesh.height = 0.07
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color.lightened(0.3)
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 3.0
	mesh.material = mat
	orb.mesh = mesh
	orb.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return orb
