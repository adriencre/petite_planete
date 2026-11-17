---
name: art-direction
description: v5 DA decided 2026-11-16 and written in repo DA.md (3D chill pastel « à la Outer Wilds »); v4 iso-blocks DA rejected; camera 3rd vs 1st person still to test
metadata:
  node_type: memory
  type: project
  originSessionId: 9f49c985-6ebd-40c5-8dfe-cd5f837f6461
  modified: 2026-11-16T03:22:40.872Z
---

2026-11-16: v4 look (iso low-poly diorama, blocks, dull sage/beige palette) rejected — "couleurs", "blocs", "ne raconte rien". Old prototype stays in `Bureau/petite-planete`, don't reuse it.

v5 DA was settled through 6 rounds of questions and is fully written in the repo's `DA.md` (read it before any visual work). Key points: 3D, pastels lumineux, no outlines, procedural "couleurs + bruit doux" shaders (no painted textures), one dominant hue per island, slow day/night cycle, NO weather, planet = Semeurs' home world, zero HUD, paper ink notebook, NO magic FX (cable + plug, see [[no-magic-robot]]), organic "grown" Semeur architecture, sky-sea-creature hidden people, mode N = soft switch to blue night.

Camera VALIDATED 2026-11-16: first person, with the antenna bulb hanging in view like an anglerfish lure (battery gauge + real light), vision blur at low battery, eyelid for mode N; 3rd person only for big cinematic moments (`scenes/test_camera.tscn`, `scripts/joueur.gd`). Night/mode N v1 REJECTED for now: "beaucoup trop éclairé, couleurs vives, pas assez pastel" — redo later, softer and pastel. Post-effects still open (only glow kept). Reference scene: `scenes/test_da.tscn` (v2 liked; the tower/ruin there are placeholders).

Process the user likes: debate in text first, they may test prompts in an image AI; then build real Godot test scenes (Blender via MCP for models).

**Why:** user disliked the v4 DA after reflection and wanted to define the new one through questions.
**How to apply:** follow DA.md; if something visual isn't covered there, ask with proposals. See [[game-vision]], [[editor-visible-scenes]].
