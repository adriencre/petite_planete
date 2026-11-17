---
name: game-vision
description: "Petite Planète v4 (2026-11-15): Outer-Wilds-style investigation « Où sont les Semeurs ? », 7 islands; docs = DESIGN.md (rules), ENQUETE.md (story), ILE_0X_*.md (one per island); v3 docs archived"
metadata:
  node_type: memory
  type: project
  originSessionId: 764b1fdb-51f6-4f8d-b387-88a40703e51d
  modified: 2026-11-15T04:42:46.297Z
---

v4 decided with the user on 2026-11-15 (replaces v3: 9 islands, two halves, bascule, peoples' missions — all archived in `archive/`).
- Docs at repo root: `DESIGN.md` (rules: battery as constraint, secret N mode, loop/cradle, carnet = investigation board, sea/boat, cycles tide 8 min / beam 40 s / moon 24 min, art), `ENQUETE.md` (story + all decisions), `ILE_01_REVEIL.md`, `ILE_02_PHARE.md`, `ILE_03_COLONIE.md`, `ROADMAP.md`. Old v3 docs in the old folder's `archive/`. 2026-11-16: game code/assets reset to zero (v5), old v4 prototype stays in the separate folder `Bureau/petite-planete`; v5 lives in `Bureau/petite-planete-v5`; only these 6 docs kept.
- Story: Semeurs came from space, lived on light like the robot; their lanterns starved the brume; Iris (la Gardienne) cut the overloaded Centrale knowingly to save the brume people → all Semeurs emptied in one night (skeletons, hidden early; false lead "ils sont partis"); the brume people accepted Iris. Robot survived via the cradle's own power line; final gesture = cut that line at the Centrale. Single free investigation, no bascule, same ending for all.
- 7 islands: 1 Réveil (robot's island), 2 Phare (Iris's post), 3 Colonie (town + serres + sunken old port), 4 Quarantaine (île blanche), 5 Nef (crash + distress antenna), 6 Centrale (underwater, finale), 7 île cachée (Iris's home). Islands 4–7 still to design.
- 6 Semeurs: Iris, Ysolde (Commandante), Tavin (Ingénieur), Saule (Médecin), Orme (Pilote), Aube (Enfant, died; teaches via drawings).

**Why:** user explicitly chose each point through many question rounds.
**How to apply:** read ENQUETE.md before designing; ask the user many questions with proposals (AskUserQuestion) before writing an island; see [[outer-wilds-direction]], [[design-docs-first]], [[pacing-feedback]], [[art-direction]].
