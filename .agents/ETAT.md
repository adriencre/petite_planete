# État du projet — passation entre agents

> Mis à jour le **2026-11-20** par **codex** pour la reprise sur Mac.

## Où on en est

- Les sept îles sont documentées. La DA v6 prévoit une vue de dessus, du low-poly à facettes et des pastels lumineux. L’île 1 est jouable en maquette.
- L’île 2 se reprend dans scenes/ile_02_maquette.tscn. Terrain Blender, brume, marée, maison du quai, hangar, recharge à la bouée, chaussée, jardin et banc d’Iris, grottes et crypte sont intégrés. L’utilisateur a terminé le tour de la maison et de la recharge sur le PC fixe.
- Le Phare comprend le circuit des trois caps, les engrenages, la barque vers le ravitailleur, la salle des cartes, la lunette à cinq crans et la chambre d’Iris avec son échelle. Le parcours principal a été vérifié par étapes jusqu’à la graduation 129°. Le parcours continu reste à essayer.
- Les derniers retours intègrent le halo et la touche E pour les objets à prendre, le fondu extérieur du Phare quand il masque le robot et l’indication de la basse mer pour les grottes. Voir le journal du 20 novembre.

## Reprise sur Mac

- Récupérer origin/main. L’ancienne sauvegarde Git du Phare est disponible sur la branche sauvegarde-phare-pc.
- Vérifier en jeu le guidage, le fondu du Phare, le banc et la lisibilité des accès et des indices. La préférence de fenêtre de marée reste à confirmer. F8 accélère le cycle.
- Continuer les décors et les interactions restantes selon la feuille de route. La piste du motif musical décliné dans les quatre couches reste à discuter.
- Demander avant tout lancement ou test Godot. Une partie lancée depuis l’éditeur bloque les écritures MCP. Les caches Godot se régénèrent localement et captures/ est exclu de l’import.
- Après une modification de la carte, régénérer le terrain avec tools/blender/terrain_ile_02.py puis réimporter le GLB. Le MCP Blender du Mac pilotait le PC Windows lors de la session précédente.
