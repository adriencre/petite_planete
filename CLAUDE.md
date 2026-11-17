## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. When the answer is under a Markdown heading, `graphify section "<heading>"` prints that section's text, so the .md need not be opened. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- graphify has no GDScript/.tscn extractor: `tools/graphify_godot.py` adds them (functions, signals, `##` comments, calls, preloads, scene → script/scene/shader/model links). After modifying code or scenes, run `python tools/graphify_godot.py` — NOT `graphify update .` alone, which would drop all the Godot nodes. No API cost.
- What graphify skips is listed in `.graphifyignore` (addons/, assets/, .claude/, scenes/archive/…). graphify-out/ is gitignored.
