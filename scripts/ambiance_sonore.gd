extends Node
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## L'ambiance sonore de l'île (ILE_01_REVEIL.md §10). Sons : tools/audio/generer_sons.py.
## - Silence pendant le premier réveil ; quand on prend la main, le vent et les vagues montent doucement.
## - Les oiseaux chantent de temps en temps, de plus en plus souvent à mesure que l'île se réveille.
## - La musique : 4 couches synchronisées, qui tournent en boucle depuis le début (muettes) ; chaque
##   petite lanterne allumée en fait entendre une de plus, la grande lanterne ajoute la nappe.

@export_range(-40.0, 6.0) var volume_vent: float = -14.0
@export_range(-40.0, 6.0) var volume_vagues: float = -12.0
@export_range(-40.0, 6.0) var volume_musique: float = -8.0
@export_range(-40.0, 6.0) var volume_oiseaux: float = -16.0
## Secondes pour qu'une couche de musique apparaisse (ou disparaisse).
@export var fondu_couche: float = 4.0

const SILENCE := -60.0

var _joueur: CharacterBody3D
var _vent: AudioStreamPlayer
var _vagues: AudioStreamPlayer
var _couches: Array[AudioStreamPlayer] = []
var _niveaux: Array[float] = [0.0, 0.0, 0.0, 0.0]   # 0..1, volume de chaque couche
var _ambiance := 0.0                                 # 0..1, vent et vagues
var _reveille := false
var _calme := 0.0
var _prochain_oiseau := 4.0


func _ready() -> void:
	# la musique et le vent continuent, doucement, quand le jeu est en pause
	process_mode = Node.PROCESS_MODE_ALWAYS
	_vent = _boucle("vent", &"Ambiance")
	_vagues = _boucle("vagues", &"Ambiance")
	for k in 4:
		_couches.append(_boucle("musique_couche_%d" % (k + 1), &"Musique"))
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	# toutes les couches démarrent ensemble (muettes) : elles restent synchronisées
	for c in _couches:
		if c.stream:
			c.play()
	for p in [_vent, _vagues]:
		if p.stream:
			p.play()


## Un lecteur qui tourne en boucle, muet au départ.
func _boucle(nom: String, bus: StringName) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.name = nom
	p.bus = bus
	var s: AudioStream = SONS.flux(nom)
	if s is AudioStreamWAV:
		s = (s as AudioStreamWAV).duplicate()
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD
		s.loop_begin = 0
		s.loop_end = int(s.get_length() * s.mix_rate)
	p.stream = s
	p.volume_db = SILENCE
	add_child(p)
	return p


func _process(delta: float) -> void:
	if _joueur == null:
		return
	# le premier réveil fini (on a la main depuis un moment), l'ambiance monte
	if not _reveille:
		_calme = _calme + delta if not bool(_joueur.get("cinematique")) else 0.0
		if _calme > 1.0:
			_reveille = true
	_ambiance = move_toward(_ambiance, 1.0 if _reveille else 0.0, delta / 6.0)
	_vent.volume_db = _db(volume_vent, _ambiance)
	_vagues.volume_db = _db(volume_vagues, _ambiance)
	# la musique : une couche par petite lanterne allumée, la nappe avec la grande
	var petites := 0
	var grande := false
	for l in get_tree().get_nodes_in_group("lanternes"):
		if not bool(l.get("allumee")):
			continue
		if int(l.get("rang")) == 0:
			petites += 1
		else:
			grande = true
	var cibles := [petites >= 1, petites >= 2, petites >= 3, grande]
	for k in 4:
		_niveaux[k] = move_toward(_niveaux[k], 1.0 if cibles[k] else 0.0, delta / fondu_couche)
		_couches[k].volume_db = _db(volume_musique, _niveaux[k])
	# les oiseaux : de temps en temps, plus souvent quand l'île se réveille
	if _reveille:
		_prochain_oiseau -= delta
		if _prochain_oiseau <= 0.0:
			var eveil := (petites + (2 if grande else 0)) / 5.0
			_prochain_oiseau = randf_range(4.0, 10.0) * (1.0 - 0.6 * eveil)
			var ou := _joueur.global_position + Vector3(randf_range(-12, 12), randf_range(3, 7), randf_range(-12, 12))
			SONS.jouer("oiseau_%d" % randi_range(1, 4), ou, volume_oiseaux + 6.0 * eveil, randf_range(0.9, 1.15))


## Un niveau 0..1 en décibels, avec une courbe douce (on n'entend pas de « marche »).
func _db(volume: float, niveau: float) -> float:
	if niveau <= 0.001:
		return SILENCE
	return volume + linear_to_db(niveau * niveau)
