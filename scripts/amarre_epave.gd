extends Node3D
## L'amarrage est ouvert lorsque le banc affleure et que le faisceau le dégage.

var port_attache := false

@onready var _indication: Label3D = $Indication


func _ready() -> void:
	add_to_group("pontons")


func amarre() -> Transform3D:
	return $Amarre.global_transform


func debarquement() -> Vector3:
	return $Debarquement.global_position


func bitte() -> Vector3:
	return $Bitte.global_position


func amarrage_possible() -> bool:
	return str(get_parent().call("condition_acces")).is_empty()


func signaler(proche: bool) -> void:
	_indication.text = str(get_parent().call("condition_acces"))
	_indication.visible = proche and not _indication.text.is_empty()
