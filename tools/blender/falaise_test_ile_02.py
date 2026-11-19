"""Île 2 — morceau de falaise TEST (style « blocs taillés à facettes, strates nettes »).

But : valider le style du terrain de l'île 2 avant de refaire tout le rocher du Phare.
Lancer dans Blender :  exec(open(r"...\\tools\\blender\\falaise_test_ile_02.py", encoding="utf-8").read())
Crée la scène « ILE02_falaise_test » : un coin du rocher (≈ 18 × 12 m, 5 m de haut) en strates,
une encoche d'escalier taillé, des blocs éboulés au pied, une bande de varech, l'estran
(sable mouillé, flaques, cailloux) et un plan d'eau pour juger.
Z vers le haut, 1 unité = 1 m. Robot ~1,90 m (un repère d'échelle est posé).
Les réglages sont en haut du fichier.
"""
import bpy, bmesh, math, random
from math import cos, sin, tau
from mathutils import Vector

NOM_SCENE = "ILE02_falaise_test"
GRAINE = 7
LONGUEUR, LARGEUR = 18.0, 12.0     # emprise du plateau (m)
STRATES = [0.9, 1.1, 0.7, 1.2, 0.6, 0.5]  # épaisseur de chaque strate, du bas vers le haut (≈ 5 m)
PAS_CONTOUR = 1.6                  # distance entre deux points du contour (m)
RETRAIT = 0.35                     # chaque strate recule de ~ça par rapport à celle du dessous
BRUIT = 0.45                       # irrégularité du contour (m)
FISSURES = 6                       # nombre de fissures verticales (encoches alignées)
PROFONDEUR_BLOC = 1.6              # profondeur des blocs taillés du bord (m)

rng = random.Random(GRAINE)

sc = bpy.data.scenes.get(NOM_SCENE) or bpy.data.scenes.new(NOM_SCENE)
bpy.context.window.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)


# ---------------------------------------------------------------- matériaux (palette île 2 : roche claire, or, bleu ciel)
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(nom, hexcol, rough=0.9, emit=None, force=0.0):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        b.inputs["Emission Strength"].default_value = force
    return m


STRATE_MATS = [
    mat("i2_roche_mouillee", "#A39D94", 0.5),   # bas, mouillé par la marée
    mat("i2_roche_grise", "#D2C8BA"),
    mat("i2_roche_creme", "#EEDDBF"),
    mat("i2_roche_claire", "#C9C1B6"),
    mat("i2_roche_ocre", "#E6C597"),
    mat("i2_roche_blanche", "#F4EEE3"),
]
BLOC = mat("i2_bloc", "#C9C2B7")
BLOC_CLAIR = mat("i2_bloc_clair", "#DDD6CA")
VARECH = mat("i2_varech", "#6F7848", 0.6)
VARECH_2 = mat("i2_varech_brun", "#8C7A46", 0.6)
HERBE = mat("i2_herbe_rase", "#BCC98C")
HERBE_2 = mat("i2_herbe_seche", "#D3CF93")
LICHEN = mat("i2_lichen", "#E6C35A")
SABLE = mat("i2_sable_mouille", "#D6C6A6", 0.35)
FLAQUE = mat("i2_flaque", "#7FC9C0", 0.05)
MER = mat("i2_mer", "#69C9C4", 0.1)
MARCHE = mat("i2_marche", "#E8E0D2")
REPERE = mat("i2_repere_robot", "#F3E9D6", 0.6, "#FFC860", 0.0)


# ---------------------------------------------------------------- outils
class Piece:
    """Un mesh en construction avec ses matériaux par face."""

    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []

    def idx(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def objet(self):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-5)
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


def prisme_contour(p, pts_bas, pts_haut, z0, z1, m, m_dessus=None):
    """Volume fermé entre un contour bas (z0) et un contour haut (z1), même nombre de points."""
    bm, n = p.bm, len(pts_bas)
    b = [bm.verts.new((x, y, z0)) for x, y in pts_bas]
    t = [bm.verts.new((x, y, z1)) for x, y in pts_haut]
    i = p.idx(m)
    for k in range(n):
        f = bm.faces.new((b[k], b[(k + 1) % n], t[(k + 1) % n], t[k]))
        f.material_index = i
    f = bm.faces.new(list(reversed(b)))
    f.material_index = i
    f = bm.faces.new(t)
    f.material_index = p.idx(m_dessus or m)


def caillou(p, c, r, m, aplati=0.6, n=9):
    """Bloc anguleux : enveloppe convexe de points tirés au hasard."""
    pts = []
    for _ in range(n):
        a, e = rng.uniform(0, tau), rng.uniform(-0.9, 0.9)
        pts.append(Vector((c[0] + r * cos(a) * cos(e) * rng.uniform(0.7, 1.1),
                           c[1] + r * sin(a) * cos(e) * rng.uniform(0.7, 1.1),
                           c[2] + r * aplati * (sin(e) + 0.35))))
    bm2 = bmesh.new()
    for v in pts:
        bm2.verts.new(v)
    bmesh.ops.convex_hull(bm2, input=list(bm2.verts))
    i = p.idx(m)
    table = {}
    for v in bm2.verts:
        table[v] = p.bm.verts.new(v.co)
    for f in bm2.faces:
        try:
            nf = p.bm.faces.new([table[v] for v in f.verts])
            nf.material_index = i
        except ValueError:
            pass
    bm2.free()


def contour_base():
    """Rectangle irrégulier : points tous les PAS_CONTOUR m, poussés vers l'intérieur au hasard."""
    L, l = LONGUEUR / 2, LARGEUR / 2
    coins = [(-L, -l), (L, -l), (L, l), (-L, l)]
    pts = []
    for k in range(4):
        a, b = Vector(coins[k]), Vector(coins[(k + 1) % 4])
        nb = max(2, round((b - a).length / PAS_CONTOUR))
        for j in range(nb):
            pts.append(a.lerp(b, j / nb))
    return pts


def pousser(pts, d):
    """Décale chaque point du contour de d m vers l'extérieur (le long de la normale)."""
    n, out = len(pts), []
    for k in range(n):
        a, b = pts[k - 1], pts[(k + 1) % n]
        t = (b - a).normalized()
        nrm = Vector((t.y, -t.x))
        out.append(pts[k] + nrm * d)
    return out


# ---------------------------------------------------------------- la falaise en strates
base = contour_base()
n = len(base)
NORMALE = pousser(base, 1)  # base décalée de 1 m vers l'extérieur
fissures = rng.sample(range(n), FISSURES)
# escalier taillé : une encoche sur le grand côté sud (y = -l), vers la gauche
escalier = [k for k, v in enumerate(base) if v.y < -LARGEUR / 2 + 0.01 and -6.0 < v.x < -2.0]

falaise = Piece("falaise_test")


def point(k, d):
    """Point k du contour, décalé de d m vers l'extérieur."""
    return base[k] + (NORMALE[k] - base[k]) * d


def segments():
    """Découpe le contour en blocs de 1 à 3 intervalles (chaque bloc a son propre recul).
    L'encoche de l'escalier est toujours un segment à part (on n'y pose pas de bloc)."""
    e0, e1 = min(escalier), max(escalier)
    out, k = [], e1
    while k < e1 + n - (e1 - e0):
        m = rng.choice([1, 1, 2, 2, 3])
        fin = min(k + m, e0 + n)           # ne jamais déborder sur l'encoche
        out.append([j % n for j in range(k, fin + 1)])
        k = fin
    return out


z = 0.0
for s, h in enumerate(STRATES):
    recul = (len(STRATES) - s) * RETRAIT
    m_s = STRATE_MATS[s % len(STRATE_MATS)]
    dernier = s == len(STRATES) - 1
    # le cœur de la strate (caché par les blocs, il porte le dessus)
    coeur = [point(k, recul - PROFONDEUR_BLOC + 0.05 - (2.6 if k in escalier else 0.0)) for k in range(n)]
    prisme_contour(falaise, [(p.x, p.y) for p in coeur], [(p.x, p.y) for p in coeur], z, z + h, m_s,
                   HERBE if dernier else None)
    # les blocs taillés du bord, chacun avec son recul et sa hauteur
    for seg in segments():
        d = recul + rng.uniform(-BRUIT, BRUIT)
        if any(k in fissures for k in seg):
            d -= rng.uniform(0.5, 0.9)          # fissure verticale (même endroit à chaque strate)
        hh = h + rng.uniform(-0.12, 0.1) if not dernier else h + rng.uniform(-0.05, 0.05)
        ext_b = [point(k, d) for k in seg]
        ext_h = [point(k, d - rng.uniform(0.05, 0.2)) for k in seg]   # le haut du bloc recule un peu
        inte = [point(k, d - PROFONDEUR_BLOC) for k in reversed(seg)]
        mb = m_s if rng.random() > 0.12 else rng.choice(STRATE_MATS)   # quelques blocs d'une autre teinte
        prisme_contour(falaise, [(p.x, p.y) for p in ext_b + inte], [(p.x, p.y) for p in ext_h + inte],
                       z, z + hh, mb, HERBE if dernier else None)
    z += h
HAUT = z
falaise.objet()

# ---------------------------------------------------------------- dessus : touffes d'herbe sèche et lichen (plaques à facettes)
dessus = Piece("dessus_test")
for _ in range(26):
    cx, cy = rng.uniform(-LONGUEUR / 2 + 2, LONGUEUR / 2 - 2), rng.uniform(-LARGEUR / 2 + 2, LARGEUR / 2 - 2)
    r = rng.uniform(0.4, 1.3)
    k = rng.randint(5, 7)
    pts = [(cx + r * cos(tau * i / k + rng.uniform(-0.3, 0.3)) * rng.uniform(0.7, 1.0),
            cy + r * sin(tau * i / k + rng.uniform(-0.3, 0.3)) * rng.uniform(0.7, 1.0)) for i in range(k)]
    m = rng.choice([HERBE_2, HERBE_2, LICHEN])
    prisme_contour(dessus, pts, pts, HAUT, HAUT + rng.uniform(0.03, 0.08), m)
for _ in range(7):   # quelques pierres posées sur le plateau
    caillou(dessus, (rng.uniform(-7, 7), rng.uniform(-4, 4), HAUT), rng.uniform(0.25, 0.6), BLOC_CLAIR, 0.5)
dessus.objet()

# ---------------------------------------------------------------- l'escalier taillé (marches de Semeurs : un peu hautes)
marches = Piece("escalier_test")
xs = [base[k].x for k in escalier]
x0, x1 = min(xs) + 0.15, max(xs) - 0.15
nb = 9                                   # marches de Semeur : ~0,55 m de haut
y_bas, y_haut = -LARGEUR / 2 - len(STRATES) * RETRAIT - 1.0, -LARGEUR / 2 + 3.6
prof = (y_haut - y_bas) / nb
for i in range(nb):
    zz = HAUT * (i + 1) / nb
    y0 = y_bas + i * prof
    pts = [(x0, y0), (x1, y0), (x1, y_haut + 0.4), (x0, y_haut + 0.4)]
    prisme_contour(marches, pts, pts, -0.4 if i == 0 else HAUT * i / nb, zz, MARCHE, MARCHE)
marches.objet()

# ---------------------------------------------------------------- pied de falaise : blocs éboulés et varech
pied = Piece("eboulis_test")
contour_pied = pousser(base, 0.9 + len(STRATES) * RETRAIT)
for k, v in enumerate(contour_pied):
    if k in escalier:
        continue
    for _ in range(rng.randint(1, 3)):
        d = rng.uniform(-0.6, 2.2)
        c = v + (NORMALE[k] - base[k]) * d
        caillou(pied, (c.x, c.y, -0.35), rng.uniform(0.35, 1.3), rng.choice([BLOC, BLOC, STRATE_MATS[0]]), 0.7)
# bande de varech : plaques collées au pied de la falaise, entre -0.4 et +0.35 m
d0 = len(STRATES) * RETRAIT
for k in range(n):
    if k in escalier or rng.random() < 0.25:
        continue
    k2 = (k + 1) % n
    pts = [point(k, d0 + 0.35), point(k2, d0 + 0.35), point(k2, d0 - 0.4), point(k, d0 - 0.4)]
    prisme_contour(pied, [(p.x, p.y) for p in pts], [(p.x, p.y) for p in pts], -0.4,
                   rng.uniform(0.05, 0.35), rng.choice([VARECH, VARECH_2]))
pied.objet()

# ---------------------------------------------------------------- l'estran : sable mouillé, flaques, cailloux, et la mer
estran = Piece("estran_test")
contour_estran = pousser(base, 6.0)
pts = [(v.x + rng.uniform(-0.8, 0.8), v.y + rng.uniform(-0.8, 0.8)) for v in contour_estran]
prisme_contour(estran, pts, pts, -0.9, -0.35, SABLE)
for _ in range(7):
    a = rng.uniform(0, tau)
    rx, ry = LONGUEUR / 2 + 3.5, LARGEUR / 2 + 3.5
    cx, cy = rx * cos(a), ry * sin(a)
    r = rng.uniform(1.2, 2.4)
    k = 6
    fl = [(cx + r * cos(tau * i / k) * rng.uniform(0.6, 1.0), cy + r * 0.7 * sin(tau * i / k) * rng.uniform(0.6, 1.0)) for i in range(k)]
    prisme_contour(estran, fl, fl, -0.36, -0.32, FLAQUE)
for _ in range(40):
    a = rng.uniform(0, tau)
    rr = rng.uniform(1.0, 1.35)
    caillou(estran, ((LONGUEUR / 2 + 1.5) * rr * cos(a), (LARGEUR / 2 + 1.5) * rr * sin(a), -0.4),
            rng.uniform(0.12, 0.35), rng.choice([BLOC, STRATE_MATS[0], BLOC_CLAIR]), 0.6)
estran.objet()

mer = Piece("mer_test")
M = 40
prisme_contour(mer, [(-M, -M), (M, -M), (M, M), (-M, M)], [(-M, -M), (M, -M), (M, M), (-M, M)], -1.2, -0.6, MER)
mer.objet()

# ---------------------------------------------------------------- repère d'échelle : un robot de 1,90 m en haut de l'escalier
rep = Piece("repere_robot_1m90")
c = ((x0 + x1) / 2, y_haut + 1.2)
prisme_contour(rep, [(c[0] - 0.35, c[1] - 0.3), (c[0] + 0.35, c[1] - 0.3), (c[0] + 0.35, c[1] + 0.3), (c[0] - 0.35, c[1] + 0.3)],
               [(c[0] - 0.3, c[1] - 0.25), (c[0] + 0.3, c[1] - 0.25), (c[0] + 0.3, c[1] + 0.25), (c[0] - 0.3, c[1] + 0.25)],
               HAUT, HAUT + 1.9, REPERE)
rep.objet()

# ---------------------------------------------------------------- lumière et caméra de jugement (vue de dessus inclinée, comme le jeu)
soleil = bpy.data.lights.new("soleil_test", "SUN")
soleil.energy = 5.0
soleil.angle = math.radians(2.0)
soleil.color = (1.0, 0.9, 0.78)
so = bpy.data.objects.new("soleil_test", soleil)
sc.collection.objects.link(so)
so.rotation_euler = (math.radians(62), 0, math.radians(-40))  # soleil rasant de fin d'après-midi

cam = bpy.data.cameras.new("cam_test")
cam.lens = 40
co = bpy.data.objects.new("cam_test", cam)
sc.collection.objects.link(co)
co.location = (20, -34, 32)
d = Vector((0, 0, 2)) - co.location
co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
sc.camera = co

if sc.world is None:
    sc.world = bpy.data.worlds.new("monde_test")
sc.world.use_nodes = True
fond = next(nd for nd in sc.world.node_tree.nodes if nd.type == "BACKGROUND")
fond.inputs[0].default_value = (*srgb("#CFE3EE"), 1)
fond.inputs[1].default_value = 0.8

print("falaise test : hauteur", round(HAUT, 2), "m, contour", n, "points")
