extends Node3D
## Fait pousser la mousse (calque de matériau) sur un ancien corps importé, sauf sur les pièces exclues.

@export var mousse: Material
@export var exclure: PackedStringArray = ["Feuille"]


func _ready() -> void:
	if mousse == null:
		return
	for noeud in find_children("*", "MeshInstance3D", true, false):
		var maillage := noeud as MeshInstance3D
		if not exclure.has(maillage.name):
			maillage.material_overlay = mousse
