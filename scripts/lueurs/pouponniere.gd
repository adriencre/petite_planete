extends Node3D
## La Pouponnière : sous le plancher de l'abri, près de la chaleur du berceau, naissent les plus
## petites Lueurs de l'archipel. Elles se cachent dans les fentes quand le robot approche.
## De temps en temps, l'une d'elles est attirée par le berceau : elle glisse le long de la traînée
## jusqu'à lui… et disparaît. (La « Bouche » boit les petites. Visible seulement dans le noir.)

const HALO := preload("res://assets/lueurs/materials/lueur_halo.tres")

@export var trail: Path3D ## la traînée graine → berceau (dans l'abri)
@export var drift_every := Vector2(9.0, 15.0) ## intervalle entre deux petites aspirées (secondes)
@export var drift_time := 4.5

var _next := 6.0


func _process(delta: float) -> void:
	if trail == null or trail.curve == null or trail.curve.point_count < 2:
		return
	_next -= delta
	if _next > 0.0:
		return
	_next = randf_range(drift_every.x, drift_every.y)
	_drift()


func _drift() -> void:
	var orb := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(0.16, 0.16)
	quad.material = HALO
	orb.mesh = quad
	orb.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	trail.add_child(orb)
	var curve := trail.curve
	var length := curve.get_baked_length()
	var t := create_tween()
	t.tween_method(func(k: float) -> void:
		orb.position = curve.sample_baked(k * length, true) + Vector3.UP * (0.06 + sin(k * 9.0) * 0.02)
		orb.scale = Vector3.ONE * (1.0 - smoothstep(0.75, 1.0, k)),
		0.0, 1.0, drift_time).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_callback(orb.queue_free)
