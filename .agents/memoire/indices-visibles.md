---
name: indices-visibles
description: Les indices d'une énigme doivent se trouver sans connaître le jeu — appel fort (halo + rayon), caméra qui les montre, intérieurs où l'on circule sans grimper
metadata:
  type: feedback
---

2026-11-22, après le premier essai de G2 (Colonie) : « personne va trouver les affiches, les bouts de carte… là c'est complètement impossible ». Les papiers luisaient trop peu et la caméra fixe les cachait. Dans la maison commune, la grande table bloquait la salle, le bureau était trop petit et il fallait monter sur les meubles pour passer.

**Why:** l'utilisateur est le développeur, il sait où sont les choses ; il juge donc la lisibilité pour un joueur qui ne sait rien.
**How to apply:**
- Tout papier d'énigme reçoit `appel_fort = true` (page_lisible.gd) : halo fort, petite lumière et rayon vertical tant qu'il n'est pas lu.
- Placer les indices face à la caméra. Caméra : un cadre **stable** par quartier (`zone_camera.gd` + `camera_zones.gd`), dans l'axe des rues bordées de deux rangées de maisons (une vue perpendiculaire reste bloquée derrière les toits), jamais une caméra qui tourne à chaque pas (« horrible », 2026-11-22). Pendant une rotation, les touches tenues gardent leur sens (joueur.gd).
- Les indices clés vont dans des lieux ouverts, sur un meuble, face à la caméra. Jamais au dos d'un support. Ex. : les morceaux du plan G2 dans le quai, chez les couturières et à l'école.
- Dans chaque intérieur, laisser un passage libre d'au moins 1,5 m de la porte à chaque objet lisible. Les meubles vont contre les murs. Le robot ne doit jamais avoir à grimper.
Voir [[pacing-feedback]].
