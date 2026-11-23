# 2026-11-23 — claude — Navigation entre les îles

## Demandé
« je veux que tu connectes les 3 îles, que je puisse me balader vers les autres îles une fois l'île 1 finie »

## Fait
- Traversée « cap + brume » : silhouettes des autres îles au large (feu qui perce la brume), cap dessus, la brume du large s'épaissit (~25 m), chargement « Traversée vers … », la barque sort de la brume devant le port de l'île visée, robot à la barre.
- `scripts/archipel.gd`, `scripts/large.gd`, `scenes/large.tscn`, `scenes/archipel/silhouette_{reveil,phare,colonie}.tscn`.
- `sauvegarde.gd` : `traverser()`, `arrivee_de`, `batterie_arrivee`. `barque.gd` : arrivée en mer, Large au lieu du rayon fixe. `reveil.gd` : pas de réveil en arrivant par la mer. `ponton.gd` : `bois_visible`.
- Scènes : `Large` dans les 3 îles ; Colonie : `PontonDuCarillon` (repères sur le ponton du GLB) et `Barque`.
- Diagnostic `tests/diag_traversee.gd` : 0 erreur.

## Décisions de l'utilisateur
- Voyage « cap + brume » (pas de scène Archipel ni de grande scène unique pour l'instant) → DESIGN.md.
- On accoste à la Colonie au ponton du quai existant.

## Fichiers touchés
- Voir ci-dessus + `scenes/ile_0{1,2,3}_maquette.tscn`, `DESIGN.md`, `.agents/A_TESTER.md` §6, `.agents/ETAT.md`.

## Reste à faire / questions ouvertes
- Essai en jeu (§6), surtout les points d'arrivée en eau libre et la lisibilité des silhouettes.
- Mort loin du Réveil, carnet commun entre îles.
- Verrou « après la fin de l'île 1 » retiré à la demande de l'utilisateur (« je peux jamais arriver au phare »).
