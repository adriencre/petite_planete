# Petite Planète — feuille de route

Chaque étape se termine par quelque chose de jouable et testable.
Voir aussi : `DESIGN.md` (le jeu) et `SCENARIO.md` (l'histoire et le script de l'île 1).

---

## Île 1 — L'Île du Réveil

### Phase A — Fondations
- [x] **1. Maquette grise de l'île**
  Forme réelle de l'île au GridMap (bas, falaise, plateau, cascade, grotte, ponton), décors provisoires nommés selon le script.
  *Test : on la parcourt de bout en bout ; distances, caméra et durée tiennent.*
- [x] **2. Effet « endormi / éveillé »**
  Île grise et immobile ; des zones de couleur se répandent depuis un point ; l'eau se réveille avec elles.
  *Test : `F1` réveille une zone. La vague de couleur doit être belle — c'est le cœur de la sensation du jeu.*
- [x] **3. Système d'interaction**
  Icône de touche près des objets utilisables ; composant « interactif » réutilisable sur toutes les îles.
  *Test : s'approcher d'une lanterne, l'icône apparaît, `E` déclenche une action.*

### Phase B — Mécaniques de l'île 1
- [x] **4. Rallumer**
  Animation de l'antenne, impulsion de lumière, petites lanternes → racines lumineuses → grande lanterne → grande vague.
- [x] **5. Planter**
  Cosse qui s'ouvre, graine portée par le robot, terreau gravé d'un symbole, racines qui poussent en escalier praticable.
- [x] **6. Plateau et fin de l'île**
  Lanterne du sommet, réveil total, transition vers le coucher de soleil, barque qui flotte, lumière qui répond au loin, départ et fondu.

### Phase C — Histoire
- [x] **7. Ouverture dans l'abri**
  Noir → yeux qui s'allument, abri poussiéreux, horloge arrêtée, **carnet v1** (pages de symboles illisibles).
- [x] **8. Secret de l'atelier**
  Rebord derrière la cascade, grotte, lanterne, atelier, dessin d'enfant, symbole du nom inscrit dans le carnet.
- [x] **9. Robot expressif**
  Yeux (surpris, content, curieux, triste) et gestes (regarder, baisser la tête, se retourner).

### Phase D — Finition
- [x] **10. Son et polish**
  Silence endormi → vent, vagues, oiseaux au réveil, piano au final ; bruitages ; partie test complète sans aucun texte ; rythme et performances.

---

## Outils réutilisables construits par l'île 1
Effet endormi/éveillé · objets interactifs · lanternes · plantation · carnet · émotions du robot · transitions de lumière · barque.

---

## Refonte v3 — prologue (île 1) adapté au nouveau design
Voir `DESIGN.md` (v3) et `SCENARIO.md`.

- [x] **11. Batterie** : jauge sur l'antenne, la brume vide, la lumière recharge, allumer coûte.
- [x] **12. Boucle et berceau** : batterie vide → le corps s'éteint sur place → réveil dans un corps neuf ; les lanternes de cette boucle s'éteignent ; les anciens corps restent.
- [x] **13. Vision à batterie basse** : les Lueurs apparaissent dans la brume quand l'antenne faiblit.
- [x] **14. Île 1 adaptée** : premier ancien corps, barque cachée dans la crique (et pierre-soleil cachée), graine cachée dans l'abri, atelier des corps (sans dessin d'enfant ni langue inventée), phare de l'île 2 au loin.
- [x] **15. Carnet v3** : carte, croquis, bestiaire, pages du journal de la Gardienne (sans symboles).

## Éteindre (ajouté après la refonte v3)
- [x] **16. Reprendre la lumière** : `E` sur une lanterne allumée → spirale vers l'antenne, batterie +, lanterne éteinte, zone qui se rendort ; 1re fois = vrai moment.
- [x] **17. Mode nuit et secrets de l'île 1** : touche `N` secrète (antenne éteinte, plus de vidage, Lueurs visibles, aucune lumière) ; croquis-indice dans le carnet ; Lueurs sur l'ancien corps ; traînée graine → berceau ; page lumineuse 7 dans l'atelier.

## Île 1 — côté ombre (voir `MONDE_OMBRE.md`, île 1)
Tout ce qui suit ne se voit qu'**antenne éteinte** (`N`) ou à batterie presque vide.
Chaque étape se termine par quelque chose de jouable. Les premières fois sont de vrais moments.

### Phase E — Les outils de l'ombre (réutilisables sur toutes les îles)
- [x] **18. Paroles de lumière** — *fait, testé*
  Un composant « parole » à poser sur n'importe quelle Lueur : des mots en français qui flottent, écrits à la main en turquoise, puis s'effacent comme de la buée.
  Selon le noir : **rien** (antenne allumée) → **bribes** (batterie basse : « …il… revient… ») → **phrase complète** (`N`).
  Les paroles importantes se recopient dans une nouvelle section **« Paroles »** du carnet.
  *Test : une Lueur dit une phrase ; on l'entend en bribes à batterie basse, en entier avec N, et elle apparaît dans le carnet.*
- [x] **19. Le kit d'habitat des Lueurs** — *fait, testé*
  Des décors en scènes `.tscn`, visibles seulement dans le noir : maison-cocon tissée, fils de lumière entre deux arbres, jardin de champignons lumineux, petite place. Plus une version **« effondrée »** pour les déserts gris.
  *Test : poser quelques maisons dans l'éditeur ; invisibles antenne allumée, belles avec N.*
- [x] **20. Les habitants** — *fait, testé*
  Une scène « Lueur habitante » avec plusieurs formes (petite boule, enfant, héron). Comportements simples :
  - flotter près de sa maison ;
  - **fuir** le robot s'il approche (1re moitié) ;
  - **venir** vers lui une fois la confiance gagnée ;
  - **parler** (étape 18).
  *Test : avec N, on s'approche d'une maison, ses habitants se cachent dedans.*

### Phase F — Île 1 côté ombre, 1re moitié (« elles ont peur »)
- [x] **21. Le hameau des pins** — *fait, testé*
  Quelques maisons basses entre les racines des pins, presque vides : les lanternes de l'île sont trop proches.
  **Première bribe du jeu** (un vrai moment) : une petite Lueur sort, regarde le robot, dit « …il… revient… » et s'enfuit.
- [x] **22. Les cicatrices** — *fait, testé*
  Allumer une lanterne **abîme le hameau** côté ombre : les maisons dans sa zone deviennent grises et effondrées.
  Reprendre sa lumière les fait **se retisser lentement**. Le joueur voit ce que coûte la lumière, sans un mot.
- [x] **23. La Pouponnière** — *fait, testé*
  Sous le plancher de l'abri, dans les fentes, de toutes petites Lueurs qui naissent près du berceau. La traînée graine → berceau existe déjà.
  Elles se cachent quand on approche ; une bribe : « …la Bouche… chaude… ».
- [x] **24. Le Compteur** — *fait, testé*
  Une vieille Lueur en forme de héron, sur la crique, près de l'ancien corps, avec un tas de **petites pierres lumineuses** : une par corps.
  À chaque mort du robot, une **pierre de plus** apparaît, et le Compteur dit seulement : « Encore un. »

### Phase G — Île 1 côté ombre, 2e moitié (« Celui-qui-revient »)
> La 2e moitié s'ouvre normalement sur l'île 9. En attendant, une **touche de debug** active la « bascule » pour tester.
- [x] **25. La bascule (provisoire) et le Compteur qui parle** — *fait, testé*
  Après la bascule, le Compteur ne fuit plus : « Tu es revenu deux cent quatorze fois, Petit-Jour. Tu tombes toujours au même endroit, près de l'eau. Tu regardais la mer. »
  Le nombre suit les vraies morts du joueur (214 + ses morts à lui).
- [x] **26. Mission « Laisser sortir les petits »** — *fait, testé*
  Une lanterne au-dessus de la porte de l'abri brûle le seuil : la Pouponnière ne peut pas sortir.
  Il faut **reprendre sa lumière**, puis **guider les petites dans le noir jusqu'aux pins**. Elles suivent le robot seulement s'il reste éteint, et s'éparpillent s'il rallume.
  Récompense : le Compteur donne **sa première pierre**, celle du tout premier corps.
- [x] **27. Le peuple est prêt** — *fait, testé*
  Le hameau **s'étend** dans les anciens déserts gris : nouvelles maisons, petites qui jouent. Ça reste d'une boucle à l'autre.
  **Aide n°1 : l'essaim de la Pouponnière** (voir `MONDE_OMBRE.md`, 3 bis). Dans le noir, il suit le robot et éclaire juste assez pour voir le relief et lire.

### Phase H — Finition
- [x] **28. Son et musique de l'ombre** — *fait, testé*
  La seconde musique, celle des Lueurs (cristalline, aquatique), qui grandit quand on éteint. Un petit son de verre pour chaque mot de lumière. Une partie complète de l'île côté ombre, du début à la fin.
  *Fait : 3 couches synchronisées (`ombre_layer1..3`, générées par `tools/make_ombre_audio.py`) : nappe aquatique dès qu'on éteint, mélodie de verre dans le vrai noir, chœur du peuple une fois la Pouponnière libérée. La musique de la lumière s'efface en même temps. Tests : `tools/test_phase_e.gd`, `test_phase_f.gd`, `test_phase_g.gd`.*

---

### Phase I — Le vrai monde de l'ombre (refonte de l'île 1)
> Les boules et cocons en fil de fer étaient « trop cheap ». Place à un vrai peuple et une vraie ville.
- [x] **29a. Le kit, modélisé dans Blender** (`blender/peuple.blend`, régénérable avec `tools/blender_*.py` puis `tools/ombre_godot.py`) — *fait, validé*
  7 habitants (enfant, petite, ancienne, pêcheur, jardinière, tisserand, le Compteur) avec les mêmes animations ;
  5 maisons (champignon, souche, coquillage, cabane sur pilotis, tour de l'ancienne) ; village et nature.
- [x] **29b. L'île se transforme** (`OmbreObjet`, `OmbreMonde`) — *fait, testé*
  Antenne éteinte : la nuit tombe (ciel, lune, brume bleue), la ville pousse du sol en vague depuis le robot,
  ses collisions n'existent que dans l'ombre. Autour d'une lanterne allumée : tout passe en cendre grise, et se retisse.
- [x] **29c. La ville des Pins** (`tools/ombre_ile1.py`) — *fait, testé*
  9 maisons, place du puits, marché, potagers, ponton, forêt de champignons géants ; les habitants vaquent
  (routines), rentrent chez eux quand ils ont peur, et ressortent si le robot reste éteint et immobile.
- [x] **29d. On leur parle (E)** (`Dialogue`) — *fait, testé*
  L'ancienne (l'histoire, les cendres, la Pouponnière après la bascule), le pêcheur (la crique, la barque cachée),
  la jardinière (les racines qui font des marches la nuit), le tisserand (retisser), l'enfant (le secret derrière l'eau qui tombe).
  Les répliques importantes vont dans « Paroles » ; certaines posent des indices (`indice_barque`, `indice_racines`…).
- [x] **29e. Les chemins de l'ombre** — *fait, testé* (`tools/test_chemins.gd`)
  **L'escalier des géants** : de la crique ouest au plateau (3 m), contre la falaise ; en haut, le belvédère et le Veilleur
  (« Celui du sommet est le pire… »). Indice : la jardinière.
  **Le pont des pêcheurs** : du ponton du village à l'**îlot de corail**, en pleine mer ; le Guetteur y parle du Phare
  (« Ceux du Phare n'ont pas d'yeux… » → indice pour l'île 2). Indice : le pêcheur (2e conversation).
  Antenne allumée, ils n'existent pas ; si on rallume dessus, le sol tient jusqu'à ce qu'on en descende.

## Le jeu de base : l'archipel (côté lumière d'abord)
> Décidé le 2026-11-15 : on développe **toutes les îles côté lumière** (explorer, comprendre, rallumer, énigmes liées entre elles),
> puis on reviendra au **monde de l'ombre** des îles 2 à 9. Voir `ARCHIPEL.md` et `ILE_02_PHARE.md` (feuille de route détaillée, phases J et K).

## Les îles suivantes (côté lumière d'abord ; le côté ombre viendra après)
- [ ] **29. Île 2 — le Phare**
- [ ] **30. Île 3 — le Marais**
- [ ] **31. Île 4 — le Village des Semeurs**
- [ ] **32. Île 5 — le Verger rose**
- [ ] **33. Île 6 — l'Île Engloutie**
- [ ] **34. Île 7 — la Nef**
- [ ] **35. Île 9 — l'île de la Gardienne et la bascule**
- [ ] **36. 2e moitié « Éteindre »** : missions des peuples, aides, la Gardienne sur chaque île
- [ ] **37. Île 8 — le Cœur et la fin** (selon les peuples prêts ; fin secrète)
