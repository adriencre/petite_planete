# 2026-11-19 — claude — dossier commun des agents

## Demandé
« Créer un dossier qui servira aux agents IA… je vais passer de temps en temps de Claude Code à Codex… qu'il utilise les mêmes procédures, les mêmes MCP, les mêmes skills… que chacun se base sur l'historique. »

## Fait
- `AGENTS.md` (point d'entrée commun, lu nativement par Codex) ; `CLAUDE.md` l'importe (`@AGENTS.md`).
- `.agents/` : README, ETAT (passation), journal, mémoire commune (12 notes reprises de la mémoire de Claude), procédures, liste MCP, skills.
- Skills déplacés de `.claude/skills/` vers `.agents/skills/` ; `.claude/skills/` est maintenant une copie générée (ignorée par git).
- `tools/agents/sync.py` : génère `.claude/skills/`, `.mcp.json` (Claude) et `.codex/config.toml` (Codex) depuis `.agents/`.
- Mémoire corrigée : la note DA disait encore « 1re personne validée » → v6 vue de dessus ; docs des îles 4-7 notés comme écrits.
- Ancienne copie `.claude/memory/` supprimée ; la mémoire automatique de Claude renvoie vers `.agents/memoire/`.

## Décisions de l'utilisateur
- Plan validé tel quel (structure `.agents/`, sync par script, clé Meshy en variable d'environnement).

## Fichiers touchés
- Nouveaux : `AGENTS.md`, `.agents/**`, `tools/agents/sync.py`, `.mcp.json`, `.codex/config.toml`
- Modifiés : `CLAUDE.md`, `.gitignore`, `.graphifyignore`

## Reste à faire / questions ouvertes
- L'utilisateur doit créer la variable d'environnement `MESHY_API_KEY` (voir README).
- Vérifier dans Codex : `/mcp` et les skills ; projet marqué « trusted » pour que `.codex/config.toml` soit lu.
- Une fois `.mcp.json` validé dans Claude, retirer les doublons MCP de `~/.claude.json` (avec accord).

## Suite : tout versionner pour GitHub
- Demande : retrouver mémoire/outils partout, quel que soit le PC ou l'agent.
- `.claude/skills/` n'est plus ignoré par git (copie générée mais versionnée → marche dès le clone).
- Plus de chemins absolus : `uvx` et `graphify` appelés par le PATH (`serveurs.json`, `.claude/settings.json`), `sync.py` relancé.
- `procedures/git.md` liste ce qui doit toujours être versionné ; `README.md` explique la mise en place sur un nouveau PC.
