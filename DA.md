# Direction artistique — Petite Planète (v5)

> Décidée le 2026-11-16, après le rejet de la DA v4 (diorama iso en blocs, couleurs ternes, « ne raconte rien »).
> Scène de référence jouable dans l'éditeur : `scenes/test_da.tscn` (captures dans `captures/`).

## En une phrase
**Un monde 3D chill et doux, aux pastels lumineux, « à la Outer Wilds »** : formes rondes et simples, matière partout, lumière dorée des Semeurs le jour, monde caché bleu et turquoise la nuit.

## Principes
1. **Pastel lumineux, jamais gris.** Ciel pêche, rose et lavande, mer turquoise, herbe vert tendre. Toujours **un accent chaud** (l'or des Semeurs) et des **nuits profondes** qui font briller les lumières.
2. **Rien n'est uni.** Chaque surface a des taches de couleur, des strates et de la mousse (shaders « couleurs + bruit doux », sans textures peintes). Herbe en brins, fleurs, petits détails au premier plan.
3. **Formes rondes et simples, pas de blocs.** Peu de détails géométriques ; la beauté vient de la lumière, de la couleur et des silhouettes.
4. **Pas de contours.** Les formes se lisent par la lumière.
5. **Ça raconte.** Chaud et doré = les Semeurs (passé, vide). Froid et turquoise = le peuple de la brume (vivant, caché). Les lieux, les plantes et l'architecture sont des indices d'enquête.

## Caméra — validée : 1re personne
- **Exploration en 1re personne** (validé le 2026-11-16 après le test jouable `scenes/test_camera.tscn`).
- **L'antenne pend devant les yeux, comme la lumière d'un poisson-lanterne** : l'ampoule flotte en haut de l'écran, ballotte à chaque pas, traîne quand on tourne la tête. C'est la jauge de batterie (zéro HUD) **et** une vraie lumière qui éclaire autour du robot.
- **La vision du robot réagit** : batterie basse = image trouble, ternie, grésillante (et des formes apparaissent dans la brume par accident). Mode N = paupière qui se ferme, noir, puis les yeux se rouvrent sur la nuit.
- **Bras entiers dans le champ** (épaules, coudes, mains), jamais de mains volantes.
- **Allumer = brancher un câble** (validé le 2026-11-16) : le robot s'approche, s'accroupit, sort une fiche reliée à un **câble qui sort de son poignet**, la branche dans la **prise** de la lanterne (clic), des **pulsations dorées** passent du robot à la lanterne (son antenne faiblit), la lanterne se charge puis **s'ouvre en crans mécaniques**, la zone se réveille, il débranche et le câble s'enroule. **Reprendre la lumière** = même geste, flux dans l'autre sens. Le câble annonce la fin (couper la ligne du berceau).
- **3e personne seulement pour les grands moments** (réveil, première lanterne, fin), filmés comme des cinématiques.

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
- **Base du test, à affiner** : rond, crème, deux yeux lumineux, **antenne à ampoule = batterie** (élément clé, zéro HUD), **écharpe** (tissée par les Semeurs).
- Ajouter de l'**usure** : rayures, mousse, rouille légère (il a dormi longtemps).
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
- **Mode N** : bascule douce (quelques secondes) vers la **nuit bleue**. Les couleurs chaudes s'éteignent, tout devient bleu profond et violet, et la brume, les plantes et le peuple **s'allument en turquoise**. Même lieu, autre monde.
- **La brume, de jour** : basse et nacrée, des bancs blanc-rosé qui rampent sur la mer et dans les creux et bougent lentement. Belle de loin, inquiétante de près (elle vide la batterie).

## Nature
- **Familière mais un peu étrange** : herbe, fleurs et buissons qu'on reconnaît, avec des détails bizarres (fleurs qui suivent la lumière, troncs en spirale, plantes qui s'allument la nuit).
- Rochers roses en strates (rose, ocre, crème) avec mousse, mer turquoise avec écume autour des îlots.

## Interface et effets
- **Zéro HUD.** La batterie se lit sur l'antenne (lumière, grésillement) et les actions possibles sur les objets (légère lueur).
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

## Prochains tests
1. ~~**Caméra**~~ : fait, 1re personne validée.
2. **Nuit / mode N** : reporté bien plus tard (décision du 2026-11-16 : on fait d'abord tout le jour). À refaire plus sombre, plus douce, pastel.
2b. ~~**Première lumière**~~ : câble + prise (test dans `scenes/ile_test.tscn`).
3. **Peaufiner le jour** : robot usé, vraie ruine organique des Semeurs (avec un squelette pris dans la mousse), fleurs moins plates, bancs de brume.
