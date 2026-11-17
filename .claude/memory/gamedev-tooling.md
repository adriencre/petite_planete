---
name: gamedev-tooling
description: Where Godot/Blender live and which MCP servers + skills are set up for the petite-planete project (installed 2026-11-13)
metadata:
  node_type: memory
  type: project
  originSessionId: 0e8515d3-4bf7-4d4e-8ce9-c37914625ac9
  modified: 2026-11-16T22:21:18.873Z
---

Setup done 2026-11-13 for the "Petite Planète" Godot project:
- Godot 4.7.2 is NOT on PATH: `C:\Users\adrie\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe`
- Blender 4.2, 4.4 and 5.3 installed; the user normally launches **5.3**. MCP addon (`blender_mcp.py`) is in both 4.4 and 5.3 `%APPDATA%/Blender Foundation/Blender/<ver>/scripts/addons` (copied to 5.3 on 2026-11-15, enabled, works). User must click "Start MCP Server" in the N panel > MCP tab.
- MCP `blender` added at local scope via full uvx path (uv installed by winget, not on PATH in old shells), DISABLE_TELEMETRY=true.
- Godot AI plugin v4.4.1 copied to `addons/godot_ai` and enabled in project.godot. The dock's Configure button did NOT register it with Claude Code; registered manually (user scope) as `godot-ai`: `uvx --link-mode copy --from godot-ai==4.4.1 godot-ai attach --port 8000 --ws-port 9500` (stdio bridge; the raw HTTP endpoint on :8000 returns 401). Needs the Godot editor open.
- 11 gamedev skills from gamedev-skills/awesome-gamedev-agent-skills copied to `.claude/skills/`.

**Why:** the user followed an external setup guide (Blender MCP + Godot AI MCP + skills).
**How to apply:** verify with `/mcp` that both servers connect before relying on them; use the full Godot path for headless tests.

Gotcha (2026-11-14): the open Godot editor keeps project.godot in memory. After editing project.godot on disk (input actions, [shader_globals], main scene), the user must do Projet > Recharger le projet actuel — otherwise global shader uniforms error in @tool scripts and the editor may later overwrite the file with its stale copy. Prefer project_manage(settings_set / set_main_scene) via MCP when the editor is open. Also: a scene left open in the editor can get re-saved after deletion (happened with old root main.tscn).

Gotcha (2026-11-14): new `class_name` scripts written from outside while the editor is open may NOT get registered (the editor rewrites .godot/global_script_class_cache.cfg with its stale list) → "Could not find type X in the current scope" when the user presses F5. Fix: stop the game, `filesystem_manage(op="reimport", paths=[the .gd files])` then `filesystem_manage(op="scan")`, and verify the class list in global_script_class_cache.cfg. Do this after every batch of new class_name scripts.

Gotcha (2026-11-16): the Godot editor crashed (access violation 0xc0000005) when I closed two scene tabs back to back with `scene_manage(op="close")` (test_da then test_camera, which instances test_da). Unsaved editor work is lost in that case. To move or archive scenes, ask the user to close the tabs or the editor first, then use `git mv` + headless `--import`.

Meshy MCP (2026-11-16): the robot was made with image-to-3D `meshy-t2.5` smart topology + `meshy-n1` texture, t-pose, then `meshy_rig`. Rig/animation outputs are separate GLBs (one clip each) and are not saved by `meshy_download_model`: download the URLs with curl. I merged the clips into one GLB in Blender (scene fps 30, same `bone_heuristic` for every import, one NLA track per clip, export `NLA_TRACKS`) → `assets/models/robot_meshy.glb` with `attente` / `marche` / `course`.

Gotcha (2026-11-15): the project treats "inferred from Variant" as an error. Never write `var x := <expr>` when the expr touches an untyped value (Loop.has_flag, robot.night_mode, isl().get_world_3d() on a Node, ternary of untyped strings…) — give an explicit type (`var x: bool = …`). Test scripts (`extends SceneTree`, run with `-s`) compile before autoloads exist: don't name class_name types that use autoloads (e.g. `LueurSpeech.new()`); `load()` the script at runtime instead. Run `--headless --import` first to catch parse errors before the real test runs.
