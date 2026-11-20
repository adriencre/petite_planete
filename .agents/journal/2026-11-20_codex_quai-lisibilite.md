# 2026-11-20 — codex — lisibilité du quai

## Demandé

Retirer les marques de maquette et rendre compréhensible la chaîne bouée, miroir et porte du hangar.

## Fait

- Retiré les étiquettes flottantes de l’île 2 et la mention « maquette grise » du menu.
- Repéré la lanterne d’essai qui alimente actuellement le miroir. Guidage proposé par les indices du quai, le premier allumage et le voyant du hangar. Raccordement à la bouée à réaliser après le choix de mise en scène.
- Aucun lancement Godot.

## Raccordement approuvé

- Source du miroir raccordée à la sortie optique du flotteur. La prise de recharge et les états sauvegardés sont conservés.
- Plaque originale dessinée en SVG, créée pour le projet et montée sur un support éditable dans l’île. Le premier allumage suit le trajet du rayon. La tache sur le bardage se déplace avec la manivelle, puis cède la place au voyant de la cellule une fois alignée.
- Fiche de l’île mise à jour. Aucun lancement Godot.
- Contrôle hors Godot sur huit positions du flotteur couvrant marée et oscillation. Le trajet incident est dégagé sur les collisions du terrain, le cran central vise la cellule et les deux autres rencontrent le bardage. SVG et diff vérifiés. Cadrage et enchaînement à essayer en jeu.

## Lancement sur Mac

- Sur demande, importé la plaque et lancé la maquette de l’île 2. Le journal Godot ne signale aucune erreur au démarrage. Partie laissée ouverte avec la sauvegarde existante. Parcours du premier branchement à vérifier.
