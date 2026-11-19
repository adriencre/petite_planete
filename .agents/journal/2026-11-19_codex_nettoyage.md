# 2026-11-19 — codex — nettoyage de la copie Mac

## Demandé

Nettoyer les fichiers inutiles du projet.

## Fait

- Ajouté `captures/.gdignore` et retiré les 38 fiches d’import des rendus Blender. Vérifié les références aux chemins et UID. Les 38 PNG restent à leur emplacement.
- Retiré les caches d’import de ces captures, les caches shaders de Godot et les caches Python des outils. Copie de secours locale hors du projet, environ 29 Mo.
- Conservé les scènes d’archive citées par la direction artistique et les références de conception, dont les croquis chargés par le carnet.
- Vérification statique et `git diff --check`. Aucun lancement Godot ni commit.
