# 2026-11-19 — codex — point de reprise de l’île 2

## Demandé

Retrouver où le travail sur l’île 2 s’était arrêté.

## Fait

- Recoupé le journal du Phare, le lot `4ca2d67` et l’état Git. La dernière intervention porte sur la coupe du Phare et les animations de l’échelle d’Iris. Leur rendu Godot reste à vérifier sur accord.
- Actualisé `.agents/ETAT.md` avec les éléments déjà intégrés à la chaussée, à la marée et à la maison du quai. Les changements du Phare restent locaux sur Mac. La copie Windows reste à vérifier.

## Suite

- L’utilisateur confirme que le Phare fonctionne bien et demande quel chantier prendre ensuite. Proposition de reprendre le rallumage par les trois caps, en commençant par la station du cap Est.
- L’utilisateur délègue le choix et propose Meshy. Direction retenue : station à manivelle et contrepoids, consignée dans `ILE_02_PHARE.md`. Les repères éditables de la station et du faisceau sont placés dans la maquette. Le terrain a été contrôlé dans Blender sur les deux emplacements et le rayon Est → Large de 46,7 m. Solde Meshy de 2 750 crédits vérifié. Lot de deux géométries en T2.5 proposé à 10 crédits, en attente d’accord.

## Station du cap Est

- Accord obtenu et 10 crédits dépensés pour deux géométries Meshy T2.5. Bâti : `01a1f3d5-b141-746f-9a15-7a02811548b0`. Tête : `01a1f3d5-bad2-756f-8827-e90cd41c387d`. Les GLB sources sont conservés sous `tools/blender/sources/miroir_caps/`.
- `tools/blender/miroir_caps.py` sépare la manivelle, pose les aplats, remet la surface réfléchissante à plat et ajoute le bras et son contrepoids. Les trois exports sont assemblés dans `scenes/ile02/miroir_cap.tscn`, avec une collision simple pour le bâti.
- Le cap Est réutilise le branchement au câble des lanternes. La manivelle règle un cran par pression sur E et le faisceau suit la rotation. Au bon cran, une courte mise en scène accompagne la première arrivée du faisceau sur le voyant du cap du Large. La position du miroir et le passage de la mise en scène sont sauvegardés.
- Vérifications Blender, syntaxe et références statiques, puis import Godot sans erreur. À la demande de l’utilisateur, lancement de l’île 2 sur Mac et partie laissée ouverte. L’erreur connue du menu pause au démarrage direct est réapparue. Le parcours en jeu jusqu’au miroir reste à essayer.

## Circuit des trois caps

- L’utilisateur confirme que le cap Est fonctionne et demande l’énigme complète. Les mêmes pièces Meshy équipent le Large, l’Ouest et le miroir d’essai du quai. Aucun crédit supplémentaire. Les trois trajets vers les cellules réceptrices passent le contrôle Blender, y compris devant la galerie.
- Le Phare s’allume quand les trois stations transmettent. La première mise en lumière monte dans la tour, montre l’épave et ajoute la carte au carnet. La lentille tourne ensuite en 40 secondes et sa lumière disperse les nappes de brume. Couper une station éteint le circuit.
- Ajout de la coque éditable de l’épave dans Blender et pose de la pierre-soleil rechargeable dans la flaque. L’île 2 dispose de sa propre sauvegarde et de son carnet dès l’arrivée.
- Import Godot réussi. Lancement direct de la maquette sur Mac à la demande de l’utilisateur, sans erreur de démarrage. Validation en jeu du circuit entier encore à faire.

## Réflexions du rayon unique

- L’utilisateur confirme que le circuit fonctionne en jeu et demande une vraie continuité optique. La lanterne du cap Est devient l’unique source du Phare. Les deux lanternes secondaires et les cellules intercalées sont retirées. Un impact se dessine sur le verre et le rayon repart selon la normale de la vitre. Le Phare ne reçoit de lumière que du dernier miroir.
- La page de tournée d’Iris est mise à jour et réillustrée. L’ancienne clé de lecture et les entrées du carnet déjà acquises sont conservées.
- Les quatre segments ont été contrôlés dans Blender. Essai Godot sans fenêtre autorisé : huit vérifications réussies, dont les trois désalignements, la disparition des reflets suivants, l’allumage final, l’ajout de la carte au carnet et l’extinction à la source.

## Salle des machines et couronne d’orientation

- L’utilisateur confirme le nouveau trajet de lumière et lance G4. Trois roues Blender à développante partagent le même pas. En position correcte, les dents passent le contrôle de maillage sur 32 positions sans intersection. Le sol sous les supports et la commande a aussi été vérifié.
- La scène éditable place les roues, les axes, le chariot, les repères de calage et le schéma couvert de suie. Mal montée, une roue peut retourner à son support. La réparation est sauvegardée et déverrouille la manivelle de la galerie. Les crans de la lentille suivent la géographie de la carte actuelle ; les relèvements seront reliés au lot G3.
- Cric d’atelier Meshy T2.5 proposé à 5 crédits sur les 2 740 disponibles. Appel payant en attente d’accord.
- Import Godot autorisé et réussi. Neuf contrôles réussis sans fenêtre, dont l’assemblage, la tension des 26 maillons, l’état sauvegardable et l’orientation de la lentille par la manivelle. Godot signale des ressources encore en mémoire à la fermeture du test, comme lors du test du circuit optique.
- Accord pour 5 crédits obtenu. Cric Meshy T2.5, tâche `01a1f404-c1cd-7059-8b1d-a7e26b40a72c`. Source dans `tools/blender/sources/cric_phare/cric_meshy.glb`. Le script Blender `tools/blender/cric_phare.py` applique les aplats, détache la manivelle et la sellette, puis ajoute les deux griffes. Le chariot soulève le moyeu avec la sellette et la manivelle tourne pendant la montée. Le rendu assemblé dans Blender et les références de la scène ont été vérifiés. L’import Godot du cric reste à faire sur accord.
- Import du cric terminé et île 2 lancée sur Mac à la demande de l’utilisateur. Démarrage sans erreur, partie laissée ouverte.

## Grande vue du mécanisme

- L’utilisateur trouve les roues et les axes difficiles à choisir dans la vue du jeu. La touche E près du mécanisme ouvre un panneau de face avec les trois axes, leurs empreintes, le râtelier et les boutons de rotation et de retrait. Échap ou E ferme la vue et rend les commandes au robot.
- La scène conserve le cric, les mouvements réels et les données de sauvegarde. Le dernier cran referme le panneau avant la mise en scène de la chaîne. Accord demandé pour essayer l’ouverture, les clics et la fermeture dans Godot.
- Import Godot réussi. L’ancienne fenêtre a été fermée normalement et la nouvelle maquette a été lancée sur Mac à la demande de l’utilisateur. Démarrage sans erreur.

## Cabine du ravitailleur et salle des cartes

- L’utilisateur valide le parcours de la barque à la salle des cartes et demande un vrai décor. La cabine a été modélisée dans Blender à l’échelle des Semeurs, avec bordé en cuivre patiné, hublots, chevrons brisés, bureau de quart, tiroirs, couchette, flacons et clé en laiton. Le toit et la poupe s’ouvrent en coupe. Aucun crédit Meshy engagé.
- La barque existante flotte à la hauteur réelle de la marée. L’amarrage près de l’épave exige la basse mer et le faisceau. Les points de débarquement et les collisions sont éditables. La clé et l’ouverture de la porte des cartes sont conservées dans la sauvegarde. Les relèvements illustrés se lisent en jeu et correspondent à la graduation de la lentille.
- Implants contrôlés sur le terrain, géométrie et lisibilité de la cabine vérifiées sous Blender. Références Godot et syntaxe contrôlées sans lancement. Accord demandé pour un contrôle Godot sans fenêtre.
- Modèles importés et île 2 lancée sur Mac à la demande de l’utilisateur. La fenêtre est ouverte et le démarrage n’a signalé aucune erreur.

## Salle des cartes masquée par la montée

- Les rayons lancés sous l’angle de la caméra de jeu passent par une marche ou un garde-corps de la montée vers la galerie. Le fondu réutilise la logique du bureau et cible les 73 nœuds visuels de cette volée. La proximité du centre et la profondeur derrière la porte ouverte distinguent la visite de la circulation.
- Vérifié sur trois positions dans la salle et deux sur le palier ou l’escalier. Les collisions restent dans leur groupe. Vérification du rendu Godot à faire sur demande de relance.

## Bilan des chantiers restants

- Recoupement de la fiche de l’île, de la feuille de route et de la passation. Suite proposée : la lunette d’Iris et l’ancien corps de la galerie. Les essais du panneau des engrenages, du fondu de la montée des cartes et de la chaussée restent à faire.

## Lunette d’Iris sur la galerie

- L’utilisateur lance le chantier proposé de la lunette. Le tube Blender tourne sur le socle, une vue d’oculaire s’ouvre et les flèches passent d’un cran au suivant. Le carnet conserve un croquis par vue après la transition.
- Cinq illustrations SVG originales pour les îles encore absentes du monde. Le cran de la petite maison vise la mer vide à 318°, comme la commande du Phare, et ne montre pas l’île cachée en maquette.
- Contrôles hors Godot de la syntaxe GDScript, des références et des dimensions SVG, puis inspection de la planche. Import et parcours en jeu à faire sur accord.
- Import Godot réussi, puis lancement graphique de l’île 2 sur Mac à la demande de l’utilisateur. Démarrage sans erreur, partie laissée ouverte. Manipulation des crans et consultation du carnet à vérifier en jeu.

## Inventaire des assets restants

- Comparé la maquette, le décor Blender de la maison et la fiche de l’île. Premier lot proposé : hangar, sa porte, barques retournées, bouée et échelle de marée. Pas de changement de scène.

## Chantier du quai

- Hangar de réparation créé dans Blender. Bardage bleu, socle, couverture d’ardoise, coquilles de deux barques, tréteaux, rails, établi et outils. Toit et murs hauts s’effacent à l’entrée. Rampe calée sur les mesures du terrain.
- Grappin et toile validés pour 10 crédits. Les deux modèles Meshy T2.5 sont intégrés après remise à l’échelle et aplats. Sources et identifiants dans le manifeste du lot.
- Le capteur de la façade est reçoit le miroir du port. Premier alignement filmé, deux vantaux coulissants et état sauvegardé. Jauge à traits peints et bouée liée à la marée. La recharge de la bouée depuis la barque reste à implémenter.
- Deux rendus Blender et neuf contrôles Godot autorisés. Faisceau clair, seuil, ouverture, état sauvegardable, coupe et flotteur vérifiés.
- Godot signale deux ressources encore en mémoire à la fermeture de l’essai headless. Import réussi, démarrage graphique sans erreur et partie laissée ouverte.

## Recharge à la bouée

- Prise physique côté quai. Depuis la barque, E immobilise le bateau, débranche le câble de proue et le raccorde à la bouée. Premier allumage mis en scène, flux inversé vers le robot et retour du câble à la proue. La bouée reste allumée après sauvegarde et peut rendre la batterie pleine plusieurs fois.
- La scène existante de la barque garde ses commandes de navigation et d’amarrage. Syntaxe et références contrôlées hors moteur. Accord demandé pour l’essai et la relance.

## Passation vers le PC fixe

- L’utilisateur demande de pousser tout le travail local pour reprendre sur le PC fixe. Le lot inclut scènes, scripts, modèles, sources Blender, concepts, captures et notes de passation.
- La recharge à la bouée reste à essayer en jeu. Aucun lancement Godot pour cette passation.
