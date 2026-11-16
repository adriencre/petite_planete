# Île 4 — La Quarantaine (l'île blanche)

> Document de l'île, rempli au fil des décisions (commencé le 2026-11-16). À lire avec `ENQUETE.md` et `DESIGN.md`.
> Seul ce qui est écrit ici est décidé.

---

## 1. En une phrase
L'hôpital de Saule, la Médecin, perdu dans la brume la plus épaisse de l'archipel : les malades y sont morts dans leurs lits, sous les lanternes qui devaient les soigner.

## 2. Sa place dans le jeu
- **Le fil principal** : la maladie et les lanternes.
- **Ce qu'on y comprend : juste un doute** (décidé le 2026-11-16). On voit que les lanternes n'ont pas soigné les malades. Le pourquoi (le peuple de la brume affamé) et la grande nuit se comprennent plus tard (Nef, Centrale).
- **L'un des chocs du jeu** : les premiers squelettes, dans les lits.
- **Ce que les autres îles en disent** :
  - Phare : « Île blanche : on m'en demande encore… Je n'y crois plus. » ; « Demande à Saule ce qu'elle a vu, elle. »
  - Colonie : « Les malades seront envoyés à l'île blanche jusqu'à guérison. » ; « Tous à la Nef. Sauf : malades de l'île blanche. »
  - Tavin : « Chaque lanterne que nous ajoutons, la brume semble la sentir. Elle s'épaissit autour. »
- **Accès** : la brume très épaisse en mer (lanterne de la barque bien remplie, ou le faisceau du Phare orienté vers l'île).
- **Pas de marée** sur cette île (décidé le 2026-11-16).
- **Durée** : environ 1 h 30.

## 2b. Forme v6 (décidée le 2026-11-16) : **cour d'hôpital**
Un **anneau de bâtiments surélevé** (niveau 2) autour d'une **cour creuse** (niveau 1) noyée de brume : la salle des lits. Une seule entrée dans l'anneau, côté ponton (sud). Le pavillon de Saule et la salle noire sont dans l'anneau, à l'ouest ; le cimetière est dehors, à l'est ; le sémaphore se dresse sur un rocher au nord (niveau 3). Palette blanc et lavande.
Schéma : `concept/ile_04_formes.png` (variante B), dessiné par `tools/carte_iso.py ile_04`.

## 3. Les lieux (décidé le 2026-11-16)
| Lieu | Ce qu'on y trouve |
|---|---|
| **La salle des lits** | Des draps suspendus dans la brume, les lits des malades sous des lanternes, **un squelette dans chaque lit**, couvert de mousse et de fleurs (au début, on peut les prendre pour des racines). |
| **Le pavillon de Saule** | Son bureau, son journal médical, les fiches des malades. **Le squelette de Saule**, assise à son bureau, la plume à la main : elle est restée avec ceux qui ne pouvaient pas partir et a écrit jusqu'au bout. |
| **La salle noire** | Peinte en noir, sans lanterne, **un seul lit, vide**, sans squelette. Une **note de Saule, mystérieuse** (texte à écrire). On ne sait pas pourquoi le lit est vide. |
| **Le cimetière** | Des stèles, toutes à terre, rangées de la plus ancienne à la plus récente le long du chemin. Sur chacune, **deux rangées de gravures, sans chiffres ni explication** : des **petites lanternes** (celles qui veillaient le malade) et des **encoches** (le temps de sa maladie). Les plus anciennes : une lanterne, une longue rangée d'encoches. Les plus récentes : beaucoup de lanternes, presque pas d'encoches. **Plus le malade est récent, plus il y avait de lanternes, et plus il est mort vite.** Rien ne le dit : on le remarque, ou pas. |
| **Le sémaphore** | Une tour avec 3 grandes lampes, pour envoyer des signaux lumineux à la Nef. On y monte sans énigme. Le **carnet des signaux** de Saule : son dernier message, « Gardez-nous une place », n'a jamais eu de réponse. **Son motif de lampes sert de code à la porte du poste de pilotage de la Nef** : gauche, droite, milieu, droite (décidé le 2026-11-16). |
| **L'ancien corps** | Perdu au milieu de la salle des lits, loin de toute sortie, avec la même écharpe. On peut mourir là si on ne suit pas les cordes. |

## 4. Le récit et les textes
- **La note de la salle noire** (décidée le 2026-11-16), posée près du lit vide :
  > Lit 12.
  > Jour 9 : il ~~~~~~~~ *(barré, plusieurs fois)*
  > Il survit ?
  > Je n'ose pas l'écrire.
- **Le journal médical de Saule** (sur son bureau, décidé le 2026-11-16) :
  > Ils arrivent pâles et froids, comme des lampes qu'on aurait oublié de remonter.
  > Je leur donne de la lumière.
  > Ils vont mieux. Puis plus mal.
  > J'ajoute des lanternes.
  > Ysolde m'en envoie encore. Je ne les déballe plus.
  > Ce soir, ils partent tous à la Nef.
  > Moi, je reste avec ceux qui ne peuvent pas marcher.
- **La lettre d'Iris à Saule** (la clé de la pleine lune) est **dans la main de Saule** : elle l'a relue la dernière nuit (décidée le 2026-11-16).
  > Saule,
  > Si un jour tu doutes, viens chez moi.
  > Ma maison n'a pas de lanterne, alors personne ne la voit.
  > Le Phare ne chante que quand il dort.
  > Une nuit de grosse lune, laisse-le dormir, tourné vers rien, et tu verras où je suis.
  > — Iris

## 5. Les énigmes (décidé le 2026-11-16 : Q1, Q2, Q3)

### Q1. Les cordes de Saule (lieu caché + batterie)
- **La situation** : la salle des lits est pleine de draps suspendus, dans une brume qui vide la batterie très vite. On s'y perd, on y meurt.
- **L'indice** : au ponton, un panneau de Saule : « Pour les malades qui ne voient plus. Un nœud : les lits. Deux nœuds : mon bureau. Trois nœuds : le cimetière. » Des cordes à nœuds sont tendues entre les poteaux.
- **La solution** : suivre la corde à deux nœuds pour traverser la brume.
- **Ce que ça ouvre** : le pavillon de Saule (et, par la corde à trois nœuds, le cimetière).

### Q2. Le lit qui manque (observation)
- **La situation** : au pavillon, les fiches des malades vont du lit 1 au lit 12. Dans la salle des lits, on n'en compte que **11** (numéros peints sur les lits ; le 12 n'y est pas).
- **La solution** : chercher le lit 12. Derrière un rideau du pavillon, une porte qu'on n'avait pas remarquée.
- **Ce que ça ouvre** : le chemin vers la salle noire.

### Q3. La double porte de la salle noire (mécanisme de lumière)
- **La situation** : un petit couloir fermé par deux portes, une lanterne au milieu. Une plaque : « Ne rien laisser entrer de clair. »
- **Le mécanisme** : la 1re porte ne s'ouvre que si la lanterne du couloir est **allumée** ; la 2e seulement si le couloir est **noir**.
- **La solution** : allumer la lanterne, entrer, **reprendre sa lumière** depuis l'intérieur : le couloir devient noir, la 2e porte s'ouvre.
- **Ce que ça ouvre** : la salle noire, son lit vide et la note mystérieuse.

*Q2 et Q3 s'enchaînent : on trouve le lit qui manque, puis on ouvre la double porte.*

## 6. Points ouverts
1. Le côté nuit : rien pour l'instant (reporté, comme pour les autres îles).
