# 2026-11-19 — codex — conception du Phare

## Demandé

Imaginer un bâtiment marquant, cohérent avec la direction artistique, en tirant parti de Blender et de Meshy.

## Fait

- Consulté la direction artistique, le document de l'île, le croquis du Phare, l'image cible et la capture du plateau.
- Proposé une tour côtière à pans coupés, une cage optique lisible depuis le dessus et un volume latéral pour le bureau et la lucarne d'Iris. Proposition de visite continue avec ouverture visuelle au niveau du robot.
- Proposé de faire dans Blender le premier volume et les organes mobiles, puis d'utiliser Meshy pour les accessoires sculptés au besoin.

## Reste à faire

- Relier la clé de l'épave à la porte des cartes, construire les crans de la lunette et l'accès à la chambre. L'énigme G4 reste à produire. L'utilisateur a préféré poursuivre avant un essai en jeu.

## Maquette Blender

- L'utilisateur a validé le rendu d'ensemble dans Blender comme première étape, puis le choix des ajouts Meshy après examen.
- Tour côtière à pans coupés avec soubassement à contreforts, couronne en pierre et cuivre, aile et lucarne d'Iris. Lentille, couronne et roues sont éditables et distinctes. Mise en contexte avec le terrain original et le robot à l'échelle.
- `tools/blender/phare_ile_02.py` génère le `.blend` et les trois PNG dans `concept/phare_ile_02/`. Cadrages depuis le ponton, vue d'ensemble et caméra d'entrée à 9 m / 40°. Scène ouverte dans Blender 5.3 sur le PC, après vérification que le document courant était vierge.
- Le MCP Godot ne voit pas l'éditeur Windows, qui est ouvert. Aucun lancement de Godot ou de test, aucun appel payant Meshy.

## Deuxième maquette

- L'utilisateur trouve le premier Phare « un peu cheap ». Proposition d'un socle commun avec parvis, d'un bureau en aile vitrée avec toit bas et d'une couronne ouverte à trois nervures.
- V2 générée sur le PC et dans la copie Mac. Les deux variantes utilisent les mêmes caméras et éclairages pour la comparaison. L'utilisateur aime la V2. Direction extérieure consignée dans `ILE_02_PHARE.md`.

## Salle des machines et seuil

- La tour reprend le parvis V2. Portail en retrait, schéma peint, traces des roues, établi et chaîne. Escalier en U à deux volées jusqu'au palier d'Iris. Aperçus Blender dans `concept/phare_ile_02_rez/`.
- `tools/blender/salle_machines_phare.py` exporte `assets/models/ile02/phare.glb` avec un groupe `Coupe` et un maillage physique `-colonly`. `scenes/ile02/phare.tscn` est instanciée dans `scenes/ile_02_maquette.tscn` à la place de la tour provisoire. Elle reprend `batiment_coupe.gd` et expose deux volumes d'entrée et les repères du seuil et du palier.
- Blender et fichiers Godot synchronisés sur le PC. Références Godot vérifiées par le vérificateur statique, collision du GLB échantillonnée du seuil au palier. Le MCP Godot demeure déconnecté et l'import de la scène sur le PC n'a pas été constaté. Aucun lancement du jeu ni d'un test Godot.

## Bureau d'Iris

- Couloir du palier vers le bureau, grande baie côté Large, table des relevés, dossiers, porte de la chambre et dessin d'Aube. Le modèle actuel est exporté par `tools/blender/bureau_iris.py`. Les deux vues du bureau sont dans `concept/phare_ile_02_bureau/`.
- `scripts/phare_coupe.gd` reprend le fondu du bâtiment et montre le bureau à hauteur de palier. Le plafond visible est indépendant de la collision. `page_lisible.gd` accepte une portée verticale facultative pour éviter la lecture depuis le rez-de-chaussée.
- Page 1 validée, note de la clé avec la ligne de la pleine lune et dessin d'Aube lisibles. Plan des miroirs et table des marées réunis sur le relevé illustré `assets/affiches/releves_iris.png`. Aucun appel Meshy ni lancement Godot.

## Salle des cartes et galerie

- `tools/blender/sommet_phare.py` prolonge la circulation avec deux volées rayonnantes depuis le bureau. Le palier des cartes débouche à la fois sur une porte fermée et sur la suite de l'escalier. La galerie conserve la lentille et reçoit la lunette tournée vers le ravitailleur.
- `phare.tscn` sépare la collision de la porte des cartes pour la future serrure. Le pupitre porte le registre validé. Rose des vents dans la salle, angles de navigation et clé de l'épave à relier. Coupe adaptée aux niveaux dans `phare_coupe.gd`. Aucun lancement de Godot.

## Décoration du bureau d'Iris

- L'utilisateur demande des images de tous les éléments car les intérieurs lui paraissent trop simples. Douze références sur deux planches et une vue meublée générées avec imagegen, sauvegardées dans `concept/bureau_iris_decoration/` avec les prompts. Le siège en côtes de bois, le manteau et les relevés structurent la proposition. Aucun appel payant Meshy.

- L'utilisateur approuve les références puis le lot Meshy T2.5 des dix objets en géométrie seule pour 50 crédits. Les dix tâches réussissent. Sources et provenance dans `tools/blender/sources/bureau_iris/`.
- `tools/blender/decoration_bureau_iris.py` applique les aplats et l'échelle, assemble le bureau autour des documents existants, puis exporte le Phare complet. Le passage vers la salle des cartes est contrôlé sur le modèle de collision. Aucun lancement Godot.

## Vérification de l’intégration dans le projet

- `scenes/ile_02_maquette.tscn` instancie `scenes/ile02/phare.tscn` sous `Monde/Phare`. La scène charge `assets/models/ile02/phare.glb`. Vérifié sur la copie Mac, avec des changements locaux non commités. Copie Windows non vérifiée. Aucun lancement Godot.
- À la demande de l’utilisateur, lancement direct de la maquette de l’île 2 sur Mac avec Godot 4.7.2. Processus laissé ouvert après vérification du démarrage.

## Accès de plain-pied à l’escalier

- En jeu, l’utilisateur constate que l’ouverture donne sur le côté des marches, ce qui exige un saut.
- `salle_machines_phare.py` décale l’ouverture visuelle et physique vers le pied de la volée et ajoute des dalles qui guident vers le palier. Le modèle complet `assets/models/ile02/phare.glb` est réexporté. Contrôle Blender du sol continu, du dégagement de la capsule et de la pente de la première volée. La réimportation et l’essai Godot restent à faire sur accord.

## Bureau dégagé en coupe

- La capture en jeu montre la montée des cartes devant la table d’Iris. `phare_coupe.gd` efface progressivement ses maillages quand le robot visite le bureau et les réaffiche à l’approche du pied de la volée. Le repère `ReperePiedMonteeCartes` est visible dans la scène. Les 79 maillages ciblés sont distincts des collisions. Vérification statique des références sans erreur. Rendu Godot à vérifier sur accord.
- Sur accord de l’utilisateur, Godot réimporte `phare.glb` sans erreur sur Mac. La maquette de l’île 2 est ouverte pour l’essai des deux corrections. Le journal au démarrage signale un appel de `Sauvegarde.en_partie()` par le menu pause alors que l’arbre est indisponible. Le processus de jeu reste actif.
- Inventaire du travail restant à partir du document de l’île et de la scène actuelle. Il couvre le rallumage, les engrenages, le déverrouillage et les relèvements, la chambre d’Iris et les interactions de la galerie. Aucun changement à la scène.

## Papiers illustrés, entrée des cartes et chambre d’Iris

- L’utilisateur choisit la porte des cartes face à l’arrivée de l’escalier et une descente mise en scène depuis la galerie.
- Page de tournée, billet de la clé, dessin du toit, registre, lettre à Ysolde et dessin « Nos amis du noir » rendus avec les sources HTML/SVG. Le relevé existant reste en place. Les anciennes clés de lecture sont préservées et les entrées du carnet retrouvent l’illustration au chargement de l’île.
- Porte et serrure des cartes réorientées avec leur collision, cartouche affiché à l’arrivée. La chambre possède son lit, sa table de nuit, sa tasse, sa lanterne débranchée et deux documents. L’échelle pose les membres du robot sur les barreaux pendant les traversées. La lucarne descend vers la chambre sur un sol continu, et la coupe dégage le mobilier.
- Les papiers sont inspectés en planche et la chambre en coupe dans Blender. Contrôle des collisions réussi du débouché de l’escalier de la galerie à la zone de lecture, après élargissement entre les garde-corps. Les références et la syntaxe des scripts passent les contrôles statiques. Le modèle final est réexporté dans `assets/models/ile02/phare.glb`. Import et essai Godot à faire sur accord.
- Sur accord, réimportation du modèle et des papiers, puis lancement direct de l’île 2 sur Mac dans Godot 4.7.2. Démarrage sans erreur signalée et partie laissée ouverte.

## Dégagement de l’escalier après l’ajout de la chambre

- L’utilisateur signale que la chambre bloque la montée. Son ancien plancher traversait le volume au-dessus de l’escalier en U.
- Chambre et documents décalés dans une aile attenante à l’est. La porte est au bout du palier du bureau et la passerelle relie le pied de l’échelle à la lucarne. Le modèle complet est réexporté.
- Contrôle du GLB final dans Blender avec la capsule du robot de la salle des machines jusqu’au bureau, puis sur la galerie, l’échelle, la passerelle et la lucarne jusqu’à la zone de lecture. Réimportation et lancement Godot à faire sur accord.
- Sur accord, réimportation du modèle corrigé et lancement direct de l’île 2 sur Mac. Démarrage sans erreur signalée, partie laissée ouverte.

## Coupe par niveau et chambre isolée

- La capture de l’utilisateur montre l’échelle, l’aile et le rez depuis le palier des cartes. Il voit également la tour depuis la chambre. L’export groupe séparément l’accès d’Iris, la chambre, la salle des machines, ses volées et son palier haut.
- `phare_coupe.gd` affiche les pièces proches pendant la montée, ouvre l’accès visuel depuis la galerie et masque les intérieurs de la tour dans la chambre. Contrôles de la hiérarchie du GLB et du trajet de collision réussis. Rendu à vérifier après réimport et relance Godot sur accord.

## Recherche d’animations Meshy pour l’échelle

- L’utilisateur demande une animation Meshy de qualité. La bibliothèque propose une prise d’échelle (436), un cycle de montée (438) et une sortie (435). L’armature existante est disponible. Coût des trois clips : 9 crédits sur 2 759 disponibles. Aucun appel payant avant accord.
- Accord obtenu. Tâche Meshy `01a1f305-de94-70bc-8fd8-c153d5d5ca7f`, réussie, 9 crédits dépensés. Source `tools/blender/sources/meshy/robot_rig/robot_echelle.glb`. `tools/blender/robot_echelle.py` adapte le déplacement du bassin au trajet du joueur, ferme la boucle et ajoute les trois clips au GLB sans réencoder le maillage ni les 15 animations précédentes.
- Dans Godot, le cycle suit l’espacement de 31 cm, la descente inverse les clips et le correcteur d’appuis intervient quand la main ou le pied approche d’un barreau. Le passage du rebord du palier est fractionné pour que le robot finisse de se hisser avant de s’avancer. Contrôle Blender réussi dans les deux sens. Réimport et rendu en jeu à vérifier sur accord.
