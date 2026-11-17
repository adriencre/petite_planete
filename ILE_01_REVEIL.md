# Île 1 — L'Île du Réveil

> Document complet de l'île. À lire avec **`ENQUETE.md`** (l'histoire v4 : les Semeurs, la grande nuit, Iris, les 7 îles).
> **L'île est déjà construite** (`scenes/islands/island_01.tscn`). Ce document décrit ce qui existe, ce qui change avec la v4, et ce qu'il faut retirer ou adapter (§13).
> Mis à jour le 2026-11-15 pour la v4. Les points marqués **[à valider]** sont des propositions.

---

## 1. En une phrase
Le prologue : on se réveille dans un corps neuf, sur une île grise et noyée de brume. On apprend à vivre avec une batterie, à rallumer, à reprendre la lumière… et, pour les curieux, que la nuit cache une ville entière.

## 2. Sa place dans le jeu
- **La maison.** C'est ici qu'on se réveille à chaque boucle, dans le berceau de l'abri.
- **Dans l'histoire (v4)** : c'est l'**île du robot**. Les Semeurs y avaient installé le **berceau** et l'**atelier des robots**, mais personne n'y vivait : **pas de squelettes ici**, et rien qui contredise la fausse piste « ils sont partis ».
- **Ce qu'elle apprend** (sans un mot) : la batterie, la brume, allumer, reprendre la lumière, mourir et revenir, le carnet.
- **Ce qu'elle cache** : la page 7 d'Iris, l'atelier. (La ville des Pins n'apparaît qu'à la fin.)
- **Ce qu'elle ouvre** : la barque, donc tout l'archipel. On voit le Phare au loin.
- **Les fils de l'enquête présents ici** :
  - **le berceau et les corps** (le berceau, l'atelier, le premier ancien corps) ;
  - **Iris** (la page 7, pour qui la trouve).
- **Durée** : 30 à 45 min la première fois. Un joueur qui sait peut en partir en 5 minutes (pierre-soleil cachée → barque).

---

## 3. Le lieu

```
                    ▲ sommet (6 m) : GRANDE LANTERNE, vue sur le Phare
                    │
        plateau (3 m) ── cascade ─┐ rebord caché → grotte → ATELIER DES ROBOTS
              ▲                   │
   escalier                       │
              │                   │
   lanternes 1, 2, 3 (racines vers le sommet) ── ABRI (berceau) ── pierre-soleil
              │
   crique ouest (brume épaisse) : ancien corps, BARQUE cachée sous les racines,
                                  pierre-soleil cachée
```
*(Les détails exacts sont dans la scène ; la carte du carnet est dessinée depuis le GridMap.)*

### Forme v6 (décidée le 2026-11-16) : **gradins**
L'île monte en **3 marches** de la plage au sommet : plage (abri, pierre-soleil) → niveau 1 (lanternes 2 et 3) → niveau 2 (escalier, cascade, atelier) → niveau 3 (sommet, grande lanterne). On voit le but dès le réveil. La crique ouest est une entaille dans la brume, au niveau de la mer. Environ 12 × 10 cases de 4 m.
Schéma : `concept/ile_01_formes.png` (variante A), dessiné par `tools/carte_iso.py`.

### Détails v6 (décidés question par question)
- **L'abri** (2026-11-16) : sur un **petit promontoire à l'est**, un peu à l'écart, porte tournée vers l'ouest. En sortant, **toute l'île se dévoile en panorama** (lanternes éteintes, gradins, sommet) ; le Phare est dans le dos. La pierre-soleil est juste devant la porte. Schéma : `concept/ile_01_abri.png` (variante C).
- **Les lanternes 1-2-3** (2026-11-16) : réparties autour du centre de l'île. **Décidé le 2026-11-17 : une seule grande lanterne, au sommet** (l'ancienne lanterne du sommet est retirée). Lanterne 1 près de l'abri (est, sur la plage), lanterne 2 à l'ouest **au bord de la brume** (apprend que la brume vide la batterie), lanterne 3 à l'est du niveau 1. Les **racines lumineuses** de la grande descendent du sommet vers les trois, en grimpant les falaises : on comprend sans texte qu'il faut les trois, dans l'ordre qu'on veut, et la lumière monte vers le but. Schéma : `concept/ile_01_lanternes.png` (variante B).
- **La cascade et l'atelier** (2026-11-16) : **à l'est**. Une rivière descend du sommet en marches jusqu'à la mer ; on la voit dès l'abri, dans le panorama. Le **rebord caché** est derrière la chute, au niveau 2 ; la **grotte et l'atelier** sont creusés sous le sommet. L'**escalier** est à l'ouest du niveau 1, de l'autre côté : l'ouest (escalier, brume, crique) et l'est (cascade, atelier) s'équilibrent. Schéma : `concept/ile_01_cascade.png` (variante A).
- **La crique ouest** (2026-11-16) : **encaissée**, une poche fermée par de hautes falaises où la brume stagne comme dans un bol, avec **une seule entrée** par la plage, au sud. La **barque** est au pied de la falaise, sous les racines ; l'**ancien corps** et la **pierre-soleil cachée** sont dans la poche. Schéma : `concept/ile_01_crique.png` (variante B).
- **Le plateau et le sommet** (2026-11-16) : le **sommet est au centre**, petit pic au niveau 3, visible de partout (y compris du panorama de l'abri). Sur le plateau (niveau 2), en arrivant par l'escalier : la charrette, le banc, le jardin mort, puis la montée vers le sommet. La rivière de la cascade prend sa source juste à l'est du sommet. Schéma : `concept/ile_01_sommet.png` (variante A).
- **Plan complet** : `concept/ile_01_plan.png` (`tools/carte_iso.py ile_01_plan`). La grille de ce plan sert de base à la maquette jouable.

### Les lieux
| Lieu | Ce qu'on y trouve |
|---|---|
| **L'abri** | Le berceau (lumière qui s'allume à chaque réveil), **un papier posé à côté du berceau : l'ordre d'Ysolde** (§7), **sur le tapis, le mode d'emploi du petit jardinier, signé Tavin** (ce qu'il faut faire sur l'île, décidé le 2026-11-17), l'horloge arrêtée, le carnet, un coin sombre où quelque chose scintille, la veilleuse au-dessus de la porte. L'abri est **à la taille du robot**. |
| **La pierre-soleil** | Juste à la sortie de l'abri : l'antenne vide s'y recharge. Premier geste du jeu. |
| **Les lanternes 1, 2, 3** | Le chemin vers le centre de l'île. Chacune réveille sa zone. |
| **La grande lanterne** | Au sommet, visible de partout. Elle ne s'allume qu'une fois les trois petites allumées (racines lumineuses qui montent jusqu'à elle). L'allumer, c'est la fin de l'île. |
| **L'escalier** | Un simple escalier de pierre monte au plateau, ouvert dès le début. Rien à planter ni à faire pousser (décidé le 2026-11-17). |
| **Le plateau et le sommet** | Le jardin mort, la charrette, le banc. Au sommet, la **grande lanterne** : l'île entière s'éveille. |
| **La cascade** | Derrière l'eau, un rebord caché → une grotte → **l'atelier des robots**. |
| **L'atelier des robots** | Le moule, les pièces détachées, l'établi, la lanterne de l'atelier, la **page 7**. **Un peu trop grand pour le robot** (Semeurs de 2,50 à 3 m) : établi à hauteur de poitrine, portes d'environ 3 m, marches un peu hautes. |
| **La crique ouest** | Noyée de **brume épaisse**. Le **premier ancien corps**, couvert de mousse. La **barque**, cachée sous les racines. La **pierre-soleil cachée**. |
| **Au loin** | La silhouette sombre du Phare, et la petite lueur de la bouée de son port. |

---

## 4. Les cycles sur l'île
- **Pas de marée sur l'île 1** (décidé le 2026-11-16) : la marée est propre à certaines îles (le Phare d'abord).
- Une fois le Phare rallumé (dans la même boucle), on voit son **faisceau** balayer la mer depuis le sommet.

---

## 5. Côté lumière

### Le déroulé (première boucle)
1. **Le réveil** (~23 s, sans contrôle) : noir → le robot couché sur le flanc → un œil vacille, puis l'autre → il se redresse, regarde ses mains, se lève en titubant, regarde autour de lui. On prend la main.
2. **La sortie** : la caméra recule lentement sur l'île grise (sans contrôle). Une **luciole** apparaît et guide.
3. **L'antenne est vide** : on la recharge à la **pierre-soleil**.
4. **La première lumière** (longue cinématique) : le robot s'accroupit, branche le câble de son poignet dans la prise de la lanterne → pulsations dorées → la lanterne se charge et s'ouvre en crans → la zone se réveille en vague de couleur → il débranche. Les suivantes sont plus courtes. *(2026-11-16 : remplace le glyphe tracé dans l'air — pas de magie, voir DA.md.)*
5. Lanternes 1, 2, 3 → **racines lumineuses** qui montent vers le sommet.
6. **Le plateau** : on monte par l'escalier ; la charrette, le banc, le jardin mort.
7. **La grande lanterne, au sommet** : toutes les lanternes s'allument en cascade, la caméra s'élève sur l'île illuminée, passe par la barque, puis montre le Phare éteint et la lueur de sa bouée au coucher du soleil.
8. **La barque** : on la trouve dans la crique, et on part librement (plus de fondu).

### Les énigmes
L'île 1 est un tutoriel : ses énigmes sont petites.

| Énigme | Ce qu'il faut comprendre |
|---|---|
| **L'antenne vide** | La pierre-soleil recharge. |
| **La batterie** | La brume vide, la lumière recharge, allumer coûte. On avance de lumière en lumière. |
| **La grande lanterne** | Elle a besoin des trois petites (les racines lumineuses le montrent). |
| **La crique** | La brume épaisse vide trop vite : il faut y arriver avec assez de batterie, ou avec la pierre-soleil cachée. |

### Le premier « échec »
- Tôt ou tard, la batterie se vide : le robot s'éteint **sur place** et se réveille dans l'abri, **dans un corps neuf**. Son ancien corps reste là-bas.
- Les lanternes allumées avec cette batterie **s'éteignent** : l'île se rendort.
- Le joueur ne comprend pas encore que ces corps sont lui.

### Reprendre la lumière
- `E` sur une lanterne allumée : la lumière descend en spirale dans l'antenne, la batterie remonte, la lanterne s'éteint, **sa zone se rendort**. La première fois est un vrai moment.

### Les secrets
| Secret | Ce qu'il donne |
|---|---|
| **La pierre-soleil cachée** | Le raccourci vers la barque dès le début. |
| **L'atelier des robots** (derrière la cascade) | Le moule, les pièces : on fabrique des robots ici. |
| **La page 7 d'Iris** (sur l'établi) | **Lisible normalement** (décidé le 2026-11-16 : plus de peinture qui brille). |
| **La graine cachée** (coin de l'abri) | À batterie presque vide, une traînée floue en part et file sous le berceau. |
| **Le premier ancien corps** (crique) | Couvert de mousse ; dans le noir, des Lueurs brillent dessus. Il porte **exactement la même écharpe que le robot, avec le même nœud** (décidé le 2026-11-16) : le premier détail du fil « les corps, c'est moi », à remarquer sans comprendre. |

---

## 6. Le monde de la brume (plus de touche `N`, décidé le 2026-11-16)
- **Plus de mode nuit ni de touche `N`.** Le robot ne voit le peuple de la brume qu'une fois accepté par eux, en coupant la ligne de son berceau (la fin, voir `DESIGN.md`).
- Avant, seulement **des bribes à batterie presque vide** : des formes floues, quelques mots (« …il… revient… »).
- **À retirer du jeu** : le croquis de la touche `N` dans l'atelier, le mode nuit.

---

## 7. Le récit (ce que le joueur comprend sur l'île 1)
- Je suis un petit robot jardinier. Le monde est gris, la brume me vide, la lumière me fait du bien.
- D'autres robots sont venus avant moi (les anciens corps). *(Faux : c'est lui.)*
- Quand je meurs, je reviens dans l'abri.
- Quelqu'un, de très grand, fabriquait des robots comme moi (l'atelier), et **m'a laissé une consigne**.
- La page 7, pour qui la trouve : *« Elles ne sont pas la brume. Elles sont dans la brume… »* C'est le premier vrai doute, très tôt, pour les curieux.

### L'ordre des Semeurs (un papier posé à côté du berceau) — *décidé le 2026-11-16*
Ce n'est pas une énigme : on le lit dès le réveil.
> « Garder la lumière jusqu'à notre retour. »
> — Ysolde, Commandante

*(La première trace de la fausse piste « ils sont partis » : ils vont revenir. Le nom d'Ysolde mène à la Colonie.)*

### La page 7 (déjà dans le jeu)
> Elles ne sont pas la brume. Elles sont dans la brume. Chaque fois que je souffle ma lanterne, elles s'allument tout autour de moi, comme si elles m'attendaient.
> Les autres disent que le pollen m'a pris la tête.
> Le petit jardinier qu'ils moulent dans cet atelier ne les voit pas : son antenne les éblouit, elle aussi.
> Si tu lis ceci, suis-les. Elles connaissent le chemin de chez moi.
> — G.

---

## 8. Le peuple caché : la ville des Pins
> Déjà construit (phases E à I de `archive/ROADMAP_v3.md`). **Décidé le 2026-11-16 : plus de touche `N`.** La ville des Pins n'est plus jouable pendant la partie : on la voit dans **la cinématique de fin**, où le robot vit sa vie dans sa nouvelle famille, la brume. Avant, seulement des bribes à batterie presque vide. Ce qui suit reste comme matière pour cette fin (et pour les bribes).

### Ce qui se passe quand on éteint
- La nuit tombe (ciel, lune, brume bleue). **La ville pousse du sol** en vague depuis le robot, avec ses collisions (ses chemins n'existent que dans le noir).
- Autour de chaque lanterne allumée, tout est **cendre grise** : des maisons effondrées. Reprendre la lumière les fait **se retisser** lentement. *Chaque lanterne allumée est une cicatrice.*

### Les quartiers (toute l'île est habitée)
| Quartier | Ce qu'il y a |
|---|---|
| **Le hameau des pins** | Les premières maisons, entre les racines. La **première bribe** du jeu. |
| **Le village** | Le ponton, la cabane sur pilotis, la tour de l'Ancienne, le puits, le linge, le banc. |
| **La grande place** | La **fontaine** (là où se trouve la grande lanterne, côté lumière), des maisons et le marché. |
| **Les champs** | Ils ne poussent que la nuit. |
| **Le Levant** | Le côté où se levait le soleil, près de la cascade. |
| **Les Hauts** | Le plateau, sous la grande lanterne. |
| **La forêt** | Des champignons géants. |
| **La Pouponnière** | Sous le plancher de l'abri, dans les fentes. |
| **La crique** | Le **Compteur** et son tas de pierres. |

### Les habitants et ce qu'ils disent
Ils vaquent (routines), rentrent chez eux s'ils ont peur, et ressortent si le robot reste éteint et immobile. On leur parle avec `E`. Les répliques importantes vont dans « Paroles » du carnet.

| Habitant | Ce qu'il dit (résumé) | Ce que ça donne |
|---|---|---|
| **La petite** (1re bribe) | « …il… revient… » | La première parole du jeu. |
| **L'enfant** | « Tu ne m'as pas brûlé. Il y a un endroit secret derrière l'eau qui tombe. » | Indice de l'atelier. |
| **L'Ancienne** | Les Grands-Aveugles ont tout allumé ; chaque fois que tu allumes, une maison tombe en cendre ; Celle-qui-a-soufflé est partie **vers le nord**. | Les cicatrices ; **direction de l'île cachée** (Iris). |
| **Le pêcheur** | Tu tombes toujours près de l'eau ; le Compteur garde une pierre par fois ; j'ai caché une barque sous les racines, à l'ouest. Puis : mon frère guette sur l'îlot de corail. | La barque ; l'îlot. |
| **La jardinière** | La nuit, les racines des grands champignons font des marches. | L'escalier des géants. |
| **Le tisserand** | Je retisse chaque maison fil à fil ; si tu reprends la lumière, je recommence. | Le retissage. |
| **La marchande** | La grande lanterne était notre fontaine ; on vend vite tant qu'il fait noir. | Ce que coûte la grande lanterne. |
| **Le paysan** | Nos champs ne poussent que la nuit ; les deux Soleils du sud brûlent tout. | |
| **La pêcheuse du Levant** | La cascade cache quelque chose : les Grands-Aveugles y gardaient leurs papiers. | 2e indice de l'atelier. |
| **Le gardien des Hauts** | Le Soleil du sommet est le plus vieux, c'est lui qui a chassé nos grands-parents. | |
| **Le Veilleur** (belvédère) | « Celui du sommet est le pire. Quand il brûle, sa lumière descend jusqu'à la mer. » | |
| **Le Guetteur** (îlot de corail) | « De mon île, je vois le Phare… Ceux du Phare n'ont pas d'yeux. Ils écoutent. Si tu vas les voir, va doucement. Et éteint. » | Lien vers le Phare (côté ombre, reporté). |
| **Le Compteur** | « Encore un. » (une pierre de plus à chaque mort) | Le fil des corps (sans le dire). |

### Les chemins de l'ombre
- **L'escalier des géants** : de la crique ouest au plateau, contre la falaise ; en haut, le belvédère et le Veilleur. Indice : la jardinière.
- **Le pont des pêcheurs** : du ponton du village à l'**îlot de corail**, en pleine mer ; le Guetteur. Indice : le pêcheur (2e conversation).
- Antenne allumée, ils n'existent pas. Si on rallume dessus, le sol tient jusqu'à ce qu'on en descende.

---

## 9. Le carnet (juste ce qu'on a vu, sans flèches ni questions — décidé le 2026-11-16)
- **Lieux** : l'abri, la pierre-soleil, les lanternes, la cascade, l'atelier, le sommet, la crique, la barque.
- **Textes** : le mode d'emploi de Tavin (sur le tapis de l'abri), l'ordre d'Ysolde (papier du berceau), la page 7 (pour qui la trouve). **Croquis** : le Phare vu du sommet.
- **Bestiaire** : la méduse. **Paroles** : la 1re bribe, et celles de la ville des Pins.

## 10. Son et ambiance
- Silence endormi → vent, vagues, oiseaux au réveil ; piano doux en couches qui s'ajoutent quand on allume.
- Côté ombre : nappe aquatique dès qu'on éteint, mélodie de verre dans le vrai noir.

## 11. Les liens avec les autres îles
| Sens | Lien |
|---|---|
| île 1 → île 2 (Phare) | On voit le Phare au loin. Le Guetteur parle de ceux du Phare. |
| île 1 → île 3 (Colonie) | L'ordre d'Ysolde, sur le papier à côté du berceau (« jusqu'à notre retour »). |
| île 1 → île 7 (île cachée) | L'Ancienne : Celle-qui-a-soufflé est partie **vers le nord**. La page 7 : « suis-les, elles connaissent le chemin de chez moi ». |
| île 1 → île 6 (Centrale) | Le berceau a sa propre ligne d'énergie : c'est elle qu'on coupera à la fin. |
| île 2 → île 1 | Le câble de la crypte du Phare est la ligne du berceau. |
| île 3 → île 1 | La lettre de Tavin : « Le berceau du jardinier a sa propre ligne. Quoi qu'il arrive, il tiendra. » |

---

## 12. Ce qui change avec la v4 (résumé)
- L'île devient **l'île du robot** : berceau et atelier des Semeurs, personne n'y vivait.
- **Plus de 2e moitié** : la ville des Pins reste, mais comme un **secret** visible pour qui éteint.
- **La fin du jeu** passe par ici d'une autre façon : c'est la ligne du berceau qu'on coupera, à la Centrale.

## 13. Ce qu'il faut retirer ou adapter (à faire au prochain dev)
**Décidé le 2026-11-15**
1. **La fin de l'île 1** : plus de fondu. Au sommet, on voit la **silhouette sombre du Phare** et la **lueur de sa bouée** (le Phare ne s'allume plus au loin).
2. **La barque** revient **cachée dans la crique** à chaque boucle, **toujours à flot**.
3. **Retirer le contenu de l'ancienne 2e moitié** :
   - la touche de debug « bascule » ;
   - le Compteur qui dit « Tu es revenu deux cent quatorze fois » (il garde seulement « Encore un. ») ;
   - la mission « Laisser sortir les petits » (veilleuse de l'abri, guidage de la Pouponnière, récompense) ;
   - l'Ancienne après la bascule (« Celui-qui-revient… ») et après la mission (« Les petites ont vu les pins… ») ;
   - l'aide « essaim de la Pouponnière » ;
   - l'extension du hameau et la 3e couche musicale (le chœur du peuple après la libération).

**Décidé le 2026-11-16**
4. Ajouter **l'ordre d'Ysolde** sur un papier posé à côté du berceau (pas une énigme).
5. L'atelier est **un peu trop grand** pour le robot (Semeurs de 2,50 à 3 m) : établi à hauteur de poitrine, portes d'environ 3 m.
6. **Pas de marée** sur l'île 1.
