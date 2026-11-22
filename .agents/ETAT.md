# État du projet — passation entre agents

> Mis à jour le **2026-11-22** par **Codex** (PC fixe).

- **Coin noir d’Aube** : entrée, palier, galerie et salle reconstruits. Deux maillages de collision dédiés dans le GLB, surfaces continues et décor sans collision. Le robot arrive sur le palier, face à la galerie. Les commandes reviennent après le fondu.
- **Collisions côté ruelle** : la terrasse est découpée aux limites exactes de l’ouverture. La rampe rejoint la rue sans recouvrement et les parois latérales épousent le niveau du terrain. GLB vérifié sur 23 lignes au seuil, écart maximal de 0,05 mm entre les surfaces aux points mesurés.
- **Vérification du GLB** : 2 221 mesures sous l’empreinte de la capsule, pentes maximales de 28,9° à l’entrée et 30,6° sous terre.
- **Visibilité** : le Réveil, le Phare et la Colonie partagent le matériau gris et le script de détection. L’enveloppe passe en fantôme si tous les repères du robot sont masqués. Les aménagements sont cachés pendant l’effet et les coupes de visite restent actives. Le modèle du hangar sépare le mobilier de son enveloppe.
- **À vérifier en jeu sur accord** : traversée et retour du Coin noir, déclenchement derrière l’abri, l’atelier, le phare, la maison du quai, le hangar et les bâtiments de la Colonie.
- La Colonie est accessible par le menu de développement, sans sauvegarde de l’île. Le carnet lit celui de l’île 1. Interactions de l’école et souvenir encore à essayer. Petite porte de la maison d’Aube déjà validée en jeu. Thème musical provisoire.
- Île 2 : parcours continu du Phare et derniers ajustements de guidage, de marée et de fondu extérieur à essayer. Menu : retour visuel et parcours de chargement à vérifier.
- Les changements de la Colonie sont non commités. Passations dans les journaux Codex et Claude du 22 novembre. Recharger la scène dans l’éditeur après réimport du GLB. Demander avant tout lancement ou test Godot.
