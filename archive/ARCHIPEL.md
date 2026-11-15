# Petite Planète — le jeu de base : l'archipel

> Document de référence pour développer **toutes les îles côté lumière** (explorer, comprendre, allumer…).
> Le monde de l'ombre des îles 2 à 9 (`MONDE_OMBRE.md`) viendra **après**, une fois le jeu de base fini.
> À lire avec `DESIGN.md` (le moteur : batterie, boucle, berceau) et `ILE_02_PHARE.md`.
> Rédigé le 2026-11-15 à partir des choix de l'utilisateur. Les points marqués **[à valider]** sont des propositions.

---

## 1. Ce qui a été décidé

| Sujet | Décision |
|---|---|
| Voyage | **Navigation libre** : on pilote la barque sur une vraie mer, on voit les îles au loin. |
| La mer | Noyée de **brume** par endroits (elle vide la batterie), mais la barque porte une **lanterne**. |
| Mort loin de l'île 1 | Réveil dans le **berceau de l'île 1**, corps neuf ; la **barque attend au ponton de l'île 1**. L'ancien corps reste où il est tombé. |
| Ordre des îles | **Ouvert** dès qu'on a la barque, avec un **ordre conseillé** (on voit le Phare depuis l'île 1, chaque île pointe vers d'autres). |
| Temps | **Cycles permanents** (marée, faisceau du Phare…) qui tournent sans s'arrêter, indépendants du réveil. |
| Énigmes | **Peu, mais grosses**. Et surtout : **tout est lié**. Une île fait comprendre quelque chose sur une autre. |
| Le Phare | C'était le **poste de la Gardienne** : de là, elle gardait les lanternes de tout l'archipel. |

### Ce qui manque aujourd'hui (constat de l'utilisateur)
L'île 1 se résume à « allumer des lumières ». Le jeu de base doit devenir un **réseau d'énigmes de savoir**, comme Outer Wilds :
- des endroits **accessibles seulement à un certain moment** (marée basse, passage du faisceau…) ;
- des **réponses trouvées sur une île pour une question posée sur une autre** ;
- très peu de « fais ceci pour avancer », beaucoup de « maintenant que je sais, je peux ».

---

## 2. La boucle du jeu de base

1. On se réveille dans le berceau (île 1). Batterie pleine.
2. On prend la barque, on traverse la brume de la mer, on explore une île.
3. On apprend des choses (lieux, horaires des cycles, pages de la Gardienne, mécanismes des Semeurs, codes…).
4. La batterie finit par se vider : le corps s'éteint là où il est. Réveil au berceau.
5. **Tout se réinitialise** (lanternes, mécanismes, barque au ponton de l'île 1). **Seul le savoir reste** (le carnet, et la tête du joueur), plus les anciens corps.
6. Avec ce qu'on sait, on va plus loin.

**Ce qui persiste d'une boucle à l'autre :**
- le carnet : carte, croquis, pages, notes ;
- les anciens corps ;
- **aucun changement définitif** (décidé le 2026-11-15) : à chaque réveil, tout le monde se remet comme au premier jour. Seul le savoir avance.

---

## 3. La mer et la barque

### La mer
- Une **seule grande mer** contient les 9 îles. On les voit au loin : leurs silhouettes et leurs lanternes allumées.
- **Brume en mer**, en bancs plus ou moins épais :
  - mer claire : on ne perd rien ;
  - brume légère : elle vide lentement (comme sur les îles) ;
  - **brume épaisse** : elle vide vite. Certaines îles en sont entourées (le Marais, l'île de la Gardienne…).
- **Les repères en mer** :
  - les **bouées-lanternes** des Semeurs, éteintes au début. Allumées, ce sont des points de recharge et elles dessinent des routes ;
  - **le faisceau du Phare** (une fois rallumé) : là où il passe, la brume recule un instant ;
  - les rochers, les épaves, les îlots.

### La lanterne de la barque (décidé le 2026-11-15)
- La barque porte une lanterne de Semeur. **Tant qu'elle brille, la brume de la mer ne vide pas le robot.**
- Elle a sa **propre réserve** (3 crans, visibles sur la lanterne) qui baisse en traversant la brume (vite en brume épaisse).
- On la **remplit en y versant de la lumière** : on reprend la lumière d'une lanterne (geste déjà connu) puis on la donne à la barque. On peut aussi la remplir au passage du faisceau du Phare ou près d'une bouée allumée.
- Si elle s'éteint en mer, c'est la batterie du robot qui prend le relais… et on risque de mourir au milieu de l'eau.
- Conséquence : **chaque traversée se prépare** (combien de lumière emporter, par quelle route, à quel moment du cycle). C'est déjà une petite énigme, sans menu ni chiffre.

### Piloter
- La barque se pilote comme le robot (mêmes touches), lentement, avec de l'inertie ; la caméra recule en mer.
- On **accoste** en s'approchant d'un ponton ou d'une plage (`E`). On ne peut accoster que là (pas n'importe où sur la côte).
- La barque reste où on la laisse **pendant la boucle** ; à la mort, elle revient au ponton de l'île 1.

---

## 4. Les cycles du monde (permanents)
Ils tournent en continu, sans jamais se remettre à zéro. Le carnet note ce qu'on a compris (« la mer descend quand… »).

| Cycle | Durée | Ce qu'il change |
|---|---|---|
| **La marée** | 8 min (4 basse, 4 haute, avec montée et descente visibles) | Chaussées, grottes, récifs et épaves émergent à marée basse (Phare, Île Engloutie, Marais…). Certains pontons sont inaccessibles à marée basse. |
| **Le faisceau du Phare** | 40 s par tour (une fois le Phare rallumé) | Il balaie l'île 2 et la mer ; là où il passe, la brume recule et on se recharge. Pointé vers une île, il y déclenche quelque chose. |
| **La lune** | 24 min (3 marées) | Phases visibles dans le ciel ; à la pleine lune, certaines choses n'ont lieu que là (une créature, un reflet, une porte des Semeurs qui s'ouvre au « clair de lune »). Elle sert aux grandes énigmes de la fin. |

Pour le joueur, **apprendre les cycles fait partie du savoir** : il saura qu'il faut quitter l'île 1 « juste après le passage du faisceau », ou attendre la marée basse avant de partir vers l'épave.

---

## 5. Les énigmes : peu, grosses, et liées

### Principe
- **2 ou 3 grandes énigmes par île**, longues, qu'on résout par compréhension et pas par essais. Plus des **secrets** optionnels (corps, pages, créatures, raccourcis).
- **Les liens entre îles sont irréguliers, jamais proportionnels** : la plupart des énigmes se comprennent sur place ; quelques-unes demandent un savoir venu d'ailleurs ; certaines phrases ne prennent leur sens que bien plus tard, sur une autre île. Une île peut beaucoup donner sans rien demander, ou l'inverse.
- **Rien ne s'achète, rien ne s'équipe** : la seule progression est ce que l'on sait. Un joueur qui sait tout peut finir le jeu de base en une boucle.
- On ne dit jamais quoi faire. Le carnet **note** ce qu'on a vu, jamais ce qu'il faut faire.

### Les briques réutilisables (le vocabulaire des énigmes)
| Brique | Exemple |
|---|---|
| **Batterie** | quelles lanternes allumer ou reprendre pour atteindre un point ; transporter la lumière dans la lanterne de la barque |
| **Timing de cycle** | n'atteindre une grotte qu'à marée basse ; traverser une brume en suivant le faisceau |
| **Lumière dirigée** | miroirs et lentilles des Semeurs : renvoyer la lumière là où on ne peut pas aller |
| **Plantes** | racines, lianes (déjà sur l'île 1) |
| **Mécanismes des Semeurs** | portes, vannes, écluses, ascenseurs, avec des **codes** et des **ordres** à retrouver ailleurs |
| **Le noir** | éteindre au bon endroit pour voir ce qui est caché (pages lumineuses, chemins de Lueurs) |
| **Les anciens corps** | un corps mort au mauvais moment raconte une erreur (« il est tombé là à marée haute ») |

---

## 6. La toile du savoir

> Pas de règle du type « chaque île donne deux savoirs et en demande un » : les liens sont **irréguliers**.
> Ils sont décidés île par île, dans le document de chaque île. Ce tableau ne fait que les rassembler.

| Lien | Nature |
|---|---|
| île 1 → île 2 | On voit le Phare depuis l'île 1. |
| île 2 → île 6, île 3 | La **table des marées** (bureau du Phare). |
| île 2 → île 4, île 7 | Le **principe des miroirs**. |
| île 2 → tout l'archipel | La **carte de l'archipel** (sommet du Phare). |
| île 3 → île 2 | « Quand le grand œil nous regarde, la brume s'ouvre » : on revient tourner la lentille vers le Marais. |
| île 7 → île 2 | La page 8 donne le sens de la phrase « les nuits de pleine lune, le Phare chante, et je vois ma maison » : la lentille montre l'île de la Gardienne. |

*Les liens des îles 3 à 9 seront ajoutés au fil de leur conception.*

**L'ordre conseillé** (jamais imposé) : 1 → 2 (le Phare se voit et ouvre la carte) → ensuite libre.

## 7. Comment on le construit (technique)

- **Une scène « Archipel »** : la mer, le ciel, la brume en mer, les cycles (une horloge du monde, en autoload), la barque, les bouées.
- **Chaque île reste sa propre scène** (`scenes/islands/island_0X.tscn`), posée à sa place dans l'Archipel. **Les îles lointaines sont remplacées par une silhouette légère** (ce qui est déjà le cas de l'île du Phare vue depuis l'île 1), et chargées en entier quand on approche.
- **L'horloge du monde** (`WorldClock`, autoload) donne l'heure des cycles à tout le monde : la marée lit `WorldClock.tide()`, le Phare lit `WorldClock.beam_angle()`.
- **Les états qui se réinitialisent** à chaque boucle sont regroupés (`Loop`), comme aujourd'hui.
- Les îles 2 à 9 sont développées **côté lumière d'abord**. Leur nœud `Ombre` reste vide jusqu'à la grande phase « monde de la brume ».

---

## 8. Décisions prises
- Lanterne de barque : **une réserve qu'on remplit** avec la lumière reprise (ou au faisceau, ou près d'une bouée allumée).
- Cycles : marée **8 min**, faisceau **40 s**, lune **24 min**.
- **Aucun changement définitif** d'une boucle à l'autre.
- Liens entre îles **irréguliers**, décidés île par île.
