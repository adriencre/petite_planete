# Git

- Branche : `main` (projet solo). Ne committer **que si l'utilisateur le demande**.
- Messages de commit **en français** : une ligne de titre (`vX : résumé`), puis une liste à puces de ce qui change. Signer avec la ligne d'attribution de l'agent :
  - Claude : `Co-Authored-By: Claude <noreply@anthropic.com>` (ou la version indiquée par l'outil)
  - Codex : `Co-Authored-By: Codex <noreply@openai.com>`
- **Jamais de secret** dans git (clés API, `.env`, `~/.claude.json`, `.claude/settings.local.json`). La clé Meshy passe par la variable d'environnement `MESHY_API_KEY`.
- Fichiers générés non versionnés : `.godot/`, `graphify-out/` (se régénère avec `python tools/graphify_godot.py`).
- **Toujours versionnés** (pour retrouver mémoire et outils sur n'importe quel PC / agent) : `AGENTS.md`, `CLAUDE.md`, tout `.agents/` (mémoire, journal, ETAT, procédures, skills), `tools/agents/`, et les fichiers générés `.claude/skills/`, `.claude/settings.json`, `.mcp.json`, `.codex/config.toml`. Avant un commit : `python tools/agents/sync.py --check`.
- Pas de chemin absolu propre à un PC dans ces fichiers : on appelle `uvx`, `graphify`, `npx` par le PATH.
- Avant un déplacement de scène : `git mv` (voir `godot.md` pour l'éditeur ouvert).
- Le travail d'une session est décrit dans `.agents/journal/` : un commit peut y renvoyer.
