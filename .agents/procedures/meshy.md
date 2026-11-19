# Meshy — génération de modèles 3D

- **Ça coûte des crédits** : toujours annoncer le coût et attendre l'accord de l'utilisateur avant un appel payant. `meshy_check_balance` est gratuit.
- La clé est lue depuis la variable d'environnement `MESHY_API_KEY` (jamais écrite dans le repo).
- Recette qui a marché pour le robot (2026-11-16) : image-to-3D `meshy-t2.5` (smart topology, `target_polycount`) + texture `meshy-n1`, pose en T, puis `meshy_rig`.
- Les sorties rig/animation sont des GLB séparés (un clip chacun) et **ne sont pas enregistrées par `meshy_download_model`** : télécharger les URL avec curl.
- Fusion des clips dans Blender : scène à 30 fps, même `bone_heuristic` à chaque import, une piste NLA par clip, export `NLA_TRACKS` → `assets/models/robot_meshy.glb` (clips `attente` / `marche` / `course`). Script : `tools/blender/robot_ajouter_clips.py`.
- Si un appel de création échoue (timeout, 5xx), vérifier `meshy_list_tasks` avant de relancer : la tâche a peut-être été créée et facturée.
