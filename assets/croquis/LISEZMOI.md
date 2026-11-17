# Les dessins au crayon du carnet

Le carnet (`scripts/carnet.gd`) a une page dessinée pour **les lieux qui comptent pour l'enquête**
(5 ou 6 par île). Les autres lieux n'ont pas de page : juste leur nom sur la carte du carnet.
S'il manque un dessin prévu, le carnet garde un croquis automatique en secours.

## Comment les faire
1. Les photos à redessiner sont dans `concept/croquis_sources/` (1536 × 1024, sans brume).
   Pour les refaire : cocher **Exporter photos** sur le nœud **Carnet**, lancer le jeu une fois, décocher.
2. Les donner à ChatGPT, toutes dans la même conversation, avec ce prompt :

> Redessine cette image comme un croquis au crayon dans un carnet de voyage d'explorateur : traits de
> graphite fins et un peu tremblés, hachures légères pour les ombres, quelques touches d'aquarelle très
> pâle (vert sauge, rose poudré, or doux), sur papier crème légèrement texturé. Garde exactement la
> composition et les formes de l'image. Le petit robot blanc à antenne reste un robot. Les bords du
> dessin se fondent dans le papier, sans cadre. Style dessiné à la main, naïf et doux. Aucun texte,
> aucune signature. Format paysage 3:2.

3. Enregistrer chaque dessin ici, en PNG, avec **le même nom** que la photo.

## Île 1 : 6 dessins
| Fichier | Lieu | Pourquoi |
|---|---|---|
| `abri.png` ✅ | l'abri | là où tout commence, le berceau |
| `grande_lanterne.png` ✅ | la grande lanterne, au sommet | le but de l'île |
| `atelier.png` ✅ | l'atelier des robots | le secret : on fabrique des robots ici |
| `ancien_corps.png` ✅ | l'ancien corps | le premier indice : « les corps, c'est moi » |
| `barque.png` ✅ | la barque | ce qui ouvre l'archipel |
| `phare.png` ⏳ | le Phare vu du sommet | dessin de la fin, l'appel vers l'île 2 |

Pour ajouter un lieu dessiné : `DESSIN_DU_LIEU` dans `scripts/carnet.gd` (repère de la carte → nom du fichier).
