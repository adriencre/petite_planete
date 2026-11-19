---
name: ask-before-launching
description: Always warn/ask the user before launching the Godot game or any test that opens a window
metadata:
  type: feedback
---

Before running the game or any Godot test script (even headless imports), tell the user and wait for their OK.

**Why:** 2026-11-14 the user was playing another game (LoL) while Godot test windows kept popping up; they also complained about the game being relaunched in a loop "doing the same thing". They explicitly said "préviens avant de teste et lancer le jeu".
**How to apply:** batch code changes first, then ask once ("je peux lancer le test ? ça ouvre une fenêtre"); never re-run the same test repeatedly just to grab another screenshot — offer that they test in the editor instead. See [[gamedev-tooling]].
