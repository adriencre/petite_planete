extends Node3D
const SONS := preload("res://scripts/sons.gd")  # les effets sonores (assets/audio/)
## Une page qu'on peut lire (la page 7 d'Iris sur l'établi de l'atelier, plus tard l'ordre d'Ysolde…).
## La feuille luit doucement (plus fort quand le robot est près) ; E : on la lit sur un papier crème à
## l'encre brune (DA : pas de HUD, un carnet dessiné). La première lecture est un moment posé : le robot
## se tourne vers la page, la caméra descend dessus, le texte s'écrit lentement. Les suivantes sont
## immédiates. E ou Échap pour refermer.
## Avec une `image` (un document dessiné : affiche, lettre, page de journal, rendu par
## tools/affiches/rendre.py), c'est ce document qu'on voit, en grand ; la feuille posée dans le décor
## le porte aussi, en miniature. Le `texte` reste la copie gardée par le carnet.
## Une fois lue et refermée, la feuille est rangée dans le carnet (`ramasser`) : elle quitte le décor,
## et on la relit dans le carnet. Quand deux feuilles sont à portée, seule la plus proche répond à E.

@export_multiline var texte: String = ""
@export var signature: String = ""
## Texte d'une version précédente, pour reconnaître la feuille déjà lue.
@export_multiline var texte_ancien: String = ""
@export var distance_lecture: float = 2.4
## Écart vertical maximal entre les pieds du robot et la feuille. Zéro garde la portée horizontale.
@export var hauteur_lecture: float = 0.0
@export var taille_feuille: Vector2 = Vector2(0.34, 0.26)
## Le papier à l'écran : taille du texte et largeur (px). Un long texte (le mode d'emploi, abri.gd) : plus large.
@export var taille_police: int = 21
## Le document dessiné (assets/affiches/*.png). Vide : un papier simple avec le texte.
@export var image: Texture2D
## Illustre une feuille déjà distribuée en conservant sa clé de sauvegarde.
@export var garder_cle_sans_image := false
## Après la lecture, le robot la range dans son carnet : elle disparaît du décor.
@export var ramasser: bool = true
@export var largeur_papier: float = 560.0
## Force de la lueur dorée. Une grande surface (le tableau de l'école) brille moins fort qu'une feuille.
@export_range(0.0, 1.0) var intensite_lueur: float = 1.0
## Un papier à trouver (énigme) : tant qu'il n'est pas lu, halo fort qui pulse, petite lumière dorée et
## rayon de lumière vertical qu'on voit de loin, comme une pierre-soleil (décidé le 2026-11-22).
@export var appel_fort: bool = false
@export var hauteur_rayon: float = 5.0
## Un morceau d'un document déchiré : le carnet le recolle avec les autres morceaux du même assemblage sur
## une seule page (carnet.noter_morceau), puis s'ouvre dessus quand on referme la lecture.
@export var assemblage: String = ""
@export var titre_assemblage: String = ""

var lecture_autorisee: Callable
var deja_lue: bool = false
var _joueur: CharacterBody3D
var _lueur: MeshInstance3D
var _lueur_mat := StandardMaterial3D.new()
var _calque: CanvasLayer
var _papier: PanelContainer
var _texte: RichTextLabel
var _ouverte: bool = false
var _en_cours: bool = false
var _ecriture: Tween
var _doc: Control          # ce qui apparaît à l'écran : le papier écrit, ou le document dessiné
var _voile: ColorRect
var _rayon: MeshInstance3D
var _recolle: Texture2D
var _halo := OmniLight3D.new()


func _ready() -> void:
	add_to_group("interactif")
	if ramasser:
		add_to_group("a_ramasser")
	add_to_group("pages_lisibles")
	add_to_group("sauvegarde")
	if garder_cle_sans_image and image:
		add_to_group("pages_illustrees")
	# la lueur : un voile crème lumineux juste au-dessus de la feuille
	_lueur = MeshInstance3D.new()
	var q := PlaneMesh.new()
	q.size = taille_feuille * 1.15
	_lueur.mesh = q
	_lueur.position = Vector3.UP * 0.012
	_lueur_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_lueur_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_lueur_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_lueur_mat.albedo_color = Color(1.0, 0.85, 0.55, 0.0)
	_lueur.material_override = _lueur_mat
	_lueur.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_lueur)
	if appel_fort:
		q.size = taille_feuille * 1.6
		_preparer_appel()
	if image:
		_feuille_dessinee()
	_construire_papier()
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D
	# « Continuer » : une feuille déjà lue et rangée dans le carnet n'est plus dans le décor
	deja_lue = bool(Sauvegarde.donnees(cle_sauvegarde()).get("lue", false))
	if deja_lue and ramasser:
		hide()
		# Les anciennes entrées du carnet sont chargées après la deuxième frame.
		if is_in_group("pages_illustrees"):
			await get_tree().process_frame
		queue_free()


## Clé stable : ce qui est écrit (ou dessiné) sur la feuille.
func cle_sauvegarde() -> String:
	var chemin := image.resource_path if image and not garder_cle_sans_image else ""
	var identifiant := texte_ancien if not texte_ancien.is_empty() else texte
	return "page:%d" % (signature + identifiant + chemin).hash()


func sauver() -> Dictionary:
	return {"lue": deja_lue}


## Pour guidage.gd : 2 = E possible maintenant, 1 = à découvrir (pas encore lue), 0 = rien à signaler.
## (`point_appel` : où se pose la lueur dorée.)
func etat_interaction() -> int:
	if _joueur == null or _ouverte or _en_cours or not is_visible_in_tree():
		return 0
	if _a_portee() and not bool(_joueur.get("cinematique")):
		return 2
	return 0 if deja_lue else 1


## À portée de lecture, et la plus proche des feuilles à portée (deux feuilles voisines : une seule répond).
func _a_portee() -> bool:
	var d := _distance()
	if d >= distance_lecture:
		return false
	for p in get_tree().get_nodes_in_group("pages_lisibles"):
		if p != self and p.is_inside_tree() and float(p.call("_distance")) < d and float(p.call("_distance")) < float(p.get("distance_lecture")):
			return false
	return true


func point_appel() -> Vector3:
	return global_position


func _distance() -> float:
	if _joueur == null or not is_visible_in_tree():
		return INF
	if lecture_autorisee.is_valid() and not lecture_autorisee.call():
		return INF
	var a := _joueur.global_position
	if hauteur_lecture > 0.0 and absf(a.y - global_position.y) > hauteur_lecture:
		return INF
	return Vector2(a.x - global_position.x, a.z - global_position.z).length()


func _process(_delta: float) -> void:
	if _joueur == null:
		return
	var onde: float = 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.003)
	var force: float = 0.18 if deja_lue else 0.3
	if _distance() < distance_lecture:
		force = 0.55
	# ce qu'on ne peut pas emporter (le tableau, une inscription) : une fois copié dans le carnet,
	# il ne luit plus (décidé le 2026-11-22)
	if deja_lue and not ramasser:
		force = 0.0
	var appel: bool = appel_fort and not deja_lue and not _ouverte
	if appel:
		force = 1.0
	_lueur_mat.albedo_color.a = minf(1.0, force * intensite_lueur * (0.6 + 0.4 * onde) * (0.0 if _ouverte else 1.0))
	if _rayon:
		_rayon.visible = appel and is_visible_in_tree()
		_halo.visible = _rayon.visible
		if _rayon.visible:
			var sortie: Vector3 = global_basis.y.normalized() * 0.3
			_rayon.global_transform = Transform3D(Basis.IDENTITY, global_position + sortie + Vector3.UP * (hauteur_rayon * 0.5 - 0.3))
			_halo.global_position = global_position + global_basis.y.normalized() * 0.6
			_halo.light_energy = 1.2 + 0.8 * onde


## Le rayon vertical et la petite lumière d'un papier à trouver (`appel_fort`). Ils restent droits même
## si la feuille est debout contre un mur : on les place dans le monde, pas dans le repère de la feuille.
func _preparer_appel() -> void:
	_rayon = MeshInstance3D.new()
	_rayon.name = "Rayon"
	var cone := CylinderMesh.new()
	cone.top_radius = 0.55
	cone.bottom_radius = 0.14
	cone.height = hauteur_rayon
	cone.radial_segments = 16
	cone.cap_top = false
	cone.cap_bottom = false
	var mat := ShaderMaterial.new()
	mat.shader = preload("res://shaders/rayon_lumiere.gdshader")
	mat.set_shader_parameter("couleur", Color(1.0, 0.8, 0.45))
	mat.set_shader_parameter("hauteur", hauteur_rayon)
	mat.set_shader_parameter("intensite", 0.8)
	cone.material = mat
	_rayon.mesh = cone
	_rayon.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_rayon.top_level = true
	add_child(_rayon)
	_halo.light_color = Color(1.0, 0.8, 0.45)
	_halo.omni_range = 3.5
	_halo.shadow_enabled = false
	_halo.top_level = true
	add_child(_halo)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or _joueur == null:
		return
	var k := event as InputEventKey
	if not k.pressed or k.echo:
		return
	# E pendant que le texte s'écrit : on l'affiche en entier tout de suite
	if _ecriture and _ecriture.is_running() and k.physical_keycode == KEY_E:
		get_viewport().set_input_as_handled()
		_ecriture.kill()
		_texte.visible_ratio = 1.0
		return
	if _en_cours:
		return
	if _ouverte and (k.physical_keycode == KEY_E or k.physical_keycode == KEY_ESCAPE):
		get_viewport().set_input_as_handled()
		_fermer()
	elif not _ouverte and k.physical_keycode == KEY_E and not bool(_joueur.get("cinematique")) and _a_portee():
		get_viewport().set_input_as_handled()
		_lire()


# ---------------------------------------------------------------- lire

func _lire() -> void:
	_en_cours = true
	_ouverte = true
	var premiere: bool = not deja_lue
	deja_lue = true
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", global_position)
	if premiere:
		# il se tourne vers la page ; la caméra descend dessus
		var cible: Vector3 = global_position + Vector3.UP * 0.1
		var vers: Vector3 = _joueur.global_position - global_position
		vers.y = 0.0
		vers = vers.normalized() if vers.length() > 0.01 else Vector3.BACK
		_joueur.set("cine_cible", cible)
		_joueur.set("cine_position", cible + vers * 1.4 + Vector3.UP * 1.5)
		var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		t.tween_property(_joueur, "cine_melange", 1.0, 1.8)
		await t.finished
		await get_tree().create_timer(0.6, false).timeout
	# le papier apparaît ; le carnet en garde une copie
	var carnet := get_tree().get_first_node_in_group("carnet")
	if carnet and not assemblage.is_empty():
		_recolle = carnet.call("noter_morceau", assemblage, image, titre_assemblage) as Texture2D
	elif carnet:
		carnet.call("noter_texte", texte, signature, image)
	SONS.jouer("page")
	if _texte:
		_texte.visible_ratio = 0.0 if premiere else 1.0
	_calque.visible = true
	_cadrer_document()
	_doc.modulate.a = 0.0
	var f := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	var duree := 0.6 if premiere else 0.25
	f.tween_property(_doc, "modulate:a", 1.0, duree)
	if _voile:
		f.tween_property(_voile, "color:a", 0.55, duree)
	if image:   # le document se pose, un peu de travers, comme une feuille qu'on tient
		_doc.scale = Vector2.ONE * 0.93
		_doc.rotation_degrees = -3.5
		f.tween_property(_doc, "scale", Vector2.ONE, duree * 1.4)
		f.tween_property(_doc, "rotation_degrees", -1.0, duree * 1.4)
	await f.finished
	if premiere and _texte:   # le texte s'écrit lentement, comme une lecture
		var n: int = _texte.get_total_character_count()
		_ecriture = create_tween()
		_ecriture.tween_property(_texte, "visible_ratio", 1.0, clampf(n * 0.035, 3.0, 12.0))
		while _ecriture.is_running():
			await get_tree().process_frame
	_en_cours = false


func _fermer() -> void:
	_en_cours = true
	var f := create_tween().set_parallel()
	f.tween_property(_doc, "modulate:a", 0.0, 0.35)
	if _voile:
		f.tween_property(_voile, "color:a", 0.0, 0.35)
	await f.finished
	_calque.visible = false
	_ouverte = false
	if float(_joueur.get("cine_melange")) > 0.0:
		var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		t.tween_property(_joueur, "cine_melange", 0.0, 1.5)
		await t.finished
	_joueur.set("cinematique", false)
	_en_cours = false
	# Un morceau de document : on voit tout de suite où il se place parmi ceux déjà trouvés.
	if _recolle:
		var carnet := get_tree().get_first_node_in_group("carnet")
		if carnet:
			carnet.call("ouvrir_sur_image", _recolle)
		_recolle = null
	if ramasser:
		_ranger()


## Il la plie et la range dans son carnet : la feuille se soulève, file vers le robot et disparaît
## (le carnet en a déjà gardé le dessin, voir _lire).
func _ranger() -> void:
	_en_cours = true
	Sauvegarde.noter(cle_sauvegarde(), sauver())
	remove_from_group("interactif")
	remove_from_group("pages_lisibles")
	SONS.jouer("page", global_position, -6.0, 1.2)
	var depart := global_position
	var vole := func(t: float) -> void:
		var vers: Vector3 = _joueur.global_position + Vector3.UP * 1.1
		var p := depart.lerp(vers, t)
		p.y += sin(t * PI) * 0.5
		global_position = p
		scale = Vector3.ONE * maxf(1.0 - t * 0.9, 0.05)
	var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	t.tween_method(vole, 0.0, 1.0, 0.7)
	await t.finished
	queue_free()


# ---------------------------------------------------------------- le papier (DA : crème, encre brune)

func _construire_papier() -> void:
	_calque = CanvasLayer.new()
	_calque.layer = 15
	_calque.visible = false
	add_child(_calque)
	if image:
		_construire_document()
		return
	var centre := CenterContainer.new()
	centre.set_anchors_preset(Control.PRESET_FULL_RECT)
	centre.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_calque.add_child(centre)
	_papier = PanelContainer.new()
	_papier.custom_minimum_size = Vector2(largeur_papier, 0)
	_papier.rotation_degrees = -1.2
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.97, 0.93, 0.84)
	style.border_color = Color(0.82, 0.72, 0.56)
	style.set_border_width_all(2)
	style.set_corner_radius_all(6)
	style.shadow_color = Color(0.25, 0.18, 0.1, 0.35)
	style.shadow_size = 14
	style.shadow_offset = Vector2(4, 6)
	style.content_margin_left = 44
	style.content_margin_right = 44
	style.content_margin_top = 36
	style.content_margin_bottom = 36
	_papier.add_theme_stylebox_override("panel", style)
	centre.add_child(_papier)
	_doc = _papier
	_texte = RichTextLabel.new()
	_texte.bbcode_enabled = true
	_texte.fit_content = true
	_texte.scroll_active = false
	_texte.custom_minimum_size = Vector2(largeur_papier - 88.0, 0)
	_texte.add_theme_color_override("default_color", Color(0.36, 0.24, 0.14))
	_texte.add_theme_font_size_override("normal_font_size", taille_police)
	_texte.add_theme_font_size_override("italics_font_size", taille_police)
	_texte.add_theme_font_size_override("bold_font_size", taille_police)
	_texte.add_theme_constant_override("line_separation", 6)
	var corps := texte.strip_edges().replace("\n\n", "\n \n")
	_texte.text = corps + ("\n \n[right][i]%s[/i][/right]" % signature if signature != "" else "")
	_papier.add_child(_texte)


# ---------------------------------------------------------------- le document dessiné

## À l'écran : le document en grand (90 % de la fenêtre au plus), sur un voile sombre.
func _construire_document() -> void:
	_voile = ColorRect.new()
	_voile.color = Color(0.1, 0.07, 0.12, 0.0)
	_voile.set_anchors_preset(Control.PRESET_FULL_RECT)
	_voile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_calque.add_child(_voile)
	var affiche := TextureRect.new()
	affiche.texture = image
	affiche.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	affiche.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	affiche.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_calque.add_child(affiche)
	_doc = affiche


func _cadrer_document() -> void:
	if image == null:
		return
	var ecran := get_viewport().get_visible_rect().size
	var taille := image.get_size()
	var k := minf(ecran.x * 0.9 / taille.x, ecran.y * 0.9 / taille.y)
	_doc.size = taille * k
	_doc.position = (ecran - _doc.size) * 0.5
	_doc.pivot_offset = _doc.size * 0.5


## Dans le décor : la feuille porte le document, en miniature (bords déchirés compris, mipmaps à l'import).
func _feuille_dessinee() -> void:
	var feuille := MeshInstance3D.new()
	feuille.name = "Feuille"
	var q := PlaneMesh.new()
	q.size = taille_feuille
	feuille.mesh = q
	var m := StandardMaterial3D.new()
	m.albedo_texture = image
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	m.alpha_scissor_threshold = 0.5
	m.roughness = 1.0
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	feuille.material_override = m
	feuille.position = Vector3.UP * 0.004
	add_child(feuille)
