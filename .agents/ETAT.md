# État du projet — passation entre agents

> Mis à jour le **2026-11-19** par **codex** (passation Mac → PC fixe).
> À réécrire à chaque fin de session (voir `procedures/fin-de-session.md`). ≤ 1 page.

## Où on en est
- **Docs de conception** : les 7 îles sont écrites (`ILE_01` … `ILE_07`, `TOILE_ENQUETE.md`). Feuille de route : `ROADMAP.md`.
- **DA v6** (`DA.md`) : vue de dessus, low-poly à facettes, pastels lumineux.
- **Île 1** jouable en maquette : `scenes/ile_01_maquette.tscn`.
- **Île 2** (`scenes/ile_02_maquette.tscn`) : terrain refait dans Blender en « blocs taillés à facettes, strates nettes » (validé par l'utilisateur), généré par `tools/blender/terrain_ile_02.py` depuis la carte du nœud Maquette → `assets/models/ile02/terrain_ile_02.glb`, branché par `terrain_modele`. Ambiance : `assets/ambiances/ile_02.tres`. Phare, maison du quai, stations des caps et chantier du quai modélisés.

## Reprise sur le PC fixe
- Récupérer `main` depuis `origin` dans la copie Windows. Le lot comprend la maquette de l’île 2, les sources Blender et les documents illustrés.
- Premier essai en jeu à prévoir sur accord : recharge à la bouée depuis la barque, avec vérification du branchement, de la batterie et de la sauvegarde.

## En chantier
- Nettoyage Mac : `captures/` contient les rendus Blender et est exclu de l’import Godot. Les 38 fiches d’import et leurs caches, ainsi que les caches shaders et Python, ont été retirés. Vérification statique uniquement.
- Le lot `4ca2d67` inclut le terrain, la brume liée à la batterie, la marée et ses effets, la maison du quai avec sa lanterne de recharge, son horloge et son cahier illustré, ainsi que les trois balises de la chaussée. Voir le journal `2026-11-19_claude_ile-02-terrain.md`.
- **Phare** : scène `scenes/ile02/phare.tscn`, modèle complet généré par `tools/blender/decoration_bureau_iris.py`. La porte des cartes fait face à l’arrivée de la volée, avec plaque et serrure. La chambre d’Iris est meublée et accessible depuis la galerie par une traversée de l’échelle mise en scène avec `E`, puis par une volée sous la lucarne. L’échelle fonctionne dans les deux sens. Les six nouveaux documents sont dessinés et branchés dans le décor, la lecture et le carnet.
- Après le retour en jeu, la chambre a été déplacée dans une aile à l’est pour dégager les deux volées depuis le rez. Sa porte fermée donne au bout du palier du bureau. Une passerelle relie le pied de l’échelle à la lucarne.
- La coupe masque l’échelle et l’aile d’Iris pendant la montée dans la tour. Dans la chambre, elle masque les intérieurs de la tour. Les marches et paliers proches restent visibles. L’utilisateur confirme que le Phare fonctionne bien après le point sur l’échelle et la coupe.
- Animation Meshy de l’échelle intégrée sur l’armature existante. Trois clips pour 9 crédits, dans `robot_meshy.glb`. Le cycle est calé sur les barreaux et joué à l’envers pour descendre. Les anciens clips et le maillage sont identiques. Les transitions aux deux paliers ont passé le contrôle des collisions Blender.
- L’instance `Monde/Phare`, sa scène et le modèle sont présents dans la copie Mac, avec des changements locaux non commités. La copie Windows reste à vérifier.
- L’utilisateur a signalé que l’ouverture latérale débouchait sur des marches et exigeait un saut. Le modèle du Phare a été réexporté avec une ouverture au sud-est et un palier de plain-pied. Le sol, le dégagement de la capsule et la pente ont été contrôlés sur les collisions Blender. GLB réimporté sur Mac et île 2 lancée sur accord pour que l’utilisateur vérifie le passage.
- La montée des cartes masquait aussi le bureau sur la capture en jeu. Ses maillages s’effacent progressivement pendant la visite du bureau, reviennent au pied des marches et restent visibles pendant la montée. Le repère est éditable dans `scenes/ile02/phare.tscn`. Rendu à vérifier pendant la partie ouverte.
- La sauvegarde de l’île 2 utilise son propre fichier. La notification de démarrage du menu pause est protégée avant l’entrée dans l’arbre de scène.

## Prochaines étapes (île 2)
- **Port** : hangar visitable en coupe, deux coques, établi, porte à deux vantaux ouverte par le miroir d’essai et état sauvegardable. Bouée flottante et échelle peinte posées. Deux accessoires Meshy T2.5 pour 10 crédits, sources dans `tools/blender/sources/hangar_quai/`. Neuf contrôles Godot réussis et île 2 laissée ouverte sur Mac. Recharge depuis la barque raccordée, avec prise côté quai, échange du câble, premier allumage mis en scène et état sauvegardable. Contrôles statiques terminés, essai de ce nouveau geste dans Godot sur accord. Prochains lots : chaussée et anciens corps, jardin et banc d’Iris, grottes et crypte, finitions de la maison.
- **Lunette d’Iris** : scène éditable sur la galerie, cinq crans avec rotation du tube et fondu dans l’oculaire, vues illustrées et croquis persistants dans le carnet. Cran sans nom à 318°. Import Godot réussi et île 2 lancée sur Mac à la demande de l’utilisateur. Essai des crans et du carnet en jeu à faire. L’ancien corps de la galerie reste à réaliser.
- **Bureau d'Iris** : l'utilisateur a approuvé les planches et 50 crédits pour le lot des dix objets en volume. Géométries sources dans `tools/blender/sources/bureau_iris/`. Bureau meublé et deux documents assemblés dans Blender. Prévisualisation dans `concept/bureau_iris_meuble/`.
1. K3 : une seule lanterne, au cap Est, éclaire le premier miroir. La réflexion part de la vitre et dépend de son orientation. Chaque miroir transmet uniquement s’il reçoit le rayon du précédent. Le premier rallumage révèle l’épave et ajoute la carte. Les quatre segments sont dégagés dans Blender. Vérifié dans Godot sans fenêtre : chaque désalignement éteint les reflets suivants, les trois reflets allument le Phare et couper la source assombrit tout le circuit.
   **G4** : `E` ouvre un panneau de face avec trois axes, un râtelier et les actions de rotation et de retrait. L’assemblage reste dans la scène du Phare avec le chariot et le cric Meshy. Le bon assemblage tend la chaîne et déverrouille la manivelle de la galerie. Tests de l’ancienne interaction réussis ; nouvel écran importé et jeu relancé sur Mac sans erreur au démarrage. Interactions du panneau à vérifier en jeu.
   **G3** : barque au ponton, venue à l’épave possible à marée basse si le Phare est rallumé. Coque et cabine meublée modélisées dans Blender, avec coupe et passerelle physique. Clé à prendre sur le bureau, porte animée et état sauvegardé. Relèvements dans la pièce, le carnet et la graduation de la commande. Rendu Blender vérifié et ressources importées. Île 2 ouverte sur Mac sans erreur au démarrage. Parcours complet à vérifier en jeu.
   **Coupe des cartes** : l’utilisateur signale que l’escalier masque la pièce. Sous l’angle de jeu, trois cadrages Blender confirment que la montée vers la galerie masque le registre. La montée s’efface en entrant dans la salle ouverte et revient en ressortant. Vérification en jeu sur accord.
2. Faire tester en jeu la brume épaisse, la marée et les effets qui signalent que l’eau emporte le robot. F8 accélère le cycle. Ajuster les réglages selon le retour.
3. Fondu des obstacles entre la caméra et le robot (le Phare le cachera). Relief : on GARDE 2,5 m par niveau (décidé).
4. Vérifier le parcours de la chaussée et les trois balises en jeu. Restent les dalles et l’ancien corps.
5. Maison du quai : la scène, le cahier et la recharge sont en place. Restent les objets principaux à détailler (poêle, cirés, bottes…).
6. Accessoires sculptés éventuels pour le Phare et objets des autres lieux (maison du quai, hangar, miroirs, banc, arbre rose mort…) — annoncer le coût Meshy avant.

## Pièges actifs
- Modifier la carte de l'île 2 → relancer `terrain_ile_02.py` dans Blender, puis réimporter le .glb (`filesystem_manage reimport`).
- Le jeu lancé depuis l'éditeur bloque toutes les écritures MCP : demander à l'utilisateur de l'arrêter.
- Script `@tool` modifié de l'extérieur : ses nouvelles `@export` peuvent rester `null` dans l'éditeur → les régler via MCP (voir procedures/godot.md).
- Le MCP Blender n'a pas d'état entre deux appels (`exec` du script à chaque fois).
- Depuis cette session sur Mac, le MCP Blender pilote le PC Windows. Celui-ci a sa copie du projet dans `OneDrive/Bureau/petite-planete-v5`. L'éditeur Godot tournait sur le PC, sans session connectée au MCP Godot de Codex.
- Toujours **demander avant de lancer** le jeu ou un test.
- Meshy répond dans Codex sur le Mac. Solde vérifié avant le cric : 2 740 crédits, dont 2 541 mensuels (renouvellement le 2026-12-16) et 199 permanents. Le cric a consommé 5 crédits.

## Questions ouvertes pour l'utilisateur
- Caméra v6 : angle/focale, fixe ou orientable, tilt-shift ? (`DA.md`)
