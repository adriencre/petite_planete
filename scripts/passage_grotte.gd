extends Area3D
## Passage par une arche noire (la grotte d'Aube, île 3) : quand le robot entre dans l'arche, l'écran
## passe au noir, il réapparaît à l'autre bout (`cible`), tourné comme le repère, puis l'image revient.
## La grotte est construite sous l'île, bien plus bas : ce fondu relie les marches de la ruelle à celles
## de la grotte (tools/blender/grotte_aube.py). Rien de magique : on descend dans le noir, on remonte vers le jour.

@export var cible: Node3D
@export var duree_noir: float = 0.7
@export var duree_retour: float = 1.1

var _voile: ColorRect


func _ready() -> void:
	body_entered.connect(_entree)
	var calque := CanvasLayer.new()
	calque.layer = 30
	add_child(calque)
	_voile = ColorRect.new()
	_voile.color = Color(0.03, 0.02, 0.05, 0.0)
	_voile.set_anchors_preset(Control.PRESET_FULL_RECT)
	_voile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	calque.add_child(_voile)


func _entree(corps: Node3D) -> void:
	if cible == null or not corps.is_in_group("joueur") or bool(corps.get("cinematique")):
		return
	var joueur := corps as CharacterBody3D
	joueur.set("cinematique", true)
	joueur.velocity = Vector3.ZERO
	var t := create_tween().set_trans(Tween.TRANS_SINE)
	t.tween_property(_voile, "color:a", 1.0, duree_noir)
	await t.finished
	# la grotte est sous l'île : on abaisse la limite de chute tant qu'on y est
	joueur.set("altitude_chute", minf(-2.0, cible.global_position.y - 10.0))
	joueur.global_position = cible.global_position
	joueur.velocity = Vector3.ZERO
	var vers := -cible.global_basis.z
	var modele: Node3D = joueur.get("modele")
	if modele:
		modele.rotation.y = atan2(vers.x, vers.z)
	await get_tree().create_timer(0.35, false).timeout
	var r := create_tween().set_trans(Tween.TRANS_SINE)
	r.tween_property(_voile, "color:a", 0.0, duree_retour)
	await r.finished
	joueur.set("cinematique", false)
