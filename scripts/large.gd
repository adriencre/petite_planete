@tool
extends Node3D
## Le large autour d'une île (scenes/large.tscn), posé au centre de l'île. Au-delà de `rayon_depart`,
## la barque (barque.gd) entre dans la brume du large :
## - proue tournée vers la silhouette d'une autre île (à `ouverture` degrés près) : la brume s'épaissit
##   sur `epaisseur` mètres jusqu'à tout couvrir, puis c'est la traversée (Sauvegarde.traverser) ;
## - sinon, ou sur le Réveil tant que l'île n'est pas finie : un courant ramène doucement la barque.
## Enfants :
##   Silhouettes : les autres îles au loin, nommées comme dans archipel.gd (« phare », « colonie »…).
##                 Elles se placent seules dans leur direction, rapprochées à `distance_silhouettes`
##                 (et rapetissées d'autant, pour garder leur taille apparente dans la brume).
##   Arrivee     : où la barque sort de la brume quand on arrive sur cette île (proue vers +Z).
##   Brume/Voile : le blanc de la brume du large, par-dessus l'image.

const ARCHIPEL := preload("res://scripts/archipel.gd")

@export_enum("reveil", "phare", "colonie") var ile: String = "reveil":
	set(v):
		ile = v
		_placer_silhouettes()
## Distance (m) au centre où commence la brume du large.
@export var rayon_depart: float = 60.0
## Mètres de brume à traverser avant de partir (≈ 6 s à pleine vitesse).
@export var epaisseur: float = 25.0
## Écart (degrés) toléré entre la proue et la silhouette visée.
@export_range(5.0, 60.0) var ouverture: float = 25.0
## Distance (m) où l'on pose les silhouettes (au-delà, la brume les mangerait).
@export var distance_silhouettes: float = 130.0:
	set(v):
		distance_silhouettes = v
		_placer_silhouettes()
## Le courant qui ramène vers l'île quand on ne vise rien.
@export var force_courant: float = 1.2
## Sur le Réveil : on ne part qu'une fois l'île finie (la grande lanterne du sommet, fin_sommet.gd).
@export var apres_fin_ile_1: bool = false
## En arrivant : durée (s) pendant laquelle la brume se lève autour de la barque.
@export var duree_sortie_brume: float = 4.5

var _epais: float = 0.0
var _parti: bool = false
@onready var _voile: ColorRect = get_node_or_null("Brume/Voile") as ColorRect


func _ready() -> void:
	_placer_silhouettes()
	if Engine.is_editor_hint():
		return
	add_to_group("large")
	if _voile == null:
		return
	if arrivee_par_la_mer():
		# on sort de la brume : elle se lève lentement autour de la barque
		_epais = 1.0
		_voile.modulate.a = 1.0
		var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		t.tween_interval(0.8)
		t.tween_property(self, "_epais", 0.0, duree_sortie_brume)
	else:
		_voile.modulate.a = 0.0


func _process(_delta: float) -> void:
	if _voile and not Engine.is_editor_hint():
		_voile.modulate.a = _epais * _epais * (3.0 - 2.0 * _epais)


## Vrai si la scène vient d'être chargée par une traversée (la barque arrive en mer).
func arrivee_par_la_mer() -> bool:
	var s := get_node_or_null("/root/Sauvegarde")
	return s != null and String(s.get("arrivee_de")) != ""


## Où la barque arrive en mer (proue vers +Z).
func arrivee() -> Transform3D:
	var m := get_node_or_null("Arrivee") as Node3D
	return m.global_transform if m else global_transform


## Appelé par la barque à chaque image de navigation : renvoie le courant (accélération, m/s²) et
## épaissit la brume ; quand elle couvre tout, la traversée part.
func au_large(pos: Vector3, avant: Vector3, delta: float) -> Vector3:
	if _parti:
		return Vector3.ZERO
	var vers := Vector3(pos.x - global_position.x, 0.0, pos.z - global_position.z)
	var trop := vers.length() - rayon_depart
	var dest := destination(pos, avant) if trop > 0.0 else ""
	var voulu := clampf(trop / maxf(epaisseur, 1.0), 0.0, 1.0) if dest != "" else 0.0
	# la brume suit la distance, mais retombe doucement si on fait demi-tour
	_epais = voulu if voulu > _epais else move_toward(_epais, voulu, delta * 0.5)
	if dest != "" and voulu >= 1.0:
		_partir(dest)
		return Vector3.ZERO
	if dest == "" and trop > 0.0:
		return -vers.normalized() * trop * force_courant
	return Vector3.ZERO


## L'île dont la silhouette est devant la proue ("" si aucune, ou si on ne peut pas encore partir).
func destination(pos: Vector3, avant: Vector3) -> String:
	if apres_fin_ile_1 and not _ile_1_finie():
		return ""
	var silhouettes := get_node_or_null("Silhouettes")
	if silhouettes == null:
		return ""
	var cap := Vector3(avant.x, 0.0, avant.z).normalized()
	var meilleure := ""
	var ecart_min := ouverture
	for c in silhouettes.get_children():
		var nom := String(c.name)
		if nom == ile or not ARCHIPEL.ILES.has(nom) or not (c is Node3D):
			continue
		var d := Vector3((c as Node3D).global_position.x - pos.x, 0.0, (c as Node3D).global_position.z - pos.z).normalized()
		var ecart := rad_to_deg(acos(clampf(cap.dot(d), -1.0, 1.0)))
		if ecart < ecart_min:
			ecart_min = ecart
			meilleure = nom
	return meilleure


func _ile_1_finie() -> bool:
	for n in get_tree().get_nodes_in_group("sauvegarde"):
		if n.has_method("cle_sauvegarde") and str(n.call("cle_sauvegarde")) == "fin_ile_1":
			return bool((n.call("sauver") as Dictionary).get("fait", false))
	return false


func _partir(dest: String) -> void:
	_parti = true
	var joueur := get_tree().get_first_node_in_group("joueur")
	var batterie: float = float(joueur.get("batterie")) if joueur else -1.0
	var sauvegarde := get_node_or_null("/root/Sauvegarde")
	if sauvegarde:
		sauvegarde.call("traverser", ile, dest, batterie)


## Chaque silhouette dans la direction de son île, à `distance_silhouettes` au plus. Pas de rotation :
## une silhouette est une maquette de l'île dans ses propres coordonnées (même orientation que sa scène).
func _placer_silhouettes() -> void:
	if not is_inside_tree() or not ARCHIPEL.ILES.has(ile):
		return
	var silhouettes := get_node_or_null("Silhouettes")
	if silhouettes == null:
		return
	var ici: Vector3 = ARCHIPEL.ILES[ile]["position"]
	for c in silhouettes.get_children():
		var nom := String(c.name)
		if not (c is Node3D) or nom == ile or not ARCHIPEL.ILES.has(nom):
			continue
		var v: Vector3 = ARCHIPEL.ILES[nom]["position"] - ici
		var d := v.length()
		if d < 1.0:
			continue
		var k := minf(1.0, distance_silhouettes / d)
		var n3 := c as Node3D
		# l'origine de la scène d'île est sa position sur la carte
		n3.global_transform = Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * k), v * k)
