extends Node3D
## La barque des Semeurs (assets/models/barque.glb, découpée par tools/blender/barque.py). Elle avance
## à la lumière : rien de magique, le robot branche le câble de son poignet dans la prise de la barque
## et sa batterie alimente la lanterne de proue, qui la pousse.
##
## Elle attend amarrée à un ponton (scenes/ponton.tscn), au port d'attache au début et à chaque réveil.
## - E sur le ponton, près d'elle : le robot saute dedans, s'assoit, se branche ; la corde se dénoue.
## - Z / S : avancer, freiner puis reculer. Q / D : la barre (elle tourne mieux quand elle a de l'erre).
##   La barque a du poids : elle glisse, dérive un peu dans les virages, s'y penche, et rebondit
##   doucement contre la côte. La caméra la suit de derrière, en souplesse.
## - Près d'un ponton, sa petite lanterne s'éveille : E, la barque vient s'amarrer toute seule,
##   la corde se noue, le robot se débranche et saute sur le ponton.
## - Au large (large.gd) : cap sur la silhouette d'une autre île, on entre dans la brume et on traverse ;
##   sur l'autre île, la barque arrive en mer devant le port, le robot déjà à la barre.

const CABLE := preload("res://scripts/cable.gd")
const SONS := preload("res://scripts/sons.gd")

@export_group("Navigation")
@export var vitesse_max: float = 4.2
## m/s² pour prendre de la vitesse.
@export var acceleration: float = 1.1
## m/s² quand on freine (S en avançant).
@export var freinage: float = 2.2
## m/s² quand on lâche tout : elle continue sur son erre.
@export var erre: float = 0.4
## Vitesse en marche arrière, en part de la vitesse max.
@export var part_arriere: float = 0.3
## rad/s à pleine erre.
@export var virage: float = 0.95
## Part du virage possible à l'arrêt (elle pivote doucement sur place).
@export var virage_a_l_arret: float = 0.35
## rad/s² : la barre met un peu de temps à mordre.
@export var reactivite_barre: float = 2.4
## Plus c'est haut, moins elle dérive de côté dans les virages.
@export var quille: float = 2.2
## Sans nœud « Large » dans la scène : on ne s'éloigne pas à plus de ça du centre de l'île.
## Avec un Large (large.gd), c'est lui qui décide : brume du large, traversée ou courant.
@export var rayon_max: float = 60.0
@export var suit_maree := false
@export_group("Caméra")
@export var distance_camera: float = 8.0
@export var hauteur_camera: float = 4.2
## Où regarde la caméra, devant la barque (m).
@export var regard_avant: float = 3.5
## Vitesse à laquelle la caméra se replace derrière la barque quand elle tourne.
@export var suivi_camera: float = 1.4
## Durée du passage vue de dessus <-> caméra de la barque (s).
@export var duree_bascule: float = 2.2
## 1re personne : à la barre, rester dans les yeux du robot assis. Décidé le 2026-11-23 : non, la barque se
## pilote toujours en vue extérieure (caméra de poursuite) ; on revient dans ses yeux en débarquant.
@export var yeux_a_la_barre: bool = false
## Hauteur des yeux du robot assis au-dessus du plancher, et durée du passage poursuite <-> yeux.
@export var hauteur_yeux_assis: float = 1.28
@export var duree_yeux: float = 1.4
@export_group("Ponton")
## Distance (m) à l'amarre d'un ponton sous laquelle on peut accoster (E).
@export var distance_amarrage: float = 7.0
## Distance (m) robot - barque pour y monter depuis le ponton.
@export var distance_monter: float = 3.2
@export_group("Lumière")
## Batterie consommée par seconde à pleine vitesse (≈ 2 min de navigation avec une batterie pleine).
@export var consommation: float = 0.008
## En dessous, la batterie ne descend plus : la barque avance encore, lentement (on ne reste jamais coincé en mer).
@export var reserve: float = 0.12
@export var couleur_or: Color = Color(1.0, 0.76, 0.38)
## Rayon (m) du rond sans brume autour de la lanterne de proue : à l'arrêt (branchée), à pleine vitesse.
## Au moins le triple de celui du robot (brume_batterie.gd : rayon_plein = 5,5 m).
@export var rayon_brume_arret: float = 17.0
@export var rayon_brume_vitesse: float = 22.0
## Amarrée, sans personne : la petite lueur de veille repousse un peu la brume.
@export var rayon_brume_veille: float = 5.0

## Points de la coque (repère de la barque, proue vers +Z) qui touchent la côte ou les pontons.
const COQUE: Array[Vector3] = [
	Vector3(0, 0, 1.75), Vector3(0.38, 0, 1.25), Vector3(-0.38, 0, 1.25),
	Vector3(0.6, 0, 0.3), Vector3(-0.6, 0, 0.3), Vector3(0.55, 0, -1.0), Vector3(-0.55, 0, -1.0),
	Vector3(0, 0, -1.65),
]
## Où la corde s'attache sur la barque (à la proue).
const TAQUET := Vector3(0, 0.4, 1.15)

@export var maquette: Node        # pour savoir où est la terre (maquette.gd : _case_a)
var pilotee: bool = false
var _joueur: CharacterBody3D
var _robot: Node3D
var _corps: StaticBody3D
var _siege: Node3D
var _prise: Node3D
var _en_cours: bool = false
var _tenir: bool = false            # le robot est assis : il suit la barque
var _t: float = 0.0

# le mouvement (sur l'eau, y = 0)
var _pos := Vector3.ZERO
var _cap: float = 0.0
var _vel := Vector3.ZERO
var _vit_ang: float = 0.0
var _v_prec: float = 0.0
var _roulis: float = 0.0
var _tangage: float = 0.0
var _enfonce: float = 0.0           # quand le robot saute dedans

# la caméra
var _cam_melange: float = 0.0
## 1re personne : 0 = caméra de la barque (poursuite), 1 = dans les yeux du robot assis.
var _yeux: float = 0.0
## Le regard du robot assis, par rapport à la proue (souris, en 1re personne).
var _regard_yaw: float = 0.0
var _regard_pitch: float = -0.08
var _cam_yaw: float = 0.0
var _cam_recul: float = 8.0

# le ponton
var _ponton: Node3D = null          # celui où elle est amarrée
var _ponton_vise: Node3D = null     # celui où on peut accoster
var _corde
var _noue: float = 0.0              # 0 = corde à bord, 1 = nouée à la bitte

var _cable
var _prise_externe: Marker3D
var _branche: float = 0.0           # 0 = câble rangé, 1 = fiche dans la prise
var _lanterne_mat: BaseMaterial3D
var _lueur: OmniLight3D
var _sillage: CPUParticles3D
var _ecume: CPUParticles3D
var _rayon_brume: float = 0.0
var _lanterne: Node3D
var _large: Node3D
@onready var _touche: Label3D = get_node_or_null("ToucheEmbarquement") as Label3D


func _ready() -> void:
	_siege = find_child("Siege", true, false) as Node3D
	_prise = find_child("Prise", true, false) as Node3D
	for c in get_children():
		if c is StaticBody3D:
			_corps = c
	_pos = Vector3(global_position.x, 0.0, global_position.z)
	_cap = rotation.y
	add_to_group("interactif")
	add_to_group("barque_qui_flotte")
	_preparer_lanterne()
	_sillage = _particules(Vector3(0, 0.05, -1.7), Color(1.0, 0.9, 0.6), Color(1.0, 0.7, 0.35, 0.0), 0.09, 2.6, 90)
	_ecume = _particules(Vector3(0, 0.08, 1.55), Color(1.0, 1.0, 0.97, 0.9), Color(1.0, 1.0, 1.0, 0.0), 0.07, 0.9, 50)
	_ecume.emission_box_extents = Vector3(0.3, 0.02, 0.05)
	_ecume.initial_velocity_max = 0.7
	_ecume.gravity = Vector3(0, -2.0, 0)
	((_ecume.mesh as PrimitiveMesh).material as BaseMaterial3D).blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	_cable = CABLE.new()
	_cable.visible = false
	_cable.affaissement = 0.12
	add_child(_cable)
	_corde = CABLE.new()
	_corde.visible = false
	_corde.affaissement = 0.18
	_corde.epaisseur = 0.017
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.8, 0.7, 0.52)
	m.roughness = 1.0
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	_corde.material_override = m
	add_child(_corde)
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if _joueur:
		_robot = _joueur.get("modele")
	var port := _port()
	if port:
		_amarrer_tout_de_suite(port)
	_large = get_tree().get_first_node_in_group("large") as Node3D
	if _large and _joueur and bool(_large.call("arrivee_par_la_mer")):
		_arriver_du_large()


## Après une traversée (large.gd) : la barque sort de la brume devant le port, le robot déjà assis et
## branché, avec un peu d'erre ; on reprend la barre tout de suite.
func _arriver_du_large() -> void:
	var a: Transform3D = _large.call("arrivee")
	_pos = Vector3(a.origin.x, 0.0, a.origin.z)
	_cap = atan2(a.basis.z.x, a.basis.z.z)
	_vel = _avant() * vitesse_max * 0.45
	_v_prec = _vel.length()
	_vit_ang = 0.0
	_ponton = null
	_noue = 0.0
	_corde.visible = false
	var b: float = float(Sauvegarde.batterie_arrivee)
	if b >= 0.0:
		_joueur.set("batterie", b)
	_joueur.set("cinematique", true)
	_joueur.set("embarque", self)
	_joueur.velocity = Vector3.ZERO
	if _corps:
		_joueur.add_collision_exception_with(_corps)
	_poser()
	_tenir = true
	_tenir_robot()
	if _robot:
		_robot.call("jouer_action", "assis", 1.0, 0.2)
	_cam_yaw = _cap
	_cam_recul = distance_camera
	_cam_melange = 1.0
	_branche = 1.0
	_cable.materiau.set_shader_parameter("flux", 0.0)
	_cable.visible = true
	_lanterne_mat.emission_energy_multiplier = 1.5
	_lueur.light_energy = 1.2
	pilotee = true


## Après une mort : la barque revient au port d'attache, toujours à flot (ILE_01_REVEIL.md §13.2).
func revenir_au_port() -> void:
	if pilotee or _en_cours:
		return
	var port := _port()
	if port:
		_amarrer_tout_de_suite(port)


func _port() -> Node3D:
	var pontons := get_tree().get_nodes_in_group("pontons")
	for p in pontons:
		if bool(p.get("port_attache")):
			return p
	return pontons[0] if not pontons.is_empty() else null


func _amarrer_tout_de_suite(p: Node3D) -> void:
	var a: Transform3D = p.call("amarre")
	_pos = Vector3(a.origin.x, 0.0, a.origin.z)
	_cap = atan2(a.basis.z.x, a.basis.z.z)
	_vel = Vector3.ZERO
	_vit_ang = 0.0
	_ponton = p
	_noue = 1.0
	_corde.visible = true


# ---------------------------------------------------------------- outils

func _plat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0, v.z)


func _avant() -> Vector3:
	return Vector3(sin(_cap), 0, cos(_cap))


## Le flanc gauche (vers +X quand la proue regarde +Z).
func _gauche() -> Vector3:
	return Vector3(cos(_cap), 0, -sin(_cap))


func _base() -> Basis:
	return Basis(Vector3.UP, _cap)


## Où poser le robot : sur le plancher, sous le banc (le clip « assis » garde les pieds à l'origine).
func _place_robot() -> Vector3:
	var s: Vector3 = _siege.global_position if _siege else global_position
	return s - global_basis.y * 0.43


func _pos_prise() -> Vector3:
	return _prise.global_position if _prise else global_position + Vector3.UP * 0.3


func _clef(touches: Array) -> float:
	for k in touches:
		if Input.is_physical_key_pressed(k):
			return 1.0
	return 0.0


# ---------------------------------------------------------------- chaque image

func _process(delta: float) -> void:
	delta = minf(delta, 0.05)
	_t += delta
	if pilotee and not _en_cours:
		_naviguer(delta)
	else:
		_vel = _vel.lerp(Vector3.ZERO, 1.0 - exp(-1.5 * delta))
		_roulis = lerpf(_roulis, 0.0, 1.0 - exp(-2.0 * delta))
		_tangage = lerpf(_tangage, 0.0, 1.0 - exp(-2.0 * delta))
		if not _en_cours:
			_lumiere(0.0)
			_appeler(delta)
	_poser()
	if _touche:
		_touche.visible = etat_interaction() == 2
		if _touche.visible:
			_touche.global_position = point_appel() + Vector3.UP * 1.0
			_touche.text = "E   Accoster" if pilotee else "E   Embarquer"
	if _joueur and _joueur.get("embarque") == self:
		if _tenir:
			_tenir_robot()
		_placer_camera(delta)
		if is_instance_valid(_prise_externe):
			_joueur.call("_appliquer_cine")
	if _cable.visible and _joueur:
		var poignet: Vector3 = _joueur.call("poignet_droit_monde")
		_cable.debut = poignet
		var prise := _prise_externe.global_position if is_instance_valid(_prise_externe) else _pos_prise()
		_cable.fin = poignet.lerp(prise, _branche)
	_brume(delta)
	if _corde.visible:
		var taquet := global_transform * TAQUET
		var bitte: Vector3 = _ponton.call("bitte") if _ponton else taquet
		_corde.debut = taquet
		_corde.fin = taquet.lerp(bitte, _noue)


## La barque sur l'eau : le cap, la houle, le roulis des virages, le tangage quand elle accélère.
func _poser() -> void:
	var houle_y := sin(_t * 1.1) * 0.05 - _enfonce
	var tangage := _tangage + sin(_t * 0.6) * 0.02
	var roulis := _roulis + sin(_t * 0.8 + 1.0) * 0.035
	global_transform = Transform3D(Basis.from_euler(Vector3(tangage, _cap, roulis)), _pos + Vector3.UP * (_eau() + houle_y))
	set_meta("origine", _pos)


## Le robot assis fait corps avec la barque : il penche et tangue avec elle, face à la proue.
func _tenir_robot() -> void:
	var p := _place_robot()
	_joueur.global_position = p
	_joueur.velocity = Vector3.ZERO
	if _robot:
		_robot.global_transform = Transform3D(global_basis, p)


## Amarrée, quand le robot est sur le ponton tout près : la lanterne de proue respire doucement.
func _appeler(_delta: float) -> void:
	if _lanterne_mat == null or _joueur == null:
		return
	var pres := _peut_monter()
	_lanterne_mat.emission_energy_multiplier = 0.55 + 0.35 * sin(_t * 2.6) if pres else 0.3


# ---------------------------------------------------------------- naviguer

func _naviguer(delta: float) -> void:
	var avance := _clef([KEY_W, KEY_UP])
	var recule := _clef([KEY_S, KEY_DOWN])
	var barre := _clef([KEY_D, KEY_RIGHT]) - _clef([KEY_A, KEY_LEFT])
	var avant := _avant()
	var gauche := _gauche()
	var v_av := _vel.dot(avant)
	var v_lat := _vel.dot(gauche)
	# la lumière pousse : batterie faible, barque lente (jamais à l'arrêt complet)
	var b: float = _joueur.get("batterie")
	var force := clampf(b * 1.6, 0.35, 1.0)
	var cible := 0.0
	var taux := erre
	if avance > 0.0:
		cible = vitesse_max * force
		taux = acceleration
	elif recule > 0.0:
		cible = -vitesse_max * part_arriere * force
		taux = freinage if v_av > 0.2 else acceleration * 0.6
	v_av = move_toward(v_av, cible, taux * delta)
	v_lat *= exp(-quille * delta)   # la quille : elle ne glisse pas longtemps de côté
	_vel = avant * v_av + gauche * v_lat
	# la barre mord mieux avec de l'erre ; en marche arrière, elle tourne à l'envers
	var erre_rel := clampf(absf(v_av) / (vitesse_max * 0.5), 0.0, 1.0)
	var efficacite := lerpf(virage_a_l_arret, 1.0, erre_rel)
	var sens := -1.0 if v_av < -0.2 else 1.0
	_vit_ang = move_toward(_vit_ang, -barre * virage * efficacite * sens, reactivite_barre * delta)
	_cap = wrapf(_cap + _vit_ang * delta, -PI, PI)
	_pos += _vel * delta
	_heurter()
	_au_large(delta)
	# elle se penche dans les virages, lève le nez quand elle accélère
	var accel := (v_av - _v_prec) / maxf(delta, 0.001)
	_v_prec = v_av
	_roulis = lerpf(_roulis, clampf(-_vit_ang * v_av * 0.07, -0.13, 0.13), 1.0 - exp(-3.0 * delta))
	_tangage = lerpf(_tangage, clampf(-accel * 0.035 - absf(v_av) * 0.008, -0.08, 0.05), 1.0 - exp(-3.0 * delta))
	# la batterie part dans la lanterne
	var t := absf(v_av) / vitesse_max
	if avance + recule > 0.0 and b > reserve:
		_joueur.set("batterie", maxf(reserve, b - consommation * maxf(t, 0.25) * delta))
	_lumiere(t)
	# un ponton tout près ? sa lanterne s'éveille
	_ponton_vise = null
	var distance_visee := distance_amarrage
	for p in get_tree().get_nodes_in_group("pontons"):
		var a: Transform3D = p.call("amarre")
		var distance := _plat(a.origin - _pos).length()
		p.call("signaler", distance < distance_amarrage)
		if distance < distance_visee and _amarrage_possible(p):
			_ponton_vise = p
			distance_visee = distance


func _amarrage_possible(ponton: Node3D) -> bool:
	return not ponton.has_method("amarrage_possible") or bool(ponton.call("amarrage_possible"))


func _eau() -> float:
	return HorlogeMonde.niveau_mer() if suit_maree else 0.0


## La côte, les rochers, les pontons : la barque s'y appuie et glisse le long, ou rebondit un peu.
func _heurter() -> void:
	var espace := get_world_3d().direct_space_state
	var hauteur := _eau() + 0.3
	var depuis := _pos + Vector3.UP * hauteur
	var exclus: Array[RID] = [_joueur.get_rid()]
	if _corps:
		exclus.append(_corps.get_rid())
	for local in COQUE:
		var w := _pos + _base() * local + Vector3.UP * hauteur
		var n := Vector3.ZERO
		if maquette:
			var case: Dictionary = maquette.call("_case_a", w)
			var terrain: Vector3 = case.centre
			if int(case.niv) >= 0 and (not suit_maree or terrain.y >= _eau() - 0.14):
				n = _plat(_pos - w).normalized()
		var q := PhysicsRayQueryParameters3D.create(depuis, w)
		q.exclude = exclus
		var touche := espace.intersect_ray(q)
		if not touche.is_empty():
			var nh := _plat(touche.normal)
			n = nh.normalized() if nh.length() > 0.1 else _plat(_pos - w).normalized()
		if n == Vector3.ZERO:
			continue
		var vn := _vel.dot(n)
		if vn < 0.0:
			_vel -= n * vn * 1.25          # un petit rebond
			_vel *= 0.92
			if -vn > 0.7:
				_choc(-vn)
		_pos += n * 0.02                   # elle se décolle doucement
		# touchée sur l'avant ou l'arrière d'un flanc : elle pivote un peu
		_vit_ang += clampf(local.z * n.dot(_gauche()) * -0.4, -0.3, 0.3) * absf(minf(vn, 0.0))


func _choc(force: float) -> void:
	SONS.jouer("clic", _pos, -10.0 + force * 3.0, 0.55)
	_roulis += randf_range(-1.0, 1.0) * 0.04 * force
	_tangage += 0.03 * force


## Trop loin de l'île : un courant la ramène doucement. Avec un Large : la brume du large et la traversée.
func _au_large(delta: float) -> void:
	if _large:
		var courant: Vector3 = _large.call("au_large", _pos, _avant(), delta)
		_vel += courant * delta
		return
	if maquette == null:
		return
	var centre := _plat((maquette as Node3D).global_position)
	var vers := _plat(_pos - centre)
	var trop := vers.length() - rayon_max
	if trop > 0.0:
		_vel -= vers.normalized() * trop * 1.2 * delta


## Plus la barque va vite, plus la lanterne brille, plus les pulsations courent dans le câble, plus le sillage luit.
func _lumiere(t: float) -> void:
	if pilotee:
		if _lanterne_mat:
			_lanterne_mat.emission_energy_multiplier = lerpf(1.5, 5.0, t)
		if _lueur:
			_lueur.light_energy = lerpf(1.2, 3.0, t)
			_lueur.omni_range = lerpf(3.0, 6.0, t)
		_cable.materiau.set_shader_parameter("flux", clampf(t * 1.5, 0.0, 1.0))
	_sillage.emitting = pilotee and t > 0.08
	_ecume.emitting = pilotee and t > 0.45


## La lumière de la lanterne de proue repousse la brume, comme l'antenne du robot : un rond qui
## large (au moins le triple de celui du robot), qui grandit encore quand on va vite.
func _brume(delta: float) -> void:
	var cible := rayon_brume_veille
	if pilotee or _branche > 0.5:
		var t := clampf(absf(_vel.dot(_avant())) / vitesse_max, 0.0, 1.0)
		cible = lerpf(rayon_brume_arret, rayon_brume_vitesse, t)
	_rayon_brume = move_toward(_rayon_brume, cible, delta * 7.0)


## Pour brume_batterie.gd (qui le passe aux shaders de brume) : xyz = la lanterne de proue, w = rayon.
func bulle_lanterne() -> Vector4:
	var p: Vector3 = _lanterne.global_position if _lanterne else global_transform * Vector3(0, 0.6, 1.6)
	return Vector4(p.x, p.y, p.z, _rayon_brume)


# ---------------------------------------------------------------- la caméra

## Vue de dessus (à terre) <-> caméra derrière la barque, en fondu. La caméra suit le cap avec
## un peu de retard, et recule un peu quand on va vite ; la houle ne la secoue pas.
func _placer_camera(delta: float) -> void:
	var cam: Camera3D = _joueur.get("camera")
	if cam == null:
		return
	_cam_yaw = lerp_angle(_cam_yaw, _cap, 1.0 - exp(-suivi_camera * delta))
	var dir := Vector3(sin(_cam_yaw), 0, cos(_cam_yaw))
	_cam_recul = lerpf(_cam_recul, distance_camera + absf(_vel.dot(_avant())) * 0.35, 1.0 - exp(-1.5 * delta))
	var oeil := _pos + Vector3.UP * hauteur_camera - dir * _cam_recul
	var vise := _pos + dir * regard_avant + Vector3.UP * 0.5
	var poursuite := Transform3D(Basis.looking_at(vise - oeil), oeil)
	# d'où l'on part et où l'on revient : la vue du joueur (de dessus, ou dans ses yeux, ou derrière lui)
	var libre: Transform3D = _joueur.call("transform_vue_libre")
	var k := _cam_melange * _cam_melange * (3.0 - 2.0 * _cam_melange)
	var vue := libre.interpolate_with(poursuite, k)
	# en 1re personne, une fois à la barre (hors manœuvres filmées), on revient dans les yeux du robot assis
	var yeux_voulus: bool = yeux_a_la_barre and _en_1re() and pilotee and not _en_cours and not is_instance_valid(_prise_externe)
	_yeux = move_toward(_yeux, 1.0 if yeux_voulus else 0.0, delta / maxf(0.1, duree_yeux))
	if _yeux > 0.0:
		var y := _yeux * _yeux * (3.0 - 2.0 * _yeux)
		vue = vue.interpolate_with(_vue_yeux(), y)
	cam.global_transform = vue
	# la lumière de l'antenne suit le robot assis (en 1re personne elle resterait collée à la caméra)
	var lum: Node3D = _joueur.get("lumiere")
	if lum:
		lum.global_position = _place_robot() + global_basis.y * 2.0
	# on ne voit pas le robot quand on est dans sa tête (ni la caméra le traverser)
	if _robot:
		var tete := _place_robot() + global_basis.y * hauteur_yeux_assis
		_robot.visible = cam.global_position.distance_to(tete) > 0.75 and not (_yeux > 0.6)


func _en_1re() -> bool:
	return not bool(_joueur.get("vue_dessus")) and bool(_joueur.get("premiere_personne"))


## Les yeux du robot assis : face à la proue, la tête suit la souris ; la barque le berce.
func _vue_yeux() -> Transform3D:
	var oeil := _place_robot() + global_basis * Vector3(0, hauteur_yeux_assis, 0.12)
	return Transform3D(global_basis * Basis.from_euler(Vector3(_regard_pitch, PI + _regard_yaw, 0)), oeil)


func _basculer_camera(vers: float) -> Tween:
	var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(self, "_cam_melange", vers, duree_bascule)
	return t


## Une bouée ne peut prendre la main que pendant la navigation libre.
func peut_recharger() -> bool:
	return pilotee and not _en_cours and _ponton_vise == null


func brancher_recharge(prise: Marker3D) -> void:
	_en_cours = true
	_vel = Vector3.ZERO
	_lumiere(0.0)
	SONS.jouer("clic", _pos_prise(), -8.0)
	await _deplacer_fiche(0.0, 0.40)
	_prise_externe = prise
	await _deplacer_fiche(1.0, 0.62)
	SONS.jouer("clic", prise.global_position, -5.0, 0.9)


func _deplacer_fiche(fraction: float, duree: float) -> void:
	var geste := create_tween().set_trans(Tween.TRANS_SINE)
	geste.tween_property(self, "_branche", fraction, duree)
	await geste.finished


func flux_recharge(sens: float, intensite: float) -> void:
	_cable.materiau.set_shader_parameter("sens", sens)
	_cable.materiau.set_shader_parameter("flux", intensite)


func reprendre_navigation() -> void:
	flux_recharge(1.0, 0.0)
	await _deplacer_fiche(0.0, 0.40)
	_prise_externe = null
	await _deplacer_fiche(1.0, 0.50)
	SONS.jouer("clic", _pos_prise(), -8.0)
	_en_cours = false


# ---------------------------------------------------------------- monter / s'amarrer

func _unhandled_input(event: InputEvent) -> void:
	# 1re personne à la barre : la souris tourne la tête du robot (pas plus loin qu'un cou de robot)
	if event is InputEventMouseMotion and _joueur and _joueur.get("embarque") == self and _yeux > 0.0:
		var m := event as InputEventMouseMotion
		var sens: float = float(_joueur.get("sensibilite_souris"))
		_regard_yaw = clampf(_regard_yaw - m.relative.x * sens, -1.9, 1.9)
		_regard_pitch = clampf(_regard_pitch - m.relative.y * sens, -0.9, 0.7)
		return
	if not (event is InputEventKey) or _joueur == null or _en_cours:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo or k.physical_keycode != KEY_E:
		return
	if pilotee:
		if _ponton_vise and _amarrage_possible(_ponton_vise):
			get_viewport().set_input_as_handled()
			_amarrer(_ponton_vise)
	elif not bool(_joueur.get("cinematique")) and _peut_monter():
		get_viewport().set_input_as_handled()
		_embarquer()


## Pour guidage.gd : 2 = E possible (monter, ou accoster au ponton tout près), 1 = amarrée, 0 = rien.
## (`point_appel` : la barque, ou le ponton où l'on peut accoster.)
func etat_interaction() -> int:
	if _joueur == null or _en_cours:
		return 0
	if pilotee:
		return 2 if _ponton_vise else 0
	if not bool(_joueur.get("cinematique")) and _peut_monter():
		return 2
	return 1


func point_appel() -> Vector3:
	if pilotee and _ponton_vise:
		return _ponton_vise.call("debarquement")
	return global_position + Vector3.UP * 0.5


func _peut_monter() -> bool:
	return _plat(_joueur.global_position - _pos).length() < distance_monter


## Un saut en cloche du robot entre deux points ; `vers` est recalculé à chaque image (la barque bouge).
func _sauter(depuis: Vector3, vers: Callable, duree: float, hauteur: float, basis_fin: Callable) -> void:
	var basis_debut: Basis = _robot.global_basis if _robot else Basis()
	var pas := func(t: float) -> void:
		var p: Vector3 = depuis.lerp(vers.call(), t)
		p.y += sin(t * PI) * hauteur
		_joueur.global_position = p
		if _robot:
			var b: Basis = basis_fin.call()
			_robot.global_transform = Transform3D(basis_debut.slerp(b, clampf(t * 1.4, 0.0, 1.0)), p)
	var s := create_tween()
	s.tween_method(pas, 0.0, 1.0, duree).set_trans(Tween.TRANS_SINE)
	await s.finished


func _embarquer() -> void:
	_en_cours = true
	_joueur.set("cinematique", true)
	_joueur.set("embarque", self)
	_joueur.velocity = Vector3.ZERO
	if _corps:
		_joueur.add_collision_exception_with(_corps)
	_cam_yaw = _cap
	_cam_recul = distance_camera
	_regard_yaw = 0.0
	_regard_pitch = -0.08
	_basculer_camera(1.0)
	# il saute dans la barque ; elle s'enfonce un peu sous son poids
	await _sauter(_joueur.global_position, _place_robot, 0.75, 0.8, func() -> Basis: return global_basis)
	_tenir = true
	var poids := create_tween().set_trans(Tween.TRANS_SINE)
	poids.tween_property(self, "_enfonce", 0.09, 0.15).set_ease(Tween.EASE_OUT)
	poids.tween_property(self, "_enfonce", 0.0, 1.1).set_ease(Tween.EASE_IN_OUT)
	_roulis += 0.05
	if _robot:
		_robot.call("jouer_action", "assis", 1.0, 0.4)
	await get_tree().create_timer(0.5, false).timeout
	# il sort la fiche de son poignet et la branche : clic, la lanterne de proue s'éveille
	_cable.materiau.set_shader_parameter("flux", 0.0)
	_cable.visible = true
	var fiche := create_tween().set_trans(Tween.TRANS_SINE)
	fiche.tween_property(self, "_branche", 1.0, 0.5)
	await fiche.finished
	SONS.jouer("clic", _pos_prise(), -6.0)
	var eveil := create_tween().set_parallel()
	eveil.tween_property(_lanterne_mat, "emission_energy_multiplier", 1.5, 0.6)
	eveil.tween_property(_lueur, "light_energy", 1.2, 0.6)
	# la corde se dénoue et revient à bord
	if _corde.visible:
		var denoue := create_tween().set_trans(Tween.TRANS_SINE)
		denoue.tween_property(self, "_noue", 0.0, 0.7)
		await denoue.finished
		_corde.visible = false
	# elle s'écarte du ponton
	if _ponton:
		var cote := signf(_plat(_pos - _ponton.global_position).dot(_gauche()))
		_vel = _gauche() * cote * 0.5 + _avant() * 0.4
		_ponton = null
	pilotee = true
	_en_cours = false


func _amarrer(p: Node3D) -> void:
	if not _amarrage_possible(p):
		return
	_en_cours = true
	p.call("signaler", false)
	_joueur.set("cinematique", true)
	var a: Transform3D = p.call("amarre")
	var fin := Vector3(a.origin.x, 0.0, a.origin.z)
	var cap_fin := atan2(a.basis.z.x, a.basis.z.z)
	# elle s'amarre dans le sens où elle arrive (proue vers la mer ou vers la terre)
	if absf(wrapf(cap_fin - _cap, -PI, PI)) > PI * 0.5:
		cap_fin = wrapf(cap_fin + PI, -PI, PI)
	var debut := _pos
	var cap_debut := _cap
	var dist := _plat(fin - debut).length()
	var elan := debut + _vel.normalized() * minf(dist * 0.45, _vel.length() * 1.2) if _vel.length() > 0.1 else debut
	var duree := clampf(dist / 1.6, 2.0, 4.5)
	_vel = Vector3.ZERO
	_vit_ang = 0.0
	var approche := func(u: float) -> void:
		var e := 1.0 - pow(1.0 - u, 2.2)   # elle ralentit en arrivant
		var w := 1.0 - e
		_pos = debut * w * w + elan * 2.0 * w * e + fin * e * e
		_cap = lerp_angle(cap_debut, cap_fin, e * e * (3.0 - 2.0 * e))
		_lumiere(lerpf(0.4, 0.0, e))
	var glisse := create_tween()
	glisse.tween_method(approche, 0.0, 1.0, duree)
	await glisse.finished
	_pos = fin
	_cap = cap_fin
	# un petit choc contre le bois
	_roulis += 0.045
	SONS.jouer("clic", _pos, -12.0, 0.5)
	_ponton = p
	# la corde se noue à la bitte
	_noue = 0.0
	_corde.visible = true
	var noue := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	noue.tween_property(self, "_noue", 1.0, 0.8)
	await noue.finished
	await get_tree().create_timer(0.3, false).timeout
	# il se débranche : le câble se rembobine, la lanterne s'assoupit
	pilotee = false
	_sillage.emitting = false
	_ecume.emitting = false
	var range_cable := create_tween().set_parallel().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	range_cable.tween_property(self, "_branche", 0.0, 0.35)
	range_cable.tween_property(_lanterne_mat, "emission_energy_multiplier", 0.3, 0.8)
	range_cable.tween_property(_lueur, "light_energy", 0.6, 0.8)
	await range_cable.finished
	_cable.visible = false
	if _robot:
		_robot.call("fin_action")
	await get_tree().create_timer(0.4, false).timeout
	# il se lève et saute sur le ponton ; la caméra revient au-dessus de l'île (ou dans ses yeux, face à la terre)
	_tenir = false
	var pied: Vector3 = p.call("debarquement")
	var vers_terre := -_plat(p.global_basis.z).normalized()
	_joueur.call("regarder_vers", vers_terre)
	var bascule := _basculer_camera(0.0)
	var face := Basis(Vector3.UP, atan2(vers_terre.x, vers_terre.z))
	await _sauter(_joueur.global_position, func() -> Vector3: return pied, 0.8, 0.9, func() -> Basis: return face)
	_enfonce = 0.07
	create_tween().set_trans(Tween.TRANS_SINE).tween_property(self, "_enfonce", 0.0, 1.0)
	if _robot:
		_robot.transform = Transform3D(face, Vector3.ZERO)
	_joueur.velocity = Vector3.ZERO
	await bascule.finished
	if _robot:
		_robot.visible = true
	if _corps:
		_joueur.remove_collision_exception_with(_corps)
	_joueur.set("embarque", null)
	_joueur.set("cinematique", false)
	_en_cours = false


# ---------------------------------------------------------------- la lanterne de proue, le sillage

func _preparer_lanterne() -> void:
	var lant := find_child("Lanterne", true, false) as MeshInstance3D
	_lanterne = lant
	if lant == null:
		_lanterne_mat = StandardMaterial3D.new()
		_lueur = OmniLight3D.new()
		add_child(_lueur)
		return
	var m := lant.mesh.surface_get_material(0) if lant.mesh else null
	_lanterne_mat = (m.duplicate() as BaseMaterial3D) if m is BaseMaterial3D else StandardMaterial3D.new()
	_lanterne_mat.emission_enabled = true
	_lanterne_mat.emission = couleur_or
	_lanterne_mat.emission_energy_multiplier = 0.3
	lant.material_override = _lanterne_mat
	_lueur = OmniLight3D.new()
	_lueur.light_color = couleur_or
	_lueur.light_energy = 0.6
	_lueur.omni_range = 3.0
	lant.add_child(_lueur)


## Des grains de lumière qui restent sur l'eau là où ils tombent : le sillage doré (poupe), l'écume (proue).
func _particules(pos: Vector3, debut: Color, fin: Color, taille: float, vie: float, nombre: int) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(taille, taille)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.vertex_color_use_as_albedo = true
	quad.material = m
	p.mesh = quad
	p.local_coords = false
	p.amount = nombre
	p.lifetime = vie
	p.emitting = false
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(0.35, 0.02, 0.1)
	p.direction = Vector3.UP
	p.spread = 60.0
	p.initial_velocity_min = 0.05
	p.initial_velocity_max = 0.25
	p.gravity = Vector3.ZERO
	p.damping_min = 0.5
	p.damping_max = 1.0
	var g := Gradient.new()
	g.set_color(0, debut)
	g.set_color(1, fin)
	p.color_ramp = g
	p.position = pos
	add_child(p)
	return p
