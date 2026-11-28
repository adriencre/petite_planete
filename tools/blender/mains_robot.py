"""Mains du robot vues en 1re personne : main droite (bobine du câble au poignet), main gauche, fiche.

Doigts fins articulés façon outil de jardinier : trois doigts et un pouce, trois phalanges chacun,
un os par phalange. Pièces rigides à facettes (chaque pièce suit un seul os).
Les poses des doigts sont des actions (une piste NLA chacune) : repos, ouverte, pincer.
« pincer » est calculée (chercher_prise) : la fiche, dans l'axe des doigts et broches en avant, est serrée
entre le coussinet de l'index posé dessus et le bout du pouce glissé dessous ; majeur et annulaire repliés.
Chaque main porte son avant-bras jusqu'au coude (rigide avec le poignet), qui sort du champ par le bas.

Repère Blender de la main : poignet à l'origine, doigts vers +Y (= -Z Godot), dos de la main vers +Z (= +Y Godot).
Exports : assets/models/mains/main_robot_d.glb, main_robot_g.glb, fiche_cable.glb,
et reperes_mains.json (repère Godot de la main : point de pince, sortie du câble, fiche au repos).

Exécution : Blender -b --python tools/blender/mains_robot.py [-- --rendu DOSSIER]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "assets/models/mains"

DOIGTS = ("index", "majeur", "annulaire")
# x de la base (main droite), longueurs des trois phalanges
GEOMETRIE = {
    "index": (-0.021, (0.030, 0.024, 0.019)),
    "majeur": (0.0, (0.032, 0.026, 0.020)),
    "annulaire": (0.021, (0.028, 0.022, 0.018)),
}
BASE_DOIGTS_Y = 0.072
POUCE_BASE = Vector((-0.031, 0.028, -0.006))
POUCE_DIR = Vector((-0.38, 0.84, -0.40)).normalized()
POUCE_LONG = (0.032, 0.026, 0.020)
RAYONS = (0.0068, 0.0060, 0.0052)
# la fiche au repos, couchée sur le dos du poignet droit, broches vers l'avant et un peu vers la main gauche
FICHE_REPOS = Vector((0.0, -0.014, 0.040))
FICHE_REPOS_LACET = -35.0   # degrés autour de l'axe vertical (Blender Z = Godot Y)
DEMI_HAUTEUR_FICHE = 0.009
# avant-bras : du raccord de la manchette jusqu'au coude, un peu vers le bas et vers l'extérieur
AVANT_BRAS_DEBUT = Vector((0.0, -0.100, 0.0))
AVANT_BRAS_LONG = 0.27
SORTIE_CABLE = Vector((0.0, -0.046, 0.040))

# Poses : os -> (rx, ry, rz) en degrés, main droite. rx < 0 replie le doigt vers la paume.
POSES = {
    "repos": {
        "index_1": (-14, 0, 2), "index_2": (-16, 0, 0), "index_3": (-10, 0, 0),
        "majeur_1": (-18, 0, 0), "majeur_2": (-20, 0, 0), "majeur_3": (-12, 0, 0),
        "annulaire_1": (-22, 0, -2), "annulaire_2": (-24, 0, 0), "annulaire_3": (-14, 0, 0),
        "pouce_1": (-8, 0, -6), "pouce_2": (-10, 0, 0), "pouce_3": (-8, 0, 0),
    },
    "ouverte": {
        "index_1": (-2, 0, 7), "index_2": (-3, 0, 0), "index_3": (-2, 0, 0),
        "majeur_1": (-3, 0, 0), "majeur_2": (-4, 0, 0), "majeur_3": (-2, 0, 0),
        "annulaire_1": (-4, 0, -7), "annulaire_2": (-4, 0, 0), "annulaire_3": (-3, 0, 0),
        "pouce_1": (6, 0, -16), "pouce_2": (0, 0, 0), "pouce_3": (0, 0, 0),
    },
    # l'index et le pouce de « pincer » sont calculés par chercher_prise()
    "pincer": {
        "majeur_1": (-62, 0, 0), "majeur_2": (-70, 0, 0), "majeur_3": (-45, 0, 0),
        "annulaire_1": (-70, 0, -3), "annulaire_2": (-78, 0, 0), "annulaire_3": (-50, 0, 0),
    },
}


def godot(v):
    """Vecteur Blender -> Godot."""
    return [round(v.x, 5), round(v.z, 5), round(-v.y, 5)]


def mat(nom, couleur, metal=0.0, rugosite=0.6):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.diffuse_color = (*couleur, 1)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*couleur, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rugosite
    return m


def palette():
    # mêmes teintes que la coque et les articulations du robot (joueur.tscn), passées en linéaire
    return {
        "coque": mat("Coque crème", (0.75, 0.49, 0.30), 0.35, 0.45),
        "sombre": mat("Graphite des articulations", (0.069, 0.060, 0.10), 0.2, 0.55),
        "bronze": mat("Bronze des bagues", (0.25, 0.15, 0.067), 0.63, 0.41),
        "laiton": mat("Laiton des broches", (0.83, 0.54, 0.20), 0.57, 0.26),
        "cable": mat("Câble vert", (0.15, 0.21, 0.10), 0.0, 0.7),
    }


# ---------------------------------------------------------------- pièces

def _finir(o, os_nom, matiere):
    o.data.materials.clear()
    o.data.materials.append(matiere)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    o.vertex_groups.new(name=os_nom).add(range(len(o.data.vertices)), 1.0, "REPLACE")
    return o


def prisme(a, b, r, os_nom, matiere, cotes=6, r2=None):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=cotes, radius1=r, radius2=r if r2 is None else r2,
                                    depth=(b - a).length, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return _finir(o, os_nom, matiere)


def bille(c, r, os_nom, matiere):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=c)
    return _finir(bpy.context.object, os_nom, matiere)


def boite(c, taille, os_nom, matiere, chanfrein=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c, rotation=rot)
    o = bpy.context.object
    o.scale = taille
    if chanfrein:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        biseau = o.modifiers.new("Arêtes taillées", "BEVEL")
        biseau.width = chanfrein
        biseau.segments = 1
    return _finir(o, os_nom, matiere)


def anneau(y, r, r_fil, os_nom, matiere, x=0.0, z=0.0):
    bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=5, major_radius=r,
                                     minor_radius=r_fil, location=(x, y, z), rotation=(math.pi / 2, 0, 0))
    return _finir(bpy.context.object, os_nom, matiere)


# ---------------------------------------------------------------- une main

def aligne(d):
    """Angles d'Euler qui couchent l'axe Y d'une pièce le long de d."""
    return d.to_track_quat("Y", "Z").to_euler()


def avant_bras(cote, m):
    """Avant-bras de robot jardinier : âme graphite à huit pans, coque crème sur le dessus et l'extérieur,
    deux vérins de laiton dessous (les tendons), bagues de bronze, coude en rotule."""
    d = Vector((0.12 * cote, -1.0, -0.45)).normalized()  # poignet un peu cassé : le bras descend vers le coude
    a = AVANT_BRAS_DEBUT
    b = a + d * AVANT_BRAS_LONG
    haut = Vector((0, 0, 1))
    cote_ext = Vector((cote, 0, 0))
    out = [prisme(a, b, 0.028, "poignet", m["sombre"], 8, 0.034)]
    # coque du dessus, en deux plaques, et plaque de l'extérieur
    for t0, t1, l in ((0.04, 0.50, 0.050), (0.54, 0.92, 0.058)):
        c = a + d * ((t0 + t1) / 2 * AVANT_BRAS_LONG) + haut * (0.027 + 0.008 * t0)
        out.append(boite(c, (l, (t1 - t0) * AVANT_BRAS_LONG, 0.014), "poignet", m["coque"], 0.005, aligne(d)))
    c = a + d * (0.48 * AVANT_BRAS_LONG) + cote_ext * 0.030 - haut * 0.004
    out.append(boite(c, (0.012, 0.66 * AVANT_BRAS_LONG, 0.034), "poignet", m["coque"], 0.004, aligne(d)))
    # vérins sous l'avant-bras, côté intérieur
    for dx in (-0.012, 0.004):
        p0 = a + d * 0.03 + Vector((dx * cote, 0, -0.030))
        p1 = a + d * (0.80 * AVANT_BRAS_LONG) + Vector((dx * cote, 0, -0.036))
        out.append(prisme(p0, p1, 0.0042, "poignet", m["laiton"], 6))
        out.append(prisme(p1 - (p1 - p0).normalized() * 0.05, p1 + d * 0.012, 0.0062, "poignet", m["sombre"], 6))
    # bagues de bronze et coude
    for t, r in ((0.02, 0.034), (0.52, 0.039), (0.96, 0.041)):
        c = a + d * (t * AVANT_BRAS_LONG)
        out.append(prisme(c - d * 0.005, c + d * 0.005, r, "poignet", m["bronze"], 8))
    out.append(bille(b + d * 0.020, 0.040, "poignet", m["sombre"]))
    out.append(prisme(b + d * 0.010 + haut * 0.030, b + d * 0.040 + haut * 0.030, 0.016, "poignet", m["coque"], 6))
    return out


def chaines(cote):
    """Articulations de chaque doigt (repos) : nom -> liste de 4 points (base, 2 jointures, bout)."""
    out = {}
    for d in DOIGTS:
        x, longs = GEOMETRIE[d]
        ecart = {"index": 0.06, "majeur": 0.0, "annulaire": -0.06}[d]  # doigts un peu en éventail
        direction = Vector((-ecart * cote, 1.0, 0.0)).normalized()
        p = Vector((x * cote, BASE_DOIGTS_Y, 0.0))
        pts = [p.copy()]
        for long in longs:
            p = p + direction * long
            pts.append(p.copy())
        out[d] = pts
    p = Vector((POUCE_BASE.x * cote, POUCE_BASE.y, POUCE_BASE.z))
    direction = Vector((POUCE_DIR.x * cote, POUCE_DIR.y, POUCE_DIR.z))
    pts = [p.copy()]
    for long in POUCE_LONG:
        p = p + direction * long
        pts.append(p.copy())
    out["pouce"] = pts
    return out


def squelette(nom, cote):
    donnees = bpy.data.armatures.new(nom)
    arm = bpy.data.objects.new(nom, donnees)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    racine = donnees.edit_bones.new("poignet")
    racine.head, racine.tail = (0, -0.03, 0), (0, 0.03, 0)
    for doigt, pts in chaines(cote).items():
        parent = racine
        for i in range(3):
            eb = donnees.edit_bones.new(f"{doigt}_{i + 1}")
            eb.head, eb.tail = pts[i], pts[i + 1]
            eb.parent = parent
            eb.use_connect = i > 0
            # axe Z de l'os vers le dos de la main : rx < 0 replie vers la paume
            eb.align_roll(Vector((0, 0, 1)) if doigt != "pouce" else Vector((cote * 0.5, 0.0, 1.0)))
            parent = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    return arm


def construire_main(nom, cote, m):
    """cote = 1 : main droite (pouce vers -X) ; -1 : main gauche (miroir)."""
    arm = squelette(nom, cote)
    pieces = []
    x = lambda v: (v[0] * cote, v[1], v[2])  # noqa: E731

    # paume : coque crème taillée sur le dos, semelle graphite dessous, barre de bronze aux jointures
    pieces.append(boite((0, 0.036, 0.002), (0.062, 0.064, 0.018), "poignet", m["coque"], 0.008))
    pieces.append(boite((0, 0.040, 0.012), (0.040, 0.040, 0.006), "poignet", m["coque"], 0.003))  # plaque du dos
    pieces.append(boite((0, 0.034, -0.009), (0.058, 0.056, 0.012), "poignet", m["sombre"], 0.003))
    pieces.append(boite((0, 0.066, 0.009), (0.062, 0.007, 0.007), "poignet", m["bronze"], 0.0015))
    pieces.append(boite(x((-0.027, 0.016, -0.005)), (0.020, 0.030, 0.016), "poignet", m["sombre"], 0.003))
    # poignet : rotule, bague de bronze, manchette crème jusqu'au raccord de l'avant-bras (Godot z = 0,10)
    pieces.append(bille((0, -0.006, 0), 0.018, "poignet", m["sombre"]))
    pieces.append(prisme((0, -0.020, 0), (0, -0.030, 0), 0.031, "poignet", m["bronze"], 8))
    pieces.append(prisme((0, -0.028, 0), (0, -0.106, 0), 0.027, "poignet", m["coque"], 8, 0.031))
    pieces += avant_bras(cote, m)
    if cote == 1:
        # la bobine du câble : deux flasques de bronze, des spires vertes, l'œillet de sortie, l'agrafe de la fiche
        for y in (-0.046, -0.094):
            pieces.append(prisme((0, y + 0.002, 0), (0, y - 0.002, 0), 0.043, "poignet", m["bronze"], 8))
        for i in range(6):
            pieces.append(anneau(-0.051 - i * 0.0074, 0.034, 0.0042, "poignet", m["cable"]))
        pieces.append(anneau(SORTIE_CABLE.y, 0.005, 0.0016, "poignet", m["bronze"], 0, SORTIE_CABLE.z))
        # agrafe de la fiche : un petit berceau graphite sous elle, dans son axe
        pieces.append(boite((0, -0.018, 0.030), (0.010, 0.018, 0.006), "poignet", m["sombre"], 0.0015,
                            (0, 0, math.radians(FICHE_REPOS_LACET))))
    else:
        pieces.append(prisme((0, -0.060, 0), (0, -0.066, 0), 0.032, "poignet", m["bronze"], 8))

    # doigts : phalanges graphite à six pans, jointures de bronze, plaques crème, bouts taillés en pointe d'outil
    for doigt, pts in chaines(cote).items():
        for i in range(3):
            a, b = pts[i], pts[i + 1]
            d = (b - a).normalized()
            os_nom = f"{doigt}_{i + 1}"
            pieces.append(bille(a, RAYONS[i] + 0.0012, os_nom, m["bronze"]))
            if i < 2:
                pieces.append(prisme(a + d * 0.004, b - d * 0.002, RAYONS[i], os_nom, m["sombre"]))
                if doigt != "pouce" or i == 0:
                    lacet = math.atan2(-d.x, d.y)
                    milieu = (a + b) / 2 + Vector((0, 0, RAYONS[i] * 0.85))
                    pieces.append(boite(milieu, (0.011, (b - a).length * 0.62, 0.004), os_nom,
                                        m["coque"], 0.0012, (0, 0, lacet)))
            else:
                coupe = b - d * 0.012
                pieces.append(prisme(a + d * 0.004, coupe, RAYONS[i], os_nom, m["sombre"]))
                pieces.append(prisme(coupe, b + d * 0.001, RAYONS[i] + 0.0006, os_nom, m["coque"], 5, 0.0026))

    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    corps = bpy.context.object
    corps.name = f"{nom}_corps"
    for poly in corps.data.polygons:
        poly.use_smooth = False
    corps.parent = arm
    corps.modifiers.new("Squelette", "ARMATURE").object = arm
    return arm


# ---------------------------------------------------------------- poses

def poser(arm, pose, cote):
    for pb in arm.pose.bones:
        rx, ry, rz = pose.get(pb.name, (0, 0, 0))
        pb.rotation_euler = Euler((math.radians(rx), math.radians(ry * cote), math.radians(rz * cote)))
    bpy.context.view_layer.update()


def bout(arm, nom):
    return arm.matrix_world @ arm.pose.bones[nom].tail


def coussinet(arm, nom):
    """Surface du coussinet d'une dernière phalange (côté paume)."""
    pb = arm.pose.bones[nom]
    p = pb.head.lerp(pb.tail, 0.70) - pb.z_axis * RAYONS[2]
    return arm.matrix_world @ p


def chercher_prise(arm, cote):
    """Pose de « pincer » et centre de la fiche (repère de la main) : la fiche dans l'axe des doigts,
    dessus contre le coussinet de l'index, dessous contre le bout du pouce. On essaie des courbures d'index
    et on garde celle que le pouce atteint le mieux (bouts du pouce précalculés : ils ne dépendent pas de l'index)."""
    base = dict(POSES["pincer"])
    pouces = []
    for rx1 in range(-40, 41, 5):
        for rz1 in range(-60, 31, 5):
            for rx2 in range(-50, 11, 5):
                essai = dict(base, pouce_1=(rx1, 0, rz1), pouce_2=(rx2, 0, 0), pouce_3=(rx2 * 0.7, 0, 0))
                poser(arm, essai, cote)
                pouces.append((bout(arm, "pouce_3"), essai))
    meilleur = None
    for i1 in range(-70, -4, 5):
        for i2 in range(-80, -4, 5):
            index = {"index_1": (i1, 0, 0), "index_2": (i2, 0, 0), "index_3": (i2 * 0.6, 0, 0)}
            poser(arm, dict(base, **index), cote)
            haut = coussinet(arm, "index_3")
            # la fiche ne doit pas rentrer dans la paume
            if haut.z > -0.012:
                continue
            for p, essai in pouces:
                # le pouce peut prendre la fiche un peu en avant ou en arrière de l'index (fiche longue de 34 mm)
                dy = max(-0.016, min(0.016, p.y - haut.y))
                cible = haut - Vector((0, -dy, 2 * DEMI_HAUTEUR_FICHE + RAYONS[2]))
                ecart = (p - cible).length
                cout = ecart + 0.00003 * (abs(i1) + abs(i2)) + 0.1 * abs(dy) ** 2
                if meilleur is None or cout < meilleur[0]:
                    centre = haut + Vector((0, dy / 2, -DEMI_HAUTEUR_FICHE))
                    meilleur = (cout, ecart, dict(essai, **index), centre)
    _, ecart, pose, centre = meilleur
    print(f"PRISE {arm.name}: écart pouce/fiche {ecart * 1000:.1f} mm, index={pose['index_1']}/{pose['index_2']}, "
          f"pouce_1={pose['pouce_1']} pouce_2={pose['pouce_2']}, fiche {tuple(round(v, 4) for v in centre)}")
    return pose, centre


def actions(arm, poses, cote):
    ad = arm.animation_data_create()
    for nom, pose in poses.items():
        act = bpy.data.actions.new(f"{nom}")
        ad.action = act
        poser(arm, pose, cote)
        for pb in arm.pose.bones:
            for f in (1, 6):
                pb.keyframe_insert("rotation_euler", frame=f)
        ad.action = None
        piste = ad.nla_tracks.new()
        piste.name = nom
        bande = piste.strips.new(nom, 1, act)
        if hasattr(bande, "action_slot") and getattr(act, "slots", None) and len(act.slots):
            bande.action_slot = act.slots[0]
    poser(arm, poses["repos"], cote)


def exporter(objets, fichier, anim):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objets:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objets[0]
    options = dict(export_animation_mode="NLA_TRACKS", export_force_sampling=True) if anim else dict(export_animations=False)
    bpy.ops.export_scene.gltf(filepath=str(SORTIE / fichier), export_format="GLB", use_selection=True,
                              export_apply=False, **options)


def construire_fiche(m):
    """Fiche à deux broches : corps graphite, collerette de bronze, broches de laiton vers +Y, gaine verte."""
    pieces = [
        boite((0, 0, 0), (0.014, 0.034, 2 * DEMI_HAUTEUR_FICHE), "fiche", m["sombre"], 0.003),
        boite((0, 0.018, 0), (0.017, 0.004, 0.021), "fiche", m["bronze"], 0.001),
        boite((0, 0.028, 0.0045), (0.003, 0.018, 0.003), "fiche", m["laiton"]),
        boite((0, 0.028, -0.0045), (0.003, 0.018, 0.003), "fiche", m["laiton"]),
        prisme((0, -0.017, 0), (0, -0.030, 0), 0.0055, "fiche", m["cable"], 6, 0.004),
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = "Fiche"
    o.vertex_groups.clear()
    for poly in o.data.polygons:
        poly.use_smooth = False
    return o


def rendu(dossier, arm_d, arm_g, poses_d, poses_g):
    """Planches de contrôle : chaque pose, main droite et main gauche côte à côte, vue de trois quarts."""
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_WORKBENCH"
    except TypeError as e:
        print("MOTEUR", e)
    sc.world = bpy.data.worlds.new("Fond de contrôle")
    sc.world.color = (0.45, 0.47, 0.52)
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_cavity = True
    sc.render.resolution_x, sc.render.resolution_y = 900, 520
    arm_d.location, arm_g.location = (0.07, 0, 0), (-0.07, 0, 0)
    arm_d.animation_data.use_nla = arm_g.animation_data.use_nla = False  # sinon les pistes écrasent la pose
    cam = bpy.data.objects.new("Caméra de contrôle", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 50
    cam.data.clip_start = 0.005
    vues = {"dessus": ((0.04, -0.06, 0.34), (0, 0.05, 0)), "cote": ((0.36, 0.06, 0.0), (0, 0.05, -0.01)),
            "face": ((0.0, 0.40, 0.08), (0, 0.05, 0)), "joueur": ((-0.10, -0.42, 0.20), (0, 0.06, 0)),
            "prise": ((0.05, 0.16, -0.16), (-0.07, 0.08, -0.04)), "loin": ((0.25, -0.55, 0.45), (0, -0.08, 0))}
    for nom_pose in poses_d:
        poser(arm_d, poses_d[nom_pose], 1)
        poser(arm_g, poses_g[nom_pose], -1)
        for nom_vue, (oeil, cible) in vues.items():
            cam.location = oeil
            cam.rotation_euler = (Vector(cible) - Vector(oeil)).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = str(Path(dossier) / f"main_{nom_pose}_{nom_vue}.png")
            bpy.ops.render.render(write_still=True)
    arm_d.location = arm_g.location = (0, 0, 0)
    arm_d.animation_data.use_nla = arm_g.animation_data.use_nla = True


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    SORTIE.mkdir(parents=True, exist_ok=True)
    m = palette()
    reperes = {}
    mains = {}
    for cote, nom, fichier in ((1, "MainDroite", "main_robot_d.glb"), (-1, "MainGauche", "main_robot_g.glb")):
        arm = construire_main(nom, cote, m)
        poses = {k: dict(v) for k, v in POSES.items()}
        poses["pincer"], pince = chercher_prise(arm, cote)
        actions(arm, poses, cote)
        mains[cote] = (arm, poses, pince)
        reperes[nom] = {"pince": godot(pince)}
        print(f"REPERE {nom}: pince (Godot) = {godot(pince)}")
    reperes["MainDroite"]["sortie_cable"] = godot(SORTIE_CABLE)
    reperes["MainDroite"]["fiche_repos"] = godot(FICHE_REPOS)
    reperes["MainDroite"]["fiche_repos_lacet"] = FICHE_REPOS_LACET
    (SORTIE / "reperes_mains.json").write_text(json.dumps(reperes, indent=1, ensure_ascii=False))

    for cote, fichier in ((1, "main_robot_d.glb"), (-1, "main_robot_g.glb")):
        arm = mains[cote][0]
        exporter([arm] + list(arm.children), fichier, True)
    fiche = construire_fiche(m)
    exporter([fiche], "fiche_cable.glb", False)

    if "--rendu" in args:
        # fiche tenue par la main gauche, pour juger la prise
        fiche.location = mains[-1][2] + Vector((-0.07, 0, 0))
        rendu(args[args.index("--rendu") + 1], mains[1][0], mains[-1][0], mains[1][1], mains[-1][1])
    print("MAINS EXPORTÉES dans", SORTIE)


if __name__ == "__main__":
    main()
