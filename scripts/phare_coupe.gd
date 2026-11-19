extends "res://scripts/batiment_coupe.gd"
## Dégage l'étage que le robot traverse sans modifier les collisions du bâtiment.

@onready var _bureau: Node3D = find_child("EtageIris", true, false) as Node3D
@onready var _montee_cartes: Node3D = find_child("MonteeCartes", true, false) as Node3D
@onready var _cartes: Node3D = find_child("EtageCartes", true, false) as Node3D
@onready var _montee_galerie: Node3D = find_child("MonteeGalerie", true, false) as Node3D
@onready var _galerie: Node3D = find_child("GalerieHaute", true, false) as Node3D
@onready var _documents_bureau: Node3D = $DocumentsBureau
@onready var _documents_cartes: Node3D = $DocumentsCartes
@onready var _palier: Marker3D = $ReperePalierIris
@onready var _palier_cartes: Marker3D = $ReperePalierCartes
@onready var _seuil_galerie: Marker3D = $RepereSeuilGalerie
var _joueur_du_phare: Node3D


func _physics_process(_delta: float) -> void:
	if not is_instance_valid(_joueur_du_phare):
		_joueur_du_phare = get_tree().get_first_node_in_group("joueur") as Node3D
	if _bureau == null or _joueur_du_phare == null:
		return
	var dehors := _dedans == 0
	var hauteur := _joueur_du_phare.global_position.y
	var niveau_bureau := hauteur >= _palier.global_position.y - 0.12
	var niveau_cartes := hauteur >= _palier_cartes.global_position.y - 0.24
	var niveau_galerie := hauteur >= _seuil_galerie.global_position.y - 0.22
	_bureau.visible = dehors or (niveau_bureau and not niveau_cartes)
	_documents_bureau.visible = _bureau.visible
	if _montee_cartes and _cartes and _montee_galerie and _galerie:
		_montee_cartes.visible = dehors or (niveau_bureau and not niveau_galerie)
		_cartes.visible = dehors or (niveau_cartes and not niveau_galerie)
		_documents_cartes.visible = _cartes.visible
		_montee_galerie.visible = dehors or niveau_cartes
		_galerie.visible = dehors or niveau_galerie
