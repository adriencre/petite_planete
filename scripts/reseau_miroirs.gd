extends Node3D
## La lentille s'allume lorsque le rayon a traversé les trois miroirs.

const MIROIR := preload("res://scripts/miroir_cap.gd")
const SONS := preload("res://scripts/sons.gd")
const LUNETTE := preload("res://scripts/lunette_iris.gd")
const RAYON_EPAVE := 13.0
const PORTEE := 118.0
const PERIODE := 40.0
const AZIMUT_LENTILLE_AU_REPOS := 158.0
const CRANS_LENTILLE := [-129.0, -58.0, -9.0, 42.0, 73.0]

@export var station_ouest: MIROIR
@export var optique: Node3D
@export var epave: Node3D
@export var maquette: Node3D
@export var joueur: CharacterBody3D
@export var carnet: CanvasLayer
@export var engrenages: Node3D
@export var commande: Node3D
@export var lunette: LUNETTE
@export var rayon_galerie := 3.85

@onready var _axe: Node3D = optique.get_node("AxeFaisceau")
@onready var _inclinaison: Node3D = _axe.get_node("Inclinaison")
@onready var _projecteur: SpotLight3D = _inclinaison.get_node("Projecteur")
@onready var _coeur: OmniLight3D = optique.get_node("CoeurLentille")
@onready var _montee: MeshInstance3D = optique.get_node("Montee")
@onready var _rayon: MeshInstance3D = _inclinaison.get_node("Rayon")
@onready var _matiere: ShaderMaterial = _rayon.mesh.surface_get_material(0) as ShaderMaterial
@onready var _touche_commande: Label3D = commande.get_node("Touche")
@onready var _manivelle_commande: Node3D = commande.get_node("Manivelle")
@onready var _graduation: Label3D = commande.get_node("Graduation")

var allume := false
var _deja_vu := false
var _en_cours := false
var _puissance := 0.0
var _ascension := 0.0
var _azimut := 0.0
var _depart_vers_epave := 0.0
var _rotor: Node3D
var _brume: ShaderMaterial
var _cran_lentille := -1
var _manivelle_occupee := false


func _ready() -> void:
	add_to_group("sauvegarde")
	if lunette:
		lunette.commande_lentille_prioritaire = _commande_accessible
	var etat := Sauvegarde.donnees(cle_sauvegarde(), self)
	_deja_vu = bool(etat.get("deja_vu", false))
	_cran_lentille = clampi(int(etat.get("cran_lentille", -1)), -1, CRANS_LENTILLE.size() - 1)
	_rotor = optique.get_parent().find_child("Axe de rotation de la lentille", true, false) as Node3D
	var vers := epave.global_position + Vector3.UP * 0.45 - optique.global_position
	_depart_vers_epave = atan2(-vers.x, -vers.z)
	_azimut = _depart_vers_epave
	if _cran_lentille >= 0:
		_azimut = deg_to_rad(CRANS_LENTILLE[_cran_lentille])
	_inclinaison.rotation.x = atan2(vers.y, Vector2(vers.x, vers.z).length())
	var nappes := maquette.get_node_or_null("BrumeEpaisse") as MeshInstance3D
	if nappes:
		_brume = nappes.material_override as ShaderMaterial
	if _deja_vu:
		# Laisse le carnet restaurer ses pages avant de rattraper un départ en cours de scène.
		await get_tree().physics_frame
		await get_tree().physics_frame
		_noter_carte()


func cle_sauvegarde() -> String:
	return "rallumage_phare"


func sauver() -> Dictionary:
	return {"deja_vu": _deja_vu, "cran_lentille": _cran_lentille}


func _process(delta: float) -> void:
	allume = station_ouest.transmet()
	if allume and not _deja_vu and not _en_cours and not bool(joueur.get("cinematique")):
		_premier_rallumage()
	if not _en_cours:
		_puissance = move_toward(_puissance, 1.0 if allume and _deja_vu else 0.0, delta)
		if _cran_lentille >= 0:
			_azimut = rotate_toward(_azimut, deg_to_rad(CRANS_LENTILLE[_cran_lentille]), delta * 0.55)
		elif allume and _deja_vu:
			_azimut += TAU * delta * HorlogeMonde.vitesse / PERIODE
	_touche_commande.visible = _commande_accessible()
	_graduation.visible = (_touche_commande.visible or _manivelle_occupee) and _cran_lentille >= 0
	if _graduation.visible:
		_graduation.text = "%03d°" % posmod(roundi(-CRANS_LENTILLE[_cran_lentille]), 360)
	engrenages.call("suivre_lentille", _azimut)
	_actualiser_lumiere()


func _commande_accessible() -> bool:
	if _manivelle_occupee or not bool(engrenages.get("repare")) or bool(joueur.get("cinematique")):
		return false
	var ecart := joueur.global_position - commande.global_position
	var depuis_axe := joueur.global_position - optique.global_position
	if absf(ecart.y) >= 1.0 or Vector2(depuis_axe.x, depuis_axe.z).length() > rayon_galerie:
		return false
	if not lunette or not lunette.a_portee(joueur):
		return true
	var depuis_lunette := joueur.global_position - lunette.global_position
	return Vector2(ecart.x, ecart.z).length_squared() <= Vector2(depuis_lunette.x, depuis_lunette.z).length_squared()


func _unhandled_input(event: InputEvent) -> void:
	var touche := event as InputEventKey
	if not touche or not touche.pressed or touche.echo or touche.physical_keycode != KEY_E or not _commande_accessible():
		return
	get_viewport().set_input_as_handled()
	_cran_lentille = (_cran_lentille + 2) % (CRANS_LENTILLE.size() + 1) - 1
	_manivelle_occupee = true
	SONS.jouer("clic", commande.global_position, -2.0, 0.65)
	var mouvement := create_tween().set_trans(Tween.TRANS_SINE)
	mouvement.tween_property(_manivelle_commande, "rotation:z", TAU, 0.95)
	await mouvement.finished
	_manivelle_commande.rotation.z = 0.0
	_manivelle_occupee = false


func _actualiser_lumiere() -> void:
	_axe.visible = _puissance > 0.001
	_axe.rotation.y = _azimut
	_matiere.set_shader_parameter("intensite", 1.2 * _puissance)
	_projecteur.light_energy = 4.6 * _puissance
	_coeur.light_energy = 6.2 * _puissance
	if _rotor and (_puissance > 0.001 or _en_cours or _cran_lentille >= 0):
		_rotor.rotation.y = _azimut - deg_to_rad(AZIMUT_LENTILLE_AU_REPOS)
	_montee.visible = _ascension > 0.001
	_montee.scale.y = maxf(0.001, 12.0 * _ascension)
	_montee.position.y = -12.0 + _montee.scale.y * 0.5
	if _brume:
		var centre := optique.global_position
		var dir := _direction_horizontale() * _puissance
		_brume.set_shader_parameter("phare_passage", Vector4(centre.x, centre.z, dir.x, dir.y))
		var cible := epave.global_position
		_brume.set_shader_parameter("phare_epave", Vector4(cible.x, cible.z, RAYON_EPAVE, _puissance))


func _direction_horizontale() -> Vector2:
	return Vector2(-sin(_azimut), -cos(_azimut))


## La trouée qui se voit dans l'air dispense aussi le robot de repousser la brume.
func dissipe_brume(point: Vector3) -> bool:
	if _puissance < 0.65:
		return false
	var lieu := Vector2(point.x, point.z)
	var cible := Vector2(epave.global_position.x, epave.global_position.z)
	if lieu.distance_to(cible) < RAYON_EPAVE * 0.78:
		return true
	var ecart := lieu - Vector2(optique.global_position.x, optique.global_position.z)
	var dir := _direction_horizontale()
	var distance := ecart.dot(dir)
	return distance > 0.0 and distance < PORTEE and absf(ecart.cross(dir)) < 2.2 + 0.036 * distance


func _premier_rallumage() -> void:
	_en_cours = true
	_azimut = _depart_vers_epave
	joueur.set("cinematique", true)
	joueur.velocity = Vector3.ZERO
	var lentille := optique.global_position
	var cible := epave.global_position + Vector3.UP * 0.65
	joueur.set("regard_cible", lentille)
	joueur.set("cine_position", lentille + Vector3(-34, 12, 30))
	joueur.set("cine_cible", lentille + Vector3(-13, -9, 0))
	var scene := create_tween().set_trans(Tween.TRANS_SINE)
	scene.tween_property(joueur, "cine_melange", 1.0, 0.85)
	scene.tween_callback(SONS.jouer.bind("recharge", lentille, -6.0, 0.66))
	scene.tween_property(self, "_ascension", 1.0, 1.85)
	scene.parallel().tween_property(joueur, "cine_cible", lentille, 1.85)
	scene.tween_callback(SONS.jouer.bind("allumage", lentille, -2.0, 0.8))
	scene.tween_property(self, "_puissance", 1.0, 1.5)
	scene.parallel().tween_property(self, "_ascension", 0.0, 0.65)
	scene.tween_property(joueur, "cine_position", cible + Vector3(-10, 20, -16), 1.7)
	scene.parallel().tween_property(joueur, "cine_cible", cible, 1.7)
	scene.tween_interval(0.8)
	scene.tween_property(joueur, "cine_melange", 0.0, 0.7)
	await scene.finished
	_deja_vu = true
	_en_cours = false
	joueur.set("cinematique", false)
	_noter_carte()


func _noter_carte() -> void:
	carnet.call("noter_archipel")
