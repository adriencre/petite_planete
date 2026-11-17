@tool
extends Node3D
## Un ponton de bois où la barque s'amarre (scenes/ponton.tscn). On ne monte dans la barque et on n'en
## descend qu'à un ponton. L'origine est au bord de la terre ; le ponton part vers la mer, le long de +Z.
## Repères (à déplacer dans l'éditeur) :
##   Amarre        : où la barque s'arrête, proue vers +Z ;
##   Debarquement  : où le robot pose le pied en sautant de la barque ;
##   Bitte         : le poteau où la corde s'attache.
## Le bois (planches, pilotis, poteaux, lanterne) est fabriqué par ce script, aussi dans l'éditeur.
## La barque : scripts/barque.gd.

## Le port d'attache : la barque y attend au début, et y revient à chaque réveil.
@export var port_attache: bool = false
@export var longueur: float = 6.0:
	set(v): longueur = v; _construire()
@export var largeur: float = 1.6:
	set(v): largeur = v; _construire()
## Hauteur du plancher au-dessus de la mer (la terre du niveau 0 est à 0,6 m).
@export var hauteur_pont: float = 0.7:
	set(v): hauteur_pont = v; _construire()
## Longueur du ponton posée sur la terre.
@export var sur_terre: float = 1.5:
	set(v): sur_terre = v; _construire()
@export var graine: int = 7:
	set(v): graine = v; _construire()

const BOIS := Color(0.6, 0.44, 0.3)
const BOIS_CLAIR := Color(0.68, 0.52, 0.36)
const PILOTIS := Color(0.38, 0.29, 0.22)
const CORDE := Color(0.82, 0.72, 0.54)
const OR := Color(1.0, 0.76, 0.38)

var _lampe_mat: StandardMaterial3D
var _lampe: OmniLight3D
var _eclat: float = 0.0
var _eclat_tween: Tween


func _ready() -> void:
	add_to_group("pontons")
	_construire()


func amarre() -> Transform3D:
	var m := get_node_or_null("Amarre") as Node3D
	return m.global_transform if m else global_transform


func debarquement() -> Vector3:
	var m := get_node_or_null("Debarquement") as Node3D
	return m.global_position if m else global_position + Vector3.UP * hauteur_pont


func bitte() -> Vector3:
	var m := get_node_or_null("Bitte") as Node3D
	return m.global_position if m else global_position


## La petite lanterne du bout du ponton s'éveille quand la barque est assez près pour accoster.
func signaler(proche: bool) -> void:
	var cible := 1.0 if proche else 0.0
	if is_equal_approx(cible, _eclat) or _lampe_mat == null:
		return
	_eclat = cible
	if _eclat_tween:
		_eclat_tween.kill()
	_eclat_tween = create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	_eclat_tween.tween_property(_lampe_mat, "emission_energy_multiplier", lerpf(0.4, 3.5, cible), 0.6)
	_eclat_tween.tween_property(_lampe, "light_energy", lerpf(0.0, 1.4, cible), 0.6)


# ---------------------------------------------------------------- le bois

func _construire() -> void:
	if not is_inside_tree():
		return
	var ancien := get_node_or_null("Bois")
	if ancien:
		remove_child(ancien)
		ancien.free()
	var bois := Node3D.new()
	bois.name = "Bois"
	add_child(bois)   # pas de propriétaire : rien n'est enregistré dans la scène
	var rng := RandomNumberGenerator.new()
	rng.seed = graine
	var m_bois := _mat(BOIS)
	var m_clair := _mat(BOIS_CLAIR)
	var m_pilotis := _mat(PILOTIS)
	var m_corde := _mat(CORDE)
	var demi := largeur * 0.5
	# les planches, en travers, un peu irrégulières
	var z := -sur_terre
	var i := 0
	while z < longueur:
		var ep := rng.randf_range(0.26, 0.32)
		var planche := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = Vector3(largeur + rng.randf_range(-0.08, 0.1), 0.07, ep - 0.035)
		planche.mesh = b
		planche.material_override = m_clair if i % 3 == 1 else m_bois
		planche.position = Vector3(rng.randf_range(-0.04, 0.04), hauteur_pont - 0.035, z + ep * 0.5)
		planche.rotation = Vector3(0, rng.randf_range(-0.03, 0.03), rng.randf_range(-0.015, 0.015))
		bois.add_child(planche)
		z += ep
		i += 1
	# les deux longerons sous les planches
	for cote in [-1.0, 1.0]:
		var long := MeshInstance3D.new()
		var lb := BoxMesh.new()
		lb.size = Vector3(0.14, 0.16, longueur + sur_terre)
		long.mesh = lb
		long.material_override = m_pilotis
		long.position = Vector3(cote * (demi - 0.2), hauteur_pont - 0.15, (longueur - sur_terre) * 0.5)
		bois.add_child(long)
	# les pilotis (seulement au-dessus de la mer), un peu penchés
	var zp := 0.6
	while zp <= longueur - 0.1:
		for cote in [-1.0, 1.0]:
			var p := _poteau(m_pilotis, 0.11, hauteur_pont + 1.2)
			p.position = Vector3(cote * (demi - 0.12), hauteur_pont * 0.5 - 0.6, zp)
			p.rotation = Vector3(rng.randf_range(-0.04, 0.04), 0, rng.randf_range(-0.04, 0.04))
			bois.add_child(p)
		zp += 1.8
	# les bittes d'amarrage, côté barque, avec un tour de corde
	var repere := get_node_or_null("Bitte") as Node3D
	var pos_bitte := repere.position if repere else Vector3(demi - 0.15, hauteur_pont + 0.3, longueur * 0.85)
	for pz in [pos_bitte.z, pos_bitte.z - 2.4]:
		var b2 := _poteau(m_pilotis, 0.1, 0.42)
		b2.position = Vector3(pos_bitte.x, hauteur_pont + 0.21, pz)
		bois.add_child(b2)
		var tour := MeshInstance3D.new()
		var tm := TorusMesh.new()
		tm.inner_radius = 0.1
		tm.outer_radius = 0.15
		tm.rings = 8
		tm.ring_segments = 5
		tour.mesh = tm
		tour.material_override = m_corde
		tour.position = Vector3(pos_bitte.x, hauteur_pont + 0.24, pz)
		bois.add_child(tour)
	# au bout, côté opposé : un poteau et sa petite lanterne (elle s'éveille quand la barque approche)
	var mat := _poteau(m_pilotis, 0.07, 1.7)
	mat.position = Vector3(-demi + 0.12, hauteur_pont + 0.85, longueur - 0.15)
	bois.add_child(mat)
	var bras := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.06, 0.06, 0.45)
	bras.mesh = bm
	bras.material_override = m_pilotis
	bras.position = Vector3(-demi + 0.12, hauteur_pont + 1.62, longueur + 0.05)
	bois.add_child(bras)
	var lampe := MeshInstance3D.new()
	var sm := CylinderMesh.new()
	sm.top_radius = 0.06
	sm.bottom_radius = 0.09
	sm.height = 0.2
	sm.radial_segments = 6
	sm.rings = 1
	lampe.mesh = sm
	_lampe_mat = _mat(Color(1.0, 0.93, 0.78))
	_lampe_mat.emission_enabled = true
	_lampe_mat.emission = OR
	_lampe_mat.emission_energy_multiplier = lerpf(0.4, 3.5, _eclat)
	lampe.material_override = _lampe_mat
	lampe.position = Vector3(-demi + 0.12, hauteur_pont + 1.45, longueur + 0.22)
	bois.add_child(lampe)
	_lampe = OmniLight3D.new()
	_lampe.light_color = OR
	_lampe.omni_range = 4.0
	_lampe.light_energy = lerpf(0.0, 1.4, _eclat)
	lampe.add_child(_lampe)
	if not Engine.is_editor_hint():
		_collisions(bois)


## Le plancher (épais : il arrête aussi la barque) et des murets invisibles le long des bords,
## pour ne pas tomber à l'eau en marchant (on monte dans la barque avec E, d'un saut).
func _collisions(bois: Node3D) -> void:
	var corps := StaticBody3D.new()
	corps.name = "CorpsPonton"
	bois.add_child(corps)
	var demi := largeur * 0.5
	var total := longueur + sur_terre
	var centre_z := (longueur - sur_terre) * 0.5
	_boite(corps, Vector3(largeur, hauteur_pont + 0.6, total), Vector3(0, (hauteur_pont - 0.6) * 0.5, centre_z))
	for cote in [-1.0, 1.0]:
		_boite(corps, Vector3(0.1, 1.2, longueur), Vector3(cote * (demi + 0.05), hauteur_pont + 0.6, longueur * 0.5))
	_boite(corps, Vector3(largeur, 1.2, 0.1), Vector3(0, hauteur_pont + 0.6, longueur + 0.05))


func _boite(corps: StaticBody3D, taille: Vector3, pos: Vector3) -> void:
	var cs := CollisionShape3D.new()
	var b := BoxShape3D.new()
	b.size = taille
	cs.shape = b
	cs.position = pos
	corps.add_child(cs)


func _poteau(m: Material, rayon: float, hauteur: float) -> MeshInstance3D:
	var p := MeshInstance3D.new()
	var c := CylinderMesh.new()
	c.top_radius = rayon * 0.9
	c.bottom_radius = rayon
	c.height = hauteur
	c.radial_segments = 6
	c.rings = 1
	p.mesh = c
	p.material_override = m
	return p


func _mat(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 0.9
	return m
