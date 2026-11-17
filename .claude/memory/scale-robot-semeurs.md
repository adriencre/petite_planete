---
name: scale-robot-semeurs
description: "Scale decided 2026-11-16: robot ~1.90 m, Semeurs 2.5–3 m (only a bit taller) — NOT tiny robot vs giant Semeurs"
metadata:
  node_type: memory
  type: project
  originSessionId: 9f49c985-6ebd-40c5-8dfe-cd5f837f6461
  modified: 2026-11-16T03:05:37.530Z
---

After playing the island test, the user found robot 0.95 m vs Semeurs ~4 m far too different: "le robot doit être un petit peu plus petit… genre le robot 1m90 et les gens 2m50 à 3m".
Applied: robot model ×2 (capsule 1.9 m, eyes 1.65 m in `scripts/joueur.gd`), Semeur objects ×0.7 (doors ~3 m).

**Why:** user wants the Semeurs only slightly taller than the robot, not giants.
**How to apply:** build all Semeur architecture/props for 2.5–3 m beings; older island docs (ILE_01/02 "très grands", "établi immense", robot "assez petit pour passer" like Aube) predate this and need checking. See [[art-direction]].
