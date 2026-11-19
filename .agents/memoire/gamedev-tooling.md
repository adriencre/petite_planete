---
name: gamedev-tooling
description: Où sont Godot/Blender sur la machine, quels MCP et skills sont installés ; les modes opératoires détaillés sont dans .agents/procedures/
metadata:
  type: reference
---

Installé le 2026-11-13 (l'utilisateur a suivi un guide externe Blender MCP + Godot AI MCP + skills) :
- **Godot 4.7.2**, pas dans le PATH : `C:\Users\adrie\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe`
- **Blender** 4.2, 4.4 et 5.3 ; l'utilisateur lance **5.3**. Addon MCP `blender_mcp.py` installé et activé dans 4.4 et 5.3.
- **uv/uvx** installé par winget, pas toujours dans le PATH : `C:\Users\adrie\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uvx.exe`
- **Plugin Godot AI v4.4.1** dans `addons/godot_ai` (activé dans project.godot).
- **MCP** : blender, godot-ai, meshy — liste canonique dans `.agents/mcp/serveurs.json`.
- **Skills** : 11 skills gamedev (gamedev-skills/awesome-gamedev-agent-skills) dans `.agents/skills/`.
- **graphify** : `C:/Users/adrie/.local/bin/graphify.EXE`.
- **Chrome** (rendu des affiches) : `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Disque C: presque plein (~11 Go libres le 2026-11-17) : pas de gros installs locaux.

**How to apply:** procédures dans [[procedures-index]] (`.agents/procedures/` : godot.md, blender.md, meshy.md…). Vérifier que les MCP sont connectés avant de compter dessus.
