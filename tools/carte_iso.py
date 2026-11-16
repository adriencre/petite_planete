"""Dessine des cartes d'îles en vue iso (blocs) depuis une grille texte.
Jeton : chiffre = niveau, "." = mer, "~" = mer dans la brume, "=" = ruines englouties, "_" = estran (seulement à marée basse).
Suffixes : lettres de repère (voir REPERES), "b" = brume sur la case, "n" = coque de la Nef, "g" = plantes qui brillent, "h" = bâtiment, "w" = eau qui coule (rivière, cascade).
Usage : python3 tools/carte_iso.py ile_01 sortie.png"""
import sys
from PIL import Image, ImageDraw, ImageFont

TW, TH, HZ = 66, 33, 22          # largeur/hauteur d'une case iso, pixels par niveau
F = lambda s: ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", s)
HERBE = [(232, 214, 170), (170, 214, 120), (140, 200, 110), (115, 185, 105), (95, 170, 100)]
FALAISE_G, FALAISE_D = (226, 150, 140), (240, 186, 150)
MER, BRUME = (120, 214, 210), (250, 238, 242)
REPERES = {  # lettre: (couleur, légende)
    "A": ((255, 246, 225), "Abri (berceau)"), "P": ((255, 200, 80), "Pierre-soleil"),
    "L": ((255, 190, 60), "Lanternes 1-2-3"), "G": ((255, 160, 30), "Grande lanterne"),
    "R": ((150, 100, 60), "Racines-escalier"), "C": ((90, 160, 255), "Cascade"),
    "T": ((120, 120, 140), "Atelier (grotte)"), "S": ((255, 120, 40), "Sommet"),
    "K": ((200, 180, 220), "Crique + barque"), "M": ((210, 170, 210), "Ancien corps"),
}

def lire(carte):
    g = []
    for ligne in carte.strip().split("\n"):
        rang = []
        for j in ligne.split():
            h = -1 if j[0] in ".~=" else 0 if j[0] == "_" else int(j[0])
            suf = j[1:]
            rang.append((h, j[0] == "~" or "b" in suf, suf.replace("b", "").replace("n", "").replace("g", "").replace("h", "").replace("w", ""), j[0] == "_", j[0] == "=", "n" in suf, "g" in suf, "h" in suf, "w" in suf))
        g.append(rang)
    return g

def dessiner(img, carte, ox, oy, titre, chemin=""):
    d = ImageDraw.Draw(img, "RGBA")
    g = lire(carte)
    d.text((ox - 160, oy - 110), titre, fill=(80, 60, 90), font=F(26))
    cases = sorted(((r, c) for r in range(len(g)) for c in range(len(g[r]))), key=lambda rc: rc[0] + rc[1])
    reperes = []
    for r, c in cases:
        h, brume, rep, estran, englouti, nef, lueur, bat, eau = g[r][c]
        x = ox + (c - r) * TW / 2
        y = oy + (c + r) * TH / 2
        if h < 0:
            top = y + 4
            d.polygon([(x, top), (x + TW / 2, top + TH / 2), (x, top + TH), (x - TW / 2, top + TH / 2)], fill=(70, 160, 175) if englouti else MER)
            if englouti:  # murs de ruines sous l'eau
                d.polygon([(x, top + 8), (x + TW / 4, top + TH / 2), (x, top + TH - 8), (x - TW / 4, top + TH / 2)], outline=(150, 220, 215), width=2)
            if brume:
                d.ellipse([x - TW * 0.6, top - 6, x + TW * 0.6, top + TH + 2], fill=BRUME + (170,))
            for ch in rep:
                reperes.append((x, top + TH / 2, ch))
            continue
        z = HZ * 0.45 if estran else (h + 1) * HZ
        t = y - z
        # faces latérales jusqu'à la mer
        d.polygon([(x - TW / 2, t + TH / 2), (x, t + TH), (x, y + TH + 4), (x - TW / 2, y + TH / 2 + 4)], fill=(150, 95, 85) if nef else (225, 210, 190) if bat else FALAISE_G)
        d.polygon([(x + TW / 2, t + TH / 2), (x, t + TH), (x, y + TH + 4), (x + TW / 2, y + TH / 2 + 4)], fill=(180, 112, 95) if nef else (240, 228, 210) if bat else FALAISE_D)
        for k in range(1, h + 1):  # strates
            yy = t + k * HZ
            d.line([(x - TW / 2, yy + TH / 2), (x, yy + TH), (x + TW / 2, yy + TH / 2)], fill=(250, 220, 190), width=1)
        d.polygon([(x, t), (x + TW / 2, t + TH / 2), (x, t + TH), (x - TW / 2, t + TH / 2)], fill=(120, 200, 235) if eau else (225, 125, 100) if nef else (252, 244, 228) if bat else (214, 196, 168) if estran else HERBE[min(h, 4)], outline=(255, 255, 255, 60))
        if lueur:
            for dx, dy in ((-12, 2), (8, 6), (-2, 13), (14, 15)):
                d.ellipse([x + dx - 3, t + TH / 2 + dy - 9, x + dx + 3, t + TH / 2 + dy - 3], fill=(130, 255, 225))
        if brume:
            d.ellipse([x - TW * 0.6, t - 4, x + TW * 0.6, t + TH + 4], fill=BRUME + (170,))
        for ch in rep:
            reperes.append((x, t + TH / 2, ch))
    pos = {ch: (x, y - 14) for x, y, ch in reperes}
    pts = [pos[ch] for ch in chemin if ch in pos]
    for a, b in zip(pts, pts[1:]):  # trajet du joueur, en pointillés
        for k in range(0, 20, 2):
            d.line([(a[0] + (b[0] - a[0]) * k / 20, a[1] + (b[1] - a[1]) * k / 20), (a[0] + (b[0] - a[0]) * (k + 1) / 20, a[1] + (b[1] - a[1]) * (k + 1) / 20)], fill=(60, 110, 230), width=4)
    for x, y, ch in reperes:  # repères par-dessus tout
        if ch == "F":  # tour du phare
            d.rectangle([x - 9, y - 110, x + 9, y], fill=(250, 248, 240), outline=(120, 100, 110))
            for k in (30, 60):
                d.rectangle([x - 9, y - 110 + k, x + 9, y - 100 + k], fill=(205, 120, 90))
            d.ellipse([x - 12, y - 128, x + 12, y - 104], fill=(255, 200, 80), outline=(120, 100, 110))
        if ch == "Y":  # antenne
            d.line([(x, y), (x, y - 150)], fill=(120, 80, 70), width=5)
            d.line([(x - 18, y - 120), (x + 18, y - 120)], fill=(120, 80, 70), width=4)
            d.ellipse([x - 7, y - 158, x + 7, y - 144], fill=(255, 90, 70))
        col = REPERES[ch][0]
        d.ellipse([x - 11, y - 25, x + 11, y - 3], fill=col, outline=(70, 50, 70), width=2)
        d.text((x, y - 14), ch, fill=(50, 35, 50), font=F(14), anchor="mm")

def legende(img, x, y):
    d = ImageDraw.Draw(img, "RGBA")
    for i, (ch, (col, nom)) in enumerate(REPERES.items()):
        yy = y + i * 30
        d.ellipse([x, yy, x + 22, yy + 22], fill=col, outline=(70, 50, 70), width=2)
        d.text((x + 11, yy + 11), ch, fill=(50, 35, 50), font=F(14), anchor="mm")
        d.text((x + 32, yy + 11), nom, fill=(70, 55, 80), font=F(17), anchor="lm")
    yy = y + len(REPERES) * 30 + 10
    d.rectangle([x, yy - 4, x + 22, yy + 16], fill=(214, 196, 168)); d.text((x + 32, yy + 6), "Estran (marée basse)", fill=(70, 55, 80), font=F(17), anchor="lm")
    yy += 30
    d.rectangle([x, yy - 4, x + 22, yy + 16], fill=(70, 160, 175)); d.text((x + 32, yy + 6), "Ruines englouties", fill=(70, 55, 80), font=F(17), anchor="lm")
    yy += 30
    d.ellipse([x - 4, yy, x + 26, yy + 20], fill=BRUME); d.text((x + 32, yy + 10), "Brume épaisse", fill=(70, 55, 80), font=F(17), anchor="lm")
    for k, col in enumerate(HERBE[1:4]):
        d.rectangle([x, yy + 32 + k * 26, x + 22, yy + 52 + k * 26], fill=col)
        d.text((x + 32, yy + 42 + k * 26), f"Niveau {k + 1}", fill=(70, 55, 80), font=F(17), anchor="lm")

REPERES_ILE = {}
ILES = {}

ILES["ile_01"] = (REPERES, [
        ("A. Gradins", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2C 2T . . .
. . ~ 2 2R 2 2 2 2 2 . .
. ~ ~ 1 1 1G 1 1 1 1 . .
. ~K ~M 1 1L 1 1 1L 1 1 . .
. ~ 0 0 0 0L 0 0 0 0 . .
. . 0 0 0A 0P 0 0 . . . .
. . . 0 0 0 . . . . . .
. . . . . . . . . . . ."""),
        ("B. Fer à cheval", """
. . . . . . . . . . . .
. . 2 2 2 2 2C 2T . . . .
. 2 2 2R 2 2 3 3S 3 . . .
. 1 1 . . . . . 2 2 . .
. 1 1G . ~ ~ ~ . . 2 . .
. 1 1L . ~K ~M ~ . . 1 . .
. 0 0L . . . . . . 1 . .
. 0 0L 0 . . . . 0 0 . .
. 0 0A 0P 0 . . 0 0 . . .
. . . . . . . . . . . ."""),
        ("C. Mesa centrale", """
. . . . . . . . . . . .
. . 0 0 1 1 1 1 0 . . .
. 0 1 2 2 2 2 2C 2T 1 . .
. ~ 1 2 3 3 3 3 2 1 . .
. ~K ~M 2R 3 3S 3 3 2 1 . .
. ~ 1 2 3 3 3 3 2 1 . .
. . 1 1G 2 2 2 2 2 1L . .
. . 0 1L 1 1 1 1L 1 0 . .
. . . 0 0A 0P 0 0 . . . .
. . . . . . . . . . . ."""),
])

ILES["ile_02"] = ({
    "P": ((200, 170, 130), "Ponton (arrivée)"), "B": ((255, 190, 60), "Bouée-lanterne"),
    "Q": ((255, 246, 225), "Maison du quai"), "H": ((180, 150, 120), "Hangar (miroir d'essai)"),
    "F": ((255, 200, 80), "Le Phare"), "J": ((190, 140, 160), "Banc d'Iris + jardin mort"),
    "G": ((120, 120, 140), "Entrée des grottes (crypte)"), "O": ((255, 160, 30), "Cap Ouest : lanterne + miroir"),
    "E": ((255, 160, 30), "Cap Est : lanterne + miroir"), "N": ((255, 160, 30), "Cap du Large : lanterne + miroir"),
    "S": ((255, 120, 40), "Flaque + pierre-soleil"), "X": ((210, 170, 210), "Ancien corps"),
    "W": ((150, 110, 90), "Épave du ravitailleur"),
}, [
    ("A. Croix", """
. . . . . . . . . . . . . .
. . . . . . 1X 1N . . . . . .
. . . . . . . _ . . . . . .
. . . . . . . _ . . . . . .
. 2O 2 2b 2b 2 3 3F 2 1 1E _S . .
. 2 2 . . 2 3 3J 2 1 1 . . .
. . . . _G 2 2 2 2 . . . . .
. . . . . . _b . . . . . . .
. . . . . . _bX . . . . . . .
. . . . . . _b . . . . . . .
. . . . . 0 0Q 0H 0 . . . . .
. . . . . 0 0 0 0P . . . . .
. ~ _W ~ . . . . . .B . . .
. . . . . . . . . . . . . ."""),
    ("B. Rocher massif", """
. . . . . . . . . . . . . .
. . . . . . 1X 1N . . . . . .
. . . . . . . _ . . . . . .
. . 2O 2 2b 2b 2b 2 2 1E . . . .
. . 2 2 3 3 3 3 2 1 _S . . .
. . . 2 3 3F 3 3 2 1 . . . .
. . . 2 3 3J 3 3 2 . . . . .
. . . _G 2 2 2 2 2 . . . . .
. . . . . . _b . . . . . . .
. . . . . . _bX . . . . . . .
. . . . . 0 0Q 0H 0 . . . . .
. . . . . 0 0 0 0P . . . . .
. ~ _W ~ . . . . . .B . . .
. . . . . . . . . . . . . ."""),
    ("C. Archipel", """
. . . . . . . . . . . . . .
. . . . . . 1X 1N . . . . . .
. . . . . . 1 1 . . . . . .
. . . . . . . _ . . . . . .
. 2O 2 . . . . _ . . . . . .
. 2 2b 2b 2b 3 3F 3 . _ 1E 1 . .
. . . . . 3 3J 3 . . 1 _S . .
. . . . _G 2 2 2 . . . . . .
. . . . . . _b . . . . . . .
. . . . . . _bX . . . . . . .
. . . . . . _b . . . . . . .
. . . . . 0 0Q 0H 0 . . . . .
. ~ _W ~ . 0 0 0 0P . . . . .
. . . . . . . . . .B . . .
. . . . . . . . . . . . . ."""),
])

ILES["ile_03"] = ({
    "Q": ((200, 170, 130), "Quai + carillon"), "E": ((120, 170, 200), "Écluse (canal vers les serres)"),
    "B": ((240, 200, 150), "Ville basse (1 lanterne/maison)"), "C": ((255, 246, 225), "École (comptine)"),
    "A": ((255, 170, 190), "Maison d'Aube"), "X": ((210, 170, 210), "Ancien corps"),
    "H": ((110, 100, 110), "Ville haute (projecteurs)"), "T": ((255, 190, 60), "Rue des Trois-Soleils"),
    "M": ((255, 160, 30), "Maison commune (Ysolde)"), "S": ((255, 190, 210), "Serres (arbres roses)"),
    "J": ((255, 120, 40), "Jardin du haut (lampe-mère)"), "V": ((70, 160, 175), "Vieux port englouti"),
}, [
    ("A. Amphithéâtre", """
. . . . . . . . . . . . . .
. . 3 3 3S 3 3S 3 3 . 3J 3 . .
. 2 3 3 3 3 3 3 3 . 3 3 . .
. 2 2H 2 2T 2 2M 2 2 . 2 2 . .
. 2 2 2 2 2 2 2 2 . 2 2 . .
. 1 1 1 1 1 1 1 1 . 1 1 . .
. 1 1C 1X 1A 1 1 1 1B . 1 1 . .
. 1 1 = = = = = 1 . 1 1 . .
. 0 1 = =V = = = 1 . 0 . . .
. 0 0 = = = = = 0 .E 0 . . .
. 0Q 0 = = = = = 0 . . . . .
. . . . . . . . . . . . . ."""),
    ("B. Croissant ouvert", """
. . . . . . . . . . . . . .
. 3 3S 3 3 3 3S 3J 3 . . . . .
. 3 3 3 3 3 3 3 3 . . . . .
. 2 2H 2 2T 2M 2 2 . . . . . .
. 2 2 2 2 2 2 1 . . . . . .
. 2 2 1B 1 1 1 . . . . . . .
. 1 1C 1A 1X 1 = = = . . . . .
. 1 1 1 = = = = = . . . . .
. 0 . 1 = =V = = . . . . . .
. 0 .E 0 = = = . . . . . . .
. 0Q 0 0 . . . . . . . . . .
. . . . . . . . . . . . . ."""),
    ("C. Lagon fermé", """
. . . . . . . . . . . . . .
. . . 3 3S 3 3S 3 3J . . . . .
. . 3 3 3 3 3 3 3 3 . . . .
. 2 2H 2T 2M 2 2 2 2 2 2 . . .
. 2 2 1 1 1 1 1 1 1 2 . . .
. 1B 1 = = = = = = 1 1 . . .
. 1C 1 = = =V = = = 1 1 . . .
. 1A 1X = = = = = = 1 0 . . .
. 0 0 0 = = = = 0 0 0 . . .
. . 0Q 0 0 0 .E 0 0 0 . . . .
. . . . . . . . . . . . . ."""),
])

ILES["ile_04"] = ({
    "P": ((200, 170, 130), "Ponton + panneau des cordes"), "L": ((240, 236, 245), "Salle des lits (draps, brume)"),
    "X": ((210, 170, 210), "Ancien corps"), "V": ((255, 246, 225), "Pavillon de Saule"),
    "N": ((60, 50, 70), "Salle noire (lit 12)"), "C": ((180, 170, 190), "Cimetière (stèles)"),
    "F": ((255, 200, 80), "Sémaphore (3 lampes)"),
}, [
    ("A. Plateau blanc", """
. . . . . . . . . . . .
. . 1b 1b 1b 1b 1b 2 2F . . .
. 1b 1b 1b 1b 1b 1b 2 2 . . .
. 1bV 1bN 1b 1bL 1b 1bX 1b 1b 1b . .
. 1b 1b 1b 1b 1b 1b 1b 1bC 1b . .
. . 1b 1b 1b 1b 1b 1b 1b 1b . .
. . . 0 0P 1b 1b 1b 1b . . .
. . . . . . . . . . . ."""),
    ("B. Cour d'hôpital", """
. . . . . . . . . . . .
. . . . 3 3F . . . . . .
. . 2 2 2 2 2 2 . . . .
. . 2V 1b 1b 1b 1b 2 . . . .
. 2N 2 1b 1bL 1bX 1b 2 . . . .
. . 2 1b 1b 1b 1b 2 1C 1 . .
. . 2 2 1b 2 2 2 1 1C . .
. . . . 0 0P . . . . . .
. . . . . . . . . . . ."""),
    ("C. Île longue", """
. . . . . . . . . . . . . .
. . . . . . . . . 2 3 3F . .
. 0P 1b 1b 1b 1b 1bV 1N 1C 1C 2 3 . .
. 0 1b 1bL 1bX 1b 1b 1 1 1 2 . . .
. . . 1b 1b . . . . . . . . .
. . . . . . . . . . . . . ."""),
], [(232, 214, 170), (242, 238, 246), (226, 218, 238), (210, 200, 230), (196, 186, 222)])

ILES["ile_05"] = ({
    "P": ((200, 170, 130), "Ponton"), "R": ((255, 246, 225), "Passerelle (file de squelettes)"),
    "O": ((255, 160, 30), "Poste de pilotage (Orme, Ysolde)"), "Y": ((255, 90, 70), "Antenne + salle de l'appel"),
    "D": ((255, 190, 210), "Soute des graines"), "K": ((120, 170, 200), "Brèche (marée basse)"),
    "X": ((210, 170, 210), "Ancien corps (noyé)"),
}, [
    ("A. Échouée sur la plage", """
. . . . . . . . . . . . . .
. . . 1 1 1 1 1 1 . . . . .
. . 1 1 4n 4nO 3n 3n 2nX 1 . . . .
. . 1 1 4n 4n 3n 3nY 2n 2nD _K . . .
. . 1 1R 1 1 1 1 1 _ _ . . .
. . . 0 0P 0 0 . . . . . . .
. . . . . . . . . . . . . ."""),
    ("B. Encastrée dans la falaise", """
. . . . . . . . . . . . . .
. . 3 3 3 3 3 3 3 . . . . .
. . 3 3 4nO 4n 3 3 3 . . . . .
. . 2 2 4n 4n 2 2 2 . . . . .
. . 1 1R 3nY 3n 1 1 . . . . . .
. . 0 0 2n 2nX 0 0 . . . . . .
. . . _ 1nD 1n _K . . . . . . .
. . . 0P . . . . . . . . . .
. . . . . . . . . . . . . ."""),
    ("C. Dans un cratère", """
. . . . . . . . . . . . . .
. 2 3 3 3 3 3 3 3 2 . . . .
. 2 3 _ _ _ _ _ 3 2 . . . .
. 2 3 _ 2nO 2n 2nY 2n 3 2 . . . .
. 2 3 _ 1nD 1nX 1n 1n 3 2 . . . .
. 2 3 _ _ _ _K _ 3 2 . . . .
. 1 1R 1 1 1 _ 3 3 2 . . . .
. 0 0P 0 . . . . . . . . . .
. . . . . . . . . . . . . ."""),
], [(232, 214, 170), (214, 200, 140), (200, 186, 128), (186, 172, 118), (172, 160, 110)])

ILES["ile_06"] = ({  # complexe sous-marin vu sans toit : plus le niveau est bas, plus c'est profond
    "E": ((120, 170, 200), "Sas d'entrée (porte du vieux port)"), "G": ((255, 190, 60), "Galerie des câbles"),
    "T": ((255, 160, 30), "Salle de contrôle (Tavin)"), "D": ((255, 246, 225), "Dortoirs des ouvriers"),
    "Z": ((255, 120, 40), "Salle de la barrière (le fond)"),
}, [
    ("A. Couloir qui descend", """
. . . . . . . . . . . .
. 3E 3 . . . . . . . . .
. . 3 2 2G 2 1 1 1 0 0Z .
. . . . 2T 2 . 1D 1 . 0 .
. . . . 2 2 . 1 1 . . .
. . . . . . . . . . . ."""),
    ("B. Spirale descendante", """
. . . . . . . .
. 4E 4 4 4 4 3 .
. 1 1 1 . . 3 .
. 1D . 0Z 0 . 3G .
. 1 . . . . 3 .
. 1 2 2 2T 2 2 .
. . . . . . . ."""),
    ("C. Salle centrale + bras", """
. . . . . . . . . . .
. . . . 3E . . . . . .
. . . . 3 . . . . . .
. . . . 2 . . . . . .
. 2D 2 2 2T 2 2G 1 1 . .
. . . . 2 . . . 1 . .
. . . . . . . . 0 0Z .
. . . . . . . . . . ."""),
], [(232, 214, 170), (222, 242, 240), (204, 234, 232), (186, 224, 224), (170, 214, 216)])

ILES["ile_07"] = ({
    "A": ((220, 225, 255), "Arrivée (chemin de lune)"), "M": ((255, 230, 150), "Maison d'Iris (métier, carnet)"),
}, [
    ("A. Jardin clos", """
. . . . . . . . .
. . 1g 1g 1g 1g . . .
. 1g 1g 2g 2g 1g 1g . .
. 1g 2g 2M 2g 2g 1g . .
. 1g 1g 2g 2g 1g 1g . .
. . 1g 1g 1g 0 0A . .
. . . . . . . . ."""),
    ("B. Piton", """
. . . . . . . .
. . 2g 3g 3g . . .
. 1g 3g 4M 3g 2g . .
. 1g 2g 3g 3g 2g . .
. . 1g 1g 1 0A . .
. . . . . . . ."""),
    ("C. Atoll", """
. . . . . . . . . .
. . 1g 1g 1g 1g 1g . . .
. 1g 1g . . . 1g 1g . .
. 1g . . 2M . . 1g . .
. 1g 1g . . . 1g 1g . .
. . 1g 1g . 1g 1g . . .
. . . . .A . . . . .
. . . . . . . . . ."""),
], [(232, 214, 170), (96, 116, 168), (84, 104, 156), (74, 92, 144), (64, 82, 134)])

ILES["ile_01_abri"] = ({
    "A": ((255, 246, 225), "Abri (berceau)"), "O": ((120, 90, 70), "Porte de l'abri"),
    "P": ((255, 200, 80), "Pierre-soleil"), "V": ((90, 160, 255), "Ce qu'on voit en sortant"),
    "Z": ((255, 200, 80), "Direction du Phare (au loin)"), "L": ((255, 190, 60), "Lanternes 1-2-3"),
    "G": ((255, 160, 30), "Grande lanterne"), "S": ((255, 120, 40), "Sommet"), "K": ((200, 180, 220), "Crique"),
}, [
    ("A. Au pied des gradins, porte au nord", """
. . . . . . . . . . . .
. . . . 3 3 3SV 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2 2 2 2 2 2 . .
. ~ ~ 1 1 1G 1 1 1 1 . .
. ~K ~ 1 1L 1 1 1L 1 1 . .
. ~ 0 0 0O 0L 0 0 0 0 . .
. . 0 0P 1hA 0 0 0 . . . .
. . . 0 0 0 . . . . . .
. . . . . . . . . . .Z ."""),
    ("B. Creusé dans la falaise, porte vers la mer", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2 2 2 2 2 2 . .
. ~ ~ 1 1 1G 1 1 1 1 . .
. ~K ~ 1 1hA 1L 1 1 1L 1 . .
. ~ 0 0 0O 0 0L 0 0 0 . .
. . 0 0 0P 0 0 0 . . . .
. . . 0 0 0 . . . . . .
. . . . . . . . . . .ZV ."""),
    ("C. Sur un promontoire, porte vers l'île", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2 2 2 2 2 2 . .
. ~ ~ 1 1 1G 1 1 1 1 . .
. ~K ~ 1 1L 1 1 1L 1 . . .
. ~ 0 0 0 0L 0V 0 0 . . .
. . 0 0 0 0 0 0 0O 1hA . .
. . . 0 0 0 . . 0P 1 . .
. . . . . . . . . . .Z ."""),
])

ILES["ile_01_lanternes"] = ({
    "A": ((255, 246, 225), "Abri (promontoire)"), "P": ((255, 200, 80), "Pierre-soleil"),
    "1": ((255, 190, 60), "Lanterne 1"), "2": ((255, 190, 60), "Lanterne 2"), "3": ((255, 190, 60), "Lanterne 3"),
    "G": ((255, 160, 30), "Grande lanterne"), "R": ((150, 100, 60), "Racines-escalier (vers le plateau)"),
    "S": ((255, 120, 40), "Sommet"), "K": ((200, 180, 220), "Crique"),
}, [
    ("A. En ligne, le long de la plage", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2R 2 2 2 2 2 . .
. ~ ~ 1 1 1G 1 1 1 1 . .
. ~K ~ 1 1 1 1 1 1 . . .
. ~ 0 0 03 0 02 0 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0P 1 . .
. . . . . . . . . . . .""", "AP123G"),
    ("B. En triangle autour de la grande", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2R 2 2 2 2 2 . .
. ~ ~ 12 1 1 1 1 1 1 . .
. ~K ~ 1 1 1G 1 1 13 . . .
. ~ 0 0 0 0 0 0 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0P 1 . .
. . . . . . . . . . . .""", "AP132G"),
    ("C. En zigzag qui monte", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . ~ 2 2R 2 2 2 2 2 . .
. ~ ~ 13 1 1 1G 1 1 1 . .
. ~K ~ 1 1 1 1 1 12 . . .
. ~ 0 0 0 0 0 0 0 . . .
. . 0 0 01 0 0 0 0 1hA . .
. . . 0 0 0 . . 0P 1 . .
. . . . . . . . . . . .""", "AP123G"),
])

ILES["ile_01_cascade"] = ({
    "A": ((255, 246, 225), "Abri"), "1": ((255, 190, 60), "Lanterne 1"), "2": ((255, 190, 60), "Lanterne 2"),
    "3": ((255, 190, 60), "Lanterne 3"), "G": ((255, 160, 30), "Grande lanterne"),
    "T": ((170, 120, 70), "Terreau (on y plante la graine)"), "R": ((150, 100, 60), "Racines-escalier"),
    "C": ((90, 160, 255), "Cascade"), "W": ((70, 90, 140), "Rebord caché derrière l'eau"),
    "X": ((120, 120, 140), "Grotte + atelier des robots"), "S": ((255, 120, 40), "Sommet"), "K": ((200, 180, 220), "Crique"),
}, [
    ("A. Cascade à l'est, du sommet", """
. . . . . . . . . . . .
. . . . 3 3 3S 3w 3X . . .
. . . 2 2 2 2 2wC 2W . . .
. . ~ 2 2R 2 2 2w 2 2 . .
. ~ ~ 12 1T 1 1 1w 1 1 . .
. ~K ~ 1 1 1G 1 1w 13 . . .
. ~ 0 0 0 0 0 0w 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "TRCWX"),
    ("B. Dans une gorge au centre", """
. . . . . . . . . . . .
. . . . 3 3X 3w 3S . . . .
. . . 2 2 2W 1wC 2 2 . . .
. . ~ 2 2R 2 1w 2 2 2 . .
. ~ ~ 12 1T 1 0w 1 1 1 . .
. ~K ~ 1 1 1G 0w 1 13 . . .
. ~ 0 0 0 0 0w 0 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "TRCWX"),
    ("C. Cachée à l'ouest, dans la brume", """
. . . . . . . . . . . .
. . . . 3 3 3S 3 . . . .
. . . 2 2 2 2 2 2 . . .
. . 2bX 2wC 2 2R 2 2 2 2 . .
. ~ ~W 1w 12 1T 1 1 1 1 . .
. ~K ~ 1 1 1G 1 1 13 . . .
. ~ 0 0 0 0 0 0 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "TRCWX"),
])

ILES["ile_01_crique"] = ({
    "A": ((255, 246, 225), "Abri"), "1": ((255, 190, 60), "Lanterne 1"), "2": ((255, 190, 60), "Lanterne 2 (bord de la brume)"),
    "3": ((255, 190, 60), "Lanterne 3"), "G": ((255, 160, 30), "Grande lanterne"), "T": ((170, 120, 70), "Terreau"),
    "R": ((150, 100, 60), "Racines-escalier"), "C": ((90, 160, 255), "Cascade"), "W": ((70, 90, 140), "Rebord caché"),
    "X": ((120, 120, 140), "Atelier"), "S": ((255, 120, 40), "Sommet"),
    "K": ((200, 180, 220), "Crique"), "M": ((210, 170, 210), "Ancien corps"),
    "B": ((180, 140, 100), "Barque (sous les racines)"), "Q": ((255, 200, 80), "Pierre-soleil cachée"),
}, [
    ("A. Anse ouverte dans la brume", """
. . . . . . . . . . . .
. . . . 3 3 3S 3w 3X . . .
. . . 2 2 2 2 2wC 2W . . .
. ~ ~ 2 2R 2 2 2w 2 2 . .
~ 0b 0bQ 12 1T 1 1 1w 1 1 . .
~ 0bM 0bK 1 1 1G 1 1w 13 . . .
~ 0bB 0b 0 0 0 0 0w 0 . . .
. ~ 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "2KMQB"),
    ("B. Crique encaissée", """
. . . . . . . . . . . .
. . . . 3 3 3S 3w 3X . . .
. 2 2 2 2 2 2 2wC 2W . . .
. 2 2 2 2R 2 2 2w 2 2 . .
. 2 0bQ 12 1T 1 1 1w 1 1 . .
. 0bB 0bM 1 1 1G 1 1w 13 . . .
. 0bK 0b 0 0 0 0 0w 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "2KMQB"),
    ("C. Îlot de brume", """
. . . . . . . . . . . .
. . . . 3 3 3S 3w 3X . . .
. . . 2 2 2 2 2wC 2W . . .
. . ~ 2 2R 2 2 2w 2 2 . .
0bQ 0b ~ 12 1T 1 1 1w 1 1 . .
0bM 0bB ~ 1 1 1G 1 1w 13 . . .
~ 0 0bK 0 0 0 0 0w 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . .""", "2KMBQ"),
])

BAS_ILE_01 = """. 2 0bQ 12 1T 1 1 1w 1 1 . .
. 0bB 0bM 1 1 1G 1 1w 13 . . .
. 0bK 0b 0 0 0 0 0w 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0 1 . .
. . . . . . . . . . . ."""
ILES["ile_01_sommet"] = ({
    "R": ((150, 100, 60), "Racines-escalier (arrivée)"), "H": ((180, 140, 100), "Charrette"),
    "N": ((200, 170, 140), "Banc"), "J": ((170, 150, 110), "Jardin mort"), "E": ((240, 220, 190), "Montée vers le sommet"),
    "S": ((255, 120, 40), "Sommet + lanterne du sommet"), "C": ((90, 160, 255), "Cascade"),
    "W": ((70, 90, 140), "Rebord caché"), "X": ((120, 120, 140), "Atelier"), "A": ((255, 246, 225), "Abri"),
    "G": ((255, 160, 30), "Grande lanterne"), "K": ((200, 180, 220), "Crique"),
    "Q": ((255, 200, 80), "Pierre-soleil cachée"), "B": ((180, 140, 100), "Barque"), "M": ((210, 170, 210), "Ancien corps"),
    "T": ((170, 120, 70), "Terreau"), "1": ((255, 190, 60), "Lanterne 1"), "2": ((255, 190, 60), "Lanterne 2"), "3": ((255, 190, 60), "Lanterne 3"),
}, [
    ("A. Sommet au centre", """
. . . . . . . . . . . .
. . . . 3 3S 3 3w 3X . . .
. 2 2 2J 2 2E 2 2wC 2W . . .
. 2 2N 2H 2R 2 2 2w 2 2 . .
""" + BAS_ILE_01, "RHNJES"),
    ("B. Crête, sommet au-dessus de la crique", """
. . . . . . . . . . . .
. . 3S 3 3 3 3 3w 3X . . .
. 2 2 2J 2 2 2E 2wC 2W . . .
. 2 2N 2H 2R 2 2 2w 2 2 . .
""" + BAS_ILE_01, "RHNJES"),
    ("C. Sommet à la source de la cascade", """
. . . . . . . . . . . .
. . . . . . 3 3w 3S 3X . .
. 2 2 2J 2 2 2E 2wC 2W . . .
. 2 2N 2H 2R 2 2 2w 2 2 . .
""" + BAS_ILE_01, "RHNJES"),
])

ILES["ile_01_plan"] = (dict(ILES["ile_01_sommet"][0], P=((255, 200, 80), "Pierre-soleil")), [
    ("Île 1 — plan v6 (décidé le 2026-11-16)", """
. . . . . . . . . . . .
. . . . 3 3S 3 3w 3X . . .
. 2 2 2J 2 2E 2 2wC 2W . . .
. 2 2N 2H 2R 2 2 2w 2 2 . .
. 2 0bQ 12 1T 1 1 1w 1 1 . .
. 0bB 0bM 1 1 1G 1 1w 13 . . .
. 0bK 0b 0 0 0 0 0w 0 . . .
. . 0 0 0 0 0 0 01 1hA . .
. . . 0 0 0 . . 0P 1 . .
. . . . . . . . . . . .""", "AP1G2TRHNJES"),
])

if __name__ == "__main__":
    REPERES, variantes, *palette = ILES[sys.argv[1]]
    if palette:
        HERBE = palette[0]
    img = Image.new("RGB", (3200, 1000), (252, 240, 236))
    for i, (titre, carte, *chemin) in enumerate(variantes):
        dessiner(img, carte, 440 + i * 930, 260, titre, chemin[0] if chemin else "")
    legende(img, 2880, 120)
    img.save(sys.argv[2])
