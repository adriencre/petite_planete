# État du projet — passation entre agents

> Mis à jour le **2026-11-19** par **claude** (session : île 2, terrain « blocs taillés » + lumière).
> À réécrire à chaque fin de session (voir `procedures/fin-de-session.md`). ≤ 1 page.

## Où on en est
- **Docs de conception** : les 7 îles sont écrites (`ILE_01` … `ILE_07`, `TOILE_ENQUETE.md`). Feuille de route : `ROADMAP.md`.
- **DA v6** (`DA.md`) : vue de dessus, low-poly à facettes, pastels lumineux.
- **Île 1** jouable en maquette : `scenes/ile_01_maquette.tscn`.
- **Île 2** (`scenes/ile_02_maquette.tscn`) : terrain refait dans Blender en « blocs taillés à facettes, strates nettes » (validé par l'utilisateur), généré par `tools/blender/terrain_ile_02.py` depuis la carte du nœud Maquette → `assets/models/ile02/terrain_ile_02.glb`, branché par `terrain_modele`. Ambiance : `assets/ambiances/ile_02.tres`. Objets (Phare, maisons, caps…) encore provisoires.

## En chantier (non commité sur `main`)
- Tout le travail île 2 du 2026-11-19 (voir journal `2026-11-19_claude_ile-02-terrain.md`).
→ Proposer à l'utilisateur de committer.

## Prochaines étapes (île 2)
1. Faire vérifier les escaliers en jeu par l'utilisateur (ou lancer `tests/diag_escaliers_ile_02.gd`, **avec son accord** : il a refusé une fois).
2. Faire tester en jeu la brume épaisse (branchée sur la batterie) et la marée (autoload `HorlogeMonde`, F8 accélère) ; régler les chiffres. Mettre en scène « emporté par la mer » (pour l'instant un simple retour au sec).
3. Fondu des obstacles entre la caméra et le robot (le Phare le cachera). Relief : on GARDE 2,5 m par niveau (décidé).
4. K2 (G1 : chaussée + 3 balises à allumer, échelle de marée, ancien corps), chaussée en dalles.
5. Maison du quai : construite (Blender + scène `scenes/ile02/maison_quai.tscn`) ; reste les objets héros Meshy (poêle, cirés/bottes…), la lanterne de recharge (modèle des Semeurs à poser au repère `RepereLanterne`), le texte du cahier.
6. Autres objets Meshy (~120 crédits : Phare, maison du quai, hangar, miroirs, banc, arbre rose mort…) — annoncer le coût avant.

## Pièges actifs
- Modifier la carte de l'île 2 → relancer `terrain_ile_02.py` dans Blender, puis réimporter le .glb (`filesystem_manage reimport`).
- Le jeu lancé depuis l'éditeur bloque toutes les écritures MCP : demander à l'utilisateur de l'arrêter.
- Script `@tool` modifié de l'extérieur : ses nouvelles `@export` peuvent rester `null` dans l'éditeur → les régler via MCP (voir procedures/godot.md).
- Le MCP Blender n'a pas d'état entre deux appels (`exec` du script à chaque fois).
- Toujours **demander avant de lancer** le jeu ou un test.
- Meshy : 2 637 des 2 836 crédits sont mensuels (renouvellement 2026-12-16).

## Questions ouvertes pour l'utilisateur
- Caméra v6 : angle/focale, fixe ou orientable, tilt-shift ? (`DA.md`)
