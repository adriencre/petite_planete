# `.agents/` — dossier commun des agents IA

Ce dossier est **la source de vérité partagée** par tous les agents qui travaillent sur le projet (Claude Code, Codex, ou un autre). Le point d'entrée est `AGENTS.md` à la racine.

## Contenu
| Chemin | Rôle | Qui l'écrit |
|---|---|---|
| `ETAT.md` | Passation : où on en est, en chantier, prochaines étapes, pièges | Réécrit à chaque fin de session |
| `journal/` | Une entrée par session (`AAAA-MM-JJ_<agent>_<sujet>.md`, modèle `_modele.md`) | Ajouté à chaque session |
| `memoire/` | Faits durables : retours et décisions de l'utilisateur, références. Index : `memoire/INDEX.md` | Quand une décision/un retour durable apparaît |
| `procedures/` | Comment faire : Godot, Blender, Meshy, audio, affiches, graphify, git, fin de session | Quand un mode opératoire change |
| `mcp/serveurs.json` | Liste canonique des serveurs MCP (sans secret) | À la main, puis `sync.py` |
| `skills/` | Skills partagés (format SKILL.md). Codex les lit ici directement | Installés ici, puis `sync.py` |

Ce qui **n'est pas** ici : les décisions de design du jeu. Elles vivent dans les docs à la racine (DA.md, DESIGN.md, ENQUETE.md, ILE_0X, ROADMAP.md) qui font foi.

## Format d'une note mémoire
```markdown
---
name: nom-en-kebab-case
description: résumé en une ligne (sert à juger si la note est utile)
metadata:
  type: user | feedback | project | reference
---

Le fait. Pour feedback/project : **Why:** (pourquoi) et **How to apply:** (comment l'appliquer).
Liens vers d'autres notes : [[nom-d-une-autre-note]].
```
Une note = un fait. Corriger une note plutôt qu'en créer une deuxième ; supprimer celles qui deviennent fausses ; toujours mettre à jour `memoire/INDEX.md`.

## Synchronisation avec chaque outil
Chaque outil lit ses fichiers à un endroit différent. `python tools/agents/sync.py` les génère depuis ce dossier :

| Outil | Instructions | Skills | MCP |
|---|---|---|---|
| Codex | `AGENTS.md` (natif) | `.agents/skills/` (natif) | `.codex/config.toml` (généré) |
| Claude Code | `CLAUDE.md` → `@AGENTS.md` | `.claude/skills/` (copie générée) | `.mcp.json` (généré) |

`python tools/agents/sync.py --check` vérifie sans rien modifier.

## Mise en place sur la machine (une seule fois)
Tout est versionné : un `git clone` (ou `git pull`) suffit pour retrouver mémoire, journal, skills et MCP, avec Claude Code comme avec Codex. Sur un nouveau PC il faut seulement avoir dans le PATH : `uv` (`winget install astral-sh.uv`), `node`/`npx`, `graphify` et Godot (voir `procedures/godot.md`).
0. Après le clone : `python tools/agents/sync.py --check` (doit dire « tout est synchronisé »).
1. **Clé Meshy en variable d'environnement** (elle ne doit jamais être dans le repo). Dans un terminal :
   `setx MESHY_API_KEY "msy_…"` puis fermer/rouvrir les terminaux, Claude Code et Codex.
2. **Codex** : ouvrir le projet une fois et accepter de le marquer « trusted » (sinon `.codex/config.toml` n'est pas lu). Vérifier avec `/mcp`.
3. **Claude Code** : à la première session, accepter les serveurs MCP du projet (`.mcp.json`). Vérifier avec `/mcp`.

## Ajouter un skill ou un MCP
- Skill : le mettre dans `.agents/skills/<nom>/SKILL.md` (et dans `skills-lock.json` s'il vient d'un dépôt), puis `python tools/agents/sync.py`.
- MCP : l'ajouter dans `mcp/serveurs.json` (secret → `env_depuis_systeme`), puis `python tools/agents/sync.py`, puis une ligne dans `procedures/` si besoin.
