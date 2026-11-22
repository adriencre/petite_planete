# État du projet — passation entre agents

> Mis à jour le **2026-11-22** par **Claude** (PC fixe).

## G2, la rue des Trois-Soleils (Colonie) — jouable, validé par l'utilisateur (« ça marche »), commité
- **Blender** : `tools/blender/ville_haute.py` (parvis, maison commune au secteur 14, ville haute habillée, colonnes, panneau, borne). Rendus `concept/ile_03/ville_haute_*.png`.
- **Documents** : 11 PNG dans `assets/affiches/` (affiches 1 à 4 + départ, plan d'éclairage A/B/C via `plan_eclairage.js`, ordres d'Ysolde, lettres de Tavin, plan de l'archipel).
- **Godot** : `scenes/ile03/parvis_trois_soleils.tscn` (9 lanternes, `scripts/porte_trois_soleils.gd`), `scenes/ile03/borne_recharge.tscn` (pierre_soleil.gd), documents et coupe `InterieurCommune` dans la Colonie. Généré par `tools/godot/ville_haute_scenes.py` (n'ajoute rien si le parvis existe déjà). `batiments_fantomes.gd` : bâtiment « commune ».
- `lanterne_fleur.gd` : en vue de dessus, seule la lanterne la plus proche répond à E (avant : n'importe laquelle à moins de 5 m).
- Après le 1er essai : maison commune réaménagée, appel fort des papiers (`page_lisible.appel_fort`), caméra par zones de cadrage (`scripts/camera_zones.gd`, `scripts/zone_camera.gd`, nœuds Zone* ; la caméra d'anneau, refusée, est supprimée). Relancé sans erreur. À essayer : `.agents/A_TESTER.md` 4.21 à 4.34.
- Après une modif Blender de la ville haute : `python tools/godot/ville_haute_scenes.py` (il remplace ses blocs dans la Colonie), réimport du GLB, puis `scene_open(force_reload=true)`.

## Colonie, déjà en place
- Ville basse, école, maison d'Aube, Coin noir (grotte), bâtiments fantômes. Presque rien n'a été essayé en jeu : voir `.agents/A_TESTER.md` (bloc 4 et points 5.7 à 5.15).
- La Colonie est accessible par le menu de développement, sans sauvegarde de l'île. Le carnet lit celui de l'île 1. Thème d'Aube provisoire.
- Reste pour l'île : G3 (marée, carillon, écluse, serres, lampe-mère), G4 (pleine lune, vieux port, Centrale), dessins d'Aube éparpillés, valises « Nef », vraies maisons « adresses » de la ville haute (verriers, projecteurs, palier : encore des boîtes).

## Ailleurs
- Île 2 : parcours continu du Phare, guidage, marée et fondu à essayer. Menu : retour visuel et chargement à vérifier.

## Pièges actifs
- Tout ce qui est ajouté au script Colonie après `export_scene.gltf` n'arrive pas dans Godot.
- Blender peut tourner sans MCP : `blender.exe -b -P tools/blender/colonie_du_lagon.py -- --sans-rendu` (voir procédures/blender.md).
- Demander avant tout lancement ou test Godot. Tout est commité (G2, Coin noir, visibilité, ponts, menu…).
