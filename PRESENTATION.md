# Petite Planète — présentation complète du jeu

> Un jeu d'exploration et d'enquête, calme et mélancolique, fait avec Godot.
> Ce document explique **tout** le jeu, **fin et secrets compris**, pour qu'on puisse en discuter.
> Réécrit le 2026-11-16 avec toutes les décisions des documents d'îles (`ILE_01` à `ILE_07`), de `DESIGN.md`, `ENQUETE.md`, `DA.md` et `TOILE_ENQUETE.md`.

---

## 1. L'idée en une phrase

Un petit robot jardinier se réveille sur un archipel noyé de brume, où tout est construit, éclairé… et vide. Il enquête : **où sont les Semeurs ?** Il finit par comprendre qu'ils sont morts de leur propre lumière, qu'un peuple vit caché dans la brume depuis le début… et que ce peuple le fait revivre à chaque mort, au prix de sa propre vie.

## 2. Le pitch

Tu incarnes un petit robot. Tu te réveilles dans un abri, couché dans une sorte de berceau, sur une île grise. À côté de toi, un papier : « Garder la lumière jusqu'à notre retour. — Ysolde, Commandante ». Autour : des lanternes, des chemins, des maisons, des serres, un phare au loin… Tout a été construit par un peuple étrange, **les Semeurs**. Mais il n'y a plus personne.

Une seule question guide tout le jeu : **« Où sont les Semeurs ? »**

Pour y répondre, tu explores librement un archipel de **7 îles** en barque. Tu fouilles leurs maisons, tu lis leurs lettres, tu résous leurs mécanismes, et tu reconstitues peu à peu ce qui s'est passé. Personne ne te dit quoi faire ni où aller : c'est ta curiosité qui fait avancer l'histoire.

## 3. Les inspirations et les piliers

La référence principale est **Outer Wilds**.

1. **Le savoir est la seule vraie progression.** Le monde est ouvert, rien ne s'achète ni ne s'équipe. Un joueur qui sait peut aller presque partout très tôt, et même finir le jeu très vite.
2. **Une grande enquête.** Une question, quatre fils qui traversent les îles, une vérité reconstituée par morceaux, dans l'ordre que le joueur choisit.
3. **Beaucoup d'énigmes variées sur chaque île**, mélangées : le temps et les cycles, l'observation et les lieux cachés, les mécanismes et les codes.
4. **Chill mais exigeant.** Pas de danger, pas d'ennemis, pas de combat.
5. **Le monde ment par omission.** Ce que le joueur croit au début est faux.
6. **Beau, calme, mélancolique**, avec une fin dont on se souvient.

---

## 4. Comment on joue

### En première personne
On voit par les yeux du robot. **Zéro interface à l'écran** : l'antenne du robot pend devant ses yeux, comme la lumière d'un poisson-lanterne. Son ampoule est à la fois **la jauge de batterie** et une vraie lumière qui éclaire autour de lui. Ses bras sont dans le champ ; il tourne la tête vers ce qui est intéressant.

### La batterie : vivre de lumière
- **La brume le vide**, doucement mais sûrement.
- **La lumière le recharge** : lanternes allumées, pierres-soleil.
- **Allumer une lanterne coûte de la batterie** : le robot s'accroupit, sort un **câble de son poignet**, le branche dans la prise de la lanterne, et des pulsations dorées passent de lui à elle. La lanterne s'ouvre en crans, et la zone grise autour se réveille en vague de couleur. Pas de magie : des câbles, des prises, des mécanismes.
- **Reprendre la lumière** : le même geste, dans l'autre sens. La batterie remonte, la lanterne s'éteint, sa zone se rendort.

La batterie n'est pas un type d'énigme, c'est une **contrainte partout** : jusqu'où je peux aller dans la brume ? Est-ce que j'allume ici pour pouvoir revenir ?

> 💡 **Les Semeurs vivaient exactement comme ça.** Le robot est fait à leur image. Le joueur vit leur mort sans le savoir.

### La boucle : mourir et revenir
- La conscience du robot vit dans le **berceau** de l'abri. Le robot n'est qu'un **corps**.
- Batterie vide : le corps s'éteint **sur place**, et la conscience se réveille dans **un corps neuf**, dans l'abri.
- Le monde se remet à zéro : lanternes, mécanismes, barque (qui revient cachée dans la crique de l'île 1).
- Ce qui reste : **ce que le joueur sait**, le **carnet**… et **les anciens corps**, là où ils sont tombés.
- Le robot croit que ces corps éteints, qu'il croise partout, sont d'autres robots. Ils portent pourtant **la même écharpe, avec le même nœud**.

### Le monde de la brume : invisible jusqu'à la fin
- Un peuple vit dans la brume, mais **le robot ne le voit pas**. Il n'y a pas de bouton, pas de mode secret.
- Seule exception : **quand la batterie est presque vide**, des formes floues apparaissent dans la brume, et quelques mots de lumière flottent (« …il… revient… »). Assez pour intriguer, jamais assez pour comprendre.
- Le robot ne verra ce peuple **qu'une fois accepté par lui**, c'est-à-dire **à la toute fin**.

### Le carnet : juste ce qu'on a vu
Il garde les lieux visités, les textes lus, les cartes, les croquis, les dessins d'Aube, les lettres des Semeurs. **Aucune flèche, aucune question, aucun objectif** : le carnet n'indique jamais où aller. Le joueur fait les liens dans sa tête.

### La mer et la barque
- Une seule mer, les 7 îles dedans, visibles au loin. Navigation libre, lente, avec de l'inertie.
- En mer aussi, la brume vide la batterie (légère, ou très épaisse autour de certaines îles).
- **La lanterne de la barque** protège le robot tant qu'elle brille. Elle a sa propre réserve (3 crans), qu'on remplit avec la lumière reprise d'une lanterne, au passage du faisceau du Phare, ou près d'une bouée allumée.
- **Tout l'archipel est ouvert dès qu'on a la barque.** Seul ce qu'on ne sait pas encore bloque.

### Les cycles du monde
Trois horloges tournent en permanence, sans jamais se remettre à zéro (même quand on meurt) :

| Cycle | Durée | Ce qu'il change |
|---|---|---|
| **La marée** | 8 min (4 basse, 4 haute) | Sur certaines îles seulement (Phare, Colonie, Nef) : chaussées, gués, grottes et épaves sortent de l'eau à marée basse. |
| **Le faisceau du Phare** | 40 s par tour (une fois rallumé) | La brume recule là où il passe. Orienté, il vise une île. |
| **La lune** | 24 min | À la pleine lune, la mer descend **plus bas que tout** : le vieux port de la Colonie sort de l'eau. Et le Phare, éteint, peut révéler l'île cachée. |

---

## 5. L'histoire : ce qui s'est vraiment passé

### Les Semeurs
Un peuple **venu de l'espace** : la Nef est leur vaisseau, échoué depuis leur arrivée. Leur monde d'origine, une **grosse planète**, est toujours visible dans le ciel. Ils mesurent **2,50 à 3 m** : un peu plus grands que le robot (1,90 m), fins, avec de longs bras et **une tête creuse en forme de cage** où brillait leur lumière. Leur corps est organique, comme du bois clair et de la nacre. Leurs maisons sont poussées plutôt que construites, et un peu trop grandes pour le robot.

Ils **vivaient de lumière, comme le robot** : la brume les vidait, la lumière les rechargeait. Alors ils ont allumé, toujours plus. Des lanternes partout, une **Centrale** sous la mer pour toutes les alimenter, et de plus en plus **peur du noir**.

| Nom | Rôle | Qui elle / il était | Où on le retrouve |
|---|---|---|---|
| **Iris** | la Gardienne | Surveillait toutes les lanternes depuis le Phare. Précise, fière… puis elle a vu ce que personne ne voyait. | Devenue une habitante de la brume. Sa maison sur l'île cachée. |
| **Ysolde** | la Commandante | La peur faite cheffe : « Une lanterne par foyer »… « Toute ombre est un danger ». | Au poste de pilotage de la Nef. |
| **Tavin** | l'Ingénieur | A construit les lanternes, la Centrale et le berceau. Prévenait que « la centrale ne tiendra pas ». | Au pupitre de la Centrale, la main sur le levier poussé au maximum. |
| **Saule** | la Médecin | Soignait les malades avec de la lumière… et doutait. | À son bureau de la Quarantaine, une lettre d'Iris à la main. |
| **Orme** | le Pilote | A envoyé 612 appels au secours vers leur planète. Jamais de réponse. | Au poste de pilotage de la Nef, à ses commandes. |
| **Aube** | l'Enfant | Voyait des « amis » dans la brume et les dessinait. | Au coin noir de la Colonie : elle n'est jamais montée dans la Nef. |

### Le peuple de la brume
- Une vie minuscule qui **ne brille que dans le noir**. Seules, des grains de poussière lumineuse ; ensemble, elles forment **des êtres**, avec des maisons, des familles, des enfants.
- Elles se nourrissent de **lumière douce**. Une lumière forte et fixe les **aveugle**, puis les tue. Autour de chaque lanterne, chez elles, il n'y a que de la cendre.
- **Affamées par les lanternes**, elles ont fini par vider tout ce qui brille… les Semeurs compris. Ce n'était pas une maladie : c'était leur faim.
- Leurs mots : le robot est **le Petit-Jour** ; les lanternes, **les Soleils-Fixes** ; les Semeurs, **les Grands-Aveugles** ; le berceau, **la Bouche** ; Iris, **Celle-qui-a-soufflé** ; mourir se dit **rentrer**.

### La grande nuit
Il y a **des siècles**, Ysolde ordonne le départ : tout le monde à la Nef. Pour décoller, la Nef doit être chargée à fond, et Tavin pousse la Centrale **au maximum toute la nuit**.

Iris a compris que cette nuit-là tuerait **tout le peuple de la brume**. Depuis longtemps, elle avait fabriqué en secret un **boîtier** qui désactive la barrière de sécurité protégeant les câbles de la Centrale.

**Elle descend à la Centrale, active son boîtier, et coupe tous les câbles un par un.** Elle sait qu'elle se tue elle-même et qu'elle tue tous les siens.

Toutes les lumières s'éteignent d'un coup. La Nef s'arrête à 96 % de charge. La brume affamée vide tous les Semeurs **là où ils étaient** : dans la file d'embarquement, à leur poste, dans leur lit. On retrouve leurs **squelettes**, couverts de mousse et de fleurs, morts en pleine vie, jamais glauques.

**Iris épargne un seul câble : celui du berceau.** Elle n'a pas le cœur de tuer le petit jardinier, qui n'a rien choisi. Elle pose son boîtier au pied du câble et se tourne vers la brume : **« Gardez le petit en vie. »**

Le peuple de la brume l'accepte parmi eux. Elle devient l'une d'eux.

### La promesse
Le peuple de la brume tient toujours ses promesses. Depuis des siècles, **à chaque mort du robot, il donne un peu de sa propre lumière** à la ligne du berceau pour le faire revenir. Même s'il a peur de lui, même si le robot rallume sans cesse les lanternes qui le brûlent, même s'il en meurt un peu à chaque fois.

C'est pour ça que « **il revient toujours** ».

### Ce que le joueur croit, et ce qui est vrai
| Au début, on croit… | En vrai… |
|---|---|
| « Ils sont partis » (valises « Nef », « jusqu'à notre retour ») | Ils sont tous morts, la même nuit. La Nef n'est jamais repartie. |
| La brume est une chose morte et hostile | C'est un peuple vivant, affamé par la lumière. |
| Les corps éteints sont d'autres robots | Ce sont tous les anciens corps du joueur. |
| Rallumer les lanternes, c'est réparer le monde | C'est exactement ce qui a tué les Semeurs. |
| Je reviens grâce au berceau | Je reviens grâce au sacrifice du peuple de la brume. |

**La fausse piste est construite exprès** : les premières îles sont vides et rangées. **Les squelettes n'apparaissent qu'au milieu du jeu** (la Quarantaine, la Nef), et c'est là que vient le choc.

### Les 4 fils de l'enquête
Chacun traverse plusieurs îles (le détail est dans `TOILE_ENQUETE.md`) :
1. **La maladie et les lanternes** : du registre du Phare au carnet d'Iris, on comprend qu'ils se sont tués eux-mêmes.
2. **La Nef et l'appel au secours** : du papier d'Ysolde à la boîte noire de la Nef, « ils sont partis » s'effondre.
3. **Le berceau et les corps** : de l'écharpe identique au compteur de la Centrale, qui augmente de 1 à chaque mort.
4. **La Gardienne** : de la page 7 au carnet de sa maison cachée.

---

## 6. L'archipel, île par île

| # | Île | Ce qu'il faut savoir pour y entrer |
|---|---|---|
| 1 | **Le Réveil** | rien, on y commence |
| 2 | **Le Phare** | la marée : la chaussée n'est praticable qu'à marée basse |
| 3 | **La Colonie** | rien |
| 4 | **La Quarantaine** | traverser la brume très épaisse (lanterne de la barque bien remplie, ou faisceau du Phare pointé sur l'île) |
| 5 | **La Nef** | deux portes à code, trouvés à la Colonie et à la Quarantaine |
| 6 | **La Centrale** | la porte du vieux port, qui ne sort de l'eau qu'à la pleine lune |
| 7 | **L'île cachée** | le Phare **éteint**, tourné vers le cran sans nom, une nuit de pleine lune |

### 1. Le Réveil — l'île du robot
Le prologue : 30 à 45 min la première fois, 5 min pour qui sait. On apprend sans un mot la batterie, allumer, reprendre la lumière, mourir et revenir.
- **L'abri** et le berceau, avec **le papier d'Ysolde** juste à côté.
- **L'atelier des robots**, caché derrière une cascade, un peu trop grand pour le robot : le moule, les pièces… et **la page 7** d'Iris : « Elles ne sont pas la brume. Elles sont dans la brume… Suis-les. Elles connaissent le chemin de chez moi. — G. »
- **La crique** : le premier ancien corps (même écharpe, même nœud) et la **barque** cachée sous les racines.
- Pas de squelettes, pas de marée.

### 2. Le Phare — le poste d'Iris
Un phare sur un rocher coupé du monde par la marée. Il ne fabrique pas sa lumière : il la **rassemble**, grâce aux miroirs de trois caps.
- **Atteindre le Phare** (marée) : la chaussée est noyée à marée haute et couverte de brume épaisse à marée basse. « Basse mer : six tours du faisceau. Pas un de plus. »
- **Rallumer le Grand Phare** (miroirs) : Cap Est → Cap du Large → Cap Ouest → lentille. Du sommet, le carnet dessine la carte de l'archipel.
- **La clé de la salle des cartes**, restée dans l'épave d'un ravitailleur. Derrière : le **registre des lanternes** (« Colonie : 40… 90… 160… 310. ») et une ligne sans nom, juste une petite maison sans lanterne.
- **La salle des machines** : remonter les engrenages pour pouvoir viser avec la lentille.
- **La chambre d'Iris**, par la lucarne : une lanterne débranchée, un dessin d'Aube (« Pour Iris. Nos amis du noir. »), et une lettre jamais envoyée : « Ysolde, … J'ai vu ce qu'elles font là-bas. Demande à Saule ce qu'elle a vu, elle. Éteins une seule nuit, avec moi. »
- **La lunette d'Iris** : chaque cran cadre une île… sauf un, qui regarde la mer vide.
- **La crypte**, sous le phare : un câble tiède qui file vers la Centrale. « Ligne du berceau. Prioritaire. Ne jamais couper. »

### 3. La Colonie — la ville des Semeurs
Une baie en croissant. La ville monte de vieilles rues (une lanterne par maison) vers des rues récentes (dix lanternes, fenêtres murées) : **on voit la peur grandir en marchant**. Toutes les valises sont étiquetées « Nef ». Une boîte à musique d'enfant pour seule musique.
- **La maison d'Aube** (lieux cachés) : fermée de l'intérieur ; on suit ses dessins jusqu'à ses cachettes. Son carnet : « Papa dit on part ce soir avec la Nef… Iris elle les voit aussi… je vais leur dire au revoir au coin noir. après je pars. promis. »
- **La rue des Trois-Soleils** (mécanisme) : trois affiches déchirées d'Ysolde donnent chacune un morceau du motif ; on allume exactement les 3 bonnes lanternes sur 9 pour ouvrir la maison commune (ordres d'Ysolde, lettres de Tavin, plan de l'archipel avec une tache d'encre au nord-ouest).
- **Le jardin du haut** (temps) : le carillon des marées, l'écluse, les arbres roses qui penchent tous vers une lampe-mère cachée.
- **Le vieux port** (temps, le plus difficile) : il ne sort de l'eau qu'à la pleine lune. On y voit une fresque : **le jour de leur arrivée, la brume brillait**. Et une porte : « Entrée de service. Jardinier. »
- **Le coin noir** : en suivant le dernier dessin d'Aube, on la trouve, assise, seule. Le seul squelette de la ville.
- La comptine de l'école (« rose au matin, bleu à midi, couleur d'or le soir, et noir quand on dort ») ne sert à rien ici… mais à la Nef.

### 4. La Quarantaine — l'île blanche
L'hôpital de Saule, dans la brume la plus épaisse de l'archipel. Des draps blancs suspendus partout, un silence épais. **Les premiers squelettes** : les malades dans leurs lits, sous les lanternes qui devaient les soigner. L'île ne donne **qu'un doute**.
- **Les cordes de Saule** : dans le labyrinthe de draps, on suit la corde à deux nœuds (« Un nœud : les lits. Deux nœuds : mon bureau. Trois nœuds : le cimetière. »). Un ancien corps du robot, perdu au milieu, montre ce qui arrive sinon.
- **Le lit qui manque** : 12 fiches de malades, mais seulement 11 lits. Derrière un rideau, une porte.
- **La double porte** : la première ne s'ouvre que si le couloir est éclairé, la seconde que s'il est noir. On allume, on entre, on reprend la lumière. Derrière : **la salle noire**, un lit vide, et une note : « Lit 12. Jour 9 : il ~~~~ Il survit ? Je n'ose pas l'écrire. »
- **Le cimetière** : sur chaque stèle, de petites lanternes et des encoches gravées. Les plus récentes ont beaucoup de lanternes et presque pas d'encoches. Rien ne l'explique.
- **Saule**, morte à son bureau, tient une lettre d'Iris : « Le Phare ne chante que quand il dort. Une nuit de grosse lune, laisse-le dormir, tourné vers rien, et tu verras où je suis. »
- **Le sémaphore** : le dernier message de Saule à la Nef, « Gardez-nous une place », jamais répondu. Son motif : gauche, droite, milieu, droite.

### 5. La Nef — le vaisseau
La carcasse rouille et corail du vaisseau, échouée et penchée. **Le grand choc** : sur la passerelle, une longue file de squelettes avec leurs valises. Parmi eux, le père d'Aube, une petite valise vide à côté de lui.
- **La porte de la comptine** : quatre lanternes colorées, à allumer dans l'ordre rose, bleu, or… et noir (la lanterne au verre noir ne se voit pas allumée).
- **La porte des signaux** : on rejoue le message de Saule. La Nef le reçoit enfin, des siècles trop tard. Derrière : le poste de pilotage, Orme à ses commandes, Ysolde debout derrière lui.
- **La soute à marée basse** : par la brèche, dans les couloirs penchés, jusqu'aux pousses d'arbres roses prêtes pour le voyage. Un ancien corps noyé montre ce qui arrive si on traîne.
- **La boîte noire** : on y branche son câble, au prix de beaucoup de batterie. Les dernières minutes se rejouent en lumière : tout le monde embarque, la charge monte… 96 %… et tout s'éteint d'un coup. **Ils sont tous morts la même nuit.**
- Le journal d'Orme : « Appel 1. Pas de réponse. … Appel 612. Pas de réponse. Ce soir, on part. On ira les chercher nous-mêmes. »

### 6. La Centrale — sous la mer
Turquoise et nacre, sous la mer et sous terre. On y entre par la porte du vieux port, à la pleine lune : **le robot est la clé**, il branche son câble dans la prise de service.
- **La galerie des câbles** : un câble par île, tous froids. Un seul est tiède, celui du berceau, avec un petit compteur qui affiche un très grand nombre… et qui **augmente de 1 à chaque mort du robot**.
- **La salle de contrôle** : Tavin au pupitre, la main sur le levier poussé au maximum. Ses notes : « Ordre d'Ysolde : tout pour la Nef… Iris est là. Elle ne dit rien. Elle regarde la barrière. »
- **L'enregistrement de la grande nuit** : on y branche son câble. On voit Iris activer son boîtier, couper tous les câbles, épargner celui du berceau, poser le boîtier à son pied, et dire à **rien** (à la brume qu'on ne voit pas) : « Gardez le petit en vie. »
- **La main de Tavin** : la porte du fond n'ouvre que « machine à l'arrêt ». Il faut déplacer doucement la main de Tavin et ramener le levier à zéro.
- **La barrière** : derrière, les câbles coupés, et celui du berceau, intact. Le boîtier d'Iris est toujours à son pied, sous la mousse.

### 7. L'île cachée — la maison d'Iris
On ne la voit jamais, sauf si l'on assemble des indices de quatre îles : une nuit de pleine lune, au Phare, la lentille **tournée vers le cran sans nom et éteinte** (le Phare « dort ») concentre le clair de lune et révèle l'île. Un **chemin de lune** se dessine sur la mer, qu'on suit en barque, **lanterne de la barque éteinte**, avant que la pleine lune ne passe.
- Une petite île sans aucune lanterne, couverte de plantes qui brillent doucement. **Pas d'énigme** : la trouver était l'énigme.
- **Son métier à tisser**, avec le même motif que l'écharpe du robot : c'est Iris qui l'a tissée.
- **Son carnet**, qui donne toutes les réponses : la nuit où elle a soufflé sa lanterne par fatigue et vu la brume s'allumer, leur faim et la nôtre, Ysolde qui a eu peur, le boîtier fabriqué en secret, « Ce soir, je vais couper. Tout. … Le petit jardinier n'a rien choisi, lui. Lui, je le laisserai. »
- Et une dernière page, écrite après, d'une encre qui brille doucement : **« Je leur ai demandé de garder le petit. Je n'aurais pas dû. »**
- Iris elle-même n'est pas visible : elle est une habitante de la brume.

---

## 7. La fin

- **Il n'y a qu'une seule enquête**, libre du début à la fin. **Rien ne dit au joueur quoi faire.**
- **La raison de finir** : le robot comprend qu'il ne revient pas grâce à une machine, mais grâce au **sacrifice du peuple de la brume**, qui tient une promesse faite à Iris. Chacune de ses morts leur coûte.
- **Le dernier geste** : à la pleine lune, entrer dans la Centrale, ramener le levier de Tavin à zéro, retrouver le boîtier d'Iris au pied du câble, l'activer… et **couper la ligne du berceau**, là où Iris a coupé les autres. Le robot termine ce qu'elle n'avait pas pu faire.
- **Ce qui se passe** : le câble s'éteint. Au loin, le berceau de l'île 1 reste noir. En coupant, le robot est **accepté** par le peuple de la brume, et **pour la première fois, il les voit**, partout autour de lui. Iris vient s'asseoir à côté de lui.
- **Une petite cinématique** : le robot **vit sa vie dans sa nouvelle famille, la brume**. On découvre enfin tout ce qui était caché depuis le début : la ville des Pins de l'île 1, les amis d'Aube, les habitants de chaque île.
- **La fin secrète** : si le joueur a lu le carnet d'Iris avant de couper, elle lui dit **« Merci. »** en s'asseyant. Sinon, elle s'assoit en silence.
- **Le chemin le plus court**, pour qui sait tout : prendre la barque, aller au vieux port de la Colonie à la pleine lune, entrer dans la Centrale, couper. Un joueur qui sait peut finir en quelques minutes.

---

## 8. L'ambiance

- **Visuel** : un monde 3D doux, aux pastels lumineux, « à la Outer Wilds ». Formes rondes, pas de blocs, pas de contours ; des surfaces jamais unies (mousse, strates, fleurs). Un ciel pêche, rose et lavande, avec la grosse planète des Semeurs. Une mer turquoise. Un cycle jour/nuit lent et toujours beau.
- **Deux mondes** : celui des Semeurs, **chaud, doré et vide**, qu'on explore tout le jeu ; celui du peuple de la brume, **bleu et turquoise, vivant**, qu'on ne découvre vraiment qu'à la fin.
- **Chaque île a sa teinte** : vert tendre et rose (Réveil), or et bleu ciel (Phare), ocre et pêche (Colonie), blanc et lavande (Quarantaine), rouille et corail (Nef), turquoise et nacre (Centrale), bleu nuit et or pâle (île cachée).
- **Son** : piano doux et nature, en couches qui s'ajoutent quand on rallume. Une boîte à musique d'enfant à la Colonie. Le silence étouffé de la Quarantaine.
- **Durée visée** : 8 à 12 heures.
- **Plateforme** : PC, clavier, fait avec Godot 4.7.

## 9. Où en est le projet

- ✅ Toute l'histoire, les règles et la fin sont décidées.
- ✅ Les 7 îles sont conçues : énigmes, indices, textes (`ILE_01` à `ILE_07`).
- ✅ La toile de l'enquête relie tous les indices sur une page (`TOILE_ENQUETE.md`).
- ✅ La direction artistique v5 est posée (`DA.md`), avec une scène de test jouable.
- ⏳ Le développement repart de zéro (v5). L'île 1 de l'ancien prototype est à adapter (retirer le mode nuit, la ville des Pins devient la matière de la fin).
- ⏳ Le côté brume de chaque île n'est montré qu'à la fin : à concevoir avec la cinématique.

## 10. Des questions pour en discuter

- Le moment où l'on comprend que les corps sont les siens (le compteur de la Centrale) : trop tard, ou juste au bon moment ?
- Est-ce que l'idée « rallumer, c'est l'erreur » se sent assez tôt, sans être donnée ?
- Le peuple de la brume reste invisible presque tout le jeu : les bribes à batterie basse suffisent-elles à le rendre présent ?
- La fin (couper son propre berceau pour libérer ceux qui le font vivre) : triste, belle, les deux ?
- Trouver l'île cachée demande des indices de quatre îles : trop difficile, ou le bon défi pour une fin secrète ?
