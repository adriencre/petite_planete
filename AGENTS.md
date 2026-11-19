# AGENTS.md — Petite Planète (v5)

Instructions communes à **tous les agents IA** (Claude Code, Codex…). L'utilisateur passe de l'un à l'autre : tout ce qui doit survivre d'une session à l'autre est dans `.agents/` (voir `.agents/README.md`).

## Le projet
Jeu Godot 4.7 (GDScript), solo, en français. Enquête à la Outer Wilds : « **Où sont les Semeurs ?** ». Un petit robot jardinier se réveille sur une île, rallume des lanternes avec un câble branché à son poignet, explore 7 îles.
- Règles du jeu : `DESIGN.md` · histoire : `ENQUETE.md` · îles : `ILE_01_REVEIL.md` … `ILE_07_ILE_CACHEE.md` · toile de l'enquête : `TOILE_ENQUETE.md`
- Direction artistique : `DA.md` (v6 : vue de dessus, low-poly à facettes, pastels lumineux) · feuille de route : `ROADMAP.md`
- Code : `scenes/`, `scripts/`, `shaders/`, `tests/` · outils : `tools/` · ancien prototype : dossier `Bureau/petite-planete` (ne pas réutiliser)

## Au démarrage de chaque session
1. Lire `.agents/ETAT.md` (où on en est, pièges actifs).
2. Lire `.agents/memoire/INDEX.md`, puis les notes utiles à la tâche.
3. Lire les 2-3 dernières entrées de `.agents/journal/` (les plus récentes par nom de fichier).
4. Si la tâche touche un outil, lire la procédure dans `.agents/procedures/`.

## Règles impératives (retours de l'utilisateur)
- **Demander avant de lancer** le jeu ou un test Godot (même headless). Regrouper, demander une fois, pas de relances en boucle.
- **Proposer avant de développer** : débattre en texte, poser des questions avec des propositions quand c'est flou. L'utilisateur aime être questionné.
- **Scènes éditables** : vraies `.tscn`/`.tres` visibles dans l'éditeur, scripts courts. Pas tout en code.
- **Rythme lent** : la 1re fois de chaque mécanique est une petite cinématique ; rien d'instantané.
- **Pas de magie** : tout est mécanique (câble, fiche, crans). **Pas de plantation** pour ouvrir des chemins.
- **DA.md fait foi** pour tout ce qui est visuel ; les docs d'île font foi pour le contenu. Une décision prise avec l'utilisateur va dans le doc concerné.
- Textes, noms de fichiers, commentaires de code et commits **en français**.
- Ne **committer** que sur demande. Jamais de secret dans le repo.

## Code : graphify d'abord
Le graphe de connaissances est dans `graphify-out/`. Avant le premier grep/lecture de source pour une question sur le code : `graphify query "<question>"` (puis `path`, `explain`, `section`). Après avoir modifié du code ou des scènes : `python tools/graphify_godot.py` (**jamais** `graphify update .` seul). Détail : `.agents/procedures/graphify.md`. Mettre cette règle dans le prompt de tout sous-agent qui explore le code.

## Procédures
`.agents/procedures/` : `godot.md` (exe, tests headless, pièges de l'éditeur ouvert, typage) · `blender.md` · `meshy.md` (payant : demander) · `audio.md` · `affiches.md` · `graphify.md` · `git.md` · `fin-de-session.md`

## Skills et MCP
- Skills partagés : `.agents/skills/` — camera-systems, create-game-assets, game-feel, godot-3d-essentials, godot-animation, godot-gdscript, godot-gdscript-headless-testing, godot-nodes-scenes, godot-shaders, level-design, procedural-gen.
- MCP : `blender` (Blender ouvert + « Start MCP Server »), `godot-ai` (éditeur Godot ouvert), `meshy` (crédits). Liste : `.agents/mcp/serveurs.json`.
- Après un changement de skills/MCP : `python tools/agents/sync.py`.

## Avant de rendre la main
Suivre `.agents/procedures/fin-de-session.md` : réécrire `.agents/ETAT.md`, ajouter l'entrée de journal, mettre à jour la mémoire et les procédures si besoin.
