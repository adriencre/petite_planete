extends Node
## La sauvegarde de la partie (autoload « Sauvegarde »), dans user://partie.json.
##
## Ce qu'on garde : ce que le robot a fait et appris (lanternes allumées, fin de l'île vue, carnet,
## pages lues, anciens corps, nombre de morts, gestes déjà appris). Pas sa position : « Continuer »,
## c'est se réveiller dans le berceau (réveil court), comme après chaque mort — c'est la règle du jeu.
##
## Chaque objet à sauver est dans le groupe « sauvegarde » et a :
##   cle_sauvegarde() -> String      une clé stable (pas un nom de nœud généré)
##   sauver() -> Dictionary          son état, en types JSON (pas de Vector3 : des tableaux)
## et, à la fin de son _ready, il relit son état : Sauvegarde.donnees(cle) (vide si nouvelle partie).
##
## Sauvegarde automatique : toutes les `intervalle` secondes hors cinématique, en revenant au titre,
## en quittant, et quand la fenêtre se ferme.

const CHEMIN := "user://partie.json"
const VERSION := 1
const SCENE_ILE := "res://scenes/ile_01_maquette.tscn"
const SCENE_ILE_02 := "res://scenes/ile_02_maquette.tscn"
const CHEMIN_ILE_02 := "user://partie_ile_02.json"
const SCENE_TITRE := "res://scenes/ecran_titre.tscn"
## Scripts dont des variables statiques sont sauvées (chargés à la demande : pas de preload, ces
## scripts utilisent eux-mêmes Sauvegarde).
const PIERRE := "res://scripts/pierre_soleil.gd"
const LANTERNE := "res://scripts/lanterne_fleur.gd"

## Secondes entre deux sauvegardes automatiques.
@export var intervalle: float = 20.0

## L'état lu au lancement de la partie : clé -> Dictionary.
var _charge: Dictionary = {}
var _charge_ile_02: Dictionary = {}
var _minuterie: float = 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	get_tree().set_auto_accept_quit(false)
	_charge_ile_02 = _lire_fichier(CHEMIN_ILE_02)


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		quitter()


func _process(delta: float) -> void:
	if get_tree().paused or not en_partie():
		return
	_minuterie += delta
	if _minuterie >= intervalle:
		var j := get_tree().get_first_node_in_group("joueur")
		if j and not bool(j.get("cinematique")):
			_minuterie = 0.0
			ecrire()


## Vrai si une partie est sauvegardée.
func existe() -> bool:
	return FileAccess.file_exists(CHEMIN)


## Vrai si on est sur l'île (pas sur l'écran titre).
func en_partie() -> bool:
	if not is_inside_tree():
		return false
	var scene := get_tree().current_scene
	return scene != null and scene.scene_file_path in [SCENE_ILE, SCENE_ILE_02]


func _sur_ile_02(source: Node = null) -> bool:
	# Certains objets restaurent leur état avant que SceneTree ait fini d'installer la scène.
	while source != null:
		if source.scene_file_path == SCENE_ILE_02:
			return true
		source = source.get_parent()
	var scene := get_tree().current_scene
	return scene != null and scene.scene_file_path == SCENE_ILE_02


## Pour un objet qui va quitter la scène : son dernier état est gardé pour la prochaine sauvegarde.
func noter(cle: String, etat: Dictionary) -> void:
	var charge := _charge_ile_02 if _sur_ile_02() else _charge
	charge[cle] = etat


## L'état sauvé d'un objet (vide pour une nouvelle partie).
func donnees(cle: String, source: Node = null) -> Dictionary:
	var charge := _charge_ile_02 if _sur_ile_02(source) else _charge
	var d = charge.get(cle, {})
	return d if d is Dictionary else {}


func nouvelle_partie() -> void:
	if existe():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(CHEMIN))
	_effacer_images()
	_charge = {}
	_statiques({})
	_minuterie = 0.0
	get_tree().change_scene_to_file(SCENE_ILE)


func continuer() -> void:
	_charge = lire()
	_statiques(_charge.get("_statiques", {}))
	_minuterie = 0.0
	get_tree().change_scene_to_file(SCENE_ILE)


## Dev : aller directement sur une île. Reprend la partie sauvegardée s'il y en a une (sans l'effacer).
func aller_dev(scene: String) -> void:
	_charge = lire() if existe() else {}
	_statiques(_charge.get("_statiques", {}))
	_minuterie = 0.0
	get_tree().change_scene_to_file(scene)


func retour_au_titre() -> void:
	ecrire()
	get_tree().paused = false
	get_tree().change_scene_to_file(SCENE_TITRE)


func quitter() -> void:
	ecrire()
	get_tree().quit()


func lire() -> Dictionary:
	return _lire_fichier(CHEMIN)


func _lire_fichier(chemin: String) -> Dictionary:
	var f := FileAccess.open(chemin, FileAccess.READ)
	if f == null:
		return {}
	var d = JSON.parse_string(f.get_as_text())
	if not (d is Dictionary) or int(d.get("_version", 0)) != VERSION:
		return {}
	return d


func ecrire() -> void:
	if not en_partie():
		return
	# on part de l'état déjà sauvé : un objet qui a quitté la scène (feuille rangée dans le carnet,
	# luciole partie) garde son dernier état
	var ile_02 := _sur_ile_02()
	var d := (_charge_ile_02 if ile_02 else _charge).duplicate(true)
	d["_version"] = VERSION
	d["_date"] = Time.get_datetime_string_from_system()
	d["_statiques"] = {
		"pierre_deja_fait": bool(load(PIERRE).get("deja_fait")),
		"reprise_faite": bool(load(LANTERNE).get("reprise_faite")),
	}
	for n in get_tree().get_nodes_in_group("sauvegarde"):
		if n.has_method("cle_sauvegarde") and n.has_method("sauver"):
			d[str(n.call("cle_sauvegarde"))] = n.call("sauver")
	var f := FileAccess.open(CHEMIN_ILE_02 if ile_02 else CHEMIN, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(d, "\t"))
	if ile_02:
		_charge_ile_02 = d
	else:
		_charge = d


## Les « première fois » partagées entre objets (variables statiques des scripts).
func _statiques(s: Dictionary) -> void:
	load(PIERRE).set("deja_fait", bool(s.get("pierre_deja_fait", false)))
	load(LANTERNE).set("reprise_faite", bool(s.get("reprise_faite", false)))


# ---------------------------------------------------------------- outils pour les objets

static func vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]


static func en_vec(a) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2])) if a is Array and a.size() == 3 else Vector3.ZERO


static func transfo(t: Transform3D) -> Array:
	var b := t.basis
	return [b.x.x, b.x.y, b.x.z, b.y.x, b.y.y, b.y.z, b.z.x, b.z.y, b.z.z, t.origin.x, t.origin.y, t.origin.z]


static func en_transfo(a) -> Transform3D:
	if not (a is Array) or a.size() != 12:
		return Transform3D.IDENTITY
	var f: Array = a.map(func(x): return float(x))
	return Transform3D(Basis(Vector3(f[0], f[1], f[2]), Vector3(f[3], f[4], f[5]), Vector3(f[6], f[7], f[8])), Vector3(f[9], f[10], f[11]))


## Une image (croquis photographié par le carnet) : gardée en PNG à côté de la sauvegarde.
## Renvoie le chemin à mettre dans la sauvegarde ("" si rien à garder).
func garder_image(tex: Texture2D, nom: String) -> String:
	if tex == null:
		return ""
	if tex.resource_path.begins_with("res://"):
		return tex.resource_path
	var img := tex.get_image()
	if img == null:
		return ""
	var dossier := "user://images_ile_02" if _sur_ile_02() else "user://images"
	var chemin := "%s/%s.png" % [dossier, nom]
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dossier))
	img.save_png(chemin)
	return chemin


func charger_image(chemin: String) -> Texture2D:
	if chemin == "":
		return null
	if chemin.begins_with("res://"):
		return load(chemin) as Texture2D if ResourceLoader.exists(chemin) else null
	var img := Image.load_from_file(chemin)
	return ImageTexture.create_from_image(img) if img else null


func _effacer_images() -> void:
	var dossier := DirAccess.open("user://images")
	if dossier == null:
		return
	for f in dossier.get_files():
		dossier.remove(f)
