"""Plan vu de dessus de l'île 2 (le Phare) — maquette K1.

Les zones sont décrites en mètres (1 case GridMap = 1 m, x vers l'est, z vers le sud).
`hauteur` = dessus du sol. Le même fichier servira à construire le GridMap.
Usage : python tools/plan_ile2.py  ->  tools/plan_ile2.png
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICI = Path(__file__).parent

# Marée : niveau de l'eau (m). Le sol à 0.0 est sec à marée basse, noyé à marée haute.
MAREE_BASSE = -0.6
MAREE_HAUTE = 0.5

# (nom, hauteur, polygone [(x, z), ...])  — l'ordre compte : les suivantes recouvrent.
ZONES = [
    ("port", 1.0, [(-14, 9), (12, 9), (15, 12), (15, 20), (10, 23), (-8, 23), (-15, 19), (-16, 13)]),
    ("ponton", 1.0, [(-1, 23), (2, 23), (2, 31), (-1, 31)]),
    ("chaussee", 0.0, [(-1, -7), (2, -7), (2, 9), (-1, 9)]),
    ("plage_grottes", 0.0, [(2, -9), (9, -9), (10, -5), (2, -5)]),
    ("rocher", 4.0, [(-12, -7), (-1, -7), (-1, -15), (2, -15), (2, -7), (10, -7), (14, -11), (14, -21),
                     (8, -26), (-6, -26), (-13, -21), (-14, -12)]),
    ("escalier", 0.5, [(-1, -15), (2, -15), (2, -7), (-1, -7)]),  # monte de 0 à 4 vers le nord
    ("plateau_phare", 5.0, [(-5, -14), (5, -14), (6, -19), (4, -23), (-4, -23), (-6, -19)]),
    ("sentier_est", 3.5, [(14, -17), (19, -17), (19, -14), (14, -14)]),
    ("cap_est", 2.5, [(18, -21), (26, -22), (29, -16), (25, -11), (18, -12)]),
    ("flaque_est", 0.0, [(25, -11), (30, -11), (30, -7), (25, -7)]),
    ("sentier_ouest", 4.0, [(-27, -15), (-13, -15), (-13, -13), (-27, -13)]),
    ("cap_ouest", 5.0, [(-35, -21), (-27, -23), (-24, -14), (-28, -9), (-35, -12)]),
    ("cap_large", 1.5, [(-4, -42), (4, -43), (6, -47), (1, -50), (-4, -48)]),
]
# Roches du gué vers le Cap du Large (praticables à marée basse seulement).
GUE_LARGE = [(-1, -28), (1, -31), (-1, -34), (1, -37), (0, -40)]

PHARE = {"centre": (0.5, -18.5), "rayon": 3.5, "niveaux": ["rez : machines", "1er : bureau", "2e : salle des cartes", "sommet : lentille + galerie"]}
EPAVE = [(-36, 26), (-28, 30), (-27, 33), (-35, 30)]

# Repères numérotés : (num, x, z, texte)
REPERES = [
    (1, 0.5, 30, "Ponton (accessible à toute marée), arrivée en barque"),
    (2, -9, 35, "Bouée-lanterne de la passe"),
    (3, -9, 15, "Maison du quai (lanterne)"),
    (4, 10, 15, "Hangar + miroir d'essai (tuto)"),
    (5, 4, 10, "Échelle de marée peinte sur le quai"),
    (6, 0.5, 5, "Balise 1"),
    (7, 0.5, 0, "Balise 2"),
    (8, 0.5, -5, "Balise 3"),
    (9, -1.8, 2, "Ancien corps couvert d'algues"),
    (10, 7, -6, "Entrée des grottes (marée basse)"),
    (11, 3.5, -19, "Crypte des Semeurs (sous le phare)"),
    (12, -9, -22, "Banc de la Gardienne"),
    (13, 9, -12, "Jardin mort"),
    (14, 23, -16, "Cap Est : lanterne + miroir"),
    (15, 27.5, -9, "Flaque + pierre-soleil (marée basse)"),
    (16, -31, -16, "Cap Ouest : lanterne + miroir (sentier dans la brume)"),
    (17, 1, -46, "Cap du Large : lanterne + miroir"),
    (18, 3, -45, "Ancien corps échoué"),
    (19, -31, 30, "Épave du ravitailleur (marée basse) : clé"),
]
# Trajet de la lumière : Cap Est -> Cap du Large -> Cap Ouest -> lentille  [à valider]
LUMIERE = [(23, -16), (1, -46), (-31, -16), (0.5, -18.5)]
BRUME_EPAISSE = [((-1, -7), (2, 9)), ((-27, -15), (-13, -13))]  # chaussée, sentier ouest


def dans_poly(x, z, poly):
    dedans = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1:
            dedans = not dedans
    return dedans


def cases():
    """Dictionnaire (cx, cz) -> (zone, hauteur), une case par mètre."""
    res = {}
    for nom, h, poly in ZONES:
        xs = [p[0] for p in poly]
        zs = [p[1] for p in poly]
        for cx in range(math.floor(min(xs)), math.ceil(max(xs))):
            for cz in range(math.floor(min(zs)), math.ceil(max(zs))):
                if dans_poly(cx + 0.5, cz + 0.5, poly):
                    hh = h
                    if nom == "escalier":  # 0.5 par marche, vers le nord
                        hh = min(4.0, 0.5 * (-7 - cz))
                    res[(cx, cz)] = (nom, hh)
    for gx, gz in GUE_LARGE:
        for dx in (0, 1):
            for dz in (0, 1):
                res[(gx + dx, gz + dz)] = ("gue", 0.0)
    return res


def couleur(nom, h):
    if h <= 0.0:
        return (196, 182, 150)  # estran : sable mouillé
    if nom in ("port", "ponton"):
        return (172, 160, 140) if nom == "port" else (150, 112, 80)
    t = min(1.0, h / 5.0)
    base, haut = (150, 170, 140), (215, 222, 205)
    return tuple(int(base[i] + (haut[i] - base[i]) * t) for i in range(3))


def main():
    S = 9  # px par mètre
    X0, X1, Z0, Z1 = -44, 38, -54, 42
    largeur_carte = (X1 - X0) * S
    W, H = largeur_carte + 430, (Z1 - Z0) * S + 300
    img = Image.new("RGB", (W, H), (126, 168, 186))
    d = ImageDraw.Draw(img, "RGBA")
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
        fb = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        fp = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 11)
    except OSError:
        f = fb = fp = ImageFont.load_default()

    def P(x, z):
        return ((x - X0) * S, (z - Z0) * S)

    # grille 10 m
    for x in range(X0, X1 + 1, 10):
        d.line([P(x, Z0), P(x, Z1)], fill=(255, 255, 255, 25))
    for z in range(Z0 - Z0 % 10, Z1 + 1, 10):
        d.line([P(X0, z), P(X1, z)], fill=(255, 255, 255, 25))

    grille = cases()
    for (cx, cz), (nom, h) in grille.items():
        x, y = P(cx, cz)
        d.rectangle([x, y, x + S - 1, y + S - 1], fill=couleur(nom, h))
    # bords de falaise (changement de hauteur)
    for (cx, cz), (nom, h) in grille.items():
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = grille.get((cx + dx, cz + dz))
            hv = v[1] if v else -1
            if h - hv >= 1.0:
                x, y = P(cx, cz)
                if dx == 1: d.line([x + S - 1, y, x + S - 1, y + S], fill=(90, 80, 70), width=2)
                if dx == -1: d.line([x, y, x, y + S], fill=(90, 80, 70), width=2)
                if dz == 1: d.line([x, y + S - 1, x + S, y + S - 1], fill=(90, 80, 70), width=2)
                if dz == -1: d.line([x, y, x + S, y], fill=(90, 80, 70), width=2)

    # brume épaisse
    for (a, b) in BRUME_EPAISSE:
        d.rectangle([*P(a[0] - 1, a[1]), *P(b[0] + 1, b[1])], fill=(235, 240, 245, 110))
    # épave
    d.polygon([P(*p) for p in EPAVE], fill=(110, 85, 60), outline=(60, 45, 30))
    # grottes (sous le rocher, pointillés)
    tunnel = [(7, -7), (6, -11), (4.5, -15), (3.5, -19)]
    for i in range(len(tunnel) - 1):
        d.line([P(*tunnel[i]), P(*tunnel[i + 1])], fill=(60, 50, 80, 200), width=3)
    # phare
    cx, cz = PHARE["centre"]
    r = PHARE["rayon"]
    d.ellipse([*P(cx - r, cz - r), *P(cx + r, cz + r)], fill=(245, 242, 235), outline=(160, 80, 60), width=3)
    d.ellipse([*P(cx - 1.2, cz - 1.2), *P(cx + 1.2, cz + 1.2)], fill=(250, 220, 120))
    # trajet de la lumière
    for i in range(len(LUMIERE) - 1):
        a, b = P(*LUMIERE[i]), P(*LUMIERE[i + 1])
        n = int(math.dist(a, b) / 10)
        for k in range(0, n, 2):
            t0, t1 = k / n, (k + 1) / n
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(255, 200, 60, 230), width=3)

    # repères
    for num, x, z, _ in REPERES:
        px, py = P(x, z)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(40, 45, 60), outline=(255, 255, 255))
        t = str(num)
        tw = d.textlength(t, font=fp)
        d.text((px - tw / 2, py - 8), t, font=fp, fill=(255, 255, 255))

    # étiquettes de zones
    for txt, x, z in [("LE PORT DES GARDIENS", -9, 20.5), ("CHAUSSÉE", 3, 3), ("ROCHER DU PHARE", -11, -10),
                      ("CAP EST", 19, -23.5), ("CAP OUEST", -36, -25), ("CAP DU LARGE", 7, -50),
                      ("gué (marée basse)", 3, -33), ("ÉPAVE", -38, 34.5), ("PHARE", -2.5, -24.5)]:
        d.text(P(x, z), txt, font=fp, fill=(30, 30, 40))

    # nord + échelle
    d.text((12, 10), "N ↑", font=fb, fill=(20, 20, 30))
    d.line([P(-40, 39), P(-30, 39)], fill=(20, 20, 30), width=3)
    d.text(P(-40, 39.5), "10 m", font=fp, fill=(20, 20, 30))

    # légende
    lx = largeur_carte + 20
    y = 16
    d.rectangle([largeur_carte, 0, W, H], fill=(245, 242, 236))
    d.text((lx, y), "Île 2 — le Phare (maquette K1)", font=fb, fill=(20, 20, 30)); y += 28
    for c, t in [((196, 182, 150), "estran : sec à marée basse, noyé à marée haute"),
                 ((172, 160, 140), "port (1 m), quai en pierre"),
                 ((150, 112, 80), "ponton en bois"),
                 (couleur("x", 2.5), "terre 2-3 m"),
                 (couleur("x", 5.0), "terre 4-5 m (rocher, Cap Ouest)"),
                 ((235, 240, 245), "brume épaisse (vide vite la batterie)")]:
        d.rectangle([lx, y + 2, lx + 16, y + 16], fill=c, outline=(80, 80, 80)); d.text((lx + 24, y), t, font=f, fill=(30, 30, 40)); y += 22
    d.line([lx, y + 9, lx + 16, y + 9], fill=(255, 200, 60), width=3)
    d.text((lx + 24, y), "trajet de la lumière [à valider]", font=f, fill=(30, 30, 40)); y += 22
    d.line([lx, y + 9, lx + 16, y + 9], fill=(60, 50, 80), width=3)
    d.text((lx + 24, y), "grottes, sous le rocher", font=f, fill=(30, 30, 40)); y += 30
    for num, _, _, t in REPERES:
        d.text((lx, y), f"{num:>2}.", font=fp, fill=(30, 30, 40)); d.text((lx + 26, y - 2), t, font=f, fill=(30, 30, 40)); y += 20
    y += 10
    d.text((lx, y), "Phare (Ø 7 m, ~18 m de haut) :", font=fp, fill=(30, 30, 40)); y += 18
    for t in PHARE["niveaux"]:
        d.text((lx + 10, y), "· " + t, font=f, fill=(30, 30, 40)); y += 18
    y += 8
    surf = sum(1 for v in grille.values() if v[1] > 0)
    for t in [f"Marée : eau à {MAREE_BASSE} m (basse) / +{MAREE_HAUTE} m (haute)",
              f"Terre ferme : ~{surf} cases (île 1 : ~887)",
              "Port → pied du phare : ~30 m",
              "Phare → Cap du Large : ~28 m (gué)"]:
        d.text((lx, y), t, font=f, fill=(30, 30, 40)); y += 19

    # île 1 à la même échelle, pour comparer
    try:
        c1 = json.load(open(ICI / "ile1_terrain.json"))["cells"]
        y0 = (Z1 - Z0) * S + 30
        d.rectangle([0, y0 - 30, W, H], fill=(126, 168, 186))
        d.text((20, y0 - 22), "Pour comparer : l'île 1, à la même échelle", font=fb, fill=(20, 20, 30))
        for c in c1:
            x, yy = 20 + (c["x"] + 26) * S, y0 + (c["z"] + 15) * S
            d.rectangle([x, yy, x + S - 1, yy + S - 1], fill=couleur("x", c["top"]) if c["top"] > 0 else (196, 182, 150))
    except (OSError, KeyError):
        pass

    img.save(ICI / "plan_ile2.png")
    print("ok", img.size, "cases:", len(grille), "terre ferme:", surf)


if __name__ == "__main__":
    main()
