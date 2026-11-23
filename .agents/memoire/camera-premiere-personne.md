---
name: camera-premiere-personne
description: "1re personne (outil de dev, touche V) : toute cinématique recule en 3e personne puis revient ; toits gardés ; voûte de grotte visible ; branchement du câble filmé de près"
metadata:
  type: feedback
---

2026-11-22 : l'utilisateur teste le jeu en 1re personne (touche DEV V : vue de dessus → 1re → 3e). Ses demandes : un dézoom de la 1re à la 3e personne au début de chaque cinématique, l'animation jouée en 3e, puis le retour ; la lampe-mère recule pour montrer le souvenir ; un plafond pour la grotte du Coin noir ; un branchement du câble « propre et pro » qu'on voit bien. Aussi : en 1re personne, les toits ne s'effacent pas en entrant.

**Why:** la vue de dessus reste la direction (DA.md), mais tout doit rester juste et soigné quand on regarde de près.
**How to apply:** une nouvelle cinématique met `cinematique = true` AVANT de tester `troisieme_personne()` (geste du robot), cadre avec `joueur.recul_cinematique(depuis)` plutôt que la position de la caméra, et commence par un plan de côté sur le geste (voir `_plan_de_cote` dans lanterne_fleur.gd / lampe_mere.gd). Un nouveau décor « coupé à plat » pour la vue de dessus prévoit son dessus (voûte, toit) pour la 1re personne. Voir [[pacing-feedback]].
