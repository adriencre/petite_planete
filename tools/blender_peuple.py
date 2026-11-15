# Le petit peuple de l'ombre, modélisé dans Blender (à exécuter après blender_kit.py).
# Tous partagent la même ossature (Corps, Tete, BrasG, BrasD, PiedG, PiedD) → mêmes animations.
# Les pivots s'appellent « Corps_<Nom> »… pour rester uniques dans le fichier Blender.

ENFANT = dict(robe=(0.27, 0.16, 0.44), neck=0.6, head=(0.31, 0.84), shoulder=(0.19, 0.47), arm=0.24, lean=0.0)
ADULTE = dict(robe=(0.3, 0.17, 0.62), neck=0.78, head=(0.27, 1.0), shoulder=(0.2, 0.64), arm=0.34, lean=0.0)


def villageois(name, base, robe_mat, scale=1.0, eyes="ronds", cheeks=True, lean=0.0, extra=None):
    k = Kit(name)
    R = lambda n: n + "_" + name
    r1, r2, rh = base["robe"]
    nz = base["neck"]
    hr, hz = base["head"]
    sx, sz = base["shoulder"]
    corps = k.empty(R("Corps"), (0, 0, 0.12))
    tete = k.empty(R("Tete"), (0, -lean, nz), corps)
    bg = k.empty(R("BrasG"), (sx, -lean * 0.5, sz), corps)
    bd = k.empty(R("BrasD"), (-sx, -lean * 0.5, sz), corps)
    pg = k.empty(R("PiedG"), (0.09 * r1 / 0.27, -0.03, 0.045))
    pd = k.empty(R("PiedD"), (-0.09 * r1 / 0.27, -0.03, 0.045))
    # pieds
    for p in (pg, pd):
        k.ball("peau_ombre", p.location, 0.075 * r1 / 0.27, (1, 1.35, 0.6), seg=8, rings=5, parent=p)
    # robe (légèrement penchée vers l'avant si le personnage est voûté)
    k.cone(robe_mat, (0, -lean * 0.3, 0.08 + rh / 2), r1, r2, rh, rot=(-math.degrees(lean) * 0.8, 0, 0), v=9, parent=corps, name=R("Robe"))
    k.ring(robe_mat if robe_mat != "tissu_rouille" else "tissu_ocre", (0, 0, 0.1), r1 - 0.015, 0.03, parent=corps)
    k.ico("lueur", (0, -r2 - 0.04 - lean * 0.5, 0.08 + rh * 0.62), 0.045, parent=corps, name=R("Coeur"))
    # bras + mains
    arm = base["arm"]
    for b, s in ((bg, 1), (bd, -1)):
        x0, _, z0 = b.location
        k.cone("peau_ombre", (x0 + 0.06 * s, b.location[1], z0 - arm / 2 + 0.02), 0.045, 0.035, arm, rot=(0, -25 * s, 0), v=6, parent=b)
        k.ball("peau_ombre", (x0 + 0.11 * s, b.location[1] - 0.01, z0 - arm + 0.01), 0.05, seg=7, rings=5, parent=b)
    # tête
    hy = -lean
    k.ico("peau_ombre", (0, hy, hz), hr, (1.0, 0.94, 0.9), sub=2, parent=tete, name=R("Crane"))
    ey = hy - hr * 0.82
    for s in (1, -1):
        x = 0.1 * s * hr / 0.31
        if eyes == "ronds":
            k.ball("oeil", (x, ey, hz), 0.075 * hr / 0.31, (0.85, 0.45, 1.15), seg=10, rings=6, parent=tete)
            k.ball("reflet", (x + 0.022, ey - 0.035, hz + 0.035), 0.022, seg=6, rings=4, parent=tete)
        elif eyes == "plisses":  # yeux mi-clos, bienveillants
            k.ball("oeil", (x, ey + 0.01, hz - 0.01), 0.07 * hr / 0.31, (0.95, 0.4, 0.45), seg=10, rings=6, parent=tete)
        elif eyes == "petits":
            k.ball("oeil", (x, ey, hz + 0.01), 0.05 * hr / 0.31, (0.9, 0.5, 1.0), seg=8, rings=5, parent=tete)
        if cheeks:
            k.ball("joue", (x * 1.75, ey + 0.035, hz - 0.09 * hr / 0.31), 0.045 * hr / 0.31, (1, 0.4, 0.7), seg=8, rings=4, parent=tete)
    # sourire
    m = k.ring("lueur_douce", (0, ey - 0.012, hz - 0.115 * hr / 0.31), 0.035 * hr / 0.31, 0.009, rot=(90, 0, 0), M=10, mm=4, parent=tete, name=R("Bouche"))
    bm = bmesh.new(); bm.from_mesh(m.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.002], context="VERTS")
    bm.to_mesh(m.data); bm.free()
    m.scale = (1.4, 1, 1)
    # veines lumineuses
    for j, (x, y, z) in enumerate([(0.78, 0.4, 0.35), (-0.8, 0.3, 0.25), (0.45, -0.3, 0.75), (-0.3, -0.55, 0.7)]):
        k.ico("lueur_douce", (x * hr, hy + y * hr, hz + z * hr), 0.018, parent=tete)
    ctx = dict(k=k, corps=corps, tete=tete, bg=bg, bd=bd, hr=hr, hz=hz, hy=hy, ey=ey, rh=rh, r1=r1, r2=r2, R=R)
    if extra:
        extra(**ctx)
    k.root.scale = (scale, scale, scale)  # à la fin : les pièces suivent leur racine
    return k


# ---------------------------------------------------------------- accessoires
def acc_enfant(k, corps, tete, hr, hz, hy, R, **_):
    k.ring("tissu_rouille", (0, 0, 0.53), 0.16, 0.055, parent=corps, name=R("Echarpe"))
    k.box("tissu_rouille", (0.1, -0.15, 0.4), (0.14, 0.05, 0.4), rot=(8, 0, -14), parent=corps)
    k.ball("tissu_ocre", (0.13, -0.16, 0.29), 0.03, (1, 0.6, 1), seg=6, rings=4, parent=corps)
    p = k.empty(R("Pousse"), (0.02, 0.02, hz + hr * 0.93), tete)
    k.cone("fougere", (0.02, 0.02, hz + hr + 0.04), 0.018, 0.012, 0.12, rot=(0, -12, 0), v=5, parent=p)
    k.cone("fougere", (0.045, 0.02, hz + hr + 0.13), 0.012, 0.008, 0.08, rot=(0, -35, 0), v=5, parent=p)
    k.box("fougere", (-0.04, 0.02, hz + hr + 0.08), (0.18, 0.024, 0.08), rot=(0, 40, 0), parent=p)
    k.ico("lueur", (0.075, 0.02, hz + hr + 0.17), 0.04, parent=p)


def acc_petite(k, corps, tete, hr, hz, R, **_):
    # bébé : un chapeau-feuille et un bourgeon
    p = k.empty(R("Pousse"), (0, 0, hz + hr * 0.9), tete)
    k.cone("fougere", (0, 0, hz + hr * 0.95), hr * 0.9, 0.0, 0.16, v=7, parent=p)
    k.ico("lueur_rose", (0, 0, hz + hr * 0.95 + 0.1), 0.05, parent=p)


def acc_ancienne(k, corps, tete, bg, hr, hz, hy, R, **_):
    # capuche, châle, lunettes, bâton à lueur ambrée
    k.lathe("tissu_prune", [(hr * 1.08, hz - hr * 0.35), (hr * 1.12, hz), (hr * 0.95, hz + hr * 0.6), (hr * 0.5, hz + hr * 0.98), (0.0, hz + hr * 1.08)],
            seg=10, loc=(0, hy + 0.05, 0), parent=tete, name=R("Capuche"))
    k.cone("tissu_mousse", (0, -0.03, 0.66), 0.27, 0.13, 0.16, v=9, parent=corps)
    for s in (1, -1):
        k.ring("lueur_douce", (0.085 * s * hr / 0.27 * 1.1, hy - hr * 0.95, hz + 0.0), 0.05, 0.008, rot=(90, 0, 0), M=10, mm=3, parent=tete)
    k.box("lueur_douce", (0, hy - hr * 0.97, hz + 0.01), (0.05, 0.008, 0.008), parent=tete)
    x0, y0, z0 = bg.location
    k.cyl("bois_nuit", (x0 + 0.15, y0 - 0.12, 0.5), 0.022, 1.0, rot=(4, -4, 0), v=5, parent=bg, name=R("Baton"))
    k.ico("lueur_ambre", (x0 + 0.13, y0 - 0.15, 1.04), 0.065, parent=bg)
    k.ring("bois_nuit", (x0 + 0.13, y0 - 0.15, 1.04), 0.07, 0.012, rot=(0, 90, 0), M=8, mm=3, parent=bg)


def acc_pecheur(k, corps, tete, bd, hr, hz, hy, ey, R, **_):
    # grand chapeau de pluie, barbe, canne à pêche avec appât lumineux, gilet
    k.cyl("tissu_ocre", (0, hy, hz + hr * 0.62), hr * 1.65, 0.05, v=12, parent=tete, name=R("Bord"))
    k.lathe("tissu_ocre", [(hr * 0.9, hz + hr * 0.62), (hr * 0.85, hz + hr * 1.05), (hr * 0.55, hz + hr * 1.25), (0.0, hz + hr * 1.28)], seg=10, loc=(0, hy, 0), parent=tete)
    k.ico("champi_pied", (0, ey + 0.1, hz - hr * 0.62), 0.15, (1.15, 0.8, 0.85), parent=tete, name=R("Barbe"))
    k.cone("tissu_rouille", (0, -0.01, 0.48), 0.3, 0.2, 0.22, v=9, parent=corps)
    x0, y0, z0 = bd.location
    hand = (x0 - 0.11, y0 - 0.02, z0 - 0.33)
    tip = (x0 - 0.12, y0 - 0.95, 1.35)
    k.stick("bois_nuit", hand, tip, 0.016, parent=bd, name=R("Canne"))
    k.stick("lueur_douce", tip, (tip[0], tip[1], 0.7), 0.006, v=4, parent=bd)
    k.ico("lueur", (tip[0], tip[1], 0.66), 0.045, parent=bd)
    k.cyl("tissu_sable", (0.28, 0.02, 0.32), 0.1, 0.18, v=7, parent=corps)  # bourriche


def acc_jardiniere(k, corps, tete, bg, hr, hz, hy, R, **_):
    k.box("tissu_rouille", (0, -0.24, 0.3), (0.26, 0.03, 0.3), rot=(-14, 0, 0), parent=corps, name=R("Tablier"))
    k.ring("tissu_rouille", (0, 0, 0.47), 0.215, 0.02, M=12, mm=3, parent=corps)
    k.lathe("tissu_mousse", [(hr * 1.03, hz + hr * 0.42), (hr * 0.95, hz + hr * 0.65), (hr * 0.5, hz + hr * 0.97), (0.0, hz + hr * 1.04)], seg=10, loc=(0, hy + 0.02, 0), parent=tete)
    k.ball("tissu_mousse", (0, hy + hr * 0.95, hz + hr * 0.1), 0.07, seg=6, rings=4, parent=tete)  # nœud du fichu
    x0, y0, z0 = bg.location
    k.cyl("tissu_sable", (x0 + 0.14, y0 - 0.05, z0 - 0.42), 0.13, 0.13, v=8, parent=bg, name=R("Panier"))
    k.ring("tissu_sable", (x0 + 0.14, y0 - 0.05, z0 - 0.3), 0.1, 0.012, rot=(90, 0, 90), M=10, mm=3, parent=bg)
    for j in range(3):
        k.ball(["lueur", "lueur_violette", "lueur_rose"][j], (x0 + 0.1 + 0.04 * j, y0 - 0.05 + 0.03 * (j - 1), z0 - 0.33), 0.045, (1, 1, 0.6), seg=6, rings=4, parent=bg)
    k.cyl("bois_nuit", (-0.2, 0.18, 0.55), 0.015, 0.7, rot=(0, -15, 0), v=5, parent=corps)  # râteau dans le dos
    k.box("bois_nuit", (-0.29, 0.18, 0.9), (0.2, 0.03, 0.03), rot=(0, -15, 0), parent=corps)


def acc_tisserand(k, corps, tete, bg, bd, hr, hz, hy, R, **_):
    # une grosse bobine de fil lumineux sur le dos, un mètre de fil autour du cou, un bonnet
    k.cyl("bois_nuit", (0, 0.32, 0.62), 0.12, 0.3, rot=(0, 90, 0), v=8, parent=corps)
    k.cyl("lueur_violette", (0, 0.32, 0.62), 0.1, 0.24, rot=(0, 90, 0), v=10, parent=corps, name=R("Bobine"))
    k.ring("lueur_douce", (0, 0, 0.72), 0.17, 0.012, M=14, mm=3, parent=corps)
    k.box("lueur_douce", (0.1, -0.17, 0.55), (0.01, 0.01, 0.3), parent=corps)
    k.lathe("tissu_ocre", [(hr * 0.98, hz + hr * 0.3), (hr * 0.85, hz + hr * 0.8), (hr * 0.4, hz + hr * 1.1), (0.0, hz + hr * 1.15)], seg=10, loc=(0, hy, 0), parent=tete)
    k.ico("tissu_rouille", (0, hy, hz + hr * 1.18), 0.06, parent=tete)
    x0, y0, z0 = bd.location
    k.cyl("bois_nuit", (x0 - 0.12, y0 - 0.12, z0 - 0.3), 0.012, 0.3, rot=(30, 0, 20), v=4, parent=bd)  # aiguille


def acc_compteur(k, corps, tete, bg, hr, hz, hy, ey, R, **_):
    # le vieux Compteur : masque de héron (long bec), longue robe, sacoche de pierres, bâton
    k.cone("champi_pied", (0, ey - 0.2, hz - 0.03), 0.07, 0.005, 0.42, rot=(95, 0, 0), v=6, parent=tete, name=R("Bec"))
    k.lathe("champi_pied", [(hr * 1.02, hz - hr * 0.2), (hr * 1.05, hz + hr * 0.3), (hr * 0.7, hz + hr * 0.85), (0.0, hz + hr * 1.0)], seg=10, loc=(0, hy + 0.03, 0), parent=tete, name=R("Masque"))
    for j in range(3):  # plumes
        k.box("tissu_nuit", (0.03 * (j - 1), hy + hr * 0.7, hz + hr * 0.95 + 0.05 * j), (0.03, 0.1, 0.18), rot=(-35 - 10 * j, 0, 10 * (j - 1)), parent=tete)
    k.cyl("tissu_sable", (0.28, -0.05, 0.42), 0.12, 0.16, v=8, parent=corps, name=R("Sacoche"))
    for j in range(4):
        k.ico("lueur", (0.25 + 0.04 * (j % 2), -0.1 + 0.03 * j, 0.52), 0.035, parent=corps)
    x0, y0, z0 = bg.location
    k.cyl("bois_nuit", (x0 + 0.14, y0 - 0.1, 0.62), 0.025, 1.3, v=5, parent=bg)
    k.ring("champi_pied", (x0 + 0.14, y0 - 0.1, 1.28), 0.06, 0.02, rot=(90, 0, 0), M=8, mm=3, parent=bg)


def build_peuple():
    villageois("Enfant", ENFANT, "tissu_ocre", 1.0, extra=acc_enfant)
    villageois("Petite", ENFANT, "lueur_douce", 0.55, eyes="ronds", extra=acc_petite)
    villageois("Ancienne", ADULTE, "tissu_prune", 1.05, eyes="plisses", lean=0.08, extra=acc_ancienne)
    villageois("Pecheur", ADULTE, "tissu_mousse", 1.15, eyes="petits", extra=acc_pecheur)
    villageois("Jardiniere", ADULTE, "tissu_sable", 1.1, extra=acc_jardiniere)
    villageois("Tisserand", ADULTE, "tissu_prune", 1.1, eyes="petits", extra=acc_tisserand)
    villageois("Compteur", ADULTE, "tissu_nuit", 1.32, eyes="plisses", cheeks=False, lean=0.1, extra=acc_compteur)
