# Petite Planète — présentation complète du jeu

> Un jeu d'exploration et d'enquête, calme et mélancolique, fait avec Godot.
> Ce document explique **tout** le jeu, **fin et secrets compris**, pour qu'on puisse en discuter ensuite.

---

## 1. L'idée en une phrase

Un petit robot jardinier se réveille sur un archipel noyé de brume, où tout est construit, éclairé… et vide. Il enquête : **où sont les Semeurs ?** Il finit par comprendre qu'ils sont morts de leur propre lumière, et qu'un peuple vit caché dans la brume depuis le début.

## 2. Le pitch

Tu incarnes un petit robot. Tu te réveilles dans un abri, couché dans une sorte de berceau, sur une île grise. Autour de toi : des lanternes, des chemins, des maisons, des serres, un phare au loin… Tout a été construit par un peuple de géants, **les Semeurs**. Mais il n'y a plus personne.

Une seule question guide tout le jeu : **« Où sont les Semeurs ? »**

Pour y répondre, tu explores librement un archipel de **7 îles** en barque. Tu fouilles leurs maisons, tu lis leurs lettres, tu résous leurs mécanismes, et tu reconstitues peu à peu ce qui s'est passé. Personne ne te dit quoi faire : c'est ta curiosité qui fait avancer l'histoire.

## 3. Les inspirations et les piliers

La référence principale est **Outer Wilds**.

1. **Le savoir est la seule vraie progression.** Le monde est ouvert, rien ne s'achète ni ne s'équipe, rien n'est donné. Un joueur qui sait peut aller presque partout très tôt, et même finir le jeu très vite.
2. **Une grande enquête.** Une question, plusieurs fils qui traversent les îles, une vérité reconstituée par morceaux, dans l'ordre que le joueur choisit.
3. **Beaucoup d'énigmes variées sur chaque île.** Jamais « une île = une mécanique ».
4. **Chill mais exigeant.** Pas de danger, pas d'ennemis, pas de combat. Des petites énigmes gratifiantes et quelques grandes vraiment difficiles.
5. **Le monde ment par omission.** Ce que le joueur croit au début est faux : les Semeurs ne sont pas partis, la brume n'est pas morte, les corps qu'il croise ne sont pas d'autres robots.
6. **Beau, calme, mélancolique**, avec une fin dont on se souvient.

---

## 4. Comment on joue

### La batterie : vivre de lumière
Le robot fonctionne à la lumière (une petite jauge sur son antenne, sans texte).
- **La brume le vide**, doucement mais sûrement.
- **La lumière le recharge** : lanternes allumées, pierres-soleil.
- **Allumer une lanterne coûte de la batterie**, mais elle éclaire le chemin et devient un point de recharge.
- On peut **reprendre la lumière** d'une lanterne : elle descend en spirale dans l'antenne, la batterie remonte, la lanterne s'éteint et sa zone se rendort.

La batterie n'est pas un type d'énigme, c'est une **contrainte partout** : jusqu'où je peux aller dans la brume ? Est-ce que j'allume ici pour pouvoir revenir ?

> 💡 Ce détail raconte déjà toute l'histoire : **les Semeurs vivaient exactement comme ça.** Le robot est fait à leur image. Le joueur vit leur mort sans le savoir.

### La boucle : mourir et revenir
- La conscience du robot vit dans le **berceau** de l'abri. Le robot n'est qu'un **corps**.
- Quand la batterie est vide, le corps s'éteint **sur place**, et la conscience se réveille dans **un corps neuf**, dans l'abri.
- Le monde se remet à zéro : lanternes, mécanismes, barque (qui revient cachée dans la crique de l'île 1).
- Ce qui reste : **ce que le joueur sait**, le **carnet**… et **les anciens corps**, là où ils sont tombés.
- Le robot ne comprend pas que ces corps éteints qu'il croise partout sont **lui-même**. Certains datent de bien avant le début de la partie : il est déjà mort des centaines de fois.

### Le mode nuit : la touche secrète `N`
- **Jamais indiquée à l'écran.** On la devine grâce à un vieux croquis dans l'atelier (un robot antenne éteinte sous la lune, avec « N » griffonné) ou à une page d'Iris écrite en peinture qui ne se lit que dans le noir.
- Le robot éteint sa propre antenne : la brume ne le vide plus, la lumière ne le recharge plus, il ne peut plus rien allumer… et **le peuple caché devient visible**.
- Il existe aussi une version accidentelle : quand la batterie est presque vide, l'antenne s'assombrit et des formes apparaissent dans la brume.
- C'est le principe du monde caché d'Outer Wilds : **rien n'est donné**. Dès l'île 1, un joueur curieux peut voir le peuple de la brume. Il ne le comprend qu'en avançant.

### Le carnet : un tableau d'enquête
Comme le journal du vaisseau d'Outer Wilds : chaque **lieu** est une fiche, des **rumeurs** relient les lieux par des flèches, des **points d'interrogation** montrent ce qui reste à trouver. Il garde aussi les cartes, les croquis, les dessins d'Aube, les lettres des Semeurs, les paroles du peuple caché.
**Il note ce qu'on a vu, jamais ce qu'il faut faire.**

### La mer et la barque
- Une seule mer, les 7 îles dedans, visibles au loin. Navigation libre, lente, avec de l'inertie.
- En mer aussi, la brume vide la batterie (légère, ou très épaisse autour de certaines îles).
- **La lanterne de la barque** protège le robot tant qu'elle brille. Elle a sa propre réserve (3 crans) qu'on remplit avec la lumière reprise d'une lanterne, au passage du faisceau du Phare, ou près d'une bouée allumée.
- **Tout l'archipel est ouvert dès qu'on a la barque.** Ce qui bloque, c'est uniquement ce qu'on ne sait pas encore.

### Les cycles du monde
Trois horloges tournent en permanence, sans jamais se remettre à zéro (même quand on meurt) :

| Cycle | Durée | Ce qu'il change |
|---|---|---|
| **La marée** | 8 min (4 basse, 4 haute) | Chaussées, gués, grottes et épaves sortent de l'eau à marée basse. |
| **Le faisceau du Phare** | 40 s par tour | La brume recule là où il passe. Orienté, il vise une île. |
| **La lune** | 24 min | À la pleine lune, la mer descend plus bas que tout, et la lentille du Phare révèle l'île cachée. |

### Les énigmes
Sur chaque île, mélangés :
- **le temps et les cycles** (passer au bon moment de la marée, de la lune…) ;
- **l'observation et les lieux cachés** (regarder au bon endroit, se mettre au bon point de vue) ;
- **les mécanismes et les codes** (miroirs, engrenages, serrures, motifs de lanternes…).

---

## 5. L'histoire : ce qui s'est vraiment passé

### Les Semeurs
Un peuple **venu de l'espace** (la Nef est leur vaisseau écrasé). Très étranges : **très grands, fins, avec de longs bras et une tête creuse en forme de cage** où brillait leur lumière. Leurs bâtiments sont à leur échelle : le petit robot s'y sent minuscule.

Ils **vivaient de lumière, comme le robot** : la brume les vidait, la lumière les rechargeait. Alors ils ont allumé, toujours plus. Des lanternes partout, une **Centrale** sous la mer pour toutes les alimenter, et de plus en plus **peur du noir** (fenêtres murées, affiches de la Commandante…).

Les six qu'on apprend à connaître :
| Nom | Rôle | Ce qu'on sait d'elle / de lui |
|---|---|---|
| **Iris** | la Gardienne | Surveillait toutes les lanternes de l'archipel depuis le Phare. Précise, fière… puis de plus en plus de doutes. |
| **Ysolde** | la Commandante | A gravé l'ordre donné au robot : « Garder la lumière jusqu'à notre retour. » |
| **Tavin** | l'Ingénieur | A construit les lanternes, la Centrale et le berceau. |
| **Saule** | la Médecin | Tenait la Quarantaine, quand les Semeurs ont commencé à « tomber malades ». |
| **Orme** | le Pilote | A lancé l'appel au secours depuis l'antenne de la Nef. |
| **Aube** | l'Enfant | Morte. Elle voyait ce que les adultes ne voyaient pas, et le racontait dans ses dessins. |

### Le peuple de la brume (les Lueurs)
- Une vie minuscule qui **ne brille que dans le noir**. Seules, des grains de poussière lumineuse ; ensemble, elles forment **des êtres**, avec des maisons, des familles, des métiers.
- Elles se nourrissent de **lumière douce** (la lune, l'eau, les champignons… les corps qui s'éteignent). Une lumière forte et fixe les **aveugle**, puis les tue.
- **Affamées par les lanternes**, elles sont devenues la « brume grise » qui vide tout ce qui brille… Semeurs compris.
- Elles parlent en **mots de lumière** qui flottent puis s'effacent comme de la buée. Plus le robot est dans le noir, mieux on les comprend : antenne allumée, rien ; batterie basse, des bribes ; antenne éteinte, des phrases complètes.
- Elles **se souviennent en gardant la lumière** : leurs souvenirs de la grande nuit sont des indices.
- **Chaque lanterne allumée est une cicatrice** : dans le noir, autour d'elle, leurs maisons sont en cendres. Reprendre sa lumière les fait se retisser.
- Elles ont **peur du robot**, dont l'antenne les brûle depuis des siècles. Et elles savent ce qu'il ignore : **il revient toujours**. Elles ont vu ses corps tomber, et s'en sont nourries.

Leurs mots à elles :
| Leur mot | Ce que c'est |
|---|---|
| le **Petit-Jour** | le robot |
| les **Soleils-Fixes** | les lanternes |
| les **Grands-Aveugles** | les Semeurs (« ils ne voyaient rien, alors ils ont tout allumé ») |
| le **Grand Jour** | l'arrivée des Semeurs, « le jour qui ne finissait pas » |
| la **Bouche** | le berceau |
| **Celle-qui-a-soufflé** | Iris |
| **rentrer** | mourir, s'éteindre |

### La grande nuit
Il y a **des siècles**, la Centrale poussait toujours plus. Iris a compris que si personne ne faisait rien, le peuple de la brume allait **mourir entièrement**.

**Elle a coupé la Centrale.** En sachant qu'elle se tuait elle-même et tuait tous les siens.

Toutes les lanternes se sont éteintes d'un coup, et la brume affamée a vidé tous les Semeurs **là où ils étaient** : à table, au lit, au travail. On retrouve leurs **squelettes**, couverts de mousse, morts en pleine vie (jamais glauques, comme les Nomai d'Outer Wilds).

Mais le peuple de la brume **a accepté Iris** : parce qu'elle les a sauvés, elle ne meurt pas. Elle devient l'une d'eux, et vit depuis dans sa maison, sur une île sans aucune lanterne, invisible.

### Le robot
- Fabriqué par les Semeurs pour **garder les lanternes** « jusqu'à notre retour ».
- Il a survécu à la grande nuit parce que le **berceau avait sa propre ligne d'énergie** (un câble qui passe par la crypte du Phare), que les Semeurs protégeaient en priorité.
- Il s'est réveillé après, seul, et a **recommencé à rallumer**. Depuis des siècles, il **continue leur erreur** sans le savoir, mourant et revenant en boucle.

### Ce que le joueur croit, et ce qui est vrai
| Au début, on croit… | En vrai… |
|---|---|
| « Ils sont partis » (valises prêtes, « jusqu'à notre retour ») | Ils sont tous morts, la même nuit. La Nef n'est jamais repartie. |
| La brume est une chose morte et hostile | C'est un peuple vivant, affamé par la lumière. |
| Les corps éteints sont d'autres robots | Ce sont tous les anciens corps du joueur. |
| Rallumer les lanternes, c'est réparer le monde | C'est exactement ce qui a tué les Semeurs. |

**La fausse piste est construite exprès** : les premières îles (l'atelier du robot, le poste d'Iris qui a survécu) sont vides et rangées. **Les squelettes n'apparaissent qu'au milieu du jeu** (la Nef, la Quarantaine, la ville engloutie). C'est là que vient le choc.

### Les 4 fils de l'enquête
Chacun traverse plusieurs îles, et chaque île contient des morceaux de plusieurs fils :
1. **La maladie et les lanternes** — on comprend qu'ils se sont tués eux-mêmes.
2. **La Nef et l'appel au secours** — ils ont essayé de partir, ou de se faire sauver.
3. **Le berceau et les corps** — qui suis-je ? combien de fois suis-je mort ?
4. **La Gardienne** — la vie d'Iris, ses doutes, son geste ; on la retrouve à la fin.

---

## 6. L'archipel, île par île

| # | Île | Ce qu'il faut savoir pour y entrer |
|---|---|---|
| 1 | **Le Réveil** | rien, on y commence |
| 2 | **Le Phare** | la marée (la chaussée n'est praticable qu'à marée basse) |
| 3 | **La Colonie** | rien, c'est l'île de départ naturelle |
| 4 | **La Quarantaine** | traverser la brume très épaisse (bien préparer la lanterne de la barque, ou viser l'île avec le faisceau du Phare pour ouvrir un couloir) |
| 5 | **La Nef** | l'intérieur est fermé par des codes trouvés ailleurs |
| 6 | **La Centrale** | l'entrée est dans la ville engloutie, qui ne sort de l'eau qu'à la pleine lune |
| 7 | **L'île cachée** | la lentille du Phare la révèle, une nuit de pleine lune |

### 1. Le Réveil — l'île du robot
Le prologue, 30 à 45 min la première fois (5 min pour qui sait). On se réveille, une luciole guide, on apprend sans un mot : la batterie, allumer, reprendre la lumière, mourir et revenir, le carnet.
- L'**abri** et le berceau, l'**atelier des robots** caché derrière une cascade (le moule gravé de l'ordre d'Ysolde), la **barque** cachée sous les racines de la crique.
- Pas de squelettes : rien ne contredit « ils sont partis ».
- **Le secret** : la page 7 d'Iris (« J'écris ici à la peinture qui brille. Seuls ceux qui éteignent pourront me lire. Elles ne sont pas la brume. Elles sont dans la brume… »). Et quand on éteint, **une ville entière** pousse du sol : la ville des Pins, avec ses quartiers, ses habitants, et des chemins qui n'existent que dans le noir (l'escalier des géants, le pont des pêcheurs).

### 2. Le Phare — le poste d'Iris
Un phare sur un rocher coupé du monde par la marée, qui ne fabrique pas sa lumière mais **la rassemble** grâce à des miroirs sur trois caps. On y découvre Iris : méticuleuse, fière… puis qui cesse d'y croire.
Les grandes énigmes :
- **Atteindre le Phare** (marée) : la chaussée est noyée à marée haute et couverte de brume épaisse à marée basse. Un ancien corps à mi-chemin montre ce qui arrive quand on part trop tard.
- **Rallumer le Grand Phare** (miroirs) : orienter les miroirs des trois caps pour renvoyer la lumière à la lentille.
- **La clé de la salle des cartes** : elle est restée dans l'épave d'un ravitailleur, qu'on voit depuis la galerie.
- **La salle des machines** (mécanisme) : remonter les engrenages d'après un schéma à moitié couvert de suie, pour pouvoir viser avec la lentille.
- **La chambre d'Iris** (lieu caché) : une lanterne éteinte et débranchée, une seule tasse, et un dessin d'Aube : des silhouettes de brume qui dansent autour d'Iris et d'elle.
- **La lunette d'Iris** (observation) : chaque cran gravé cadre un lieu lointain de l'archipel.
- Ce qu'on y gagne : la **carte de l'archipel**, la **table des marées**, le **registre des lanternes** (une page par île, année après année), et la phrase-clé : « Les nuits de pleine lune, le Phare chante, et je vois ma maison. »

### 3. La Colonie — la ville des Semeurs
Une ville vide, haute, trop grande pour le robot : des valises prêtes, des lanternes partout, des fenêtres murées… et les dessins d'**Aube**, qui voyait ce que les adultes ne voyaient pas.
- **La maison d'Aube** (lieu caché + observation) : fermée de l'intérieur, tout est trop haut.
- **La rue des Trois-Soleils** (mécanisme) : reconstituer le motif de lanternes à partir d'affiches déchirées de la Commandante pour ouvrir la maison commune.
- **Le jardin du haut** (temps) : les serres aux **arbres roses**, une espèce importée qui exige une lumière constante ; on y accède par un carillon et une écluse.
- **Le vieux port** (temps, le plus difficile) : des toits et des rues sous l'eau, qui ne sortent qu'à la pleine lune. C'est la **ville engloutie**, et l'entrée de la Centrale.
- Les petites : se placer au point de vue d'un dessin d'Aube révèle une cachette ; la comptine de l'école donne l'ordre des couleurs d'une porte de la Nef.

### 4. La Quarantaine — l'île blanche *(à concevoir)*
Entourée de brume très épaisse. L'hôpital de Saule, les tombes. C'est là que les Semeurs ont commencé à « tomber malades », sans comprendre que c'était la brume affamée.

### 5. La Nef — le vaisseau *(à concevoir)*
Le crash, l'antenne d'appel au secours d'Orme. La Nef n'est **jamais repartie** : c'est ici qu'on tombe sur les premiers squelettes, et que la fausse piste s'effondre.

### 6. La Centrale — la fin *(à concevoir)*
Sous la mer et sous terre, accessible par la ville engloutie à la pleine lune. La source de toutes les lanternes et du berceau. L'endroit où Iris a fait son geste.

### 7. L'île cachée — la maison d'Iris *(à concevoir)*
Sans aucune lanterne, invisible. On ne la voit qu'en pointant la lentille du Phare sur le cran sans nom, une nuit de pleine lune. On y retrouve Iris, devenue une habitante de la brume. Elle ne débloque rien : **elle confirme ce qu'on a compris.**

---

## 7. La fin

- **Il n'y a qu'une seule enquête**, libre du début à la fin, sans « deuxième moitié » ni bascule. La vérité arrive par morceaux, dans l'ordre que le joueur choisit.
- Aider le peuple de la brume n'est jamais obligatoire : c'est un secret possible, qui ne change pas la fin.
- **Quand le joueur a compris, rien ne lui dit quoi faire.** Mais il peut faire une dernière boucle.
- **Le dernier geste** : descendre au fond de la Centrale et **couper la ligne du berceau**, la dernière lumière des Semeurs, **là où Iris a coupé les autres**. Le robot refait son geste et termine ce qu'elle a commencé. Le trajet jusque-là est l'épreuve finale.
- Ensuite : toutes les lanternes s'éteignent, le berceau aussi. Le monde caché s'illumine. Le robot ne reviendra plus : il devient **un nid de lumière** pour le peuple de la brume… et **Iris vient s'asseoir à côté de lui**.
- La fin est **la même pour tout le monde**. Un joueur qui sait tout peut la faire très tôt.

---

## 8. L'ambiance

- **Visuel** : en 3D, doux, pastel, « un peu à la Outer Wilds » (le style exact est en cours de recherche). Deux mondes : celui des Semeurs, **chaud, doré et vide** ; celui du peuple caché, **nocturne, bleu-vert phosphorescent et vivant**.
- **Son** : piano doux et nature, en couches qui s'ajoutent quand on rallume. Une **seconde musique**, celle du peuple caché (cristalline, aquatique), qui apparaît quand on éteint.
- **Durée visée** : 8 à 12 heures (1 h 30 à 2 h par grande île).
- **Plateforme** : PC, clavier, fait avec Godot 4.

## 9. Où en est le projet

- ✅ Toute l'histoire, les règles et la fin sont décidées.
- ✅ Les îles 1, 2 et 3 sont conçues en détail.
- ⏳ Les îles 4 à 7 restent à concevoir.
- ⏳ Le style visuel est en cours de recherche (nouveau départ en v5, l'ancien style a été abandonné).
- ⏳ Le développement repart de zéro.

## 10. Des questions pour en discuter

- Le moment où on comprend que les corps sont les siens : quand doit-il arriver ?
- Est-ce que la touche `N` cachée est trop secrète, ou pas assez ?
- La fin (couper la dernière lumière et ne plus revenir) : triste, belle, les deux ?
- Est-ce que l'idée « rallumer, c'est l'erreur » se sent assez tôt, sans être donnée ?
- Qu'est-ce qu'on aimerait trouver sur la Quarantaine, la Nef, la Centrale et l'île d'Iris ?
