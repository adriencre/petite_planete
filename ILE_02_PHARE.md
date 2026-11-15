# Île 2 — Le Phare

> Document complet de l'île. À lire avec **`ENQUETE.md`** (l'histoire v4 : les Semeurs, la grande nuit, Iris, les 7 îles) et `DESIGN.md` (les règles, la mer, la barque, les cycles).
> Mis à jour le 2026-11-15 pour la v4.
> **Validé** : le plan (§3), G1, G2, G3 (§5), la page 1, « six tours du faisceau », la ligne sans nom du registre.
> Les points marqués **[à valider]** sont des propositions, dont les nouvelles énigmes ajoutées pour **enrichir** l'île (décision : l'enrichir avec d'autres types d'énigmes et des morceaux de l'enquête).

---

## 1. En une phrase
Le poste d'Iris, la Gardienne : un phare sur un rocher coupé du monde par la marée, qui ne fabrique pas sa lumière mais **la rassemble**. On y découvre une femme précise et fière qui surveillait toutes les lanternes de l'archipel… et qui, peu à peu, a cessé d'y croire.

## 2. Sa place dans le jeu
- **L'île conseillée après l'île 1** : on voit le Phare depuis le sommet de l'île 1.
- **Dans l'histoire (v4)** : c'est **le poste d'Iris**. Elle a survécu à la grande nuit (elle vivait déjà dans le noir) : **pas de squelette ici**. Le Phare est vide et rangé, comme si elle venait de partir.
- **Les fils de l'enquête présents ici** :
  - **Iris** : son bureau, ses relevés, sa chambre, ses doutes qui grandissent ;
  - **la maladie et les lanternes** : le registre montre l'escalade des lanternes, île par île ;
  - **le berceau et les corps** : le câble de la crypte (la ligne du berceau), l'ancien corps de la galerie.
- **Ce qu'elle apporte au jeu :**

| Nouveauté | Ce que ça change |
|---|---|
| **La marée** (cycle permanent, 8 min) | Premier lieu où **le moment compte** : la chaussée, le gué du Cap du Large, les grottes et l'épave n'existent qu'à marée basse. |
| **Les miroirs des Semeurs** | La **lumière dirigée** : renvoyer la lumière d'un cap à l'autre, jusqu'à la lentille. |
| **Le faisceau tournant** (une fois le Phare rallumé) | Un **rythme** sur l'île et en mer. La lentille devient **orientable**. |
| **La carte de l'archipel** | Du sommet, **le carnet dessine les autres îles**. C'est ce qui « ouvre » le jeu. |
| **Iris** | Son bureau, sa chambre, ses notes : elle devient un personnage. |

- **Durée** : 1 h à 1 h 30 pour une première découverte complète.

---

## 3. Le lieu (plan validé le 2026-11-15)

**Plan vu de dessus : `tools/plan_ile2.png`** (généré par `tools/plan_ile2.py`, qui contient les zones en mètres et servira à construire le GridMap).

```
                    CAP DU LARGE (1,5 m) — lanterne + miroir, ancien corps échoué
                          ▲
                          ░ gué : 5 roches (marée basse seulement)
                          ░
   CAP OUEST (5 m) ═══ sentier dans la brume ═══ ROCHER DU PHARE (4 m) ── CAP EST (2,5 m)
   lanterne + miroir                             plateau (5 m) + PHARE      lanterne + miroir
                                                 banc, jardin mort          flaque + pierre-soleil
                                                 escalier taillé
                                                 entrée des grottes (estran)
                                                      │
                                                 CHAUSSÉE (0 m, noyée à marée haute,
                                                      │    brume épaisse, 3 balises)
                                                      │
                                    LE PORT DES GARDIENS (1 m)
                                    maison du quai, hangar, échelle de marée
                                                      │
          ÉPAVE (marée basse)                       PONTON (toute marée)
                                         BOUÉE-LANTERNE (dans la passe)
```

- **Taille** : environ 1 190 cases de terre ferme (île 1 : 887), mais beaucoup plus **verticale** (rocher à 4 m, plateau à 5 m, tour d'environ 18 m).
- **Échelle (v4)** : le Phare est bâti **à la taille des Semeurs** (très grands, fins) : marches hautes, portes immenses, une table de travail au-dessus de la tête du robot **[à valider]**.
- **Marée** : l'eau est à −0,6 m à marée basse et à +0,5 m à marée haute. Tout ce qui est à 0 m (chaussée, gué, estran, flaque, épave) n'existe qu'à marée basse.
- **Palette** : pierre claire, falaises grises, phare blanc à bandes rouille délavée, varech, eau verte des flaques, brume froide.

### Les zones
| # | Zone | Ce qu'on y trouve |
|---|---|---|
| 1 | **Le ponton** | L'arrivée en barque, accessible à toute marée. |
| 2 | **La bouée-lanterne** | Dans la passe, à rallumer depuis la barque. Point de recharge. |
| 3 | **La maison du quai** | Le logement des gardiens de passage : lits géants, cirés, une lanterne. |
| 4 | **Le hangar** | Des barques retournées, le **miroir d'essai** et sa porte. |
| 5 | **L'échelle de marée** | Des repères peints sur le mur du quai. |
| 6–8 | **La chaussée et ses balises** | Un chemin de dalles posé sur l'eau, couvert de brume épaisse. Trois balises. |
| 9 | **L'ancien corps couvert d'algues** | À mi-chaussée : il est parti trop tard. |
| 10 | **L'entrée des grottes** | Sur une petite plage d'estran, au pied du rocher. |
| 11 | **La crypte des Semeurs** | Au fond des grottes, sous le phare : le **câble du berceau**. |
| 12 | **Le banc d'Iris** | Au bord du rocher, tourné vers le nord-ouest (vers sa maison, qu'on ne voit pas). |
| 13 | **Le jardin mort** | Des bacs de terre sèche, un arrosoir, un **arbre rose mort** **[à valider]**. |
| 14 | **Le Cap Est** | Facile d'accès. Lanterne + station de miroir. |
| 15 | **La flaque du Cap Est** | À marée basse : une **pierre-soleil** au fond. |
| 16 | **Le Cap Ouest** | Au bout d'un sentier de falaise noyé de brume. Lanterne + station de miroir. |
| 17 | **Le Cap du Large** | Au nord, au bout du gué. Lanterne + station de miroir. |
| 18 | **L'ancien corps échoué** | Sur les rochers du Large : il s'est fait prendre par la marée. |
| 19 | **L'épave du ravitailleur** | Au sud-ouest, couchée sur un banc de sable. Entourée de brume épaisse. |

### Le Phare, de bas en haut
| Niveau | Ce qu'on y trouve |
|---|---|
| **Rez** | **La salle des machines** : engrenages arrêtés, la chaîne de la lentille, le **schéma des engrenages** peint au mur. |
| **1er** | **Le bureau d'Iris** : sa table, ses relevés, la **table des marées**, la **page 1**, le **plan des miroirs**, la note de la clé, la ligne de la pleine lune. Au fond, **sa chambre**, fermée **[à valider]**. |
| **2e** | **La salle des cartes**, fermée à clé : le registre, les relèvements. |
| **Sommet** | La **grande lentille**, intacte, sans lampe, avec une couronne graduée. La **galerie extérieure**, avec **la lunette d'Iris** **[à valider]** et l'**ancien corps de la galerie**. |

---

## 4. Les cycles sur l'île
- **La marée** (8 min : 4 min basse, 4 min haute). Le ressac change avec elle. L'échelle de marée la montre.
- **Le faisceau** (une fois le Phare rallumé, un tour toutes les 40 s) : la brume recule là où il passe.
- **La mer reste basse le temps de six tours du faisceau** (6 × 40 s = 4 min) : une horloge sans chiffres (validé).
- **La lune** (24 min) : pour le secret de la pleine lune (§10) et la très basse mer du vieux port de la Colonie.

---

## 5. Côté lumière : les énigmes

> **G1 à G6 sont validés.** G4, G5 et G6 ont été ajoutés pour enrichir l'île avec d'autres types d'énigmes (mécanisme, lieux cachés, observation).

### G1. « Atteindre le Phare » (la marée) — *validé*
- **La situation** : la chaussée est sous l'eau à marée haute ; à marée basse, elle est couverte d'une brume épaisse qui vide vite la batterie.
- **Où on l'apprend** : on **voit** l'eau descendre et remonter ; l'**échelle de marée** ; l'**ancien corps** à mi-chaussée, parti trop tard.
- **La solution** : se recharger (bouée, maison du quai), attendre la marée basse, traverser **en allumant les trois balises**.
- **Le piège** : partir au début de la marée basse, pas à la fin.
- **Ce que ça ouvre** : le rocher et le phare.

### G2. « Rallumer le Grand Phare » (les miroirs) — *validé*
- **La situation** : la grande lentille est intacte, mais il n'y a pas de lampe.
- **Où on l'apprend** : la **page 1** ; le **plan des miroirs** à moitié effacé ; l'**ancien corps échoué** du Large ; le **miroir d'essai** du hangar.
- **Le trajet de la lumière** : **Cap Est → Cap du Large → Cap Ouest → lentille**.
- **Le mécanisme** : chaque cap a une **lanterne** et une **station de miroir** (`E`, par crans) ; un faisceau visible part de chaque miroir allumé ; **les trois caps doivent briller en même temps.**
- **Les contraintes** : la batterie, la marée (le gué), l'orientation, la brume du sentier Ouest.
- **Ce que ça ouvre** (un grand moment, lent) : la lumière fait le tour du rocher et monte dans la lentille ; **le faisceau** s'allume et tourne ; **le carnet dessine la carte de l'archipel** ; le faisceau perce la brume du large autour de l'épave.

### G3. « La clé de la salle des cartes » (une chaîne sur l'île) — *validé*
- **La situation** : la salle des cartes est fermée à clé.
- **Où on l'apprend** : la note du bureau (« J'ai laissé la clé dans la cabine, à bord du ravitailleur ») ; depuis la galerie, on **voit l'épave**.
- **La chaîne** : le **Phare rallumé** (son faisceau perce la brume de l'épave) + la **marée basse** (l'épave affleure) + **la barque** ; la clé est dans la cabine du capitaine.
- **Ce que ça ouvre** : la salle des cartes, avec le **registre** et les **relèvements**.

### G4. « La salle des machines » (mécanisme) — *validé*
- **La situation** : une fois le Phare rallumé, la lentille tourne, mais la couronne graduée est **bloquée** : on ne peut pas la viser.
- **Où on l'apprend** : au rez, les engrenages sont démontés, et un **schéma** peint au mur (en partie couvert de suie) montre comment ils s'emboîtent.
- **La solution** : remettre les engrenages en place (`E` pour déplacer et tourner chaque roue) en suivant le schéma. La partie effacée se devine en regardant **les marques d'usure au sol** sous chaque axe (observation).
- **Ce que ça ouvre** : la **lentille orientable**. Avec les relèvements (G3), on peut la pointer vers chaque île.

### G5. « La chambre d'Iris » (lieux cachés) — *validé*
- **La situation** : au fond du bureau, une porte fermée de l'intérieur, trop haute pour le robot.
- **Où on l'apprend** :
  - un **dessin d'Aube** (le même style que ceux de la Colonie) est punaisé au-dessus de la porte : « Pour Iris. Ma cachette, c'est par le toit » ;
  - depuis la galerie, on voit une **lucarne** ouverte sur le toit du 1er étage.
- **La solution** : sortir sur la galerie, descendre par l'échelle de service le long de la tour et entrer par la lucarne. Le robot est **assez petit pour y passer**, comme Aube.
- **Ce que ça ouvre** : **la chambre d'Iris** (§7) : sa vie à elle, plus seulement ses relevés.

### G6. « La lunette d'Iris » (observation) — *validé*
- **La situation** : sur la galerie, une **lunette** sur pied. Son socle a **des crans gravés**, avec un nom à chaque cran.
- **Ce qu'on voit** : chaque cran cadre un lieu lointain, en gros plan : le quai de la Colonie (des caisses de départ empilées), la ville haute couverte de lanternes, la Nef échouée au loin, la brume blanche de l'île blanche…
- **Le cran sans nom** : il cadre **la mer vide**, au nord-ouest. Il n'y a rien, juste de l'eau. C'est la direction du banc d'Iris, celle de la **ligne sans nom du registre**, et celle où l'on verra l'île cachée à la pleine lune.
- **Ce que ça donne** : des **rumeurs** dans le carnet vers les autres îles, et un **mystère** (pourquoi regarder la mer vide ?).

### Les petites
- **Le miroir du port** : un miroir d'essai renvoie la lumière de la bouée sur la porte du hangar, qui s'ouvre. C'est le tutoriel muet des miroirs.
- **La bouée du port** : la rallumer (depuis la barque) donne un point de recharge.
- **Le raccourci des grottes** : à marée basse, en barque, on entre par les grottes jusqu'au pied du phare.

---

## 6. Les secrets
| Secret | Où | Ce qu'il raconte |
|---|---|---|
| **La crypte et le câble du berceau** | Au fond des grottes (marée basse) | Un gros câble tiède sort de la roche et plonge vers le large, vers **la Centrale**. Une plaque : **« Ligne du berceau. Prioritaire. Ne jamais couper. »** C'est la ligne qui a survécu à la grande nuit (et celle qu'on coupera à la fin). |
| **L'ancien corps de la galerie** | Au sommet | Assis face à la mer : le robot est déjà venu ici, il y a très longtemps. |
| **L'Écoute** | Près de la bouée, à batterie basse | Une créature sans yeux (bestiaire). |
| **Le banc d'Iris** | Au bord du rocher | On s'y assoit : la caméra montre ce qu'elle regardait, le nord-ouest et la mer vide. |
| **La pierre-soleil** | La flaque du Cap Est, à marée basse | Une recharge sûre pour G2. |
| **L'arbre rose mort** | Le jardin mort | Iris en avait un ici. Elle l'a laissé mourir **[à valider]**. Seul le sens change après la Colonie (les arbres roses viennent de chez eux). |

---

## 7. Le récit et les textes

### Ce que le joueur comprend sur le Phare
- Iris ne gardait pas un phare : elle gardait **toutes** les lanternes de l'archipel, depuis le Phare.
- Ses notes montrent une femme **méticuleuse et fière**… puis ses doutes grandissent (le registre, sa chambre).
- Elle connaissait **Aube**, l'enfant de la Colonie. Toutes deux voyaient quelque chose dans la brume.
- Elle regardait souvent **la mer vide**, au nord-ouest.
- Un câble part du Phare vers la Centrale : **la ligne du berceau**, qu'on ne doit « jamais couper ».
- Elle n'est pas morte ici : le Phare est vide et rangé. *(La fausse piste tient : elle est partie, elle aussi ?)*

### La page 1 (au bureau) — *validée*
> Tournée du Phare, jour 112.
> Pour les nouveaux, puisque personne ne lit les consignes : le Phare ne fait pas de lumière. Il la rassemble. Les trois caps la lui renvoient, quand les miroirs sont bien tournés. Si un seul cap s'éteint, la lentille ne voit rien.
> J'ai nettoyé les vitres du Cap Est. Le miroir du Large a encore bougé avec la tempête. N'allez jamais au Large à marée montante : la mer ne prévient pas.
> Rappel : on ne reprend pas la lumière devant les arbres roses. Ils ne le supportent pas.
> — G.

*(À remplacer dans le jeu : `assets/notebook/journal/page_01.tres` contient l'ancienne version.)*

### Les notes du bureau
- **La note de la clé** **[à valider]** : « J'ai laissé la clé de la salle des cartes dans la cabine, à bord du ravitailleur. Je la reprendrai à la prochaine basse mer. Pas sans le Phare : la brume du large y est trop épaisse. »
- **La ligne de la pleine lune** (dans la marge d'un relevé, d'une autre encre) : « Les nuits de pleine lune, le Phare chante, et je vois ma maison. »
- **La table des marées** (validée pour les six tours) : un dessin de l'échelle du quai, avec « basse » et « haute », et dessous : « Basse mer : six tours du faisceau. Pas un de plus. » **[nouveau, à valider]** Plus bas, un troisième trait : « Pleine lune : plus bas que tout. Le vieux port respire. » (C'est un indice pour le vieux port de la Colonie.)
- **Le plan des miroirs** : les trois caps et le Phare vus de dessus ; une partie effacée par l'eau (on voit la flèche Est → Large, le reste est illisible).

### La chambre d'Iris (G5) **[textes à valider]**
- Un lit à sa taille, une seule tasse, une lanterne **éteinte et débranchée** sur la table de nuit.
- Au mur, **le dessin d'Aube** : des silhouettes de brume qui dansent autour d'une grande et d'une petite Semeuse. « Iris et moi et nos amis. »
- Une lettre jamais envoyée, à Ysolde :
> Ysolde,
> Tu me demandes d'ajouter des lanternes à l'île blanche. Je ne le ferai pas.
> Les malades vont plus mal à chaque lanterne que j'allume, pas mieux. Saule le voit aussi, mais elle n'ose pas te le dire.
> Éteins une seule nuit, avec moi. Une seule. Tu verras ce que je vois.
> — Iris

*(Le premier vrai indice de « ils se sont tués eux-mêmes ». Le prénom « Iris » est connu pendant l'enquête : validé.)*

### La salle des cartes (G3)
- **Le registre des lanternes** : un grand livre, une page par île, avec le nombre de lanternes année après année. Les lignes **[nouvelles, à valider]** :
  - « Réveil : l'abri, la veilleuse, le sommet. Rien à signaler. Le jardinier dort. »
  - « Colonie : 40… 90… 160… 310. » *(les chiffres explosent d'année en année)*
  - « Île blanche : on m'en demande encore. Ils disent que c'est pour soigner. Je n'y crois plus. »
  - « Nef : aucune, en attendant le départ. »
  - « Centrale : ne pas toucher. Tavin s'en occupe. »
  - **Une ligne sans nom**, avec seulement le dessin d'une petite maison, et aucune lanterne *(validé : comprise plus tard)*.
- **Les relèvements** : sur le mur, une rose des vents gravée avec l'angle de chaque île (« Colonie », « Île blanche », « Nef », « Centrale »). Ils se recopient dans le carnet.

### Ce qui s'inscrit dans le carnet (tableau d'enquête)
- **Carte** de l'île 2, puis **la carte de l'archipel** (G2).
- **Lieux** : le port, la chaussée, le phare (4 niveaux), les trois caps, l'épave, la crypte.
- **Rumeurs** :
  - « Le registre : la Colonie a de plus en plus de lanternes. » → **la Colonie** ;
  - « Iris refuse d'ajouter des lanternes à l'île blanche. » → **la Quarantaine** ;
  - « La lunette cadre une épave géante au loin. » → **la Nef** ;
  - « Ligne du berceau. Ne jamais couper. » → **la Centrale** ;
  - « Le cran sans nom regarde la mer vide. » / « Je vois ma maison. » → **?** (l'île cachée).
- **Notes** recopiées : la table des marées, les relèvements.
- **Bestiaire** : l'Écoute.

---

## 8. Le peuple caché : les Aveugles du Phare (reporté)
> **Reporté** : on se concentre d'abord sur le jeu de lumière. Ce qui suit est la proposition précédente, à reprendre plus tard.
> Avec la v4, il n'y a plus de 2e moitié : la mission « Voir la mer » deviendrait un **secret optionnel**.

- Une colonie qui vit **sur le rocher et dans les grottes**. Éblouies depuis des siècles, elles **ne brillent presque plus** ; elles **entendent** au lieu de voir : il faut **marcher doucement**.
- Des maisons de **coquillages retournés**, recousus de fils de lumière pâle.
- Des habitants proposés : la Sonneuse, le Passeur, la Ramasseuse de varech, l'Enfant-coquille, le Vieux du Large, l'Écoute.
- Des chemins de l'ombre proposés : les **cordes du Passeur** au-dessus de la chaussée, l'**escalier des bernacles** jusqu'à la galerie.
- **Leur souvenir de la grande nuit** **[idée v4]** : ils étaient là quand Iris a éteint le Phare pour la dernière fois. « Celle-qui-a-soufflé a soufflé le grand. Puis tout s'est éteint, partout. Et on a revu la mer. »

---

## 9. Les liens avec les autres îles

### Ce qui vient d'ailleurs
- **La pleine lune et l'île cachée** : « Les nuits de pleine lune, le Phare chante, et je vois ma maison. » À la pleine lune, la lentille pointée **au cran sans nom** concentre le clair de lune et **montre l'île cachée**. La clé de lecture viendra d'ailleurs (une île à décider : la Nef ou la Quarantaine) **[à décider]**. C'est la seule chose impossible à la première visite.
- **L'ancien lien avec le Marais** (« quand le grand œil nous regarde, la brume s'ouvre ») **est à remplacer**, puisque le Marais n'existe plus. Décidé : pointé vers **l'île blanche** (la Quarantaine), le faisceau ouvre **un couloir dans la brume de la mer** qui l'entoure. C'est une **deuxième route** pour y aller (la première : bien préparer la lanterne de la barque).

### Ce que l'île 2 donne ailleurs
- la **table des marées** (et le trait de la pleine lune), pour le vieux port de la Colonie ;
- la **carte de l'archipel** et les **relèvements** ;
- le **principe des miroirs** (pour la Nef et la Centrale) **[à valider]** ;
- le **registre** : l'escalade des lanternes, le doute d'Iris, la ligne sans nom ;
- la **page 1**, avec les arbres roses (compris à la Colonie) ;
- **la ligne du berceau** (comprise à la Centrale, coupée à la fin).

### Récapitulatif
| Sens | Lien |
|---|---|
| île 1 → île 2 | On voit le Phare depuis l'île 1. |
| île 2 → île 3 (Colonie) | Le registre de la Colonie ; le trait de la pleine lune (vieux port) ; la page 1 (arbres roses) ; le dessin d'Aube dans la chambre. |
| île 3 → île 2 | Le carnet d'Aube : « Iris dit qu'elle les voit aussi. » |
| île 2 → île 4 (Quarantaine) | La lettre d'Iris à Ysolde ; le registre de l'île blanche ; le faisceau qui ouvre la brume. |
| île 2 → île 5 (Nef) | La lunette ; « Nef : aucune, en attendant le départ ». |
| île 2 → île 6 (Centrale) | La crypte : la ligne du berceau. |
| île 2 → île 7 (île cachée) | Le banc, le cran sans nom, la ligne sans nom, la pleine lune. |

---

## 10. Son et ambiance
- **Côté lumière** : ressac et vent, mouettes au loin, cloche de la bouée ; le ressac change avec la marée. La chaîne et les engrenages du Phare au rallumage.
- **Musique** : un thème plus froid et plus large que l'île 1 (cordes graves, piano espacé), qui s'ouvre au rallumage du Phare. Dans la chambre d'Iris : presque rien, le vent par la lucarne.

---

## 11. Feuille de route de l'île 2
> Le dev ne reprend qu'une fois tous les documents des îles terminés.

**Phase J : l'archipel (commun à toutes les îles)**
- **J1.** La scène Archipel. **J2.** La barque pilotable. **J3.** La brume en mer et la lanterne de la barque. **J4.** L'horloge du monde (`WorldClock`) et la marée.

**Phase K : l'île 2**
- **K1.** La maquette grise (GridMap, depuis `tools/plan_ile2.py`), à l'échelle des Semeurs.
- **K2.** G1 : la chaussée, les balises, l'échelle de marée, l'ancien corps.
- **K3.** Les miroirs (composant réutilisable) et G2 : trois caps, la lentille, le rallumage, la carte de l'archipel.
- **K4.** Le faisceau tournant ; G4 (salle des machines) et la lentille orientable.
- **K5.** G3 : la clé dans l'épave, la salle des cartes, le registre, les relèvements.
- **K6.** G5 (chambre d'Iris), G6 (lunette), récit et secrets.
- **K7.** Habillage : modèles (Blender), son, musique.

**Ordre de travail** : K1 → J4 → K2 → K3 → K4 → J1–J3 → K5 → K6 → K7.

---

## 12. Décisions et points ouverts
**Décidé**
- Énigmes G1, G2, G3 ; le plan (`tools/plan_ile2.png`) ; le trajet de la lumière **Cap Est → Cap du Large → Cap Ouest → lentille**.
- La nouvelle page 1 ; « six tours du faisceau » ; la ligne sans nom du registre.
- Lanterne de barque, cycles (marée 8 min, faisceau 40 s, lune 24 min), aucun changement définitif.
- Le côté ombre est reporté.

**Validé le 2026-11-15 (mise à jour v4)**
- Les nouvelles énigmes **G4** (salle des machines), **G5** (chambre d'Iris) et **G6** (lunette d'Iris).
- **Le prénom « Iris » est connu pendant l'enquête** (Aube, la lettre de sa chambre). La fin secrète changera de phrase.
- **Le faisceau orienté vers l'île blanche** ouvre un couloir dans la brume de la mer qui l'entoure : une 2e route vers la Quarantaine.
- **La clé de lecture de la pleine lune** sera fixée en concevant la Quarantaine ou la Nef.

**Encore à valider**
1. Le câble de la crypte devient **la ligne du berceau** (« Ne jamais couper »).
2. Les nouveaux textes : la lettre d'Iris à Ysolde, le registre par île, le trait de la pleine lune sur la table des marées, la note de la clé.
3. L'arbre rose mort dans le jardin d'Iris.
