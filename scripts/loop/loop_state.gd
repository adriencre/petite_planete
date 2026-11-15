extends CanvasLayer
## La boucle (accessible partout sous le nom « Loop »).
## Quand la batterie du robot est vide, son corps s'éteint sur place et reste dans le monde.
## Sa conscience retourne au berceau de l'abri : l'île est rechargée, toutes les lumières
## allumées pendant cette boucle sont éteintes, et un corps neuf se réveille.
## Ce qui survit d'une boucle à l'autre : les anciens corps, le carnet, et ce qu'on a découvert (flags).

signal loop_started(count: int)

## Nombre de boucles déjà terminées (0 = premier réveil).
var count := 0
## Anciens corps : [{scene, pos, yaw}]
var bodies: Array[Dictionary] = []
## Découvertes qui restent vraies d'une boucle à l'autre (ex. &"sunstone_used").
var flags := {}

var _ending := false

@onready var _black: ColorRect = $Noir


func _ready() -> void:
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	_black.color.a = 0.0
	_black.visible = false


func has_flag(name: StringName) -> bool:
	return flags.get(name, false)


func set_flag(name: StringName, value := true) -> void:
	flags[name] = value


## Anciens corps laissés sur cette scène.
func bodies_for(scene_path: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for b in bodies:
		if b["scene"] == scene_path:
			out.append(b)
	return out


## Fin de la boucle : le corps reste où il est, l'écran s'éteint, l'île recommence.
func end_loop(robot: Node3D) -> void:
	if _ending:
		return
	_ending = true
	var scene_path := get_tree().current_scene.scene_file_path
	bodies.append({"scene": scene_path, "pos": robot.global_position, "yaw": robot.model.rotation.y})
	count += 1
	# un moment de silence sur le corps éteint, puis le noir
	await get_tree().create_timer(1.8).timeout
	Audio.fade_all(3.0)
	_black.visible = true
	var t := create_tween()
	t.tween_property(_black, "color:a", 1.0, 2.5).set_trans(Tween.TRANS_SINE)
	await t.finished
	await get_tree().create_timer(1.5).timeout
	Notebook.reset_progress()
	get_tree().reload_current_scene()
	await get_tree().process_frame
	await get_tree().process_frame
	# l'ouverture de l'île a son propre écran noir : on peut retirer le nôtre
	_black.color.a = 0.0
	_black.visible = false
	_ending = false
	loop_started.emit(count)
