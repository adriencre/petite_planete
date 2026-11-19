"""Île 2 — le Grand Phare (ILE_02_PHARE.md §3 « Le Phare, de bas en haut » ; image d'ambiance
concept/ile_02_phare_v1.png validée le 2026-11-19 avec ses ajustements).

À l'échelle des Semeurs (2,5-3 m) : une tour de ~7,8 m de diamètre à la base, 25 m avec le dôme.
Lancer dans Blender :  exec(open(r"...\\tools\\blender\\phare.py", encoding="utf-8").read())
Crée la scène « ILE02_phare » et exporte assets/models/ile02/phare.glb.

Repère : origine = centre de la tour, au niveau du plateau (Godot : 3,5 ; 8,1 ; -8,0). Z vers le haut.
X = est, Y = nord (Godot Z = -Y). La porte regarde le sud (vers la caméra et l'escalier qui monte du rocher).

Étages (sol intérieur) : 0 = salle des machines, 1 = bureau d'Iris, 2 = salle des cartes, 3 = salle de veille,
puis la galerie et la lanterne. Un escalier en colimaçon le long du mur relie les étages (rampe de collision).

Objets exportés, rangés pour la vue en coupe (scripts/phare_coupe.gd) :
  E{k}_murs_nord-col / E{k}_murs_sud-col : la maçonnerie de l'étage k (moitié nord / moitié sud, côté caméra)
  E{k}_sol-col : le plancher de l'étage k ; E{k}_escalier + E{k}_rampe-colonly ; E{k}_dedans(-col)
  Haut : galerie, lanterne, dôme, girouette (s'efface quand on est dans la tour)
  Lentille (tournera, G2/G4), Socle-col, Porte-col, Annexe-col, AnnexeToit, Echelle, Exterieur-col
"""
import bpy, bmesh, math, random, os
from math import cos, sin, tau, pi, radians
from mathutils import Vector

RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SORTIE = os.path.join(RACINE, "assets", "models", "ile02", "phare.glb")
NOM_SCENE = "ILE02_phare"
rng = random.Random(23)

# ---------------------------------------------------------------- dimensions (m)
R0, R1 = 3.9, 3.3          # rayon extérieur de la tour en bas / au sommet de la maçonnerie
EP = 0.6                   # épaisseur des murs
NS = 16                    # côtés du polygone (facettes)
BLOCS = 2                  # blocs par côté et par assise
ASSISE = 0.5
ETAGES = [0.0, 5.0, 9.5, 14.0]   # sol de chaque étage
HT = 18.0                  # haut de la maçonnerie = sol de la galerie
SOL = 0.06                 # épaisseur visible du plancher du rez (le plateau est à 0)
BANDES = [(6.0, 8.0), (12.0, 14.0), (16.6, 17.3)]   # bandes rouille (z)
PORTE = (-90.0, 2.4, 0.0, 3.8)                       # (angle°, largeur, bas, haut) : au sud
FENETRES = [(-90, 1.1, 6.2, 8.4), (30, 1.1, 6.0, 8.2), (150, 1.1, 6.4, 8.6),      # 1er
            (-30, 1.0, 10.6, 12.8), (90, 1.0, 10.8, 13.0), (210, 1.0, 10.6, 12.8),  # 2e
            (-90, 0.9, 15.0, 16.6), (60, 0.9, 15.0, 16.6), (180, 0.9, 15.0, 16.6),  # 3e (veille)
            (20, 0.9, 1.6, 3.2), (160, 0.9, 1.6, 3.2)]                              # rez (soupiraux)
ANNEXE = (-6.7, -3.7, -2.6, 3.4, 9.6)   # x0, x1, y0, y1, hauteur des murs (2 niveaux : remise + chambre)

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


def mat(nom, hexcol, rough=0.85, metal=0.0, emit=None, force=0.0, alpha=1.0):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        b.inputs["Emission Strength"].default_value = force
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    return m


CREME = [mat("ph_creme_1", "#F1E9DA"), mat("ph_creme_2", "#E8DECB"), mat("ph_creme_3", "#F6F0E5"), mat("ph_creme_4", "#DDD2BE")]
ROUILLE = [mat("ph_rouille_1", "#C4775C"), mat("ph_rouille_2", "#B86A52"), mat("ph_rouille_3", "#CF8A70"), mat("ph_rouille_pale", "#D9A28A")]
COULURE = mat("ph_coulure", "#C99A82")
SOCLE = mat("ph_socle", "#C8BEAF")
SOCLE_2 = mat("ph_socle_2", "#B9AE9D")
MOULURE = mat("ph_moulure", "#F8F3EA")
DALLE = mat("ph_dalle", "#DCD3C4")
DALLE_2 = mat("ph_dalle_2", "#CFC5B4")
BOIS = mat("ph_bois", "#B98654")
BOIS_F = mat("ph_bois_fonce", "#8E6440")
PLANCHER = [mat("ph_plancher_1", "#C9A06C"), mat("ph_plancher_2", "#BF9360"), mat("ph_plancher_3", "#D2AB78")]
FER = mat("ph_fer_forge", "#3E3A3C", 0.55, 0.4)
FER_ROUILLE = mat("ph_fer_rouille", "#7A4A34", 0.7, 0.2)
LAITON = mat("ph_laiton", "#D1A54B", 0.3, 0.8)
CUIVRE_VERT = mat("ph_cuivre_vert", "#7FB8A4", 0.55, 0.3)
CUIVRE_VERT_2 = mat("ph_cuivre_vert_2", "#6AA592", 0.55, 0.3)
CUIVRE = mat("ph_cuivre", "#C27B4E", 0.45, 0.7)
VERRE = mat("ph_verre", "#CFEFF2", 0.05, 0.0, None, 0.0, 0.28)
CRISTAL = mat("ph_cristal", "#F6E7B8", 0.08, 0.1, "#FFD78A", 0.4)
CRISTAL_2 = mat("ph_cristal_2", "#E9F3F0", 0.08, 0.1, "#FFE2A8", 0.25)
ARDOISE = [mat("ph_ardoise_1", "#6F7E88"), mat("ph_ardoise_2", "#61707A"), mat("ph_ardoise_3", "#7C8A93")]
SUIE = mat("ph_suie", "#5A5452")
ENCRE = mat("ph_encre_schema", "#3D5B78")
PLATRE = mat("ph_enduit", "#EFE6D6")
HUILE = mat("ph_tache_huile", "#7C6A58")
USURE = mat("ph_usure", "#A89880")


class Piece:
    def __init__(self, nom):
        self.nom, self.bm, self.mats = nom, bmesh.new(), []

    def idx(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def vide(self):
        return len(self.bm.faces) == 0

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


PIECES = {}


def piece(nom):
    if nom not in PIECES:
        PIECES[nom] = Piece(nom)
    return PIECES[nom]


def prisme(p, bas, haut, z0, z1, m, m_haut=None, m_bas=None):
    """Volume entre deux contours de même taille (sens trigo), bas à z0 et haut à z1."""
    bm, n = p.bm, len(bas)
    b = [bm.verts.new((x, y, z0)) for x, y in bas]
    t = [bm.verts.new((x, y, z1)) for x, y in haut]
    i = p.idx(m)
    for k in range(n):
        bm.faces.new((b[k], b[(k + 1) % n], t[(k + 1) % n], t[k])).material_index = i
    bm.faces.new(list(reversed(b))).material_index = p.idx(m_bas or m)
    bm.faces.new(t).material_index = p.idx(m_haut or m)


def boite(p, x0, x1, y0, y1, z0, z1, m, haut=None):
    q = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    prisme(p, q, q, z0, z1, m, haut)


def anneau(p, r_in, r_out, z0, z1, m, n=NS, a0=0.0, a1=tau, haut=None, decal=0.0):
    """Anneau (ou secteur d'anneau) à facettes, de a0 à a1 (radians)."""
    nseg = max(1, round(n * (a1 - a0) / tau))
    for k in range(nseg):
        u0 = a0 + (a1 - a0) * k / nseg + decal
        u1 = a0 + (a1 - a0) * (k + 1) / nseg + decal
        q = [(r_in * cos(u0), r_in * sin(u0)), (r_out * cos(u0), r_out * sin(u0)),
             (r_out * cos(u1), r_out * sin(u1)), (r_in * cos(u1), r_in * sin(u1))]
        prisme(p, q, q, z0, z1, m, haut)


def disque(p, r, z0, z1, m, n=NS, haut=None):
    q = [(r * cos(tau * k / n), r * sin(tau * k / n)) for k in range(n)]
    prisme(p, q, q, z0, z1, m, haut)


def cylindre(p, cx, cy, z0, r, h, m, n=8):
    q = [(cx + r * cos(tau * k / n), cy + r * sin(tau * k / n)) for k in range(n)]
    prisme(p, q, q, z0, z0 + h, m)


def rayon(z):
    return R0 - (R0 - R1) * min(max(z, 0.0), HT) / HT


def etage_de(z):
    k = 0
    for i, e in enumerate(ETAGES):
        if z >= e - 0.01:
            k = i
    return k


def ang_dans(a, centre_deg, demi_largeur_m, r):
    """L'angle a (rad) est-il dans l'ouverture centrée sur centre_deg, de demi-largeur (m) au rayon r ?"""
    d = math.atan2(sin(a - radians(centre_deg)), cos(a - radians(centre_deg)))
    return abs(d) * r < demi_largeur_m


# ---------------------------------------------------------------- la maçonnerie de la tour
OUVERTURES = [PORTE] + FENETRES
z = 0.0
assise = 0
while z < HT - 0.01:
    h = min(ASSISE, HT - z)
    k_etage = etage_de(z)
    r_b, r_h = rayon(z), rayon(z + h)
    dans_bande = any(b0 - 0.01 <= z < b1 - 0.01 for (b0, b1) in BANDES)
    nb = NS * BLOCS
    decal = (0.5 if assise % 2 else 0.0) * tau / nb
    for j in range(nb):
        a0 = tau * j / nb + decal
        a1 = tau * (j + 1) / nb + decal
        am = (a0 + a1) / 2
        # ouvertures : pas de bloc devant une porte ou une fenêtre
        if any(ang_dans(am, c, l / 2 + 0.05, r_b) and z < z1 - 0.01 and z + h > z0 + 0.01 for (c, l, z0, z1) in OUVERTURES):
            continue
        sail = rng.uniform(-0.025, 0.035)
        j0 = 0.012
        ob = [(r_b + sail) * cos(a0 + j0 / r_b), (r_b + sail) * sin(a0 + j0 / r_b)]
        ob2 = [(r_b + sail) * cos(a1 - j0 / r_b), (r_b + sail) * sin(a1 - j0 / r_b)]
        oh = [(r_h + sail) * cos(a0 + j0 / r_h), (r_h + sail) * sin(a0 + j0 / r_h)]
        oh2 = [(r_h + sail) * cos(a1 - j0 / r_h), (r_h + sail) * sin(a1 - j0 / r_h)]
        ri_b, ri_h = r_b - EP, r_h - EP
        ib = [(ri_b * cos(a1), ri_b * sin(a1)), (ri_b * cos(a0), ri_b * sin(a0))]
        ih = [(ri_h * cos(a1), ri_h * sin(a1)), (ri_h * cos(a0), ri_h * sin(a0))]
        if dans_bande:
            m = ROUILLE[0] if rng.random() < 0.55 else rng.choice(ROUILLE[1:])
        else:
            m = CREME[0] if rng.random() < 0.45 else rng.choice(CREME[1:])
        cote = "nord" if sin(am) >= 0 else "sud"
        p = piece(f"E{k_etage}_murs_{cote}-col")
        prisme(p, [tuple(ob), tuple(ob2)] + ib, [tuple(oh), tuple(oh2)] + ih, z + 0.012, z + h - 0.012, m, haut=m)
    z += h
    assise += 1

# enduit intérieur (un peu en retrait, continu : pas de jour entre les blocs), par étage et par moitié
for k, e0 in enumerate(ETAGES):
    e1 = ETAGES[k + 1] if k + 1 < len(ETAGES) else HT
    for cote, (a0, a1) in [("nord", (0.0, pi)), ("sud", (pi, tau))]:
        p = piece(f"E{k}_murs_{cote}-col")
        nseg = 16
        for s in range(nseg):
            u0, u1 = a0 + (a1 - a0) * s / nseg, a0 + (a1 - a0) * (s + 1) / nseg
            um = (u0 + u1) / 2
            for (z0, z1) in [(e0, e1)]:
                # trous de l'enduit aux ouvertures de cet étage
                coupes = [(c, l, zb, zh) for (c, l, zb, zh) in OUVERTURES if zb < z1 and zh > z0 and ang_dans(um, c, l / 2 + 0.05, rayon(zb) - EP)]
                bandes = [(z0, z1)]
                for (_, _, zb, zh) in coupes:
                    nouv = []
                    for (b0, b1) in bandes:
                        if zh <= b0 or zb >= b1:
                            nouv.append((b0, b1))
                        else:
                            if zb > b0:
                                nouv.append((b0, zb))
                            if zh < b1:
                                nouv.append((zh, b1))
                    bandes = nouv
                for (b0, b1) in bandes:
                    rb, rh = rayon(b0) - EP + 0.02, rayon(b1) - EP + 0.02
                    rb2, rh2 = rb + 0.15, rh + 0.15
                    q_b = [(rb * cos(u0), rb * sin(u0)), (rb2 * cos(u0), rb2 * sin(u0)), (rb2 * cos(u1), rb2 * sin(u1)), (rb * cos(u1), rb * sin(u1))]
                    q_h = [(rh * cos(u0), rh * sin(u0)), (rh2 * cos(u0), rh2 * sin(u0)), (rh2 * cos(u1), rh2 * sin(u1)), (rh * cos(u1), rh * sin(u1))]
                    prisme(p, q_b, q_h, b0, b1, PLATRE)

# moulures : un bandeau saillant à chaque plancher, un cordon sous chaque bande
for zc in ETAGES[1:] + [b1 for (_, b1) in BANDES[:2]]:
    for cote, (a0, a1) in [("nord", (0.0, pi)), ("sud", (pi, tau))]:
        k = etage_de(zc - 0.05)
        anneau(piece(f"E{k}_murs_{cote}-col"), rayon(zc) - 0.3, rayon(zc) + 0.14, zc - 0.22, zc, MOULURE, 32, a0, a1)

# coulures de rouille sous les bandes (traces verticales, légèrement en relief)
for (b0, b1) in BANDES[:2]:
    for _ in range(14):
        a = rng.uniform(0, tau)
        if any(ang_dans(a, c, l / 2 + 0.3, rayon(b0)) and zb < b0 + 0.1 and zh > b0 - 2.5 for (c, l, zb, zh) in OUVERTURES):
            continue
        lg = rng.uniform(0.6, 2.2)
        larg = rng.uniform(0.06, 0.16)
        r = rayon(b0 - lg / 2) + 0.03
        cote = "nord" if sin(a) >= 0 else "sud"
        k = etage_de(b0 - 0.1)
        z0 = b0 - lg
        q = [(r * cos(a - larg / r), r * sin(a - larg / r)), ((r + 0.02) * cos(a - larg / r), (r + 0.02) * sin(a - larg / r)),
             ((r + 0.02) * cos(a + larg / r), (r + 0.02) * sin(a + larg / r)), (r * cos(a + larg / r), r * sin(a + larg / r))]
        prisme(piece(f"E{k}_murs_{cote}-col"), q, q, z0, b0 - 0.02, COULURE)

# ---------------------------------------------------------------- le socle, la cour pavée, les marches et la porte
soc = piece("Socle-col")
anneau(soc, R0 - 0.2, R0 + 0.45, -0.4, 0.9, SOCLE, NS, haut=SOCLE_2)
anneau(soc, R0 - 0.2, R0 + 0.6, -0.4, 0.25, SOCLE_2, NS)
# la porte : le socle s'ouvre devant elle
# (le socle est un anneau plein : on le refait en secteurs, sans le secteur de la porte)
PIECES["Socle-col"] = soc = Piece("Socle-col")
ac = radians(PORTE[0])
for (rin, rout, z0, z1, m) in [(R0 - 0.2, R0 + 0.45, -0.4, 0.9, SOCLE), (R0 - 0.2, R0 + 0.6, -0.4, 0.25, SOCLE_2)]:
    nseg = 32
    for s in range(nseg):
        u0, u1 = tau * s / nseg, tau * (s + 1) / nseg
        if ang_dans((u0 + u1) / 2, PORTE[0], PORTE[1] / 2 + 0.6, R0):
            continue
        q = [(rin * cos(u0), rin * sin(u0)), (rout * cos(u0), rout * sin(u0)), (rout * cos(u1), rout * sin(u1)), (rin * cos(u1), rin * sin(u1))]
        prisme(soc, q, q, z0, z1, m, SOCLE_2 if m is SOCLE else None)
# la cour : un anneau de dalles autour de la tour (à fleur du plateau)
cour = piece("Exterieur-col")
for s in range(40):
    u0, u1 = tau * s / 40, tau * (s + 1) / 40
    for (r0_, r1_) in [(R0 + 0.6, R0 + 1.5), (R0 + 1.5, R0 + 2.3)]:
        if ang_dans((u0 + u1) / 2, -170, 3.6, R0) and r0_ > R0 + 1.0:
            continue   # côté annexe
        jit = 0.03
        q = [(r0_ * cos(u0 + jit), r0_ * sin(u0 + jit)), (r1_ * cos(u0 + jit), r1_ * sin(u0 + jit)),
             (r1_ * cos(u1 - jit), r1_ * sin(u1 - jit)), (r0_ * cos(u1 - jit), r0_ * sin(u1 - jit))]
        prisme(cour, q, q, -0.1, rng.uniform(0.03, 0.05), DALLE if rng.random() < 0.7 else DALLE_2)
# le perron : trois marches larges devant la porte (au sud), rampe de collision dessous
for i, (dy, hz) in enumerate([(1.6, 0.05), (1.1, 0.1), (0.6, 0.15)]):
    y0 = -R0 - dy
    boite(cour, -1.9 + i * 0.12, 1.9 - i * 0.12, y0 - 0.5, -R0 + 0.3, -0.1, hz, DALLE_2 if i % 2 else DALLE)
ramp = piece("Rampe_porte-colonly")
bm = ramp.bm
v = [bm.verts.new(c) for c in [(-1.6, -R0 - 2.3, -0.02), (1.6, -R0 - 2.3, -0.02), (1.6, -R0 + 0.5, SOL), (-1.6, -R0 + 0.5, SOL),
                                (-1.6, -R0 - 2.3, -0.4), (1.6, -R0 - 2.3, -0.4), (1.6, -R0 + 0.5, -0.4), (-1.6, -R0 + 0.5, -0.4)]]
for f in [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]:
    bm.faces.new([v[j] for j in f]).material_index = ramp.idx(SOCLE)

porte = piece("Porte-col")
_, pl, pb, ph = PORTE
yf = -R0 - 0.05
# pilastres, entablement, fronton triangulaire, clé de voûte
for s in (-1, 1):
    boite(porte, s * (pl / 2 + 0.05) - 0.3, s * (pl / 2 + 0.05) + 0.3, yf - 0.35, yf + 0.5, 0.0, ph + 0.1, MOULURE)
    boite(porte, s * (pl / 2 + 0.05) - 0.38, s * (pl / 2 + 0.05) + 0.38, yf - 0.42, yf + 0.5, 0.0, 0.5, SOCLE)      # base
    boite(porte, s * (pl / 2 + 0.05) - 0.36, s * (pl / 2 + 0.05) + 0.36, yf - 0.42, yf + 0.5, ph - 0.1, ph + 0.15, MOULURE)  # chapiteau
boite(porte, -pl / 2 - 0.55, pl / 2 + 0.55, yf - 0.45, yf + 0.5, ph + 0.15, ph + 0.6, MOULURE)
boite(porte, -pl / 2 - 0.65, pl / 2 + 0.65, yf - 0.55, yf + 0.5, ph + 0.6, ph + 0.72, CREME[3])
fr = [(-pl / 2 - 0.65, ph + 0.72), (pl / 2 + 0.65, ph + 0.72), (0.0, ph + 1.85)]
bm = porte.bm
for ep in [(yf - 0.5, yf + 0.5)]:
    vv = [bm.verts.new((x, ep[0], zz)) for x, zz in fr] + [bm.verts.new((x, ep[1], zz)) for x, zz in fr]
    i = porte.idx(MOULURE)
    bm.faces.new([vv[0], vv[1], vv[2]]).material_index = i
    bm.faces.new([vv[5], vv[4], vv[3]]).material_index = i
    for a_, b_ in [(0, 1), (1, 2), (2, 0)]:
        bm.faces.new([vv[a_], vv[a_ + 3], vv[b_ + 3], vv[b_]]).material_index = porte.idx(CREME[1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[-5:])
cylindre(porte, 0, yf - 0.52, ph + 1.15, 0.28, 0.06, LAITON, 10)                 # médaillon de laiton (soleil des Semeurs)
for k in range(8):
    a = tau * k / 8
    boite(porte, 0.36 * cos(a) - 0.04, 0.36 * cos(a) + 0.04, yf - 0.56, yf - 0.5, ph + 1.15 + 0.36 * sin(a) - 0.04, ph + 1.15 + 0.36 * sin(a) + 0.04, LAITON)
# deux battants en bois, grands ouverts vers l'intérieur, plaqués contre l'embrasure
for s in (-1, 1):
    x_gond = s * (pl / 2 - 0.05)
    for k in range(4):
        y0 = -R0 + EP * 0.3 + k * 0.28
        boite(porte, x_gond - s * 0.12, x_gond, y0, y0 + 0.26, 0.05, ph - 0.05, BOIS if k % 2 else BOIS_F)
    boite(porte, x_gond - s * 0.16, x_gond - s * 0.11, -R0 + 0.5, -R0 + 0.62, 1.7, 1.9, LAITON)    # anneau-heurtoir
    for zz in (0.6, ph - 0.7):
        boite(porte, x_gond - s * 0.14, x_gond - s * 0.11, -R0 + 0.15, -R0 + 1.1, zz, zz + 0.1, FER)


# ---------------------------------------------------------------- les fenêtres : encadrement de pierre, appui, arc
def fenetre(c_deg, l, zb, zh):
    a = radians(c_deg)
    r = rayon(zb) + 0.06
    k = etage_de(zb + 0.1)
    cote = "nord" if sin(a) >= 0 else "sud"
    p = piece(f"E{k}_cadres")
    t = Vector((-sin(a), cos(a)))     # tangente
    n = Vector((cos(a), sin(a)))      # normale extérieure
    c = n * r

    def bloc(s0, s1, z0, z1, d0, d1, m):
        q = [c + t * s0 + n * d0, c + t * s1 + n * d0, c + t * s1 + n * d1, c + t * s0 + n * d1]
        q = [(v.x, v.y) for v in q]
        if (q[1][0] - q[0][0]) * (q[3][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[3][0] - q[0][0]) < 0:
            q.reverse()
        prisme(p, q, q, z0, z1, m)
    # montants
    for s in (-1, 1):
        bloc(s * l / 2 - 0.12, s * l / 2 + 0.12, zb, zh, -EP - 0.02, 0.12, MOULURE)
    # appui saillant
    bloc(-l / 2 - 0.25, l / 2 + 0.25, zb - 0.18, zb, -EP + 0.1, 0.28, MOULURE)
    # arc : deux claveaux inclinés et une clé
    bloc(-l / 2 - 0.12, -0.12, zh, zh + 0.32, -EP - 0.02, 0.13, MOULURE)
    bloc(0.12, l / 2 + 0.12, zh, zh + 0.32, -EP - 0.02, 0.13, MOULURE)
    bloc(-0.16, 0.16, zh, zh + 0.5, -EP - 0.02, 0.18, CREME[3])
    # petits bois et vitre
    bloc(-0.03, 0.03, zb, zh, -EP * 0.5 - 0.03, -EP * 0.5 + 0.03, BOIS_F)
    bloc(-l / 2, l / 2, (zb + zh) / 2 - 0.03, (zb + zh) / 2 + 0.03, -EP * 0.5 - 0.03, -EP * 0.5 + 0.03, BOIS_F)
    bloc(-l / 2, l / 2, zb, zh, -EP * 0.5 - 0.005, -EP * 0.5 + 0.005, VERRE)


for (c_, l_, zb_, zh_) in FENETRES:
    fenetre(c_, l_, zb_, zh_)

# ---------------------------------------------------------------- les planchers et l'escalier en colimaçon
ESC_LARG = 1.5             # largeur des marches (du mur vers le centre)
ESC_TOUR = radians(300)    # chaque volée fait 300°
TROU = radians(135)        # le trou dans le plancher du dessus, au-dessus de la fin de la volée
depart = radians(-55)      # la 1re volée part à l'est de la porte et tourne dans le sens trigo
volees = []
for k in range(len(ETAGES)):
    z0 = ETAGES[k]
    z1 = ETAGES[k + 1] if k + 1 < len(ETAGES) else HT
    volees.append((k, z0, z1, depart, depart + ESC_TOUR))
    depart = depart + ESC_TOUR + radians(35)

for k, z0, z1, a0, a1 in volees:
    ri = rayon(z0) - EP
    # le plancher de l'étage k (sauf le rez : le sol du plateau, recouvert de dalles) : anneau autour du puits
    # de la chaîne, troué au-dessus de la fin de la volée précédente
    p = piece(f"E{k}_sol-col")
    if k == 0:
        disque(p, ri + 0.05, -0.1, SOL, DALLE, 32)
    else:
        trou_a0, trou_a1 = volees[k - 1][4] - TROU, volees[k - 1][4] + radians(8)
        nseg = 48
        for s in range(nseg):
            u0, u1 = tau * s / nseg, tau * (s + 1) / nseg
            um = (u0 + u1) / 2
            d = (um - trou_a0) % tau
            dans_trou = d < (trou_a1 - trou_a0)
            for (r0_, r1_) in [(0.45, ri - ESC_LARG), (ri - ESC_LARG, ri + 0.08)]:
                if dans_trou and r0_ > 0.5:
                    continue
                q = [(r0_ * cos(u0), r0_ * sin(u0)), (r1_ * cos(u0), r1_ * sin(u0)), (r1_ * cos(u1), r1_ * sin(u1)), (r0_ * cos(u1), r0_ * sin(u1))]
                prisme(p, q, q, z0 - 0.32, z0, BOIS_F, rng.choice(PLANCHER))
        # garde-corps autour du trou (côté centre)
        gc = piece(f"E{k}_dedans")
        nseg_t = 8
        for s in range(nseg_t):
            u0 = trou_a0 + (trou_a1 - trou_a0) * s / nseg_t
            u1 = trou_a0 + (trou_a1 - trou_a0) * (s + 1) / nseg_t
            rr = ri - ESC_LARG - 0.05
            q = [(rr * cos(u0), rr * sin(u0)), ((rr + 0.08) * cos(u0), (rr + 0.08) * sin(u0)), ((rr + 0.08) * cos(u1), (rr + 0.08) * sin(u1)), (rr * cos(u1), rr * sin(u1))]
            prisme(gc, q, q, z0 + 1.05, z0 + 1.15, BOIS)
            cylindre(gc, rr * cos(u0), rr * sin(u0), z0, 0.05, 1.15, FER, 6)
    # la volée : 12 marches de pierre adossées au mur ; le dessous est plein (escalier taillé)
    nb = max(8, round((z1 - z0) / 0.42))
    esc = piece(f"E{k}_escalier")
    for i in range(nb):
        u0 = a0 + (a1 - a0) * i / nb
        u1 = a0 + (a1 - a0) * (i + 1) / nb
        zt = z0 + (z1 - z0) * (i + 1) / nb
        rin, rout = ri - ESC_LARG, ri + 0.05
        q = [(rin * cos(u0), rin * sin(u0)), (rout * cos(u0), rout * sin(u0)), (rout * cos(u1), rout * sin(u1)), (rin * cos(u1), rin * sin(u1))]
        prisme(esc, q, q, z0 + (z1 - z0) * i / nb - (0.4 if i else 0.0), zt, CREME[1] if i % 2 else CREME[3], DALLE if i % 2 else DALLE_2)
    # main courante en fer sur le bord intérieur
    for i in range(nb):
        u = a0 + (a1 - a0) * (i + 0.5) / nb
        zt = z0 + (z1 - z0) * (i + 1) / nb
        cylindre(esc, (ri - ESC_LARG + 0.08) * cos(u), (ri - ESC_LARG + 0.08) * sin(u), zt, 0.035, 1.0, FER, 5)
    # rampe de collision : une hélice lisse qui passe au milieu des marches
    rp = piece(f"E{k}_rampe-colonly")
    bm = rp.bm
    ns = nb * 3
    anc = None
    for i in range(ns + 1):
        f = i / ns
        u = a0 + (a1 - a0) * f
        zz = z0 + (z1 - z0) * min(1.0, max(0.0, (f * nb - 0.5) / (nb - 1)))
        cur = [bm.verts.new(((ri - ESC_LARG + 0.05) * cos(u), (ri - ESC_LARG + 0.05) * sin(u), zz)),
               bm.verts.new(((ri - 0.02) * cos(u), (ri - 0.02) * sin(u), zz))]
        if anc:
            bm.faces.new((anc[0], anc[1], cur[1], cur[0])).material_index = rp.idx(SOCLE)
        anc = cur
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for fc in bm.faces:
        if fc.normal.z < 0:
            fc.normal_flip()

# ---------------------------------------------------------------- la salle des machines (rez) : G4
mach = piece("E0_dedans-col")
mach_d = piece("E0_dedans")
# le puits central : la chaîne de la lentille descend jusqu'au tambour
cylindre(mach, 0, 0, SOL, 0.55, 0.5, FER, 10)
cylindre(mach_d, 0, 0, SOL + 0.5, 0.42, 1.0, LAITON, 12)             # tambour
cylindre(mach_d, 0, 0, SOL + 1.5, 0.08, ETAGES[1] - 1.5, FER, 6)     # arbre vertical
for i in range(int((HT - 1.6) / 0.22)):                              # la chaîne : maillons alternés
    zz = 1.6 + i * 0.22
    if i % 2:
        boite(mach_d, 0.13, 0.17, -0.07, 0.07, zz, zz + 0.2, FER_ROUILLE)
    else:
        boite(mach_d, 0.08, 0.22, -0.02, 0.02, zz, zz + 0.2, FER_ROUILLE)


def engrenage(p, cx, cy, z0, r, ep, dents, m, couche=False, angle=0.0):
    """Roue dentée à facettes. Couchée (couche=True) ou debout ; ici toujours à plat, pour simplifier."""
    cylindre(p, cx, cy, z0, r, ep, m, max(10, dents))
    for d in range(dents):
        a = angle + tau * d / dents
        x, y = cx + (r + 0.07) * cos(a), cy + (r + 0.07) * sin(a)
        q = [(x - 0.07 * cos(a) - 0.06 * sin(a), y - 0.07 * sin(a) + 0.06 * cos(a)), (x + 0.07 * cos(a) - 0.06 * sin(a), y + 0.07 * sin(a) + 0.06 * cos(a)),
             (x + 0.07 * cos(a) + 0.06 * sin(a), y + 0.07 * sin(a) - 0.06 * cos(a)), (x - 0.07 * cos(a) + 0.06 * sin(a), y - 0.07 * sin(a) - 0.06 * cos(a))]
        prisme(p, q, q, z0, z0 + ep, m)
    cylindre(p, cx, cy, z0 + ep, r * 0.25, 0.05, LAITON, 8)


# le bâti : une table de fonte basse où les roues s'emboîtent ; trois axes vides (G4) + une roue en place
boite(mach, -2.2, 0.0, 0.5, 2.0, SOL, 0.7, FONTE := mat("ph_fonte", "#4C4648", 0.6, 0.3), FONTE)
AXES = [(-1.7, 1.25, 0.55), (-0.9, 1.4, 0.35), (-0.35, 0.95, 0.45)]  # (x, y, rayon de la roue qui va là)
for (x, y, r) in AXES:
    cylindre(mach_d, x, y, 0.7, 0.06, 0.55, LAITON, 6)
    # les marques d'usure sur la fonte : un cercle plus clair là où la roue frottait (l'indice de G4)
    q_in = [(x + (r - 0.05) * cos(tau * k / 16), y + (r - 0.05) * sin(tau * k / 16)) for k in range(16)]
    anneau(mach_d, r - 0.06, r + 0.04, 0.7, 0.705, USURE, 16) if False else None
    for k in range(16):
        u0, u1 = tau * k / 16, tau * (k + 1) / 16
        q = [((r - 0.07) * cos(u0) + x, (r - 0.07) * sin(u0) + y), ((r + 0.03) * cos(u0) + x, (r + 0.03) * sin(u0) + y),
             ((r + 0.03) * cos(u1) + x, (r + 0.03) * sin(u1) + y), ((r - 0.07) * cos(u1) + x, (r - 0.07) * sin(u1) + y)]
        prisme(mach_d, q, q, 0.7, 0.708, USURE)
engrenage(mach_d, 0.0, 0.0, 0.62, 0.62, 0.14, 18, LAITON)          # la grande roue, autour de l'arbre (en place)
# les roues démontées, posées par terre et contre le mur
engrenage(mach, 1.4, -1.6, SOL, 0.55, 0.16, 16, LAITON, angle=0.2)
engrenage(mach, 1.9, -0.5, SOL, 0.35, 0.14, 12, CUIVRE, angle=0.4)
engrenage(mach_d, 1.5, -1.65, SOL + 0.16, 0.45, 0.14, 14, LAITON, angle=0.1)
# l'établi (ouest), les burettes, un chiffon, la caisse à outils
boite(mach, -3.0, -1.4, -2.4, -1.5, SOL, 1.35, BOIS, BOIS)
for x in (-2.9, -1.6):
    for y in (-2.3, -1.6):
        boite(mach_d, x, x + 0.12, y, y + 0.12, SOL, 1.35, BOIS_F)
for (x, y) in [(-2.7, -1.9), (-2.4, -2.1)]:
    cylindre(mach_d, x, y, 1.35, 0.1, 0.24, CUIVRE, 8)
    cylindre(mach_d, x + 0.08, y, 1.55, 0.02, 0.15, CUIVRE, 4)
boite(mach_d, -2.0, -1.6, -2.3, -1.7, 1.35, 1.38, mat("ph_chiffon", "#C9A9A0"))
boite(mach, -2.0, -1.2, -1.2, -0.7, SOL, 0.45, BOIS_F, CUIVRE)
# taches d'huile sur les dalles
for (x, y, r) in [(-0.8, -0.6, 0.5), (1.2, 0.8, 0.35), (-1.8, -0.9, 0.3)]:
    cylindre(mach_d, x, y, SOL, r, 0.004, HUILE, 9)
# le schéma des engrenages, peint sur le mur nord, en partie couvert de suie (G4)
ri0 = rayon(1.5) - EP
yw = ri0 - 0.05
boite(mach_d, -1.6, 1.6, yw - 0.02, yw, 1.4, 3.6, mat("ph_schema_fond", "#EDE3CF"))
for (x, zc, r) in [(-0.9, 2.6, 0.5), (-0.2, 2.9, 0.3), (0.35, 2.45, 0.4), (0.95, 2.75, 0.28)]:
    for k in range(18):
        u0, u1 = tau * k / 18, tau * (k + 1) / 18
        bm = mach_d.bm
        vv = [bm.verts.new((x + r * cos(u0), yw - 0.025, zc + r * sin(u0))), bm.verts.new((x + r * cos(u1), yw - 0.025, zc + r * sin(u1))),
              bm.verts.new((x + (r - 0.05) * cos(u1), yw - 0.025, zc + (r - 0.05) * sin(u1))), bm.verts.new((x + (r - 0.05) * cos(u0), yw - 0.025, zc + (r - 0.05) * sin(u0)))]
        bm.faces.new(vv).material_index = mach_d.idx(ENCRE)
bm = mach_d.bm   # la suie : une grande tache sombre qui mange la moitié droite du schéma
vv = [bm.verts.new((0.2, yw - 0.03, 1.5)), bm.verts.new((1.7, yw - 0.03, 1.7)), bm.verts.new((1.5, yw - 0.03, 3.7)), bm.verts.new((0.4, yw - 0.03, 3.3)), bm.verts.new((0.0, yw - 0.03, 2.4))]
bm.faces.new(vv).material_index = mach_d.idx(SUIE)

# ---------------------------------------------------------------- en haut : consoles, galerie, lanterne, lentille, dôme
haut = piece("Haut")
rh = rayon(HT)
for k in range(NS):                      # consoles sous la galerie
    a = tau * (k + 0.5) / NS
    t = Vector((-sin(a), cos(a)))
    n = Vector((cos(a), sin(a)))
    for (d0, d1, z0, z1) in [(0.0, 0.45, HT - 1.0, HT - 0.65), (0.0, 0.8, HT - 0.65, HT - 0.3), (0.0, 1.15, HT - 0.3, HT)]:
        c0, c1 = n * (rh - 0.1 + d0), n * (rh - 0.1 + d1)
        q = [c0 - t * 0.18, c1 - t * 0.18, c1 + t * 0.18, c0 + t * 0.18]
        prisme(haut, [(v.x, v.y) for v in q], [(v.x, v.y) for v in q], z0, z1, MOULURE)
RG = rh + 1.3                            # rayon de la galerie
disque(haut, RG, HT, HT + 0.28, MOULURE, 24, DALLE)
anneau(haut, RG - 0.05, RG + 0.08, HT + 0.05, HT + 0.33, CREME[3], 24)
# garde-corps en fer forgé : poteaux, lisse haute, lisse basse, petites volutes (anneaux)
for k in range(48):
    a = tau * k / 48
    x, y = (RG - 0.12) * cos(a), (RG - 0.12) * sin(a)
    cylindre(haut, x, y, HT + 0.28, 0.035 if k % 4 else 0.06, 1.1 if k % 4 else 1.25, FER, 5)
    if k % 4 == 2:
        cylindre(haut, x, y, HT + 0.75, 0.12, 0.03, FER, 8)
anneau(haut, RG - 0.18, RG - 0.06, HT + 1.28, HT + 1.36, FER, 48)
anneau(haut, RG - 0.16, RG - 0.08, HT + 0.4, HT + 0.45, FER, 48)
# la lanterne : parapet, montants en laiton, vitres, anneau haut
RL = 2.5
anneau(haut, RL - 0.3, RL, HT + 0.28, HT + 1.1, CREME[0], 12, haut=MOULURE)
ZV0, ZV1 = HT + 1.1, HT + 4.0
for k in range(12):
    a = tau * k / 12
    cylindre(haut, RL * cos(a), RL * sin(a), ZV0, 0.07, ZV1 - ZV0, LAITON, 6)
    a1 = tau * (k + 1) / 12
    q = [((RL - 0.02) * cos(a), (RL - 0.02) * sin(a)), ((RL + 0.0) * cos(a), (RL + 0.0) * sin(a)),
         ((RL + 0.0) * cos(a1), (RL + 0.0) * sin(a1)), ((RL - 0.02) * cos(a1), (RL - 0.02) * sin(a1))]
    prisme(haut, q, q, ZV0, ZV1, VERRE)
    zt = (ZV0 + ZV1) / 2
    anneau(haut, RL - 0.06, RL + 0.04, zt - 0.03, zt + 0.03, LAITON, 12, a, a1)
anneau(haut, RL - 0.15, RL + 0.12, ZV1, ZV1 + 0.25, LAITON, 12)
# le dôme en cuivre vert-de-gris, en côtes, une boule et la girouette
ZD = ZV1 + 0.25
anneaux_dome = [(RL + 0.25, 0.0), (RL + 0.05, 0.55), (RL - 0.45, 1.15), (RL - 1.15, 1.6), (0.5, 1.95), (0.18, 2.1)]
for i in range(len(anneaux_dome) - 1):
    (ra, za), (rb, zb) = anneaux_dome[i], anneaux_dome[i + 1]
    for k in range(12):
        u0, u1 = tau * k / 12, tau * (k + 1) / 12
        bm = haut.bm
        vv = [bm.verts.new((ra * cos(u0), ra * sin(u0), ZD + za)), bm.verts.new((ra * cos(u1), ra * sin(u1), ZD + za)),
              bm.verts.new((rb * cos(u1), rb * sin(u1), ZD + zb)), bm.verts.new((rb * cos(u0), rb * sin(u0), ZD + zb))]
        bm.faces.new(vv).material_index = haut.idx(CUIVRE_VERT if (k + i) % 2 else CUIVRE_VERT_2)
for k in range(12):   # côtes en relief
    a = tau * k / 12
    for i in range(len(anneaux_dome) - 2):
        (ra, za), (rb, zb) = anneaux_dome[i], anneaux_dome[i + 1]
        x0, y0, x1, y1 = (ra + 0.05) * cos(a), (ra + 0.05) * sin(a), (rb + 0.05) * cos(a), (rb + 0.05) * sin(a)
        cylindre(haut, (x0 + x1) / 2, (y0 + y1) / 2, ZD + za, 0.05, zb - za + 0.05, CUIVRE_VERT_2, 4)
disque(haut, RL + 0.3, ZD - 0.05, ZD + 0.08, CUIVRE_VERT_2, 12)
# boule, tige, girouette (un objet à part : elle tournera au vent)
cylindre(haut, 0, 0, ZD + 2.1, 0.22, 0.4, CUIVRE, 10)
cylindre(haut, 0, 0, ZD + 2.5, 0.04, 1.1, FER, 5)
gir = piece("Girouette")
boite(gir, -0.8, 0.6, -0.02, 0.02, -0.05, 0.05, FER)
bm = gir.bm
vv = [bm.verts.new(c) for c in [(0.6, -0.03, -0.18), (0.95, -0.03, 0.0), (0.6, -0.03, 0.18)]]
bm.faces.new(vv).material_index = gir.idx(FER)
vv = [bm.verts.new(c) for c in [(-0.8, -0.03, -0.25), (-0.8, -0.03, 0.25), (-0.45, -0.03, 0.0)]]
bm.faces.new(vv).material_index = gir.idx(CUIVRE)
# la lentille de Fresnel : un empilement d'anneaux de cristal autour d'un cœur (objet à part : elle tournera)
len_ = piece("Lentille")
ZL = ZV0 + 0.1
disque(len_, 0.9, ZL - 0.2, ZL, LAITON, 12)
for i, (r_, h_) in enumerate([(0.75, 0.22), (0.95, 0.22), (1.1, 0.25), (1.18, 0.3), (1.2, 0.35), (1.18, 0.3), (1.1, 0.25), (0.95, 0.22), (0.75, 0.22)]):
    z0 = ZL + sum(hh for (_, hh) in [(0.75, 0.22), (0.95, 0.22), (1.1, 0.25), (1.18, 0.3), (1.2, 0.35), (1.18, 0.3), (1.1, 0.25), (0.95, 0.22), (0.75, 0.22)][:i])
    anneau(len_, r_ - 0.18, r_, z0, z0 + h_ - 0.02, CRISTAL if i % 2 else CRISTAL_2, 16, decal=i * 0.1)
    anneau(len_, r_ - 0.02, r_ + 0.01, z0 + h_ - 0.03, z0 + h_, LAITON, 16)
cylindre(len_, 0, 0, ZL, 0.35, 2.3, CRISTAL_2, 10)    # le cœur (vide : pas de lampe, ILE_02 §5 G2)
# la couronne graduée (G4), autour du pied de la lentille
anneau(len_, 1.35, 1.6, ZL - 0.25, ZL - 0.12, LAITON, 36)
for k in range(36):
    a = tau * k / 36
    boite(len_, 1.48 * cos(a) - 0.02, 1.48 * cos(a) + 0.02, 1.48 * sin(a) - 0.02, 1.48 * sin(a) + 0.02, ZL - 0.12, ZL - 0.06 if k % 3 else ZL, FER)

# ---------------------------------------------------------------- l'annexe (ouest) : remise en bas, chambre d'Iris en haut
ax0, ax1, ay0, ay1, ah = ANNEXE
ann = piece("Annexe-col")
z = 0.0
r_ = 0
while z < ah - 0.01:
    h = min(ASSISE, ah - z)
    for (xa, ya, xb, yb, nx, ny) in [(ax0, ay0, ax0, ay1, -1, 0), (ax0, ay1, ax1, ay1, 0, 1), (ax0, ay0, ax1, ay0, 0, -1)]:
        lg = math.hypot(xb - xa, yb - ya)
        s = -rng.uniform(0, 0.6) if r_ % 2 else 0.0
        while s < lg - 0.01:
            l = rng.uniform(0.8, 1.5)
            s0, s1 = max(s, 0.0), min(s + l, lg)
            s += l
            # la petite fenêtre de la remise (ouest) et la fenêtre de la chambre (ouest, en haut)
            if nx == -1 and ((0.4 < z < 2.2 and 1.8 < s0 + 0.3 < 3.6) or (6.0 < z < 8.0 and 2.4 < s0 + 0.3 < 3.8)):
                continue
            tx, ty = (xb - xa) / lg, (yb - ya) / lg
            sail = rng.uniform(-0.02, 0.03)
            p0 = (xa + tx * (s0 + 0.01) + nx * (0.0 + sail), ya + ty * (s0 + 0.01) + ny * (0.0 + sail))
            p1 = (xa + tx * (s1 - 0.01) + nx * (0.0 + sail), ya + ty * (s1 - 0.01) + ny * (0.0 + sail))
            q0 = (xa + tx * (s0 + 0.01) - nx * 0.5, ya + ty * (s0 + 0.01) - ny * 0.5)
            q1 = (xa + tx * (s1 - 0.01) - nx * 0.5, ya + ty * (s1 - 0.01) - ny * 0.5)
            q = [p0, p1, q1, q0]
            if (q[1][0] - q[0][0]) * (q[3][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[3][0] - q[0][0]) < 0:
                q.reverse()
            band = 6.0 <= z < 8.0
            m = (ROUILLE[0] if rng.random() < 0.6 else ROUILLE[3]) if band else (CREME[0] if rng.random() < 0.5 else rng.choice(CREME[1:]))
            prisme(ann, q, q, z + 0.012, z + h - 0.012, m)
    z += h
    r_ += 1
boite(ann, ax0 + 0.5, ax1, ay0 + 0.5, ay1 - 0.5, ETAGES[1] - 0.32, ETAGES[1], BOIS_F, rng.choice(PLANCHER))   # plancher de la chambre
boite(ann, ax0 + 0.5, ax1, ay0 + 0.5, ay1 - 0.5, -0.1, SOL, DALLE)
# le toit de l'annexe : un appentis d'ardoises adossé à la tour, avec la lucarne ouverte (G5)
toit_a = piece("AnnexeToit")
zt0, zt1 = ah, ah + 1.3            # bas (ouest) et haut (contre la tour)
LUC = (ax0 + 0.9, ax0 + 2.0, -0.2, 1.0)  # x0, x1, y0, y1 de la lucarne
x = ax0 - 0.4
while x < ax1 - 0.05:
    w = 0.42
    y = ay0 - 0.4
    while y < ay1 + 0.4:
        l = rng.uniform(0.5, 0.75)
        xa, xb = x, min(x + w, ax1)
        ya, yb = y, min(y + l, ay1 + 0.4)
        y += l
        if LUC[0] < (xa + xb) / 2 < LUC[1] and LUC[2] < (ya + yb) / 2 < LUC[3]:
            continue
        za = zt0 + (zt1 - zt0) * (xa - (ax0 - 0.4)) / (ax1 - ax0 + 0.4)
        zb = zt0 + (zt1 - zt0) * (xb - (ax0 - 0.4)) / (ax1 - ax0 + 0.4)
        bm = toit_a.bm
        vv = [bm.verts.new(c) for c in [(xa, ya + 0.02, za), (xb, ya + 0.02, zb), (xb, yb - 0.02, zb), (xa, yb - 0.02, za),
                                         (xa, ya + 0.02, za + 0.08), (xb, ya + 0.02, zb + 0.08), (xb, yb - 0.02, zb + 0.08), (xa, yb - 0.02, za + 0.08)]]
        i = toit_a.idx(rng.choice(ARDOISE))
        for f in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            bm.faces.new([vv[j] for j in f]).material_index = i
    x += w
# la lucarne : un cadre de bois et sa vitre relevée, calée par une tige
lx0, lx1, ly0, ly1 = LUC
zl = zt0 + (zt1 - zt0) * ((lx0 + lx1) / 2 - (ax0 - 0.4)) / (ax1 - ax0 + 0.4)
for (xa, xb, ya, yb) in [(lx0, lx1, ly0 - 0.1, ly0), (lx0, lx1, ly1, ly1 + 0.1), (lx0 - 0.1, lx0, ly0, ly1), (lx1, lx1 + 0.1, ly0, ly1)]:
    boite(toit_a, xa, xb, ya, yb, zl - 0.05, zl + 0.25, BOIS)
bm = toit_a.bm
vv = [bm.verts.new(c) for c in [(lx0, ly1 + 0.05, zl + 0.25), (lx1, ly1 + 0.05, zl + 0.25), (lx1, ly1 - 0.3, zl + 1.2), (lx0, ly1 - 0.3, zl + 1.2)]]
bm.faces.new(vv).material_index = toit_a.idx(VERRE)
cylindre(toit_a, (lx0 + lx1) / 2, ly0 + 0.4, zl + 0.2, 0.02, 0.7, FER, 4)

# ---------------------------------------------------------------- l'échelle de service : de la galerie au toit de l'annexe (G5)
ech = piece("Echelle")
ae = radians(180 - 5)                     # côté ouest, au-dessus de l'annexe
for s in (-0.32, 0.32):
    bm = ech.bm
    z0, z1 = zt1 - 0.2, HT + 0.2
    pts = []
    for zz in (z0, z1):
        r = rayon(zz) + 0.25
        pts.append((r * cos(ae) - s * sin(ae), r * sin(ae) + s * cos(ae), zz))
    a, b = Vector(pts[0]), Vector(pts[1])
    cylindre(ech, a.x, a.y, z0, 0.04, z1 - z0, FER, 5)
n_barreaux = int((HT + 0.2 - zt1) / 0.38)
for i in range(n_barreaux):
    zz = zt1 + 0.2 + i * 0.38
    r = rayon(zz) + 0.25
    cx, cy = r * cos(ae), r * sin(ae)
    t = Vector((-sin(ae), cos(ae)))
    q = [(cx - t.x * 0.32 - 0.02 * cos(ae), cy - t.y * 0.32 - 0.02 * sin(ae)), (cx + t.x * 0.32 - 0.02 * cos(ae), cy + t.y * 0.32 - 0.02 * sin(ae)),
         (cx + t.x * 0.32 + 0.02 * cos(ae), cy + t.y * 0.32 + 0.02 * sin(ae)), (cx - t.x * 0.32 + 0.02 * cos(ae), cy - t.y * 0.32 + 0.02 * sin(ae))]
    prisme(ech, q, q, zz, zz + 0.04, FER_ROUILLE)
    if i % 6 == 0:   # pattes de fixation dans la maçonnerie
        boite(ech, cx - 0.05 - 0.25 * cos(ae), cx + 0.05, cy - 0.05, cy + 0.05, zz, zz + 0.06, FER)

# ---------------------------------------------------------------- dehors : chaîne, cordages, caisses près de la porte
ext = piece("Exterieur-col")
for (x, y, r) in [(-2.6, -R0 - 1.6, 0.45), (2.9, -R0 - 1.2, 0.35)]:
    cylindre(ext, x, y, 0.0, r, 0.18, mat("ph_corde", "#C8B08A"), 12)
boite(ext, 2.4, 3.3, -R0 - 0.9, -R0 - 0.1, 0.0, 0.8, BOIS, BOIS_F)
boite(ext, 2.55, 3.15, -R0 - 0.75, -R0 - 0.25, 0.8, 1.3, BOIS_F, BOIS)
for i in range(10):   # une grosse chaîne rouillée qui traîne
    x = -3.4 + i * 0.22
    y = -R0 - 0.9 + 0.25 * sin(i * 0.9)
    if i % 2:
        boite(ext, x, x + 0.2, y - 0.03, y + 0.03, 0.0, 0.12, FER_ROUILLE)
    else:
        boite(ext, x, x + 0.2, y - 0.08, y + 0.08, 0.0, 0.05, FER_ROUILLE)

# ---------------------------------------------------------------- repères (Empties) et export
objets = [p.objet() for p in PIECES.values() if not p.vide()]
o_gir = next(o for o in objets if o.name == "Girouette")
o_gir.location = (0, 0, ZD + 3.4)
for o in objets:
    if o.name.endswith("-colonly"):
        o.hide_render = True
        o.display_type = "WIRE"


def repere(nom, x, y, zz):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_size = 0.5
    o.location = (x, y, zz)
    sc.collection.objects.link(o)
    return o


for k, e in enumerate(ETAGES):
    objets.append(repere(f"Etage{k}", 0, 0, e))
objets.append(repere("Galerie", 0, 0, HT + 0.28))
objets.append(repere("Porte", 0, -R0 - 2.0, 0.0))
objets.append(repere("Lucarne", (lx0 + lx1) / 2, (ly0 + ly1) / 2, zl))

# lumière et caméra pour juger
soleil = bpy.data.lights.new("soleil_ph", "SUN")
soleil.energy = 4.5
soleil.color = (1.0, 0.88, 0.72)
so = bpy.data.objects.new("soleil_ph", soleil)
sc.collection.objects.link(so)
so.rotation_euler = (radians(58), 0, radians(-40))
cam = bpy.data.cameras.new("cam_ph")
cam.lens = 30
co = bpy.data.objects.new("cam_ph", cam)
sc.collection.objects.link(co)
co.location = (14, -26, 22)
co.rotation_euler = (Vector((0, 0, 10)) - co.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = co
if sc.world is None:
    sc.world = bpy.data.worlds.new("monde_ph")
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
print("phare :", sum(len(o.data.polygons) for o in objets if o.type == "MESH"), "faces,", len(objets), "objets ->", SORTIE)
