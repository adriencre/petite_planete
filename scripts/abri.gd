@tool
extends Node3D
## L'abri (assets/models/abri.glb, découpé par tools/blender/abri.py) : collisions, marches devant
## la porte, et toit qui s'efface quand le robot est dedans (vue de dessus).
## Le modèle a sa porte vers +Z ; ses repères `Centre` et `Porte` sont posés sur le sol intérieur.

@export var duree_fondu: float = 0.6
@export var rayon_murs: float = 2.95
@export var hauteur_murs: float = 2.6
@export var largeur_porte: float = 1.7
@export var couleur_marches: Color = Color(0.93, 0.87, 0.8)
## Le berceau, au fond face à la porte : distance au centre (m) et angle (°).
@export var recul_berceau: float = 1.35
@export var angle_berceau: float = 0.0

const BERCEAU := preload("res://assets/models/berceau.glb")  # nettoyé par tools/blender/berceau.py

var _toit: Node3D
var _fondu: Tween
var _dedans: int = 0


var decor_seul := false


func _ready() -> void:
	if not decor_seul:
		add_to_group("abri")
	_toit = find_child("Toit", true, false) as Node3D
	var n_centre := find_child("Centre", true, false) as Node3D
	var n_porte := find_child("Porte", true, false) as Node3D
	if _toit == null or n_centre == null or n_porte == null:
		push_warning("abri.gd : nœuds Toit / Centre / Porte introuvables dans le modèle")
		return
	var centre: Vector3 = global_transform.affine_inverse() * n_centre.global_position
	var porte: Vector3 = global_transform.affine_inverse() * n_porte.global_position
	var sol: float = centre.y              # hauteur du sol intérieur au-dessus du terrain
	var z_porte: float = porte.z - centre.z  # distance du centre à la porte
	var ancien := get_node_or_null("Jeu")
	if ancien:
		ancien.free()
	var jeu := Node3D.new()
	jeu.name = "Jeu"
	jeu.position = Vector3(centre.x, 0, centre.z)
	add_child(jeu)
	_marches(jeu, sol, z_porte)
	var berceau := _berceau(jeu, sol)
	_mobilier(jeu, sol)
	_ordre_ysolde(jeu, sol)
	_notice(jeu, sol)
	var lampe := OmniLight3D.new()   # la veilleuse au-dessus de la porte
	lampe.light_color = Color(1.0, 0.78, 0.45)
	lampe.light_energy = 0.8
	lampe.omni_range = 4.0
	lampe.position = Vector3(0, sol + 2.7, z_porte + 0.3)
	jeu.add_child(lampe)
	if Engine.is_editor_hint() or decor_seul:
		return
	_collisions(jeu, sol, z_porte)
	_collision_berceau(berceau)
	_zone(jeu, sol)


## Trois marches de pierre devant la porte (le sol intérieur est plus haut que le terrain).
func _marches(jeu: Node3D, sol: float, z_porte: float) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = couleur_marches
	mat.roughness = 1.0
	for i in 3:
		var haut: float = sol * (i + 1) / 3.0
		var z1: float = z_porte + 1.65 - i * 0.5
		var m := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = Vector3(largeur_porte, haut, z1 - z_porte + 0.4)
		b.material = mat
		m.mesh = b
		m.position = Vector3(0, haut * 0.5, (z_porte - 0.4 + z1) * 0.5)
		jeu.add_child(m)


## Le berceau où le robot se réveille : encoche de sortie tournée vers la porte, lampe dorée à la tête.
func _berceau(jeu: Node3D, sol: float) -> Node3D:
	var b: Node3D = BERCEAU.instantiate()
	b.name = "Berceau"
	b.position = Vector3(0, sol, -recul_berceau)
	b.rotation.y = deg_to_rad(angle_berceau)
	jeu.add_child(b)
	var lampe := b.find_child("Lampe", true, false) as Node3D
	if lampe:
		var o := OmniLight3D.new()
		o.name = "LueurBerceau"
		o.light_color = Color(1.0, 0.8, 0.45)
		o.light_energy = 1.2
		o.omni_range = 3.5
		lampe.add_child(o)
	return b


## L'ordre des Semeurs (ILE_01_REVEIL.md §7) : un papier posé sur la table de chevet, à côté du berceau.
## Pas une énigme : on le voit et on le lit (E) dès le réveil.
const ORDRE_YSOLDE := "Garder la lumière jusqu'à notre retour."
## La table de chevet (repère de l'abri : porte vers +Z, berceau au fond le long de X).
@export var position_chevet: Vector3 = Vector3(1.6, 0.0, -0.95)
const HAUT_CHEVET := 0.55


func _ordre_ysolde(jeu: Node3D, sol: float) -> void:
	_papier(jeu, "OrdreYsolde", position_chevet + Vector3(-0.04, sol + HAUT_CHEVET + 0.004, 0.06), -12.0,
		ORDRE_YSOLDE, "— Ysolde, Commandante", "res://assets/affiches/ordre_ysolde.png", 0.32)


## Le mode d'emploi du jardinier, laissé par celui qui l'a fabriqué (décidé le 2026-11-17 : au réveil,
## on ne savait pas quoi faire). Posé sur le tapis, entre le berceau et la porte : on ne peut pas le
## rater. Il dit ce qu'il faut faire sur l'île 1, sans rien révéler de l'enquête.
const NOTICE := "[center][b]Mode d'emploi du petit jardinier[/b][/center]

[b]1.[/b] Ton antenne vit de lumière. Quand elle faiblit, va à la [b]pierre-soleil[/b], devant la porte, et tends-lui ton antenne.

[b]2.[/b] La [b]brume[/b] boit ta lumière. Ne t'y attarde pas : plus elle est épaisse, plus elle boit vite.

[b]3.[/b] Les [b]lanternes[/b] de l'île se sont endormies. Branche le câble de ton poignet dans leur prise : elles se rallument et réveillent tout autour d'elles. Chacune te coûte un peu de lumière, mais dans leur clarté, ton antenne se recharge.

[b]4.[/b] Les trois petites lanternes nourrissent la [b]grande, au sommet[/b]. Rallume les trois, puis monte rallumer la grande.

[b]5.[/b] Prends ton [b]carnet[/b], sur l'étagère. Il garde ce que tu vois.

[b]6.[/b] Si ta lumière s'éteint tout à fait, n'aie pas peur : ton berceau te réveillera.

[b]7.[/b] Quand l'île brillera, la [b]barque[/b] t'attendra au ponton de la crique, à l'ouest. Va voir la [b]Gardienne du Phare[/b] : c'est elle qui veille sur nous."
@export var position_notice: Vector3 = Vector3(-0.3, 0.0, 0.05)


func _notice(jeu: Node3D, sol: float) -> void:
	_papier(jeu, "ModeEmploi", position_notice + Vector3(0, sol + 0.035, 0), 18.0,
		NOTICE, "— Tavin, l'Ingénieur", "res://assets/affiches/mode_emploi.png", 0.34)


## Une feuille qu'on lit avec E (page_lisible.gd ; elle scintille grâce à guidage.gd) : le document
## dessiné (tools/affiches/, rendu en assets/affiches/*.png), posé là, `largeur` m de large.
## Le texte reste la version écrite (secours si l'image manque).
func _papier(jeu: Node3D, nom: String, pos: Vector3, angle: float, texte: String, signature: String, image: String, largeur: float) -> void:
	var page := Node3D.new()
	page.name = nom
	page.position = pos
	page.rotation.y = deg_to_rad(angle)
	var tex: Texture2D = load(image) as Texture2D if ResourceLoader.exists(image) else null
	var taille := Vector2(largeur, largeur * 0.72)
	if tex:
		taille.y = largeur * float(tex.get_height()) / float(tex.get_width())
	if not Engine.is_editor_hint():   # le script avant add_child, pour que son _ready tourne
		page.set_script(preload("res://scripts/page_lisible.gd"))
		page.set("texte", texte)
		page.set("signature", signature)
		page.set("taille_feuille", taille)
		page.set("image", tex)
	elif tex:   # dans l'éditeur : la feuille dessinée, pour la voir en place
		var feuille := MeshInstance3D.new()
		var q := PlaneMesh.new()
		q.size = taille
		var m := StandardMaterial3D.new()
		m.albedo_texture = tex
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
		q.material = m
		feuille.mesh = q
		page.add_child(feuille)
	jeu.add_child(page)


## Le mobilier de l'abri (ILE_01_REVEIL.md §3 : l'abri est habité, à la taille du robot) : un tapis,
## la table de chevet (le carnet, l'ordre d'Ysolde), une étagère avec des pots, l'horloge arrêtée au mur,
## deux plantes en pot, un sac de graines. Formes simples à facettes (DA v6).
## Repère de l'abri : porte vers +Z ; un angle `a` autour du centre donne (sin a, cos a) * rayon.
func _mobilier(jeu: Node3D, sol: float) -> void:
	var m := Node3D.new()
	m.name = "Mobilier"
	jeu.add_child(m)
	var bois := _mat(Color(0.82, 0.66, 0.48))
	var bois_clair := _mat(Color(0.9, 0.78, 0.62))
	var creme := _mat(Color(0.95, 0.9, 0.82))
	var sauge := _mat(Color(0.6, 0.71, 0.57))
	var rose := _mat(Color(0.9, 0.73, 0.75))
	var lavande := _mat(Color(0.74, 0.7, 0.86))
	var terre := _mat(Color(0.86, 0.6, 0.5))
	var feuille := _mat(Color(0.47, 0.66, 0.42))
	# le temps a passé (ILE_01_REVEIL.md §13, 2026-11-18) : couleurs pâlies, fentes sombres
	var rose_passe := _mat(Color(0.88, 0.8, 0.78))
	var lavande_passee := _mat(Color(0.8, 0.78, 0.84))
	var sauge_passee := _mat(Color(0.72, 0.76, 0.68))
	var sombre := _mat(Color(0.34, 0.26, 0.21))
	var liane := _mat(Color(0.42, 0.56, 0.36))
	var alea := RandomNumberGenerator.new()
	alea.seed = 7   # toujours la même liane, les mêmes pousses
	var collisions: Array = []   # [taille, position, angle]

	# le tapis rond, devant le berceau
	_cyl(m, rose_passe, 1.15, 1.15, 0.02, Vector3(0, sol + 0.01, 0.35), 8)
	_cyl(m, lavande_passee, 0.8, 0.8, 0.025, Vector3(0, sol + 0.012, 0.35), 8)
	# le passage du robot, du berceau à la porte : là, la poussière n'a jamais tenu
	_boite(m, lavande, Vector3(0.42, 0.004, 1.5), Vector3(0, sol + 0.026, 0.35))

	# la table de chevet : plateau, pied central, le carnet posé dessus
	var c := position_chevet + Vector3.UP * sol
	_boite(m, bois, Vector3(0.5, 0.05, 0.5), c + Vector3.UP * (HAUT_CHEVET - 0.025))
	_boite(m, bois_clair, Vector3(0.14, HAUT_CHEVET - 0.05, 0.14), c + Vector3.UP * (HAUT_CHEVET - 0.05) * 0.5)
	_boite(m, bois_clair, Vector3(0.36, 0.04, 0.36), c + Vector3.UP * 0.02)
	collisions.append([Vector3(0.5, HAUT_CHEVET, 0.5), c + Vector3.UP * HAUT_CHEVET * 0.5, 0.0])

	# l'étagère contre le mur, au fond à gauche : trois planches, des pots et un bocal
	var a_et := PI + 0.95
	var p_et := Vector3(sin(a_et), 0, cos(a_et)) * (rayon_murs - 0.4) + Vector3.UP * sol
	var et := Node3D.new()
	et.position = p_et
	et.rotation.y = a_et
	m.add_child(et)
	for i in 3:
		_boite(et, bois, Vector3(1.1, 0.04, 0.32), Vector3(0, 0.45 + i * 0.5, 0))
	for x in [-0.53, 0.53]:
		_boite(et, bois_clair, Vector3(0.05, 1.5, 0.32), Vector3(x, 0.75, 0))
	_cyl(et, terre, 0.09, 0.07, 0.16, Vector3(-0.3, 0.55, 0), 6)
	_cone(et, feuille, 0.12, 0.22, Vector3(-0.3, 0.74, 0))
	_cyl(et, terre, 0.08, 0.06, 0.14, Vector3(0.05, 1.04, 0), 6)
	_cone(et, feuille, 0.1, 0.18, Vector3(0.05, 1.2, 0))
	_cyl(et, creme, 0.07, 0.07, 0.2, Vector3(0.32, 1.07, 0), 6)            # un bocal de graines
	_boite(et, lavande, Vector3(0.22, 0.08, 0.2), Vector3(0.28, 0.51, 0))  # une boîte
	# le carnet du robot, couverture vert sauge, posé à plat sur l'étagère du bas (carnet.gd : E pour le prendre)
	var carnet := _boite(et, sauge, Vector3(0.2, 0.035, 0.26), Vector3(0.0, 0.488, 0.0), deg_to_rad(8))
	carnet.name = "CarnetObjet"
	carnet.add_to_group("carnet_objet")
	_boite(carnet, creme, Vector3(0.17, 0.02, 0.24), Vector3(0.012, 0.0, 0.0))   # la tranche des pages
	_boite(et, sauge_passee, Vector3(0.08, 0.26, 0.2), Vector3(-0.2, 1.6, 0), 0.0)   # des livres, pâlis
	_boite(et, rose_passe, Vector3(0.24, 0.07, 0.19), Vector3(0.0, 1.505, 0.0), 0.35)   # l'un est tombé à plat
	_toile(et, Vector3(-0.32, 1.22, -0.05), 0.0, 0.42)   # une toile dans le coin, sous la planche du haut
	collisions.append([Vector3(1.15, 1.5, 0.34), p_et + Vector3.UP * 0.75, a_et])

	# l'horloge arrêtée, au mur au fond à droite
	var a_h := PI - 0.7
	var p_h := Vector3(sin(a_h), 0, cos(a_h)) * (rayon_murs - 0.5) + Vector3.UP * (sol + 1.6)
	var h := Node3D.new()
	h.position = p_h
	h.rotation.y = a_h
	m.add_child(h)
	var cadran := _cyl(h, creme, 0.24, 0.24, 0.05, Vector3.ZERO, 10)
	cadran.rotation.x = PI * 0.5
	var bord := _cyl(h, bois, 0.28, 0.28, 0.04, Vector3(0, 0, 0.02), 10)
	bord.rotation.x = PI * 0.5
	_boite(h, bois, Vector3(0.025, 0.16, 0.01), Vector3(0, 0.06, -0.03))            # les aiguilles, figées
	_boite(h, bois, Vector3(0.11, 0.022, 0.01), Vector3(0.05, 0, -0.03), 0.0)
	for fente in [[Vector3(-0.09, 0.07, -0.028), 0.18, 0.7], [Vector3(-0.14, -0.02, -0.028), 0.12, -0.5]]:   # une fêlure
		var fl := _boite(h, sombre, Vector3(fente[1], 0.006, 0.004), fente[0])
		fl.rotation.z = fente[2]
	_toile(m, p_h + Vector3(0.25, 0.55, 0.0).rotated(Vector3.UP, a_h), a_h, 0.5)   # une toile au-dessus

	# deux plantes en pot, de part et d'autre : livrées à elles-mêmes, elles ont tout envahi
	for i in 2:
		var a: float = [1.85, -1.75][i]
		var p := Vector3(sin(a), 0, cos(a)) * (rayon_murs - 0.55) + Vector3.UP * sol
		var pot := _cyl(m, terre, 0.2, 0.15, 0.32, p + Vector3.UP * 0.16, 6)
		_cone(m, feuille, 0.42, 0.85, p + Vector3.UP * 0.72)
		_cone(m, feuille, 0.3, 0.65, p + Vector3(0.12, 1.1, 0.06))
		_cone(m, feuille, 0.26, 0.55, p + Vector3(-0.14, 0.95, -0.08))
		for k in 6:   # des feuilles qui retombent par-dessus le bord du pot
			var pivot := Node3D.new()
			pivot.position = p + Vector3.UP * 0.36
			pivot.rotation.y = TAU * k / 6.0 + 0.3 * i
			m.add_child(pivot)
			var f := _boite(pivot, feuille, Vector3(0.12, 0.015, 0.42), Vector3(0, -0.06, 0.24))
			f.rotation.x = 0.55 + 0.15 * (k % 2)
		if i == 1:
			# ce pot-là s'est fendu : ses racines sont sorties et sont entrées dans le plancher
			pot.rotation.z = 0.1
			var vers_centre := Vector3(-p.x, 0, -p.z).normalized()
			var lat := vers_centre.cross(Vector3.UP)
			_boite(m, sombre, Vector3(0.02, 0.24, 0.02), p + Vector3.UP * 0.17 + vers_centre * 0.19)
			_boite(m, sombre, Vector3(0.04, 0.008, 0.8), p + Vector3.UP * 0.003 + vers_centre * 0.55, atan2(vers_centre.x, vers_centre.z))
			for r in 3:
				var depart := p + Vector3.UP * 0.06 + vers_centre * 0.16 + lat * (r - 1) * 0.07
				var arrivee := p + Vector3.UP * 0.01 + vers_centre * (0.45 + 0.12 * r) + lat * (r - 1) * 0.04
				_tige(m, bois, depart, arrivee, 0.018)
			_liane(m, liane, feuille, p, alea, sol)
		collisions.append([Vector3(0.5, 0.6, 0.5), p + Vector3.UP * 0.3, 0.0])

	# le sac de graines, à côté de la table de chevet : renversé depuis longtemps ; des graines tombées
	# au sol ont levé toutes seules (décor : il n'y a rien à planter, ILE_01_REVEIL.md)
	var p_sac := position_chevet + Vector3(0.25, sol, -0.75)
	var sac := _cyl(m, creme, 0.19, 0.24, 0.38, p_sac + Vector3(-0.12, 0.2, 0.0), 6)
	sac.rotation.z = 1.35
	var col_sac := _cyl(m, bois_clair, 0.1, 0.16, 0.08, p_sac + Vector3(-0.36, 0.17, 0.0), 6)
	col_sac.rotation.z = 1.35
	for k in 9:
		var g := p_sac + Vector3(-0.5 - alea.randf() * 0.45, 0.012, alea.randf_range(-0.3, 0.3))
		if k < 5:
			var haut := alea.randf_range(0.08, 0.16)
			_cone(m, feuille, 0.035, haut, g + Vector3.UP * haut * 0.5)
		else:
			_boite(m, bois, Vector3(0.03, 0.02, 0.025), g, alea.randf() * TAU)

	# la poussière : des grains qui flottent lentement dans la lumière qui entre par la porte
	var poussiere := CPUParticles3D.new()
	poussiere.name = "Poussiere"
	poussiere.position = Vector3(0, sol + 1.3, 0.6)
	poussiere.amount = 70
	poussiere.lifetime = 14.0
	poussiere.preprocess = 14.0
	poussiere.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	poussiere.emission_box_extents = Vector3(1.8, 1.0, 1.6)
	poussiere.direction = Vector3.UP
	poussiere.spread = 180.0
	poussiere.gravity = Vector3(0, -0.004, 0)
	poussiere.initial_velocity_min = 0.005
	poussiere.initial_velocity_max = 0.03
	var grain := QuadMesh.new()
	grain.size = Vector2(0.012, 0.012)
	var mg := StandardMaterial3D.new()
	mg.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mg.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mg.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mg.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mg.vertex_color_use_as_albedo = true
	grain.material = mg
	poussiere.mesh = grain
	var teinte := Gradient.new()
	teinte.offsets = PackedFloat32Array([0.0, 0.3, 0.7, 1.0])
	teinte.colors = PackedColorArray([Color(1, 0.92, 0.75, 0), Color(1, 0.92, 0.75, 0.5), Color(1, 0.92, 0.75, 0.5), Color(1, 0.92, 0.75, 0)])
	poussiere.color_ramp = teinte
	m.add_child(poussiere)

	if Engine.is_editor_hint():
		return
	var corps := StaticBody3D.new()
	corps.name = "CollisionMobilier"
	m.add_child(corps)
	for col in collisions:
		var b := BoxShape3D.new()
		b.size = col[0]
		_forme(corps, b, col[1], col[2])


## Une tige (cylindre fin) de `a` à `b`.
func _tige(parent: Node3D, mat: Material, a: Vector3, b: Vector3, rayon: float) -> MeshInstance3D:
	var d := b - a
	var mi := _cyl(parent, mat, rayon, rayon, maxf(d.length(), 0.001), (a + b) * 0.5, 5)
	var y := d.normalized()
	var ref := Vector3.FORWARD if absf(y.dot(Vector3.FORWARD)) < 0.9 else Vector3.RIGHT
	var x := ref.cross(y).normalized()
	mi.basis = Basis(x, y, x.cross(y))
	return mi


## La liane : elle sort du pot fendu, gagne le mur et y grimpe en zigzag jusque sous le toit.
func _liane(parent: Node3D, mat: Material, mat_feuille: Material, pot: Vector3, alea: RandomNumberGenerator, sol: float) -> void:
	var a_mur := atan2(pot.x, pot.z) + 0.22
	var mur := Vector3(sin(a_mur), 0, cos(a_mur)) * (rayon_murs - 0.14)
	var pts: Array[Vector3] = [pot + Vector3.UP * 0.5, mur + Vector3.UP * (sol + 0.75)]
	var lat := Vector3(cos(a_mur), 0, -sin(a_mur))   # le long du mur
	for k in 6:
		pts.append(mur + lat * (0.16 if k % 2 == 0 else -0.12) + Vector3.UP * (sol + 1.05 + k * 0.27))
	for k in pts.size() - 1:
		_tige(parent, mat, pts[k], pts[k + 1], maxf(0.022 - k * 0.002, 0.008))
		for j in 2:   # deux feuilles par segment
			var f := _boite(parent, mat_feuille, Vector3(0.11, 0.012, 0.07), pts[k].lerp(pts[k + 1], 0.3 + 0.4 * j), alea.randf() * TAU)
			f.rotation.x = alea.randf_range(-0.6, 0.6)


## Une toile d'araignée : un quad avec des fils dessinés (rayons et arcs), presque transparent.
static var _tex_toile: ImageTexture


func _toile(parent: Node3D, pos: Vector3, angle_y: float, taille: float) -> void:
	if _tex_toile == null:
		var n := 128
		var img := Image.create(n, n, false, Image.FORMAT_RGBA8)
		img.fill(Color(1, 1, 1, 0))
		for r in 7:   # les rayons, depuis le coin
			var dir := Vector2.from_angle(PI * 0.5 * r / 6.0)
			for t in range(0, n * 14 / 10):
				var p := dir * t
				if p.x < n and p.y < n:
					img.set_pixel(int(p.x), int(p.y), Color(1, 1, 1, 0.55))
		for k in range(1, 7):   # les arcs, d'un rayon à l'autre
			var rr := k * 18.0
			for t in 120:
				var p := Vector2.from_angle(PI * 0.5 * t / 119.0) * (rr + 4.0 * sin(t * 0.5))
				if p.x >= 0 and p.y >= 0 and p.x < n and p.y < n:
					img.set_pixel(int(p.x), int(p.y), Color(1, 1, 1, 0.4))
		_tex_toile = ImageTexture.create_from_image(img)
	var q := QuadMesh.new()
	q.size = Vector2(taille, taille)
	var mt := StandardMaterial3D.new()
	mt.albedo_texture = _tex_toile
	mt.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mt.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mt.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = mt
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.rotation.y = angle_y
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)


func _mat(couleur: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = couleur
	mat.roughness = 1.0
	return mat


func _boite(parent: Node3D, mat: Material, taille: Vector3, pos: Vector3, angle_y: float = 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = taille
	b.material = mat
	mi.mesh = b
	mi.position = pos
	mi.rotation.y = angle_y
	parent.add_child(mi)
	return mi


func _cyl(parent: Node3D, mat: Material, r_haut: float, r_bas: float, haut: float, pos: Vector3, cotes: int) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var c := CylinderMesh.new()
	c.top_radius = r_haut
	c.bottom_radius = r_bas
	c.height = haut
	c.radial_segments = cotes
	c.rings = 1
	c.material = mat
	mi.mesh = c
	mi.position = pos
	parent.add_child(mi)
	return mi


func _cone(parent: Node3D, mat: Material, rayon: float, haut: float, pos: Vector3) -> MeshInstance3D:
	return _cyl(parent, mat, 0.0, rayon, haut, pos, 5)


## Le robot peut monter dans le berceau : un bloc plein jusqu'au matelas.
func _collision_berceau(b: Node3D) -> void:
	var couche := b.find_child("Couche", true, false) as Node3D
	if couche == null:
		return
	var haut: float = couche.position.y
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	var boite := BoxShape3D.new()
	boite.size = Vector3(2.1, haut, 0.9)
	var cs := CollisionShape3D.new()
	cs.shape = boite
	cs.position = Vector3(couche.position.x, haut * 0.5, couche.position.z)
	corps.add_child(cs)
	b.add_child(corps)


func _collisions(jeu: Node3D, sol: float, z_porte: float) -> void:
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	jeu.add_child(corps)
	# le socle et le sol intérieur : un disque plein
	var disque := CylinderShape3D.new()
	disque.radius = rayon_murs + 0.25
	disque.height = sol
	_forme(corps, disque, Vector3(0, sol * 0.5, 0), 0.0)
	# la rampe (invisible) sous les marches
	var d: float = largeur_porte * 0.5
	var z0: float = disque.radius - 0.05
	var z1: float = z_porte + 1.7
	var rampe := ConvexPolygonShape3D.new()
	rampe.points = PackedVector3Array([
		Vector3(-d, 0, z1), Vector3(d, 0, z1), Vector3(-d, 0, z0 - 0.3), Vector3(d, 0, z0 - 0.3),
		Vector3(-d, sol, z0), Vector3(d, sol, z0), Vector3(-d, sol, z0 - 0.3), Vector3(d, sol, z0 - 0.3)])
	_forme(corps, rampe, Vector3.ZERO, 0.0)
	# les murs : un anneau de pans, ouvert devant la porte
	var nb: int = 36
	var ouverture: float = asin(clampf((largeur_porte * 0.5 - 0.05) / rayon_murs, 0.0, 1.0))
	for i in nb:
		var a: float = TAU * i / nb   # 0 = vers la porte (+Z)
		if absf(wrapf(a, -PI, PI)) < ouverture + PI / nb:
			continue
		var pan := BoxShape3D.new()
		pan.size = Vector3(TAU * rayon_murs / nb + 0.1, hauteur_murs, 0.3)
		_forme(corps, pan, Vector3(sin(a) * rayon_murs, sol + hauteur_murs * 0.5, cos(a) * rayon_murs), a)


func _forme(corps: StaticBody3D, forme: Shape3D, pos: Vector3, angle_y: float) -> void:
	var cs := CollisionShape3D.new()
	cs.shape = forme
	cs.position = pos
	cs.rotation.y = angle_y
	corps.add_child(cs)


## Zone de détection : le robot est dans l'abri -> le toit s'efface.
func _zone(jeu: Node3D, sol: float) -> void:
	var zone := Area3D.new()
	zone.name = "Interieur"
	var cyl := CylinderShape3D.new()
	cyl.radius = rayon_murs - 0.1
	cyl.height = 3.0
	var cs := CollisionShape3D.new()
	cs.shape = cyl
	cs.position = Vector3(0, sol + 1.5, 0)
	zone.add_child(cs)
	jeu.add_child(zone)
	zone.body_entered.connect(_entre)
	zone.body_exited.connect(_sort)


func _entre(corps: Node3D) -> void:
	if corps is CharacterBody3D:
		_dedans += 1


func _sort(corps: Node3D) -> void:
	if corps is CharacterBody3D:
		_dedans = maxi(0, _dedans - 1)


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
		# pendant le fondu le toit ne fait plus d'ombre : l'intérieur s'éclaire tout de suite
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if visible_ else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_fondu.tween_property(g, "transparency", 0.0 if visible_ else 1.0, duree_fondu)
	if not visible_:
		_fondu.chain().tween_callback(func() -> void: _toit.visible = false)

## La coupe (toit, haut des murs) n'est utile que si l'on voit le robot de l'extérieur : en 1re personne,
## le toit reste en place (décidé le 2026-11-22). Changer de caméra dedans (touche V) la met à jour.
var _coupe := false


func _process(_delta: float) -> void:
	var j := get_tree().get_first_node_in_group("joueur")
	var couper: bool = _dedans > 0 and (j == null or bool(j.call("troisieme_personne")))
	if couper != _coupe:
		_coupe = couper
		_montrer_toit(not couper)
