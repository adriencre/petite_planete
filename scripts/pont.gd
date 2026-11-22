@tool
extends Node3D
## Petit pont de bois en dos d'âne (île 1, décidé le 2026-11-22 : on marchait sur la rivière).
## Le tablier franchit la rivière selon l'axe X local : une montée, un palier, une descente, avec deux
## garde-corps. Collision sur le tablier et les garde-corps : on ne tombe pas à l'eau.
## Réglable dans l'éditeur ; maquette.gd en pose un là où le chemin traverse la rivière.

@export var longueur: float = 5.6:
	set(v): longueur = v; _construire()
@export var largeur: float = 1.8:
	set(v): largeur = v; _construire()
## Hauteur du palier au-dessus des berges.
@export var hauteur: float = 0.35:
	set(v): hauteur = v; _construire()
@export var couleur_bois: Color = Color(0.72, 0.52, 0.4):
	set(v): couleur_bois = v; _construire()
@export var couleur_planches: Color = Color(0.86, 0.68, 0.52):
	set(v): couleur_planches = v; _construire()


func _ready() -> void:
	_construire()


func _construire() -> void:
	if not is_inside_tree():
		return
	for e in get_children():
		e.queue_free()
	var bois := StandardMaterial3D.new()
	bois.albedo_color = couleur_bois
	bois.roughness = 1.0
	var planches := StandardMaterial3D.new()
	planches.albedo_color = couleur_planches
	planches.roughness = 1.0
	var corps := StaticBody3D.new()
	corps.name = "Collision"
	add_child(corps)
	var rampe: float = longueur * 0.3
	var palier: float = longueur - 2.0 * rampe
	var pente: float = atan2(hauteur, rampe)
	var long_rampe: float = sqrt(rampe * rampe + hauteur * hauteur)
	var ep := 0.12
	# le tablier : montée, palier, descente (le bas des rampes s'enfonce un peu dans la berge)
	var segments := [
		[Vector3(-palier * 0.5 - rampe * 0.5, hauteur * 0.5 - ep * 0.5, 0), long_rampe + 0.1, pente],
		[Vector3(0, hauteur - ep * 0.5, 0), palier, 0.0],
		[Vector3(palier * 0.5 + rampe * 0.5, hauteur * 0.5 - ep * 0.5, 0), long_rampe + 0.1, -pente],
	]
	for s in segments:
		var centre: Vector3 = s[0]
		var l: float = s[1]
		var a: float = s[2]
		_boite(planches, centre, Vector3(l, ep, largeur), a)
		_forme(corps, centre, Vector3(l, ep, largeur), a)
		# lattes sombres en travers, pour lire le bois de dessus
		var n := int(l / 0.38)
		for i in n:
			var x: float = -l * 0.5 + (i + 0.5) * l / n
			var p := centre + Vector3(cos(a) * x, sin(a) * x + ep * 0.5 + 0.005, 0)
			_boite(bois, p, Vector3(0.05, 0.012, largeur * 0.98), a)
	# garde-corps : poteaux et main courante, de chaque côté
	for cote in [-1.0, 1.0]:
		var z: float = cote * (largeur * 0.5 - 0.06)
		for x in [-palier * 0.5 - rampe, -palier * 0.5, palier * 0.5, palier * 0.5 + rampe]:
			var h_sol: float = hauteur if absf(x) <= palier * 0.5 + 0.01 else 0.0
			_boite(bois, Vector3(x, h_sol + 0.45, z), Vector3(0.12, 0.9, 0.12), 0.0)
		_boite(bois, Vector3(0, hauteur + 0.85, z), Vector3(palier + 0.12, 0.08, 0.1), 0.0)
		for sens in [-1.0, 1.0]:
			var c := Vector3(sens * (palier * 0.5 + rampe * 0.5), hauteur * 0.5 + 0.85, z)
			_boite(bois, c, Vector3(long_rampe, 0.08, 0.1), -sens * pente)
		# collision des garde-corps : on ne tombe pas à l'eau
		_forme(corps, Vector3(0, hauteur + 0.5, z), Vector3(longueur - 0.6, 1.0, 0.12), 0.0)


func _boite(mat: Material, centre: Vector3, taille: Vector3, angle_z: float) -> void:
	var m := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = taille
	bm.material = mat
	m.mesh = bm
	m.position = centre
	m.rotation.z = angle_z
	add_child(m)


func _forme(corps: StaticBody3D, centre: Vector3, taille: Vector3, angle_z: float) -> void:
	var boite := BoxShape3D.new()
	boite.size = taille
	var cs := CollisionShape3D.new()
	cs.shape = boite
	cs.position = centre
	cs.rotation.z = angle_z
	corps.add_child(cs)
