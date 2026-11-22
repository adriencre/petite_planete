extends Node3D
## L'ancien corps de l'école (ILE_03_COLONIE.md) : à la première approche, une petite cinématique.
## La caméra se pose sur le corps assis, puis descend sur le dessin qu'il tient entre ses mains. Le carnet
## s'ouvre alors tout seul sur la page du même dessin, déjà copié au Phare : aucun texte, le joueur fait
## le lien (« il a fait exactement ce que je fais »). Si le carnet n'a pas ce dessin, la mise en scène suffit.
## À placer comme enfant de l'ancien corps ; `feuille` est le maillage du dessin dans ses mains.

## Le dessin que le carnet doit retrouver (celui de la maison du quai, au Phare).
@export var dessin: Texture2D
## Distance horizontale (m) à laquelle la cinématique se déclenche.
@export var distance_declenchement: float = 3.2
## Nom du maillage du dessin dans le modèle importé.
@export var nom_feuille: String = "Feuille"

var vu: bool = false
var _joueur: CharacterBody3D
var _feuille: Node3D


func _ready() -> void:
	add_to_group("sauvegarde")
	vu = bool(Sauvegarde.donnees(cle_sauvegarde(), self).get("vu", false))
	_feuille = get_parent().find_child(nom_feuille, true, false) as Node3D
	await get_tree().process_frame
	_joueur = get_tree().get_first_node_in_group("joueur") as CharacterBody3D


func cle_sauvegarde() -> String:
	return "souvenir:" + str(get_parent().name)


func sauver() -> Dictionary:
	return {"vu": vu}


func _process(_delta: float) -> void:
	if vu or _joueur == null or bool(_joueur.get("cinematique")):
		return
	var a := _joueur.global_position
	var p := global_position
	if Vector2(a.x - p.x, a.z - p.z).length() < distance_declenchement and absf(a.y - p.y) < 2.0:
		vu = true
		Sauvegarde.noter(cle_sauvegarde(), sauver())
		_jouer()


func _jouer() -> void:
	var corps: Vector3 = global_position
	var mains: Vector3 = _feuille.global_position if _feuille else corps + Vector3.UP * 0.7
	# la caméra se place du côté d'où vient le robot
	var vers: Vector3 = _joueur.global_position - corps
	vers.y = 0.0
	vers = vers.normalized() if vers.length() > 0.01 else Vector3.BACK
	_joueur.set("cinematique", true)
	_joueur.set("regard_cible", corps)
	# 1. le corps assis, de trois quarts
	_joueur.set("cine_cible", corps + Vector3.UP * 0.9)
	_joueur.set("cine_position", corps + vers * 2.8 + Vector3.UP * 1.9)
	var t := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(_joueur, "cine_melange", 1.0, 2.4)
	await t.finished
	await get_tree().create_timer(1.6, false).timeout
	# 2. on descend sur le dessin qu'il tient
	var t2 := create_tween().set_parallel().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t2.tween_property(_joueur, "cine_cible", mains, 2.6)
	t2.tween_property(_joueur, "cine_position", mains + vers * 0.9 + Vector3.UP * 0.8, 2.6)
	await t2.finished
	await get_tree().create_timer(2.0, false).timeout
	# 3. le carnet s'ouvre sur le même dessin ; on le referme soi-même
	var carnet := get_tree().get_first_node_in_group("carnet")
	if carnet and bool(carnet.call("ouvrir_sur_image", dessin)):
		while bool(carnet.get("ouvert")):
			await get_tree().process_frame
		await get_tree().create_timer(0.5, false).timeout
	else:
		await get_tree().create_timer(0.8, false).timeout
	var t3 := create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	t3.tween_property(_joueur, "cine_melange", 0.0, 2.0)
	await t3.finished
	_joueur.set("cinematique", false)
