# Île 5 — La Nef

> Document de l'île, rempli au fil des décisions (commencé le 2026-11-16). À lire avec `ENQUETE.md` et `DESIGN.md`.
> Seul ce qui est écrit ici est décidé.

---

## 1. En une phrase
Le vaisseau des Semeurs, échoué depuis leur arrivée : la nuit du départ, tout le monde était à bord, prêt à partir… et la Nef s'est éteinte.

## 2. Sa place dans le jeu
- **Le fil principal** : la Nef et l'appel au secours.
- **Le grand choc** : beaucoup de squelettes. La fausse piste « ils sont partis » s'effondre.
- **Accès** : libre, mais l'intérieur est fermé par des codes trouvés ailleurs (la comptine de la Colonie, le motif du sémaphore de la Quarantaine).
- **Palette** (DA v5) : rouille + corail, métal patiné, l'antenne.
- **Durée** : environ 2 h.

## 3. Ce qui s'est passé ici (décidé le 2026-11-16)
- **Pourquoi la Nef n'est jamais partie** : pour décoller, elle devait être chargée à fond par la Centrale, poussée au maximum cette nuit-là. Cela aurait tué tout le peuple de la brume. **C'est pour ça qu'Iris a coupé la Centrale cette nuit précise.** La Nef s'est éteinte au moment de partir, et tous ceux qui étaient à bord sont morts.
  - *Sur la Nef, on voit seulement qu'elle s'est éteinte au moment du départ. Le pourquoi se comprend à la Centrale.*
- **L'appel au secours d'Orme** : envoyé des centaines de fois vers leur planète d'origine (la grosse planète du ciel), jour après jour. **Jamais de réponse.** Le mystère reste entier : la planète est-elle vide ?
- **Ysolde et Orme** : ensemble au poste de pilotage. Orme à ses commandes, Ysolde debout derrière lui, prêts au départ.
- **Aube** : elle n'a jamais embarqué. Elle n'est **pas à la Nef** : on la trouve **au coin noir de la Colonie**, assise, en train de dire au revoir à ses amis (voir `ILE_03_COLONIE.md` §6). À la Nef, **son père** est dans la file de la passerelle, avec à côté de lui une **petite valise d'enfant** sans propriétaire : il l'attendait.
- **La grosse planète** : juste un mystère. Le journal d'Orme montre des centaines d'appels vers elle, jamais de réponse ; on ne saura jamais pourquoi.
- **Le malade du lit 12** (Quarantaine) : on ne le retrouve pas ici. Le lit vide reste une question ouverte (Iris ou le peuple de la brume pourront y répondre plus tard).
- **Ce qu'on comprend ici** : ils sont **tous morts la même nuit, d'un coup**, au moment où la Nef s'est éteinte. Pas encore pourquoi (ça, c'est la Centrale).

## 3b. Forme v6 (décidée le 2026-11-16) : **encastrée dans la falaise**
Le **nez de la Nef est planté dans un grand plateau** (poste de pilotage tout en haut, niveau 4) ; la coque descend en pente vers le sud jusqu'à la mer. **La passerelle** part du niveau du sol, à mi-pente ; **l'antenne** se dresse sur le milieu de la coque (salle de l'appel à son pied) ; **la soute** est dans la queue, au niveau de la mer, entourée d'estran, avec **la brèche** (marée basse). On progresse en montant le long du vaisseau, de la soute noyée à la révélation du poste de pilotage.
Schéma : `concept/ile_05_formes.png` (variante B), dessiné par `tools/carte_iso.py ile_05`.

## 4. Les lieux (décidé le 2026-11-16)
| Lieu | Ce qu'on y trouve |
|---|---|
| **La passerelle** | La rampe d'embarquement : une longue file de squelettes avec leurs valises « Nef ». Le premier choc, dès l'arrivée. |
| **Le poste de pilotage** | Orme à ses commandes, Ysolde debout derrière lui. Le journal de bord. |
| **La salle de l'appel** | Au pied de l'antenne : la machine de l'appel au secours et le journal d'Orme (des centaines d'envois, jamais de réponse). |
| **La soute des graines** | Les graines et pousses emportées de chez eux (les arbres roses), prêtes pour le voyage. Dans la partie basse de la coque. |

- **Marée** : oui. La coque échouée et penchée se remplit d'eau à marée haute ; les parties basses (la soute) ne sont accessibles qu'à marée basse, par la brèche.

## 5. Les énigmes (décidé le 2026-11-16 : N1, N2, N3, N4)

### N1. La porte de la comptine (code de la Colonie)
- **La situation** : en haut de la passerelle, la grande porte du vaisseau est fermée. Devant elle, 4 lanternes aux verres de couleur : rose, bleu, or, et un verre **noir**.
- **L'indice** : la comptine de l'école de la Colonie (« rose au matin, bleu à midi, couleur d'or le soir, et noir quand on dort »).
- **La solution** : allumer dans cet ordre. La lanterne au verre noir ne se voit pas allumée : on croit qu'elle est cassée, on entend juste un petit clic.
- **Ce que ça ouvre** : l'intérieur de la Nef.

### N2. La porte des signaux (code de la Quarantaine)
- **La situation** : le poste de pilotage est fermé par une porte à 3 lampes (gauche, milieu, droite), les mêmes qu'au sémaphore.
- **L'indice** : le dernier message de Saule au sémaphore (« Gardez-nous une place »), resté sans réponse. **Le motif (décidé le 2026-11-16)** : gauche, droite, milieu, droite.
  ```
  1. gauche   ● ○ ○
  2. droite   ○ ○ ●
  3. milieu   ○ ● ○
  4. droite   ○ ○ ●
  ```
- **La solution** : rejouer son motif sur les 3 lampes. La Nef reçoit enfin le message, des siècles trop tard.
- **Ce que ça ouvre** : le poste de pilotage (Orme, Ysolde, le journal de bord, la boîte noire).

### N3. La soute à marée basse (temps)
- **La situation** : la soute des graines est au fond de la coque, sous l'eau à marée haute.
- **L'indice** : la coque penchée, l'eau qui entre et sort par la brèche ; un **ancien corps du robot** noyé dans un couloir de la soute, parti trop tard.
- **La solution** : entrer par la brèche à marée basse, trouver la soute dans les couloirs penchés, ressortir avant que l'eau remonte.
- **Ce que ça ouvre** : la soute des graines, les pousses d'arbres roses prêtes pour le voyage.

### N4. La boîte noire (mécanisme + batterie)
- **La situation** : au poste de pilotage, une machine qui enregistrait tout en lumière, éteinte depuis la grande nuit, avec une **prise**.
- **La solution** : y brancher le câble du robot. Cela coûte **beaucoup de batterie** : il faut arriver jusqu'ici avec assez de charge (préparer son trajet).
- **Ce que ça ouvre** : **un souvenir rejoué en lumière**, les dernières minutes de la Nef : tout le monde embarque, la Nef se charge, la jauge monte presque au maximum… puis **tout s'éteint d'un coup**. La grande révélation de l'île : ils sont tous morts la même nuit, en même temps.

*L'antenne d'Orme n'a pas d'énigme : la salle de l'appel est un lieu, avec le journal d'Orme.*

## 6. Les textes (décidés le 2026-11-16)

### Le journal d'Orme (salle de l'appel)
> Appel 1. Pas de réponse.
> Appel 2. Pas de réponse.
> Appel 3. Pas de réponse.
> … *(des pages entières)* …
> Appel 611. Pas de réponse.
> Appel 612. Pas de réponse.
> Ce soir, on part. On ira les chercher nous-mêmes.
> — Orme

### Le journal de bord (poste de pilotage)
> Nuit du départ.
> Tous à bord, sauf l'île blanche et l'équipe de Tavin.
> Charge : 70 %. Tavin pousse la Centrale.
> Charge : 85 %.
> Charge : 96 %.
> Charge : 9
> *(la ligne s'arrête)*

*(« Tavin pousse la Centrale » : Tavin et son équipe étaient à la Centrale cette nuit-là. La boîte noire (N4) montre la même chose en lumière.)*

## 7. Points ouverts
- Le côté nuit : reporté, comme pour les autres îles.
