# Petite Planète — les règles du jeu (v4)

> **Les documents du projet :**
> - `DESIGN.md` (ce fichier) : les règles du jeu, le moteur, la mer, les cycles, la direction artistique.
> - `ENQUETE.md` : l'histoire (« Où sont les Semeurs ? »), les personnages, les 7 îles, la fin.
> - `ILE_01_REVEIL.md`, `ILE_02_PHARE.md`, `ILE_03_COLONIE.md`… : une île par document, au complet.
> - `ROADMAP.md` : ce qui est construit, et ce qui reste à faire.
> - `archive/` : les anciennes versions (v3), gardées pour mémoire.

---

## En une phrase
Un petit robot jardinier se réveille sur un archipel noyé de brume, où tout est construit, éclairé… et vide. Il enquête : où sont les Semeurs ? Il finit par comprendre qu'ils sont morts de leur propre lumière, et qu'un peuple vit caché dans la brume depuis le début.

## Piliers
1. **Le savoir est la seule vraie progression.** Comme dans Outer Wilds : le monde est ouvert, rien ne s'achète ni ne s'équipe, rien n'est donné. Un joueur qui sait peut aller presque partout très tôt.
2. **Une grande enquête.** Une question (« Où sont les Semeurs ? »), plusieurs fils qui traversent les îles, une vérité reconstituée par morceaux, dans l'ordre que le joueur choisit.
3. **Beaucoup d'énigmes variées sur chaque île.** Jamais « une île = une mécanique ». Sur toutes les îles, mélangés : **temps et cycles**, **lieux cachés et observation**, **mécanismes et codes**.
4. **Chill mais exigeant.** Pas de danger, pas d'ennemis. Des petites énigmes gratifiantes et quelques grandes vraiment exigeantes.
5. **Le monde ment par omission.** Ce que le joueur croit au début (ils sont partis, la brume est morte, les corps sont d'autres robots) est faux.
6. **Beau, calme, mélancolique**, avec une fin dont on se souvient.

---

## Le moteur : batterie, brume et berceau

### La batterie (une contrainte partout, pas un type d'énigme)
- Le robot a une **batterie** (jauge discrète sur l'antenne, sans texte).
- **La brume la vide** ; **la lumière la recharge** (lanternes allumées, pierres-soleil).
- **Allumer une lanterne coûte de la batterie**, mais elle éclaire le chemin et devient un point de recharge.
- **Reprendre la lumière** (`E` sur une lanterne allumée) : la lumière descend en spirale dans l'antenne, la batterie remonte, la lanterne s'éteint et sa zone se rendort.
- *(Dans l'histoire : les Semeurs vivaient exactement comme ça. Le robot est fait à leur image, et sa batterie raconte déjà leur mort.)*

### Le mode nuit (secret, touche `N`)
- **Jamais indiqué à l'écran.** Indices : un vieux croquis de l'atelier (robot antenne éteinte sous la lune, touche « N » griffonnée), la page 7 d'Iris.
- Le robot éteint sa propre antenne : la brume **ne le vide plus**, la lumière ne le recharge plus, **aucune action de lumière**, et **le peuple caché est visible**.
- C'est le principe du monde caché : **rien n'est donné**. Dès l'île 1, un joueur curieux peut voir le peuple de la brume ; il ne le comprend qu'en avançant.
- Voir à **batterie presque vide** est la version accidentelle : l'antenne s'assombrit et des formes apparaissent dans la brume.

### La boucle
- La conscience du robot vit dans le **berceau** (l'abri de l'île 1). Le robot n'est qu'un **corps**.
- **Batterie vide** : le corps s'éteint **sur place**, la conscience se réveille dans un **corps neuf**, couché dans l'abri.
- **Tout se réinitialise** : lanternes, mécanismes, barque (cachée dans la crique de l'île 1).
- **Ce qui reste** : le savoir du joueur, le carnet, **les anciens corps** (là où ils sont tombés). **Aucun changement définitif.**
- Le robot ne comprend pas que les anciens corps sont lui-même.

### Le carnet : un tableau d'enquête
- Comme le journal du vaisseau d'Outer Wilds : chaque **lieu** est une fiche ; des **rumeurs** relient les lieux par des flèches ; des **points d'interrogation** montrent ce qu'il reste à trouver.
- Il garde aussi : les cartes à l'encre, les croquis, les dessins d'Aube, les pages et lettres des Semeurs, les paroles du peuple caché, le bestiaire.
- **Il note ce qu'on a vu, jamais ce qu'il faut faire.**

---

## La mer et la barque
- **Une seule mer**, les 7 îles placées dedans ; on voit leurs silhouettes au loin.
- **Navigation libre** : la barque se pilote comme le robot, lentement, avec de l'inertie ; la caméra recule en mer. On **accoste** aux pontons et aux plages (`E`).
- **Brume en mer** : mer claire (rien), brume légère (vide lentement), **brume épaisse** (vide vite ; certaines îles en sont entourées).
- **La lanterne de la barque** : tant qu'elle brille, la brume de la mer ne vide pas le robot. Elle a sa **propre réserve** (3 crans visibles) ; on la remplit en y versant la lumière reprise d'une lanterne, au passage du faisceau du Phare, ou près d'une bouée allumée. Si elle s'éteint en mer, c'est la batterie du robot qui prend le relais.
- **Repères en mer** : les bouées-lanternes (points de recharge, routes), le faisceau du Phare, les rochers, les épaves.
- **Mort loin de l'île 1** : réveil au berceau ; la barque revient **cachée dans la crique** de l'île 1, toujours à flot.
- **Accès aux îles** : tout est ouvert dès qu'on a la barque ; **seul le savoir bloque** (voir `ENQUETE.md`).

## Les cycles du monde (permanents, jamais remis à zéro)
| Cycle | Durée | Ce qu'il change |
|---|---|---|
| **La marée** | 8 min (4 basse, 4 haute) | Chaussées, gués, grottes et épaves émergent à marée basse. La mer reste basse le temps de **six tours du faisceau**. |
| **Le faisceau du Phare** | 40 s par tour (une fois rallumé) | La brume recule là où il passe. Orienté (lentille), il vise une île. |
| **La lune** | 24 min | À la **pleine lune**, la mer descend **plus bas que tout** (le vieux port de la Colonie), et la lentille du Phare révèle l'île cachée. |

Apprendre les cycles fait partie du savoir.

---

## Direction artistique
- Diorama low-poly en blocs, vue de haut (caméra iso : fov 32, pitch 42°, yaw 45°), flou « maquette ».
- Palette calme : vert sauge, pierre beige, bleu brumeux, rose poudré, ombres lavande.
- **Les Semeurs étaient très grands** (hauts et fins, longs bras, tête creuse en cage où brillait leur lumière) : leurs lieux sont **à leur échelle**, et le petit robot s'y sent minuscule.
- **Deux mondes visuels** : le monde éclairé des Semeurs (chaud, doré, vide) et le monde du peuple caché (nuit, bleu-vert phosphorescent, vivant).
- **Les squelettes** des Semeurs : morts en pleine vie, couverts de mousse, jamais glauques.

## Son
- Piano doux et nature ; la musique est en **couches** qui s'ajoutent quand on allume.
- Une **seconde musique**, celle du peuple caché (cristalline, aquatique), qui apparaît quand on éteint.

## Technique
- Godot 4.7, PC clavier.
- Tout en scènes et ressources visibles dans l'éditeur ; scripts courts.
- Chaque île est sa propre scène (`scenes/islands/island_0X.tscn`) ; les îles lointaines sont des silhouettes légères, chargées en entier quand on approche.
- **L'horloge du monde** (`WorldClock`, autoload) donne l'heure des cycles à tout le monde (`WorldClock.tide()`, `WorldClock.beam_angle()`, la lune).
- Les états qui se réinitialisent à chaque boucle sont regroupés dans `Loop`.
