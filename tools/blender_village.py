# Maisons, objets du village et nature du monde de l'ombre (à exécuter après blender_kit.py).
# Convention : la façade regarde vers -y (l'avant dans Godot).


# ---------------------------------------------------------------- maisons
def maison_champignon():
    k = Kit("MaisonChampignon")
    k.lathe("champi_pied", [(0.92, 0.0), (0.88, 0.25), (0.82, 0.8), (0.75, 1.3), (0.66, 1.62), (0.0, 1.62)], 12)
    k.lathe("pierre_nuit", [(1.12, 0.0), (1.12, 0.1), (1.0, 0.18), (0.9, 0.18)], 12, cap=True)
    prof = [(0.62, 1.55), (1.5, 1.6), (1.68, 1.74), (1.62, 1.92), (1.42, 2.2), (1.1, 2.5), (0.65, 2.72), (0.0, 2.8)]
    k.lathe("champi_chapeau", prof, 14, name="Chapeau")
    k.lathe("lueur_douce", [(0.64, 1.53), (1.48, 1.58)], 14)
    top = prof[2:]

    def zat(r):
        for (r1, z1), (r2, z2) in zip(top, top[1:]):
            if r2 <= r <= r1:
                return z2 + (z1 - z2) * (r - r2) / (r1 - r2)
        return prof[-1][1]
    for j, (a, r, s) in enumerate([(15, 1.25, 0.2), (75, 1.5, 0.15), (140, 0.85, 0.18), (205, 1.35, 0.22), (260, 1.58, 0.13),
                                    (310, 0.6, 0.16), (350, 1.52, 0.12), (110, 0.25, 0.14), (175, 1.6, 0.12), (40, 0.7, 0.12)]):
        p = k.around(r, a, zat(r) + 0.01)
        k.ico("lueur", p, s, (1, 1, 0.35), rot=(0, math.degrees(math.atan2(r, 2.0) * 0.9), a - 90))
    k.door(0, 0.82, 0.46, 0.72, 0.18)
    k.window(58, 1.1, 0.79)
    k.window(-62, 0.95, 0.8, 0.13)
    k.window(180, 1.15, 0.78, 0.15)
    k.lathe("pierre_nuit", [(0.16, 1.9), (0.14, 2.75), (0.19, 2.78), (0.19, 2.88), (0.0, 2.88)], 7, loc=(0.75, 0.55, 0))
    k.box("pierre_nuit", (0, -1.12, 0.06), (0.68, 0.32, 0.12))
    k.box("pierre_nuit", (0, -1.36, 0.03), (0.6, 0.24, 0.06))
    k.box("tissu_rouille", (0, -0.98, 0.185), (0.48, 0.2, 0.02))
    k.lantern((0.6, -0.95, 0.85), arm=0.3, ang=0)
    k.mini_mushrooms([(*k.around(r, a, 0)[:2], h, s) for a, r, h, s in [(-40, 1.05, 0.18, 0.08), (-30, 1.15, 0.12, 0.06), (100, 1.0, 0.22, 0.1), (125, 1.12, 0.14, 0.07), (230, 1.05, 0.16, 0.08)]], 0.1)
    return k


def maison_souche():
    k = Kit("MaisonSouche")
    k.lathe("ecorce", [(1.0, 0.0), (0.92, 0.2), (0.86, 0.8), (0.84, 1.5), (0.88, 1.7), (0.0, 1.7)], 9, wobble=0.12, seed=3)
    for j in range(6):  # racines
        a = j * 60 + 20
        p = k.around(1.0, a, 0.12)
        k.box("ecorce", p, (0.3, 0.75, 0.3), rot=(20, 0, a))
    k.lathe("toit_mousse", [(1.15, 1.62), (1.2, 1.7), (0.85, 2.2), (0.4, 2.65), (0.12, 2.9), (0.0, 2.95)], 9, twist=0.15, wobble=0.08, seed=4, name="Toit")
    k.ico("lueur", (0, 0, 3.0), 0.09)
    for j in range(8):  # mousse lumineuse qui pend du toit
        a = j * 45 + 10
        p = k.around(1.12, a, 1.55)
        k.cone("fougere", p, 0.05, 0.0, 0.2 + 0.08 * (j % 3), rot=(180, 0, 0), v=5)
    k.door(10, 0.86, 0.44, 0.7, 0.05)
    k.window(-55, 1.15, 0.86, 0.16, glass="fenetre_ambre")
    k.window(80, 1.25, 0.86, 0.13)
    k.window(200, 1.0, 0.86, 0.14, glass="fenetre_ambre")
    # balcon et échelle
    p = k.around(0.95, 80, 1.0)
    k.box("bois_nuit", p, (0.9, 0.45, 0.06), rot=(0, 0, 80))
    for s in (-1, 1):
        q = k.around(1.15, 80 + s * 22, 1.15)
        k.box("bois_nuit", q, (0.04, 0.04, 0.3))
    for s in (-0.18, 0.18):
        k.box("bois_nuit", (0.9 + 0.0, -0.95 + s, 0.65), (0.04, 0.04, 1.3), rot=(0, -12, 0))
    for j in range(5):
        k.box("bois_nuit", (0.85 + 0.03 * j, -0.95, 0.15 + j * 0.25), (0.05, 0.42, 0.04), rot=(0, -12, 0))
    k.lantern((-0.55, -0.95, 1.2), "lueur_ambre", arm=0.25, ang=180)
    k.mini_mushrooms([(*k.around(r, a, 0)[:2], h, s) for a, r, h, s in [(150, 1.15, 0.2, 0.1), (165, 1.3, 0.12, 0.06), (290, 1.2, 0.16, 0.08)]])
    return k


def maison_coquillage():
    k = Kit("MaisonCoquillage")
    y, r = 0.0, 1.05
    for j in range(5):
        h = 0.44 - j * 0.04
        off = (0.09 * math.sin(j * 1.4), 0.09 * math.cos(j * 1.4))
        k.lathe("coquille" if j % 2 == 0 else "coquille_raie", [(r, y), (r * 1.02, y + h * 0.4), (r * 0.82, y + h), (0.0, y + h)],
                11, loc=(off[0], off[1], 0), twist=0.1, cap=True)
        y += h
        r *= 0.78
    k.cone("coquille", (0.05, 0.05, y + 0.22), r, 0.0, 0.45, v=9)
    k.ico("lueur_violette", (0.05, 0.05, y + 0.5), 0.12, sub=2)
    k.door(20, 0.96, 0.42, 0.6, 0.0)
    k.window(-60, 0.95, 0.75, 0.12)
    k.window(140, 0.6, 0.98, 0.13)
    for j, a in enumerate([70, 110, 250, 300]):  # algues
        p = k.around(1.05, a, 0.25)
        k.cone("lueur_douce", p, 0.06, 0.0, 0.55, rot=(12, 0, a), v=5)
    for j, a in enumerate([40, 175, 330]):  # petits coquillages
        p = k.around(1.25, a, 0.05)
        k.cone("coquille_raie", p, 0.1, 0.0, 0.16, v=7)
    k.lantern((0.62, -0.95, 0.75), "lueur_violette", arm=0.25)
    return k


def maison_pilotis():
    """la cabane sur pilotis de la crique (le Compteur, le pêcheur)"""
    k = Kit("MaisonPilotis")
    for x in (-0.85, 0.85):
        for y in (-0.7, 0.7):
            k.cyl("ecorce", (x, y, 0.4), 0.08, 1.0, v=6)
    k.box("bois_nuit", (0, 0, 0.92), (2.1, 1.8, 0.12))
    k.box("champi_pied", (0, 0.1, 1.45), (1.6, 1.3, 0.95))
    for j in range(5):  # planches
        k.box("bois_nuit", (-0.65 + j * 0.325, -0.56, 1.45), (0.04, 0.03, 0.95))
    # toit de mousse à deux pans
    for s in (-1, 1):
        k.box("toit_mousse", (s * 0.48, 0.1, 2.15), (1.15, 1.6, 0.1), rot=(0, s * 32, 0))
    k.box("toit_mousse", (0, 0.1, 2.48), (0.12, 1.65, 0.12))
    for j in range(6):
        k.cone("fougere", (-0.95 + 0.38 * j, -0.7, 1.82), 0.05, 0.0, 0.22, rot=(180, 0, 0), v=5)
    # porte et fenêtres
    k.box("ecorce", (0.3, -0.58, 1.35), (0.42, 0.04, 0.75))
    k.box("bois_nuit", (0.3, -0.6, 1.35), (0.36, 0.04, 0.68))
    k.cyl("fenetre_ambre", (-0.4, -0.59, 1.55), 0.15, 0.05, rot=(90, 0, 0), v=10)
    k.ring("ecorce", (-0.4, -0.61, 1.55), 0.17, 0.03, rot=(90, 0, 0), M=12)
    # échelle, ponton, filets avec flotteurs lumineux
    for s in (-0.17, 0.17):
        k.box("bois_nuit", (0.3 + s, -1.2, 0.45), (0.04, 0.04, 1.0), rot=(-28, 0, 0))
    for j in range(4):
        k.box("bois_nuit", (0.3, -1.38 + j * 0.13, 0.1 + j * 0.24), (0.38, 0.04, 0.04), rot=(-28, 0, 0))
    k.box("bois_nuit", (1.5, -0.4, 0.86), (1.2, 0.6, 0.06))
    for x in (1.0, 2.0):
        k.cyl("ecorce", (x, -0.4, 0.4), 0.06, 0.9, v=6)
    for j in range(5):
        k.ico("lueur", (1.2 + 0.18 * j, -0.12, 1.0 + 0.1 * math.sin(j)), 0.05)
        k.box("corde", (1.2 + 0.18 * j, -0.12, 1.3), (0.01, 0.01, 0.55))
    k.box("corde", (1.55, -0.12, 1.58), (0.9, 0.02, 0.02))
    k.lantern((0.8, -0.75, 1.75), "lueur_ambre", arm=0.25)
    k.cyl("pierre_nuit", (-0.6, 0.6, 2.4), 0.1, 0.6, v=6)  # tuyau de poêle
    return k


def tour_ancienne():
    k = Kit("TourAncienne")
    k.lathe("pierre_nuit", [(1.0, 0.0), (0.95, 0.6), (0.85, 0.7), (0.0, 0.7)], 9, wobble=0.06, seed=7)
    k.lathe("champi_pied", [(0.72, 0.7), (0.66, 1.6), (0.6, 2.6), (0.62, 2.7), (0.0, 2.7)], 10)
    k.lathe("champi_chapeau_violet", [(0.5, 2.55), (1.15, 2.6), (1.25, 2.72), (1.0, 3.05), (0.55, 3.3), (0.0, 3.38)], 12)
    k.lathe("lueur_violette", [(0.52, 2.53), (1.12, 2.58)], 12)
    k.lathe("champi_pied", [(0.3, 3.3), (0.28, 3.75), (0.0, 3.75)], 8)
    k.lathe("champi_chapeau_violet", [(0.25, 3.7), (0.6, 3.72), (0.45, 3.95), (0.0, 4.05)], 10)
    k.ico("lueur_ambre", (0, 0, 4.12), 0.1)
    k.door(0, 0.72, 0.42, 0.68, 0.7)
    for j, (a, z) in enumerate([(70, 1.4), (-60, 1.9), (160, 2.2), (0, 2.1)]):
        k.window(a, z, 0.66, 0.13, glass="fenetre_ambre" if j % 2 else "fenetre")
    # escalier en colimaçon autour de la base
    for j in range(7):
        a = -20 - j * 25
        p = k.around(1.05, a, 0.1 + j * 0.09)
        k.box("pierre_nuit", p, (0.38, 0.3, 0.08), rot=(0, 0, a))
    # balcon rond à mi-hauteur
    k.lathe("bois_nuit", [(0.95, 1.75), (0.95, 1.8), (0.66, 1.8)], 12)
    for j in range(10):
        p = k.around(0.92, j * 36, 1.92)
        k.box("bois_nuit", p, (0.03, 0.03, 0.24))
    k.lathe("bois_nuit", [(0.93, 2.03), (0.9, 2.05)], 12)
    return k


# ---------------------------------------------------------------- village
def lampe_champignon():
    k = Kit("LampeChampignon")
    k.cyl("champi_pied", (0, 0, 0.25), 0.05, 0.5, v=6, rot=(0, 5, 0))
    k.ball("lueur", (0.02, 0, 0.52), 0.2, (1, 1, 0.55), seg=9, rings=4)
    k.ball("lueur_douce", (0.17, 0.05, 0.16), 0.09, (1, 1, 0.6), seg=6, rings=3)
    k.cyl("champi_pied", (0.17, 0.05, 0.08), 0.025, 0.16, v=5)
    return k


def puits():
    k = Kit("Puits")
    k.lathe("pierre_nuit", [(0.62, 0.0), (0.65, 0.55), (0.52, 0.58), (0.5, 0.45)], 10, wobble=0.05, seed=2)
    k.cyl("lueur", (0, 0, 0.42), 0.5, 0.02, v=10)
    for x in (-0.55, 0.55):
        k.box("bois_nuit", (x, 0, 0.85), (0.09, 0.09, 1.2))
    k.box("bois_nuit", (0, 0, 1.25), (1.2, 0.06, 0.06))
    k.cone("toit_mousse", (0, 0, 1.6), 0.8, 0.0, 0.45, v=4, rot=(0, 0, 45))
    k.box("corde", (0, 0, 1.05), (0.01, 0.01, 0.4))
    k.cyl("bois_nuit", (0, 0, 0.82), 0.1, 0.16, v=7)
    k.cyl("lueur", (0, 0, 0.86), 0.085, 0.04, v=7)
    return k


def etal():
    k = Kit("Etal")
    k.box("bois_nuit", (0, 0, 0.6), (1.4, 0.7, 0.08))
    for x in (-0.62, 0.62):
        for y in (-0.28, 0.28):
            k.box("bois_nuit", (x, y, 0.3), (0.07, 0.07, 0.6))
    for x in (-0.66, 0.66):
        k.box("bois_nuit", (x, 0.3, 1.1), (0.06, 0.06, 1.0))
    k.box("tissu_prune", (0, 0.0, 1.55), (1.55, 0.9, 0.04), rot=(-14, 0, 0))
    for j in range(5):  # festons
        k.box("tissu_rouille" if j % 2 else "tissu_sable", (-0.62 + j * 0.31, -0.43, 1.42), (0.3, 0.02, 0.16), rot=(-14, 0, 0))
    for j in range(7):
        k.ball(["lueur", "lueur_ambre", "lueur_violette"][j % 3], (-0.5 + j * 0.16, 0.1 * math.sin(j * 2.0), 0.7), 0.07, (1, 1, 0.85), seg=6, rings=4)
    k.cyl("tissu_sable", (0.4, 0.15, 0.73), 0.2, 0.18, v=8)
    k.cyl("tissu_sable", (-0.45, 0.2, 0.71), 0.15, 0.14, v=8)
    k.box("bois_nuit", (0.75, -0.1, 0.25), (0.35, 0.35, 0.5))  # caisse
    k.lantern((-0.66, -0.15, 1.3), "lueur_ambre", arm=0.2, ang=0)
    return k


def corde_linge():
    k = Kit("CordeLinge")
    for x in (-1.0, 1.0):
        k.box("bois_nuit", (x, 0, 0.7), (0.08, 0.08, 1.4))
    k.box("lueur_douce", (0, 0, 1.32), (2.0, 0.015, 0.015))
    for j, (x, m, h) in enumerate([(-0.65, "tissu_rouille", 0.35), (-0.25, "tissu_sable", 0.28), (0.15, "tissu_mousse", 0.42), (0.55, "tissu_prune", 0.25), (0.82, "tissu_ocre", 0.18)]):
        k.box(m, (x, 0, 1.3 - h / 2), (0.3, 0.02, h), rot=(0, 0, 3 * (j - 2)))
    return k


def potager():
    k = Kit("Potager")
    k.box("ecorce", (0, 0, 0.07), (1.6, 1.0, 0.14))
    for x in (-0.82, 0.82):
        k.box("bois_nuit", (x, 0, 0.1), (0.06, 1.05, 0.2))
    for y in (-0.52, 0.52):
        k.box("bois_nuit", (0, y, 0.1), (1.7, 0.06, 0.2))
    for j in range(10):
        x = -0.6 + (j % 5) * 0.3
        y = -0.25 if j < 5 else 0.25
        k.cyl("champi_pied", (x, y, 0.2), 0.02, 0.14, v=4)
        k.ball("lueur" if j % 3 else "lueur_violette", (x, y, 0.28), 0.075 + 0.02 * (j % 2), (1, 1, 0.6), seg=6, rings=3)
    k.box("bois_nuit", (0.95, 0.4, 0.45), (0.04, 0.04, 0.9))  # piquet + épouvantail-lanterne
    k.ico("lueur_ambre", (0.95, 0.4, 0.95), 0.07)
    return k


def banc():
    k = Kit("Banc")
    k.box("bois_nuit", (0, 0, 0.38), (1.2, 0.36, 0.07))
    k.box("bois_nuit", (0, 0.17, 0.62), (1.2, 0.05, 0.3), rot=(-10, 0, 0))
    for x in (-0.5, 0.5):
        k.box("ecorce", (x, 0, 0.18), (0.12, 0.3, 0.36))
    return k


def ponton():
    k = Kit("Ponton")
    for j in range(8):
        k.box("bois_nuit", (0, -j * 0.32, 0.5), (0.9, 0.28, 0.06), rot=(0, 0, 2 * math.sin(j)))
    for j in (0, 3, 7):
        for x in (-0.42, 0.42):
            k.cyl("ecorce", (x, -j * 0.32, 0.15), 0.06, 0.9, v=6)
    k.cyl("ecorce", (0.42, -2.24, 0.85), 0.06, 0.7, v=6)
    k.lantern((0.42, -2.24, 1.05), "lueur_ambre", arm=0.2, ang=90)
    return k


def pont_corde():
    """pont de corde de 4 m (le long de -y), pour franchir un ravin dans le monde de l'ombre"""
    k = Kit("PontCorde")
    n = 14
    for j in range(n):
        y = -j * (4.0 / (n - 1))
        sag = -0.25 * math.sin(math.pi * j / (n - 1))
        k.box("bois_nuit", (0, y, sag), (0.8, 0.22, 0.05), rot=(0, 0, 3 * math.sin(j * 1.7)))
    for x in (-0.42, 0.42):
        for j in range(n - 1):
            y0, y1 = -j * 4.0 / (n - 1), -(j + 1) * 4.0 / (n - 1)
            z0 = 0.55 - 0.18 * math.sin(math.pi * j / (n - 1))
            z1 = 0.55 - 0.18 * math.sin(math.pi * (j + 1) / (n - 1))
            k.stick("corde", (x, y0, z0), (x, y1, z1), 0.015, v=4)
        for y in (0.0, -4.0):
            k.cyl("ecorce", (x, y, 0.2), 0.05, 0.9, v=6)
            k.ico("lueur", (x, y, 0.68), 0.05)
    return k


def escalier_racines():
    """escalier de racines (5 marches, monte de 1 m vers -y)"""
    k = Kit("EscalierRacines")
    for j in range(5):
        k.box("ecorce", (0.05 * math.sin(j), -j * 0.32, 0.1 + j * 0.2), (0.85 - 0.04 * (j % 2), 0.36, 0.2), rot=(0, 0, 6 * math.sin(j * 2)))
        k.ico("lueur_douce", (0.38 * (1 if j % 2 else -1), -j * 0.32, 0.22 + j * 0.2), 0.035)
    for s in (-1, 1):
        k.stick("ecorce", (s * 0.48, 0.15, 0.0), (s * 0.45, -1.45, 1.05), 0.07, v=6)
    return k


def berceau_champignon():
    """berceau de la Pouponnière : un petit champignon creux avec un lit de mousse lumineuse"""
    k = Kit("BerceauChampignon")
    k.lathe("champi_pied", [(0.32, 0.0), (0.36, 0.12), (0.42, 0.28), (0.38, 0.3), (0.3, 0.18), (0.0, 0.16)], 10)
    k.cyl("lueur_douce", (0, 0, 0.2), 0.3, 0.04, v=10)
    k.lathe("champi_chapeau", [(0.1, 0.55), (0.45, 0.62), (0.3, 0.75), (0.0, 0.8)], 10, loc=(0, 0.3, 0))
    k.stick("champi_pied", (0, 0.32, 0.28), (0, 0.3, 0.58), 0.03)
    k.ico("lueur_rose", (0.05, -0.05, 0.27), 0.06)
    return k


# ---------------------------------------------------------------- nature
def champignon_geant(name="ChampignonGeant", h=3.6, cap=1.6, m="champi_chapeau"):
    k = Kit(name)
    k.lathe("champi_pied", [(0.42, 0.0), (0.32, 0.4), (0.26, h * 0.5), (0.24, h), (0.0, h)], 8, wobble=0.08, seed=len(name))
    k.lathe("champi_pied", [(0.36, h * 0.6), (0.42, h * 0.6 - 0.06), (0.3, h * 0.6 - 0.1)], 8)
    prof = [(0.25, h - 0.05), (cap * 0.95, h), (cap, h + 0.12), (cap * 0.85, h + cap * 0.3), (cap * 0.5, h + cap * 0.5), (0.0, h + cap * 0.55)]
    k.lathe(m, prof, 12)
    k.lathe("lueur_douce", [(0.27, h - 0.07), (cap * 0.93, h - 0.02)], 12)
    top = prof[2:]

    def zat(r):
        for (r1, z1), (r2, z2) in zip(top, top[1:]):
            if r2 <= r <= r1:
                return z2 + (z1 - z2) * (r - r2) / (r1 - r2)
        return prof[-1][1]
    for j in range(9):
        r = cap * (0.15 + 0.1 * (j % 7))
        p = k.around(r, j * 47, zat(r) + 0.01)
        k.ico("lueur", p, cap * (0.07 + 0.025 * (j % 3)), (1, 1, 0.35), rot=(0, math.degrees(math.atan2(r, cap * 1.3)), j * 47 - 90))
    return k


def fougere():
    k = Kit("Fougere")
    for j in range(6):
        a = j * 60
        p = k.around(0.12, a, 0.18)
        k.box("fougere", p, (0.08, 0.025, 0.42), rot=(32, 0, a))
    k.ico("lueur_violette", (0, 0, 0.32), 0.045)
    return k


def corail():
    k = Kit("Corail")
    def branch(a, b, depth):
        k.stick("lueur_rose" if depth == 0 else "coquille", a, b, 0.05 - depth * 0.012, v=5)
        if depth < 2:
            from mathutils import Vector
            d = Vector(b) - Vector(a)
            for s in (-1, 1):
                c = Vector(b) + Vector((d.y * 0.4 * s + d.x * 0.6, -d.x * 0.4 * s + d.y * 0.6, d.z * 0.8))
                branch(tuple(b), tuple(c), depth + 1)
        else:
            k.ico("lueur_rose", b, 0.04)
    branch((0, 0, 0), (0.05, 0.0, 0.35), 0)
    branch((0, 0, 0), (-0.12, 0.08, 0.28), 1)
    return k


def nappe_mousse():
    k = Kit("NappeMousse")
    k.lathe("mousse_claire", [(1.0, 0.0), (0.95, 0.04), (0.0, 0.05)], 9, wobble=0.25, seed=5)
    import random
    rnd = random.Random(9)
    for j in range(14):
        a, r = rnd.uniform(0, 360), rnd.uniform(0.1, 0.85)
        k.ico("lueur" if j % 4 else "lueur_violette", k.around(r, a, 0.06), 0.03)
    return k


def pin_nuit():
    k = Kit("PinNuit")
    k.cyl("ecorce", (0, 0, 0.25), 0.1, 0.5, v=6)
    k.cone("toit_mousse", (0, 0, 0.95), 0.55, 0.0, 1.1, v=7)
    k.cone("toit_mousse", (0, 0, 1.45), 0.42, 0.0, 0.9, v=7, rot=(0, 0, 23))
    for j, (a, z) in enumerate([(30, 0.8), (150, 1.0), (260, 1.3), (320, 0.7)]):
        k.ico("lueur", k.around(0.36 if z < 1 else 0.25, a, z), 0.04)
    return k


def build_village():
    maison_champignon(); maison_souche(); maison_coquillage(); maison_pilotis(); tour_ancienne()
    lampe_champignon(); puits(); etal(); corde_linge(); potager(); banc(); ponton(); pont_corde()
    escalier_racines(); berceau_champignon()
    champignon_geant(); champignon_geant("ChampignonGeantViolet", 2.6, 1.2, "champi_chapeau_violet")
    champignon_geant("ChampignonGeantAmbre", 1.8, 0.9, "champi_chapeau_ambre")
    fougere(); corail(); nappe_mousse(); pin_nuit()


VILLAGE = ["MaisonChampignon", "MaisonSouche", "MaisonCoquillage", "MaisonPilotis", "TourAncienne",
           "LampeChampignon", "Puits", "Etal", "CordeLinge", "Potager", "Banc", "Ponton", "PontCorde",
           "EscalierRacines", "BerceauChampignon", "ChampignonGeant", "ChampignonGeantViolet",
           "ChampignonGeantAmbre", "Fougere", "Corail", "NappeMousse", "PinNuit"]


# ---------------------------------------------------------------- chemins de l'ombre
def escalier_falaise():
    """grand escalier de racines : monte de 3 m sur 4,5 m (le long de -y), entre deux grosses racines"""
    k = Kit("EscalierFalaise")
    n = 15
    for j in range(n):
        y = -0.15 - j * 0.3
        z = 0.1 + j * 0.2
        k.box("ecorce", (0.04 * math.sin(j * 1.3), y, z - 0.05), (1.0 - 0.06 * (j % 2), 0.34, 0.22), rot=(0, 0, 5 * math.sin(j * 2.1)))
        if j % 3 == 1:
            k.ico("lueur_douce", (0.45 * (1 if j % 2 else -1), y, z + 0.08), 0.04)
    for s in (-1, 1):
        # la racine-rampe de chaque côté, en trois tronçons qui ondulent
        pts = [(s * 0.62, 0.3, 0.0), (s * 0.7, -1.4, 1.0), (s * 0.58, -2.9, 2.1), (s * 0.66, -4.6, 3.25)]
        for a, b in zip(pts, pts[1:]):
            k.stick("ecorce", a, b, 0.11, v=6)
        for a in pts[1:]:
            k.ico("ecorce", a, 0.13)
        k.ico("lueur", (s * 0.66, -4.6, 3.45), 0.06)
    # radicelles qui pendent, et petits champignons dans les marches
    for j in range(6):
        y = -0.6 - j * 0.7
        k.stick("fougere", (0.7, y, 0.45 + j * 0.47), (0.78, y - 0.05, 0.05 + j * 0.47), 0.02, v=4)
    # le corps de racine sous les marches (plein, pour qu'on voie un vrai escalier)
    k.stick("ecorce", (0, 0.0, -0.25), (0, -4.4, 2.75), 0.42, v=7)
    k.stick("ecorce", (0.2, -0.6, -0.05), (0.15, -3.9, 2.25), 0.3, v=6)
    for j, (x, step) in enumerate([(0.35, 3), (-0.38, 7), (0.3, 11)]):
        y = -0.15 - step * 0.3
        z = 0.1 + step * 0.2 + 0.06
        k.mini_mushrooms([(x, y, 0.12, 0.06)], z)
    return k


def ilot_corail():
    """un îlot de mousse et de corail qui n'existe que la nuit (rayon 2,2 m, dessus à 0,5 m)"""
    k = Kit("IlotCorail")
    k.lathe("coquille_raie", [(1.6, -0.6), (2.1, 0.0), (2.25, 0.35), (2.15, 0.48), (0.0, 0.5)], 11, wobble=0.12, seed=12)
    k.lathe("mousse_claire", [(2.1, 0.48), (1.9, 0.53), (0.0, 0.54)], 11, wobble=0.1, seed=13)
    import random
    rnd = random.Random(21)
    for j in range(16):
        a, r = rnd.uniform(0, 360), rnd.uniform(0.3, 1.8)
        k.ico("lueur" if j % 3 else "lueur_rose", k.around(r, a, 0.56), 0.035)
    for j, (a, r) in enumerate([(30, 1.6), (150, 1.7), (260, 1.5)]):
        x, y, _ = k.around(r, a, 0)
        k.stick("lueur_rose", (x, y, 0.5), (x + 0.05, y, 1.0), 0.05)
        k.stick("coquille", (x + 0.05, y, 0.85), (x + 0.25, y + 0.1, 1.2), 0.035)
        k.stick("coquille", (x + 0.05, y, 0.8), (x - 0.2, y - 0.05, 1.15), 0.035)
        k.ico("lueur_rose", (x + 0.25, y + 0.1, 1.22), 0.05)
        k.ico("lueur_rose", (x - 0.2, y - 0.05, 1.17), 0.05)
    for j, a in enumerate([90, 200, 320]):  # algues au bord
        p = k.around(2.15, a, 0.1)
        k.cone("lueur_douce", p, 0.07, 0.0, 0.7, rot=(15, 0, a), v=5)
    # une petite cabane de guet en coquillage, une lanterne-poisson
    k.lathe("coquille", [(0.55, 0.5), (0.58, 0.9), (0.42, 1.3), (0.0, 1.45)], 9, loc=(0.9, 0.9, 0), twist=0.2)
    k.box("bois_nuit", (0.9, 0.35, 0.78), (0.3, 0.05, 0.5))
    k.lantern((-0.6, -0.9, 1.25), "lueur", arm=0.3)
    k.box("bois_nuit", (-0.6 + 0.15, -0.9, 0.8), (0.06, 0.06, 0.9))
    return k


CHEMINS = ["EscalierFalaise", "IlotCorail"]
