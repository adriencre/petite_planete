extends Node
## Les réglages du joueur (autoload « Reglages ») : volumes et plein écran.
## Gardés dans user://reglages.cfg, appliqués au lancement.
## Les bus audio (default_bus_layout.tres) : Master > Musique, Ambiance (vent, vagues), Effets.

const CHEMIN := "user://reglages.cfg"
## Nom du bus -> volume (0..1). « Master » = le volume général.
const BUS := ["Master", "Musique", "Ambiance", "Effets"]

var volumes: Dictionary = {"Master": 0.8, "Musique": 0.8, "Ambiance": 0.8, "Effets": 0.8}
var plein_ecran: bool = false


func _ready() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(CHEMIN) == OK:
		for b in BUS:
			volumes[b] = clampf(float(cfg.get_value("son", b, volumes[b])), 0.0, 1.0)
		plein_ecran = bool(cfg.get_value("ecran", "plein_ecran", plein_ecran))
	for b in BUS:
		_appliquer_volume(b)
	_appliquer_ecran()


func regler_volume(bus: String, v: float) -> void:
	volumes[bus] = clampf(v, 0.0, 1.0)
	_appliquer_volume(bus)


func regler_plein_ecran(oui: bool) -> void:
	plein_ecran = oui
	_appliquer_ecran()


func enregistrer() -> void:
	var cfg := ConfigFile.new()
	for b in BUS:
		cfg.set_value("son", b, volumes[b])
	cfg.set_value("ecran", "plein_ecran", plein_ecran)
	cfg.save(CHEMIN)


## Une courbe douce : le milieu du curseur sonne vraiment « à moitié ».
func _appliquer_volume(bus: String) -> void:
	var i := AudioServer.get_bus_index(bus)
	if i < 0:
		return
	var v: float = volumes[bus]
	AudioServer.set_bus_mute(i, v <= 0.001)
	AudioServer.set_bus_volume_db(i, linear_to_db(maxf(v * v, 0.0001)))


func _appliquer_ecran() -> void:
	if plein_ecran:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	elif DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
