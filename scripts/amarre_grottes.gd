extends "res://scripts/amarre_epave.gd"
## L'estran devant le portail reste praticable tant que le seuil est découvert.

@export var niveau_limite := 0.08


func amarrage_possible() -> bool:
	return HorlogeMonde.niveau_mer() <= niveau_limite


func signaler(proche: bool) -> void:
	_indication.visible = proche and not amarrage_possible()
