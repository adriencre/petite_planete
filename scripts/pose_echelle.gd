extends SkeletonModifier3D
## Pose les extrémités du robot sur les barreaux pendant la traversée de l'échelle.

var barreau: Vector3
const PAS := 0.31
const NB_BARREAUX := 27
var hauteur_depart := 0.0
var sens := 1.0
var distance_parcourue := 0.0
var poids := 0.0
var suivre_animation := false
var _membres: Array[Vector3i] = []


func _ready() -> void:
	var squelette := get_skeleton()
	for cote in ["Left", "Right"]:
		_membres.append(Vector3i(squelette.find_bone(cote + "Arm"),
			squelette.find_bone(cote + "ForeArm"), squelette.find_bone(cote + "Hand")))
		_membres.append(Vector3i(squelette.find_bone(cote + "UpLeg"),
			squelette.find_bone(cote + "Leg"), squelette.find_bone(cote + "Foot")))


func _process_modification_with_delta(_delta: float) -> void:
	if poids <= 0.0:
		return
	var squelette := get_skeleton()
	var inverse := squelette.global_transform.affine_inverse()
	var pieds := (hauteur_depart - barreau.y) / PAS
	for i in _membres.size():
		var membre := _membres[i]
		if mini(membre.x, mini(membre.y, membre.z)) < 0:
			continue
		var main := i % 2 == 0
		if suivre_animation:
			_ajuster_appui(squelette, membre, inverse, main)
			continue
		var cote := 1.0 if i < 2 else -1.0
		var alternance := 0.0 if (cote < 0) == main else 1.0
		var cycle := distance_parcourue / PAS + alternance
		var mouvement := smoothstep(1.0, 2.0, fposmod(cycle, 2.0))
		var initial := roundf(pieds + (1.17 if main else 0.09) / PAS)
		var index := initial + sens * (floorf(cycle / 2.0) * 2.0 - alternance)
		var depart := clampf(index, 0.0, NB_BARREAUX - 1.0)
		var arrivee := clampf(index + sens * 2.0, 0.0, NB_BARREAUX - 1.0)
		var cible := barreau + Vector3(0.025 + 0.15 * sin(mouvement * PI),
			lerpf(depart, arrivee, mouvement) * PAS, cote * (0.23 if main else 0.13))
		var pivot := inverse * (cible + Vector3(1.0, 0, cote * 0.65))
		_plier(squelette, membre, inverse * cible, pivot, poids)


## Corrige seulement les extrémités qui s'approchent d'un barreau pendant le clip.
func _ajuster_appui(squelette: Skeleton3D, membre: Vector3i, inverse: Transform3D, main: bool) -> void:
	var bout := squelette.global_transform * squelette.get_bone_global_pose(membre.z).origin
	var hauteur_appui := bout.y - (0.0 if main else 0.10)
	var rang := clampf(roundf((hauteur_appui - barreau.y) / PAS), 0.0, NB_BARREAUX - 1.0)
	var transversal := clampf(bout.z - barreau.z, -0.26, 0.26)
	var cible := barreau + Vector3(0.028 if main else 0.21, rang * PAS + (0.0 if main else 0.10), transversal)
	var proximite := 1.0 - smoothstep(0.09, 0.29, bout.distance_to(cible))
	if proximite <= 0.0:
		return
	var pivot := squelette.get_bone_global_pose(membre.y).origin
	_plier(squelette, membre, inverse * cible, pivot, proximite * poids)


func _plier(squelette: Skeleton3D, membre: Vector3i, cible: Vector3, pivot: Vector3, intensite: float) -> void:
	var a := squelette.get_bone_global_pose(membre.x)
	var b := squelette.get_bone_global_pose(membre.y)
	var c := squelette.get_bone_global_pose(membre.z)
	var taille_a := a.origin.distance_to(b.origin)
	var taille_b := b.origin.distance_to(c.origin)
	var arrivee := c.origin.lerp(cible, intensite)
	var axe := (arrivee - a.origin).normalized()
	if axe.is_zero_approx() or taille_a < 0.001 or taille_b < 0.001:
		return
	var distance := clampf(a.origin.distance_to(arrivee),
		absf(taille_a - taille_b) + 0.001, taille_a + taille_b - 0.001)
	var projection := (taille_a * taille_a - taille_b * taille_b + distance * distance) / (2.0 * distance)
	var lat := (pivot - a.origin).slide(axe).normalized()
	var coude := a.origin + axe * projection + lat * sqrt(maxf(taille_a * taille_a - projection * projection, 0.0))
	a.basis = Basis(Quaternion((b.origin - a.origin).normalized(), (coude - a.origin).normalized())) * a.basis
	squelette.set_bone_global_pose(membre.x, a)
	b = squelette.get_bone_global_pose(membre.y)
	c = squelette.get_bone_global_pose(membre.z)
	var direction := (a.origin + axe * distance - b.origin).normalized()
	b.basis = Basis(Quaternion((c.origin - b.origin).normalized(), direction)) * b.basis
	squelette.set_bone_global_pose(membre.y, b)
