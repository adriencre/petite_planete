extends "res://scripts/batiment_coupe.gd"
## Dégage l'étage que le robot traverse sans modifier les collisions du bâtiment.

@onready var _modele: Node3D = $Modele
@onready var _salle_machines := _modele.find_child("SalleDesMachines", true, false) as Node3D
@onready var _escalier_iris := _modele.find_child("EscalierIris", true, false) as Node3D
@onready var _palier_iris := _modele.find_child("PalierIris", true, false) as Node3D
@onready var _chambre := _modele.find_child("ChambreIris", true, false) as Node3D
@onready var _acces_chambre := _modele.find_child("AccesChambreIris", true, false) as Node3D
@onready var _lumiere_atelier: OmniLight3D = $LumiereDeLAtelier
@onready var _engrenages: Node3D = $Engrenages

@onready var _bureau: Node3D = find_child("EtageIris", true, false) as Node3D
@onready var _montee_cartes: Node3D = find_child("MonteeCartes", true, false) as Node3D
@onready var _cartes: Node3D = find_child("EtageCartes", true, false) as Node3D
@onready var _entree_cartes := find_child("PorteCartes", true, false) as Node3D
@onready var _plaque_cartes: Node3D = $PorteCartesVerrouillee
@onready var _montee_galerie: Node3D = find_child("MonteeGalerie", true, false) as Node3D
@onready var _galerie: Node3D = find_child("GalerieHaute", true, false) as Node3D
@onready var _documents_bureau: Node3D = $DocumentsBureau
@onready var _documents_cartes: Node3D = $DocumentsCartes
@onready var _documents_chambre: Node3D = $DocumentsChambre
@onready var _toit_chambre := _modele.find_child("ToitChambre", true, false) as Node3D
@onready var _facades_chambre := _modele.find_child("FacadesChambre", true, false) as Node3D
@onready var _palier: Marker3D = $ReperePalierIris
@onready var _pied_montee_cartes: Marker3D = $ReperePiedMonteeCartes
@onready var _palier_cartes: Marker3D = $ReperePalierCartes
@onready var _seuil_galerie: Marker3D = $RepereSeuilGalerie
var _joueur_du_phare: Node3D
var _maillages_montee_cartes: Array[GeometryInstance3D] = []
var _transparence_montee_cartes := 0.0
var _maillages_montee_galerie: Array[GeometryInstance3D] = []
var _transparence_montee_galerie := 0.0


func _ready() -> void:
	super._ready()
	_maillages_montee_cartes = _maillages_de(_montee_cartes)
	_maillages_montee_galerie = _maillages_de(_montee_galerie)


func _maillages_de(racine: Node3D) -> Array[GeometryInstance3D]:
	var maillages: Array[GeometryInstance3D] = []
	if racine:
		for noeud in racine.find_children("*", "GeometryInstance3D", true, false):
			maillages.append(noeud as GeometryInstance3D)
	return maillages


func _physics_process(delta: float) -> void:
	if not is_instance_valid(_joueur_du_phare):
		_joueur_du_phare = get_tree().get_first_node_in_group("joueur") as Node3D
	if _bureau == null or _joueur_du_phare == null:
		return
	var position := _joueur_du_phare.global_position
	var locale := to_local(position)
	var hauteur_bureau := position.y - _palier.global_position.y
	var hauteur_cartes := position.y - _palier_cartes.global_position.y
	var hauteur_galerie := position.y - _seuil_galerie.global_position.y
	var dans_chambre := (
		locale.x > 6.48 and locale.x < 9.48
		and locale.z > -2.76 and locale.z < 0.82
		and locale.y > 4.0 and locale.y < 6.26
	)
	var sur_toit := (
		locale.x > 3.70 and locale.x < 9.22
		and locale.z > 0.56 and locale.z < 2.13
		and locale.y >= 6.26 and locale.y < 6.75
	)
	var sur_echelle := bool(_joueur_du_phare.get("sur_echelle"))
	var dans_annexe := dans_chambre or sur_toit or sur_echelle
	var exterieur := _dedans == 0 and not dans_annexe
	var dans_tour := _dedans > 0 and not dans_annexe
	var sur_galerie := dans_tour and hauteur_galerie >= -0.04

	_montrer_noeud(_chambre, exterieur or sur_galerie or dans_annexe)
	_montrer_noeud(_acces_chambre, exterieur or sur_galerie or sur_toit or sur_echelle)
	_montrer_noeud(_toit_chambre, not dans_chambre)
	_montrer_noeud(_facades_chambre, not dans_chambre)
	_documents_chambre.visible = dans_chambre

	var au_rez := exterieur or (dans_tour and hauteur_bureau < -0.12)
	_montrer_noeud(_salle_machines, au_rez)
	_engrenages.visible = au_rez
	_lumiere_atelier.visible = au_rez
	var proche_palier_iris := hauteur_bureau < 0.1 and position.distance_to(_palier.global_position) < 1.35
	_montrer_noeud(_escalier_iris, au_rez or (dans_tour and proche_palier_iris))
	_montrer_noeud(_palier_iris, exterieur or (dans_tour and hauteur_bureau >= -0.85 and hauteur_bureau < 1.15))

	var visite_bureau := dans_tour and hauteur_bureau >= -0.12 and hauteur_bureau < 1.15
	_bureau.visible = exterieur or visite_bureau
	_documents_bureau.visible = _bureau.visible
	_montrer_noeud(_montee_cartes, exterieur or (dans_tour and hauteur_bureau >= -0.12 and hauteur_cartes < 0.55))

	var approche_cartes := exterieur or (dans_tour and hauteur_cartes >= -1.10 and hauteur_cartes < 1.30)
	_montrer_noeud(_entree_cartes, approche_cartes)
	_plaque_cartes.visible = approche_cartes
	var visite_cartes := exterieur or (dans_tour and hauteur_cartes >= -0.24 and hauteur_cartes < 1.30)
	_montrer_noeud(_cartes, visite_cartes)
	_documents_cartes.visible = visite_cartes

	var proche_sortie := position.distance_to(_seuil_galerie.global_position) < 1.55
	var ascension_galerie := dans_tour and hauteur_cartes >= -0.24 and (not sur_galerie or proche_sortie)
	_montrer_noeud(_montee_galerie, exterieur or ascension_galerie)
	_montrer_noeud(_galerie, exterieur or sur_echelle or (dans_tour and hauteur_galerie >= -0.22))

	var coupe_cartes := 0.0
	if dans_tour and visite_cartes and bool(_plaque_cartes.get("ouverte")):
		var rayon := Vector2(locale.x, locale.z).length()
		var profondeur := _plaque_cartes.to_local(position).z
		coupe_cartes = (1.0 - smoothstep(1.62, 1.88, rayon)) * smoothstep(-0.20, 0.15, profondeur)
	_actualiser_fondu_montee_cartes(visite_bureau, delta)
	_transparence_montee_galerie = _fondre_maillages(_maillages_montee_galerie,
		_transparence_montee_galerie, coupe_cartes, delta)


func _montrer_noeud(noeud: Node3D, montrer: bool) -> void:
	if noeud:
		noeud.visible = montrer


func _actualiser_fondu_montee_cartes(visite_bureau: bool, delta: float) -> void:
	var cible := 0.0
	var ecart := _joueur_du_phare.global_position - _pied_montee_cartes.global_position
	# Dès que le robot prend de la hauteur sur la volée, elle reste visible jusqu'au palier.
	if visite_bureau and ecart.y < 0.25:
		cible = smoothstep(0.9, 1.7, Vector2(ecart.x, ecart.z).length())
	_transparence_montee_cartes = _fondre_maillages(_maillages_montee_cartes,
		_transparence_montee_cartes, cible, delta)


func _fondre_maillages(maillages: Array[GeometryInstance3D], depart: float, cible: float, delta: float) -> float:
	var transparence := move_toward(depart, cible, delta / maxf(duree_fondu, 0.01))
	if transparence == depart:
		return depart
	for maillage in maillages:
		maillage.transparency = transparence
		maillage.visible = transparence < 1.0
		maillage.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if transparence == 0.0 else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return transparence
