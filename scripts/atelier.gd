extends Node3D
## L'atelier des robots (assets/models/atelier_salle.glb, préparé par tools/blender/atelier_salle.py) :
## une salle creusée dans la falaise derrière la cascade. De dehors, un bloc de roche moussu ; quand le
## robot passe la porte, le haut des murs et le couvercle s'effacent (comme le toit de l'abri).
## Le modèle : 6 m de côté, sol à y = 0, porte au sud (+Z), murs épais à l'ouest et au sud (Meshy),
## murs ajoutés au nord et à l'est.

@export var duree_fondu: float = 0.6
@export var hauteur_murs: float = 3.9
@export var ep_meshy: float = 1.2     # murs ouest et sud
@export var ep_ajout: float = 0.6     # murs nord et est

const D := 3.0
const PAGE_SCRIPT := preload("res://scripts/page_lisible.gd")
## La page 7 d'Iris, posée sur l'établi (ILE_01_REVEIL.md §7).
const PAGE_7 := "Elles ne sont pas la brume. Elles sont dans la brume. Chaque fois que je souffle ma lanterne, elles s'allument tout autour de moi, comme si elles m'attendaient.

Les autres disent que le pollen m'a pris la tête.

Le petit jardinier qu'ils moulent dans cet atelier ne les voit pas : son antenne les éblouit, elle aussi.

Si tu lis ceci, suis-les. Elles connaissent le chemin de chez moi."
## Où est la feuille sur l'établi (repère de l'établi : plateau à ~1,37 m, bord avant vers +Z).
const PAGE_SUR_ETABLI := Vector3(0.0, 1.39, 0.2)
## Le mobilier de l'atelier (chaque objet préparé par tools/blender/accessoire.py) :
## [modèle, position dans la salle, rotation (°), taille de la boîte de collision]. Avant du modèle = +Z.
const MOBILIER := [
	# l'empreinte du robot regarde la porte et la caméra (sud), un peu tournée vers le centre de la salle
	["res://assets/models/moule.glb", Vector3(1.3, 0, -0.5), -35.0, Vector3(1.6, 2.0, 1.6)],
	["res://assets/models/etabli.glb", Vector3(-0.3, 0, -1.8), 0.0, Vector3(1.9, 2.0, 1.0)],
	# contre le mur ouest, tournée vers le centre ; les écharpes de rechange sont sur le rayon du bas
	["res://assets/models/etagere.glb", Vector3(-1.3, 0, 0.4), 90.0, Vector3(2.1, 2.0, 0.9)],
]

var _toit: Node3D
var _fondu: Tween
var _dedans: int = 0


func _ready() -> void:
	add_to_group("atelier")
	_toit = find_child("Toit", true, false) as Node3D
	if Engine.is_editor_hint() or _toit == null:
		return
	var entree := find_child("Entree", true, false) as Node3D
	var cx: float = entree.position.x if entree else 0.25
	_collisions(cx)
	_zone()
	_meubler()
	_poser_page()
	var lampe := OmniLight3D.new()   # une lueur chaude et sombre, en attendant la lanterne de l'atelier
	lampe.light_color = Color(1.0, 0.8, 0.55)
	lampe.light_energy = 0.7
	lampe.omni_range = 6.0
	lampe.position = Vector3(0, 2.6, 0)
	add_child(lampe)


## Pose le mobilier (les objets pas encore générés sont simplement absents).
func _meubler() -> void:
	for m in MOBILIER:
		var chemin: String = m[0]
		if not ResourceLoader.exists(chemin):
			continue
		var o: Node3D = (load(chemin) as PackedScene).instantiate()
		o.position = m[1]
		o.rotation.y = deg_to_rad(m[2])
		add_child(o)
		var corps := StaticBody3D.new()
		var boite := BoxShape3D.new()
		boite.size = m[3]
		var cs := CollisionShape3D.new()
		cs.shape = boite
		cs.position = Vector3.UP * (boite.size.y * 0.5)
		corps.add_child(cs)
		o.add_child(corps)


## La page 7 se lit sur l'établi (si l'établi est là).
func _poser_page() -> void:
	var etabli: Node3D = null
	for c in get_children():
		if c.scene_file_path.ends_with("etabli.glb"):
			etabli = c
	if etabli == null:
		return
	var page := Node3D.new()
	page.name = "Page7"
	page.set_script(PAGE_SCRIPT)
	page.set("texte", PAGE_7)
	page.set("signature", "— G.")
	var tex := load("res://assets/affiches/page_7.png") as Texture2D
	if tex:   # la page dessinée (tools/affiches/page_7.html, rendue par rendre.py)
		page.set("image", tex)
		page.set("taille_feuille", Vector2(0.24, 0.24 * float(tex.get_height()) / float(tex.get_width())))
	page.position = PAGE_SUR_ETABLI
	etabli.add_child(page)


func _collisions(cx: float) -> void:
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	add_child(corps)
	var h := hauteur_murs
	_boite(corps, Vector3(-D, 0, -D), Vector3(-D + ep_meshy, h, D))          # ouest
	_boite(corps, Vector3(-D, 0, -D), Vector3(D, h, -D + ep_ajout))          # nord
	_boite(corps, Vector3(D - ep_ajout, 0, -D), Vector3(D, h, D))            # est
	_boite(corps, Vector3(-D, 0, D - ep_meshy), Vector3(cx - 0.75, h, D))    # sud, à gauche de la porte
	_boite(corps, Vector3(cx + 0.75, 0, D - ep_meshy), Vector3(D, h, D))     # sud, à droite de la porte
	_boite(corps, Vector3(cx - 0.75, 2.6, D - ep_meshy), Vector3(cx + 0.75, h, D))   # au-dessus de la porte


func _boite(corps: StaticBody3D, mn: Vector3, mx: Vector3) -> void:
	var b := BoxShape3D.new()
	b.size = mx - mn
	var cs := CollisionShape3D.new()
	cs.shape = b
	cs.position = (mn + mx) * 0.5
	corps.add_child(cs)


func _zone() -> void:
	var zone := Area3D.new()
	zone.name = "Interieur"
	var b := BoxShape3D.new()
	b.size = Vector3(2 * D - ep_meshy - ep_ajout - 0.2, 3.0, 2 * D - ep_meshy - ep_ajout - 0.2)
	var cs := CollisionShape3D.new()
	cs.shape = b
	cs.position = Vector3((ep_meshy - ep_ajout) * 0.5, 1.5, (ep_ajout - ep_meshy) * 0.5)
	zone.add_child(cs)
	add_child(zone)
	zone.body_entered.connect(func(c: Node3D) -> void:
		if c is CharacterBody3D:
			_dedans += 1
			_montrer_toit(false))
	zone.body_exited.connect(func(c: Node3D) -> void:
		if c is CharacterBody3D:
			_dedans = maxi(0, _dedans - 1)
			if _dedans == 0:
				_montrer_toit(true))


func _montrer_toit(visible_: bool) -> void:
	if _fondu:
		_fondu.kill()
	var pieces: Array[GeometryInstance3D] = []
	if _toit is GeometryInstance3D:
		pieces.append(_toit as GeometryInstance3D)
	for n in _toit.find_children("*", "GeometryInstance3D", true, false):
		pieces.append(n as GeometryInstance3D)
	if visible_:
		_toit.visible = true
	_fondu = create_tween().set_parallel()
	for g in pieces:
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if visible_ else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_fondu.tween_property(g, "transparency", 0.0 if visible_ else 1.0, duree_fondu)
	if not visible_:
		_fondu.chain().tween_callback(func() -> void: _toit.visible = false)
