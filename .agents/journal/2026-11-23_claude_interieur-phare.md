# 2026-11-23 — claude — Intérieur du Phare en 1re personne

## Demandé
« corrige le phare vu en 1er personne la on rentre dans le sol de l'etage » puis « la cage d'escalier ect rien ne va dans le phare refait un interieur propre pour le joueur en 1er personne »

## Fait
- `phare_coupe.gd` : en 1re personne, plus de coupe par étage, tout le Phare reste visible (comme `batiment_coupe.gd`).
- Nouveau `tools/blender/escalier_phare.py` : colimaçon contre la face intérieure octogonale de la tour, en trois volées dans le sens horaire, avec des marches pleines sous 2,6 m et en porte-à-faux au-dessus. Collisions en rampe, planchers percés d'une trémie, garde-corps et murs de collision de la tour.
- `salle_machines_phare.py` : l'escalier en U de l'aile est supprimé et le passage dans le mur est refermé. Volée du rez au nord-est puis à l'est, avec des dalles vers son pied.
- `bureau_iris.py` : plancher à trémie, porte de la chambre dans le pan nord-est (45°). `decoration_bureau_iris.py` : banquette sous la baie du Large, porte-manteau déplacé, dalles découpées autour de la trémie.
- `sommet_phare.py` : volées 2 et 3, plancher des cartes, noyau de la salle des cartes monté jusqu'à la galerie avec un plafond, dalle de la galerie avec une trémie.
- `phare.tscn` : repères du palier, du pied de la montée et du seuil de la galerie, plus le dessin d'Aube sur la nouvelle porte.
- Rendus de contrôle en 1re personne avec un script provisoire dans le dossier scratchpad de la session (non gardé).

## Décisions de l'utilisateur
- Rebâtir l'intérieur (pas rafistoler), colimaçon contre le mur, mêmes 4 niveaux et même contenu → `ILE_02_PHARE.md` (Le Phare, de bas en haut).

## Fichiers touchés
- Voir ci-dessus + `assets/models/ile02/phare.glb`, `concept/bureau_iris_meuble/*`, `ILE_02_PHARE.md`, `.agents/ETAT.md`, `.agents/procedures/godot.md`.

## Reste à faire / questions ouvertes
- Essai en jeu : montée complète en 1re et 3e personne et en vue de dessus, porte des cartes, sortie sur la galerie à côté de la borne de la lentille.
- L'aile n'est plus qu'un volume fermé vu de l'extérieur (ses baies montrent une salle vide).
- Les étages sont peu éclairés en 1re personne : ajouter des lumières dans `phare.tscn` si c'est trop sombre.

## Suite : essai en jeu (même jour)
- Retour utilisateur : « les escaliers sont cachés derrière les écrous », « un toit empêche de monter ».
- Causes trouvées avec `tests/diag_phare.gd` (capsule 0,4 × 1,9 m) : volées trop étroites, trémie de la galerie trop petite, rampes de collision triangulées trop raides au bord intérieur, dalles qui mordaient sur la dernière marche, main courante qui fermait le palier du bureau.
- Corrigé : volée du rez au pied du mur est (départ visible à droite des engrenages), bâti et chaîne reculés vers le sud, établi raccourci, noyau des cartes réduit (1,55 m), collisions du mur verticales, trémie de la galerie élargie jusqu'à 2,80 m, emprise de la lentille à 1,50 m, rampes en 4 bandes, planchers coupés au bord exact des trémies, garde-corps arrêtés à 0,5 m sous le palier, `floor_max_angle` du robot à 50°.
- Scène : porte des cartes, registre, relevés et lunette d'Iris recalés ; plafond et haut du noyau des cartes dans la Coupe ; volée de la galerie translucide en vue de dessus au palier des cartes.
- Essai visuel : `tests/essai_phare.tscn` (variable CAPTURES_PHARE pour le dossier des captures).
