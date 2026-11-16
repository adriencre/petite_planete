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
- **Ce qu'elle apprend** (sans un mot) : la batterie, la brume, allumer, reprendre la lumière, planter, mourir et revenir, le carnet.
- **Ce qu'elle cache** : le mode nuit (`N`), la page 7 d'Iris, la ville des Pins dans le noir.
- **Ce qu'elle ouvre** : la barque, donc tout l'archipel. On voit le Phare au loin.
- **Les fils de l'enquête présents ici** :
  - **le berceau et les corps** (le berceau, l'atelier, le premier ancien corps) ;
  - **Iris** (la page 7, pour qui la trouve).
- **Durée** : 30 à 45 min la première fois. Un joueur qui sait peut en partir en 5 minutes (pierre-soleil cachée → barque).

---

## 3. Le lieu

```
                    ▲ sommet (6 m) : lanterne du sommet, vue sur le Phare
                    │
        plateau (3 m) ── cascade ─┐ rebord caché → grotte → ATELIER DES ROBOTS
              ▲                   │
   racines-escalier (terreau)     │
              │                   │
   GRANDE LANTERNE ── lanternes 1, 2, 3 ── ABRI (berceau) ── pierre-soleil
              │
   crique ouest (brume épaisse) : ancien corps, BARQUE cachée sous les racines,
                                  pierre-soleil cachée
```
*(Les détails exacts sont dans la scène ; la carte du carnet est dessinée depuis le GridMap.)*

### Les lieux
| Lieu | Ce qu'on y trouve |
|---|---|
| **L'abri** | Le berceau (lumière qui s'allume à chaque réveil), l'horloge arrêtée, le carnet, un coin sombre où quelque chose scintille, la veilleuse au-dessus de la porte. L'abri est **à la taille du robot**. |
| **La pierre-soleil** | Juste à la sortie de l'abri : l'antenne vide s'y recharge. Premier geste du jeu. |
| **Les lanternes 1, 2, 3** | Le chemin vers le centre de l'île. Chacune réveille sa zone. |
| **La grande lanterne** | Au centre. Elle ne s'allume qu'une fois les trois petites allumées (racines lumineuses qui convergent). Grande vague de couleur. |
| **Le terreau** | Une cosse s'ouvre, le robot porte la graine et la plante dans le terreau gravé : des **racines-escalier** poussent jusqu'au plateau. |
| **Le plateau et le sommet** | Le jardin mort, la charrette, le banc. Au sommet, la **lanterne du sommet** : l'île entière s'éveille. |
| **La cascade** | Derrière l'eau, un rebord caché → une grotte → **l'atelier des robots**. |
| **L'atelier des robots** | Le moule, les pièces détachées, l'établi, la lanterne de l'atelier, la **page 7**. **À la taille des Semeurs** (très grands) : établi immense, outils géants **[à valider]**. |
| **La crique ouest** | Noyée de **brume épaisse**. Le **premier ancien corps**, couvert de mousse. La **barque**, cachée sous les racines. La **pierre-soleil cachée**. |
| **Au loin** | La silhouette sombre du Phare, et la petite lueur de la bouée de son port. |

---

## 4. Les cycles sur l'île
- La **marée** (8 min) touche la crique et la plage **[à valider : est-ce qu'on s'en sert ici ?]**.
- Une fois le Phare rallumé (dans la même boucle), on voit son **faisceau** balayer la mer depuis le sommet.

---

## 5. Côté lumière

### Le déroulé (première boucle)
1. **Le réveil** (~23 s, sans contrôle) : noir → le robot couché sur le flanc → un œil vacille, puis l'autre → il se redresse, regarde ses mains, se lève en titubant, regarde autour de lui. On prend la main.
2. **La sortie** : la caméra recule lentement sur l'île grise (sans contrôle). Une **luciole** apparaît et guide.
3. **L'antenne est vide** : on la recharge à la **pierre-soleil**.
4. **La première lumière** (longue cinématique) : le robot s'accroupit, branche le câble de son poignet dans la prise de la lanterne → pulsations dorées → la lanterne se charge et s'ouvre en crans → la zone se réveille en vague de couleur → il débranche. Les suivantes sont plus courtes. *(2026-11-16 : remplace le glyphe tracé dans l'air — pas de magie, voir DA.md.)*
5. Lanternes 1, 2, 3 → **racines lumineuses** → **la grande lanterne**.
6. **Planter** : la cosse, la graine, le terreau, les racines-escalier → le plateau.
7. **La lanterne du sommet** : toute l'île s'éveille, coucher de soleil. On voit le Phare éteint et la lueur de sa bouée.
8. **La barque** : on la trouve dans la crique, et on part librement (plus de fondu).

### Les énigmes
L'île 1 est un tutoriel : ses énigmes sont petites.

| Énigme | Ce qu'il faut comprendre |
|---|---|
| **L'antenne vide** | La pierre-soleil recharge. |
| **La batterie** | La brume vide, la lumière recharge, allumer coûte. On avance de lumière en lumière. |
| **La grande lanterne** | Elle a besoin des trois petites (les racines lumineuses le montrent). |
| **Monter au plateau** | La cosse donne une graine ; le terreau gravé attend une graine ; les racines font l'escalier. |
| **La crique** | La brume épaisse vide trop vite : il faut y arriver avec assez de batterie, ou avec la pierre-soleil cachée, ou dans le noir (`N`). |

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
| **L'atelier des robots** (derrière la cascade) | Le moule, les pièces : on fabrique des robots ici. Le croquis de la touche `N`. **L'ordre des Semeurs** gravé sur le moule (§7). |
| **La page 7 d'Iris** (lumineuse, sur l'établi) | Blanche tant que la lanterne de l'atelier brille. Il faut **reprendre sa lumière, puis éteindre l'antenne (`N`)** pour la lire. |
| **La graine cachée** (coin de l'abri) | En mode nuit, une traînée de Lueurs en part et file sous le berceau. |
| **Le premier ancien corps** (crique) | Couvert de mousse ; dans le noir, des Lueurs brillent dessus. |

---

## 6. Le mode nuit (touche `N`, secret)
- Jamais indiqué. Indices : le croquis de l'atelier (robot antenne éteinte sous la lune, touche « N » griffonnée), la page 7.
- Antenne éteinte : la brume ne vide plus, la lumière ne recharge plus, **aucune action de lumière**, le peuple caché est visible.
- Sur l'île 1, ça transforme tout (§8) : la nuit tombe, la lune, la ville des Pins pousse du sol.
- **C'est le principe v4 du « monde caché »** : rien n'est donné, mais dès l'île 1, un joueur curieux **peut** voir le peuple de la brume.

---

## 7. Le récit (ce que le joueur comprend sur l'île 1)
- Je suis un petit robot jardinier. Le monde est gris, la brume me vide, la lumière me fait du bien.
- D'autres robots sont venus avant moi (les anciens corps). *(Faux : c'est lui.)*
- Quand je meurs, je reviens dans l'abri.
- Quelqu'un, de très grand, fabriquait des robots comme moi (l'atelier), et **m'a laissé une consigne**.
- La page 7, pour qui la trouve : *« Elles ne sont pas la brume. Elles sont dans la brume… »* C'est le premier vrai doute, très tôt, pour les curieux.

### L'ordre des Semeurs (gravé sur le moule de l'atelier) **[nouveau, à valider]**
> « Garder la lumière jusqu'à notre retour. »
> — Ysolde, Commandante

*(La première trace de la fausse piste « ils sont partis » : ils vont revenir. Le nom d'Ysolde mène à la Colonie.)*

### La page 7 (déjà dans le jeu)
> J'écris ici à la peinture qui brille. Seuls ceux qui éteignent pourront me lire.
> Elles ne sont pas la brume. Elles sont dans la brume. Chaque fois que je souffle ma lanterne, elles s'allument tout autour de moi, comme si elles m'attendaient.
> Les autres disent que le pollen m'a pris la tête.
> Le petit jardinier qu'ils moulent dans cet atelier ne les voit pas : son antenne les éblouit, elle aussi.
> Si tu lis ceci, suis-les. Elles connaissent le chemin de chez moi.
> — G.

---

## 8. Le peuple caché : la ville des Pins
> Déjà construit (phases E à I de `archive/ROADMAP_v3.md`). Dans la v4, il n'y a plus de 2e moitié : tout ce qui suit est un **secret**, visible pour qui éteint.

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
| **Les Hauts** | Le plateau, sous la lanterne du sommet. |
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

## 9. Le carnet (tableau d'enquête)
- **Lieux** : l'abri, la pierre-soleil, les lanternes, le terreau, la cascade, l'atelier, le sommet, la crique, la barque.
- **Rumeurs** **[à valider]** :
  - « Garder la lumière jusqu'à notre retour. — Ysolde » → **où sont-ils partis ?** (mène à la Colonie) ;
  - « On voit un phare au loin, éteint. » → **le Phare** ;
  - (page 7) « Suis-les. Elles connaissent le chemin de chez moi. » → **qui est G. ?**
- **Questions ouvertes** : « Qui sont les autres robots ? », « Qui m'a fabriqué ? », « Où sont ceux qui vont revenir ? ».
- **Bestiaire** : la méduse. **Paroles** : la 1re bribe, et celles de la ville des Pins.

## 10. Son et ambiance
- Silence endormi → vent, vagues, oiseaux au réveil ; piano doux en couches qui s'ajoutent quand on allume.
- Côté ombre : nappe aquatique dès qu'on éteint, mélodie de verre dans le vrai noir.

## 11. Les liens avec les autres îles
| Sens | Lien |
|---|---|
| île 1 → île 2 (Phare) | On voit le Phare au loin. Le Guetteur parle de ceux du Phare. |
| île 1 → île 3 (Colonie) | L'ordre d'Ysolde gravé sur le moule (« jusqu'à notre retour ») **[à valider]**. |
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

**À valider**
4. Ajouter **l'ordre d'Ysolde** gravé sur le moule de l'atelier.
5. Agrandir l'atelier à la **taille des Semeurs** (établi et outils géants), pour qu'on sente dès l'île 1 qu'ils étaient très grands.
