@AGENTS.md

## Spécifique à Claude Code
- **Mémoire** : la mémoire de ce projet est `.agents/memoire/` (partagée avec Codex). Y écrire les nouvelles notes et mettre à jour `.agents/memoire/INDEX.md` ; ne pas utiliser la mémoire automatique utilisateur (`~/.claude/projects/.../memory/`) pour ce projet.
- **Skills** : `.claude/skills/` est une copie générée de `.agents/skills/` par `python tools/agents/sync.py` — modifier les skills dans `.agents/skills/`, jamais dans `.claude/skills/`.
- **MCP** : `.mcp.json` est généré depuis `.agents/mcp/serveurs.json` par le même script.
- Les hooks graphify de `.claude/settings.json` rappellent la règle « graphify d'abord » automatiquement.
