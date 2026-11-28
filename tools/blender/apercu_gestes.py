"""Aperçu d'un geste des mains en 1re personne, sans lancer Godot.

Construit les mains (mains_robot.py), les place à chaque échantillon écrit par
`python3 tools/godot/gestes_mains.py --echantillons E.json`, et rend la vue de la caméra du joueur
(champ vertical 52°, celui des mains levées) avec le câble entre la bobine et la fiche.

Exécution : Blender -b --python tools/blender/apercu_gestes.py -- E.json DOSSIER
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mains_robot as M  # noqa: E402

# Godot -> Blender : (x, y, z) -> (x, -z, y)
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def placer(objet, m_godot):
    objet.matrix_world = C @ Matrix(m_godot) @ C.inverted()


def cable(debut, fin, matiere):
    milieu = (debut + fin) / 2 + Vector((0, 0, -0.22 * (fin - debut).length))
    courbe = bpy.data.curves.new("câble", "CURVE")
    courbe.dimensions, courbe.bevel_depth = "3D", 0.0055
    sp = courbe.splines.new("POLY")
    pts = [debut * (1 - t) ** 2 + milieu * 2 * (1 - t) * t + fin * t * t for t in (i / 16 for i in range(17))]
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1)
    o = bpy.data.objects.new("câble", courbe)
    o.data.materials.append(matiere)
    bpy.context.scene.collection.objects.link(o)
    return o


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    echantillons, dossier = json.loads(Path(args[0]).read_text()), Path(args[1])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m = M.palette()
    d = M.construire_main("MainDroite", 1, m)
    g = M.construire_main("MainGauche", -1, m)
    poses_g = {k: dict(v) for k, v in M.POSES.items()}
    poses_g["pincer"] = M.chercher_prise(g, -1)[0]
    M.poser(d, M.POSES["repos"], 1)
    fiche = M.construire_fiche(m)

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light, sc.display.shading.color_type = "STUDIO", "MATERIAL"
    sc.world = bpy.data.worlds.new("fond")
    sc.world.color = (0.55, 0.6, 0.5)
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    cam = bpy.data.objects.new("œil", bpy.data.cameras.new("œil"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cam.data.sensor_fit, cam.data.angle, cam.data.clip_start = "VERTICAL", math.radians(52), 0.05

    sortie = Vector(M.SORTIE_CABLE)
    for e in echantillons:
        placer(d, e["MainDroite"])
        placer(g, e["MainGauche"])
        placer(fiche, e["Fiche"])
        M.poser(g, poses_g[e["pose_g"]], -1)
        bpy.context.view_layer.update()
        c = cable(d.matrix_world @ sortie, fiche.matrix_world @ Vector((0, -0.03, 0)), m["cable"])
        sc.render.filepath = str(dossier / f"geste_{int(e['t'] * 100):03d}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(c)


if __name__ == "__main__":
    main()
