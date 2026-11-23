# 2026-11-22 — claude — G3 : le jardin du haut (questions + Blender)

## Demandé
« explique moi G3 », « pose-moi les questions », « pose toutes tes questions », « on passe à la construction ».

## Fait
- G3 entièrement tranché avec l'utilisateur (3 séries de questions) et reporté dans `ILE_03_COLONIE.md` § G3 et § Forme v6.
- Nouveau `tools/blender/jardin_du_haut.py`, exécuté par `colonie_du_lagon.py` après `ville_haute.py` :
  - **chemin de halage** (secteurs 0 à 6, z 1,0, bordure basse, bornes) ;
  - **écluse** : quai d'arrivée, avant-port, 4 sas en escalier le long de la corde de la falaise nord (secteurs 6 à 8), murs de tête, portiques à poulies ; pas de collision au fond des sas (un robot tombé retombe sous -2 et revient au départ) ;
  - objets animables, origine sur leur pivot : `Vanne_sas_0..3` (bas de la vanne), `Eau_sas_1..4` (surface au niveau bas), `Ponton_ecluse` (centre du pont), `Levier_ecluse` + `Socle_du_levier` (axe), `Flotteur_ecluse` (niveau de la mer, index doré à +2,9), `Verrou_ecluse`, `Coeur_lampe_mere`, `Disque_lampe_mere`, `Cylindre_musique` ;
  - **jardin du haut** (secteurs 8 à 10, côté lagon, sol à 10,1) : mur blanc de 6,3 m avec piliers d'angle et contreforts côté rue, ouverture de la porte de service (secteur 8, t = 0,62), parapet ouvert devant le dernier sas et le belvédère, lampe-mère, premier arbre rose, établi et outils, belvédère, citerne de pluie, rigole ;
  - **serres basses** (`serre_basse()`, remplace l'ancienne `Verriere_XX` fermée) : porte de 3 m sur la rue, vitres côté rue presque toutes tombées, 7 arbres penchés à 48° vers la lampe, anneau de pierre au pied ;
  - plaque gravée sous le portique du carillon (`Plaque_du_carillon`) ;
  - repères Godot : `tools/blender/sources/jardin_du_haut_reperes.txt`.
- `colonie_du_lagon.py` : exec du nouveau script, appel de `serre_basse()` et de `construire_jardin_du_haut()`. `hors_friche` est étendu au jardin.
- `tools/blender/rendu_jardin_du_haut.py` : 7 vues de contrôle → `concept/ile_03/jardin_du_haut_*.png`.
- GLB et .blend régénérés en ligne de commande. **Pas de réimport Godot, pas de lancement.**

## Décisions de l'utilisateur
- Écluse à sas (citerne de pluie sur la crête), porte ouverte ~45 s au pic, carillon + cloche-relais.
- Lampe-mère : comme une lanterne (câble), cinématique plus longue. Arbres : serres basses, en éventail.
- Citerne visible de la ville ; levier à crans sur le ponton après le flotteur ; retour par une porte de service barrée (raccourci) ; indice = plaque du carillon + flotteur.
- Souvenir : disque de verre peint qui tourne (lanterne magique) projeté sur le mur ; chant = cylindre musical dans le socle.
- Jardin : premier arbre, outils, dessin d'Aube, belvédère.
- Implantation : jardin au bord de la falaise, chemin de halage, Blender puis Godot (rendus à valider d'abord).
(Tout est dans ILE_03_COLONIE.md § G3.)

## Fichiers touchés
- tools/blender/jardin_du_haut.py (nouveau), tools/blender/rendu_jardin_du_haut.py (nouveau), tools/blender/colonie_du_lagon.py, tools/blender/sources/jardin_du_haut_reperes.txt
- assets/models/ile03/colonie_du_lagon.glb, concept/ile_03/colonie_du_lagon.blend, concept/ile_03/jardin_du_haut_*.png
- ILE_03_COLONIE.md

## Reste à faire / questions ouvertes
- Validation des rendus par l'utilisateur, puis Godot : marée dans la Colonie (Mer + ponton qui suivent `HorlogeMonde.niveau_mer()`), carillon + cloche-relais au pic, flotteur et verrou, levier (E) → cinématique de montée sas par sas, porte barrée du jardin (`porte_barree.gd`), lampe-mère (câble) → souvenir projeté (SpotLight3D à projecteur) + cylindre musical, plaque du carillon et dessin d'Aube (`page_lisible`), zone de caméra du jardin, `batiments_fantomes.gd` (nouveaux noms).
- Les serres étaient des boîtes fermées : vérifier en jeu la collision (trimesh) de la porte et des parois de verre.
- Le dessin d'Aube du jardin : vers quelle énigme renvoie-t-il ? Le schéma `concept/ile_03_formes.png` montre encore l'écluse au sud.
- Petits triangles sombres aux jointures du parapet (rendu), sans gravité.

## Suite : Godot (« lets go »)
- Blender : portiques plus hauts (`HAUT_PORTIQUE` 5,6, pour une `LEVEE_VANNE` de 5,8), seuil et marches devant la porte de service (`Seuil_porte_jardin`). GLB régénéré.
- Scripts : `scripts/maree_lagon.gd` (la Mer suit `HorlogeMonde.niveau_mer()`), `scripts/ecluse_jardin.gd` (carillon et cloche-relais quand la phase passe 0,75, fenêtre de 45 s, bosse du pic qui pousse l'index et le verrou, levier sur le ponton : E trop tôt = le levier bute, E à temps = montée sas par sas, le robot est porté par le ponton, sauvegarde « ecluse:EcluseJardin »), `scripts/lampe_mere.gd` (geste de la boîte à musique, cœur et lumière, disque et cylindre qui tournent, tableaux en fondu au rythme du chant, note au carnet, reste allumée), `shaders/souvenir_projete.gdshader` (additif).
- Générateur `tools/godot/jardin_du_haut_scenes.py` (ré-exécutable, blocs « jh_ ») : `scenes/ile03/porte_jardin.tscn` (porte_barree.gd) et, dans `ile_03_maquette.tscn` : MareeLagon, EcluseJardin (+ Carillon, ClocheRelais, Arrivee), LampeMere, EcranSouvenir, CentreSouvenir, PorteJardin, PlaqueCarillon, DessinBelvedere, ZoneJardin (priorité 3, une boîte par secteur).
- Sons provisoires : carillon, cloche, chaine, eau_sas (`tools/audio/sons_ile_03.py`), `chant_semeurs.wav` (`tools/audio/chant_semeurs.py`).
- Images : `assets/affiches/souvenir_arbre_rose_1..5.png` (`tools/affiches/souvenir_arbre_rose.py`), `dessin_aube_serres.png` (`dessin_aube_serres.html` + rendre.py).
- Avec l'accord de l'utilisateur : `--headless --import` sans erreur. `--check-only` : ecluse_jardin et lampe_mere compilent (vérifiés sur des copies où Sauvegarde et HorlogeMonde sont neutralisés, à cause du piège des autoloads). `tests/diag_jardin_du_haut.gd` : 15 pièces trouvées dans le GLB, Colonie et porte instanciables. **Pas joué.**
- Pour tester vite : Page↑ accélère la marée (x4, x16, x64), Page↓ ralentit ; F8 arrête le jeu (raccourci de Godot). Le premier carillon sonne vers 7 min de jeu (phase de départ 0,85, pic à 0,75).
