extends Node
## Tout le son du jeu (accessible partout sous le nom « Audio »).
## - Ambiance : vent gris de l'île endormie → vent doux, vagues et oiseaux là où l'île est réveillée,
##   calculée à l'endroit où se trouve le robot.
## - Musique en couches : chaque lanterne ajoute une couche du même morceau (synchronisées).
## - Musique de l'ombre (les Lueurs) : 3 couches qui montent quand on éteint, pendant que celle
##   de la lumière s'efface. La 3e (le peuple) n'arrive qu'une fois la Pouponnière libérée.
## - Bruitages : play("nom") ou play("nom", position) pour un son placé dans le monde.
## Les sons sont dans assets/audio/{ambience,sfx,music}.

const SFX := "res://assets/audio/sfx/%s.wav"
const AMB := "res://assets/audio/ambience/%s.wav"
const MUSIC := "res://assets/audio/music/%s.wav"
const SILENT := -60.0

@export var music_layers: Array[String] = ["island01_layer1", "island01_layer2", "island01_layer3", "island01_layer4", "island01_layer5"]
@export var layer_volume_db := -4.0
@export var ombre_layers: Array[String] = ["ombre_layer1", "ombre_layer2", "ombre_layer3"]
@export var ombre_volume_db := -5.0
@export var ombre_people_flag: StringName = &"pouponniere_libre" ## débloque la 3e couche (le peuple)

var _amb := {}            # nom -> AudioStreamPlayer
var _music: AudioStreamPlayer
var _sync: AudioStreamSynchronized
var _layers_on := 0
var _loops := {}          # id -> lecteur en boucle
var _awake := 0.0
var _indoor := 0.0
var _music_duck := 0.0
var _vision := 0.0
var _ombre: AudioStreamPlayer
var _ombre_sync: AudioStreamSynchronized
var _ombre_mix := [0.0, 0.0, 0.0]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for name in ["wind_sleep", "wind_awake", "waves", "birds", "lueurs"]:
		var p := AudioStreamPlayer.new()
		p.stream = _looping(load(AMB % name))
		p.bus = &"Ambience"
		p.volume_db = SILENT
		add_child(p)
		_amb[name] = p
	_sync = AudioStreamSynchronized.new()
	_sync.stream_count = music_layers.size()
	for i in music_layers.size():
		_sync.set_sync_stream(i, _looping(load(MUSIC % music_layers[i])))
		_sync.set_sync_stream_volume(i, SILENT)
	_music = AudioStreamPlayer.new()
	_music.stream = _sync
	_music.bus = &"Music"
	add_child(_music)
	_ombre_sync = AudioStreamSynchronized.new()
	_ombre_sync.stream_count = ombre_layers.size()
	for i in ombre_layers.size():
		_ombre_sync.set_sync_stream(i, _looping(load(MUSIC % ombre_layers[i])))
		_ombre_sync.set_sync_stream_volume(i, SILENT)
	_ombre = AudioStreamPlayer.new()
	_ombre.stream = _ombre_sync
	_ombre.bus = &"Music"
	add_child(_ombre)


## Lance l'ambiance (appelé par l'île au démarrage).
func start_island() -> void:
	_layers_on = 0
	for i in music_layers.size():
		_sync.set_sync_stream_volume(i, SILENT)
	for p in _amb.values():
		if not p.playing:
			p.play()
	if not _music.playing:
		_music.play()
	if not _ombre.playing:
		_ombre.play()


func _process(delta: float) -> void:
	var player := get_tree().get_first_node_in_group(&"player") as Node3D
	if player:
		_awake = lerpf(_awake, WakeZone.awake_at(get_tree(), player.global_position), 1.0 - exp(-1.5 * delta))
	# dans un intérieur (abri, grotte), l'extérieur s'entend étouffé
	_indoor = lerpf(_indoor, InteriorZone.inside_amount(), 1.0 - exp(-2.0 * delta))
	var muffle := -9.0 * _indoor
	_set_amb("wind_sleep", lerpf(-8.0, -40.0, _awake) + muffle)
	_set_amb("wind_awake", lerpf(-42.0, -15.0, _awake) + muffle)
	_set_amb("waves", lerpf(-26.0, -13.0, _awake) + muffle * 1.3)
	_set_amb("birds", lerpf(-60.0, -15.0, smoothstep(0.3, 1.0, _awake)) + muffle)
	# les Lueurs : un chant cristallin qui monte quand l'antenne faiblit (et que la brume l'entoure)
	var vision := 0.0
	if player and player.has_node("Battery"):
		vision = player.get_node("Battery").vision() * (1.0 - _awake)
	_vision = lerpf(_vision, vision, 1.0 - exp(-2.0 * delta))
	_set_amb("lueurs", lerpf(-60.0, -8.0, sqrt(_vision)) - 5.0 * _ombre_mix[1])
	_set_amb("wind_sleep", lerpf(-8.0, -40.0, _awake) + muffle - 14.0 * _vision)
	# la musique de la lumière s'efface quand on éteint ; celle de l'ombre prend le relais
	_music.volume_db = -14.0 * _music_duck - 22.0 * smoothstep(0.2, 0.9, _vision)
	_update_ombre(delta)


## Les couches de l'ombre : 1 = on commence à voir, 2 = vraiment dans le noir, 3 = le peuple est prêt.
func _update_ombre(delta: float) -> void:
	var people: bool = Loop.has_flag(ombre_people_flag)
	var targets := [
		smoothstep(0.08, 0.5, _vision),
		smoothstep(0.55, 0.95, _vision),
		smoothstep(0.7, 1.0, _vision) if people else 0.0,
	]
	for i in mini(ombre_layers.size(), targets.size()):
		_ombre_mix[i] = lerpf(_ombre_mix[i], targets[i], 1.0 - exp(-0.8 * delta))
		var db: float = SILENT if _ombre_mix[i] < 0.002 else ombre_volume_db + linear_to_db(_ombre_mix[i])
		_ombre_sync.set_sync_stream_volume(i, maxf(db, SILENT))
	_ombre.volume_db = -14.0 * _music_duck


func _set_amb(name: String, db: float) -> void:
	_amb[name].volume_db = maxf(db, SILENT)


# L'île est-elle réveillée à cet endroit ? (0 = endormie, 1 = éveillée)
func _awake_at(pos: Vector3) -> float:
	var best := 0.0
	for zone in get_tree().get_nodes_in_group(&"wake_zone"):
		var d := Vector2(pos.x - zone.global_position.x, pos.z - zone.global_position.z).length()
		var r: float = zone.current_radius
		if r > 0.01:
			best = maxf(best, clampf((r - d) / 2.5 + 0.5, 0.0, 1.0))
	return best


# ---------- musique ----------
## Ajoute la couche suivante du morceau (ou va directement jusqu'à la couche `upto`).
func music_add_layer(upto := -1, fade := 6.0) -> void:
	var target := (_layers_on + 1) if upto < 0 else upto
	target = clampi(target, 0, music_layers.size())
	for i in range(_layers_on, target):
		var idx := i
		var t := create_tween()
		t.tween_method(func(db: float) -> void: _sync.set_sync_stream_volume(idx, db), SILENT, layer_volume_db, fade).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_layers_on = maxi(_layers_on, target)


## Une phrase musicale spéciale ; la musique en couches s'efface un moment pour la laisser respirer.
func stinger(name: String, duck := true) -> void:
	var p := AudioStreamPlayer.new()
	p.stream = load(MUSIC % name)
	p.bus = &"Music"
	add_child(p)
	p.play()
	p.finished.connect(p.queue_free)
	if duck:
		var length := p.stream.get_length()
		var t := create_tween()
		t.tween_property(self, "_music_duck", 1.0, 1.0)
		t.tween_interval(maxf(length - 4.0, 1.0))
		t.tween_property(self, "_music_duck", 0.0, 3.0)


## Fait taire progressivement la musique et l'ambiance (fin de l'île).
func fade_all(duration := 4.0) -> void:
	var t := create_tween().set_parallel()
	t.tween_property(_music, "volume_db", SILENT, duration)
	t.tween_property(_ombre, "volume_db", SILENT, duration)
	for p in _amb.values():
		t.tween_property(p, "volume_db", SILENT, duration)
	set_process(false)
	await t.finished
	set_process(true)


# ---------- bruitages ----------
## Joue un bruitage. `at` (Vector3) = son placé dans le monde ; sinon il est entendu partout.
func play(name: String, at: Variant = null, volume_db := 0.0, pitch := 1.0) -> Node:
	var stream: AudioStream = load(SFX % name)
	var p: Node
	if at is Vector3:
		var p3 := AudioStreamPlayer3D.new()
		p3.unit_size = 6.0
		p3.max_distance = 40.0
		p3.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
		get_tree().current_scene.add_child(p3)
		p3.global_position = at
		p3.stream = stream
		p3.volume_db = volume_db
		p3.pitch_scale = pitch
		p3.bus = &"SFX"
		p3.play()
		p = p3
	else:
		var p2 := AudioStreamPlayer.new()
		add_child(p2)
		p2.stream = stream
		p2.volume_db = volume_db
		p2.pitch_scale = pitch
		p2.bus = &"SFX"
		p2.play()
		p = p2
	p.finished.connect(p.queue_free)
	return p


## Variante au hasard parmi nom_0, nom_1… avec un léger changement de hauteur.
func play_random(prefix: String, count: int, at: Variant = null, volume_db := 0.0) -> void:
	play("%s_%d" % [prefix, randi() % count], at, volume_db, randf_range(0.9, 1.1))


## Bruitage en boucle (ex. le scintillement pendant qu'on trace un glyphe).
func start_loop(id: StringName, name: String, volume_db := 0.0) -> void:
	stop_loop(id, 0.0)
	var p := AudioStreamPlayer.new()
	p.stream = _looping(load(SFX % name))
	p.bus = &"SFX"
	p.volume_db = volume_db
	add_child(p)
	p.play()
	_loops[id] = p


func stop_loop(id: StringName, fade := 0.4) -> void:
	if not _loops.has(id):
		return
	var p: AudioStreamPlayer = _loops[id]
	_loops.erase(id)
	if fade <= 0.0:
		p.queue_free()
		return
	var t := create_tween()
	t.tween_property(p, "volume_db", SILENT, fade)
	t.tween_callback(p.queue_free)


func _looping(stream: AudioStream) -> AudioStream:
	if stream is AudioStreamWAV:
		var wav := stream as AudioStreamWAV
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate)
	return stream
