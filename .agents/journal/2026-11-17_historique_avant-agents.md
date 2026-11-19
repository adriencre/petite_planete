# 2026-11-13 → 2026-11-18 — historique reconstruit (avant le dossier `.agents/`)

Entrée écrite le 2026-11-19 par claude à partir des commits et de l'ancienne mémoire de Claude. Toutes ces sessions étaient faites avec Claude Code.

## Ce qui s'est passé
- **2026-11-13** : installation des outils (Godot 4.7.2, Blender MCP, Godot AI MCP, 11 skills). Une 1re version « tout en code » (main.gd de 46 Ko) est rejetée → scènes éditables dans l'éditeur.
- **2026-11-14** : retour « ça va beaucoup trop vite » → réveil lent, premières fois en cinématique. L'utilisateur demande de **prévenir avant de lancer** le jeu/les tests.
- **2026-11-15** : histoire v4 (enquête « Où sont les Semeurs ? », 7 îles, 6 Semeurs) ; décision d'écrire **toutes les îles** avant de développer ; rejet de « une île = une mécanique ». Premier commit `e0d980e`.
- **2026-11-16** : v5 (nouveau dossier `petite-planete-v5`), DA v5, échelle robot 1,90 m / Semeurs 2,5–3 m, allumage par **câble** (pas de magie), mode N retiré. Puis **DA v6** : vue de dessus low-poly, formes des 7 îles, maquette jouable île 1, robot Meshy rigué. Commits `5a4106f`, `778cc63`.
- **2026-11-17** : plantation retirée (escalier simple) ; musique refaite via ACE-Step en ligne (4 couches) ; affiches des Semeurs rendues depuis HTML ; graphify + `tools/graphify_godot.py`. Commit `5f25fda`. Puis écran titre, pause, réglages, sauvegarde (non commité).
- **2026-11-18** : un seul HUD (jauge batterie) ; abri vieilli, les « pas de géants » vers l'atelier, Tavin envoie au Phare (non commité).

## Où trouver le détail
- Décisions de design : DA.md, DESIGN.md, ENQUETE.md, ILE_0X (sections « Décisions »), ROADMAP.md.
- Préférences de l'utilisateur : `.agents/memoire/`.
