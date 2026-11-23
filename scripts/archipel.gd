extends RefCounted
## La carte de la mer : où sont les îles les unes par rapport aux autres. Chaque scène d'île a son
## origine à sa position sur cette carte (m ; x vers l'est, z vers le sud, comme dans les scènes).
## - Le Phare : à 170 m du Réveil, à l'est (fin_sommet.gd : direction_phare, distance_phare).
## - La Colonie : au cap 129° depuis le Phare (la rose des vents de la maison d'Iris, ILE_02_PHARE.md),
##   à 120 m.
## Sert à large.gd (silhouettes au loin, traversées) et à sauvegarde.gd (Sauvegarde.traverser).

const ILES := {
	"reveil": {"nom": "le Réveil", "scene": "res://scenes/ile_01_maquette.tscn", "position": Vector3(0.0, 0.0, 0.0)},
	"phare": {"nom": "le Phare", "scene": "res://scenes/ile_02_maquette.tscn", "position": Vector3(168.8, 0.0, -20.25)},
	"colonie": {"nom": "la Colonie", "scene": "res://scenes/ile_03_maquette.tscn", "position": Vector3(262.05, 0.0, 55.27)},
}
