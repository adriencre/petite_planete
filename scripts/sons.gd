extends RefCounted
## (à charger avec : const SONS := preload("res://scripts/sons.gd"))
## Joue un effet sonore de assets/audio/ (fabriqués par tools/audio/generer_sons.py).
##   SONS.jouer("clic", position_monde)   # dans l'espace (plus fort de près)
##   SONS.jouer("page")                    # sans position : partout pareil

const DOSSIER := "res://assets/audio/"

static var _cache: Dictionary = {}


static func flux(nom: String) -> AudioStream:
	if not _cache.has(nom):
		var chemin := DOSSIER + nom + ".wav"
		_cache[nom] = load(chemin) if ResourceLoader.exists(chemin) else null
	return _cache[nom]


static func jouer(nom: String, ou = null, volume_db: float = 0.0, hauteur: float = 1.0) -> void:
	var s := flux(nom)
	var arbre := Engine.get_main_loop() as SceneTree
	if s == null or arbre == null or arbre.current_scene == null:
		return
	if ou is Vector3:
		var l3 := AudioStreamPlayer3D.new()
		l3.stream = s
		l3.volume_db = volume_db
		l3.pitch_scale = hauteur
		l3.unit_size = 6.0
		l3.max_distance = 40.0
		arbre.current_scene.add_child(l3)
		l3.global_position = ou
		l3.play()
		l3.finished.connect(l3.queue_free)
	else:
		var l := AudioStreamPlayer.new()
		l.stream = s
		l.volume_db = volume_db
		l.pitch_scale = hauteur
		arbre.current_scene.add_child(l)
		l.play()
		l.finished.connect(l.queue_free)
