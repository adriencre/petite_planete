extends SceneTree
## Vérification sans fenêtre : ordre d'allumage (petites -> grande -> sommet).

func _init() -> void:
	var racine := (load("res://scenes/ile_01_maquette.tscn") as PackedScene).instantiate()
	root.add_child(racine)
	for i in 10:
		await physics_frame
	var par_rang := {}
	for l in get_nodes_in_group("lanternes"):
		var r: int = l.get("rang")
		if not par_rang.has(r):
			par_rang[r] = []
		par_rang[r].append(l)
	print("lanternes par rang : ", par_rang.keys().map(func(k): return "%d:%d" % [k, par_rang[k].size()]))
	var grande: Node = par_rang[1][0] if par_rang.has(1) else null
	var sommet: Node = par_rang[2][0] if par_rang.has(2) else null
	print("au depart : grande prete=%s sommet pret=%s" % [grande.call("_prete") if grande else "-", sommet.call("_prete") if sommet else "-"])
	for l in par_rang[0]:
		l.set("allumee", true)
	print("3 petites allumees : grande prete=%s sommet pret=%s" % [grande.call("_prete") if grande else "-", sommet.call("_prete") if sommet else "-"])
	if grande:
		grande.set("allumee", true)
	print("grande allumee : sommet pret=%s" % [sommet.call("_prete") if sommet else "-"])
	quit()
