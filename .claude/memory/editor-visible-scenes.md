---
name: editor-visible-scenes
description: "Petite Planète must be built as real .tscn scenes/resources visible in the Godot editor, small scripts, chill minimal scope — not one giant procedural script"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2218259f-2f88-48b0-9b2b-5b0a1db0270d
  modified: 2026-11-13T23:15:15.503Z
---

On 2026-11-13 the user scrapped the first version (a 46 KB main.gd generating everything in code) because "tout en commande, aucun asset affiché" and it was "trop poussé", losing the chill visual. They also rejected a realistic-grass meadow as "pas assez low poly chill".

**Why:** the user wants something sustainable they can open and tweak in the editor, and a calm mood over feature count. They like to see ideas/mockups before dev ("propose des idées avant de dev").
**How to apply:** add things as nodes/scenes/resources in .tscn/.tres, keep scripts short, use @tool when generated content should show in the editor; propose + render a quick mockup before big visual changes; verify with screenshots. Art direction: see [[art-direction]].
