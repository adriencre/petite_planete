# Petite Planète — feuille de route (v4)

> Voir `DESIGN.md` (les règles), `ENQUETE.md` (l'histoire) et les documents des îles.
> L'ancienne feuille de route détaillée (étapes 1 à 29e) est dans `archive/ROADMAP_v3.md`.
> **Décision du 2026-11-15** : on rédige **toutes les îles au complet** avant de reprendre le développement.

---

## Étape 1 — Écrire le jeu (en cours)
- [x] `DESIGN.md` : les règles du jeu (v4)
- [x] `ENQUETE.md` : l'histoire, les personnages, les 7 îles, la fin
- [x] `ILE_01_REVEIL.md` (mis à jour v4)
- [x] `ILE_02_PHARE.md` (mis à jour v4 ; quelques textes encore à valider)
- [x] `ILE_03_COLONIE.md` (quelques points encore à valider)
- [x] `ILE_04_QUARANTAINE.md` (l'île blanche)
- [x] `ILE_05_NEF.md` (le crash et l'antenne d'appel au secours)
- [x] `ILE_06_CENTRALE.md` (sous la mer, la fin)
- [x] `ILE_07_ILE_CACHEE.md` (la maison d'Iris)
- [x] La toile de l'enquête (doc de conception, pas dans le jeu) : `TOILE_ENQUETE.md`
- [x] La fin et la fin secrète (« Merci. », voir `ILE_06_CENTRALE.md` §7)
- [x] La touche `N` : **retirée** (2026-11-16). On voit la brume une fois accepté (en coupant son câble) ; avant, des bribes à batterie basse.

---

## Ce qui est déjà construit (île 1)
Détail complet dans `archive/ROADMAP_v3.md`.
- **Fondations** : maquette GridMap, effet endormi/éveillé, objets interactifs.
- **Mécaniques** : rallumer, planter (racines-escalier), fin de l'île et barque.
- **Histoire** : réveil dans l'abri, atelier derrière la cascade, robot expressif, son et musique.
- **Moteur** : batterie, boucle et berceau, anciens corps, vision à batterie basse, carnet (carte, croquis, bestiaire, pages), reprendre la lumière, mode nuit `N`, page 7.
- **Le peuple caché de l'île 1** : paroles de lumière, kit d'habitat modélisé dans Blender, habitants avec routines et dialogues (`E`), cicatrices autour des lanternes, la ville des Pins, l'escalier des géants, le pont des pêcheurs et l'îlot de corail, musique de l'ombre.

---

## Étape 2 — Adapter l'île 1 à la v4 (au prochain dev)
Voir `ILE_01_REVEIL.md` §13.
- [ ] Fin de l'île : plus de fondu, plus de Phare qui s'allume au loin (silhouette sombre + lueur de la bouée).
- [ ] Barque cachée dans la crique à chaque boucle, toujours à flot.
- [ ] Retirer le mode nuit `N` et le croquis de l'atelier ; la ville des Pins devient la matière de la cinématique de fin.
- [ ] Retirer l'ancienne 2e moitié : touche de debug « bascule », « Tu es revenu deux cent quatorze fois », mission « Laisser sortir les petits », répliques de l'Ancienne après la bascule, aide de l'essaim, extension du hameau, 3e couche musicale.
- [ ] Remplacer la page 1 (`assets/notebook/journal/page_01.tres`) par la nouvelle version (voir `ILE_02_PHARE.md` §7).
- [ ] L'ordre d'Ysolde sur un papier à côté du berceau ; l'atelier un peu trop grand pour le robot (décidé le 2026-11-16).
- [ ] Le carnet : juste ce qu'on a vu (lieux, textes, dessins, cartes), sans flèches ni questions.

## Étape 3 — L'archipel et l'île 2
Voir `ILE_02_PHARE.md` §11 (phases J et K).
- Ordre : K1 (maquette grise) → J4 (`WorldClock`, marée) → K2 → K3 → K4 → J1–J3 (scène Archipel, barque pilotable, brume en mer) → K5 → K6 → K7.

## Étape 4 — Les îles 3 à 7
Une fois leurs documents validés.

## Plus tard — le peuple caché des îles 2 à 7 (visible seulement dans la cinématique de fin et les bribes à batterie basse)
Après le jeu de lumière (décision : on se concentre d'abord sur le jeu de lumière).
