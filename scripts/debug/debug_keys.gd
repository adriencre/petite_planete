extends Node
## Touches de test (seulement en version debug) :
## F1 = réveille la zone suivante, F2 = rendort toute l'île,
## F9 = « bascule » provisoire (2e moitié du jeu, en attendant l'île 9).


func _ready() -> void:
	if not OS.is_debug_build():
		queue_free()


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_F1:
			for zone in get_tree().get_nodes_in_group(&"wake_zone"):
				if not zone.is_awake:
					zone.wake()
					return
		KEY_F2:
			for zone in get_tree().get_nodes_in_group(&"wake_zone"):
				zone.sleep()
		KEY_F9:
			Loop.set_flag(&"bascule")
			print("[debug] bascule : 2e moitié activée (rechargée à la prochaine boucle ou en relançant l'île)")
			get_tree().reload_current_scene()
