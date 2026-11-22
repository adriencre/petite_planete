extends Node
## Change l'apparence des bâtiments qui masquent le robot vu de l'extérieur.

@export var colonie: Node3D
@export var maquette_reveil: Node3D
@export var monde_phare: Node3D
@export var joueur: CharacterBody3D
@export var materiau: Material = preload("res://assets/ambiances/gris_fantome.tres")

class Batiment:
	var enveloppe: Array[MeshInstance3D] = []
	var interieur: Array[Node3D] = []
	var zones: Array[Area3D] = []
	var volume: AABB
	var materiaux: Dictionary[MeshInstance3D, Material] = {}
	var calques: Dictionary[VisualInstance3D, int] = {}
	var condition: Callable
	var fantome := false

var _batiments: Dictionary[String, Batiment] = {}
var _faces: Dictionary[Mesh, PackedVector3Array] = {}
@onready var _camera := joueur.get_node("Camera") as Camera3D


func _ready() -> void:
	process_priority = 10
	if colonie:
		_preparer_colonie()
	if maquette_reveil:
		_preparer_reveil()
	if monde_phare:
		_preparer_phare()


func _preparer_colonie() -> void:
	for enfant: Node in colonie.get_children():
		var nom := String(enfant.name)
		if nom.begins_with("Logis_"):
			var elements := nom.split("_")
			var cle := "_".join(elements.slice(0, 4))
			_ajouter_maillages(_batiment(cle), enfant)
		elif nom.begins_with("Maison_") or nom.begins_with("Verriere_") or nom == "Beffroi_civique":
			_ajouter_maillages(_batiment(nom), enfant)
	_amenager("ecole", ["Toit_ecole", "Socle_ecole", "Murs_hauts_ecole", "Murs_du_fond_ecole", "Soubassement_ecole", "Preau_de_l_ecole"],
		["Mobilier_ecole", "Affaires_de_classe", "Pupitre_Aube"],
		["AncienCorpsEcole", "TableauComptine", "DessinEscalier"], ["InterieurEcole"])
	_amenager("aube", ["Toit_Aube", "Socle_Aube", "Murs_hauts_Aube", "Murs_fond_Aube", "Cave_bas_Aube", "Cave_haut_Aube", "Cave_fond_Aube", "Etage_bas_Aube"],
		["Plancher_Aube", "Palier_Aube", "Palier_Aube_creux", "Escalier_cave_Aube", "Mobilier_cave_Aube", "Mobilier_etage_Aube", "Objets_Aube", "Boite_musique_Aube", "Prise_boite_Aube", "Lanterne_chevet_Aube"],
		["PorteAube", "BoiteMusiqueAube", "CarnetAube", "DessinCoinNoir"], ["InterieurAube", "CaveAube", "PassageAube"])
	_amenager("quai", ["Toit_maison_du_quai", "Murs_hauts_maison_du_quai", "Socle_maison_du_quai", "Soubassement_maison_du_quai"],
		["Sol_et_objets_maison_du_quai", "Mobilier_maison_du_quai", "Poele_et_objets_du_port", "Premiere_valise"],
		[], ["InterieurMaisonDuQuai"])
	_amenager("couturieres", ["Toit_des_couturieres", "Murs_hauts_des_couturieres", "Socle_des_couturieres", "Soubassement_des_couturieres"],
		["Mobilier_des_couturieres", "Mannequin_et_outils", "Ouvrage_et_linge", "Valise_des_couturieres"],
		[], ["InterieurCouturieres"])
	_amenager("commune", ["Toit_maison_commune", "Murs_hauts_maison_commune", "Murs_du_fond_maison_commune",
			"Socle_maison_commune", "Soubassement_maison_commune", "Murs_hauts_bureau_commune",
			"Murs_du_fond_bureau_commune", "Soubassement_bureau_commune", "Socle_bureau_commune",
			"Porte_commune_gauche", "Porte_commune_droite", "Serrure_commune", "Verrou_commune",
			"Cran_commune_1", "Cran_commune_2", "Cran_commune_3"],
		["Sol_maison_commune", "Mobilier_maison_commune", "Objets_maison_commune", "Mobilier_bureau_commune",
			"Papiers_bureau_commune"],
		["PlanArchipel", "OrdresYsolde", "LettresTavin"], ["InterieurCommune"])


func _preparer_reveil() -> void:
	var abri := maquette_reveil.get_node_or_null("Abri")
	if abri:
		_configurer(abri, ["Base", "Toit", "Veilleuse"], ["Mobilier", "Berceau", "OrdreYsolde", "ModeEmploi"])
	var atelier := maquette_reveil.get_node_or_null("Atelier")
	if atelier:
		var batiment := _configurer(atelier, ["Base", "Toit"], [])
		for enfant: Node in atelier.get_children():
			if enfant is Node3D and enfant.scene_file_path.ends_with(".glb"):
				batiment.interieur.append(enfant as Node3D)


func _preparer_phare() -> void:
	var maison := monde_phare.get_node_or_null("Port/MaisonDuQuai")
	if maison:
		_configurer(maison, ["Toit", "Coupe", "murs", "socle", "Porte"],
			["mobilier", "Decor", "AiguilleMaree", "Cadres", "Lanterne", "Cahier", "DessinAube"])
	var hangar := monde_phare.get_node_or_null("Port/Hangar")
	if hangar:
		_configurer(hangar, ["Atelier", "Coupe", "Toit", "VantailGauche", "VantailDroit"], ["Mobilier", "Capteur"])
	var phare := monde_phare.get_node_or_null("Phare")
	if phare == null:
		return
	var batiment := _configurer(phare, [],
		["SalleDesMachines", "EscalierIris", "PalierIris", "EtageIris", "EtageCartes", "PorteCartes",
		"MonteeCartes", "MonteeGalerie", "GalerieHaute", "PorteCartesVerrouillee",
		"DocumentsBureau", "DocumentsCartes", "DocumentsChambre", "Engrenages", "AncienCorpsGalerie", "LunetteIris"])
	batiment.condition = Callable(phare, "exterieur_pour_fantome")
	var chambre := phare.find_child("ChambreIris", true, false)
	if chambre:
		for enfant: Node in chambre.get_children():
			if enfant is Node3D and enfant.name not in [&"ToitChambre", &"FacadesChambre"]:
				batiment.interieur.append(enfant as Node3D)
	_ajouter_maillages(batiment, phare.get_node_or_null("Modele"))


func _configurer(racine: Node, enveloppe: Array[String], interieur: Array[String]) -> Batiment:
	var batiment := _batiment(String(racine.name))
	for nom in interieur:
		var objet := racine.find_child(nom, true, false) as Node3D
		if objet:
			batiment.interieur.append(objet)
	for nom in enveloppe:
		_ajouter_maillages(batiment, racine.find_child(nom, true, false))
	var zone := racine.find_child("Interieur", true, false) as Area3D
	if zone:
		batiment.zones.append(zone)
	return batiment


func _ajouter_maillages(batiment: Batiment, racine: Node) -> void:
	if racine == null:
		return
	var pieces := racine.find_children("*", "MeshInstance3D", true, false)
	if racine is MeshInstance3D:
		pieces.push_front(racine)
	for noeud in pieces:
		var piece := noeud as MeshInstance3D
		if piece.mesh == null:
			continue
		var dedans := false
		for objet: Node3D in batiment.interieur:
			if objet == piece or objet.is_ancestor_of(piece):
				dedans = true
				break
		if not dedans and not batiment.enveloppe.has(piece):
			_ajouter_enveloppe(batiment, piece)


func _batiment(cle: String) -> Batiment:
	if not _batiments.has(cle):
		_batiments[cle] = Batiment.new()
	return _batiments[cle]


func _ajouter_enveloppe(batiment: Batiment, piece: MeshInstance3D) -> void:
	var limites := piece.global_transform * piece.get_aabb()
	batiment.volume = limites if batiment.enveloppe.is_empty() else batiment.volume.merge(limites)
	batiment.enveloppe.append(piece)


func _amenager(cle: String, enveloppe: Array[String], interieur: Array[String],
		objets: Array[String], zones: Array[String]) -> void:
	var batiment := _batiment(cle)
	for nom in enveloppe:
		_ajouter_maillages(batiment, colonie.get_node_or_null(NodePath(nom)))
	for nom in interieur:
		var piece := colonie.get_node_or_null(NodePath(nom)) as Node3D
		if piece:
			batiment.interieur.append(piece)
	for nom in objets:
		var objet := get_parent().get_node_or_null(NodePath(nom)) as Node3D
		if objet:
			batiment.interieur.append(objet)
	for nom in zones:
		var zone := get_parent().get_node_or_null(NodePath(nom)) as Area3D
		if zone:
			batiment.zones.append(zone)


func _process(_delta: float) -> void:
	var vue_du_joueur := _camera.is_current() and bool(joueur.get("vue_dessus")) and not bool(joueur.get("cinematique"))
	var origine := _camera.global_position
	var droite := _camera.global_basis.x
	var centre := joueur.global_position
	var reperes := PackedVector3Array()
	for hauteur: float in [0.15, 0.95, 1.8]:
		for decalage: float in [-0.34, 0.0, 0.34]:
			reperes.append(centre + Vector3.UP * hauteur + droite * decalage)
	for batiment: Batiment in _batiments.values():
		var masque := vue_du_joueur and _masque_entierement(batiment, origine, reperes)
		if masque != batiment.fantome:
			_changer_apparence(batiment, masque)


func _masque_entierement(batiment: Batiment, origine: Vector3, reperes: PackedVector3Array) -> bool:
	if batiment.enveloppe.is_empty():
		return false
	if batiment.condition.is_valid() and not bool(batiment.condition.call()):
		return false
	for zone: Area3D in batiment.zones:
		if zone.overlaps_body(joueur):
			return false
	for repere: Vector3 in reperes:
		var depart := origine + origine.direction_to(repere) * _camera.near
		if batiment.volume.intersects_segment(depart, repere) == null:
			return false
		if not _coupe_enveloppe(batiment, depart, repere):
			return false
	return true


func _coupe_enveloppe(batiment: Batiment, depart: Vector3, arrivee: Vector3) -> bool:
	for piece: MeshInstance3D in batiment.enveloppe:
		if not piece.is_visible_in_tree() or piece.transparency >= 0.99:
			continue
		var a := piece.to_local(depart)
		var b := piece.to_local(arrivee)
		if piece.get_aabb().grow(0.001).intersects_segment(a, b) == null:
			continue
		if not _faces.has(piece.mesh):
			_faces[piece.mesh] = piece.mesh.get_faces()
		var faces: PackedVector3Array = _faces[piece.mesh]
		for i in range(0, faces.size(), 3):
			if Geometry3D.segment_intersects_triangle(a, b, faces[i], faces[i + 1], faces[i + 2]) != null:
				return true
	return false


func _changer_apparence(batiment: Batiment, fantome: bool) -> void:
	batiment.fantome = fantome
	for piece: MeshInstance3D in batiment.enveloppe:
		if fantome:
			batiment.materiaux[piece] = piece.material_override
			piece.material_override = materiau
		else:
			piece.material_override = batiment.materiaux[piece]
	if not fantome:
		for visuel: VisualInstance3D in batiment.calques:
			if is_instance_valid(visuel):
				visuel.layers = batiment.calques[visuel]
		batiment.calques.clear()
		return
	# Les scripts de visite peuvent continuer à régler la visibilité des pièces.
	for objet: Node3D in batiment.interieur:
		if not is_instance_valid(objet):
			continue
		var visuels := objet.find_children("*", "GeometryInstance3D", true, false)
		if objet is GeometryInstance3D:
			visuels.push_front(objet)
		for noeud in visuels:
			var visuel := noeud as VisualInstance3D
			if not batiment.calques.has(visuel):
				batiment.calques[visuel] = visuel.layers
				visuel.layers = 0
