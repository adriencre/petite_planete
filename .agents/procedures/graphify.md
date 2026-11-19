# graphify — graphe de connaissances du code

Le projet a un graphe dans `graphify-out/` (ignoré par git). Exécutable : `graphify` (`C:/Users/adrie/.local/bin/graphify.EXE`).

Règles (valables pour tous les agents) :
- Quand `graphify-out/graph.json` existe, lancer `graphify query "<question>"` **avant** le premier grep, recherche ou lecture de fichier source pour une question sur le code. Mettre cette règle dans le prompt de tout sous-agent qui explore le code.
- Lire les fichiers bruts seulement pour les lignes que le graphe (ou une lecture précédente) a déjà localisées.
- `graphify path "<A>" "<B>"` pour les relations, `graphify explain "<concept>"` pour un concept, `graphify section "<titre>"` pour le texte d'une section Markdown sans ouvrir le .md.
- Si `graphify-out/wiki/index.md` existe, l'utiliser pour naviguer.
- `graphify-out/GRAPH_REPORT.md` : seulement pour une revue d'architecture générale.

Mise à jour :
- graphify n'a pas d'extracteur GDScript/.tscn : **`python tools/graphify_godot.py`** les ajoute (fonctions, signaux, commentaires `##`, appels, preloads, liens scène → script/scène/shader/modèle). Pas de coût d'API.
- Après avoir modifié du code ou des scènes : `python tools/graphify_godot.py`. **Jamais `graphify update .` seul** (ça supprime tous les nœuds Godot).
- Ce qui est ignoré : `.graphifyignore` (addons/, assets/, .claude/, .agents/skills/, scenes/archive/…).

Côté Claude Code, des hooks (`.claude/settings.json`) rappellent cette règle automatiquement. Côté Codex il n'y en a pas : appliquer la règle soi-même.
