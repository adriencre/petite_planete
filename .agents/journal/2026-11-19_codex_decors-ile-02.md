# 2026-11-19 — codex — décors de l’île 2

## Demandé

Finir les bâtiments et les assets de l’île 2 avant de brancher les interactions.

## Fait

- Ordre de production consigné dans la fiche de l’île et dans la passation.
- Inventaire recoupé avec la maquette et la maison du quai. Les grottes et la crypte sont le principal chantier de décor. L’ancien corps du Large a déjà un modèle placé, celui de la chaussée est provisoire et celui de la galerie reste à poser.
- Premier lot proposé : grottes et crypte dans Blender, avec l’entrée sur l’estran et la ligne du berceau. Aucun lancement Godot.

## Grottes et crypte du berceau

- L’utilisateur lance ce lot et demande un rendu détaillé. Modélisation originale dans Blender 5.3, sans génération payante. Portail, galerie, crypte et voûtes sont exportés séparément depuis une origine commune au seuil. Les quatre GLB sont assemblés dans une scène indépendante et les éléments de coupe y sont masqués par défaut.
- Fichier Blender éditable dans `tools/blender/sources/grottes_crypte/`, générateur dans `tools/blender/grottes_crypte.py` et trois cadrages dans `captures/grottes_crypte/`. Rendus inspectés, dimensions et en-têtes GLB contrôlés.
- Reste le percement de la falaise, le placement sur l’estran, les collisions, la logique de marée et la validation en jeu sur accord.

## Placement dans l’île

- L’utilisateur demande de placer les grottes dans l’île. L’instance remplace le bloc provisoire sur l’estran, à gauche de l’escalier en arrivant du quai. Ouverture de la falaise et du caniveau dans le générateur de terrain. Couverture séparée, collisions éditables et fondu réutilisé depuis la maison du quai. Deux cadrages en situation dans `captures/grottes_crypte/`.
- Contrôle Godot 4.7.2 sans fenêtre sur accord, dans un projet temporaire. Le premier passage détectait une marche au raccord du sol. Raccord corrigé, puis 153 positions de sol et de capsule validées. La couverture s’efface et revient, et le plateau garde sa collision pendant la coupe.
- La partie existante et ses sauvegardes n’ont pas été touchées. Restent la validation visuelle dans la maquette complète et la logique de marée propre à l’accès.
- Les caches de l’éditeur ont été actualisés. Le terrain est déclaré valide avec une empreinte à jour, malgré deux diagnostics `vertices.is_empty()` signalés pendant sa réimportation. Le contrôle de géométrie Blender reste positif après le filtrage des triangles dégénérés.

## Chaussée et anciens corps

- L’utilisateur valide ce lot. Dalles de calcaire, sédiments, varech, cercles autour des trois balises et pente vers le quai modélisés dans Blender par `tools/blender/chaussee_anciens_corps.py`. Maillage de collision séparé et scène de l’île mise à jour.
- Le corps de l’estran réutilise `ancien_corps.glb`, avec un modèle de varech positionné sur les contacts du poignet, du corps et des pieds. Le corps de la galerie reprend le robot d’origine figé dans son clip assis et posé sur une assise de pierre. Les deux ont une collision simple. Aucun crédit Meshy.
- Sol vérifié sur 336 sondes et assise contrôlée dans les collisions du phare sous Blender. Trois rendus dans `captures/chaussee_anciens_corps/`. La partie existante reste ouverte et l’essai Godot est à faire sur accord.

## Jardin mort et banc d’Iris

- L’utilisateur lance le jardin. Banc à lames sur socles de calcaire, arbre rose mort, trois bacs terre sèche, arrosoir et bordures modélisés dans Blender par `tools/blender/jardin_iris.py`. Aucun crédit Meshy.
- La scène `scenes/ile02/jardin_iris.tscn` remplace les volumes provisoires dans la maquette. Le repère de carte est déplacé du niveau supérieur vers le rebord nord-ouest. Le banc et le repère de vue suivent la direction 318° de la lunette d’Iris. Le geste de s’asseoir reste à brancher.
- Rendus Blender en situation dans `captures/jardin_iris/`. Appuis contrôlés, 39 points de sol sur le passage vers le cap Ouest et trois rayons à différents angles de plongée dégagés au cap 318°. Validation en jeu sur accord. Prochain lot de décors : les finitions de la maison du quai.

## Suite proposée

- Terminer les accessoires de la maison du quai. Regrouper ensuite les vérifications en jeu de l’île 2 sur accord, en commençant par la recharge à la bouée. La logique de marée des grottes reste à raccorder après les décors.

## Maison du quai

- L’utilisateur demande un bâtiment plus travaillé et valide 15 crédits pour trois géométries Meshy T2.5. Poêle avec bouilloire, deux cirés et paire de bottes intégrés et mis en couleur dans Blender. Sources et identifiants dans `tools/blender/sources/maison_quai/`.
- Médaillon émaillé au pignon, auvent au seuil, volets et appui de la grande fenêtre détaillés, cheminée, banc et caisses repris. GLB réexporté et trois cadrages dans `captures/maison_quai/`.
- Godot 4.7.2 sans fenêtre sur accord (copie temporaire) : import, entrée avec la capsule du robot sans saut, disparition du toit et du haut du mur, collision du mur pendant le fondu, retour à la sortie et repères des interactions vérifiés. Rendu de la maquette complète à vérifier.

## Vérification en jeu

- Tour de vérification de la maison et de la recharge à la bouée terminé selon le retour utilisateur. Prochain chantier proposé : raccorder l’accès des grottes en barque à la marée et rendre lisible la plaque de la ligne du berceau.

## Raccourci des grottes

- L’utilisateur valide le passage en barque avec une sortie de service utilisable à haute mer. Borne, repères d’accostage et seuil raccordés à la marée. Galerie et crypte abritées. La plaque reprend le texte canonique et apparaît dans le carnet après lecture.
- Puits percé dans le terrain Blender. Échelle éditable dans la scène, avec la traversée animée du Phare et deux paliers. Les protections latérales bordent le plateau.
- Godot 4.7.2 sans fenêtre sur accord, dans une copie de l’île 2. Accostage à basse mer, arrivée de la barque, chemin jusqu’à la crypte sans saut, fermeture de l’accès maritime et crypte au sec à haute mer, lecture et ajout au carnet, montée jusqu’au sol du plateau vérifiés. Zéro échec. Le contrôle visuel en jeu reste à faire.

## Interaction du banc d’Iris

- Le robot s’assoit avec E depuis le sentier. Le clip assis existant est calé sur le bord du banc. La première vue se pose au cap 318° et son état est sauvegardable. E ou Échap rend les commandes.
- Appui vérifié par cinq sondes Blender et pose contrôlée sur un rendu. Références Godot valides. Contrôle sans fenêtre préparé dans la copie temporaire et en attente d’accord.

## Contrôle de la chaîne principale

- Test autorisé dans une copie temporaire de la maquette complète, Godot 4.7.2 sans fenêtre. Partie fraîche. Le diagnostic repositionne joueur et barque entre les lieux, fixe les phases de marée et déclenche les interactions E et les boutons du panneau dans l’ordre.
- Zéro échec : lanterne du cap Est, trois reflets, révélation de l’épave et carte du carnet, accès à basse mer seulement après rallumage, embarquement, accostage, clé, retour au quai, ouverture des cartes, relevés au carnet, engrenages et graduation Colonie à 129°.
- Les trois documents illustrés ont été relus. Ils relient le cap Est au Large, le billet à la cabine et les relèvements aux graduations. Test sans continuité de déplacement. Repérage des lieux et des indices depuis la caméra du jeu à vérifier sur une partie de découverte. Aucun changement de code ou de scène.

## Lancement sur le PC fixe

- Île 2 lancée directement à la demande de l’utilisateur. Godot 4.7.2, démarrage Vulkan Forward+ sans erreur dans le journal de lancement. Partie laissée ouverte.
