extends MeshInstance3D
## Une racine lumineuse (maquette.gd : _racines) : elle relie une petite lanterne à la grande.
## Quand la petite lanterne s'allume, la lumière monte le long de la racine jusqu'à la grande ;
## quand elle s'éteint (mort, reprise de la lumière), la lumière redescend.

## La petite lanterne d'où part la lumière.
var lanterne: Node
## Temps (s) pour que la lumière parcoure toute la racine.
@export var duree_montee: float = 3.5
@export var duree_descente: float = 1.5

var _lumiere: float = 0.0
var _mat: ShaderMaterial


func _ready() -> void:
	_mat = material_override as ShaderMaterial


func _process(delta: float) -> void:
	if lanterne == null or _mat == null:
		return
	var cible: float = 1.0 if bool(lanterne.get("allumee")) else 0.0
	if is_equal_approx(_lumiere, cible):
		return
	var vitesse: float = 1.0 / (duree_montee if cible > _lumiere else duree_descente)
	_lumiere = move_toward(_lumiere, cible, delta * vitesse)
	_mat.set_shader_parameter("lumiere", _lumiere)
