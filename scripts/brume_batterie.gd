extends Node
## La lumière de l'antenne repousse la brume, et c'est ça qui use la batterie (DESIGN.md, « Le moteur »).
## - Autour du robot, un rond sans brume : sa taille suit la batterie (pleine = large, presque vide = la
##   brume se referme sur lui). C'est la jauge de batterie, sans interface. Antenne éteinte : plus de rond.
## - Tenir la brume à distance coûte : la batterie descend dans la brume légère, plus vite dans la brume
##   épaisse (suffixe « b » de la carte, ex. la crique), où elle presse plus fort.
## - Dans la lumière d'une lanterne allumée, rien à repousser : la batterie remonte doucement.
## - À l'abri (cases « h ») et dans l'atelier (« X ») : rien ne bouge.
## Rien pendant une cinématique, ni à bord de la barque (elle gère sa propre consommation).
## - La lanterne de proue de la barque repousse aussi la brume (barque.gd : bulle_lanterne, uniforme « barque »).

@export var maquette: Node3D
## Batterie perdue par seconde dans la brume légère (0,006 ≈ 2 min 45 pour une batterie pleine).
@export var vidage_leger: float = 0.006
## Batterie perdue par seconde dans la brume épaisse (0,05 ≈ 20 s).
@export var vidage_epais: float = 0.05
## Batterie regagnée par seconde dans la lumière d'une lanterne allumée.
@export var recharge_lumiere: float = 0.03
@export_group("Le rond de lumière")
## Rayon (m) du rond sans brume, batterie pleine et presque vide.
@export var rayon_plein: float = 5.5
@export var rayon_vide: float = 2.0
## Dans la brume épaisse, la brume presse : le rond est plus petit.
@export var reduction_epaisse: float = 0.6

var _joueur: CharacterBody3D
var _rayon := 0.0
var _materiaux: Array[ShaderMaterial] = []


func _ready() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	for v in get_tree().get_nodes_in_group("brume_ile"):
		var m: Material = (v as FogVolume).material if v is FogVolume else (v as GeometryInstance3D).material_override
		if m is ShaderMaterial:
			_materiaux.append(m)


func _physics_process(delta: float) -> void:
	if _joueur == null or maquette == null:
		return
	var p := _joueur.global_position
	var k: Dictionary = maquette.call("_case_a", p)
	var suf: String = str(k.get("suf", ""))
	var epaisse := "b" in suf
	var b: float = _joueur.get("batterie")
	# le rond de lumière : il suit la batterie, se resserre dans la brume épaisse, disparaît antenne éteinte
	var cible := lerpf(rayon_vide, rayon_plein, clampf(b, 0.0, 1.0)) * (reduction_epaisse if epaisse else 1.0)
	if not bool(_joueur.get("antenne_allumee")):
		cible = 0.0
	_rayon = move_toward(_rayon, cible, delta * 2.0)
	for m in _materiaux:
		m.set_shader_parameter("robot", Vector4(p.x, p.y, p.z, _rayon))
	var la_barque := get_tree().get_first_node_in_group("barque_qui_flotte")
	var bulle: Vector4 = la_barque.call("bulle_lanterne") if la_barque and la_barque.has_method("bulle_lanterne") else Vector4.ZERO
	for m in _materiaux:
		m.set_shader_parameter("barque", bulle)
	# ce que ça coûte
	if bool(_joueur.get("cinematique")):
		return
	for barque in get_tree().get_nodes_in_group("barque_qui_flotte"):
		if bool(barque.get("pilotee")):
			return
	if "h" in suf or "X" in suf:
		return
	if _dans_la_lumiere():   # la lumière d'une lanterne allumée repousse même la brume épaisse
		b += recharge_lumiere * delta
	elif epaisse:
		b -= vidage_epais * delta
	else:
		b -= vidage_leger * delta
	_joueur.set("batterie", clampf(b, 0.0, 1.0))


func _dans_la_lumiere() -> bool:
	var p := _joueur.global_position
	for l in get_tree().get_nodes_in_group("lanternes"):
		if not bool(l.get("allumee")):
			continue
		var c: Vector3 = (l as Node3D).global_position
		if Vector2(p.x - c.x, p.z - c.z).length() < float(l.get("rayon_zone")):
			return true
	return false
