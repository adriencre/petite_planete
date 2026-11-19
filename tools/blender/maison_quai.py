"""Île 2 — la maison du quai (ILE_02_PHARE.md §3 « La maison du quai », décidé le 2026-11-19).

Une seule pièce de gardiens, à l'échelle des Semeurs (2,5-3 m) : le robot (1,90 m) y est petit.
Lancer dans Blender :  exec(open(r"...\\tools\\blender\\maison_quai.py", encoding="utf-8").read())
Crée la scène « ILE02_maison_quai » et exporte assets/models/ile02/maison_quai.glb.

Repère : origine = centre du sol intérieur, au niveau du terrain du port. Z vers le haut.
X = est (la porte est sur le mur est), Y = nord (la grande fenêtre, vers la chaussée et le Phare).
Dans Godot : X = X, Godot Z = -Y (la fenêtre regarde vers -Z, le nord).

Objets exportés (suffixe « -col » = collision créée à l'import par Godot) :
  murs-col, socle-col, mobilier-col, Decor, Cadres, Toit (+ pignons, charpente, cheminée),
  Coupe (le haut du mur sud, côté caméra : s'efface avec le toit, vue en coupe), AiguilleMaree,
  et des repères (Empties) : Centre, Porte, RepereLanterne, RepereCahier, RepereDessin, RepereHorloge.
Les objets « héros » (poêle, lanterne, horloge, cirés, cahier) seront remplacés par Meshy : ici, ce sont
des versions simples à la bonne place et à la bonne taille.
"""
import bpy, bmesh, math, random, os
from math import cos, sin, tau, pi
from mathutils import Vector

RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SORTIE = os.path.join(RACINE, "assets", "models", "ile02", "maison_quai.glb")
NOM_SCENE = "ILE02_maison_quai"
rng = random.Random(11)

# ---------------------------------------------------------------- dimensions (m)
IX, IY = 3.6, 4.6          # demi-intérieur (7,2 × 9,2 m)
EP = 0.5                   # épaisseur des murs
H = 4.4                    # hauteur des murs
SOL = 0.08                 # dessus du plancher
ASSISE = 0.55              # hauteur d'une assise de pierre
FAITAGE = 2.6              # hauteur du toit au-dessus des murs
DEBORD = 0.6               # débord du toit
# ouvertures : (mur, centre le long du mur, largeur, bas, haut)
PORTE = ("est", -2.0, 2.0, 0.0, 3.2)
FENETRE_N = ("nord", 0.8, 2.8, 1.3, 3.4)
FENETRE_O = ("ouest", -1.2, 1.4, 1.7, 3.1)
OUVERTURES = [PORTE, FENETRE_N, FENETRE_O]

# ---------------------------------------------------------------- scène
sc = bpy.data.scenes.get(NOM_SCENE) or bpy.data.scenes.new(NOM_SCENE)
bpy.context.window.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(nom, hexcol, rough=0.85, metal=0.0, emit=None, force=0.0):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        b.inputs["Emission Strength"].default_value = force
    return m


PIERRES = [mat("mq_pierre_1", "#ECE3D3"), mat("mq_pierre_2", "#DFD5C4"), mat("mq_pierre_3", "#F3EDE2"), mat("mq_pierre_4", "#D6CBB9")]
SOCLE = mat("mq_socle", "#C9BFB0")
BOIS = mat("mq_bois_miel", "#C99A62")
BOIS_F = mat("mq_bois_fonce", "#9C7048")
PLANCHES = [mat("mq_planche_1", "#D9AE74"), mat("mq_planche_2", "#CFA066"), mat("mq_planche_3", "#E0B985")]
TUILES = [mat("mq_tuile_1", "#C7735A"), mat("mq_tuile_2", "#B8664F"), mat("mq_tuile_3", "#D28A6E")]
VOLET = mat("mq_volet_bleu", "#8FB4C4")
FONTE = mat("mq_fonte", "#4E4A4C", 0.6, 0.3)
LAITON = mat("mq_laiton", "#D1A54B", 0.35, 0.7)
CUIVRE = mat("mq_cuivre", "#C27B4E", 0.45, 0.7)
DRAP = mat("mq_drap_creme", "#F1E8D8")
COUV_R = mat("mq_couverture_rouge", "#C96A5A")
COUV_B = mat("mq_couverture_bleue", "#7FA2C4")
CIRE = mat("mq_cire_jaune", "#F2C53D", 0.5)
BOTTE = mat("mq_botte_verte", "#4F6B52", 0.6)
PAPIER = mat("mq_papier", "#F7EEDC")
CARTE = mat("mq_carte_marine", "#E8DDBE")
TAPIS = mat("mq_tapis", "#8DA9B8")
CORDE = mat("mq_corde", "#C8B08A")
CADRAN = mat("mq_cadran", "#F4EEDF")
CADRAN_BAS = mat("mq_cadran_basse", "#7FC0C8")
CADRAN_HAUT = mat("mq_cadran_haute", "#3E7FA6")
AIGUILLE = mat("mq_aiguille", "#3B3436", 0.5)
DESSIN = [mat("mq_crayon_rose", "#E88FA8"), mat("mq_crayon_bleu", "#5FA8D3"), mat("mq_crayon_jaune", "#F0C24B")]


class Piece:
    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []

    def idx(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def objet(self, parent=None):
        me = bpy.data.meshes.new(self.nom)
        self.bm.to_mesh(me)
        self.bm.free()
        for p in me.polygons:
            p.use_smooth = False
        for m in self.mats:
            me.materials.append(m)
        o = bpy.data.objects.new(self.nom, me)
        sc.collection.objects.link(o)
        if parent:
            o.parent = parent
        return o


def boite(p, x0, x1, y0, y1, z0, z1, m, haut=None):
    """Pavé aligné (haut = matériau du dessus, sinon m)."""
    bm = p.bm
    v = [bm.verts.new(c) for c in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                    (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
    i = p.idx(m)
    for f in [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
        bm.faces.new([v[j] for j in f]).material_index = i
    bm.faces.new([v[4], v[5], v[6], v[7]]).material_index = p.idx(haut or m)


def boite_c(p, cx, cy, cz, sx, sy, sz, m, haut=None):
    """Pavé centré en (cx, cy) posé sur cz."""
    boite(p, cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz, cz + sz, m, haut)


def prisme(p, pts, z0, z1, m, haut=None):
    bm, n = p.bm, len(pts)
    b = [bm.verts.new((x, y, z0)) for x, y in pts]
    t = [bm.verts.new((x, y, z1)) for x, y in pts]
    i = p.idx(m)
    for k in range(n):
        bm.faces.new((b[k], b[(k + 1) % n], t[(k + 1) % n], t[k])).material_index = i
    bm.faces.new(list(reversed(b))).material_index = i
    bm.faces.new(t).material_index = p.idx(haut or m)


def cylindre(p, cx, cy, z0, r, h, m, n=8, axe="z"):
    """Cylindre à facettes (axe z, ou « y » : couché, pour une horloge au mur)."""
    bm = p.bm
    if axe == "z":
        b = [bm.verts.new((cx + r * cos(tau * k / n), cy + r * sin(tau * k / n), z0)) for k in range(n)]
        t = [bm.verts.new((cx + r * cos(tau * k / n), cy + r * sin(tau * k / n), z0 + h)) for k in range(n)]
    else:   # couché le long de -Y : (cx, cy) = point de départ au mur, z0 = hauteur du centre
        b = [bm.verts.new((cx + r * cos(tau * k / n), cy, z0 + r * sin(tau * k / n))) for k in range(n)]
        t = [bm.verts.new((cx + r * cos(tau * k / n), cy - h, z0 + r * sin(tau * k / n))) for k in range(n)]
    i = p.idx(m)
    for k in range(n):
        bm.faces.new((b[k], b[(k + 1) % n], t[(k + 1) % n], t[k])).material_index = i
    bm.faces.new(list(reversed(b))).material_index = i
    bm.faces.new(t).material_index = i
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[-(n + 2):])


def repere(nom, x, y, z):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_size = 0.4
    o.location = (x, y, z)
    sc.collection.objects.link(o)
    return o


murs = Piece("murs-col")
socle = Piece("socle-col")
mobilier = Piece("mobilier-col")
decor = Piece("Decor")
cadres = Piece("Cadres")
toit = Piece("Toit")
coupe = Piece("Coupe-col")  # le haut du mur sud (côté caméra) : s'efface avec le toit quand on entre
COUPE_Z = 1.1              # hauteur sous laquelle le mur sud reste visible (vue en coupe)
aiguille = Piece("AiguilleMaree")

# ---------------------------------------------------------------- le socle et le plancher
boite(socle, -IX - EP - 0.35, IX + EP + 0.35, -IY - EP - 0.35, IY + EP + 0.35, -0.6, 0.02, SOCLE)
x = -IX
while x < IX - 0.01:   # planches le long de Y, largeur 0,45 m, joints décalés
    l = min(0.45, IX - x)
    y = -IY - rng.uniform(0, 2.0)
    while y < IY:
        lg = rng.uniform(2.0, 3.6)
        boite(socle, x + 0.015, x + l - 0.015, max(y, -IY) + 0.01, min(y + lg, IY) - 0.01, 0.0, SOL + rng.uniform(-0.008, 0.008),
              rng.choice(PLANCHES))
        y += lg
    x += l


# ---------------------------------------------------------------- les murs en assises de pierre
def mur(nom, a, b, interieur):
    """Un mur droit de a à b (points 2D au milieu de l'épaisseur), `interieur` = normale vers la pièce."""
    a, b = Vector(a), Vector(b)
    t = (b - a).normalized()
    n = Vector(interieur)
    longueur = (b - a).length
    ouv = []
    for (m_, centre, larg, bas, haut) in OUVERTURES:
        if m_ == nom:
            # centre exprimé en coordonnée monde le long du mur : convertir en abscisse depuis a
            cm = Vector((centre, 0)) if nom in ("nord", "sud") else Vector((0, centre))
            s = (cm - a).dot(t) if nom in ("nord", "sud") else (Vector((a.x, centre)) - a).dot(t)
            ouv.append((s - larg / 2, s + larg / 2, bas, haut))
    z = 0.0
    rang = 0
    while z < H - 0.01:
        h = min(ASSISE, H - z)
        exclus = [(s0, s1) for (s0, s1, bas, haut) in ouv if z < haut - 0.01 and z + h > bas + 0.01]
        s = -rng.uniform(0.0, 0.7) if rang % 2 else 0.0
        while s < longueur - 0.01:
            lg = rng.uniform(0.8, 1.7)
            s0, s1 = max(s, 0.0), min(s + lg, longueur)
            s = s + lg
            # couper le bloc autour des ouvertures
            morceaux = [(s0, s1)]
            for (e0, e1) in exclus:
                nouveaux = []
                for (m0, m1) in morceaux:
                    if m1 <= e0 or m0 >= e1:
                        nouveaux.append((m0, m1))
                    else:
                        if m0 < e0:
                            nouveaux.append((m0, e0))
                        if m1 > e1:
                            nouveaux.append((e1, m1))
                morceaux = nouveaux
            for (m0, m1) in morceaux:
                if m1 - m0 < 0.05:
                    continue
                sail = rng.uniform(-0.03, 0.03)
                j0, j1 = 0.012, 0.012
                p0 = a + t * (m0 + j0) - n * (EP / 2 + sail)
                p1 = a + t * (m1 - j1) - n * (EP / 2 + sail)
                q0 = a + t * (m0 + j0) + n * (EP / 2 + 0.005)
                q1 = a + t * (m1 - j1) + n * (EP / 2 + 0.005)
                cible = coupe if (nom == "sud" and z >= COUPE_Z - 0.01) else murs
                prisme(cible, [(p0.x, p0.y), (p1.x, p1.y), (q1.x, q1.y), (q0.x, q0.y)], z + 0.012, z + h - 0.012,
                       rng.choice(PIERRES))
        z += h
        rang += 1
    # un mortier continu derrière les blocs (pas de jour entre les pierres)
    return ouv


# murs : nord et sud sur toute la largeur extérieure, est et ouest entre les deux
mur("sud", (IX + EP, -IY - EP / 2), (-IX - EP, -IY - EP / 2), (0, 1))
mur("nord", (-IX - EP, IY + EP / 2), (IX + EP, IY + EP / 2), (0, -1))
mur("est", (IX + EP / 2, -IY), (IX + EP / 2, IY), (-1, 0))
mur("ouest", (-IX - EP / 2, IY), (-IX - EP / 2, -IY), (1, 0))

# mortier : une âme continue au milieu de chaque mur, percée aux ouvertures (évite les jours entre les blocs)
for (x0, x1, y0, y1, nom) in [(-IX - EP + 0.1, IX + EP - 0.1, -IY - EP + 0.15, -IY - 0.15, "sud"),
                              (-IX - EP + 0.1, IX + EP - 0.1, IY + 0.15, IY + EP - 0.15, "nord"),
                              (IX + 0.15, IX + EP - 0.15, -IY, IY, "est"),
                              (-IX - EP + 0.15, -IX - 0.15, -IY, IY, "ouest")]:
    ouv = [o for o in OUVERTURES if o[0] == nom]
    le_long_x = nom in ("nord", "sud")
    coupes = sorted([(c - l / 2, c + l / 2, bas, haut) for (_, c, l, bas, haut) in ouv])
    # bandes verticales entre les ouvertures, et au-dessus / au-dessous de chacune
    debut = x0 if le_long_x else y0
    fin = x1 if le_long_x else y1
    s = debut
    for (c0, c1, bas, haut) in coupes + [(fin, fin, 0, 0)]:
        if c0 > s:
            if le_long_x and nom == "sud":
                boite(murs, s, c0, y0, y1, 0.0, COUPE_Z, SOCLE)
                boite(coupe, s, c0, y0, y1, COUPE_Z, H - 0.02, SOCLE)
            elif le_long_x:
                boite(murs, s, c0, y0, y1, 0.0, H - 0.02, SOCLE)
            else:
                boite(murs, x0, x1, s, c0, 0.0, H - 0.02, SOCLE)
        if c1 > c0:
            for (z0, z1) in [(0.0, bas), (haut, H - 0.02)]:
                if z1 - z0 > 0.02:
                    if le_long_x:
                        boite(murs, c0, c1, y0, y1, z0, z1, SOCLE)
                    else:
                        boite(murs, x0, x1, c0, c1, z0, z1, SOCLE)
        s = max(s, c1)

# ---------------------------------------------------------------- la charpente apparente
P = 0.36   # section des poteaux
for (cx, cy) in [(IX + EP, IY + EP), (-IX - EP, IY + EP), (IX + EP, -IY - EP), (-IX - EP, -IY - EP)]:
    px, py = cx - math.copysign(P / 2 - 0.08, cx), cy - math.copysign(P / 2 - 0.08, cy)
    if cy < 0:
        boite_c(cadres, px, py, 0.0, P, P, COUPE_Z, BOIS_F)
        boite_c(coupe, px, py, COUPE_Z, P, P, H + 0.05 - COUPE_Z, BOIS_F)
    else:
        boite_c(cadres, px, py, 0.0, P, P, H + 0.05, BOIS_F)
# sablières (le haut des murs)
boite(coupe, -IX - EP - 0.1, IX + EP + 0.1, -IY - EP - 0.1, -IY + 0.05, H - 0.3, H + 0.05, BOIS)
boite(cadres, -IX - EP - 0.1, IX + EP + 0.1, IY - 0.05, IY + EP + 0.1, H - 0.3, H + 0.05, BOIS)
boite(cadres, IX - 0.05, IX + EP + 0.1, -IY - EP, IY + EP, H - 0.3, H + 0.05, BOIS)
boite(cadres, -IX - EP - 0.1, -IX + 0.05, -IY - EP, IY + EP, H - 0.3, H + 0.05, BOIS)
# deux entraits au-dessus de la pièce (vus d'en haut quand le toit s'efface)
for y in (-1.4, 2.2):   # entraits et poinçons : avec le toit (ils s'effacent avec lui)
    boite(toit, -IX - 0.1, IX + 0.1, y - 0.17, y + 0.17, H - 0.42, H - 0.08, BOIS_F)
    boite(toit, -0.14, 0.14, y - 0.12, y + 0.12, H - 0.08, H + FAITAGE, BOIS_F)

# la porte : encadrement, linteau, battant entrouvert vers l'intérieur
_, pc, pl, pb, ph = PORTE
for s in (-1, 1):
    boite(cadres, IX - 0.08, IX + EP + 0.1, pc + s * pl / 2 - (0.22 if s > 0 else 0.0), pc + s * pl / 2 + (0.0 if s > 0 else 0.22) , 0.0, ph, BOIS_F)
boite(cadres, IX - 0.08, IX + EP + 0.1, pc - pl / 2 - 0.25, pc + pl / 2 + 0.25, ph, ph + 0.4, BOIS)
# battant grand ouvert vers l'extérieur, rabattu contre la façade (gond au sud) : des planches verticales
gx, gy = IX + EP + 0.04, pc - pl / 2
for k in range(5):
    boite(cadres, gx, gx + 0.1, gy - (k + 1) * pl / 5 + 0.01, gy - k * pl / 5 - 0.01, 0.05, ph - 0.1, BOIS if k % 2 else BOIS_F)
for z in (0.6, ph - 0.7):   # pentures en fer
    boite(cadres, gx + 0.1, gx + 0.13, gy - pl + 0.1, gy - 0.05, z, z + 0.12, FONTE)
cylindre(cadres, gx + 0.18, gy - pl + 0.3, 1.55, 0.09, 0.12, LAITON, 8)   # la poignée, bien au-dessus du robot
# seuil
boite(socle, IX - 0.1, IX + EP + 0.5, pc - pl / 2, pc + pl / 2, 0.0, 0.06, BOIS_F)


def fenetre(cx, cy, larg, bas, haut, axe):
    """Encadrement, meneau, traverse, appui et volets ouverts. axe = « x » (mur nord/sud) ou « y »."""
    if axe == "x":
        e0, e1 = IY - 0.05, IY + EP + 0.08
        boite(cadres, cx - larg / 2 - 0.2, cx + larg / 2 + 0.2, e0 - 0.15, e1, bas - 0.16, bas, BOIS)       # appui
        boite(cadres, cx - larg / 2 - 0.25, cx + larg / 2 + 0.25, e0, e1, haut, haut + 0.35, BOIS)          # linteau
        for s in (-1, 1):
            boite(cadres, cx + s * larg / 2 - 0.1, cx + s * larg / 2 + 0.1, e0, e1, bas, haut, BOIS_F)
        boite(cadres, cx - 0.06, cx + 0.06, IY + EP / 2 - 0.05, IY + EP / 2 + 0.05, bas, haut, BOIS_F)       # meneau
        boite(cadres, cx - larg / 2, cx + larg / 2, IY + EP / 2 - 0.05, IY + EP / 2 + 0.05, (bas + haut) / 2 - 0.05, (bas + haut) / 2 + 0.05, BOIS_F)
        for s in (-1, 1):   # volets ouverts, plaqués à l'extérieur
            x0 = cx + s * (larg / 2 + 0.1)
            x1 = x0 + s * larg / 2
            boite(cadres, min(x0, x1), max(x0, x1), IY + EP + 0.02, IY + EP + 0.1, bas, haut, VOLET)
    else:
        e0, e1 = -IX - EP - 0.08, -IX + 0.05
        boite(cadres, e0, e1 + 0.15, cy - larg / 2 - 0.2, cy + larg / 2 + 0.2, bas - 0.16, bas, BOIS)
        boite(cadres, e0, e1, cy - larg / 2 - 0.25, cy + larg / 2 + 0.25, haut, haut + 0.35, BOIS)
        for s in (-1, 1):
            boite(cadres, e0, e1, cy + s * larg / 2 - 0.1, cy + s * larg / 2 + 0.1, bas, haut, BOIS_F)
        boite(cadres, -IX - EP / 2 - 0.05, -IX - EP / 2 + 0.05, cy - 0.06, cy + 0.06, bas, haut, BOIS_F)
        for s in (-1, 1):
            y0 = cy + s * (larg / 2 + 0.1)
            y1 = y0 + s * larg / 2
            boite(cadres, -IX - EP - 0.1, -IX - EP - 0.02, min(y0, y1), max(y0, y1), bas, haut, VOLET)


fenetre(FENETRE_N[1], 0, FENETRE_N[2], FENETRE_N[3], FENETRE_N[4], "x")
fenetre(0, FENETRE_O[1], FENETRE_O[2], FENETRE_O[3], FENETRE_O[4], "y")

# ---------------------------------------------------------------- le toit (s'efface quand on entre)
xe, ye = IX + EP + DEBORD, IY + EP + DEBORD
zt = H + 0.05
# tuiles : des rangs nets de l'égout au faîtage ; chaque tuile est une plaque inclinée dont le bas
# déborde un peu sur le rang du dessous (le ressaut dessine les rangs vus d'en haut)
for cote in (-1, 1):
    nb = 8
    for r in range(nb):
        u0, u1 = r / nb, (r + 1) / nb
        x0, x1 = cote * xe * (1 - u0) + cote * 0.08, cote * xe * (1 - u1)
        z0, z1 = zt + FAITAGE * u0 - 0.02, zt + FAITAGE * u1 + 0.06
        y = -ye + (0.0 if r % 2 == 0 else -0.35)
        while y < ye - 0.01:
            l = rng.uniform(0.75, 0.95)
            ya, yb = max(y, -ye), min(y + l, ye)
            y += l
            if yb - ya < 0.1:
                continue
            m = TUILES[0] if rng.random() < 0.7 else rng.choice(TUILES[1:])
            bm = toit.bm
            ep = 0.1
            v = [bm.verts.new(c) for c in [(x0, ya + 0.02, z0), (x1, ya + 0.02, z1), (x1, yb - 0.02, z1), (x0, yb - 0.02, z0),
                                            (x0, ya + 0.02, z0 + ep), (x1, ya + 0.02, z1 + ep), (x1, yb - 0.02, z1 + ep), (x0, yb - 0.02, z0 + ep)]]
            i = toit.idx(m)
            for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
                bm.faces.new([v[j] for j in f]).material_index = i
    bmesh.ops.recalc_face_normals(toit.bm, faces=toit.bm.faces[:])
# faîtage
boite(toit, -0.2, 0.2, -ye - 0.05, ye + 0.05, zt + FAITAGE - 0.05, zt + FAITAGE + 0.22, BOIS_F)
# pignons (triangles en planches verticales, nord et sud)
for sy in (-1, 1):
    y0, y1 = sy * (IY + EP) - 0.02 * sy, sy * (IY + EP) - (EP - 0.05) * sy
    k = 0
    x = -IX - EP
    while x < IX + EP - 0.01:
        l = min(0.5, IX + EP - x)
        xm = x + l / 2
        hz = FAITAGE * (1 - abs(xm) / (IX + EP + DEBORD))
        boite(toit, x + 0.01, x + l - 0.01, min(y0, y1), max(y0, y1), zt - 0.05, zt + hz, BOIS if k % 2 else BOIS_F)
        x += l
        k += 1
# cheminée en pierre, au-dessus du poêle (coin sud-ouest)
CHEM = (-2.6, -3.5)
for k in range(6):
    boite_c(toit, CHEM[0], CHEM[1], zt + 0.6 + k * 0.45, 0.95, 0.95, 0.43, rng.choice(PIERRES))
boite_c(toit, CHEM[0], CHEM[1], zt + 0.6 + 6 * 0.45, 1.1, 1.1, 0.12, SOCLE)

# ---------------------------------------------------------------- le mobilier (à l'échelle des Semeurs)
# la table, à hauteur de poitrine du robot (1,40 m), et ses deux bancs
# posée dans le sens nord-sud, à l'ouest de l'allée : de la porte au milieu de la pièce, plus de 2 m de passage
TX, TY = -0.2, -1.5
boite_c(mobilier, TX, TY, 1.3, 1.5, 3.6, 0.12, BOIS, BOIS)
for sx in (-1, 1):
    for sy in (-1, 1):
        boite_c(mobilier, TX + sx * 0.55, TY + sy * 1.55, SOL, 0.2, 0.2, 1.3, BOIS_F)
boite_c(mobilier, TX, TY, 0.35, 0.12, 3.2, 0.12, BOIS_F)   # entretoise
for sy in (-1, 1):
    bx = TX + sy * 1.15
    boite_c(mobilier, bx, TY, 0.72, 0.5, 3.3, 0.1, BOIS)
    for sx in (-1, 1):
        boite_c(mobilier, bx, TY + sx * 1.4, SOL, 0.4, 0.16, 0.64, BOIS_F)
# le coin couchage : cloison basse en planches (nord-ouest), lits superposés géants contre le mur ouest
for k in range(6):
    x0 = -IX + k * 0.42
    boite(decor, x0 + 0.01, x0 + 0.41, 0.35, 0.47, SOL, 1.55 + (0.08 if k % 2 else 0.0), BOIS if k % 2 else BOIS_F)
boite(mobilier, -IX, -IX + 2.52, 0.3, 0.52, SOL, 0.3, BOIS_F)   # bas de cloison (collision)
LX0, LX1, LY0, LY1 = -IX + 0.05, -IX + 2.25, 0.9, IY - 0.05
for (x, y) in [(LX0, LY0), (LX1 - 0.22, LY0), (LX0, LY1 - 0.22), (LX1 - 0.22, LY1 - 0.22)]:
    boite(mobilier, x, x + 0.22, y, y + 0.22, SOL, 3.7, BOIS_F)
for (zc, couv) in [(0.75, COUV_R), (2.45, COUV_B)]:
    boite(mobilier, LX0 + 0.1, LX1 - 0.1, LY0 + 0.1, LY1 - 0.1, zc, zc + 0.18, BOIS)               # cadre
    boite(decor, LX0 + 0.15, LX1 - 0.15, LY0 + 0.15, LY1 - 0.15, zc + 0.18, zc + 0.42, DRAP)       # matelas
    boite(decor, LX0 + 0.35, LX1 - 0.35, LY1 - 0.95, LY1 - 0.25, zc + 0.42, zc + 0.6, DRAP)        # oreiller
    boite(decor, LX0 + 0.3, LX1 - 0.3, LY0 + 0.3, LY0 + 1.0, zc + 0.42, zc + 0.62, couv)           # couverture pliée au carré
boite(decor, LX1 - 0.05, LX1 + 0.05, LY0 + 0.1, LY1 - 0.1, 2.6, 2.75, BOIS_F)                       # garde-corps
for k in range(5):   # échelle
    boite(decor, LX1 + 0.02, LX1 + 0.1, LY0 + 0.5, LY0 + 1.3, 0.55 + k * 0.5, 0.62 + k * 0.5, BOIS)
for y in (LY0 + 0.5, LY0 + 1.3):
    boite(decor, LX1 + 0.02, LX1 + 0.12, y - 0.05, y + 0.05, SOL, 2.6, BOIS_F)
# la couchette d'Aube : petite, à taille d'enfant, sous la fenêtre qui regarde le Phare
AX0, AX1, AY0, AY1 = -1.15, 0.55, IY - 1.0, IY - 0.08
boite(mobilier, AX0, AX1, AY0, AY1, SOL, 0.45, BOIS)
boite(decor, AX0 + 0.06, AX1 - 0.06, AY0 + 0.06, AY1 - 0.06, 0.45, 0.62, DRAP)
boite(decor, AX0 + 0.1, AX0 + 0.55, AY0 + 0.15, AY1 - 0.15, 0.62, 0.74, DRAP)                    # oreiller
boite(decor, AX0 + 0.75, AX1 - 0.1, AY0 + 0.1, AY1 - 0.1, 0.62, 0.7, COUV_R)                      # petite couverture
boite(decor, AX0 + 0.42, AX0 + 0.72, AY0 + 0.25, AY0 + 0.6, 0.66, 0.672, PAPIER)                   # le dessin qui dépasse
for k in range(3):
    boite(decor, AX0 + 0.47 + k * 0.08, AX0 + 0.52 + k * 0.08, AY0 + 0.32, AY0 + 0.52, 0.672, 0.676, DESSIN[k])
for x in (AX0, AX1 - 0.12):   # montants
    boite(decor, x, x + 0.12, AY0, AY0 + 0.12, SOL, 0.95, BOIS_F)
# le poêle en fonte (coin sud-ouest), sa bouilloire et son tuyau jusqu'à la cheminée
SX, SY = CHEM
boite_c(mobilier, SX, SY, SOL, 1.5, 1.1, 0.25, FONTE)
boite_c(mobilier, SX, SY, SOL + 0.25, 1.4, 1.0, 1.05, FONTE)
boite_c(decor, SX, SY, SOL + 1.3, 1.55, 1.15, 0.08, FONTE)
boite_c(decor, SX + 0.71, SY, SOL + 0.45, 0.02, 0.6, 0.5, LAITON)   # porte du foyer
cylindre(decor, SX - 0.2, SY + 0.2, SOL + 1.38, 0.16, H - SOL - 1.38 + 0.1, FONTE, 8)
cylindre(decor, SX + 0.35, SY - 0.15, SOL + 1.38, 0.22, 0.32, CUIVRE, 8)                           # bouilloire
cylindre(decor, SX + 0.35, SY - 0.15, SOL + 1.7, 0.08, 0.1, CUIVRE, 6)
boite(decor, SX - 0.6, SX + 0.4, SY + 0.7, SY + 1.0, SOL, 0.5, BOIS_F)                             # bûches
# étagères (mur est, au nord : le mur sud s'efface en vue de coupe) : bocaux, pots
for z in (1.7, 2.6):
    boite(decor, IX - 0.45, IX - 0.02, 2.3, 4.4, z, z + 0.07, BOIS)
    for k in range(4):
        cylindre(decor, IX - 0.25, 2.55 + k * 0.5 + rng.uniform(-0.08, 0.08), z + 0.07, rng.uniform(0.1, 0.15), rng.uniform(0.25, 0.4),
                 rng.choice([CARTE, LAITON, VOLET, PAPIER]), 7)
for y in (2.32, 4.3):
    boite(decor, IX - 0.35, IX - 0.02, y, y + 0.08, 1.5, 1.77, BOIS_F)
# rouleau de corde et caisses, dans le coin sud-est
cylindre(mobilier, 1.8, -3.9, SOL, 0.55, 0.35, CORDE, 10)
cylindre(decor, 1.8, -3.9, SOL + 0.35, 0.3, 0.05, BOIS_F, 10)
boite_c(mobilier, 3.0, -3.95, SOL, 1.0, 1.0, 0.9, BOIS, BOIS_F)
boite_c(mobilier, 3.05, -3.9, SOL + 0.9, 0.75, 0.75, 0.6, BOIS_F, BOIS)
# patères, cirés jaunes et bottes géantes (mur est, au nord de la porte)
boite(decor, IX - 0.12, IX - 0.02, -0.7, 2.0, 2.85, 3.0, BOIS_F)
for k, y in enumerate((-0.3, 0.6, 1.5)):
    boite(decor, IX - 0.3, IX - 0.05, y - 0.04, y + 0.04, 2.9, 2.96, BOIS_F)
    if k < 2:   # deux cirés pendus (un manteau long, en prisme)
        bm = decor.bm
        pts = [(IX - 0.1, y - 0.45, 1.0), (IX - 0.1, y + 0.45, 1.0), (IX - 0.55, y + 0.4, 1.0), (IX - 0.55, y - 0.4, 1.0)]
        top = [(IX - 0.1, y - 0.2, 2.9), (IX - 0.1, y + 0.2, 2.9), (IX - 0.32, y + 0.2, 2.9), (IX - 0.32, y - 0.2, 2.9)]
        vb = [bm.verts.new(c) for c in pts]
        vt = [bm.verts.new(c) for c in top]
        i = decor.idx(CIRE)
        for j in range(4):
            bm.faces.new((vb[j], vb[(j + 1) % 4], vt[(j + 1) % 4], vt[j])).material_index = i
        bm.faces.new(list(reversed(vb))).material_index = i
        bm.faces.new(vt).material_index = i
for k, y in enumerate((-0.2, 0.45)):
    boite(mobilier, IX - 0.85, IX - 0.25, y - 0.22, y + 0.22, SOL, 0.75, BOTTE)
    boite(decor, IX - 1.05, IX - 0.25, y - 0.22, y + 0.22, SOL, 0.22, BOTTE)
# le tapis sous la table, la carte marine (mur ouest, au sud de la fenêtre), le cahier, les tasses
boite(decor, TX - 1.9, TX + 1.9, TY - 2.2, TY + 2.2, SOL, SOL + 0.015, TAPIS)
boite(decor, -IX + 0.01, -IX + 0.03, -3.6, -2.2, 1.7, 2.8, CARTE)
for k in range(4):
    boite(decor, -IX + 0.03, -IX + 0.035, -3.5 + k * 0.33, -3.3 + k * 0.33, 1.9 + (k % 2) * 0.4, 2.1 + (k % 2) * 0.4, VOLET)
CAHIER = (TX + 0.05, TY + 0.7)
for s in (-1, 1):   # le cahier ouvert : deux pages légèrement relevées
    bm = decor.bm
    x0 = CAHIER[0]
    x1 = CAHIER[0] + s * 0.42
    v = [bm.verts.new(c) for c in [(x0, CAHIER[1] - 0.3, 1.43), (x1, CAHIER[1] - 0.3, 1.46), (x1, CAHIER[1] + 0.3, 1.46), (x0, CAHIER[1] + 0.3, 1.43)]]
    f = bm.faces.new(v if s > 0 else list(reversed(v)))
    f.material_index = decor.idx(PAPIER)
boite(decor, CAHIER[0] - 0.46, CAHIER[0] + 0.46, CAHIER[1] - 0.33, CAHIER[1] + 0.33, 1.42, 1.43, BOIS_F)
for (x, y) in [(TX + 0.35, TY - 0.6), (TX - 0.4, TY - 1.2), (TX + 0.3, TY + 1.5)]:
    cylindre(decor, x, y, 1.42, 0.11, 0.2, rng.choice([PAPIER, VOLET]), 8)
# l'horloge de marée (mur nord, à l'est de la fenêtre) : cadran, moitié « basse » / moitié « haute », une aiguille
HX, HZ = 2.95, 2.75
cylindre(decor, HX, IY - 0.0, HZ, 0.55, 0.08, LAITON, 12, "y")
cylindre(decor, HX, IY - 0.08, HZ, 0.47, 0.03, CADRAN, 12, "y")
for k in range(6):   # secteurs colorés : bas = basse mer (clair), haut = haute mer (foncé)
    a0, a1 = pi + k * pi / 6, pi + (k + 1) * pi / 6
    for (aa, m) in [((a0, a1), CADRAN_BAS), ((a0 - pi, a1 - pi), CADRAN_HAUT)]:
        bm = decor.bm
        v = [bm.verts.new((HX, IY - 0.115, HZ)), bm.verts.new((HX + 0.42 * cos(aa[0]), IY - 0.115, HZ + 0.42 * sin(aa[0]))),
             bm.verts.new((HX + 0.42 * cos(aa[1]), IY - 0.115, HZ + 0.42 * sin(aa[1])))]
        f = bm.faces.new(v)
        f.material_index = decor.idx(m)
bm = aiguille.bm   # l'aiguille : pivot à l'origine de l'objet (le centre du cadran), pointe vers +Z
v = [bm.verts.new(c) for c in [(-0.035, 0, -0.08), (0.035, 0, -0.08), (0.015, 0, 0.38), (-0.015, 0, 0.38),
                                (-0.035, -0.03, -0.08), (0.035, -0.03, -0.08), (0.015, -0.03, 0.38), (-0.015, -0.03, 0.38)]]
for f in [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]:
    bm.faces.new([v[j] for j in f]).material_index = aiguille.idx(AIGUILLE)
# le socle de la lanterne (la lanterne elle-même : la lanterne des Semeurs, posée dans maison_quai.tscn)
LAX, LAY = 2.5, 3.4
cylindre(mobilier, LAX, LAY, SOL, 0.45, 0.25, SOCLE, 8)
# (la prise est celle du modèle de lanterne, posé dans Godot)

# ---------------------------------------------------------------- dehors : un banc, une bouée, des casiers
boite_c(mobilier, IX + EP + 0.9, 1.6, 0.0, 0.6, 2.6, 0.7, BOIS, BOIS)
boite_c(mobilier, IX + EP + 0.8, -4.2, 0.0, 1.1, 0.9, 0.7, BOIS_F, BOIS)   # casier
boite_c(decor, IX + EP + 0.75, -4.15, 0.7, 0.9, 0.8, 0.5, BOIS, BOIS_F)

# ---------------------------------------------------------------- objets, repères, export
objets = []
for p in (murs, socle, mobilier, decor, cadres, toit, coupe):
    objets.append(p.objet())
o_aig = aiguille.objet()
o_aig.location = (HX, IY - 0.13, HZ)
objets.append(o_aig)
for (nom, x, y, z) in [("Centre", 0, 0, SOL), ("Porte", IX + EP + 1.2, PORTE[1], 0.0), ("RepereLanterne", LAX, LAY, SOL + 0.25),
                       ("RepereCahier", CAHIER[0], CAHIER[1], 1.46), ("RepereDessin", AX0 + 0.57, AY0 + 0.42, 0.68),
                       ("RepereHorloge", HX, IY - 0.13, HZ)]:
    objets.append(repere(nom, x, y, z))

# un repère d'échelle pour juger dans Blender (non exporté)
ech = Piece("echelle_robot_1m90")
boite_c(ech, 1.8, 0.8, SOL, 0.7, 0.6, 1.9, mat("mq_repere", "#FFFFFF", 0.6))
o_ech = ech.objet()

soleil = bpy.data.lights.new("soleil_mq", "SUN")
soleil.energy = 4.5
soleil.color = (1.0, 0.88, 0.72)
so = bpy.data.objects.new("soleil_mq", soleil)
sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(-35))
cam = bpy.data.cameras.new("cam_mq")
cam.lens = 30
co = bpy.data.objects.new("cam_mq", cam)
sc.collection.objects.link(co)
co.location = (12, -14, 15)
co.rotation_euler = (Vector((0, 0, 1)) - co.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = co
if sc.world is None:
    sc.world = bpy.data.worlds.new("monde_mq")
sc.world.use_nodes = True
fond = next(nd for nd in sc.world.node_tree.nodes if nd.type == "BACKGROUND")
fond.inputs[0].default_value = (*srgb("#CFE3EE"), 1)
fond.inputs[1].default_value = 0.9

os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
for o in objets:
    o.select_set(True)
bpy.context.view_layer.objects.active = objets[0]
bpy.ops.export_scene.gltf(filepath=SORTIE, export_format="GLB", use_selection=True, use_active_scene=True,
                          export_apply=True, export_yup=True, export_lights=False, export_cameras=False)
print("maison du quai :", sum(len(o.data.polygons) for o in objets if o.type == "MESH"), "faces ->", SORTIE)
