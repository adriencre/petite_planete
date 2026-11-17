"""Île 1 — bâtiments des Semeurs, low-poly à facettes (DA v6), modélisés à la main dans Blender.

Lancer dans Blender :  exec(open(r"...\\tools\\blender\\batiments_ile_01.py", encoding="utf-8").read())
Crée la scène « ILE01_batiments » avec une planche : abri, atelier (entrée + intérieur),
petite lanterne, grande lanterne, lanterne du sommet, pierre-soleil, terreau + cosse.
Chaque bâtiment est un Empty racine (nom = fichier .glb) ; les pièces animées (pétales) sont
des objets séparés dont l'origine est le pivot.
Avant = -Y dans Blender (= +Z dans Godot). 1 unité = 1 m. Robot ~1,90 m, Semeurs 2,5-3 m.
"""
import bpy, bmesh, math, os
from math import cos, sin, pi, tau
from mathutils import Vector, Matrix
from contextlib import contextmanager

RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
OUT = os.path.join(RACINE, "assets", "models", "ile01")
NOM_SCENE = "ILE01_batiments"

sc = bpy.data.scenes.get(NOM_SCENE) or bpy.data.scenes.new(NOM_SCENE)
bpy.context.window.scene = sc
GARDER = {"soleil"}
for o in list(sc.objects):
    if o.name in GARDER or any(c.name == "robot_echelle" for c in o.users_collection):
        continue
    bpy.data.objects.remove(o, do_unlink=True)


# ---------------------------------------------------------------- matériaux
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(nom, hexcol, rough=0.9, metal=0.0, emit=None, force=0.0):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Emission Color"].default_value = (*srgb(emit or hexcol), 1)
    b.inputs["Emission Strength"].default_value = force if emit else 0.0
    return m


NACRE = mat("nacre", "#F1E6D6", 0.6)           # coques des Semeurs
NACRE_ROSE = mat("nacre_rose", "#EBC9C0", 0.6)  # pétales
BOIS = mat("bois_clair", "#D8B48A")            # côtes, tiges, pieds
BOIS_FONCE = mat("bois_fonce", "#A9805E")
PIERRE = mat("pierre", "#EADDCB")              # socles, dalles
ROCHE_1 = mat("roche_rose", "#E3A79E")         # strates de falaise
ROCHE_2 = mat("roche_ocre", "#E4BC8E")
ROCHE_3 = mat("roche_creme", "#F0DCC4")
ROCHE_4 = mat("roche_rose_fonce", "#CF8C86")
OR = mat("or", "#E7B04C", 0.35, 0.6)            # incrustations, anneaux
OR_LUMIERE = mat("or_lumiere", "#FFD38A", 0.3, 0.0, "#FFB948", 4.0)   # cœurs allumés
OR_ETEINT = mat("coeur_eteint", "#C9A77A", 0.5, 0.2, "#FFB948", 0.15) # cœur de lanterne éteinte
RACINE_LUMIERE = mat("racine_lumiere", "#E9C27A", 0.5, 0.0, "#FFB948", 0.0)  # Godot l'allume
CUIVRE = mat("cuivre", "#C27B4E", 0.5, 0.7)      # prises, mécanismes (comme le robot)
CUIVRE_VERT = mat("cuivre_vert", "#8FB3A0", 0.6, 0.4)
MOUSSE = mat("mousse", "#9DBB68")
MOUSSE_2 = mat("mousse_claire", "#B9CF7D")
TERREAU = mat("terreau", "#6E4C3C")
PAPIER = mat("papier", "#F7EEDC")
TISSU = mat("tissu_vert", "#7FA87A")


# ---------------------------------------------------------------- construction
class Piece:
    """Un mesh en construction (bmesh) avec ses matériaux par face."""

    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []

    @contextmanager
    def m(self, materiau):
        avant = set(self.bm.faces)
        yield self.bm
        if materiau not in self.mats:
            self.mats.append(materiau)
        i = self.mats.index(materiau)
        for f in self.bm.faces:
            if f not in avant:
                f.material_index = i

    def objet(self, parent=None, loc=(0, 0, 0)):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-5)
        me = bpy.data.meshes.new(self.nom)
        self.bm.to_mesh(me)
        self.bm.free()
        for p in me.polygons:
            p.use_smooth = False
        for mm in self.mats:
            me.materials.append(mm)
        o = bpy.data.objects.new(self.nom, me)
        sc.collection.objects.link(o)
        o.location = loc
        if parent:
            o.parent = parent
        return o


def racine(nom):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_size = 0.5
    sc.collection.objects.link(o)
    return o


def prisme(bm, n, r0, r1, h, z0=0.0, rot=0.0, c=(0, 0), ech=(1, 1), bas=True, haut=True):
    """Prisme / tronc de pyramide à n côtés (r1=0 -> pointe)."""
    cx, cy = c
    b = [bm.verts.new((cx + r0 * ech[0] * cos(rot + tau * i / n), cy + r0 * ech[1] * sin(rot + tau * i / n), z0)) for i in range(n)]
    if r1 <= 0:
        t = bm.verts.new((cx, cy, z0 + h))
        for i in range(n):
            bm.faces.new((b[i], b[(i + 1) % n], t))
    else:
        t = [bm.verts.new((cx + r1 * ech[0] * cos(rot + tau * i / n), cy + r1 * ech[1] * sin(rot + tau * i / n), z0 + h)) for i in range(n)]
        for i in range(n):
            bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
        if haut:
            bm.faces.new(t)
    if bas:
        bm.faces.new(list(reversed(b)))


def boite(bm, centre, taille, rz=0.0):
    x, y, z = (s / 2 for s in taille)
    M = Matrix.Translation(centre) @ Matrix.Rotation(rz, 4, "Z")
    v = [bm.verts.new(M @ Vector((sx * x, sy * y, sz * z))) for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in f])


def tube(bm, pts, rayons, cotes=4, fermer=True, tourne=0.0):
    """Tube à section polygonale le long d'une suite de points (côtes, tiges, racines)."""
    pts = [Vector(p) for p in pts]
    if not isinstance(rayons, (list, tuple)):
        rayons = [rayons] * len(pts)
    anneaux = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        w = t.cross(u).normalized()
        anneaux.append([bm.verts.new(p + rayons[i] * (u * cos(tourne + tau * k / cotes) + w * sin(tourne + tau * k / cotes))) for k in range(cotes)])
    for a, b in zip(anneaux, anneaux[1:]):
        for k in range(cotes):
            bm.faces.new((a[k], a[(k + 1) % cotes], b[(k + 1) % cotes], b[k]))
    if fermer:
        bm.faces.new(list(reversed(anneaux[0])))
        bm.faces.new(anneaux[-1])


def polyedre(bm, centre, ech, sub=1, rot=0.0):
    """Icosphère à facettes déformée (mousse, cristaux, rochers, têtes)."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=sub, radius=1.0)
    M = Matrix.Translation(centre) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((*ech, 1))
    _fusion(bm, tmp, M)


def ellipsoide(bm, centre, ech, u=8, v=6, zmin=-2.0, zmax=2.0):
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=u, v_segments=v, radius=1.0)
    bmesh.ops.delete(tmp, geom=[x for x in tmp.verts if x.co.z < zmin - 1e-4 or x.co.z > zmax + 1e-4], context="VERTS")
    M = Matrix.Translation(centre) @ Matrix.Diagonal((*ech, 1))
    _fusion(bm, tmp, M)


def _fusion(bm, tmp, M):
    me = bpy.data.meshes.new("_tmp")
    tmp.transform(M)
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def extrusion(bm, pts_xz, y0, y1):
    """Profil 2D (x, z) extrudé en y : découpes de portes en ogive, plaques."""
    a = [bm.verts.new((x, y0, z)) for x, z in pts_xz]
    b = [bm.verts.new((x, y1, z)) for x, z in pts_xz]
    n = len(pts_xz)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        bm.faces.new((a[i], b[i], b[(i + 1) % n], a[(i + 1) % n]))


def ogive(l, h, hp, pas=3):
    """Profil de porte en ogive (largeur l, haut des montants hp, sommet h)."""
    pts = [(-l / 2, 0), (l / 2, 0), (l / 2, hp)]
    for i in range(1, pas):
        t = i / pas
        pts.append((l / 2 * (1 - t) ** 0.8, hp + (h - hp) * sin(t * pi / 2)))
    pts.append((0, h))
    for i in range(pas - 1, 0, -1):
        t = i / pas
        pts.append((-l / 2 * (1 - t) ** 0.8, hp + (h - hp) * sin(t * pi / 2)))
    pts.append((-l / 2, hp))
    return pts


def spirale(bm, centre, u, v, tours=2.2, rmax=0.4, larg=0.035, ep=0.02, pas=40):
    """L'écriture des Semeurs : une spirale-pousse en ruban, dans le plan (u, v), normale u×v."""
    c, u, v = Vector(centre), Vector(u).normalized(), Vector(v).normalized()
    n = u.cross(v).normalized()
    pts = []
    for i in range(pas + 1):
        t = i / pas
        a = t * tours * tau
        r = rmax * (0.12 + 0.88 * t)
        pts.append(c + u * r * cos(a) + v * r * sin(a))
    pts.append(pts[-1] + (pts[-1] - pts[-2]).normalized() * rmax * 0.5)  # la tige qui part
    gauche, droite = [], []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        s = t.cross(n) * larg / 2
        gauche.append((bm.verts.new(p + s), bm.verts.new(p + s + n * ep)))
        droite.append((bm.verts.new(p - s), bm.verts.new(p - s + n * ep)))
    for i in range(len(pts) - 1):
        (g0, gh0), (g1, gh1) = gauche[i], gauche[i + 1]
        (d0, dh0), (d1, dh1) = droite[i], droite[i + 1]
        bm.faces.new((gh0, dh0, dh1, gh1))
        bm.faces.new((g0, gh0, gh1, g1))
        bm.faces.new((d1, dh1, dh0, d0))


def appliquer(piece, mods):
    """Applique des modificateurs (solidify, boolean...) à une Piece -> renvoie une nouvelle Piece."""
    o = piece.objet()
    for kind, kw in mods:
        md = o.modifiers.new(kind, kind)
        for k, val in kw.items():
            try:
                setattr(md, k, val)
            except (TypeError, AttributeError):
                pass
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    mats = list(o.data.materials)
    vieux = o.data
    bpy.data.objects.remove(o)
    bpy.data.meshes.remove(vieux)
    p = Piece(piece.nom)
    p.bm.from_mesh(me)
    p.mats = mats
    bpy.data.meshes.remove(me)
    return p


def coupeur(nom, construire):
    p = Piece(nom)
    construire(p.bm)
    o = p.objet()
    o.hide_render = o.hide_viewport = True
    return o


def ajouter(dest, src):
    """Fusionne la Piece src dans dest en gardant les matériaux."""
    me = bpy.data.meshes.new("_tmp")
    src.bm.to_mesh(me)
    src.bm.free()
    avant = set(dest.bm.faces)
    dest.bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    nouv = [f for f in dest.bm.faces if f not in avant]
    for f in nouv:
        mm = src.mats[f.material_index] if f.material_index < len(src.mats) else src.mats[0]
        if mm not in dest.mats:
            dest.mats.append(mm)
        f.material_index = dest.mats.index(mm)


def prise(bm_piece, centre, face_y=-1):
    """La prise des Semeurs (où le robot branche son câble) : plaque cuivre + 2 trous."""
    x, y, z = centre
    with bm_piece.m(CUIVRE) as bm:
        boite(bm, (x, y, z), (0.22, 0.08, 0.28))
    with bm_piece.m(TERREAU) as bm:
        for dx in (-0.05, 0.05):
            boite(bm, (x + dx, y + face_y * 0.042, z + 0.02), (0.035, 0.01, 0.07))


def mousse(bm_piece, centre, ech, rot=0.0, claire=False):
    with bm_piece.m(MOUSSE_2 if claire else MOUSSE) as bm:
        polyedre(bm, centre, ech, 1, rot)


def nettoyer_coupeurs():
    for o in list(sc.objects):
        if o.name.startswith("_coupe"):
            bpy.data.objects.remove(o, do_unlink=True)


# =================================================================== L'ABRI
def abri():
    """Coque de graine nacrée à côtes de bois, à la taille du robot. Porte en ogive vers -Y.
    Dedans : le berceau doré (sa propre ligne d'énergie), le papier d'Ysolde, l'horloge arrêtée."""
    r = racine("abri")
    RX, RY, RZ = 2.6, 2.6, 3.3

    # socle octogonal + seuil
    s = Piece("abri_socle")
    with s.m(PIERRE) as bm:
        prisme(bm, 8, 3.1, 2.95, 0.3, rot=pi / 8)
    with s.m(PIERRE) as bm:
        boite(bm, (0, -3.15, 0.08), (1.6, 0.6, 0.16))

    # coque : demi-ellipsoïde pointue, épaisse, porte découpée
    c = Piece("abri_coque")
    with c.m(NACRE) as bm:
        ellipsoide(bm, (0, 0, 0.3), (RX, RY, RZ), u=12, v=10, zmin=0.0)
        for v in bm.verts:
            if v.co.z > 0.3 + RZ * 0.92:
                v.co.z += 0.35  # pointe de graine
    c = appliquer(c, [("SOLIDIFY", dict(thickness=0.18, offset=-1.0))])
    porte = coupeur("_coupe_porte", lambda bm: extrusion(bm, [(x, z + 0.3) for x, z in ogive(1.3, 2.35, 1.6)], -3.5, -1.5))
    lucarnes = coupeur("_coupe_lucarnes", lambda bm: [
        extrusion(bm, [(x * 0.5 + 0, z * 0.5 + 1.6) for x, z in ogive(1.0, 1.0, 0.55)], -0.4, 0.4)
        for _ in [0]])
    lucarnes.rotation_euler.z = pi / 2
    lucarnes.location.x = 2.4
    c = appliquer(c, [("BOOLEAN", dict(object=porte, operation="DIFFERENCE", solver="EXACT")),
                      ("BOOLEAN", dict(object=lucarnes, operation="DIFFERENCE", solver="EXACT"))])

    # côtes de bois : 12 méridiens (sauf devant la porte), qui se rejoignent à la pointe
    with c.m(BOIS) as bm:
        for k in range(12):
            th = tau * k / 12 + pi / 12
            if abs(math.atan2(sin(th - (-pi / 2)), cos(th - (-pi / 2)))) < 0.4:
                continue
            pts = []
            for i in range(9):
                ph = (pi / 2) * i / 8 * 0.93
                pts.append((1.05 * RX * cos(ph) * cos(th), 1.05 * RY * cos(ph) * sin(th), 0.3 + RZ * sin(ph) * 1.02))
            pts.append((0, 0, 0.3 + RZ + 0.45))
            tube(bm, pts, [0.11 - 0.05 * i / 9 for i in range(10)], 4, tourne=pi / 4)
        # cadre de porte en ogive
        cadre = [(x, -RY * 0.93 - 0.12, z + 0.3) for x, z in ogive(1.55, 2.6, 1.75, 4)[2:]] + [(-0.775, -RY * 0.93 - 0.12, 0.3)]
        tube(bm, [(0.775, -RY * 0.93 - 0.12, 0.3)] + cadre, 0.1, 4)
    with c.m(OR) as bm:
        # anneau doré à la base
        tube(bm, [(1.0 * RX * cos(t), 1.0 * RY * sin(t), 0.42) for t in [tau * i / 24 - pi / 2 + 0.33 for i in range(22)]] , 0.07, 4, fermer=True)
        # spirale des Semeurs au-dessus de la porte
        spirale(bm, (0, -RY * 0.86 - 0.18, 3.05), (1, 0, 0), (0, -0.25, 1), 2.0, 0.28, 0.045, 0.03)
    # mousse sur le haut
    for (x, y, z, e, rr) in [(0.9, 0.6, 3.25, (0.7, 0.55, 0.22), 0.3), (-1.0, 0.9, 3.0, (0.6, 0.5, 0.22), 1.1),
                             (0.2, -0.8, 3.4, (0.45, 0.4, 0.18), 2.0), (1.8, -0.4, 2.2, (0.4, 0.5, 0.25), 0.5),
                             (-1.6, -1.0, 1.9, (0.35, 0.3, 0.2), 0.9), (0.0, 0.2, 3.75, (0.35, 0.35, 0.15), 0.0)]:
        mousse(c, (x, y, z), e, rr, claire=(z > 3.3))

    # veilleuse au-dessus de la porte : petite cage dorée
    v = Piece("abri_veilleuse")
    with v.m(BOIS) as bm:
        tube(bm, [(0, -RY * 0.8, 2.85), (0, -RY - 0.25, 2.95), (0, -RY - 0.45, 2.75)], 0.04, 4)
        for k in range(4):
            a = tau * k / 4 + pi / 4
            tube(bm, [(0, -RY - 0.45, 2.75)] + [(0.16 * cos(a) * sin(t), -RY - 0.45 + 0.16 * sin(a) * sin(t), 2.6 - 0.16 * cos(t))
                                                for t in (0.6, 1.3, 2.0, 2.6)], 0.018, 3, fermer=False)
    with v.m(OR_LUMIERE) as bm:
        polyedre(bm, (0, -RY - 0.45, 2.55), (0.11, 0.11, 0.13), 1)

    # l'intérieur : le berceau, son câble, le papier, l'horloge
    b = Piece("abri_berceau")
    with b.m(BOIS) as bm:
        prisme(bm, 6, 0.55, 0.4, 0.35, 0.3, c=(0, 0.7), ech=(1.0, 1.8))
    with b.m(OR) as bm:
        ellipsoide(bm, (0, 0.7, 0.95), (0.75, 1.25, 0.45), u=10, v=8, zmax=0.0)
    b = appliquer(b, [("SOLIDIFY", dict(thickness=0.06, offset=1.0))])
    with b.m(TISSU) as bm:
        ellipsoide(bm, (0, 0.7, 0.75), (0.6, 1.05, 0.1), u=10, v=4, zmin=0.0)
    with b.m(CUIVRE) as bm:  # la ligne du berceau : un câble qui plonge dans le sol
        tube(bm, [(0, 1.95, 0.75), (0, 2.15, 0.55), (0, 2.2, 0.32), (0.3, 2.1, 0.31)], 0.06, 5)
    with b.m(PAPIER) as bm:  # l'ordre d'Ysolde, posé sur un petit tabouret
        prisme(bm, 5, 0.22, 0.2, 0.45, 0.3, c=(1.05, 0.0))
    with b.m(PAPIER) as bm:
        boite(bm, (1.05, 0.0, 0.77), (0.3, 0.22, 0.012), 0.3)
    b.objet(r)

    # l'horloge arrêtée, au mur du fond
    horloge = Piece("abri_horloge")
    with horloge.m(BOIS_FONCE) as bm:
        prisme(bm, 8, 0.32, 0.3, 0.07, 0, rot=pi / 8)
    with horloge.m(OR) as bm:
        boite(bm, (0.0, 0.0, 0.08), (0.03, 0.22, 0.02))
        boite(bm, (0.08, 0.0, 0.08), (0.17, 0.025, 0.02), 0.6)
    ho = horloge.objet(r, (0, 2.2, 2.0))
    ho.rotation_euler.x = pi / 2

    s.objet(r)
    c.objet(r)
    v.objet(r)
    nettoyer_coupeurs()
    return r


# =================================================================== LANTERNES
def petales(r, nom, n, z, r_base, longueur, largeur, inclinaison, mat_ext=NACRE_ROSE):
    """Pétales à facettes, fermés. Chaque pétale = un objet dont l'origine est la charnière."""
    for k in range(n):
        a = tau * k / n
        p = Piece(f"{nom}_petale_{k + 1}")
        L, W = longueur, largeur
        with p.m(mat_ext) as bm:
            # losange épais, dressé selon +Z, dans le plan local XZ, bombé vers +Y (extérieur)
            pts = [(0, 0, 0), (W * 0.5, 0.05, L * 0.35), (W * 0.32, 0.06, L * 0.75), (0, 0.04, L),
                   (-W * 0.32, 0.06, L * 0.75), (-W * 0.5, 0.05, L * 0.35)]
            ext = [bm.verts.new((x, y + 0.03, zz)) for x, y, zz in pts]
            inn = [bm.verts.new((x * 0.9, y - 0.03, zz * 0.97)) for x, y, zz in pts]
            c_e = bm.verts.new((0, 0.13, L * 0.45))
            c_i = bm.verts.new((0, 0.02, L * 0.45))
            m_ = len(pts)
            for i in range(m_):
                bm.faces.new((ext[i], ext[(i + 1) % m_], c_e))
                bm.faces.new((inn[(i + 1) % m_], inn[i], c_i))
                bm.faces.new((ext[(i + 1) % m_], ext[i], inn[i], inn[(i + 1) % m_]))
        with p.m(OR) as bm:  # nervure dorée
            tube(bm, [(0, 0.1, L * 0.12), (0, 0.125, L * 0.45), (0, 0.08, L * 0.85)], 0.016, 3)
        o = p.objet(r, (r_base * cos(a), r_base * sin(a), z))
        # extérieur du pétale (+Y local) tourné vers l'extérieur, penché vers le centre (fermé)
        o.rotation_mode = "ZXY"
        o.rotation_euler = (-inclinaison, 0, a - pi / 2)


def coeur(r, nom, z, rayon, allume=False):
    p = Piece(f"{nom}_coeur")
    with p.m(OR_LUMIERE if allume else OR_ETEINT) as bm:
        polyedre(bm, (0, 0, 0), (rayon, rayon, rayon * 1.15), 1)
    return p.objet(r, (0, 0, z))


def petite_lanterne():
    """Lanterne-fleur (x3). ~2,1 m : la fleur fermée est à hauteur de tête du robot.
    Prise à hauteur de genou, côté -Y."""
    r = racine("lanterne_petite")
    p = Piece("lanterne_petite_pied")
    with p.m(PIERRE) as bm:
        prisme(bm, 6, 0.55, 0.45, 0.22)
        prisme(bm, 6, 0.42, 0.34, 0.28, 0.22, rot=pi / 6)
    H = 2.05  # haut de la tige
    with p.m(BOIS) as bm:  # tige en hélice à facettes, trois brins tressés
        for k in range(3):
            pts = [(0.1 * cos(tau * k / 3 + t * 2.6), 0.1 * sin(tau * k / 3 + t * 2.6), 0.45 + (H - 0.45) * t) for t in [i / 8 for i in range(9)]]
            tube(bm, pts, [0.08 - 0.025 * i / 8 for i in range(9)], 5)
        # feuilles basses
        for k in range(2):
            a = pi * k + 0.6
            tube(bm, [(0.08 * cos(a), 0.08 * sin(a), 0.9), (0.4 * cos(a), 0.4 * sin(a), 1.05), (0.6 * cos(a), 0.6 * sin(a), 0.92)], [0.05, 0.08, 0.01], 3)
    with p.m(OR) as bm:  # collerette dorée
        prisme(bm, 6, 0.16, 0.26, 0.12, H, rot=pi / 6)
    prise(p, (0, -0.37, 0.42))
    with p.m(CUIVRE) as bm:  # le câble de la prise remonte la tige
        tube(bm, [(0, -0.33, 0.55), (0, -0.2, 0.8), (0.0, -0.12, 1.2), (0, -0.13, 1.9)], 0.025, 4)
    p.objet(r)
    coeur(r, "lanterne_petite", H + 0.32, 0.17)
    petales(r, "lanterne_petite", 5, H + 0.1, 0.18, 0.68, 0.34, 0.22)
    return r


def grande_lanterne():
    """Au centre du niveau 1 : sur une ancienne fontaine. Trois racines partent vers les petites
    (matériau racine_lumiere, que Godot allume). ~4,6 m."""
    r = racine("lanterne_grande")
    p = Piece("lanterne_grande_pied")
    with p.m(PIERRE) as bm:  # bassin de fontaine octogonal, à sec
        prisme(bm, 8, 2.3, 2.2, 0.15, rot=pi / 8)
    bassin = Piece("_b")
    with bassin.m(PIERRE) as bm:
        prisme(bm, 8, 2.1, 2.1, 0.6, 0.15, rot=pi / 8, haut=True)
    creux = coupeur("_coupe_bassin", lambda bm: prisme(bm, 8, 1.8, 1.8, 1.0, 0.35, rot=pi / 8))
    bassin = appliquer(bassin, [("BOOLEAN", dict(object=creux, operation="DIFFERENCE", solver="EXACT"))])
    ajouter(p, bassin)
    with p.m(MOUSSE) as bm:  # fond du bassin envahi de mousse
        prisme(bm, 8, 1.8, 1.8, 0.05, 0.35, rot=pi / 8)
    with p.m(OR) as bm:
        spirale(bm, (0, -2.12, 0.5), (1, 0, 0), (0, 0, 1), 1.8, 0.16, 0.03, 0.02)
    with p.m(BOIS) as bm:  # tronc torsadé : 5 brins
        for k in range(5):
            pts = [(0.32 * (1 - 0.35 * t) * cos(tau * k / 5 + t * 2.6), 0.32 * (1 - 0.35 * t) * sin(tau * k / 5 + t * 2.6), 0.4 + 3.0 * t) for t in [i / 8 for i in range(9)]]
            tube(bm, pts, [0.15 - 0.06 * i / 8 for i in range(9)], 5)
    with p.m(RACINE_LUMIERE) as bm:  # les 3 racines vers les petites lanternes (120°)
        for k in range(3):
            a = tau * k / 3 + pi / 2
            pts = [(0.25 * cos(a), 0.25 * sin(a), 0.7), (1.0 * cos(a), 1.0 * sin(a), 0.62), (1.85 * cos(a), 1.85 * sin(a), 0.85),
                   (2.35 * cos(a), 2.35 * sin(a), 0.55), (2.9 * cos(a + 0.08), 2.9 * sin(a + 0.08), 0.12), (3.6 * cos(a + 0.1), 3.6 * sin(a + 0.1), 0.02)]
            tube(bm, pts, [0.2, 0.18, 0.16, 0.14, 0.11, 0.06], 5)
    with p.m(OR) as bm:
        prisme(bm, 8, 0.32, 0.5, 0.2, 3.35, rot=pi / 8)
    prise(p, (0, -2.16, 0.4))
    p.objet(r)
    coeur(r, "lanterne_grande", 4.0, 0.36)
    petales(r, "lanterne_grande", 7, 3.55, 0.36, 1.25, 0.6, 0.24)
    for k, (x, y, z, e) in enumerate([(1.3, 1.2, 0.75, (0.4, 0.3, 0.15)), (-1.5, 0.6, 0.72, (0.35, 0.3, 0.12)), (0.4, -1.75, 0.76, (0.3, 0.25, 0.1))]):
        m_ = Piece(f"lanterne_grande_mousse_{k}")
        mousse(m_, (x, y, z), e, k)
        m_.objet(r)
    nettoyer_coupeurs()
    return r


def lanterne_sommet():
    """Au sommet : trois grandes côtes courbes en trépied tiennent une cage où dort une boule d'or.
    ~5,2 m, la plus vieille lanterne de l'île."""
    r = racine("lanterne_sommet")
    p = Piece("lanterne_sommet_pied")
    with p.m(PIERRE) as bm:
        prisme(bm, 10, 2.0, 1.85, 0.3)
        prisme(bm, 10, 1.3, 1.2, 0.25, 0.3, rot=pi / 10)
    with p.m(OR) as bm:
        for k in range(3):
            a = tau * k / 3 + pi / 6
            spirale(bm, (1.55 * cos(a), 1.55 * sin(a), 0.305), (cos(a + pi / 2), sin(a + pi / 2), 0), (cos(a), sin(a), 0), 1.6, 0.2, 0.035, 0.015)
    with p.m(BOIS) as bm:
        for k in range(3):
            a = tau * k / 3 - pi / 2
            pts = []
            for i in range(10):
                t = i / 9
                rr = 1.6 * (1 - t) ** 1.3 + 0.55 * sin(t * pi) * 0.8
                pts.append((rr * cos(a + 0.5 * t), rr * sin(a + 0.5 * t), 0.3 + 5.0 * t))
            tube(bm, pts, [0.2 - 0.12 * i / 9 for i in range(10)], 5)
    with p.m(CUIVRE_VERT) as bm:  # la cage : 6 méridiens autour de la boule
        for k in range(6):
            a = tau * k / 6
            tube(bm, [(0.62 * sin(t) * cos(a), 0.62 * sin(t) * sin(a), 3.75 - 0.75 * cos(t)) for t in [i * pi / 8 for i in range(9)]], 0.035, 4, fermer=False)
        prisme(bm, 8, 0.25, 0.12, 0.25, 4.5)
        prisme(bm, 8, 0.12, 0.25, 0.2, 2.8)
    prise(p, (0, -1.32, 0.45))
    with p.m(CUIVRE) as bm:
        tube(bm, [(0, -1.25, 0.6), (0, -1.0, 0.56), (0, -0.4, 0.56), (0.0, 0.0, 0.56)], 0.04, 4)
    for k, (x, y, e) in enumerate([(1.4, 0.8, (0.6, 0.4, 0.18)), (-1.2, 1.1, (0.5, 0.45, 0.15)), (0.2, 1.5, (0.4, 0.3, 0.14))]):
        mousse(p, (x, y, 0.32), e, k)
    p.objet(r)
    coeur(r, "lanterne_sommet", 3.75, 0.45)
    return r


def pierre_soleil():
    """Un cristal d'or à facettes tenu par trois griffes de bois sur un socle. ~1,5 m.
    Le robot y approche son antenne pour la recharger."""
    r = racine("pierre_soleil")
    p = Piece("pierre_soleil_socle")
    with p.m(PIERRE) as bm:
        prisme(bm, 6, 0.6, 0.5, 0.25)
        prisme(bm, 6, 0.38, 0.3, 0.55, 0.25, rot=pi / 6)
    with p.m(BOIS) as bm:
        for k in range(3):
            a = tau * k / 3 + pi / 2
            tube(bm, [(0.25 * cos(a), 0.25 * sin(a), 0.75), (0.42 * cos(a), 0.42 * sin(a), 0.95), (0.36 * cos(a), 0.36 * sin(a), 1.25), (0.2 * cos(a), 0.2 * sin(a), 1.4)],
                 [0.07, 0.06, 0.045, 0.02], 4)
    with p.m(OR) as bm:
        spirale(bm, (0, -0.34, 0.55), (1, 0, 0), (0, -0.25, 1), 1.6, 0.13, 0.025, 0.015)
    mousse(p, (0.35, 0.3, 0.27), (0.35, 0.3, 0.1), 0.4)
    p.objet(r)
    c = Piece("pierre_soleil_cristal")
    with c.m(OR_LUMIERE) as bm:
        prisme(bm, 6, 0.0001, 0.26, 0.35, 0.0, haut=False, bas=False)
        prisme(bm, 6, 0.26, 0.0, 0.55, 0.35, bas=False)
    c.objet(r, (0, 0, 0.8))
    return r


def terreau():
    """Le terreau gravé : bac octogonal de pierre plein de terre, spirale d'or sur le bord,
    un creux au centre qui attend la graine. À côté, la cosse (fermée)."""
    r = racine("terreau")
    p = Piece("terreau_bac")
    bac = Piece("_t")
    with bac.m(PIERRE) as bm:
        prisme(bm, 8, 1.35, 1.25, 0.5, rot=pi / 8)
    creux = coupeur("_coupe_terreau", lambda bm: prisme(bm, 8, 1.05, 1.05, 1.0, 0.25, rot=pi / 8))
    bac = appliquer(bac, [("BOOLEAN", dict(object=creux, operation="DIFFERENCE", solver="EXACT"))])
    ajouter(p, bac)
    with p.m(TERREAU) as bm:
        prisme(bm, 8, 1.05, 1.0, 0.18, 0.25, rot=pi / 8)
        prisme(bm, 6, 0.45, 0.0, 0.08, 0.43)
    with p.m(OR) as bm:
        for k in range(8):
            a = tau * k / 8
            spirale(bm, (1.2 * cos(a + pi / 8), 1.2 * sin(a + pi / 8), 0.501), (cos(a + pi / 8 + pi / 2), sin(a + pi / 8 + pi / 2), 0), (cos(a + pi / 8), sin(a + pi / 8), 0), 1.4, 0.09, 0.02, 0.012, 24)
        prisme(bm, 6, 0.16, 0.12, 0.05, 0.45)
    with p.m(TERREAU) as bm:
        prisme(bm, 6, 0.1, 0.1, 0.06, 0.47)
    p.objet(r)

    # la cosse : une tige courbe, une gousse fermée en 4 valves
    cs = racine("cosse")
    cs.parent = r
    cs.location = (1.9, -0.6, 0)
    q = Piece("cosse_tige")
    with q.m(BOIS) as bm:
        tube(bm, [(0, 0, 0), (0.05, 0, 0.5), (0.2, 0, 0.95), (0.45, 0, 1.1)], [0.08, 0.06, 0.05, 0.04], 5)
        for k in range(3):
            a = tau * k / 3
            tube(bm, [(0, 0, 0.05), (0.35 * cos(a), 0.35 * sin(a), 0.12), (0.5 * cos(a + 0.3), 0.5 * sin(a + 0.3), 0.02)], [0.06, 0.05, 0.01], 3)
    q.objet(cs)
    for k in range(4):
        v = Piece(f"cosse_valve_{k + 1}")
        with v.m(MOUSSE_2) as bm:
            ellipsoide(bm, (0, 0, 0), (0.22, 0.2, 0.42), u=6, v=6)
            bmesh.ops.delete(bm, geom=[x for x in bm.verts if x.co.y < -0.04], context="VERTS")
        o = v.objet(cs, (0.5, 0, 0.75))
        o.rotation_euler.z = tau * k / 4
    g = Piece("cosse_graine")
    with g.m(OR_LUMIERE) as bm:
        polyedre(bm, (0, 0, 0), (0.1, 0.1, 0.15), 1)
    g.objet(cs, (0.5, 0, 0.75))
    nettoyer_coupeurs()
    return r


# =================================================================== L'ATELIER
def strate(bm_piece, x0, x1, y0, y1, z0, hauteurs, mats, rz=0.0):
    z = z0
    for i, h in enumerate(hauteurs):
        d = 0.15 * ((i * 37) % 5 - 2)
        with bm_piece.m(mats[i % len(mats)]) as bm:
            boite(bm, ((x0 + x1) / 2, (y0 + y1) / 2 + d * 0.5, z + h / 2), (x1 - x0 + d, y1 - y0 + abs(d), h), rz)
        z += h


def atelier_entree():
    """Derrière la cascade : un pan de falaise rose en strates, percé d'une porte de Semeur (~3,2 m),
    encadrée d'arches en côtes. Trop grande pour le robot."""
    r = racine("atelier_entree")
    p = Piece("atelier_entree_falaise")
    # strates : sous 3,6 m elles s'arrêtent de part et d'autre de la porte (pas de booléen)
    z = 0.0
    for i, h in enumerate([0.9, 0.6, 1.1, 0.5, 0.9, 0.7, 0.8]):
        d = 0.15 * ((i * 37) % 5 - 2)
        m_ = [ROCHE_1, ROCHE_2, ROCHE_3, ROCHE_4][i % 4]
        morceaux = [(-4.5 - d, 4.5 + d)] if z >= 3.6 else [(-4.5 - d, -1.05), (1.05, 4.5 + d)]
        for x0, x1 in morceaux:
            with p.m(m_) as bm:
                boite(bm, ((x0 + x1) / 2, 0.4 + d * 0.5, z + h / 2), (x1 - x0, 2.4 + abs(d), h))
        z += h
    with p.m(TERREAU) as bm:  # le noir de la grotte, et le haut de l'ogive bouché
        boite(bm, (0, 1.2, 1.8), (2.2, 0.1, 3.6))
    with p.m(ROCHE_4) as bm:
        for x, z, l in [(-0.8, 3.15, 0.5), (0.8, 3.15, 0.5), (-0.55, 3.45, 0.4), (0.55, 3.45, 0.4)]:
            boite(bm, (x, -0.2, z), (l, 1.2, 0.3 if z < 3.3 else 0.3))
    with p.m(BOIS) as bm:  # 3 arches concentriques en côtes
        for k, (l, h, y) in enumerate([(2.5, 3.8, -0.95), (2.25, 3.55, -0.85)]):
            o = ogive(l, h, h - 1.1, 5)
            pts = [(x, y, z) for x, z in o[1:]] + [(o[0][0], y, o[0][1])]
            tube(bm, pts, 0.13 - 0.03 * k, 5)
        # racines qui coulent du haut de la falaise
        for x in (-3.2, -2.1, 2.6, 3.6):
            tube(bm, [(x, -0.7, 5.5), (x + 0.2, -0.95, 4.3), (x - 0.1, -0.9, 3.0), (x + 0.1, -1.0, 1.8)], [0.12, 0.09, 0.06, 0.02], 4)
    with p.m(OR) as bm:
        spirale(bm, (0, -0.97, 4.25), (1, 0, 0), (0, 0, 1), 2.2, 0.32, 0.05, 0.03)
    with p.m(PIERRE) as bm:  # marches un peu hautes pour le robot (0,35 m)
        boite(bm, (0, -1.4, 0.175), (2.4, 0.8, 0.35))
        boite(bm, (0, -1.0, 0.45), (2.2, 0.5, 0.2))
    for k, (x, z, e) in enumerate([(-2.8, 5.65, (1.2, 0.8, 0.3)), (1.5, 5.7, (1.6, 0.9, 0.3)), (3.8, 3.2, (0.4, 0.5, 0.3)), (-4.0, 2.0, (0.35, 0.5, 0.3))]):
        mousse(p, (x, -0.3 if z > 5 else -0.85, z), e, k, claire=z > 5)
    p.objet(r)
    return r


def atelier_interieur():
    """L'atelier des robots, sous le sommet (vue en coupe : pas de plafond, mur avant ouvert).
    Salle octogonale voûtée de côtes, à l'échelle des Semeurs : établi à 1,35 m (poitrine du robot),
    le moule ouvert, les étagères de pièces, la lanterne de l'atelier, la page 7 sur l'établi."""
    r = racine("atelier_interieur")
    p = Piece("atelier_salle")
    R = 5.0
    with p.m(PIERRE) as bm:
        prisme(bm, 8, R, R, 0.2, -0.2, rot=pi / 8)
    with p.m(ROCHE_3) as bm:  # dalles du sol
        for k in range(8):
            a = tau * k / 8 + pi / 8
            boite(bm, (2.6 * cos(a), 2.6 * sin(a), 0.015), (1.4, 1.4, 0.03), a)
    # murs : 5 pans du fond (coupe ouverte vers -Y)
    for k in range(8):
        a0, a1 = tau * k / 8 + pi / 8, tau * (k + 1) / 8 + pi / 8
        milieu = (a0 + a1) / 2
        if sin(milieu) < -0.3:
            continue
        x0, y0, x1, y1 = R * cos(a0), R * sin(a0), R * cos(a1), R * sin(a1)
        L = math.hypot(x1 - x0, y1 - y0)
        hs = [0.8, 0.6, 1.0, 0.7, 0.9, 0.5]
        z = 0
        for i, h in enumerate(hs):
            with p.m([ROCHE_1, ROCHE_2, ROCHE_3, ROCHE_4][(i + k) % 4]) as bm:
                boite(bm, ((x0 + x1) / 2 * 1.04, (y0 + y1) / 2 * 1.04, z + h / 2), (L + 0.1, 0.6, h), milieu + pi / 2)
            z += h
    with p.m(BOIS) as bm:  # côtes de voûte, qui montent des piliers vers le centre
        for k in range(8):
            a = tau * k / 8 + pi / 8
            if sin(a) < -0.5:
                continue
            pts = [(R * 0.93 * cos(a), R * 0.93 * sin(a), 0)] + [((R * 0.93 - (R * 0.93) * t) * cos(a), (R * 0.93 - (R * 0.93) * t) * sin(a), 4.5 + 1.8 * sin(t * pi / 2)) for t in (0.0, 0.3, 0.6)]
            pts[1] = (R * 0.93 * cos(a), R * 0.93 * sin(a), 4.2)
            tube(bm, pts, [0.2, 0.17, 0.13, 0.1], 5)

    # l'établi : plateau à 1,35 m, pieds en racines, trop haut pour le robot
    with p.m(BOIS) as bm:
        boite(bm, (0, 3.3, 1.3), (4.4, 1.3, 0.12))
        for x in (-1.9, 1.9):
            for y in (2.8, 3.8):
                tube(bm, [(x * 1.05, y + (0.1 if y > 3 else -0.1), 0), (x, y, 0.6), (x, y, 1.25)], [0.14, 0.09, 0.1], 5)
    with p.m(BOIS_FONCE) as bm:
        boite(bm, (0, 3.9, 1.85), (4.2, 0.12, 1.0))  # dosseret à outils
    with p.m(CUIVRE) as bm:  # outils accrochés + pièces sur l'établi
        for i, x in enumerate((-1.6, -1.1, -0.6, 0.6, 1.2)):
            boite(bm, (x, 3.8, 1.95), (0.08, 0.06, 0.55 - 0.08 * (i % 2)))
        polyedre(bm, (-1.3, 3.2, 1.5), (0.22, 0.2, 0.18), 1)  # une tête vide
        tube(bm, [(0.2, 3.1, 1.4), (0.8, 3.3, 1.4)], 0.07, 5)  # un avant-bras
        prisme(bm, 10, 0.18, 0.18, 0.12, 1.36, c=(1.4, 3.0))  # l'enrouleur de câble
    with p.m(PAPIER) as bm:  # la page 7
        boite(bm, (-0.3, 2.95, 1.37), (0.32, 0.42, 0.01), 0.25)
    # étagères avec pièces de robots (à gauche)
    with p.m(BOIS) as bm:
        for z in (0.6, 1.5, 2.4):
            boite(bm, (-3.7, 1.0, z), (0.7, 2.6, 0.08), 0)
        for y in (-0.2, 2.2):
            boite(bm, (-3.7, y, 1.5), (0.7, 0.1, 3.0))
    with p.m(CUIVRE) as bm:
        for i, y in enumerate((0.2, 0.8, 1.4, 1.9)):
            polyedre(bm, (-3.7, y, 0.8), (0.2, 0.2, 0.16), 1)  # têtes
            boite(bm, (-3.7, y, 1.62), (0.12, 0.35, 0.12), 0.3 * i)  # bras
            prisme(bm, 6, 0.1, 0.1, 0.25, 2.45, c=(-3.7, y))  # articulations
    with p.m(CUIVRE_VERT) as bm:
        polyedre(bm, (-3.7, 0.5, 2.6), (0.16, 0.16, 0.13), 1)

    # le moule : une coque de robot ouverte en deux, debout, à droite
    with p.m(PIERRE) as bm:
        prisme(bm, 8, 1.0, 0.9, 0.3, 0, c=(3.0, 1.0))
    with p.m(CUIVRE) as bm:
        tube(bm, [(2.3, 1.0, 0.3), (2.3, 1.0, 2.7), (3.0, 1.0, 3.0), (3.7, 1.0, 2.7), (3.7, 1.0, 0.3)], 0.08, 5, fermer=True)
    moule = Piece("_moule")
    with moule.m(CUIVRE_VERT) as bm:
        ellipsoide(bm, (0, 0, 0), (0.55, 0.35, 1.0), u=10, v=8)
        bmesh.ops.delete(bm, geom=[x for x in bm.verts if x.co.y < -0.01], context="VERTS")
    moule = appliquer(moule, [("SOLIDIFY", dict(thickness=0.08, offset=1.0))])
    for v in moule.bm.verts:
        v.co = Matrix.Translation((3.0, 1.35, 1.45)) @ v.co
    ajouter(p, moule)
    moule2 = Piece("_moule2")
    with moule2.m(CUIVRE_VERT) as bm:
        ellipsoide(bm, (0, 0, 0), (0.55, 0.35, 1.0), u=10, v=8)
        bmesh.ops.delete(bm, geom=[x for x in bm.verts if x.co.y > 0.01], context="VERTS")
    moule2 = appliquer(moule2, [("SOLIDIFY", dict(thickness=0.08, offset=1.0))])
    for v in moule2.bm.verts:
        v.co = Matrix.Translation((3.6, 0.2, 1.45)) @ Matrix.Rotation(-1.1, 4, "Z") @ v.co
    ajouter(p, moule2)
    with p.m(OR) as bm:
        spirale(bm, (3.0, 1.0, 3.25), (1, 0, 0), (0, 0, 1), 1.8, 0.2, 0.03, 0.02)
    prise(p, (3.0, 1.85, 0.6), face_y=1)

    # la lanterne de l'atelier, suspendue au centre de la voûte
    with p.m(BOIS) as bm:
        tube(bm, [(0, 0, 6.3), (0, 0, 4.0)], 0.03, 4)
    with p.m(CUIVRE_VERT) as bm:
        for k in range(5):
            a = tau * k / 5
            tube(bm, [(0, 0, 4.0)] + [(0.3 * sin(t) * cos(a), 0.3 * sin(t) * sin(a), 3.7 - 0.3 * cos(t) + 0.0) for t in (0.7, 1.5, 2.3)] + [(0, 0, 3.4)], 0.02, 3, fermer=False)
    with p.m(OR_ETEINT) as bm:
        polyedre(bm, (0, 0, 3.7), (0.2, 0.2, 0.22), 1)
    prise(p, (1.2, 4.6, 0.5), face_y=1)
    with p.m(CUIVRE) as bm:
        tube(bm, [(1.2, 4.55, 0.65), (1.2, 4.75, 2.0), (0.6, 4.75, 4.3), (0.2, 2.0, 6.25), (0, 0, 6.3)], 0.04, 4)
    for k, (x, y, z, e) in enumerate([(-3.0, 3.5, 0.03, (0.8, 0.6, 0.06)), (2.5, 3.6, 0.03, (0.5, 0.4, 0.05)), (-1.0, 4.4, 3.8, (0.6, 0.3, 0.3))]):
        mousse(p, (x, y, z), e, k)
    p.objet(r)
    return r


# =================================================================== PLANCHE
def planche():
    pos = {
        "abri": (0, 0, 0),
        "lanterne_petite": (6.5, -1.0, 0),
        "lanterne_grande": (12.5, 0.5, 0),
        "lanterne_sommet": (20.0, 0.5, 0),
        "pierre_soleil": (6.5, 2.5, 0),
        "terreau": (25.5, 0.0, 0),
        "atelier_entree": (34.0, 1.0, 0),
        "atelier_interieur": (46.0, 1.0, 0),
    }
    faits = {"abri": abri, "lanterne_petite": petite_lanterne, "lanterne_grande": grande_lanterne,
             "lanterne_sommet": lanterne_sommet, "pierre_soleil": pierre_soleil, "terreau": terreau,
             "atelier_entree": atelier_entree, "atelier_interieur": atelier_interieur}
    for nom, fn in faits.items():
        o = fn()
        o.location = pos[nom]
    # sol de la planche (juste sous z=0 pour éviter le scintillement)
    s = Piece("_sol_planche")
    with s.m(mat("sol_planche", "#BFD88F")) as bm:
        boite(bm, (23, 0.5, -0.06), (62, 14, 0.1))
    s.objet()
    # robots pour l'échelle (instances de la collection robot_echelle, robot placé en (1.6, -4.2))
    col = bpy.data.collections.get("robot_echelle")
    if col:
        for nom, (x, y) in [("lanterne_petite", (7.6, -2.3)), ("lanterne_grande", (13.2, -3.2)), ("lanterne_sommet", (21.8, -2.0)),
                            ("terreau", (24.5, -2.4)), ("atelier_entree", (35.8, -1.7)), ("atelier_interieur", (45.6, 2.0))]:
            e = bpy.data.objects.new("robot_" + nom, None)
            e.instance_type = "COLLECTION"
            e.instance_collection = col
            sc.collection.objects.link(e)
            e.location = (x - 1.6, y + 4.2, 0)


planche()
print("ok", len(sc.objects), "objets")
