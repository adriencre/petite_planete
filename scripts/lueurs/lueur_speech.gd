class_name LueurSpeech
extends Node3D
## Paroles de lumière : ce qu'une Lueur dit, en français, en mots qui flottent puis s'effacent comme de la buée.
## Plus le robot est dans le noir, plus on comprend :
##  - antenne allumée (vision faible) : rien ;
##  - batterie basse : des BRIBES (« …il… revient… ») ;
##  - antenne éteinte (N) : la phrase COMPLÈTE, recopiée dans le carnet (section « Paroles »).
## À poser comme enfant d'une Lueur (habitant, créature…) ou seul, n'importe où.
## Si le parent a une méthode can_speak(), elle doit renvoyer vrai pour que la Lueur parle.

signal said(full: bool)

const FONT := preload("res://assets/fonts/Caveat.ttf")
const COLOR := Color(0.6, 1.0, 0.9)

@export_multiline var text := ""
@export var id: StringName ## identifiant pour le carnet (vide = pas recopié)
@export var auto := true ## parle d'elle-même quand le robot approche
@export var hear_distance := 4.0
@export var repeat_delay := 12.0 ## avant de reparler au même robot (secondes)
@export var height := 1.2 ## hauteur des mots au-dessus de la Lueur
@export var word_time := 0.32 ## temps d'apparition de chaque mot
@export var requires_flag: StringName ## ne parle d'elle-même qu'après ce moment (flag de Loop), si renseigné

var _hush_id := 0 # change quand la parole est interrompue
var _label: Label3D
var _speaking := false
var _cooldown := 0.0
var _check := 0.0


func _ready() -> void:
	_label = Label3D.new()
	_label.font = FONT
	_label.font_size = 64
	_label.pixel_size = 0.0035
	_label.outline_size = 14
	_label.outline_modulate = Color(COLOR, 0.25)
	_label.modulate = Color(COLOR, 0.0)
	_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_label.no_depth_test = true
	_label.shaded = false
	_label.double_sided = true
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.width = 620.0
	_label.render_priority = 3
	_label.outline_render_priority = 2
	_label.position = Vector3.UP * height
	add_child(_label)


func _process(delta: float) -> void:
	_cooldown -= delta
	if not auto or _speaking or _cooldown > 0.0:
		return
	if requires_flag != &"" and not Loop.has_flag(requires_flag):
		return
	_check -= delta
	if _check > 0.0:
		return
	_check = 0.3
	var robot := get_tree().get_first_node_in_group(&"player") as Node3D
	if robot == null or robot.global_position.distance_to(global_position) > hear_distance:
		return
	if clarity() < 0.3 or _sibling_speaking():
		return
	say()


# Une même Lueur ne dit pas deux phrases à la fois.
func _siblings() -> Array[LueurSpeech]:
	var out: Array[LueurSpeech] = []
	var parent := get_parent()
	if parent:
		for c in parent.get_children():
			if c != self and c is LueurSpeech:
				out.append(c)
	return out


func _sibling_speaking() -> bool:
	for s in _siblings():
		if s._speaking:
			return true
	return false


## Fait taire cette parole tout de suite (une autre, plus importante, commence).
func hush() -> void:
	if not _speaking:
		return
	_hush_id += 1
	var t := create_tween()
	t.tween_property(_label, "modulate:a", 0.0, 0.3)
	await t.finished
	_label.text = ""
	_speaking = false
	_cooldown = repeat_delay


## À quel point le robot peut comprendre ici (0 = rien, 1 = tout).
func clarity() -> float:
	var robot := get_tree().get_first_node_in_group(&"player")
	if robot == null or not robot.has_node("Battery"):
		return 0.0
	if WakeZone.awake_at(get_tree(), global_position) > 0.5:
		return 0.0  # trop de lumière ici : elles se taisent
	var parent := get_parent()
	if parent and parent.has_method("can_speak") and not parent.can_speak():
		return 0.0
	return robot.get_node("Battery").vision()


## Dit la phrase (en bribes ou en entier selon le noir). Se termine quand les mots se sont effacés.
func say() -> void:
	if _speaking or text.strip_edges() == "":
		return
	var c := clarity()
	if c < 0.3:
		return
	var full := c >= 0.95
	await _show(_words(full, c), full, full and id != &"")


## Mise en scène : dit exactement ces mots (bribes écrites à la main), sans rien recopier.
func say_exact(line: String) -> void:
	if _speaking:
		return
	await _show(_split_fragments(line), false, false)


func _split_fragments(line: String) -> PackedStringArray:
	var out := PackedStringArray()
	for part in line.replace("…", " … ").split(" ", false):
		out.append(part)
	return out


func _show(words: PackedStringArray, full: bool, record: bool) -> void:
	for s in _siblings():
		s.hush()
	_hush_id += 1
	var my_id := _hush_id
	_speaking = true
	_label.text = ""
	_label.modulate.a = 1.0
	_label.position = Vector3.UP * height
	var shown := ""
	for w in words:
		# « …il… revient… » : les points de suspension collent au mot d'avant (sauf tout au début)
		if w == "…" or shown == "" or shown == "…":
			shown += w
		else:
			shown += " " + w
		_label.text = shown
		if w != "…":
			# un petit son de verre par mot de lumière
			Audio.play("glass_word_%d" % (randi() % 4), global_position, -14.0, randf_range(0.97, 1.03))
		await get_tree().create_timer(word_time * (0.6 if w == "…" else 1.0)).timeout
		if my_id != _hush_id:
			return
	if record:
		Notebook.add_parole(id, text)
	said.emit(full)
	# la phrase reste un moment, puis s'efface comme de la buée en montant un peu
	await get_tree().create_timer(2.2 + 0.08 * words.size()).timeout
	if my_id != _hush_id:
		return
	var t := create_tween().set_parallel()
	t.tween_property(_label, "modulate:a", 0.0, 1.6)
	t.tween_property(_label, "position:y", height + 0.25, 1.6)
	await t.finished
	_label.text = ""
	_speaking = false
	_cooldown = repeat_delay


## Les mots qu'on capte : tous si `full`, sinon une partie (toujours les mêmes, pour qu'on puisse recouper).
func _words(full: bool, c: float) -> PackedStringArray:
	var all := text.replace("\n", " ").split(" ", false)
	if full:
		return all
	var keep := clampf((c - 0.3) / 0.65, 0.0, 1.0) * 0.6 + 0.15
	var out := PackedStringArray()
	for i in all.size():
		var h := float(hash(String(id) + str(i) + all[i]) % 1000) / 1000.0
		if h < keep:
			out.append(all[i].trim_suffix(",").trim_suffix("."))
		elif out.is_empty() or out[out.size() - 1] != "…":
			out.append("…")
	if out.size() <= 1:
		out = PackedStringArray(["…", all[all.size() - 1].trim_suffix("."), "…"])
	return out
