# 2026-11-20 — codex — menu principal

## Demandé

Un menu de jeu professionnel et de vrais chargements.

## Fait

- Repéré la scène titre, les réglages, la pause et le changement de scène synchrone via Sauvegarde.
- Préparé la proposition visuelle et fonctionnelle. Aucun code ni scène modifiés, aucun lancement Godot.

## Direction approuvée et intégration

- Créé le diorama 3D de l’accueil à l’aube, avec la lanterne et le berceau du jeu, une caméra lente et un thème commun au titre, à la pause et aux réglages.
- Remplacé les changements de scène synchrones depuis les menus par un chargement en arrière-plan avec progression, fondus et récupération en cas d’échec. La nouvelle partie ne réinitialise la sauvegarde qu’après acceptation du changement de scène.
- Vérifié statiquement les références du projet. Aucun lancement Godot.

## Lancement sur Mac

- Jeu lancé sur demande sur le nouvel accueil. Démarrage sans erreur dans le journal. Le jeu reste ouvert pour essayer les menus et les transitions.

## Retour sur le décor du titre

- La maquette simplifiée a été rejetée. L’accueil référence désormais le même décor que l’île 1, avec ses falaises, sa cascade, sa végétation et ses bâtiments.
- Le titre utilise une caméra et une lumière dédiées. Les interactions et la restauration de sauvegarde des lanternes restent réservées à l’île jouable.
- Références vérifiées hors moteur. La nouvelle version attend un lancement pour vérifier le cadrage et les performances.

- Nouvelle version relancée sur Mac après accord. Démarrage sans erreur au journal, jeu laissé ouvert à l’accueil.
