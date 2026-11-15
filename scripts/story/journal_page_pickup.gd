extends Node3D
## Une page du journal de la Gardienne, posée sous une pierre.
## Le robot la ramasse : elle rejoint son carnet, qui s'ouvre directement dessus.
## Page lumineuse : l'écriture n'apparaît que dans le noir (antenne faible ou éteinte, et aucune lanterne
## allumée tout près) ; sinon la page semble blanche.

const LUEUR_SHADER := preload("res://assets/shaders/lueur.gdshader")

@export var page: JournalPage
@export var read_vision := 0.35 ## page lumineuse : il faut au moins ce niveau de « vision » pour la lire

@onready var _interactable: Interactable = $Interactable
@onready var _writing: Node3D = $Sheet/Ecriture


func _ready() -> void:
	if page == null or Notebook.has_journal_page(page.number):
		queue_free()
		return
	var mat: Material
	if page.luminous:
		var lueur := ShaderMaterial.new()
		lueur.shader = LUEUR_SHADER
		lueur.set_shader_parameter("billboard", false)
		lueur.set_shader_parameter("round_sprite", false)
		lueur.set_shader_parameter("intensity", 2.4)
		lueur.render_priority = 1
		mat = lueur
	else:
		var ink := StandardMaterial3D.new()
		ink.albedo_color = Color(0.31, 0.25, 0.22)
		mat = ink
	for line in _writing.get_children():
		(line as MeshInstance3D).material_override = mat
	_interactable.interacted.connect(_on_take)


func _on_take(robot: Node3D) -> void:
	if page.luminous and (robot.battery.vision() < read_vision or WakeZone.awake_at(get_tree(), global_position) > 0.5):
		# une page blanche… (il faudrait la voir dans le noir)
		robot.face.set_expression(&"curious", 0.4)
		await robot.face_toward(global_position, 0.4)
		robot.emote(&"curious", &"", 1.5)
		return
	_interactable.enabled = false
	robot.busy = true
	robot.velocity = Vector3.ZERO
	robot.face.set_expression(&"curious", 0.4)
	await robot.face_toward(global_position, 0.4)
	await get_tree().create_timer(0.4).timeout
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	tween.tween_property($Sheet, "global_position", robot.carry_point.global_position, 0.6)
	tween.tween_property($Sheet, "scale", Vector3.ONE * 0.3, 0.6)
	await tween.finished
	$Sheet.visible = false
	Audio.play("page_turn", null, -4.0)
	Audio.stinger("stinger_discovery")
	if not Notebook.is_unlocked:
		Notebook.unlock()
	Notebook.add_journal_page(page)
	robot.busy = false
	await get_tree().create_timer(0.5).timeout
	Notebook.open(Notebook.spread_of_journal(page.number))
	queue_free()
