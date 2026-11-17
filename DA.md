# Direction artistique — Petite Planète (v6)

> **v6 décidée le 2026-11-16** : vue de dessus et low-poly à facettes, après le test 1re personne/formes rondes (« quelque chose d'arrondi pour un jeu géométrique », ça ne collait pas).
> La v5 avait rejeté la v4 (diorama iso en blocs) pour ses **couleurs ternes** et parce qu'elle « ne raconte rien ». La v6 reprend la vue de dessus et les blocs, mais **garde les pastels lumineux et la narration de la v5**.
> Scène de test du terrain en terrasses : `scenes/archive/ile_terrasses.tscn` (+ `scripts/terrasses.gd`). L'ancienne référence v5 reste `scenes/archive/test_da.tscn`.

## En une phrase
**Un monde 3D en maquette, low-poly à facettes, aux pastels lumineux** : plateaux carrés, angles nets, aplats de couleur, lumière dorée des Semeurs le jour, monde caché bleu et turquoise la nuit. Inspiration de forme : les jeux d'aventure isométriques en diorama (sans copier aucun jeu existant).

## Principes
1. **Pastel lumineux, jamais gris.** Ciel pêche, rose et lavande, mer turquoise, herbe vert tendre. Toujours **un accent chaud** (l'or des Semeurs) et des **nuits profondes** qui font briller les lumières.
2. **Aplats à facettes** (v6). Chaque face a une couleur unie ; la variété vient de l'éclairage par face, de la palette et des strates nettes sur les falaises, pas du bruit ni des textures. *(Remplace « rien n'est uni » et le relief de pierre scanné de la v5 : à simplifier dans les shaders.)*
3. **Formes géométriques, angles nets** (v6). Terrain en plateaux carrés sur une grille, falaises droites, marches nettes, blocs cubiques, arbres en cônes. Quelques éléments ronds (lanternes, ampoule, Semeurs) ressortent justement parce que tout le reste est anguleux. *(Remplace « formes rondes, pas de blocs ».)*
4. **Pas de contours.** Les formes se lisent par la lumière.
5. **Ça raconte.** Chaud et doré = les Semeurs (passé, vide). Froid et turquoise = le peuple de la brume (vivant, caché). Les lieux, les plantes et l'architecture sont des indices d'enquête.

## Caméra — v6 : vue de dessus
- **Exploration en vue de dessus**, caméra haute et inclinée, robot vu en entier, effet maquette (décidé le 2026-11-16, remplace la 1re personne validée plus tôt le même jour).
- **À décider** : angle et focale exacts, caméra fixe ou orientable, flou de maquette (tilt-shift) ou non.
- **L'ampoule de l'antenne reste la jauge de batterie (zéro HUD)**, lue directement sur le robot : elle brille plus ou moins, grésille quand elle faiblit et éclaire le sol autour de lui. Elle doit être assez grosse et lumineuse pour se lire de haut.
- ~~Bras dans le champ~~, ~~ampoule en haut de l'écran~~ : abandonnés avec la 1re personne.
- **Vision trouble à batterie basse** : à repenser pour la vue de dessus (effet d'écran ou seulement l'ampoule ?). *(Le mode N est retiré le 2026-11-16 : le monde de la brume ne se voit qu'à la fin.)*
- **Allumer = brancher un câble** (validé le 2026-11-16) : le robot s'approche, s'accroupit, sort une fiche reliée à un **câble qui sort de son poignet**, la branche dans la **prise** de la lanterne (clic), des **pulsations dorées** passent du robot à la lanterne (son antenne faiblit), la lanterne se charge puis **s'ouvre en crans mécaniques**, la zone se réveille, il débranche et le câble s'enroule. **Reprendre la lumière** = même geste, flux dans l'autre sens. Le câble annonce la fin (couper la ligne du berceau).
- **Grands moments** (réveil, première lanterne, fin) : la caméra descend plus près du robot, filmés comme des cinématiques.

## Lumière et temps
- **Cycle jour/nuit lent, toujours beau** (lié au cycle de lune de 24 min et à la marée) : aube rose, journée lumineuse, crépuscule doré, nuit bleue. Chaque heure a sa palette.
- **Pas de météo.** Seuls l'heure et la brume changent.
- **Ciel** : dégradé pastel, nuages en couches éclairés par le soleil, et **la grosse planète, monde d'origine des Semeurs**, toujours visible (indice possible : ce qu'ils ont fui, pourquoi ils ne sont jamais rentrés).
- Post-effets : **halo doux sur les lumières** (glow). Le reste (flou de profondeur, grain, vignette) est à décider.

## Palettes des îles
| Île | Teinte | Ambiance |
|---|---|---|
| 1 Réveil | vert tendre + rose | prairie, falaises roses, berceau doré |
| 2 Phare | or + bleu ciel | rochers clairs, mer turquoise, lumière tournante |
| 3 Colonie | ocre + pêche | ville poussée, serres de verre, vieux port englouti |
| 4 Quarantaine | blanc + lavande | île blanche, silence, brume dense, tissus |
| 5 Nef | rouille + corail | carcasse du vaisseau, métal patiné, antenne |
| 6 Centrale | turquoise + nacre | sous l'eau, bulles, lumière filtrée |
| 7 Île cachée | bleu nuit + or pâle | maison d'Iris, visible surtout la nuit |

Même style partout ; on reconnaît chaque île d'un coup d'œil, même de loin.

## Le robot
- **Taille : ~1,90 m** (yeux à ~1,65 m), un peu plus petit que les Semeurs.
- **Design v6 (concept Meshy du 2026-11-16)** : low-poly à facettes, crème, corps en œuf, grosse tête, deux yeux ronds lumineux avec **paupières** (sourcils expressifs), jambes courtes et **gros pieds**, **écharpe** verte à spirales dorées (tissée par les Semeurs, indice), **sacoche à graines** en bandoulière (jardinier), **enrouleur de câble avec fiche sur l'avant-bras droit** (pour brancher les lanternes).
- **Antenne à ampoule = batterie** (élément clé, zéro HUD) : longue, en segments souples, qui part vers l'avant ; ampoule en cristal doré à facettes.
- **Usure** : mousse **en plaques vertes à facettes** sur le dessus (crâne, épaules, pieds), rouille orangée aux articulations. Pas de taches de camouflage, pas de mousse « réaliste ».
- **Mains** : 3 gros doigts crème, lisibles (elles branchent le câble), pas de petites pinces.
- **Fabrication** : Meshy génère le robot **avec son squelette (rig), sans antenne** ; on fait nos propres animations. L'antenne + l'ampoule sont un objet à part, accroché à l'os de la tête ; l'écharpe reçoit 2-3 os ajoutés pour ballotter.
- **Animation : mignon et un peu maladroit.** Petits pas rebondis, il se rattrape quand il trébuche, l'antenne et l'écharpe ballottent, il **tourne la tête vers ce qui est intéressant** (indice sans texte).

## Les Semeurs
- **Un peu plus grands que le robot : 2,50 à 3 m** (le robot fait ~1,90 m — décidé le 2026-11-16, l'écart 1 m / 4 m était trop grand). Fins, longs bras, **tête creuse en cage** où brillait leur lumière.
- **Corps organique et végétal** : bois clair, nacre, fibres, comme une branche ou un coquillage.
- **Squelettes pris dans la nature** : couverts de mousse et de fleurs, dans des poses de vie (assis, au travail). Au début, on peut les prendre pour des statues ou des racines ; on comprend plus tard. Jamais glauques.
- **Architecture organique, poussée plutôt que construite** : arches en côtes, coques, racines, tout à leur échelle (portes d'environ 3 m, tables à hauteur de poitrine du robot, marches un peu hautes). Ils « sèment » leurs maisons.
- **Leur lumière : or chaud**, boules douces dans des cages (lanternes, pierres-soleil, sommets des tours).
- **Leurs plantes** : dorées, en rangs, qui poussent sur leurs structures. On lit dans le paysage où ils ont vécu.
- **Écriture : courbes végétales** (spirales, vrilles, points comme des pousses), gravée ou peinte sur leurs objets — pas de glyphes magiques.

## Le monde caché
> ⚠️ **La version nuit du test n'est pas encore ça** (avis du 2026-11-16) : beaucoup trop éclairée, couleurs trop vives, pas assez pastel. À retravailler dans un 2e temps — la nuit doit rester douce et pastel.

- **Le peuple de la brume : des créatures marines du ciel**, translucides et phosphorescentes (méduses, raies, poissons-lanternes) qui flottent dans la brume. Douces et curieuses, jamais effrayantes.
- **À la fin** (plus de mode N depuis le 2026-11-16 : le robot voit la brume une fois accepté, en coupant son câble) : bascule douce (quelques secondes) vers la **nuit bleue**. Les couleurs chaudes s'éteignent, tout devient bleu profond et violet, et la brume, les plantes et le peuple **s'allument en turquoise**. Même lieu, autre monde.
- **La brume, de jour** : basse et nacrée, des bancs blanc-rosé qui rampent sur la mer et dans les creux et bougent lentement. Belle de loin, inquiétante de près (elle vide la batterie).

## Nature
- **Familière mais un peu étrange** : herbe, fleurs et buissons qu'on reconnaît, avec des détails bizarres (fleurs qui suivent la lumière, troncs en spirale, plantes qui s'allument la nuit).
- Rochers roses en strates (rose, ocre, crème) avec mousse, mer turquoise avec écume autour des îlots.
- **v6** : arbres en cônes et prismes à facettes, rochers et blocs cubiques, buissons en polyèdres. Le côté « un peu étrange » reste (troncs en spirale à facettes, fleurs qui suivent la lumière).

## Interface et effets
- **Zéro HUD.** La batterie se lit sur l'ampoule du robot, vue de dessus (lumière, grésillement, cercle éclairé au sol), et les actions possibles sur les objets (légère lueur).
- **Le guidage** (décidé le 2026-11-17 : au réveil, on se sentait posé là sans repère) : tout ce qu'on peut utiliser scintille en doré (grains de lumière qui montent, halo doux), plus fort à portée de `E` ; une petite **touche E dorée** flotte au-dessus, jusqu'à ce que le geste soit appris (`scripts/guidage.gd`). Et, sur le tapis de l'abri, le **mode d'emploi du petit jardinier** signé Tavin, l'Ingénieur : une affiche illustrée, ce qu'il faut faire sur l'île 1 en 7 vignettes. *(Les « pensées du robot », essayées le même jour, ont été retirées.)*
- **Les documents laissés par les gens sont de vrais documents dessinés** (décidé le 2026-11-17), jamais du texte brut : chacun a son style (affiche de l'atelier à cadre doré et vignettes ; ordre officiel plié en trois, scellé à la cire ; page de journal arrachée, lignée, écrite vite). Sources HTML/SVG dans `tools/affiches/` (papier vieilli, encre au trait tremblé, aquarelle), rendues en PNG transparents par `python tools/affiches/rendre.py` dans `assets/affiches/`. En jeu, E montre le document en grand ; la feuille posée dans le décor le porte en miniature, et le carnet en garde le dessin.
- **Carnet papier dessiné** : papier crème, encre brune, aquarelle légère. Les croquis se dessinent trait par trait à la découverte, et les liens entre indices sont des fils ou des flèches à la main.
- **Pas de magie** (décidé le 2026-11-16) : pas de glyphes tracés dans l'air ni de sorts. Le robot est une machine : la lumière passe par des **câbles, des prises, des mécanismes**. Effets = pulsations dorées dans les câbles, cœurs qui se chargent, pétales qui s'ouvrent en crans, un peu de pollen doré.
- **Zones endormies** : autour d'une lanterne éteinte, le monde est gris et terne ; quand elle s'allume, une **vague de couleur** à front doré réveille la zone.

## Technique (base posée dans le test)
- Godot 4.7, tout réglable dans l'inspecteur.
- `shaders/ciel_pastel.gdshader` : dégradé, nuages, soleil, planète.
- `shaders/roche_herbe.gdshader` : herbe en taches sur les faces plates, roche en strates sur les pentes, mousse entre les deux.
- `shaders/vegetation.gdshader` + `scripts/semis_vegetation.gd` : brins d'herbe et fleurs semés sur un mesh (outil visible dans l'éditeur).
- `shaders/mer.gdshader` : turquoise, eau claire et écume près des rochers.
- Modèles faits dans Blender (MCP), exportés en `.glb` dans `assets/models/`.
- **v6 — qui fabrique quoi** : formes simples **par script** (terrain en terrasses via `scripts/terrasses.gd`, blocs, rochers cubiques, arbres en cônes, marches) ; **Meshy** pour les objets complexes (robot, lanternes, bâtiments des Semeurs, squelettes, créatures, objets d'enquête). Liste complète des assets et règles d'export : à faire avant l'abonnement Meshy.
- **v6 — à adapter** : `roche_herbe.gdshader` (bruit et relief scanné → aplats et strates nettes), `vegetation.gdshader` (brins d'herbe → touffes low-poly ?), `joueur.gd` (caméra 1re personne → vue de dessus).

## Prochains tests
1. ~~**Caméra**~~ : 1re personne validée, puis **remplacée par la vue de dessus** (v6, 2026-11-16). Prochain test : caméra de dessus + aplats low-poly sur `scenes/archive/ile_terrasses.tscn`.
2. **Nuit / monde de la brume (fin)** : reporté bien plus tard (décision du 2026-11-16 : on fait d'abord tout le jour). À refaire plus sombre, plus douce, pastel.
2b. ~~**Première lumière**~~ : câble + prise (test dans `scenes/archive/ile_test.tscn`).
3. **Peaufiner le jour** : robot usé, vraie ruine organique des Semeurs (avec un squelette pris dans la mousse), fleurs moins plates, bancs de brume.
