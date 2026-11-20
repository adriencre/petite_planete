"""Île 2 — le terrain complet, en « blocs taillés à facettes, strates nettes » (style validé le 2026-11-19
sur tools/blender/falaise_test_ile_02.py).

Source unique : la carte texte du nœud Maquette de scenes/ile_02_maquette.tscn (même grille que Godot).
Lancer depuis le projet : blender -b --python tools/blender/terrain_ile_02.py
Crée la scène « ILE02_terrain » et exporte assets/models/ile02/terrain_ile_02.glb.

Ce qui est construit :
- des anneaux de falaise, un par niveau (union des cases de ce niveau ou plus), chacun en strates
  de blocs taillés qui avancent / reculent un peu ; les strates du bas débordent (talus) ;
- des fissures verticales ; un escalier creusé dans une encoche sur chaque case à flèche (^ v < >),
  avec une rampe de collision invisible (« -colonly » : Godot en fait une collision sans mesh) ;
- l'estran (« _ ») en sable mouillé à 0 m, la flaque, les éboulis et le varech au pied des falaises ;
- le dessus : herbe rase, plaques d'herbe sèche et de lichen doré, pierres ; le port en dalles.
Coordonnées : Blender X = Godot X, Blender Y = -Godot Z (l'export glTF fait la conversion).
Objets exportés (suffixe « -col » = collision concave créée à l'import par Godot) :
  roche-col, plateaux-col, port-col, estran-col, eboulis-col, decor, escaliers, joues-col, rampes-colonly
Le volume des grottes est creusé avant export et sa couverture de terrain sort en pièces séparées.
"""
import bpy, bmesh, math, random, re, os
from math import cos, sin, tau
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

RACINE = Path(__file__).resolve().parents[2]
SCENE_GODOT = os.path.join(RACINE, "scenes", "ile_02_maquette.tscn")
SORTIE = os.path.join(RACINE, "assets", "models", "ile02", "terrain_ile_02.glb")
NOM_SCENE = "ILE02_terrain"
GRAINE = 7

TAILLE_CASE = 7.0          # = taille_case du nœud Maquette
HAUTEUR_NIVEAU = 2.5       # = hauteur_niveau
Z_NIV0 = 0.6               # niveau 0 (le port) ; niveau n = Z_NIV0 + n * HAUTEUR_NIVEAU
Z_ESTRAN = 0.1             # l'estran : découvert seulement à marée basse (mer de -0,6 à +0,5)
Z_FOND = -1.6              # pied des falaises, sous la mer
PAS_CONTOUR = 1.6          # distance entre deux points du contour (m)
CHANFREIN = (1.2, 2.8)     # coins coupés (m), pour casser la grille
TALUS = 0.16               # recul des falaises par mètre de hauteur (les strates du bas débordent)
BRUIT = 0.4                # irrégularité de chaque bloc (m)
PROFONDEUR_BLOC = 1.6      # profondeur des blocs du bord (m)
STRATE = (0.6, 1.1)        # épaisseur d'une strate (m)
PROBA_FISSURE = 0.08       # part des points du contour qui portent une fissure verticale
LARGEUR_ESCALIER = 3.6    # joues comprises
LARGEUR_JOUE = 0.4         # muret de chaque côté des marches
HAUTEUR_JOUE = 0.3         # la joue dépasse la marche de ça
JEU_ENCOCHE = 0.2          # jour entre la joue et la paroi de l'encoche
HAUTEUR_MARCHE = 0.42      # marches de Semeur : un peu hautes pour le robot (la rampe de collision lisse tout)
LONGUEUR_MARCHES = 4.6     # longueur des marches dans la case du bas (m)
PALIER = 1.8               # profondeur de l'encoche dans la falaise du haut = palier d'arrivée (m)
SOL_PAS = 1.5              # taille des facettes du dessus des plateaux (m)
SOL_RELIEF = 0.14          # bosses du sol à facettes (m) : assez pour la lumière, trop peu pour gêner
SOL_MARGE = 0.5            # distance mini entre une facette et le bord du plateau (m)

rng = random.Random(GRAINE)


# ---------------------------------------------------------------- la carte (lue dans la scène Godot)
def lire_carte():
    txt = open(SCENE_GODOT, encoding="utf-8").read()
    m = re.search(r'\[node name="Maquette".*?\ncarte = "(.*?)"\n', txt, re.S)
    lignes = [l.split() for l in m.group(1).strip().split("\n")]
    grille = {}
    for r, rang in enumerate(lignes):
        for c, j in enumerate(rang):
            if j[0] in ".~":
                continue
            estran = j[0] == "_"
            niv = -1 if estran else int(j[0])          # -1 = estran
            cx = (c - len(rang) * 0.5 + 0.5) * TAILLE_CASE
            cz = (r - len(lignes) * 0.5 + 0.5) * TAILLE_CASE
            grille[(r, c)] = {"niv": niv, "suf": j[1:], "x": cx, "y": -cz}
    return grille, len(lignes), max(len(l) for l in lignes)


def z_niveau(niv):
    return Z_ESTRAN if niv < 0 else Z_NIV0 + niv * HAUTEUR_NIVEAU


GRILLE, NB_LIGNES, NB_COLONNES = lire_carte()
Z_MAX = max(z_niveau(k["niv"]) for k in GRILLE.values())


# ---------------------------------------------------------------- scène
sc = bpy.data.scenes.get(NOM_SCENE) or bpy.data.scenes.new(NOM_SCENE)
bpy.context.window.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for me in list(bpy.data.meshes):   # meshes orphelins (sinon les noms prennent « .001 »)
    if me.users == 0:
        bpy.data.meshes.remove(me)


# ---------------------------------------------------------------- matériaux (palette île 2 : roche claire, or, bleu ciel)
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(nom, hexcol, rough=0.9):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    return m


MOUILLEE = mat("i2_roche_mouillee", "#A39D94", 0.5)
STRATES = [mat("i2_roche_grise", "#D2C8BA"), mat("i2_roche_creme", "#EEDDBF"), mat("i2_roche_claire", "#C9C1B6"),
           mat("i2_roche_ocre", "#E6C597"), mat("i2_roche_blanche", "#F4EEE3")]
BLOC = mat("i2_bloc", "#C9C2B7")
BLOC_CLAIR = mat("i2_bloc_clair", "#DDD6CA")
VARECH = mat("i2_varech", "#6F7848", 0.6)
VARECH_2 = mat("i2_varech_brun", "#8C7A46", 0.6)
HERBE = mat("i2_herbe_rase", "#A9C27C")
HERBE_2 = mat("i2_herbe_seche", "#C9C584")
HERBE_3 = mat("i2_herbe_fonce", "#98B672")
HERBE_4 = mat("i2_herbe_claire", "#B8CB86")
ROCHE_SOL = mat("i2_roche_affleurante", "#DAD2C4")
LICHEN = mat("i2_lichen", "#E6C35A")
SABLE = mat("i2_sable_mouille", "#D6C6A6", 0.35)
FLAQUE = mat("i2_flaque", "#7FC9C0", 0.05)
DALLE = mat("i2_dalle_port", "#E3DACB")
DALLE_2 = mat("i2_dalle_port_2", "#D4CABA")
DALLE_3 = mat("i2_dalle_port_3", "#C9BEAD")
SABLE_2 = mat("i2_sable_2", "#CBB994", 0.35)
SABLE_3 = mat("i2_sable_3", "#DFD2B6", 0.35)
MARCHE = mat("i2_marche", "#E8E0D2")
MARCHE_2 = mat("i2_marche_2", "#DED4C3")
JOUE = mat("i2_joue", "#CFC6B8")
INVISIBLE = mat("i2_collision", "#FF00FF")


# ---------------------------------------------------------------- outils de mesh
class Piece:
    """Un mesh en construction avec ses matériaux par face."""

    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []

    def idx(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def objet(self):
        me = bpy.data.meshes.new(self.nom)
        self.bm.to_mesh(me)
        self.bm.free()
        for p in me.polygons:
            p.use_smooth = False
        for m in self.mats:
            me.materials.append(m)
        o = bpy.data.objects.new(self.nom, me)
        sc.collection.objects.link(o)
        return o


def prisme(p, bas, haut, z0, z1, m, m_dessus=None, fond=True):
    """Volume fermé entre un contour bas (z0) et un contour haut (z1), même nombre de points (sens trigo)."""
    bm, n = p.bm, len(bas)
    b = [bm.verts.new((x, y, z0)) for x, y in bas]
    t = [bm.verts.new((x, y, z1)) for x, y in haut]
    i = p.idx(m)
    for k in range(n):
        bm.faces.new((b[k], b[(k + 1) % n], t[(k + 1) % n], t[k])).material_index = i
    if fond:
        bm.faces.new(list(reversed(b))).material_index = i
    bm.faces.new(t).material_index = p.idx(m_dessus or m)


def caillou(p, c, r, m, aplati=0.6, n=9):
    """Bloc anguleux : enveloppe convexe de points tirés au hasard."""
    bm2 = bmesh.new()
    for _ in range(n):
        a, e = rng.uniform(0, tau), rng.uniform(-0.9, 0.9)
        bm2.verts.new((c[0] + r * cos(a) * cos(e) * rng.uniform(0.7, 1.1),
                       c[1] + r * sin(a) * cos(e) * rng.uniform(0.7, 1.1),
                       c[2] + r * aplati * (sin(e) + 0.35)))
    bmesh.ops.convex_hull(bm2, input=list(bm2.verts))
    i = p.idx(m)
    table = {v: p.bm.verts.new(v.co) for v in bm2.verts}
    for f in bm2.faces:
        try:
            p.bm.faces.new([table[v] for v in f.verts]).material_index = i
        except ValueError:
            pass
    bm2.free()


def plaque(p, cx, cy, r, z, ep, m, k=6):
    pts = [(cx + r * cos(tau * i / k + rng.uniform(-0.3, 0.3)) * rng.uniform(0.7, 1.0),
            cy + r * sin(tau * i / k + rng.uniform(-0.3, 0.3)) * rng.uniform(0.7, 1.0)) for i in range(k)]
    prisme(p, pts, pts, z, z + ep, m, fond=False)


# ---------------------------------------------------------------- contours : bord de l'union des cases
def contours(pred):
    """Boucles (sens trigo, intérieur à gauche) qui bordent l'union des cases où pred(case) est vrai."""
    d = TAILLE_CASE / 2
    aretes = {}
    for (r, c), k in GRILLE.items():
        if not pred(k):
            continue
        x, y = k["x"], k["y"]
        coins = [(x - d, y - d), (x + d, y - d), (x + d, y + d), (x - d, y + d)]
        voisins = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]   # sud, est, nord, ouest
        for i, v in enumerate(voisins):
            kv = GRILLE.get(v)
            if kv is None or not pred(kv):
                a = (round(coins[i][0], 3), round(coins[i][1], 3))
                b = (round(coins[(i + 1) % 4][0], 3), round(coins[(i + 1) % 4][1], 3))
                aretes.setdefault(a, []).append(b)
    boucles = []
    while aretes:
        depart = next(iter(aretes))
        boucle, p = [depart], depart
        while True:
            suite = aretes[p].pop()
            if not aretes[p]:
                del aretes[p]
            if suite == depart:
                break
            boucle.append(suite)
            p = suite
            if p not in aretes:
                break
        # garder seulement les coins
        coins = []
        n = len(boucle)
        for i in range(n):
            a, b, c = Vector(boucle[i - 1]), Vector(boucle[i]), Vector(boucle[(i + 1) % n])
            if abs((b - a).x * (c - b).y - (b - a).y * (c - b).x) > 1e-6:   # pas aligné : c'est un coin
                coins.append(b)
        boucles.append(coins)
    return boucles


# ---------------------------------------------------------------- escaliers
# Une flèche (^ v < >) sur une case = un escalier DANS cette case (la plus basse), qui monte vers la case
# voisine plus haute (comme dans l'ancienne maquette). Il arrive dans une ENCOCHE taillée au carré dans la
# falaise du haut : sur sa largeur, les blocs du bord sont retirés et le cœur est creusé de PALIER mètres.
DIRS = {"^": (-1, 0, (0, 1)), "v": (1, 0, (0, -1)), "<": (0, -1, (-1, 0)), ">": (0, 1, (1, 0))}


class Escalier:
    def __init__(self, k, d, zb, zh):
        self.d = d                                   # direction de la montée (2D, unitaire)
        self.lat = Vector((-d.y, d.x))               # perpendiculaire
        self.zb, self.zh = zb, zh
        self.bord = Vector((k["x"], k["y"])) + d * TAILLE_CASE / 2   # milieu du bord commun
        self.demi = LARGEUR_ESCALIER / 2 + JEU_ENCOCHE               # demi-largeur de l'encoche

    def concerne(self, z0):
        """Cet escalier traverse-t-il l'anneau de falaise qui commence à z0 ?"""
        return self.zb - 0.01 <= z0 < self.zh - 0.01

    def sur_le_bord(self, p, tol=0.05):
        return abs((p - self.bord).dot(self.d)) < tol

    def t(self, p):
        return (p - self.bord).dot(self.lat)

    def dans_encoche(self, p):
        return self.sur_le_bord(p) and abs(self.t(p)) < self.demi - 1e-3

    def bord_encoche(self, p):
        return self.sur_le_bord(p) and abs(abs(self.t(p)) - self.demi) < 1e-3

    def zone_libre(self, p, marge=1.2):
        """Zone à garder dégagée (marches + palier + abords) : pas d'éboulis ni de décor."""
        v = p - self.bord
        return abs(v.dot(self.lat)) < self.demi + marge and -(LONGUEUR_MARCHES + marge) < v.dot(self.d) < PALIER + 0.5


ESCALIERS = []
for (r, c), k in GRILLE.items():
    for ch in k["suf"]:
        if ch in DIRS:
            dr, dc, dxy = DIRS[ch]
            kv = GRILLE.get((r + dr, c + dc))
            if kv is None or z_niveau(kv["niv"]) <= z_niveau(k["niv"]):
                print("escalier ignoré (pas de case plus haute) :", r, c, ch)
                continue
            ESCALIERS.append(Escalier(k, Vector(dxy), z_niveau(k["niv"]), z_niveau(kv["niv"])))


def adoucir(coins, escs):
    """Coupe les coins (chanfrein au hasard, plus petit près d'un escalier), redécoupe tous les
    PAS_CONTOUR m, puis insère des points exacts aux deux bords de chaque encoche."""
    n = len(coins)
    pts = []
    for i in range(n):
        a, b, c = coins[i - 1], coins[i], coins[(i + 1) % n]
        ch = rng.uniform(*CHANFREIN)
        ch = min(ch, (b - a).length * 0.45, (c - b).length * 0.45)
        for e in escs:   # le chanfrein ne doit pas mordre sur l'encoche
            ch = min(ch, max(0.15, (b - e.bord).length - e.demi - 0.4))
        pts.append(b + (a - b).normalized() * ch)
        pts.append(b + (c - b).normalized() * ch)
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if (b - a).length < 1e-4:
            continue
        coupes = []
        for e in escs:
            if e.sur_le_bord(a) and e.sur_le_bord(b):
                ta, tb = e.t(a), e.t(b)
                for tc in (-e.demi, e.demi):
                    if min(ta, tb) + 0.05 < tc < max(ta, tb) - 0.05:
                        coupes.append(abs(tc - ta) / abs(tb - ta))
        jalons = sorted([0.0] + coupes + [1.0])
        for j in range(len(jalons) - 1):
            u0, u1 = jalons[j], jalons[j + 1]
            nb = max(1, round((b - a).length * (u1 - u0) / PAS_CONTOUR))
            for s in range(nb):
                out.append(a.lerp(b, u0 + (u1 - u0) * s / nb))
    return out


def normales(pts):
    n, out = len(pts), []
    for k in range(n):
        t = (pts[(k + 1) % n] - pts[k - 1]).normalized()
        out.append(Vector((t.y, -t.x)))   # vers l'extérieur
    return out


# ---------------------------------------------------------------- les falaises
roche = Piece("roche-col")
plateaux = Piece("plateaux-col")
port = Piece("port-col")
estran = Piece("estran-col")
eboulis = Piece("eboulis-col")
decor = Piece("decor")


def recul_a(z):
    return (Z_MAX - z) * TALUS


def case_a(p):
    """La case de la grille sous un point 2D (ou None pour la mer)."""
    c = math.floor(p.x / TAILLE_CASE + NB_COLONNES / 2)
    r = math.floor(-p.y / TAILLE_CASE + NB_LIGNES / 2)
    return GRILLE.get((r, c))


def dedans(p, poly):
    """Point dans un polygone (règle pair-impair)."""
    x, y, ok = p.x, p.y, False
    n = len(poly)
    for i in range(n):
        a, b = poly[i - 1], poly[i]
        if (a.y > y) != (b.y > y) and x < a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y):
            ok = not ok
    return ok


def sol_facette(p, poly, z, teintes=None, relief=None, affleurements=True):
    """Le dessus d'un plateau en facettes : une grille de triangles un peu bosselée (0 à SOL_RELIEF m),
    chaque facette d'une teinte d'herbe, avec quelques dalles de roche qui affleurent. Posée sur le cœur
    (bord rentré de SOL_MARGE) ; jamais sur un escalier ni un palier."""
    xs = [v.x for v in poly]
    ys = [v.y for v in poly]
    pas = SOL_PAS
    nx = int((max(xs) - min(xs)) / pas) + 2
    ny = int((max(ys) - min(ys)) / (pas * 0.866)) + 2
    sommets = {}
    for j in range(ny):
        for i in range(nx):
            x = min(xs) + (i + (0.5 if j % 2 else 0.0)) * pas + rng.uniform(-0.25, 0.25) * pas
            y = min(ys) + j * pas * 0.866 + rng.uniform(-0.2, 0.2) * pas
            sommets[(i, j)] = Vector((x, y))
    bm = p.bm
    verts = {}

    def v3(ij):
        if ij not in verts:
            q = sommets[ij]
            verts[ij] = bm.verts.new((q.x, q.y, z + rng.uniform(0.0, SOL_RELIEF if relief is None else relief)))
        return verts[ij]

    tris = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            if j % 2 == 0:
                tris += [((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i + 1, j + 1), (i, j + 1))]
            else:
                tris += [((i, j), (i + 1, j + 1), (i, j + 1)), ((i, j), (i + 1, j), (i + 1, j + 1))]
    for t in tris:
        pts = [sommets[ij] for ij in t]
        c = (pts[0] + pts[1] + pts[2]) / 3
        if not all(dedans(q, poly) for q in pts + [c]):
            continue
        if any(e.zone_libre(q, 0.4) for e in ESCALIERS for q in pts):
            continue
        # garder une marge avec le bord du cœur (sinon une facette déborde au-dessus d'un bloc)
        if min(min((q - v).length for v in poly) for q in pts) < SOL_MARGE:
            continue
        r = rng.random()
        if teintes:
            m = teintes[min(int(r * len(teintes)), len(teintes) - 1)]
        else:
            m = HERBE if r < 0.45 else HERBE_3 if r < 0.7 else HERBE_4 if r < 0.9 else HERBE_2
        try:
            f = bm.faces.new([v3(ij) for ij in t])
        except ValueError:
            continue
        if f.normal.z < 0:
            f.normal_flip()
        f.material_index = p.idx(m)
    # dalles de roche qui affleurent, en petits groupes
    for _ in range(int(abs(aire(poly)) / 60) if affleurements else 0):
        c = Vector((rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))))
        if not dedans(c, poly) or any(e.zone_libre(c, 1.0) for e in ESCALIERS):
            continue
        if min((c - v).length for v in poly) < 2.0:
            continue
        for _ in range(rng.randint(1, 4)):
            q = c + Vector((rng.uniform(-1.4, 1.4), rng.uniform(-1.4, 1.4)))
            r = rng.uniform(0.5, 1.1)
            k = rng.randint(4, 6)
            a0 = rng.uniform(0, tau)
            contour = [(q.x + r * cos(a0 + tau * i / k) * rng.uniform(0.7, 1.0), q.y + r * sin(a0 + tau * i / k) * rng.uniform(0.6, 1.0)) for i in range(k)]
            haut = [(x + rng.uniform(-0.08, 0.08), y + rng.uniform(-0.08, 0.08)) for x, y in contour]
            prisme(p, contour, [(q.x + (x - q.x) * 0.85, q.y + (y - q.y) * 0.85) for x, y in haut], z - 0.1,
                   z + rng.uniform(0.12, 0.3), ROCHE_SOL, fond=False)


def dallage(p, poly, z):
    """Le quai du port : des dalles de Semeur (grandes, ~1,4 m) en rangs décalés, joints creux, teintes variées."""
    xs = [v.x for v in poly]
    ys = [v.y for v in poly]
    L, l, joint = 1.6, 1.2, 0.07
    j = 0
    y = min(ys)
    while y < max(ys):
        x = min(xs) - (L / 2 if j % 2 else 0.0)
        while x < max(xs):
            q = [Vector((x + joint, y + joint)), Vector((x + L - joint, y + joint)),
                 Vector((x + L - joint, y + l - joint)), Vector((x + joint, y + l - joint))]
            c = (q[0] + q[2]) / 2
            if all(dedans(v, poly) for v in q) and min(min((v - w).length for w in poly) for v in q) > 0.3                     and not any(e.zone_libre(c, 0.3) for e in ESCALIERS):
                h = rng.uniform(0.04, 0.09)
                m = rng.choice([DALLE, DALLE, DALLE_2, DALLE_3])
                prisme(p, [(v.x, v.y) for v in q], [(v.x, v.y) for v in q], z - 0.05, z + h, m, fond=False)
            x += L
        y += l
        j += 1


def aire(poly):
    return sum(poly[i - 1].x * poly[i].y - poly[i].x * poly[i - 1].y for i in range(len(poly))) / 2


def anneau(boucle, z0, z1, m_dessus, cible, pied_mer):
    """Une bande de falaise entre z0 et z1 le long d'une boucle, en strates de blocs taillés."""
    escs = [e for e in ESCALIERS if e.concerne(z0)]
    pts = adoucir(boucle, escs)
    nrm = normales(pts)
    n = len(pts)
    # pour chaque point : l'escalier dont il est dans l'encoche (ou None) ; les bords d'encoche
    # sont des coupures obligatoires (un bloc ne passe jamais devant une encoche)
    enc = [next((e for e in escs if e.dans_encoche(pts[k])), None) for k in range(n)]
    bord_enc = [next((e for e in escs if e.bord_encoche(pts[k])), None) for k in range(n)]
    fissures = {k for k in range(n) if rng.random() < PROBA_FISSURE}
    eps, h = [], z1 - z0
    while h > 0.05:
        e = min(h, rng.uniform(*STRATE))
        if h - e < 0.35:
            e = h
        eps.append(e)
        h -= e
    z = z0
    for s, e in enumerate(eps):
        dernier = s == len(eps) - 1
        recul = recul_a(z)
        m_s = MOUILLEE if z < 0.4 else STRATES[int((z - Z_FOND) / 0.85) % len(STRATES)]
        # le cœur : contour rentré de PROFONDEUR_BLOC ; dans une encoche, creusé jusqu'à PALIER (murs droits)
        coeur = []
        for k in range(n):
            normal = pts[k] + nrm[k] * (recul - PROFONDEUR_BLOC + 0.05)
            if enc[k]:
                coeur.append(pts[k] + enc[k].d * PALIER)
            elif bord_enc[k]:
                creux = pts[k] + bord_enc[k].d * PALIER
                coeur += [normal, creux] if enc[(k + 1) % n] else [creux, normal]
            else:
                coeur.append(normal)
        prisme(cible if dernier else roche, [(p.x, p.y) for p in coeur], [(p.x, p.y) for p in coeur], z, z + e,
               m_s, m_dessus if dernier else None)
        if dernier and m_dessus is HERBE:
            sol_facette(cible, coeur, z + e)
        elif dernier and m_dessus is SABLE:
            sol_facette(cible, coeur, z + e, [SABLE, SABLE, SABLE_2, SABLE_3], 0.06, False)
        elif dernier and m_dessus is DALLE:
            dallage(cible, coeur, z + e)
        # les blocs du bord (jamais à cheval sur une encoche)
        k = rng.randint(0, 2)
        debut = k
        while k < debut + n:
            fin = min(k + rng.choice([1, 1, 2, 2, 3]), debut + n)
            for j in range(k + 1, fin):
                if bord_enc[j % n]:
                    fin = j
                    break
            seg = [j % n for j in range(k, fin + 1)]
            k = fin
            if any(enc[j] for j in seg) or (bord_enc[seg[0]] and bord_enc[seg[-1]] and len(seg) == 2):
                continue
            d = recul + rng.uniform(-BRUIT, BRUIT)
            if any(j in fissures for j in seg):
                d -= rng.uniform(0.5, 0.9)
            hh = e + (rng.uniform(-0.12, 0.1) if not dernier else rng.uniform(-0.03, 0.05))
            ext_b = [pts[j] + nrm[j] * d for j in seg]
            ext_h = [pts[j] + nrm[j] * (d - rng.uniform(0.05, 0.2)) for j in seg]
            inte = [pts[j] + nrm[j] * (d - PROFONDEUR_BLOC) for j in reversed(seg)]
            mb = m_s if rng.random() > 0.12 else rng.choice(STRATES)
            if z < 0.4:
                mb = MOUILLEE
            dessus_bloc = None
            if dernier:   # au port, seul le dessus des cases du port est dallé ; ailleurs c'est de la roche
                dessus_bloc = m_dessus
                if m_dessus is DALLE:
                    kc = case_a((pts[seg[0]] + pts[seg[-1]]) / 2 - nrm[seg[0]] * 1.0)
                    if kc is None or kc["niv"] != 0:
                        dessus_bloc = m_s
            prisme(cible if dernier else roche, [(p.x, p.y) for p in ext_b + inte], [(p.x, p.y) for p in ext_h + inte],
                   z, z + hh, mb, dessus_bloc)
        z += e
    # pied : éboulis (et varech si le pied est dans la mer), jamais devant un escalier
    rb = recul_a(z0)
    for k in range(n):
        if any(es.zone_libre(pts[k]) for es in ESCALIERS):
            continue
        nb = rng.randint(0, 2) if pied_mer else (1 if rng.random() < 0.25 else 0)
        for _ in range(nb):
            c = pts[k] + nrm[k] * (rb + rng.uniform(-0.4, 2.0))
            if any(es.zone_libre(c) for es in ESCALIERS):
                continue
            r = rng.uniform(0.35, 1.3) if pied_mer else rng.uniform(0.25, 0.6)
            caillou(eboulis, (c.x, c.y, z0 - 0.3), r, rng.choice([BLOC, BLOC, BLOC_CLAIR, MOUILLEE]), 0.7)
        if pied_mer:   # varech : des touffes basses et plates collées au pied, découvertes à marée basse
            for _ in range(rng.randint(1, 3)):
                c = pts[k] + nrm[k] * (rb + rng.uniform(-0.2, 0.9)) + Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6)))
                if any(es.zone_libre(c) for es in ESCALIERS):
                    continue
                caillou(decor, (c.x, c.y, rng.uniform(-0.45, -0.15)), rng.uniform(0.3, 0.7), rng.choice([VARECH, VARECH_2]), 0.35, 7)


# l'estran et le pied de toute l'île : de Z_FOND à Z_ESTRAN, sur toutes les cases de terre
for b in contours(lambda k: True):
    anneau(b, Z_FOND, Z_ESTRAN, SABLE, estran, True)
# le port (niveau 0) et les niveaux au-dessus
niv_max = max(k["niv"] for k in GRILLE.values())
for niv in range(0, niv_max + 1):
    z0 = Z_ESTRAN if niv == 0 else z_niveau(niv - 1)
    for b in contours(lambda k, niv=niv: k["niv"] >= niv):
        anneau(b, z0, z_niveau(niv), DALLE if niv == 0 else HERBE, port if niv == 0 else plateaux, False)

# ---------------------------------------------------------------- escaliers (visuels), joues (collision) et rampes (collision)
# Profil : LONGUEUR_MARCHES dans la case du bas + PALIER dans l'encoche. La dernière marche sert de palier.
escaliers = Piece("escaliers")
joues = Piece("joues-col")
rampes = Piece("rampes-colonly")


def boite(p, a, b, demi_l, lat, z0, z1, m):
    """Pavé de a à b (points 2D sur l'axe), de demi-largeur demi_l (perpendiculaire lat)."""
    q = [a - lat * demi_l, b - lat * demi_l, b + lat * demi_l, a + lat * demi_l]
    if (q[1] - q[0]).x * (q[3] - q[0]).y - (q[1] - q[0]).y * (q[3] - q[0]).x < 0:
        q.reverse()   # sens trigo
    prisme(p, [(v.x, v.y) for v in q], [(v.x, v.y) for v in q], z0, z1, m)


for e in ESCALIERS:
    d, lat = e.d, e.lat
    h = e.zh - e.zb
    nb = max(2, round(h / HAUTEUR_MARCHE))
    haut_m = h / nb
    debut = e.bord - d * LONGUEUR_MARCHES
    fin = e.bord + d * PALIER
    giron = (LONGUEUR_MARCHES + PALIER - 0.9) / nb      # la dernière marche est plus longue : c'est le palier
    demi_marche = LARGEUR_ESCALIER / 2 - LARGEUR_JOUE
    for i in range(nb):
        a = debut + d * (i * giron)
        z_haut = e.zb + haut_m * (i + 1)
        boite(escaliers, a, fin + d * 0.25, demi_marche, lat, e.zb - 0.3 if i == 0 else e.zb + haut_m * i, z_haut,
              MARCHE if i % 2 == 0 else MARCHE_2)
        # joues : un muret de chaque côté, un peu plus haut que la marche
        b = a + d * giron if i < nb - 1 else fin
        for cote in (-1, 1):
            off = lat * cote * (LARGEUR_ESCALIER / 2 - LARGEUR_JOUE / 2)
            boite(joues, a + off, b + off, LARGEUR_JOUE / 2, lat, e.zb - 0.3, min(z_haut + HAUTEUR_JOUE, e.zh + 0.1), JOUE)
    # rampe (collision seule) : un plan qui passe au milieu de chaque marche, puis plat sur le palier
    x0 = -giron / 2                                      # abscisse (depuis « debut ») où la rampe touche le sol
    x1 = (nb - 1) * giron + giron / 2                    # où elle atteint le haut
    xf = LONGUEUR_MARCHES + PALIER + 0.3
    prof = [(x0, e.zb - 0.02), (x1, e.zh), (xf, e.zh), (xf, e.zb - 0.8), (x0, e.zb - 0.8)]
    bm = rampes.bm
    g = [bm.verts.new((*(debut + d * x - lat * demi_marche), zz)) for x, zz in prof]
    dr = [bm.verts.new((*(debut + d * x + lat * demi_marche), zz)) for x, zz in prof]
    i_m = rampes.idx(INVISIBLE)
    for j in range(len(prof)):
        bm.faces.new((g[j], g[(j + 1) % len(prof)], dr[(j + 1) % len(prof)], dr[j])).material_index = i_m
    bm.faces.new(g).material_index = i_m
    bm.faces.new(list(reversed(dr))).material_index = i_m
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[-(len(prof) + 2):])

# ---------------------------------------------------------------- le dessus : herbe sèche, lichen, pierres ; dalles du port ; flaques
d = TAILLE_CASE / 2


def libre(x, y):
    """Pas de décor sur les marches, les paliers et leurs abords."""
    return not any(e.zone_libre(Vector((x, y)), 0.6) for e in ESCALIERS)


def au_hasard(k, f):
    """Un point au hasard dans la case k (f = part de la demi-case utilisée), ou None s'il gêne un escalier."""
    x, y = k["x"] + rng.uniform(-d, d) * f, k["y"] + rng.uniform(-d, d) * f
    return (x, y) if libre(x, y) else None


for (r, c), k in GRILLE.items():
    z = z_niveau(k["niv"])
    if any(ch in DIRS for ch in k["suf"]):
        continue
    if k["niv"] >= 1:
        for _ in range(rng.randint(0, 2)):   # lichen doré (au-dessus des bosses du sol à facettes)
            p = au_hasard(k, 0.7)
            if p:
                plaque(decor, *p, rng.uniform(0.3, 0.8), z + SOL_RELIEF - 0.02, 0.03, LICHEN)
        for _ in range(rng.randint(0, 2)):   # pierres posées (avec collision : on les contourne)
            p = au_hasard(k, 0.75)
            if p:
                caillou(eboulis, (*p, z), rng.uniform(0.25, 0.55), BLOC_CLAIR, 0.5)
    elif k["niv"] == 0:   # le port : quelques dalles d'une autre teinte
        for _ in range(rng.randint(3, 6)):
            p = au_hasard(k, 0.85)
            if p:
                x, y = p
                s_ = rng.uniform(0.6, 1.1)
                q = [(x - s_, y - s_ * 0.7), (x + s_, y - s_ * 0.7), (x + s_, y + s_ * 0.7), (x - s_, y + s_ * 0.7)]
                prisme(decor, q, q, z, z + 0.03, DALLE_2, fond=False)
    else:                 # l'estran : flaques et cailloux
        if "S" in k["suf"]:
            plaque(decor, k["x"], k["y"], 2.4, z, 0.02, FLAQUE, 7)
        for _ in range(rng.randint(1, 2)):
            p = au_hasard(k, 0.6)
            if p and rng.random() < 0.5:
                plaque(decor, *p, rng.uniform(0.7, 1.6), z, 0.02, FLAQUE)
        for _ in range(rng.randint(3, 7)):   # petits cailloux (sans collision : on marche dessus)
            p = au_hasard(k, 0.9)
            if p:
                caillou(decor, (*p, z - 0.05), rng.uniform(0.12, 0.3), rng.choice([BLOC, MOUILLEE, BLOC_CLAIR]), 0.6)

objets = [p.objet() for p in (roche, plateaux, port, estran, eboulis, decor, escaliers, joues, rampes)]

# Coordonnées Blender, communes à l'instance EntreeGrottes dans la maquette.
# Les deux volumes suivent le couloir puis l'élargissement de la crypte.
VIDES_GROTTES = [
    ((-16.24, -9.00, 0.15), (-10.05, 1.27, 3.96)),
    ((-15.55, 0.74, 0.15), (-6.52, 10.05, 5.48)),
]
CANIVEAU_GROTTES = ((-11.79, 3.42, -0.66), (-10.11, 9.76, 0.3))
PUITS_GROTTES = ((-9.25, 4.35, 2.70), (-7.05, 6.65, 8.3))
APPROCHE_GROTTES = ((-16.05, -11.35, -1.3), (-11.96, -6.22, 1.85))
COUVERTURE_GROTTES = ((-17.48, -9.00, 1.85), (-3.18, 10.65, 9.0))


def partager_polygone(points, axe, limite, signe):
    """Découpe un polygone convexe par un plan, en conservant son orientation."""
    dedans, dehors = [], []
    a = points[-1]
    da = signe * (a[axe] - limite)
    for b in points:
        db = signe * (b[axe] - limite)
        if (da >= 0) != (db >= 0):
            coupe = a.lerp(b, da / (da - db))
            dedans.append(coupe)
            dehors.append(coupe)
        (dedans if db >= 0 else dehors).append(b)
        a, da = b, db
    return dedans, dehors


def partager_boite(points, boite):
    """Renvoie la partie contenue et les morceaux restés à l'extérieur."""
    bas, haut = boite
    if any(max(p[i] for p in points) < bas[i] or min(p[i] for p in points) > haut[i] for i in range(3)):
        return [], [points]
    restes = []
    for i in range(3):
        for limite, signe in ((bas[i], 1), (haut[i], -1)):
            points, bord = partager_polygone(points, i, limite, signe)
            if len(bord) >= 3:
                restes.append(bord)
            if len(points) < 3:
                return [], restes
    return points, restes


def maillage_decoupe(nom, polygones, materiaux):
    sommets, faces, indices, references = [], [], [], {}
    for points, matiere in polygones:
        face = []
        for p in points:
            cle = tuple(round(c, 6) for c in p)
            if cle not in references:
                references[cle] = len(sommets)
                sommets.append(tuple(p))
            indice = references[cle]
            if indice not in face:
                face.append(indice)
        for a, b in zip(face[1:], face[2:]):
            origine = Vector(sommets[face[0]])
            u = Vector(sommets[a]) - origine
            v = Vector(sommets[b]) - origine
            if u.cross(v).length_squared > 1.0e-12:
                faces.append((face[0], a, b))
                indices.append(matiere)
    mesh = bpy.data.meshes.new(nom)
    mesh.from_pydata(sommets, [], faces)
    for matiere in materiaux:
        mesh.materials.append(matiere)
    for face, indice in zip(mesh.polygons, indices):
        face.material_index = indice
    return mesh


def creuser_grottes(objet, vides, detacher_couverture=True):
    mesh = objet.data
    mesh.calc_loop_triangles()
    exterieur, couverture = [], []
    for tri in mesh.loop_triangles:
        pans = [[mesh.vertices[i].co.copy() for i in tri.vertices]]
        for boite in vides:
            pans = [reste for pan in pans for reste in partager_boite(pan, boite)[1]]
        for pan in pans:
            dessus, restes = partager_boite(pan, COUVERTURE_GROTTES) if detacher_couverture else ([], [pan])
            exterieur.extend((reste, tri.material_index) for reste in restes)
            if dessus:
                couverture.append((dessus, tri.material_index))
    materiaux = list(mesh.materials)
    objet.data = maillage_decoupe(objet.name, exterieur, materiaux)
    bpy.data.meshes.remove(mesh)
    if couverture:
        nom = "CouvertureGrottes_" + objet.name
        couvert = bpy.data.objects.new(nom, maillage_decoupe(nom, couverture, materiaux))
        sc.collection.objects.link(couvert)
        return couvert
    return None


for objet in objets[:]:
    nature = objet.name.split("-")[0]
    if nature == "estran":
        creuser_grottes(objet, [CANIVEAU_GROTTES], detacher_couverture=False)
    elif nature in ("roche", "plateaux", "port", "eboulis", "decor"):
        vides = VIDES_GROTTES + [CANIVEAU_GROTTES, PUITS_GROTTES]
        if nature in ("eboulis", "decor"):
            vides = vides + [APPROCHE_GROTTES]
        couvert = creuser_grottes(objet, vides)
        if couvert is not None:
            objets.append(couvert)


def habiller_bords_coupe():
    """Ferme les tranches du terrain, visibles lorsque le plateau s'efface."""
    mailles = [o.data for o in objets if o.name.startswith(("plateaux-", "roche-"))]
    sommets, faces = [], []
    for mesh in mailles:
        faces.extend(tuple(i + len(sommets) for i in p.vertices) for p in mesh.polygons)
        sommets.extend(v.co.copy() for v in mesh.vertices)
    terrain = BVHTree.FromPolygons(sommets, faces)
    bas, haut = COUVERTURE_GROTTES
    parois = []
    matieres = [MOUILLEE, STRATES[0], STRATES[1], STRATES[2]]
    for axe in (0, 1):
        autre = 1 - axe
        for limite, sens in ((bas[axe], -1), (haut[axe], 1)):
            longueur = haut[autre] - bas[autre]
            portions = math.ceil(longueur / 0.38)
            profil = []
            for j in range(portions + 1):
                co = Vector((0, 0, haut[2] + 0.1))
                co[axe] = limite + sens * 0.028
                co[autre] = bas[autre] + longueur * j / portions
                sol, _, _, _ = terrain.ray_cast(co, (0, 0, -1), 10)
                co[axe] = limite + sens * 0.012
                co.z = max(0.20, sol.z - 0.013) if sol else 0.20
                profil.append(co)
            for a, b in zip(profil, profil[1:]):
                if max(a.z, b.z) < 0.65:
                    continue
                for k, (plancher, plafond) in enumerate(((0.03, 0.65), (0.65, 2.05), (2.05, 3.8), (3.8, 9.0))):
                    if max(a.z, b.z) <= plancher:
                        break
                    points = [Vector((p.x, p.y, min(p.z, h))) for p, h in
                              ((a, plancher), (b, plancher), (b, plafond), (a, plafond))]
                    if (axe == 0 and sens > 0) or (axe == 1 and sens < 0):
                        points.reverse()
                    parois.append((points, k))
    nom = "TranchesGrottes"
    tranche = bpy.data.objects.new(nom, maillage_decoupe(nom, parois, matieres))
    sc.collection.objects.link(tranche)
    return tranche


objets.append(habiller_bords_coupe())

for o in objets:
    if o.name.startswith("rampes"):
        o.hide_render = True
        o.display_type = "WIRE"

# ---------------------------------------------------------------- lumière et caméra pour juger dans Blender
soleil = bpy.data.lights.new("soleil", "SUN")
soleil.energy = 5.0
soleil.angle = math.radians(2.0)
soleil.color = (1.0, 0.9, 0.78)
so = bpy.data.objects.new("soleil", soleil)
sc.collection.objects.link(so)
so.rotation_euler = (math.radians(58), 0, math.radians(-40))
cam = bpy.data.cameras.new("cam_ile")
cam.lens = 35
co = bpy.data.objects.new("cam_ile", cam)
sc.collection.objects.link(co)
co.location = (55, -85, 85)
co.rotation_euler = (Vector((0, -5, 0)) - co.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = co
mer = Piece("mer_apercu")
M = 160
prisme(mer, [(-M, -M), (M, -M), (M, M), (-M, M)], [(-M, -M), (M, -M), (M, M), (-M, M)], -1.0, -0.1, mat("i2_mer_apercu", "#69C9C4", 0.1))
mer_o = mer.objet()
if sc.world is None:
    sc.world = bpy.data.worlds.new("monde_ile02")
sc.world.use_nodes = True
fond = next(nd for nd in sc.world.node_tree.nodes if nd.type == "BACKGROUND")
fond.inputs[0].default_value = (*srgb("#CFE3EE"), 1)
fond.inputs[1].default_value = 0.8

# ---------------------------------------------------------------- export glTF (sans la mer d'aperçu, la caméra et le soleil)
os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
for o in objets:
    o.select_set(True)
bpy.context.view_layer.objects.active = objets[0]
bpy.ops.export_scene.gltf(filepath=SORTIE, export_format="GLB", use_selection=True, use_active_scene=True, export_apply=True,
                          export_yup=True, export_lights=False, export_cameras=False)
nb_faces = sum(len(o.data.polygons) for o in objets)
print("terrain île 2 :", len(GRILLE), "cases,", len(ESCALIERS), "escaliers,", nb_faces, "faces ->", SORTIE)
