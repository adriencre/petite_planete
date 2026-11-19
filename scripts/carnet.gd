extends CanvasLayer
## Le carnet du robot (ILE_01_REVEIL.md §9) : juste ce qu'on a vu, sans flèches ni questions.
## - On le trouve dans l'abri, sur l'étagère (E) : il s'ouvre une première fois tout seul.
## - Tab : ouvrir / fermer. Q / D (A / D en QWERTY) : tourner les pages. Échap ou E : fermer.
## Les pages, dans l'ordre :
##   la CARTE (seulement les cases vues ; lieux découverts ; lanternes allumées en or ; le robot),
##   les LIEUX (un croquis pris au moment de la découverte, redessiné à l'encre),
##   les TEXTES lus (recopiés),
##   les DESSINS (le Phare vu du sommet…).
## Quand quelque chose s'ajoute : une petite icône de carnet et un bruit de page, sans texte.

const SONS := preload("res://scripts/sons.gd")
const CARTE := preload("res://scripts/carte_carnet.gd")
const CROQUIS := preload("res://shaders/croquis.gdshader")
const POLICE := preload("res://assets/fonts/Caveat.ttf")
const ENCRE := Color(0.33, 0.24, 0.17)
const PAPIER := Color(0.97, 0.93, 0.84)

@export var maquette: Node3D
## Distance (m) à laquelle un lieu est « vu » et entre dans le carnet.
@export var distance_decouverte: float = 5.0
## Rayon (en cases) autour du robot que la carte dessine.
@export var rayon_vue: int = 1
## Repères qui n'entrent pas dans le carnet comme lieux (la montée, l'escalier).
@export var reperes_ignores: String = "ER"
## Outil : au lancement, photographie chaque lieu (et le Phare) en grand, sans brume ni filtre, dans
## concept/croquis_sources/ : ce sont les modèles à redessiner au crayon (voir assets/croquis/LISEZMOI.md).
@export var exporter_photos: bool = false

## Les dessins au crayon faits à la main (assets/croquis/<nom>.png) : seulement les lieux qui comptent
## pour l'enquête (5 ou 6 par île) ; les autres lieux n'ont pas de page, juste leur nom sur la carte.
## S'il manque un dessin prévu, le carnet garde un croquis automatique en secours.
const DOSSIER_DESSINS := "res://assets/croquis/"
const DOSSIER_PHOTOS := "res://concept/croquis_sources/"
const DESSIN_DU_LIEU := {
	"A": "abri",               # là où tout commence, le berceau
	"G": "grande_lanterne",    # le but de l'île
	"X": "atelier",            # le secret : on fabrique des robots ici
	"M": "ancien_corps",       # le premier indice : « les corps, c'est moi »
	"B": "barque",             # ce qui ouvre l'archipel
}
const DESSIN_PHARE := "phare"

var debloque := false
var ouvert := false
var lieux: Array = []      # [{ch, nom, pos, croquis}]
var textes: Array = []     # [{texte, signature}]
var dessins: Array = []    # [{titre, image}]

var _vu: Dictionary = {}
var _reperes: Array = []
var _grille: Dictionary = {}
var _joueur: CharacterBody3D
var _double: int = 0
var _etait_cinematique := false
var _echelle := 1.0
var _en_capture := false
var _sombre: ColorRect
var _livre: Control
var _pages: Array[VBoxContainer] = []
var _numeros: Array[Label] = []
var _signe: Control
var _signe_tween: Tween


func _ready() -> void:
	add_to_group("carnet")
	add_to_group("sauvegarde")
	layer = 18
	_construire()
	await get_tree().process_frame
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	if maquette:
		_reperes = maquette.call("reperes_carnet")
		_grille = maquette.call("carte_carnet")
	_charger(Sauvegarde.donnees(cle_sauvegarde()))
	if exporter_photos:
		_exporter_photos()
	# pour guidage.gd : le carnet posé sur l'étagère appelle (lueur, touche E) tant qu'on ne l'a pas pris
	for o in get_tree().get_nodes_in_group("carnet_objet"):
		o.set_meta("etat_interaction", _etat_objet.bind(o))
		o.add_to_group("interactif")


func _etat_objet(o: Node3D) -> int:
	if debloque or _joueur == null or not o.visible:
		return 0
	if not bool(_joueur.get("cinematique")) and _objet_proche() == o:
		return 2
	return 1


# ---------------------------------------------------------------- sauvegarde (sauvegarde.gd)

func cle_sauvegarde() -> String:
	return "carnet"


## Les croquis photographiés (pas un dessin du projet) sont gardés en PNG à côté de la sauvegarde.
func sauver() -> Dictionary:
	var l: Array = []
	for x in lieux:
		l.append({"ch": x.ch, "croquis": Sauvegarde.garder_image(x.croquis, "lieu_" + str(x.ch).to_lower()), "dessine": x.dessine})
	var t: Array = []
	for x in textes:
		var img: Texture2D = x.image
		t.append({"texte": x.texte, "signature": x.signature, "image": img.resource_path if img else ""})
	var d: Array = []
	for i in dessins.size():
		var x: Dictionary = dessins[i]
		d.append({"titre": x.titre, "image": Sauvegarde.garder_image(x.image, "dessin_%d" % i), "dessine": x.dessine})
	var vu: Array = []
	for v in _vu:
		vu.append([v.x, v.y])
	return {"debloque": debloque, "lieux": l, "textes": t, "dessins": d, "vu": vu}


func _charger(d: Dictionary) -> void:
	if d.is_empty():
		return
	debloque = bool(d.get("debloque", false))
	if debloque:
		for o in get_tree().get_nodes_in_group("carnet_objet"):
			(o as Node3D).visible = false
	for x in d.get("lieux", []):
		for rep in _reperes:
			if rep.ch == str(x.get("ch", "")):
				var croquis: Texture2D = Sauvegarde.charger_image(str(x.get("croquis", "")))
				lieux.append({"ch": rep.ch, "nom": rep.nom, "pos": rep.pos, "croquis": croquis, "dessine": bool(x.get("dessine", false))})
				break
	for x in d.get("textes", []):
		textes.append({"texte": str(x.get("texte", "")), "signature": str(x.get("signature", "")), "image": Sauvegarde.charger_image(str(x.get("image", "")))})
	for x in d.get("dessins", []):
		var img: Texture2D = Sauvegarde.charger_image(str(x.get("image", "")))
		if img:
			dessins.append({"titre": str(x.get("titre", "")), "image": img, "dessine": bool(x.get("dessine", false))})
	for v in d.get("vu", []):
		if v is Array and v.size() == 2:
			_vu[Vector2i(int(v[0]), int(v[1]))] = true


# ---------------------------------------------------------------- ce qu'on voit

func _process(_delta: float) -> void:
	if _joueur == null or _grille.is_empty():
		return
	var p := _joueur.global_position
	var t: float = _grille.taille
	var lignes: int = _grille.grille.size()
	var colonnes: int = _grille.grille[0].size()
	var c := int(floor(p.x / t + colonnes * 0.5))
	var r := int(floor(p.z / t + lignes * 0.5))
	for dr in range(-rayon_vue, rayon_vue + 1):
		for dc in range(-rayon_vue, rayon_vue + 1):
			_vu[Vector2i(c + dc, r + dr)] = true
	if _en_capture or bool(_joueur.get("cinematique")):
		return
	for rep in _reperes:
		if rep.ch in reperes_ignores or _connu(rep.ch):
			continue
		var d := Vector2(p.x - rep.pos.x, p.z - rep.pos.z).length()
		if d < distance_decouverte:
			_decouvrir(rep)
			break


func _connu(ch: String) -> bool:
	for l in lieux:
		if l.ch == ch:
			return true
	return false


## Un lieu découvert : on garde un croquis du lieu, bien cadré (voir _photographier).
func _decouvrir(rep: Dictionary) -> void:
	_en_capture = true
	var croquis: Texture2D = null
	var dessin: Texture2D = null
	if DESSIN_DU_LIEU.has(rep.ch):
		dessin = _dessin(str(DESSIN_DU_LIEU[rep.ch]))
		croquis = dessin if dessin else await _photographier_lieu(rep.pos, Vector2i(480, 300), rep.ch)
	lieux.append({"ch": rep.ch, "nom": rep.nom, "pos": rep.pos, "croquis": croquis, "dessine": dessin != null})
	_en_capture = false
	_signaler()


## Appelé par page_lisible.gd quand on lit une page.
func noter_texte(texte: String, signature: String, image: Texture2D = null) -> void:
	for t in textes:
		if t.texte == texte:
			return
	textes.append({"texte": texte, "signature": signature, "image": image})
	_signaler()


## Appelé par fin_sommet.gd pendant le plan sur le Phare.
func noter_dessin(titre: String) -> void:
	for d in dessins:
		if d.titre == titre:
			return
	# ce que montre la caméra du jeu à cet instant, mais vu sans brume
	var cam := get_viewport().get_camera_3d()
	var dessin := _dessin(DESSIN_PHARE)
	if dessin:
		dessins.append({"titre": titre, "image": dessin, "dessine": true})
		_signaler()
		return
	if cam == null:
		return
	var image: Texture2D = await _photographier(cam.global_transform, Vector2i(600, 380))
	dessins.append({"titre": titre, "image": image, "dessine": false})
	_signaler()


# ---------------------------------------------------------------- le « studio » : une photo propre

## Les croquis ne sont pas des captures d'écran (vue de dessus, brume, filtre gris, flou : illisible) :
## une caméra dédiée, dans une SubViewport qui partage le monde, photographie le lieu de trois quarts,
## sans brume ni flou ; le filtre gris et les nappes de brume sont sur le calque 2, qu'elle ne voit pas.
var _studio: SubViewport
var _objectif: Camera3D


func _preparer_studio() -> void:
	_studio = SubViewport.new()
	_studio.world_3d = get_viewport().world_3d
	_studio.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_studio.msaa_3d = Viewport.MSAA_4X
	add_child(_studio)
	_objectif = Camera3D.new()
	_objectif.fov = 48.0
	_objectif.cull_mask = 1
	_objectif.attributes = CameraAttributesPractical.new()   # pas de flou
	var we := get_tree().current_scene.find_children("*", "WorldEnvironment", true, false)
	if not we.is_empty():
		var env: Environment = (we[0] as WorldEnvironment).environment.duplicate()
		env.fog_enabled = false
		env.volumetric_fog_enabled = false
		env.adjustment_saturation = 1.0
		_objectif.environment = env
	_studio.add_child(_objectif)
	for n in get_tree().get_nodes_in_group("zone_endormie"):
		(n as VisualInstance3D).layers = 2
	for n in get_tree().get_nodes_in_group("brume_ile"):
		(n as VisualInstance3D).layers = 2


## Le dessin fait à la main pour ce lieu, s'il existe (sinon null).
func _dessin(nom: String) -> Texture2D:
	if nom == "":
		return null
	var chemin := DOSSIER_DESSINS + nom + ".png"
	return load(chemin) as Texture2D if ResourceLoader.exists(chemin) else null


## Outil : une photo propre (1536 × 1024) de chaque lieu et du Phare, à redessiner au crayon.
func _exporter_photos() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(DOSSIER_PHOTOS))
	var faits := {}
	for rep in _reperes:
		var nom := str(DESSIN_DU_LIEU.get(rep.ch, ""))
		if nom == "" or faits.has(nom):
			continue
		faits[nom] = true
		var tex := await _photographier_lieu(rep.pos, Vector2i(1536, 1024), rep.ch)
		tex.get_image().save_png(ProjectSettings.globalize_path(DOSSIER_PHOTOS + nom + ".png"))
		print("carnet : photo ", nom)
	# le Phare, vu du sommet (la grande lanterne)
	var fin := get_tree().current_scene.find_child("FinSommet", true, false)
	for rep in _reperes:
		if rep.ch == "G" and fin:
			var phare: Vector3 = fin.call("_position_phare")
			var depuis: Vector3 = rep.pos + Vector3.UP * 3.0 + (phare - rep.pos).normalized() * 3.0
			var cible := phare + Vector3.UP * 14.0
			var xf := Transform3D(Basis.looking_at(cible - depuis), depuis)
			var tex := await _photographier(xf, Vector2i(1536, 1024))
			tex.get_image().save_png(ProjectSettings.globalize_path(DOSSIER_PHOTOS + DESSIN_PHARE + ".png"))
			print("carnet : photo ", DESSIN_PHARE)
	print("carnet : photos terminées dans ", ProjectSettings.globalize_path(DOSSIER_PHOTOS))


## Photographie un lieu : de trois quarts, un peu en hauteur, à ~10 m ; on tourne autour jusqu'à
## trouver un angle d'où rien ne cache le lieu.
## Cadrages particuliers : `ecart` = d'où regarde la caméra (par rapport au lieu) ;
## `toit` = cacher le toit du bâtiment le temps de la photo (on voit l'intérieur, de haut) ;
## `groupe` = viser l'objet de ce groupe plutôt que le centre de la case (la barque flotte au large).
const CADRAGES := {
	"X": {"ecart": Vector3(2.0, 7.0, 3.0), "toit": "Atelier", "hauteur": 0.6},
	"B": {"ecart": Vector3(3.2, 2.6, 4.2), "groupe": "barque_qui_flotte", "hauteur": 0.4},
}


func _photographier_lieu(pos: Vector3, taille: Vector2i = Vector2i(480, 300), ch: String = "") -> Texture2D:
	var cadrage: Dictionary = CADRAGES.get(ch, {})
	var ecart: Vector3 = cadrage.get("ecart", Vector3(5.0, 4.5, 7.5))
	if cadrage.has("groupe"):
		var objet := get_tree().get_first_node_in_group(cadrage.groupe) as Node3D
		if objet:
			pos = objet.global_position
			# on la regarde depuis le large, la falaise derrière elle
			var large := Vector3(pos.x, 0, pos.z).normalized()
			ecart = large * 4.6 + Vector3.UP * ecart.y + large.cross(Vector3.UP) * 1.8
	var cible := pos + Vector3.UP * float(cadrage.get("hauteur", 1.2))
	# le toit caché le temps de la photo
	var toit: Node3D = null
	if cadrage.has("toit"):
		var batiment := get_tree().current_scene.find_child(cadrage.toit, true, false)
		toit = batiment.find_child("Toit", true, false) as Node3D if batiment else null
	var toit_visible := toit.visible if toit else false
	if toit:
		toit.visible = false
	var espace := get_viewport().world_3d.direct_space_state
	var depuis := cible + ecart
	for k in 8:
		var essai := cible + ecart.rotated(Vector3.UP, k * TAU / 8.0)
		var q := PhysicsRayQueryParameters3D.create(cible, essai)
		q.exclude = [_joueur.get_rid()]
		if espace.intersect_ray(q).is_empty():
			depuis = essai
			break
	var xf := Transform3D(Basis.looking_at(cible - depuis), depuis)
	var photo := await _photographier(xf, taille)
	if toit:
		toit.visible = toit_visible
	return photo


func _photographier(xf: Transform3D, taille: Vector2i) -> Texture2D:
	if _studio == null:
		_preparer_studio()
	_studio.size = taille
	_objectif.global_transform = xf
	_objectif.current = true
	_studio.render_target_update_mode = SubViewport.UPDATE_ONCE
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	return ImageTexture.create_from_image(_studio.get_texture().get_image())


func _signaler() -> void:
	if not debloque or ouvert:
		return
	SONS.jouer("page", null, -10.0, 1.15)
	if _signe_tween:
		_signe_tween.kill()
	_signe_tween = create_tween()
	_signe_tween.tween_property(_signe, "modulate:a", 1.0, 0.4)
	_signe_tween.tween_interval(1.6)
	_signe_tween.tween_property(_signe, "modulate:a", 0.0, 0.8)


# ---------------------------------------------------------------- prendre, ouvrir, feuilleter

func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo or _joueur == null:
		return
	var k := (event as InputEventKey).physical_keycode
	if ouvert:
		if k == KEY_TAB or k == KEY_ESCAPE or k == KEY_E:
			get_viewport().set_input_as_handled()
			fermer()
		elif k == KEY_A or k == KEY_LEFT:
			get_viewport().set_input_as_handled()
			_tourner(-1)
		elif k == KEY_D or k == KEY_RIGHT:
			get_viewport().set_input_as_handled()
			_tourner(1)
		return
	if bool(_joueur.get("cinematique")):
		return
	if k == KEY_TAB and debloque:
		get_viewport().set_input_as_handled()
		ouvrir()
	elif k == KEY_E and not debloque:
		var objet := _objet_proche()
		if objet:
			get_viewport().set_input_as_handled()
			_prendre(objet)


## Le carnet posé sur l'étagère de l'abri, s'il est à portée de main.
func _objet_proche() -> Node3D:
	for o in get_tree().get_nodes_in_group("carnet_objet"):
		var p: Vector3 = (o as Node3D).global_position
		var q := _joueur.global_position
		if Vector2(p.x - q.x, p.z - q.z).length() < 1.7:
			return o
	return null


## Le premier moment : il prend le carnet, et le carnet s'ouvre une première fois.
func _prendre(objet: Node3D) -> void:
	debloque = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", objet.global_position)
	SONS.jouer("page", objet.global_position)
	var t := create_tween()
	t.tween_property(objet, "scale", Vector3.ONE * 0.01, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	await t.finished
	objet.visible = false
	await get_tree().create_timer(0.6, false).timeout
	_joueur.set("cinematique", false)
	ouvrir()


func ouvrir() -> void:
	if ouvert:
		return
	ouvert = true
	_etait_cinematique = bool(_joueur.get("cinematique"))
	_joueur.set("cinematique", true)
	_double = clampi(_double, 0, maxi(0, (_toutes_les_pages().size() - 1) / 2))
	_remplir()
	# le livre tient toujours dans la fenêtre
	var ecran := get_viewport().get_visible_rect().size
	var echelle := minf(1.0, minf((ecran.y - 70.0) / 610.0, (ecran.x - 70.0) / 1010.0))
	_livre.pivot_offset = _livre.custom_minimum_size * 0.5
	_echelle = echelle
	_livre.scale = Vector2.ONE * echelle * 0.94
	visible = true
	SONS.jouer("page")
	_livre.modulate.a = 0.0
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	t.tween_property(_sombre, "color:a", 0.45, 0.4)
	t.tween_property(_livre, "scale", Vector2.ONE * echelle, 0.4)
	t.tween_property(_livre, "modulate:a", 1.0, 0.35)


func fermer() -> void:
	if not ouvert:
		return
	ouvert = false
	SONS.jouer("page", null, -4.0, 0.9)
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_property(_sombre, "color:a", 0.0, 0.3)
	t.tween_property(_livre, "scale", Vector2.ONE * _echelle * 0.94, 0.3)
	t.tween_property(_livre, "modulate:a", 0.0, 0.3)
	await t.finished
	if not ouvert:
		visible = false
		_joueur.set("cinematique", _etait_cinematique)


func _tourner(sens: int) -> void:
	var dernier := maxi(0, (_toutes_les_pages().size() - 1) / 2)
	var nouveau := clampi(_double + sens, 0, dernier)
	if nouveau == _double:
		return
	_double = nouveau
	SONS.jouer("page", null, -6.0, randf_range(0.95, 1.1))
	_remplir()


# ---------------------------------------------------------------- les pages

func _toutes_les_pages() -> Array:
	var pages: Array = [{"type": "carte"}]
	for l in lieux:
		if l.croquis != null:
			pages.append({"type": "lieux", "items": [l]})
	for t in textes:
		pages.append({"type": "texte", "item": t})
	for d in dessins:
		pages.append({"type": "dessin", "item": d})
	return pages


func _remplir() -> void:
	var pages := _toutes_les_pages()
	for cote in 2:
		var conteneur := _pages[cote]
		for enfant in conteneur.get_children():
			enfant.queue_free()
		var i := _double * 2 + cote
		_numeros[cote].text = str(i + 1) if i < pages.size() else ""
		if i >= pages.size():
			continue
		var page: Dictionary = pages[i]
		match page.type:
			"carte":
				conteneur.add_child(_titre("L'île"))
				var carte := Control.new()
				carte.set_script(CARTE)
				carte.size_flags_vertical = Control.SIZE_EXPAND_FILL
				carte.set("grille", _grille.get("grille", []))
				carte.set("taille_case", _grille.get("taille", 6.0))
				carte.set("vu", _vu)
				carte.set("lieux", lieux)
				var ls: Array = []
				for l in get_tree().get_nodes_in_group("lanternes"):
					ls.append({"pos": (l as Node3D).global_position, "allumee": bool(l.get("allumee"))})
				carte.set("lanternes", ls)
				carte.set("robot", _joueur.global_position)
				conteneur.add_child(carte)
			"lieux":
				for l in page.items:
					conteneur.add_child(_espace(30))
					conteneur.add_child(_image(l.croquis, Vector2(420, 380), bool(l.get("dessine", false))))
					conteneur.add_child(_legende(l.nom))
			"texte" when page.item.get("image") != null:
				# un document dessiné (affiche, lettre, page de journal) : le carnet en garde le dessin
				conteneur.add_child(_espace(6))
				conteneur.add_child(_image(page.item.image, Vector2(420, 470), true))
			"texte":
				var t := RichTextLabel.new()
				t.bbcode_enabled = true
				t.fit_content = true
				t.scroll_active = false
				t.add_theme_font_override("normal_font", POLICE)
				t.add_theme_font_override("italics_font", POLICE)
				t.add_theme_font_size_override("normal_font_size", 26)
				t.add_theme_font_size_override("italics_font_size", 26)
				t.add_theme_color_override("default_color", ENCRE)
				t.add_theme_constant_override("line_separation", 2)
				var corps: String = str(page.item.texte).strip_edges().replace("\n\n", "\n \n")
				var sig: String = str(page.item.signature)
				t.text = corps + ("\n \n[right][i]%s[/i][/right]" % sig if sig != "" else "")
				conteneur.add_child(t)
			"dessin":
				conteneur.add_child(_image(page.item.image, Vector2(400, 260), bool(page.item.get("dessine", false))))
				conteneur.add_child(_legende(page.item.titre))


func _espace(hauteur: float) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(0, hauteur)
	return c


func _titre(texte: String) -> Label:
	var l := Label.new()
	l.text = texte
	l.add_theme_font_override("font", POLICE)
	l.add_theme_font_size_override("font_size", 38)
	l.add_theme_color_override("font_color", ENCRE)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	return l


func _legende(texte: String) -> Label:
	var l := _titre(texte)
	l.add_theme_font_size_override("font_size", 28)
	return l


func _image(tex: Texture2D, taille: Vector2, dessine: bool = false) -> TextureRect:
	var r := TextureRect.new()
	r.texture = tex
	r.custom_minimum_size = taille
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	r.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	if not dessine:   # un vrai dessin s'affiche tel quel ; sinon, le croquis automatique
		var m := ShaderMaterial.new()
		m.shader = CROQUIS
		r.material = m
	return r


# ---------------------------------------------------------------- le livre (construit en code)

func _construire() -> void:
	visible = false
	_sombre = ColorRect.new()
	_sombre.color = Color(0.12, 0.08, 0.14, 0.0)
	_sombre.set_anchors_preset(Control.PRESET_FULL_RECT)
	_sombre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_sombre)
	var centre := CenterContainer.new()
	centre.set_anchors_preset(Control.PRESET_FULL_RECT)
	centre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(centre)
	_livre = Control.new()
	_livre.custom_minimum_size = Vector2(980, 580)
	centre.add_child(_livre)
	# la couverture (un liseré vert sauge autour des pages)
	var couverture := Panel.new()
	couverture.set_anchors_preset(Control.PRESET_FULL_RECT)
	couverture.offset_left = -14
	couverture.offset_top = -14
	couverture.offset_right = 14
	couverture.offset_bottom = 14
	var sc := StyleBoxFlat.new()
	sc.bg_color = Color(0.5, 0.6, 0.47)
	sc.set_corner_radius_all(12)
	sc.shadow_color = Color(0.1, 0.06, 0.05, 0.4)
	sc.shadow_size = 18
	sc.shadow_offset = Vector2(4, 8)
	couverture.add_theme_stylebox_override("panel", sc)
	_livre.add_child(couverture)
	for cote in 2:
		var feuille := PanelContainer.new()
		feuille.position = Vector2(cote * 490, 0)
		feuille.size = Vector2(490, 580)
		var sp := StyleBoxFlat.new()
		sp.bg_color = PAPIER
		sp.border_color = Color(0.86, 0.78, 0.64)
		sp.set_border_width_all(1)
		# la reliure : un peu d'ombre vers le milieu
		if cote == 0:
			sp.corner_radius_top_left = 6
			sp.corner_radius_bottom_left = 6
		else:
			sp.corner_radius_top_right = 6
			sp.corner_radius_bottom_right = 6
		sp.content_margin_left = 34
		sp.content_margin_right = 34
		sp.content_margin_top = 26
		sp.content_margin_bottom = 40
		feuille.add_theme_stylebox_override("panel", sp)
		_livre.add_child(feuille)
		var contenu := VBoxContainer.new()
		contenu.add_theme_constant_override("separation", 10)
		feuille.add_child(contenu)
		_pages.append(contenu)
		var numero := Label.new()
		numero.add_theme_font_override("font", POLICE)
		numero.add_theme_font_size_override("font_size", 22)
		numero.add_theme_color_override("font_color", Color(ENCRE, 0.7))
		numero.position = Vector2(cote * 490 + (40 if cote == 0 else 430), 540)
		_livre.add_child(numero)
		_numeros.append(numero)
	var reliure := ColorRect.new()
	reliure.color = Color(0.55, 0.45, 0.35, 0.35)
	reliure.position = Vector2(486, 0)
	reliure.size = Vector2(8, 580)
	_livre.add_child(reliure)
	# la petite icône « quelque chose s'ajoute au carnet » (en bas à droite de l'écran, hors du livre)
	_signe = Panel.new()
	_signe.size = Vector2(34, 44)
	_signe.anchor_left = 1.0
	_signe.anchor_top = 1.0
	_signe.anchor_right = 1.0
	_signe.anchor_bottom = 1.0
	_signe.offset_left = -64
	_signe.offset_top = -74
	_signe.offset_right = -30
	_signe.offset_bottom = -30
	var si := StyleBoxFlat.new()
	si.bg_color = Color(0.5, 0.6, 0.47)
	si.border_color = PAPIER
	si.border_width_right = 5
	si.set_corner_radius_all(4)
	_signe.add_theme_stylebox_override("panel", si)
	_signe.modulate.a = 0.0
	var calque_signe := CanvasLayer.new()
	calque_signe.layer = 17
	add_sibling.call_deferred(calque_signe)
	calque_signe.add_child(_signe)
