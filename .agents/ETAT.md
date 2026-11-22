# État du projet — passation entre agents

> Mis à jour le **2026-11-22** par **claude** (PC fixe).

## En cours : l'école de la Colonie (22 novembre)

- La boutique des couturières, l'école, l'ancien corps de l'école et la maison d'Aube sont décrits dans ILE_03_COLONIE.md. Le travail du 20 au soir n'est **pas commité**.
- La classe est habillée dans Blender : affaires abandonnées, banc renversé, pupitre d'Aube et pièce séparée `Dessin_escalier`. GLB régénéré, **pas encore réimporté dans Godot**.
- Interactions de l'école câblées dans `scenes/ile_03_maquette.tscn` (GLB réimporté via MCP) : `TableauComptine` (page_lisible, image `tableau_comptine.png` posée sur l'ardoise, lueur 0,3), `DessinEscalier` (à ramasser sur le pupitre d'Aube), `Carnet` et `Guidage` ajoutés à l'île 3. Cinématique de l'ancien corps : `scripts/souvenir_ancien_corps.gd` (nœud `Souvenir` dans `scenes/ile03/ancien_corps_ecole.tscn`), avec `carnet.ouvrir_sur_image()`.
- **Pas encore essayé en jeu.** À vérifier : orientation et lisibilité de l'image du tableau et du dessin, cadrage de la cinématique.
- **Piège** : la sauvegarde ne couvre que l'île 1 et l'île 2 (`Sauvegarde.en_partie`). Le carnet de la Colonie lit celui de l'île 1, donc il n'a pas le dessin du Phare : la cinématique saute alors l'ouverture du carnet. À régler avec le raccord des îles.
- La Colonie est dans le menu de développement (`ecran_titre.gd`, « Île 3 — La Colonie »). Pause active via `Sauvegarde.en_jeu()`, mais **rien n'est sauvegardé** sur l'île 3 (`ILES_SANS_SAUVEGARDE`) : la cinématique de l'ancien corps se rejoue à chaque visite.
- Ensuite : la maison d'Aube (le script Blender a déjà une fonction `maison_aube`).

## Menu principal

- Le premier diorama du titre a été rejeté. L’accueil utilise maintenant le vrai décor 3D du Réveil, partagé avec l’île jouable, avec une caméra et un éclairage dédiés. La pause et les réglages reprennent le thème du menu.
- Nouvelle partie, reprise, accès de développement et retour au titre passent par un chargement en arrière-plan. La suppression de l’ancienne partie intervient après acceptation du changement de scène par Godot.
- Vérifications statiques effectuées. La version avec le vrai décor a démarré sur Mac sans erreur au journal. Le jeu est ouvert à l’accueil. Le retour visuel et le parcours de chargement restent à vérifier.

## Colonie — reconstruction du lagon

- Nouvelle implantation indépendante dans `tools/blender/colonie_du_lagon.py`. Source Blender et rendu dans `concept/ile_03/colonie_du_lagon.*`. La scène de l’île charge désormais le nouveau GLB avec collisions par suffixe Godot.
- Arrivée intime au quai sud, ville basse à l’ouest, ville haute à l’est, trois verrières au nord. Les habitations sont des extérieurs. Marée, parcours secret, jardin réservé et interactions restent à développer. Nouveau GLB importé sur Mac et Colonie lancée directement sur demande, sans erreur au démarrage. Partie laissée ouverte. Collisions et parcours à vérifier.

Les 17 habitations de décor utilisent les quatre modèles fermés éditables dans Blender, avec des maillages partagés par variante. Pignon et terrasse en ville basse, contreforts et balcon en ville haute. Sept habitations de l’enquête, école, maison commune et serres préservées. GLB réimporté avec les collisions des murs et des socles. Colonie lancée sur demande et laissée ouverte sur Mac, sans erreur au démarrage. Caméra de la Colonie alignée sur celle du Phare (distance 9 m, angle 40°). Partie relancée avec ce cadrage et laissée ouverte sur Mac, sans erreur au démarrage. Cadrage et circulation à vérifier en jouant.

Les rues et les talus de la Colonie sont désormais en friche. Touffes à facettes, mousse, pavés disjoints et vergers moins uniformes. Le décor Blender est réexporté et réimporté dans Godot sans erreur. La partie ouverte précède cette modification. La nouvelle végétation sera chargée à la prochaine ouverture de la Colonie.

Le quai et sa maison forment le premier ensemble aménagé. Maison déplacée côté lagon, porte face à l’arrivée. Ponton raccordé au seuil dans son axe par une passerelle, carillon et échelle sculptés, première valise « Nef » et intérieur meublé. La scène prévoit le fondu du toit et du haut des murs à l’entrée. Réimport et essai en jeu à faire sur accord. Le déclenchement du carillon par la marée et l’écluse restent à raccorder.

Le deuxième foyer, la maison des couturières, est aménagé en atelier visitable. Les deux maisons sont réimportées et la Colonie est ouverte au quai. Le fondu des toits et la traversée des seuils restent à essayer en jouant.

Extérieurs du quai et des couturières repris dans Blender. Toit cintré et oculus au quai, toiture asymétrique à claire-voie et auvent de toile chez les couturières.

Les deux premiers foyers ont leur mobilier et leurs objets modélisés dans Blender. Poêle, carte et matériel du port au quai. Mannequin, outils et tissus chez les couturières.

## Où on en est

- Les sept îles sont documentées. La DA v6 prévoit une vue de dessus, du low-poly à facettes et des pastels lumineux. L’île 1 est jouable en maquette.
- L’île 2 se reprend dans scenes/ile_02_maquette.tscn. Terrain Blender, brume, marée, maison du quai, hangar, recharge à la bouée, chaussée, jardin et banc d’Iris, grottes et crypte sont intégrés. L’utilisateur a terminé le tour de la maison et de la recharge sur le PC fixe.
- Le Phare comprend le circuit des trois caps, les engrenages, la barque vers le ravitailleur, la salle des cartes, la lunette à cinq crans et la chambre d’Iris avec son échelle. Le parcours principal a été vérifié par étapes jusqu’à la graduation 129°. Le parcours continu reste à essayer.
- Après réparation des engrenages, la commande de la lentille est accessible depuis les trois côtés de la galerie. La touche E privilégie l’instrument le plus proche près de la lunette d’Iris. Essai en jeu en attente d’accord.
- Les derniers retours intègrent le halo et la touche E pour les objets à prendre, le fondu extérieur du Phare quand il masque le robot et l’indication de la basse mer pour les grottes. Voir le journal du 20 novembre.

- Le dessin d’Aube dans la maison du quai et le journal de quart de l’épave sont consultables et copiés au carnet. Le corps du Large est replacé au bord du gué et celui de la galerie vise le cap 318°. Les deux documents ont été importés et l’île a démarré sans erreur sur Mac. Les interactions restent à essayer.
- Les étiquettes flottantes sont retirées et le nom du menu est corrigé. La bouée alimente le miroir du hangar. Plaque au ponton, premier allumage filmé et impact sur le mur raccordés. La lisibilité du parcours reste à essayer en jeu sur accord.

- Ambiance du Phare : le trajet A et le rallumage A sont validés. Ébauche du motif au piano et aux cordes montée sur le rallumage A. Écoute musicale à valider avant l’intégration. Sources dans `tools/audio/ile_02/ECOUTES.md`.

## Reprise sur Mac

- Les travaux sur le menu, le Phare et la Colonie sont regroupés sur main pour publication depuis le Mac. L’ancienne sauvegarde Git du Phare est disponible sur la branche sauvegarde-phare-pc.
- Les nouvelles ressources sont importées sur le Mac. La maquette de l’île 2 avec le nouveau circuit du hangar est ouverte à la demande de l’utilisateur, sans erreur au démarrage.
- Vérifier en jeu le guidage, le fondu du Phare, le banc et la lisibilité des accès et des indices. La préférence de fenêtre de marée reste à confirmer. F8 accélère le cycle.
- Le parcours local est assemblé. Restent la validation sur une partie continue, l’habillage sonore propre à l’île et les raccords à l’archipel (navigation, Quarantaine, pleine lune). L’Écoute dépend du chantier ombre reporté. Voir le journal d’inventaire.
- Demander avant tout lancement ou test Godot. Une partie lancée depuis l’éditeur bloque les écritures MCP. Les caches Godot se régénèrent localement et captures/ est exclu de l’import.
- Après une modification de la carte, régénérer le terrain avec tools/blender/terrain_ile_02.py puis réimporter le GLB. Le MCP Blender du Mac pilotait le PC Windows lors de la session précédente.
