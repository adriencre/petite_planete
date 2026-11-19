# Fin de session — passation

À faire **avant de rendre la main** (ou quand l'utilisateur dit qu'il change d'outil, « on s'arrête », « je passe sur Codex/Claude ») :

1. **`.agents/ETAT.md`** : le réécrire (≤ 1 page) — ce qui est en chantier, ce qui marche/ne marche pas, prochaines étapes, pièges actifs, questions ouvertes pour l'utilisateur. Mettre la date et l'agent.
2. **Journal** : créer `.agents/journal/AAAA-MM-JJ_<agent>_<sujet-court>.md` (agent = `claude` ou `codex`) à partir de `.agents/journal/_modele.md`. Une entrée par session ; si la session continue le même jour sur le même sujet, compléter l'entrée existante.
3. **Mémoire** : si l'utilisateur a pris une décision durable, donné un retour (« je veux pas… », « plutôt comme ça »), ou si un piège d'outil a été découvert → ajouter/corriger une note dans `.agents/memoire/` + sa ligne dans `INDEX.md`. Supprimer les notes devenues fausses.
4. **Procédures** : si un mode opératoire a changé (nouvelle commande, nouvel outil), mettre à jour le fichier de `.agents/procedures/` concerné.
5. **Docs du jeu** : si une décision de design a été prise, la reporter dans le doc concerné (DA.md, DESIGN.md, ENQUETE.md, ILE_0X, ROADMAP.md) — ce sont eux qui font foi.
6. Si du code ou des scènes ont changé : `python tools/graphify_godot.py`.
7. Si des skills ou MCP ont changé : `python tools/agents/sync.py`.
8. Ne pas committer sans demande ; dire à l'utilisateur ce qui reste non commité.
