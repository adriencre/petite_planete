# Petite Planète — document de design (v3)

> v3 (2026-11-14) : refonte complète. Jeu d'**exploration et de savoir** façon Outer Wilds,
> mais la boucle est liée à la **batterie** du robot, pas au temps.
> L'ancienne histoire (enfant, langue inventée) est abandonnée.
> Le monde de l'ombre (les Lueurs comme peuple, les 9 îles côté ombre) est décrit dans **`MONDE_OMBRE.md`**.
> **Le jeu de base** (toutes les îles côté lumière : la mer, la barque, les cycles, les énigmes liées) est dans **`ARCHIPEL.md`** ;
> chaque île a son document complet (`ILE_01_REVEIL.md`, `ILE_02_PHARE.md`, …). On développe tout le jeu de base **avant** le monde de l'ombre des îles 2 à 9.

## En une phrase
Un petit robot jardinier rallume les lanternes d'un archipel noyé dans une brume grise… et comprend peu à peu que cette brume est la vie de la planète, et que la lumière l'a presque tuée.

## Piliers
1. **Le savoir est la seule vraie progression.** Le monde est ouvert ; ce qui bloque, c'est ce qu'on ne sait pas encore. Un joueur qui sait peut aller presque partout très tôt.
2. **Chill mais exigeant.** Pas de danger, pas d'ennemis. Beaucoup de petites énigmes gratifiantes, quelques grandes énigmes vraiment exigeantes.
3. **Le monde ment par omission.** Tout ce que le joueur croit au début (la lumière est bonne, la brume est morte, les corps sont d'autres robots) est faux.
4. **Beau, calme, mélancolique**, avec une fin dont on se souvient.

## Le moteur : batterie, brume et berceau
### Batterie
- Le robot a une **batterie** (jauge discrète sur l'antenne, sans texte).
- **La brume la vide** ; **la lumière la recharge** (lanternes allumées, pierres-soleil).
- **Allumer une lanterne coûte de la batterie**, mais elle éclaire le chemin et devient un point de recharge.
- **Reprendre la lumière** (dès l'île 1, `E` sur une lanterne allumée) : la lumière descend en spirale dans l'antenne, la batterie remonte, la lanterne s'éteint et **sa zone se rendort**. On peut la rallumer. Au début c'est de la logistique ; plus tard, **éteindre devient le vrai geste**.

### Le mode nuit (secret, touche `N`)
- Jamais indiqué à l'écran. Indices : un vieux croquis du carnet (robot antenne éteinte sous la lune, touche « N » griffonnée), la page 7 de la Gardienne.
- Le robot **éteint sa propre antenne** : la brume **ne le vide plus** (elle se nourrit de lumière), la lumière ne le recharge plus (batterie figée), et **les Lueurs sont pleinement visibles**.
- En contrepartie : **aucune lumière** (ni allumer, ni reprendre, ni pierre-soleil). `N` à nouveau pour rallumer.
- Conséquence : la brume épaisse devient traversable dans le noir (2e route secrète vers la barque).

### La boucle
- La conscience du robot vit dans le **berceau**, une machine des Semeurs dans l'abri de l'île 1. Le robot n'est qu'un **corps** piloté par l'antenne.
- **Batterie vide** : le corps s'éteint **sur place**, et la conscience se réveille dans un **corps neuf**, couché dans l'abri (la scène de réveil de chaque boucle).
- **Les lanternes allumées avec cette batterie s'éteignent** : le monde se rendort tout seul.
- **Les anciens corps restent** là où ils se sont éteints, d'une boucle à l'autre.
- Le robot **garde son savoir** (chemins, solutions, ce qu'il a lu), mais **pas le souvenir d'avoir été ces corps** : pour lui, ce sont d'autres robots.
- Ce qui persiste d'une boucle à l'autre : le savoir du joueur, le carnet, les anciens corps. Tout le reste se réinitialise.

### Voir à batterie basse
- (Première découverte, accidentelle. Le mode nuit est la version volontaire.)
- Quand la batterie est presque vide, l'antenne s'assombrit et **les Lueurs deviennent visibles dans la brume** : chemins, créatures, messages.
- Il faut donc **prendre un risque pour voir la vérité**. S'éteindre exprès au bon endroit fait partie des secrets.

## Le carnet
- **Carte de l'île** dessinée à l'encre, avec les lieux découverts.
- **Croquis automatiques** des lieux et des créatures (le bestiaire des Lueurs, croquées dans le noir).
- **Pages du journal de la Gardienne**, en français.
- **Pas de langue inventée.**

## Énigmes
- **Petites (partout, gratifiantes)** :
  - logistique de batterie (quelles lanternes allumer ou reprendre pour atteindre un point) ;
  - plantes (racines, lianes) ;
  - éteindre au bon endroit pour révéler un passage.
- **Grandes (exigeantes)** : elles combinent plusieurs îles, plusieurs vérités et la gestion de la batterie, jusqu'à la traversée finale.

## La vérité cachée
- La planète vit naturellement dans la pénombre. Sa vie, ce sont **les Lueurs** : une brume d'organismes minuscules qui **ne brillent que dans le noir**.
- Les Semeurs, arrivés d'ailleurs, ne voyaient rien et ont planté des **lanternes partout**. **Éblouies, les Lueurs ont cessé de briller** et sont devenues la « brume grise ».
- **La brume vide la batterie parce qu'elle se nourrit de lumière** : elle a faim, les lanternes l'affament.
- Les **arbres roses** sont une espèce importée, qui exige une lumière constante.
- Le **« pollen » qui rendait les Semeurs malades** était les **spores des Lueurs**, qui réagissaient à la lumière : la planète essayait de leur parler.
- Le **berceau** puise son énergie au fond du **Cœur**, dans la plus grande poche de Lueurs. **Chaque renaissance coûte un peu de vie à la planète.**
- Les anciens corps sont **le robot lui-même**. Les Lueurs les recouvrent et brillent dessus : **ses morts les ont nourries pendant des siècles.**

## Fin
Une dernière boucle, avec tout ce que l'on sait :
1. traverser l'archipel en **éteignant les lanternes une à une** (en reprenant leur lumière), dans un ordre qui permet à la batterie de tenir jusqu'au bout ;
2. atteindre le Cœur et **éteindre le berceau**, en sachant qu'il n'y aura plus de retour ;
3. le noir total, le silence…
4. … puis **les Lueurs se rallument d'elles-mêmes** : forêts phosphorescentes, créatures qui volent, vagues lumineuses, et la musique qui revient autrement ;
5. la batterie s'épuise ; les Lueurs s'enroulent autour du robot, son corps devient un nid lumineux. La caméra recule : **la planète brille dans l'espace comme un bijou.**

**Fin secrète** (toutes les pages du journal) : après le générique, la Gardienne, assise dans le noir sur son île, entourée de Lueurs, qui sourit.

## Deux moitiés, deux visages
- **Visage de la lumière** (antenne allumée) : le monde des Semeurs, mort mais éclairé.
- **Visage de l'ombre** (`N`, accessible dès le début) : le monde des Lueurs, vivant mais caché : maisons, familles, paroles.
- Les Lueurs **parlent en mots de lumière, en français** : bribes à batterie basse, phrases complètes antenne éteinte. Leurs paroles importantes se recopient dans le carnet (« Paroles »).
- **1re moitié, « Rallumer »** : on croit qu'il faut rallumer l'archipel ; les Lueurs fuient le « Petit-Jour ».
- **Bascule sur l'île 9** : la Gardienne révèle tout.
- **2e moitié, « Éteindre »** : chaque peuple doit être prêt à se rallumer quand le berceau s'arrêtera (confiance, mission, ordre des lanternes). La fin dépend des peuples prêts.

## Monde : l'archipel (9 îles)
| Île | Côté lumière | Côté ombre (voir `MONDE_OMBRE.md`) |
|---|---|---|
| 1. **Le Réveil** | prologue, berceau, barque cachée, premier corps | la Pouponnière, le Compteur |
| 2. **Le Phare** | grande lanterne des Semeurs, 1re page de la Gardienne | les Aveugles du Phare |
| 3. **Le Marais** | brume très épaisse | le Village des Roseaux, Mère Brume ; ponts de Lueurs |
| 4. **Le Village des Semeurs** | maisons vides, fresques, « maladie du pollen » | les Locataires ; souvenirs rejoués des Semeurs |
| 5. **Le Verger rose** | arbres roses ; un coin mort où la brume brille | les Jardinières, Pétale ; le dilemme des arbres |
| 6. **L'Île Engloutie** | une tache sombre dans la mer | la Cité d'en bas, le Conseil des Marées ; le récif |
| 7. **La Nef** | l'épave du vaisseau des Semeurs | les Fossiles ; l'ordre laissé au robot |
| 8. **Le Cœur** | visible dès le début ; le berceau, ses câbles, la fin | la Poche, mer de Lueurs pâles |
| 9. **L'île de la Gardienne** | sans lanterne, invisible antenne allumée | la Gardienne ; la bascule |

**La barque** est cachée sur l'île 1, au fond d'une crique noyée de brume. Le chemin normal est de rallumer l'île pour pouvoir l'atteindre. Un curieux qui trouve la pierre-soleil cachée peut y arriver en quelques minutes. Ensuite, l'archipel entier est ouvert.

## Direction artistique
- Diorama low-poly en blocs vu de haut, flou « maquette ».
- Palette calme : vert sauge, pierre beige, bleu brumeux, rose poudré, ombres lavande.
- **Deux mondes visuels** : le monde éclairé des Semeurs (chaud, doré) et le monde des Lueurs (sombre, bleu-vert phosphorescent), révélé peu à peu.

## Son
- Piano doux et nature. La musique est en **couches** qui s'ajoutent quand on allume.
- **Plus tard dans le jeu, une seconde musique**, celle des Lueurs (cristalline, aquatique), qui apparaît quand on éteint.

## Technique
- Godot 4.7, PC clavier.
- Tout en scènes et ressources visibles dans l'éditeur ; scripts courts.
