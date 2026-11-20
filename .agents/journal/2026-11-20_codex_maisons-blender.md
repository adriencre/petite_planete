# 2026-11-20 — codex — maisons fermées de la Colonie

## Demandé

Refaire les maisons fermées dans Blender après le rejet du rendu Meshy.

## Fait

- Reconstruit les quatre maisons aux emplacements du quai et de la ville haute. Les portes sont pleines avec cadre polygonal, les fenêtres en retrait. Les variantes se distinguent par un pignon, une terrasse, des contreforts ou un balcon.
- Enregistré les collections éditables dans `concept/ile_03/colonie_du_lagon.blend`, générées par `tools/blender/colonie_du_lagon.py`. Réexporté `assets/models/ile03/colonie_du_lagon.glb` avec collisions des socles et des murs.
- Décision reportée dans `ILE_03_COLONIE.md` et dans la note de direction artistique. Contrôle en jeu en attente d’un lancement autorisé.
- Vérifié les arêtes et les faces des quatre collections dans Blender. Les huit volumes de collision sont présents dans le GLB. Aperçu rapproché dans `concept/ile_03/maisons_fermees_blender.png`. Graphe régénéré.

## Généralisation au quartier

- Remplacé les 17 logis de décor du lagon et de la rangée extérieure par les quatre variantes, alternées dans chaque quartier. Les variantes partagent les mêmes maillages Blender entre les emplacements.
- Préservé les sept adresses de l’enquête et les bâtiments publics. Décor réexporté avec les collisions. Aucun lancement Godot.

## Lancement demandé

- Réimport du décor et lancement direct de la Colonie sous Godot 4.7.2 sur Mac. Aucune erreur au démarrage. Partie laissée ouverte.

## Cadrage

- Aligné la caméra de la Colonie sur celle du Phare en reprenant les réglages du joueur de l’île 2. Distance de 9 m, inclinaison de 40° et même orientation. Comparaison statique effectuée. La partie déjà ouverte précède ce changement.
- Sur demande, relancé la Colonie avec le nouveau cadrage. Aucune erreur au démarrage et partie laissée ouverte.
