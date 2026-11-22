# Blender — procédures

- L'utilisateur utilise **Blender 5.3**. L'addon MCP (`blender_mcp.py`) est dans `%APPDATA%/Blender Foundation/Blender/<ver>/scripts/addons` (4.4 et 5.3).
- **L'utilisateur doit cliquer « Start MCP Server »** (panneau N > onglet MCP) avant que le MCP `blender` réponde. Sinon, lui demander.
- Commencer par `get_addon_status` puis `get_scene_info` ; `look` pour voir le résultat (petite taille d'image pour économiser).
- Les nœuds de shader se cherchent par type, pas par nom (noms traduits en français).
- Scripts de modélisation du projet : `tools/blender/*.py` (un fichier par objet : `abri.py`, `barque.py`, `grande_lanterne.py`…, fonctions communes dans `helpers.py`, pont MCP dans `blender_bridge.py`). Réutiliser / étendre ces scripts plutôt que modéliser à la main sans trace.
- **Sans MCP** (ou pour ne pas toucher à la scène ouverte de l'utilisateur) : `"/c/Program Files/Blender Foundation/Blender 5.3/blender.exe" -b -P tools/blender/colonie_du_lagon.py -- --sans-rendu` régénère GLB et .blend en ~3 s. Rendus de contrôle : `blender.exe -b concept/ile_03/colonie_du_lagon.blend -P tools/blender/rendu_ville_haute.py -- [vues] --echantillons 24`, puis lire les PNG.
- Export vers `assets/models/*.glb`. Échelle : robot ~1,90 m, Semeurs 2,5–3 m (portes ~3 m).
- Style : low-poly à facettes, aplats, pas de textures peintes (voir DA.md).
