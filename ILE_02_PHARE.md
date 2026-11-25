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

### Forme v6 (décidée le 2026-11-16) : **croix**
Le rocher du Phare au centre (niveau le plus haut) et trois bras : le cap Ouest par le sentier dans la brume, le cap Est, et le cap du Large par le gué (estran). Au sud, la chaussée (estran dans la brume) mène au port. L'épave est sur un estran au sud-ouest, dans la brume. Plan validé conservé, en plateaux carrés.
Schéma : `concept/ile_02_formes.png` (variante A), dessiné par `tools/carte_iso.py ile_02`.

```
                    CAP DU LARGE (1,5 m) — miroir, ancien corps échoué
                          ▲
                          ░ gué : 5 roches (marée basse seulement)
                          ░
   CAP OUEST (5 m) ═══ sentier dans la brume ═══ ROCHER DU PHARE (4 m) ── CAP EST (2,5 m)
   miroir                                        plateau (5 m) + PHARE      lanterne + miroir
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
- **Échelle (DA v5)** : le Phare est bâti à la taille des Semeurs (2,50 à 3 m), donc **un peu trop grand pour le robot**, comme l'atelier de l'île 1 : marches un peu hautes, portes d'environ 3 m, table à hauteur de poitrine.
- **Marée** : l'eau est à −0,6 m à marée basse et à +0,5 m à marée haute. Tout ce qui est à 0 m (chaussée, gué, estran, flaque, épave) n'existe qu'à marée basse.
- **Palette** : roche claire à facettes, pierre ivoire, terre cuite délavée, cuivre patiné bleu ardoise et lentille ambrée. Varech, eau verte des flaques, brume froide.
- **Silhouette du Phare (direction V2 retenue le 2026-11-19)** : tour à pans coupés. Le socle se prolonge en parvis et porte l'aile vitrée d'Iris, avec son toit bas et sa lucarne. Deux grandes nervures montent du socle jusqu'à la couronne ; une troisième la soutient à l'arrière. La couronne ajourée laisse lire la lentille depuis le port. Référence : `concept/phare_ile_02_v2/phare_ile_02_ensemble.png`.
- **Style du terrain (validé le 2026-11-19)** : « blocs taillés à facettes, strates nettes » : falaises en strates de blocs qui avancent / reculent, fissures, escaliers creusés dans des encoches, éboulis et varech au pied, herbe rase + lichen doré dessus. Plus de damier de plateaux. Généré par `tools/blender/terrain_ile_02.py` depuis la carte du nœud Maquette → `assets/models/ile02/terrain_ile_02.glb` (branché par `terrain_modele` dans `scripts/maquette.gd`). Test d'origine : `concept/ile_02_falaise_test_v1.png`.
- **Image cible d'ambiance (2026-11-19)** : `concept/ile_02_cible_v1.png` (Meshy, depuis la variante « croix »). Elle sert de référence pour **l'ambiance** (lumière dorée, brume en nappes, phare vieilli, détails) ; **pas** pour la forme (le port y est collé au rocher, la chaussée trop courte) : la forme reste celle du plan.

### Les zones
| # | Zone | Ce qu'on y trouve |
|---|---|---|
| 1 | **Le ponton** | L'arrivée en barque, accessible à toute marée. |
| 2 | **La bouée-lanterne** | Dans la passe, à rallumer depuis la barque. Point de recharge. |
| 3 | **La maison du quai** | Le logement des gardiens de passage : lits géants, cirés, une lanterne. Intérieur détaillé (décidé le 2026-11-19, voir ci-dessous). |
| 4 | **Le hangar** | Des barques retournées, le **miroir d'essai** et sa porte. |
| 5 | **L'échelle de marée** | Des repères peints sur le mur du quai. |
| 6–8 | **La chaussée et ses balises** | Un chemin de dalles posé sur l'eau, couvert de brume épaisse. Trois balises. |
| 9 | **L'ancien corps couvert d'algues** | À mi-chaussée : il est parti trop tard. |
| 10 | **L'entrée des grottes** | Sur une petite plage d'estran, au pied du rocher. |
| 11 | **La crypte des Semeurs** | Au fond des grottes, sous le phare : le **câble du berceau**. |
| 12 | **Le banc d'Iris** | Au bord du rocher, tourné vers le nord-ouest (vers sa maison, qu'on ne voit pas). |
| 13 | **Le jardin mort** | Des bacs de terre sèche, un arrosoir, un **arbre rose mort**. |
| 14 | **Le Cap Est** | Facile d'accès. Lanterne + station de miroir. |
| 15 | **La flaque du Cap Est** | À marée basse : une **pierre-soleil** au fond. |
| 16 | **Le Cap Ouest** | Au bout d'un sentier de falaise noyé de brume. Station de miroir. |
| 17 | **Le Cap du Large** | Au nord, au bout du gué. Station de miroir. |
| 18 | **L'ancien corps échoué** | Sur les rochers du Large : il s'est fait prendre par la marée. |
| 19 | **L'épave du ravitailleur** | Au sud-ouest, couchée sur un banc de sable. Entourée de brume épaisse. |

### La maison du quai (décidé le 2026-11-19)
Une halte de gardiens, rangée puis abandonnée, à l'échelle des Semeurs (portes ~3 m, plafond haut). Le toit s'efface quand le robot entre (comme l'abri de l'île 1). Fabrication : structure et intérieur dans Blender, meubles « héros » par Meshy.
- **Le décor** : un grand poêle en fonte froid (la bouilloire dessus), deux lits géants superposés aux couvertures pliées, des cirés jaunes et des bottes immenses près de la porte, une table et des tasses, une carte marine au mur, une grande fenêtre tournée vers la chaussée et le Phare.
- **La façade** porte le médaillon bleu émaillé des gardiens sur le pignon sud. Un auvent abrite le seuil à l’est. Le poêle, les cirés et les bottes sont sculptés avec Meshy puis mis à l’échelle et colorés dans Blender.
- **La lanterne** de la maison : à rallumer avec le câble ; c'est le point de recharge avant la traversée (G1).
- **Le cahier des passages** sur la table : les traversées notées par les gardiens (« Parti au début de la basse mer, arrivé sec »…), la dernière ligne inachevée (l'ancien corps de la chaussée). Indice muet du piège de G1 : partir au **début** de la basse mer.
- **L'horloge de marée** au mur : une aiguille qui suit la vraie marée du jeu (HorlogeMonde).
- **La couchette d'Aube** : une troisième couchette, à taille d'enfant, un dessin d’Aube dépasse de l’oreiller. Avec E, on voit Iris et Aube à la fenêtre du quai, face à la marée montante. Le carnet en garde une copie. Le dessin fait écho au jour 22 du cahier des passages.

### Le chantier du quai

Hangar de réparation à l’échelle des Semeurs, en bardage bleu sur un socle de calcaire. Deux vantaux coulissent sur un rail visible. L’atelier conserve une allée de manutention sur rails, une coque retournée sur tréteaux, une barque en cours de réparation et un établi avec son étau, ses outils, du cordage et de la toile. La charpente, les ardoises et le haut des murs passent en coupe pendant la visite.

Une plaque de service sur le ponton montre une fiche et une bouée. La bouée suit la marée et le quai porte des traits peints aux niveaux de basse et haute mer. Depuis la barque, on approche par le côté quai. L’invite « E · Brancher la bouée » indique le premier geste. E arrête la barque et déplace la fiche de la proue vers la prise. Au premier allumage, la caméra suit le rayon de la bouée jusqu’au miroir. La lumière renvoyée forme une tache sur le bardage à côté de la cellule. Au miroir, « E · Tourner le miroir » fait avancer la tache par crans. Quand le rayon atteint la cellule, le voyant s’allume et les deux vantaux coulissent pendant un court plan. L’ouverture se conserve. La bouée reste allumée et sert aussi de point de recharge.

### Le Phare, de bas en haut
| Niveau | Ce qu'on y trouve |
|---|---|
| **Rez** | **La salle des machines** : engrenages arrêtés, la chaîne de la lentille, le **schéma des engrenages** peint au mur. Des dalles mènent, entre l'établi et le bâti de chaîne, au pied du colimaçon qui longe le mur est. |
| **1er** | **Le bureau d'Iris** : sa table, ses relevés, la **table des marées**, la **page 1**, le **plan des miroirs**, la note de la clé, la ligne de la pleine lune. La porte fermée de **sa chambre** est dans le pan nord-est, côté aile, avec le dessin d'Aube punaisé dessus. La chambre occupe l'aile et se rejoint par le toit. |
| **2e** | **La salle des cartes**, fermée à clé, au centre de la tour ; sa porte marquée est face à l'arrivée de l'escalier, qui continue autour d'elle jusqu'à la galerie. À l'intérieur, le registre et les relèvements. |
| **Sommet** | La **grande lentille** en ruche (anneaux de prismes ambrés, deux œils de Fresnel sur l'axe du faisceau), intacte, sans lampe, sur une couronne graduée. La **galerie extérieure**, avec **la lunette d'Iris** **[à valider]** et l'**ancien corps de la galerie**. |

**L'escalier (refait le 2026-11-23 pour la 1re personne)** : un colimaçon de pierre contre le mur de la tour, en trois volées dans le sens horaire (rez → bureau → salle des cartes → galerie). Chaque étage a un vrai plancher qui sert de plafond à l'étage du dessous, percé d'une trémie bordée d'un garde-corps au-dessus de la volée. Sous la partie basse des volées, la maçonnerie descend jusqu'au sol. L'aile n'a plus d'escalier. Script : `tools/blender/escalier_phare.py`.

En vue de dessus, la coupe dégage le niveau visité et les marches qui y mènent. À l’extérieur, le Phare devient translucide s’il masque le robot. En entrant dans la salle des cartes, la volée vers la galerie s’efface pour dégager le registre et les relèvements. L'échelle et l'aile d'Iris apparaissent depuis la galerie et le toit. Dans la chambre, la coupe montre le mobilier et les documents de la pièce.

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
- **Le mécanisme** : le robot branche la seule lanterne du circuit, au cap Est. Son rayon frappe la vitre du premier miroir. Le robot pivote les trois miroirs par crans (`E`) pour réfléchir le même rayon jusqu'à la lentille. Un miroir qui ne reçoit pas le rayon reste sombre.
- **Station de miroir** : bâti fixe en pierre ivoire, tête pivotante à cadre de cuivre patiné, manivelle et contrepoids apparents. La manivelle est à portée du robot et la tête pivote par crans au-dessus du bâti. Le cap Est sert de premier montage.
- **Les contraintes** : la batterie, la marée (le gué), l'orientation, la brume du sentier Ouest.
- **Ce que ça ouvre** (un grand moment, lent) : la lumière fait le tour du rocher et monte dans la lentille ; **le faisceau** s'allume et tourne ; **le carnet dessine la carte de l'archipel** ; le faisceau perce la brume du large autour de l'épave.

### G3. « La clé de la salle des cartes » (une chaîne sur l'île) — *validé*
- **La situation** : la salle des cartes est fermée à clé.
- **Où on l'apprend** : la note du bureau (« J'ai laissé la clé dans la cabine, à bord du ravitailleur ») ; depuis la galerie, on **voit l'épave**.
- **La chaîne** : le **Phare rallumé** (son faisceau perce la brume de l'épave) + la **marée basse** (l'épave affleure) + **la barque** ; la clé est dans la cabine du capitaine.
- **À bord du ravitailleur** : on amarre la barque à une passerelle fixée au flanc éventré. Le pont reste ouvert jusqu’à la cabine. Le toit et la poupe s’effacent en coupe à l’entrée. La clé est posée sur le bureau, à côté du journal de quart, en face de la couchette. Le journal est consultable et se copie dans le carnet : « Iris est repassée pour les relèvements. Elle a laissé la clé sur le bureau. Je la lui rendrai à la prochaine basse mer. »
- **Ce que ça ouvre** : la salle des cartes, avec le **registre** et les **relèvements**.

### G4. « La salle des machines » (mécanisme) — *validé*
- **La situation** : une fois le Phare rallumé, la lentille tourne, mais la couronne graduée est **bloquée** : on ne peut pas la viser.
- **Où on l'apprend** : au rez, les engrenages sont démontés, et un **schéma** peint au mur (en partie couvert de suie) montre comment ils s'emboîtent.
- **La solution** : remettre les engrenages en place (`E` pour déplacer et tourner chaque roue) en suivant le schéma. La partie effacée se devine en regardant **les marques d'usure au sol** sous chaque axe (observation).
- **Dans la salle** : `E` devant la machine ouvre une grande vue de face. Le joueur choisit une roue dans le râtelier, puis un axe libre. Les commandes permettent de tourner la roue d’un cran ou de la retirer. La taille doit correspondre à l’empreinte et le repère en laiton doit rejoindre la clavette. Le chariot applique les déplacements dans la salle. Le dernier cran ferme la vue, tend la chaîne et libère la manivelle de la galerie.
- **La commande** (décidé le 2026-11-25) : un **pupitre en laiton** sur la galerie, à l'écart de l'arrivée de l'escalier. Socle de pierre ivoire, plateau incliné avec un cadran gradué dont l'aiguille suit la lentille, un compteur qui affiche le cap, et un volant à poignée de bois en façade. Pas de texte flottant : la touche E vient du guidage commun.
- **Ce que ça ouvre** : la **lentille orientable**. Sur les trois côtés accessibles de la galerie, l’invite « E · Orienter la lentille » permet de tourner la manivelle depuis sa position. Auprès de la lunette d’Iris, l’instrument le plus proche prend la touche E. Avec les relèvements (G3), on peut la pointer vers chaque île.

### G5. « La chambre d'Iris » (lieux cachés) — *validé*
- **La situation** : à l'extrémité du palier du bureau, une porte fermée de l'intérieur.
- **Où on l'apprend** :
  - un **dessin d'Aube** (le même style que ceux de la Colonie) est punaisé au-dessus de la porte : « Pour Iris. Ma cachette, c'est par le toit » ;
  - depuis la galerie, on voit une **lucarne** ouverte sur le toit du 1er étage.
- **La solution** : sortir sur la galerie, saisir l'échelle de service avec `E` et descendre barreau par barreau jusqu'à la passerelle du toit. Elle mène à la lucarne de l'aile. Le robot est **assez petit pour y passer**, comme Aube. Il peut remonter par l'échelle avec le même geste.
- **Ce que ça ouvre** : **la chambre d'Iris** (§7) : sa vie à elle, plus seulement ses relevés.

### G6. « La lunette d'Iris » (observation) — *validé*
- **La situation** : sur la galerie, une **lunette** sur pied. Son socle a **des crans gravés**, avec un nom à chaque cran.
- **Ce qu'on voit** : chaque cran cadre un lieu lointain, en gros plan : le quai de la Colonie (des caisses de départ empilées), la ville haute couverte de lanternes, la Nef échouée au loin, la brume blanche de l'île blanche…
- **Le cran sans nom** : il cadre **la mer vide**, au nord-ouest. Il n'y a rien, juste de l'eau. C'est la direction du banc d'Iris, celle de la **ligne sans nom du registre**, et celle où l'on verra l'île cachée à la pleine lune.
- **Ce que ça donne** : des croquis de lieux lointains dans le carnet (sans flèche), et un **mystère** (pourquoi regarder la mer vide ?).
- **Maquette jouable** : E sur la galerie, flèches pour tourner. Les cinq vues sont des illustrations en attendant les décors de l’archipel. Le cran gravé d’une maison reprend le cap 318° de la commande du Phare. Le quai et la ville haute partagent la direction de la Colonie avec deux cadrages rapprochés.

### Les petites
- **Le miroir du port** : un miroir d'essai renvoie la lumière de la bouée sur la porte du hangar, qui s'ouvre. C'est le tutoriel muet des miroirs. **Précisé le 2026-11-22** (on ne comprenait pas le hangar) : le premier allumage est filmé lentement, du rayon qui touche le capteur à la porte qui glisse, puis la caméra regarde l'établi. Sur l'établi, la **fiche d'atelier des miroirs** (affiche dessinée `tools/affiches/fiche_miroirs.html`) explique le principe en quatre vignettes, bouée → miroir à crans → voyant du capteur → porte, sans donner l'ordre des caps (texte provisoire, à valider).
- **La bouée du port** : la rallumer (depuis la barque) donne un point de recharge.
- **Le raccourci des grottes** : quand la mer découvre le seuil, le robot amarre la barque à la borne de l'estran et gagne la galerie à pied. La galerie et la crypte restent abritées de la marée. Une échelle de service dans un puits rejoint le plateau au pied du Phare dans les deux sens. Si la mer remonte pendant la visite, le robot peut donc repartir par le plateau.

---

## 6. Les secrets
| Secret | Où | Ce qu'il raconte |
|---|---|---|
| **La crypte et le câble du berceau** | Au fond des grottes (marée basse) | Un gros câble tiède sort de la roche et plonge vers le large, vers **la Centrale**. Une plaque : **« Ligne du berceau. Prioritaire. Ne jamais couper. »** C'est la ligne qui a survécu à la grande nuit (et celle qu'on coupera à la fin). |
| **L'ancien corps de la galerie** | Au sommet | Assis face à la mer : le robot est déjà venu ici, il y a très longtemps. |
| **L'Écoute** | Près de la bouée, à batterie basse | Une créature sans yeux (bestiaire). |
| **Le banc d'Iris** | Au bord du rocher | On s'y assoit : la caméra montre ce qu'elle regardait, le nord-ouest et la mer vide. |
| **La pierre-soleil** | La flaque du Cap Est, à marée basse | Une recharge sûre pour G2. |
| **L'arbre rose mort** | Le jardin mort | Iris en avait un ici. Elle l'a laissé mourir. Seul le sens change après la Colonie (les arbres roses viennent de chez eux). |

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
> Pour les nouveaux, puisque personne ne lit les consignes : la lanterne du cap Est donne toute la lumière. Le premier miroir l'envoie vers le Large. Si une glace dévie, le rayon se perd avant d'atteindre le Phare.
> J'ai nettoyé les vitres du Cap Est. Le miroir du Large a encore bougé avec la tempête. N'allez jamais au Large à marée montante : la mer ne prévient pas.
> Rappel : on ne reprend pas la lumière devant les arbres roses. Ils ne le supportent pas.
> — G.

*Cette version est placée sur la table d'Iris dans `scenes/ile02/phare.tscn`.*

### Les notes du bureau
- **Décor du bureau** : table en frêne miel, siège de veille à dossier en côtes de bois et coussin lavande, ciré ocre sur son porte-manteau, banquette, meuble à cartes roulées et étagère de dossiers. Sur la table, lampe articulée, tasse bleue, presse-papiers ambré et carnets. Références approuvées dans `concept/bureau_iris_decoration/`.
- **La note de la clé** (validée) : « J'ai laissé la clé de la salle des cartes dans la cabine, à bord du ravitailleur. Je la reprendrai à la prochaine basse mer. Pas sans le Phare : la brume du large y est trop épaisse. »
- **La ligne de la pleine lune** (dans la marge d'un relevé, d'une autre encre) : « Les nuits de pleine lune, le Phare chante, et je vois ma maison. »
- **La table des marées** (validée pour les six tours) : un dessin de l'échelle du quai, avec « basse » et « haute », et dessous : « Basse mer : six tours du faisceau. Pas un de plus. » (validé) Plus bas, un troisième trait : « Pleine lune : plus bas que tout. Le vieux port respire. » (C'est un indice pour le vieux port de la Colonie.)
- **Le plan des miroirs** : les trois caps et le Phare vus de dessus ; une partie effacée par l'eau (on voit la flèche Est → Large, le reste est illisible).

### La chambre d'Iris (G5)
- Un lit à sa taille, une seule tasse, une lanterne **éteinte et débranchée** sur la table de nuit.
- Au mur, **le dessin d'Aube** : des silhouettes de brume qui dansent autour d'une grande et d'une petite Semeuse. « Pour Iris. Nos amis du noir. » (validé le 2026-11-16)
- Une lettre jamais envoyée, à Ysolde (**validée le 2026-11-16**, version mystérieuse) :
> Ysolde,
> Tu me demandes encore des lanternes pour l'île blanche. Je ne les poserai pas.
> J'ai vu ce qu'elles font là-bas. Demande à Saule ce qu'elle a vu, elle.
> Éteins une seule nuit, avec moi. Une seule. Tu verras ce que je vois.
> — Iris

*(Un doute, pas une explication : la vérité « les lanternes tuaient » reste pour la Quarantaine. Le nom de Saule y mène. Le prénom « Iris » est connu pendant l'enquête : validé.)*

### La salle des cartes (G3)
- **Le registre des lanternes** : un grand livre, une page par île, avec le nombre de lanternes année après année. Les lignes (validées le 2026-11-16) :
  - « Réveil : l'abri, la veilleuse, le sommet. Rien à signaler. Le jardinier dort. »
  - « Colonie : 40… 90… 160… 310. » *(les chiffres explosent d'année en année)*
  - « Île blanche : on m'en demande encore. Ils disent que c'est pour soigner. Je n'y crois plus. »
  - « Nef : aucune, en attendant le départ. »
  - « Centrale : ne pas toucher. Tavin s'en occupe. »
  - **Une ligne sans nom**, avec seulement le dessin d'une petite maison, et aucune lanterne *(validé : comprise plus tard)*.
- **Les relèvements** : sur le mur, une rose des vents note Colonie 129°, Île blanche 058°, Nef 009° et Centrale 287°. Ils se recopient dans le carnet et se lisent sur la graduation de la commande de la galerie.

### Ce qui s'inscrit dans le carnet (juste ce qu'on a vu, sans flèches)
- **Carte** de l'île 2, puis **la carte de l'archipel** (G2).
- **Lieux** : le port, la chaussée, le phare (4 niveaux), les trois caps, l'épave, la crypte.
- **Textes** : la page 1, les notes du bureau, la lettre à Ysolde, le registre, la plaque du câble, ce qu'on a vu dans la lunette.
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
- **La pleine lune et l'île cachée** : « Les nuits de pleine lune, le Phare chante, et je vois ma maison. » À la pleine lune, la lentille pointée **au cran sans nom** et **éteinte** (le Phare « dort ») concentre le clair de lune et **montre l'île cachée**. C'est la seule chose impossible à la première visite.
  - **La clé de lecture (décidé le 2026-11-16)** : une **lettre d'Iris à Saule**, à la Quarantaine : « Le Phare ne chante que quand il dort. Une nuit de grosse lune, laisse-le dormir, tourné vers rien, et tu verras où je suis. »
  - **Le bonus des observateurs** : une nuit de pleine lune, si la lentille est éteinte (quelle que soit son orientation), un **reflet argenté** court sur la mer depuis le Phare. On le voit sans le comprendre.
  - *Comment on fait, dans une même boucle* : rallumer le Phare (G2), réparer les engrenages (G4), tourner la lentille au cran sans nom, puis **reprendre la lumière de la lanterne du cap Est** : la lentille s'éteint mais garde son orientation.
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

**Ordre de production décidé le 2026-11-19** : terminer les bâtiments, les décors et les accessoires de l'île avant la passe de raccordement des interactions. Les nouveaux décors sont préparés à l'échelle du jeu dans Blender.

**Grottes et crypte** : la maquette de l'île instancie les quatre modules de `scenes/ile02/grottes_crypte.tscn` à côté de l'escalier de l'estran. L'entrée maçonnée s'appuie sur le calcaire. Les fanaux balisent la galerie dallée. Dans la crypte, une bride étanche fixe la ligne du berceau à la roche. Le câble plonge vers le large sous une grille de visite, près du treuil et de la plaque lettrée. Le robot peut lire la plaque avec E et retrouver son texte dans le carnet. La couverture de la falaise s'efface quand le robot entre et les collisions du plateau restent actives autour du puits.

**Chaussée et anciens corps** : des dalles de calcaire chanfreinées et une pente raccordent le quai à l'estran. Les trois balises ont chacune un cercle de pierres. À mi-chaussée, le robot effondré repose sur le côté, avec du varech accroché au poignet, à la coque et aux pieds. Au Large, le corps est tourné vers le chemin du retour, une main au rocher et du varech accroché à la coque. Sur la galerie, un autre corps reprend la pose assise du robot jardinier et regarde la mer au cap 318°, comme depuis le banc d’Iris. Les trois corps racontent leur histoire par la pose et le lieu.

**Jardin et banc d’Iris** : le jardin occupe le rebord nord-ouest du plateau, entre le Phare et le départ vers le cap Ouest. Trois bacs de bois contiennent de la terre craquelée. L’arrosoir en cuivre verdi est resté auprès de l’arbre rose mort, aux racines apparentes. Depuis le sentier devant le banc, E fait asseoir le robot. La caméra se pose au cap 318°, comme le cran sans nom de la lunette. La première transition prend plus de temps. E ou Échap rend la marche au robot.
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

**Validé le 2026-11-16**
- **La clé de lecture de la pleine lune** : la lentille doit être éteinte ; l'indice est une lettre d'Iris à Saule, à la Quarantaine, plus le reflet argenté au Phare (§9).
- Le câble de la crypte est **la ligne du berceau**, avec sa plaque (« Ligne du berceau. Prioritaire. Ne jamais couper. »).
- L'**arbre rose mort** dans le jardin d'Iris.
- Les textes : la lettre d'Iris à Ysolde (version mystérieuse), le registre, la table des marées, la note de la clé, la légende du dessin d'Aube (« Pour Iris. Nos amis du noir. »).

**Plus rien à valider** sur le côté lumière de l'île 2 (le côté ombre reste reporté).
