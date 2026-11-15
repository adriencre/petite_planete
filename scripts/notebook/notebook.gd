extends CanvasLayer
## Le carnet du robot (accessible partout sous le nom « Notebook »). Aucun symbole, aucune langue inventée.
## Dans l'ordre :
##  - la CARTE de l'île (à l'encre ; lieux découverts : vide = à faire, doré = fait ; anciens corps) ;
##  - les CROQUIS des lieux que le robot a vus ;
##  - le BESTIAIRE : les créatures des Lueurs, croquées dans le noir (une par page) ;
##  - les PAROLES : ce que les Lueurs ont dit, entendu en entier dans le noir, recopié à l'encre turquoise ;
##  - les pages du JOURNAL DE LA GARDIENNE, en français (les pages lumineuses : écriture claire sur fond nuit) ;
##  - de vieux croquis déjà dans le carnet : de vrais endroits de l'île, qui servent d'indices.
## Ouvrir : Tab (une fois le carnet trouvé). Tourner les pages : Q / D. Fermer : E, Tab ou Échap.

signal unlocked
signal place_added(id: StringName)
signal creature_added(entry: CreatureEntry)
signal journal_page_added(page: JournalPage)

const SKETCH_PATH := "res://assets/textures/story/%s.png"
const INK := Color(0.31, 0.25, 0.22, 0.92)
const HAND_FONT := preload("res://assets/fonts/Caveat.ttf")
const NIGHT := Color(0.07, 0.1, 0.17)
const LUEUR := Color(0.55, 1.0, 0.88)
const TURQUOISE_INK := Color(0.16, 0.5, 0.47, 0.95)
const PAROLES_PER_PAGE := 5

## Anciens croquis du carnet : chacun montre un vrai lieu de l'île.
## Ce sont des indices : la pierre au rayon de soleil, la chaîne de lanternes, le terreau au pied de la falaise,
## la grotte derrière la cascade… (et déjà, sans qu'on le sache, les arbres roses et le pollen).
const OLD_NOTES := [
	{"sketch": "sketch_sunstone"},
	{"sketch": "sketch_lantern_chain"},
	{"sketch": "sketch_soil_cliff"},
	{"sketch": "sketch_cascade"},
	{"sketch": "sketch_tree"},
	{"sketch": "sketch_night"},  # un robot antenne éteinte sous la lune, et une touche « N » griffonnée
]

var is_unlocked := false
var is_open := false
var places := {}           # id -> {sketch, pos, icon, done_icon, done}
var place_order: Array[StringName] = []
var creatures := {}        # id -> CreatureEntry
var journal := {}          # numéro -> JournalPage
var paroles: Array[Dictionary] = []  # [{id, text}] dans l'ordre où on les a entendues
var _map_heights := {}
var _map_cell := Vector2.ONE
var _map_origin := Vector2.ZERO
var _spread := 0  # double page affichée

@onready var _book: Control = $Book
@onready var _dim: ColorRect = $Dim
@onready var _left: VBoxContainer = $Book/LeftPage/Margin/Content
@onready var _right: VBoxContainer = $Book/RightPage/Margin/Content
@onready var _dots: HBoxContainer = $Book/Dots
@onready var _toast: Control = $Toast
@onready var _toast_picture: TextureRect = $Toast/Row/Picture


func _ready() -> void:
	_set_visible(false)
	_toast.modulate.a = 0.0


# ---------- données ----------
func unlock() -> void:
	if is_unlocked:
		return
	is_unlocked = true
	unlocked.emit()
	_show_toast(null)


## Un lieu vu par le robot : son croquis rejoint le carnet, son icône apparaît sur la carte.
func add_place(id: StringName, sketch: Texture2D, world_pos: Vector3, icon: StringName, done_icon: StringName = &"") -> void:
	if places.has(id):
		return
	places[id] = {"sketch": sketch, "pos": world_pos, "icon": icon, "done_icon": done_icon, "done": false}
	place_order.append(id)
	place_added.emit(id)
	if is_unlocked:
		_show_toast(sketch)
		Audio.play("pencil_sketch", null, -10.0)


## Une créature des Lueurs vue de près dans le noir : elle entre dans le bestiaire.
func add_creature(entry: CreatureEntry) -> void:
	if entry == null or creatures.has(entry.id):
		return
	creatures[entry.id] = entry
	creature_added.emit(entry)


## Petit croquis qui s'ajoute au carnet, en haut à droite (avec le bruit du crayon).
func show_sketch_toast(picture: Texture2D) -> void:
	if is_unlocked:
		_show_toast(picture)
		Audio.play("pencil_sketch", null, -8.0)


func has_creature(id: StringName) -> bool:
	return creatures.has(id)


## Une page du journal de la Gardienne, glissée dans le carnet.
func add_journal_page(page: JournalPage) -> void:
	if page == null or journal.has(page.number):
		return
	journal[page.number] = page
	journal_page_added.emit(page)


## Une parole de Lueur entendue en entier : recopiée dans le carnet (une seule fois).
func add_parole(id: StringName, text: String) -> void:
	for p in paroles:
		if p["id"] == id:
			return
	paroles.append({"id": id, "text": text})
	if is_unlocked:
		_show_toast(null)
		Audio.play("pencil_sketch", null, -12.0, 1.15)


func has_parole(id: StringName) -> bool:
	for p in paroles:
		if p["id"] == id:
			return true
	return false


func has_journal_page(number: int) -> bool:
	return journal.has(number)


## Double page où se trouve une page du journal (pour ouvrir le carnet directement dessus).
func spread_of_journal(number: int) -> int:
	var pages := _pages()
	for i in pages.size():
		var page: JournalPage = pages[i].get("journal")
		if page and page.number == number:
			return i / 2
	return 0


## Le lieu est accompli (ex. la lanterne est rallumée) : il devient doré sur la carte.
func set_place_done(id: StringName) -> void:
	if places.has(id):
		places[id]["done"] = true


## Nouvelle boucle : les lieux restent connus, mais plus rien n'y est « fait » (la lumière s'est éteinte).
func reset_progress() -> void:
	for id in places:
		places[id]["done"] = false


## Forme de l'île, fournie par l'île elle-même (scripts/notebook/island_map_source.gd).
func set_map(heights: Dictionary, cell: Vector2, origin: Vector2) -> void:
	_map_heights = heights
	_map_cell = cell
	_map_origin = origin


# ---------- ouverture / fermeture ----------
func open(spread := -1) -> void:
	if not is_unlocked:
		return
	is_open = true
	if spread >= 0:
		_spread = spread
	_build_spread()
	_set_visible(true)
	Audio.play("book_open", null, -6.0)
	_book.scale = Vector2(0.92, 0.92)
	_book.modulate.a = 0.0
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	t.tween_property(_book, "scale", Vector2.ONE, 0.3)
	t.tween_property(_book, "modulate:a", 1.0, 0.2)
	_set_player_busy(true)


func close() -> void:
	if not is_open:
		return
	is_open = false
	Audio.play("book_close", null, -8.0)
	var t := create_tween().set_parallel()
	t.tween_property(_book, "modulate:a", 0.0, 0.15)
	t.tween_property(_dim, "modulate:a", 0.0, 0.15)
	await t.finished
	_set_visible(false)
	_set_player_busy(false)


func _unhandled_input(event: InputEvent) -> void:
	if not is_unlocked or not (event is InputEventKey or event is InputEventAction):
		return
	if is_open:
		if event.is_action_pressed("move_left"):
			_flip(-1)
		elif event.is_action_pressed("move_right"):
			_flip(1)
		elif event.is_action_pressed("interact") or _is_key(event, [KEY_TAB, KEY_ESCAPE]):
			close()
		else:
			return
		get_viewport().set_input_as_handled()
	elif _is_key(event, [KEY_TAB]):
		var player := get_tree().get_first_node_in_group(&"player")
		if player == null or not player.busy:
			open()
			get_viewport().set_input_as_handled()


func _is_key(event: InputEvent, keys: Array) -> bool:
	return event is InputEventKey and event.pressed and not event.echo and event.physical_keycode in keys


func _flip(dir: int) -> void:
	var count := _spread_count()
	var next := clampi(_spread + dir, 0, count - 1)
	if next == _spread:
		return
	_spread = next
	_build_spread()
	Audio.play("page_turn", null, -8.0, randf_range(0.95, 1.05))


# ---------- mise en page ----------
func _pages() -> Array:
	var pages := [{"map": true}, {"places": true}]
	var beasts := creatures.values()
	beasts.sort_custom(func(a: CreatureEntry, b: CreatureEntry) -> bool: return a.order < b.order)
	for c in beasts:
		pages.append({"creature": c})
	for i in range(0, paroles.size(), PAROLES_PER_PAGE):
		pages.append({"paroles": paroles.slice(i, i + PAROLES_PER_PAGE)})
	var numbers := journal.keys()
	numbers.sort()
	if not numbers.is_empty() and pages.size() % 2 == 1:
		pages.append({})  # le journal commence sur une page de gauche
	for n in numbers:
		pages.append({"journal": journal[n]})
	if pages.size() % 2 == 1:
		pages.append({})
	pages.append_array(OLD_NOTES)
	return pages


func _spread_count() -> int:
	return ceili(_pages().size() / 2.0)


func _build_spread() -> void:
	var pages := _pages()
	_fill(_left, pages[_spread * 2] if _spread * 2 < pages.size() else {})
	_fill(_right, pages[_spread * 2 + 1] if _spread * 2 + 1 < pages.size() else {})
	for child in _dots.get_children():
		child.queue_free()
	for i in _spread_count():
		var dot := ColorRect.new()
		dot.custom_minimum_size = Vector2(10, 10)
		dot.color = INK if i == _spread else Color(INK, 0.25)
		_dots.add_child(dot)


func _fill(page: VBoxContainer, data: Dictionary) -> void:
	for child in page.get_children():
		child.queue_free()
	if data.get("map", false):
		_fill_map(page)
		return
	if data.get("places", false):
		_fill_places(page)
		return
	if data.has("creature"):
		_fill_creature(page, data["creature"])
		return
	if data.has("journal"):
		_fill_journal(page, data["journal"])
		return
	if data.has("paroles"):
		_fill_paroles(page, data["paroles"])
		return
	if data.get("sketch", "") != "":
		var sketch := TextureRect.new()
		sketch.texture = load(SKETCH_PATH % data["sketch"])
		sketch.custom_minimum_size = Vector2(170, 170)
		sketch.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		sketch.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		sketch.modulate = INK
		sketch.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		page.add_child(sketch)


# Carte de l'île : côtes, falaises, lieux découverts et position du robot.
func _fill_map(page: VBoxContainer) -> void:
	var map := Control.new()
	map.set_script(preload("res://scripts/notebook/map_view.gd"))
	map.custom_minimum_size = Vector2(370, 440)
	map.size_flags_vertical = Control.SIZE_EXPAND_FILL
	map.heights = _map_heights
	map.cell = _map_cell
	map.origin = _map_origin
	map.places = places
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	if player:
		map.player_pos = player.global_position
	page.add_child(map)
	map.resized.connect(map.refresh)
	map.refresh.call_deferred()


# Croquis des lieux vus, avec un petit soleil doré quand c'est accompli.
func _fill_places(page: VBoxContainer) -> void:
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 6)
	page.add_child(grid)
	for id in place_order:
		var p: Dictionary = places[id]
		var cell := Control.new()
		cell.custom_minimum_size = Vector2(116, 104)
		var sketch := TextureRect.new()
		sketch.texture = p["sketch"]
		sketch.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		sketch.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		sketch.modulate = INK
		sketch.set_anchors_preset(Control.PRESET_FULL_RECT)
		cell.add_child(sketch)
		if p["done"]:
			var stamp := TextureRect.new()
			stamp.texture = load("res://assets/ui/map_icons/sun.png")
			stamp.modulate = Color(0.78, 0.55, 0.22)
			stamp.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			stamp.size = Vector2(28, 28)
			stamp.position = Vector2(88, 0)
			cell.add_child(stamp)
		grid.add_child(cell)


# Bestiaire : un grand croquis, et la petite antenne éteinte qui dit « vue dans le noir ».
func _fill_creature(page: VBoxContainer, entry: CreatureEntry) -> void:
	var sketch := TextureRect.new()
	sketch.texture = entry.sketch
	sketch.custom_minimum_size = Vector2(300, 300)
	sketch.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sketch.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	sketch.modulate = INK
	sketch.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	sketch.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(sketch)
	var seen := TextureRect.new()
	seen.texture = load("res://assets/ui/map_icons/dark.png")
	seen.custom_minimum_size = Vector2(44, 44)
	seen.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	seen.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	seen.modulate = Color(INK, 0.7)
	seen.size_flags_horizontal = Control.SIZE_SHRINK_END
	page.add_child(seen)


# Paroles des Lueurs : recopiées à l'encre turquoise, entre guillemets, séparées par un petit trait.
func _fill_paroles(page: VBoxContainer, list: Array) -> void:
	page.add_theme_constant_override("separation", 10)
	for i in list.size():
		var label := Label.new()
		label.text = "« %s »" % String(list[i]["text"]).replace("\n", " ")
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.add_theme_font_override("font", HAND_FONT)
		label.add_theme_font_size_override("font_size", 22)
		label.add_theme_constant_override("line_spacing", -5)
		label.add_theme_color_override("font_color", TURQUOISE_INK)
		page.add_child(label)
		if i < list.size() - 1:
			var dash := ColorRect.new()
			dash.custom_minimum_size = Vector2(40, 2)
			dash.color = Color(TURQUOISE_INK, 0.4)
			dash.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
			page.add_child(dash)


# Page du journal de la Gardienne, de sa main. Pages lumineuses : écriture claire sur fond nuit.
func _fill_journal(page: VBoxContainer, entry: JournalPage) -> void:
	var holder := PanelContainer.new()
	holder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var style := StyleBoxFlat.new()
	style.bg_color = NIGHT if entry.luminous else Color(0, 0, 0, 0)
	style.set_corner_radius_all(8)
	style.set_content_margin_all(14 if entry.luminous else 0)
	holder.add_theme_stylebox_override("panel", style)
	page.add_child(holder)
	var label := Label.new()
	label.text = entry.text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	label.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	label.add_theme_font_override("font", HAND_FONT)
	# les longues pages s'écrivent un peu plus petit pour tenir sur la page
	label.add_theme_font_size_override("font_size", 23 if entry.text.length() < 330 else 19)
	label.add_theme_constant_override("line_spacing", -4)
	label.add_theme_color_override("font_color", LUEUR if entry.luminous else INK)
	if entry.luminous:
		label.add_theme_color_override("font_shadow_color", Color(LUEUR, 0.35))
		label.add_theme_constant_override("shadow_outline_size", 6)
	holder.add_child(label)
	var number := Label.new()
	number.text = str(entry.number)
	number.add_theme_font_override("font", HAND_FONT)
	number.add_theme_font_size_override("font_size", 20)
	number.add_theme_color_override("font_color", Color(INK, 0.6))
	number.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	page.add_child(number)


# ---------- petite notification « nouveau croquis » ----------
func _show_toast(picture: Texture2D) -> void:
	_toast_picture.visible = picture != null
	if picture:
		_toast_picture.texture = picture
	var t := create_tween()
	t.tween_property(_toast, "modulate:a", 1.0, 0.4)
	t.tween_interval(3.0)
	t.tween_property(_toast, "modulate:a", 0.0, 0.8)


func _set_visible(on: bool) -> void:
	_book.visible = on
	_dim.visible = on
	_dim.modulate.a = 1.0


func _set_player_busy(on: bool) -> void:
	var player := get_tree().get_first_node_in_group(&"player")
	if player:
		player.busy = on
		if on:
			player.face.set_expression(&"curious")
		else:
			player.face.set_expression(&"neutral")
