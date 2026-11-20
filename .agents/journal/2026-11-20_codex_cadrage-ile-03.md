# 2026-11-20 — codex — cadrage de la Colonie

## Demandé
Proposer par quoi commencer l'île 3.

## Fait
- Relu la fiche de la Colonie, la DA et les liens avec le Phare. Proposition de partir du plan en lagon fermé et de maqueter le trajet du quai à l'école, puis de développer la piste d'Aube jusqu'à sa chambre.
- Aucun changement de scène ni lancement Godot.

## Reste à faire / questions ouvertes
- Discuter du premier parcours et de l'endroit où le joueur aperçoit le vieux port. Le tracé du canal vers le jardin du haut reste ouvert.

## Maquette complète

- Sur demande, créé `scenes/ile_03_maquette.tscn` d'après la grille de la variante C, avec les volumes nommés, les accès provisoires, les collisions et le robot. La rampe du canal longe le flanc est.
- Contrôlé les références, la hiérarchie et les neuf lanternes hors moteur. Graphe régénéré. Aucun lancement Godot.
- À vérifier après accord : lecture du lagon et des ruines, passages aux raccords des rampes, retour de chaque quartier et réapparition après une chute en mer.

## Lancement sur Mac

- À la demande de l'utilisateur, scène de l'île 3 lancée directement avec Godot 4.7.2. Aucune erreur au démarrage. Partie laissée ouverte.

## Terrain à habiller

- À la demande de l'utilisateur, reprise du terrain de toute l'île avant ajout des bâtiments, du mobilier et de la végétation. Relief par strates, rues et places, quai, lagon et fondations. Blocs de décor remplacés par des emprises et des repères.
- Rampes raccordées avec paliers et canal est divisé en tronçons. Contrôles statiques des références, repères et collisions. Aucun lancement de cette version.

- Version terrain relancée sur demande avec Godot 4.7.2. Démarrage sans erreur, partie laissée ouverte.

## Retour sur le terrain

- L'utilisateur juge le terrain en primitives trop cheap et demande le même niveau de finition du relief sous Blender que pour le Phare. La carte entière est à traiter avant les maisons, le mobilier et les plantes.
- Méthode du Phare repérée dans `tools/blender/terrain_ile_02.py`. Proposition de reprendre les falaises à facettes, les strates et les sols modelés, en gardant le plan du lagon fermé.

## Reprise Blender

- Sur « go », modelé toute la Colonie dans Blender 5.3 d'après les emprises de la scène : falaises stratifiées, terrasses à facettes, dallages, digue et vestiges engloutis. Conservé les collisions Godot et les repères pour l'habillage.
- Modèle GLB instancié dans la scène. Fichier éditable et vues du quai et de l'île entière dans `concept/ile_03/`.
- Aucune relance Godot. Les raccords des rampes et la lecture du lagon restent à essayer en jeu.

## Présentation de l’île

- Relu la fiche de la Colonie pour résumer le lieu, le rôle d’Aube dans l’enquête et l’état de la maquette.

## Programme des habitations validé

- Sept habitations visitables très détaillées, dont la maison d’Aube, et de nombreuses habitations fermées. Décision inscrite dans la fiche de la Colonie.

## Concept en vue de dessus

- Image générée avec ImageGen à partir du rendu Blender du terrain et du plan de la Colonie. Conservée dans `concept/ile_03/colonie_vue_du_haut.png`.

## Finition du terrain sur la référence du Phare

- Sur accord, repris le relief de toute la Colonie dans le générateur Blender : blocs de roche chanfreinés, éboulis, herbe rase, plaques de lichen et dalles en relief. Emprises et collisions Godot conservées.
- GLB, fichier Blender et rendus du quai, d’ensemble et de dessus régénérés. Vérification en jeu après accord.

- Sur demande, GLB réimporté dans Godot 4.7.2, puis Colonie lancée directement. Démarrage sans erreur et partie laissée ouverte.

## Reconstruction des pourtours

- Sur accord, reconstruit les arêtes des terrasses et le profil des falaises avec des strates continues, des pieds évasés et des points fixes autour des rues pavées et des accès. GLB contrôlé et graphe régénéré. Les collisions existantes sont conservées. Vérification en jeu après accord.
- Sur demande, ancienne partie fermée, nouveau GLB réimporté et Colonie relancée sur Mac. Démarrage sans erreur.

## Implantation du quartier du quai

- Sur choix de l’étape 1, instancié une scène éditable avec quatre maisons fermées, les volumes de l’école et de la maison d’Aube, une cour et un repère de vue sur le lagon. Implantation sur la rive ouest d’après les emprises existantes. Contrôle statique effectué. Vérification en jeu sur accord.
- Sur accord, relancé Godot. Corrigé la syntaxe de la rugosité des matériaux après une erreur de chargement. Relance sans erreur et contrôle visuel de la rue et du lagon. Partie laissée ouverte.

## Implantation du bâti sur toute l’île

- Sur demande, étendu les volumes éditables aux quais, aux deux quartiers, à la crête et au vieux port. Quatre habitations prévues pour la visite en ville basse, dont celle d’Aube, et trois en ville haute. Implanté aussi la maison commune, les deux serres et un abri au jardin. Les intérieurs restent à construire. Contrôle statique passé.
- Sur demande, relancé la Colonie avec le bâti de toute l’île. Démarrage sans erreur, partie laissée ouverte.
- Sur signalement de bâtiments flottants ou pris dans la roche, mesuré les appuis par rayons verticaux dans Godot sur le maillage Blender. Replacé les deux rangées concernées et les maisons isolées. Contrôle final : 43 bâtiments, 49 points par emprise, aucun écart au seuil du diagnostic.
- Sur demande, relancé la Colonie avec les positions corrigées et laissé la partie ouverte.

## Références visuelles des maisons fermées

- Généré quatre concepts isolés avec ImageGen, en trois quarts plongeant, à facettes et en aplats crème, ocre et pêche. Références conservées dans `concept/ile_03/maisons_fermees/`. L’utilisateur a validé le budget de 80 crédits et a demandé à voir les images avant la génération des maillages.

## Modèles Meshy des maisons fermées

- Sur accord, utilisé les quatre références validées dans Meshy 7.1 High Detail standard, sans texture, 20 crédits par modèle. Sources dans `tools/blender/sources/meshy/maisons_colonie/`. Tâches dans l’ordre quai, mitoyenne, angle et ville haute : `01a1f87d-456e-7748-923a-0c9d51ad59e5`, `01a1f87d-3a73-7095-bd65-102d1ea1cefb`, `01a1f87d-5198-752e-9e61-8f70cb7a7954`, `01a1f87d-5b7d-728d-9825-b7fb7c6f6b67`.
- `tools/blender/maisons_fermees_colonie.py` applique les matériaux en aplats, réduit chaque maillage à 18 000 triangles et exporte les quatre GLB et les aperçus. Les 27 volumes visuels temporaires des maisons fermées ont été remplacés. Emprises horizontales et positions des collisions conservées. Contrôles des GLB et des scènes passés. Rendu et performances en jeu à vérifier sur accord.
- Sur accord, importé les quatre GLB dans Godot et relancé la Colonie sur Mac. Démarrage sans erreur, modèles visibles au quai et cadence mesurée autour de 56 à 60 i/s au départ. Partie laissée ouverte.

## Couleurs de la maison du quai

- Sur retour utilisateur, repris les matériaux du modèle du quai à partir des pièces du maillage repérées dans les projections orthographiques : vantail, volets, auvent, lampe, socle, coque et nervures. Aperçu Blender contrôlé, GLB actualisé, aucun appel Meshy. La comparaison en jeu reste à faire sur accord.

## Nouvelles variantes de maisons fermées

- Quatre références ImageGen ajoutées dans concept/ile_03/maisons_fermees. Ville basse à pignon ou toit-terrasse, ville haute à contreforts ou balcon fermé. Vues isolées en trois quarts plongeant sur fond neutre, palette crème, ocre et pêche. Validation visuelle avant Meshy.

- Visuels validés et budget de 20 crédits approuvé. Quatre maillages Meshy T2.5 Smart Topology sans texture, cible 18 000 triangles. GLB distincts contrôlés et archivés dans tools/blender/sources/meshy/maisons_colonie. Pignon 17 015, terrasse 18 828, contreforts 18 437, balcon 17 150 triangles.
- Tâches Meshy dans cet ordre : 01a1f89e-5ad8-7773-b43d-cb840d1f133b, 01a1f89e-6341-7406-8b87-9179d046957e, 01a1f89e-5014-75ed-8df3-5020729e113c, 01a1f89e-6ce3-7727-9dd8-f094edc27726. Matériaux et intégration à faire.

- Sur demande, relancé la scène actuelle de la Colonie dans Godot 4.7.2 sur Mac. Aucun message d’erreur au démarrage. Partie laissée ouverte. Les quatre GLB bruts restent à intégrer.

- Après retour utilisateur, intégré les quatre maillages Meshy dans le décor Blender du lagon avec matériaux en aplats et fondations. Les logis fermés 01 et 02 près du quai, 14 et 15 en ville haute sont remplacés. Les sept adresses visitables restent à leur place.
- Export GLB contrôlé (quatre façades et fondations présentes, quatre anciens logis absents), projet Godot réimporté et Colonie relancée sur Mac sans erreur au journal. Partie laissée ouverte. Rendu et collisions à vérifier en jouant.

- Retour visuel : impression de rendu cheap. Analyse du rendu Blender et du générateur : couleurs assignées par position et orientation des faces, emprise identique aux quatre modèles, contraste de détail marqué avec le bâti environnant. Proposé de reprendre la maison à pignon comme référence avant les trois suivantes.

- Sur accord, repris la maison à pignon seule. Échelle uniforme avec hauteur de 6 m, palette et limites de couleurs relevées sur les vues orthographiques. Ajouté un vantail devant une face du mur Meshy qui masquait la porte. Gros plan Blender vérifié et conservé dans concept/ile_03/maisons_fermees/apercu_pignon_blender.png. Décor, source Blender et graphe régénérés. Réimport et vérification Godot à faire sur accord.
