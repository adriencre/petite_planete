# 2026-11-22 — claude — G2 : la rue des Trois-Soleils (Blender)

## Demandé
« on attaque G2, pose-moi tes questions », puis « commence par Blender, attention à prendre le temps, je veux des rendus pro ».

## Fait
- Point de reprise sur la Colonie : G1, le Coin noir et la ville basse sont posés. G2, G3 et G4 ne sont pas commencés. La liste à tester compte environ 35 points sur l'île 3.
- Nouveau `tools/blender/ville_haute.py`, exécuté par `colonie_du_lagon.py` comme la grotte :
  - **parvis** : massif de pierre mis à niveau, dallage, 9 rosaces, caniveaux et gaines de cuivre jusqu'au pupitre, muret, perron avec rampe `-colonly`, deux projecteurs ;
  - **maison commune** au secteur 14 : façade à fronton, fenêtres murées, salle du conseil, bureau d'Ysolde, beffroi. Les pièces animables ont leur origine sur leur pivot : `Porte_commune_gauche/droite`, `Cran_commune_1..3`, `Verrou_commune`, `Voyant_commune_1..9` ;
  - **ville haute habillée** (secteurs 11 à 16, de plus en plus marqué) : lanternes de façade, fenêtres murées, projecteurs, câbles pendus entre les maisons ;
  - colonnes d'affichage (secteurs 11 et 13), cadre de l'affiche 2, panneau du parvis, stèle, **borne de recharge** au bout du ponton ;
  - repères Godot dans `tools/blender/sources/ville_haute_reperes.txt`.
- `colonie_du_lagon.py` : la friche ne pousse plus sur le parvis (`hors_friche`). Le secteur 12 devient « Maison_aux_projecteurs » avec un logis côté lagon. Pas de lampadaire côté terre au secteur 14. Les façades de la ville haute sont relevées pour l'habillage.
- `tools/blender/rendu_ville_haute.py` : 9 vues de présentation avec les vraies lanternes-tulipes, dont les 3 du motif allumées. Sorties dans `concept/ile_03/ville_haute_*.png`.
- GLB et .blend régénérés en ligne de commande (le MCP n'était pas lancé au début). **Pas de réimport Godot, pas de lancement.**

## Décisions de l'utilisateur
- Parvis carré, plan d'éclairage à part déchiré en 3, tableau à 9 voyants et serrure à crans, salle + bureau, borne au quai, morceaux le long du chemin, secteur 14 renommé, ville haute habillée en entier (→ ILE_03_COLONIE.md § G2).
- Pris par Claude et signalé : maison commune déplacée du secteur 12 au 14 (ordre de la descente depuis la crête).

## Fichiers touchés
- tools/blender/ville_haute.py (nouveau), tools/blender/rendu_ville_haute.py (nouveau), tools/blender/colonie_du_lagon.py, tools/blender/sources/ville_haute_reperes.txt
- assets/models/ile03/colonie_du_lagon.glb, concept/ile_03/colonie_du_lagon.{blend,png}, concept/ile_03/ville_haute_*.png
- ILE_03_COLONIE.md

## Reste à faire / questions ouvertes
- Documents dessinés (`tools/affiches/`) : 3 morceaux du plan, affiches 1 à 5, ordres d'Ysolde, lettres de Tavin, plan de l'archipel.
- Godot : réimporter le GLB, 9 `lanterne_fleur` aux repères, script de porte (voyants, crans, verrou, vantaux), documents, borne, `_amenager("commune", …)` dans `batiments_fantomes.gd`. Les objets `Maison_*_peur` forment un bâtiment à part de leur maison.
- Les maisons « adresses » de la ville haute (verriers 11, projecteurs 12, palier 13) sont encore les anciennes boîtes de `maison()`.

## Suite : documents et Godot (« arrête le jeu et fais tout d'un coup »)
- 11 documents dessinés et rendus (rendre.py). Le plan d'éclairage est une seule affiche découpée en 3 morceaux par `plan_eclairage.js`.
- Godot : parvis (9 `lanterne_fleur`, porte animée : voyants, crans, verrou, vantaux), borne (pierre_soleil.gd + Cristal), 10 documents `page_lisible`, coupe de visite, effet fantôme. Repères corrigés (normales du panneau et du cadre mural décalées de 90°). Cœur de la borne retiré du GLB.
- Correctif `lanterne_fleur.gd` : la plus proche seulement en vue de dessus.
- GLB réimporté via MCP, Colonie lancée sans erreur. Essai complet à faire par l'utilisateur.

## Retour du premier essai et corrections
- Retour : bureau impraticable (table au milieu, salle trop petite, il faut grimper), papiers invisibles, caméra fixe qui les cache.
- Décisions : caméra « depuis le lagon » qui suit l'anneau, appel « halo + rayon » pour les papiers non lus.
- Fait : maison commune réaménagée (table contre le mur nord, bureau de 7 × 3,2 m, porte de 1,8 m), ensemble reculé (R_PARVIS 42,8). `page_lisible.gd` reçoit `appel_fort`/`hauteur_rayon`. Nouveau `scripts/camera_anneau.gd` (nœud CameraAnneau). Le générateur `tools/godot/ville_haute_scenes.py` est ré-exécutable. Mémoire : `indices-visibles.md`.

## Caméra refaite
- Retour : « la rotation de la caméra est horrible ». Cause : elle tournait en continu avec la position autour du lagon, et les commandes suivaient. Les maisons côté lagon passaient en fantôme sans arrêt, et les coupes de la ville basse cassaient.
- Remplacée par des zones de cadrage : crête (-11°), ville haute nord (-70°), ville haute sud (-119°), parvis (-102°, 12,5 m, 52°), bureau (-12°). Ailleurs, le cadrage de la scène (45°). Transition de 2,6 s après 0,45 s dans la nouvelle zone. `joueur.gd` : les touches tenues gardent leur sens. `camera_anneau.gd` supprimé.

## Deuxième essai de la caméra et morceaux déplacés
- Retour : « la caméra sur la deuxième partie de l'île est horrible, bloquée derrière les maisons » ; « cache les 3 bouts du code dans des maisons ouvertes, sur le dos des afficheurs on ne les voit pas ».
- Caméra : zones `ZoneRue06` à `ZoneRue16`, une par secteur, dans l'axe de la rue (vers le secteur précédent), 10,5 m et 56°. Les secteurs 6 et 7 font la transition depuis 45°. Parvis et bureau inchangés. Logis du lagon du secteur 14 retiré.
- Morceaux : A sur la table du quai, B sur le comptoir des couturières, C sur le bureau du maître (`morceaux_du_plan()` dans ville_haute.py, pose « plat » dans le générateur).

## Morceaux recollés au carnet
- Retour : « chaque bout est sur une page ». `carnet.gd` reçoit `noter_morceau()` et `_recoller()` : les PNG des morceaux, à la taille de la feuille entière, sont superposés sur une seule entrée. La sauvegarde garde `assemblage` et `morceaux`. `page_lisible.gd` reçoit `assemblage` et `titre_assemblage`, et ouvre le carnet sur la page recollée à la fermeture.
