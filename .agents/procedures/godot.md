# Godot — procédures et pièges

## Lancer Godot en ligne de commande
Godot n'est pas dans le PATH :
```
"C:\Users\adrie\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe"
```
- **Toujours demander à l'utilisateur avant** de lancer le jeu ou un test, même headless (voir mémoire `ask-before-launching`). Regrouper les changements, demander une fois, ne pas relancer en boucle.
- Vérifier d'abord la compilation : `<godot> --headless --path . --import` (attrape les erreurs de parsing).
- Test de diagnostic : `<godot> --headless --path . -s res://tests/diag_xxx.gd` (scripts `extends SceneTree`, voir `tests/diag_*.gd`).
- Skills utiles : `godot-gdscript`, `godot-gdscript-headless-testing`, `godot-nodes-scenes`, `godot-3d-essentials`, `godot-shaders`, `godot-animation`.

## Style de code du projet
- Scènes `.tscn` / ressources `.tres` éditables dans l'éditeur, scripts courts, `@tool` quand le contenu généré doit se voir dans l'éditeur. Pas un gros script qui génère tout.
- Noms, commentaires et textes **en français** (`## commentaire de doc` en tête de fonction/fichier).
- **« inferred from Variant » est une erreur** dans ce projet : jamais `var x := <expr>` si l'expression touche une valeur non typée → `var x: bool = …`.
- Les scripts de test (`-s`) compilent avant les autoloads : ne pas nommer de `class_name` qui utilisent un autoload ; `load()` le script à l'exécution.
- Autoloads actuels : `Reglages`, `Sauvegarde`, `MenuPause`, `_mcp_game_helper` (voir project.godot).

## Éditeur ouvert pendant qu'on modifie les fichiers
- L'éditeur garde `project.godot` en mémoire : après une modif sur disque (actions, `[shader_globals]`, scène principale), l'utilisateur doit faire **Projet > Recharger le projet actuel**, sinon l'éditeur peut réécrire sa vieille copie. Avec le MCP godot-ai, préférer `project_manage(settings_set / set_main_scene)`.
- Nouveaux scripts `class_name` écrits de l'extérieur : l'éditeur peut ne pas les enregistrer (« Could not find type X »). Correctif : arrêter le jeu, `filesystem_manage(op="reimport", paths=[...])` puis `filesystem_manage(op="scan")`, vérifier `.godot/global_script_class_cache.cfg`.
- Une scène ouverte dans l'éditeur peut être ré-enregistrée après suppression. Pour déplacer/archiver des scènes : demander à l'utilisateur de fermer les onglets (ou l'éditeur), puis `git mv` + `--import` headless.
- **Nouvelles `@export` d'un script `@tool` modifié de l'extérieur** : après le rechargement à chaud, l'éditeur peut les laisser à `null` (pas à leur valeur par défaut) sur les nœuds déjà ouverts → le script calcule avec `null` (ex. 0 couche de brume). Les régler explicitement via MCP (`node_set_property`) ou rouvrir la scène. Constaté le 2026-11-19 sur `maquette.gd`.
- **Script ouvert dans un onglet de l'éditeur** : une modif faite sur disque peut être écrasée quand l'éditeur ré-enregistre son tampon (vu le 2026-11-19 sur `maree_estran.gd`, avec une frappe parasite en plus). Pour un script ouvert, éditer avec `script_patch` (MCP godot-ai), qui passe par l'éditeur et vérifie la syntaxe.
- Pièges GDScript : `bool(null)` plante (« Nonexistent 'bool' constructor ») ; `joueur.embarque` est un nœud (la barque) ou `null`, pas un booléen.
- **Ne pas fermer deux onglets de scène à la suite via MCP** (`scene_manage(op="close")`) : crash de l'éditeur (0xc0000005) le 2026-11-16.

## MCP godot-ai
- Serveur stdio `godot-ai` (voir `.agents/mcp/serveurs.json`), il faut **l'éditeur Godot ouvert** avec le plugin actif. Sans éditeur : « connection timed out », c'est normal.
- Le bouton « Configure » du dock n'enregistre pas le serveur : la config est faite à la main par `tools/agents/sync.py`.
