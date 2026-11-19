# État du projet — passation entre agents

> Mis à jour le **2026-11-19** par **claude** (session : création du dossier `.agents/`).
> À réécrire à chaque fin de session (voir `procedures/fin-de-session.md`). ≤ 1 page.

## Où on en est
- **Docs de conception** : les 7 îles sont écrites (`ILE_01` … `ILE_07`, `TOILE_ENQUETE.md`) ; quelques points « à valider ». Feuille de route : `ROADMAP.md`.
- **DA v6** (`DA.md`) : vue de dessus, low-poly à facettes, pastels lumineux. La 1re personne est abandonnée.
- **Île 1** jouable en maquette : `scenes/ile_01_maquette.tscn` (abri, pierre-soleil, lanternes, cascade/atelier, barque, fin au sommet).
- **Île 2** : une maquette grise a démarré (`scenes/ile_02_maquette.tscn`, non commitée).

## En chantier (non commité sur `main`)
Gros lot de travail du 2026-11-17/18 pas encore commité :
- Pour les joueurs : écran titre (`scenes/ecran_titre.tscn`, scène principale), menu pause, réglages (`scenes/ui/`, `scripts/ui/`, `scripts/reglages.gd`), sauvegarde auto (`scripts/sauvegarde.gd`), jauge batterie HUD (`scenes/ui/hud_batterie.tscn`), thème `assets/ui/theme_carnet.tres`, bus audio `default_bus_layout.tres`.
- Île 1 (décisions du 2026-11-18 dans `ILE_01_REVEIL.md` §13 points 7-9) : abri vieilli sauf le berceau, « pas de géants » (dalles) vers l'atelier (`chemin_geants`), Tavin envoie au Phare ; affiches `mode_emploi` / `ordre_ysolde` refaites.
- Ce dossier `.agents/` + `AGENTS.md` + `tools/agents/sync.py` (2026-11-19).
→ Proposer à l'utilisateur de committer ce lot (il n'a pas encore été demandé).

## Prochaines étapes (d'après ROADMAP.md)
1. Étape 2 : finir d'adapter l'île 1 à la v4 (liste dans ROADMAP.md).
2. Étape 3 : archipel + île 2 (ordre K1 → J4 → K2 … dans `ILE_02_PHARE.md` §11).

## Pièges actifs
- MCP `godot-ai` : timeout si l'éditeur Godot n'est pas ouvert (normal).
- MCP `blender` : l'utilisateur doit cliquer « Start MCP Server » dans Blender.
- MCP `meshy` : il faut la variable d'environnement `MESHY_API_KEY` (voir `.agents/README.md`).
- Toujours **demander avant de lancer** le jeu ou un test.

## Questions ouvertes pour l'utilisateur
- Caméra v6 : angle/focale, fixe ou orientable, tilt-shift ? (`DA.md`, « À décider »)
- Vision trouble à batterie basse en vue de dessus : effet d'écran ou seulement l'ampoule ?
