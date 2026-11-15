# Construit la ville de l'ombre de l'île 1 dans scenes/islands/island_01.tscn (nœud « Ombre »).
# Toute l'île est habitée, en quartiers : le village des Pins (ouest), la Grand-Place (centre),
# les Champs (sud), le Levant (côte est), les Hauts (plateau nord), la crique ouest.
# Un placeur pose chaque objet À PLAT, à la hauteur du terrain (aussi dans l'éditeur), sans chevaucher
# les décors du jour (pins, rochers, abri, lanternes…), les chemins du jour, ni les autres objets.
#  - relevé du terrain : godot -s tools/dump_terrain.gd  → tools/ile1_terrain.json
#  - garde les nœuds de l'histoire (Hameau, Enfant/Petites et leurs paroles, Compteur, Veilleuse, Mission, Essaim).
# Usage : python tools/ombre_ile1.py   (repart de la sauvegarde island_01.avant_ombre.tscn.txt)
import json
import math
import os
import random
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ombre_kit import xform  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
P = os.path.join(ROOT, "scenes/islands/island_01.tscn")
BACKUP = os.path.join(ROOT, "scenes/islands/island_01.avant_ombre.tscn.txt")
if not os.path.exists(BACKUP):
    shutil.copy(P, BACKUP)
s = open(BACKUP, encoding="utf-8").read()
TERRAIN = json.load(open(os.path.join(ROOT, "tools/ile1_terrain.json"), encoding="utf-8"))

# ================================================================ le terrain et le placeur
CELLS = {(c["x"], c["z"]): (c["top"], c["item"]) for c in TERRAIN["cells"]}
OBST = [(o["x0"], o["z0"], o["x1"], o["z1"]) for o in TERRAIN["obstacles"]
        if o["y1"] - o["y0"] > 0.05 and not o["name"].startswith("Lueurs")]
TAKEN = []  # cercles (x, z, r) déjà pris par le monde de l'ombre
# endroits à garder libres : lanternes, pierres-soleil, porte de l'abri, départ du robot, terreau…
for x, z, r in [(-6.5, 8.5, 1.4), (4.5, 10.5, 1.4), (9.5, 1.5, 1.4), (1.5, 0.5, 2.2), (-3.5, -11.5, 1.6),
                (-14.0, 8.6, 1.6), (-18.7, -8.4, 1.6), (-14.0, 6.2, 1.2), (-13.8, 3.7, 0.8), (12.0, -6.95, 1.5),
                (-0.5, 1.0, 1.4), (-0.5, 0.0, 1.0), (2.9, 1.4, 0.8), (15.5, -14.5, 1.2)]:
    TAKEN.append((x, z, r))


def cell(x, z):
    return CELLS.get((math.floor(x), math.floor(z)))


def ground(x, z):
    c = cell(x, z)
    return c[0] if c else None


def free_spot(x, z, r, allow_path=False, margin=0.25, canopy=None):
    """la base (rayon r) est-elle à plat, sur l'île, hors chemins et loin des décors du jour ?
    et le toit (rayon `canopy`) ne touche-t-il aucun autre objet de l'ombre ?"""
    canopy = canopy or r
    c0 = cell(x, z)
    if c0 is None:
        return False
    top = c0[0]
    rr = r + 0.25  # pas au ras de l'eau ni d'une falaise
    for i in range(math.floor(x - rr), math.floor(x + rr) + 1):
        for j in range(math.floor(z - rr), math.floor(z + rr) + 1):
            nx = min(max(x, i), i + 1)
            nz = min(max(z, j), j + 1)
            if (nx - x) ** 2 + (nz - z) ** 2 > rr * rr:
                continue
            cc = CELLS.get((i, j))
            if cc is None or abs(cc[0] - top) > 0.01:
                return False
            if (nx - x) ** 2 + (nz - z) ** 2 <= r * r:
                if cc[1] in ("Pierre", "Escalier") or (cc[1] == "Chemin" and not allow_path):
                    return False
    for (x0, z0, x1, z1) in OBST:
        nx = min(max(x, x0), x1)
        nz = min(max(z, z0), z1)
        if (nx - x) ** 2 + (nz - z) ** 2 < (r + margin) ** 2:
            return False
    for (tx, tz, tr) in TAKEN:
        if (tx - x) ** 2 + (tz - z) ** 2 < (canopy + tr + margin * 0.5) ** 2 * 0.8:
            return False
    return True


def find(x, z, r, allow_path=False, reach=4.5, canopy=None):
    """le point libre le plus proche de (x, z), en spirale ; None si rien ne convient"""
    if free_spot(x, z, r, allow_path, canopy=canopy):
        return (x, z)
    step = 0.35
    k = 1
    while k * step <= reach:
        rad = k * step
        n = max(8, int(2 * math.pi * rad / step))
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.7
            px, pz = x + rad * math.cos(a), z + rad * math.sin(a)
            if free_spot(px, pz, r, allow_path, canopy=canopy):
                return (px, pz)
        k += 1
    return None


def find_in(bounds, rb, rc, prefer, level=None, allow_path=False):
    """le meilleur endroit libre DANS un quartier (x0, x1, z0, z1), au même niveau, le plus près de `prefer`"""
    x0, x1, z0, z1 = bounds
    best = None
    x = x0
    while x <= x1:
        z = z0
        while z <= z1:
            g = ground(x, z)
            if g is not None and (level is None or abs(g - level) < 0.01) and free_spot(x, z, rb, allow_path, canopy=rc):
                d = (x - prefer[0]) ** 2 + (z - prefer[1]) ** 2
                if best is None or d < best[0]:
                    best = (d, x, z)
            z += 0.25
        x += 0.25
    return (best[1], best[2]) if best else None


# ================================================================ ressources
ext_lines = []
ids = {}


def ext(typ, path):
    if path in ids:
        return ids[path]
    i = "om_%d" % (len(ids) + 1)
    ids[path] = i
    ext_lines.append('[ext_resource type="%s" path="%s" id="%s"]' % (typ, path, i))
    return i


SC = lambda rel: ext("PackedScene", "res://assets/ombre/%s.tscn" % rel)
DIALOGUE = ext("Script", "res://scripts/ombre/dialogue.gd")
MONDE = ext("Script", "res://scripts/ombre/ombre_monde.gd")
HABITANT = re.search(r'\[ext_resource type="PackedScene"[^\]]*path="res://assets/lueurs/habitant.tscn" id="([^"]+)"\]', s).group(1)

# ================================================================ découpe de la scène existante
head_end = s.index("\n[node ")
header = s[:head_end]
blocks = re.split(r"\n(?=\[node )", s[head_end + 1:])


def node_path(b):
    m = re.match(r'\[node name="([^"]+)"(?:[^\]]*?parent="([^"]*)")?', b)
    if m.group(2) is None:
        return ""
    return m.group(1) if m.group(2) == "." else m.group(2) + "/" + m.group(1)


REMOVE = {"Ombre/Hameau/Maison1", "Ombre/Hameau/Maison2", "Ombre/Hameau/Maison3", "Ombre/Hameau/Jardin",
          "Ombre/Hameau/Place", "Ombre/Hameau/Fils", "Ombre/Hameau/Extension/Maison4",
          "Ombre/Hameau/Extension/Maison5", "Ombre/Hameau/Extension/Jardin2"}
HAMEAU = (-11.5, 0.5, 0.5)
kept = []
for b in blocks:
    p = node_path(b)
    if p in REMOVE:
        continue
    if p == "Ombre":
        b = ('[node name="Ombre" type="Node3D" parent="." node_paths=PackedStringArray("environment", "sun")]\n'
             'script = ExtResource("%s")\nenvironment = NodePath("../WorldEnvironment")\nsun = NodePath("../Sun")\n' % MONDE)
    if p == "Ombre/Hameau":
        b = re.sub(r"transform = Transform3D\([^)]*\)", "transform = " + xform(HAMEAU), b)
    kept.append(b)

# ================================================================ écriture des nœuds
new_nodes = []
sub_res = []
ORIGINS = {"Ombre/Hameau": HAMEAU, "Ombre/Hameau/Extension": HAMEAU}
placed = {}  # nom complet → position monde


def origin_of(parent):
    o = (0.0, 0.0, 0.0)
    for k, v in ORIGINS.items():
        if parent == k or parent.startswith(k + "/"):
            o = v
    return o


def raw(name, parent, scene_id=None, typ=None, world=(0, 0, 0), rot=0.0, scale=1.0, props=None, paths=None):
    o = origin_of(parent)
    loc = (world[0] - o[0], world[1] - o[1], world[2] - o[2])
    hdr = '[node name="%s"' % name
    if typ:
        hdr += ' type="%s"' % typ
    hdr += ' parent="%s"' % parent
    if paths:
        hdr += " node_paths=PackedStringArray(%s)" % ", ".join('"%s"' % x for x in paths)
    if scene_id:
        hdr += ' instance=ExtResource("%s")' % scene_id
    txt = hdr + "]\ntransform = %s\n" % xform(loc, (0, rot, 0), scale)
    for k, v in (props or {}).items():
        txt += "%s = %s\n" % (k, v)
    new_nodes.append(txt)
    placed[parent + "/" + name] = world


def facing(px, pz, tx, tz):
    return math.degrees(math.atan2(tx - px, tz - pz))


# (base au sol, toit) : la base doit être à plat et loin des décors ; le toit ne touche pas les autres objets
RADIUS = {"maisons/maison_champignon": (1.0, 1.7), "maisons/maison_souche": (1.1, 1.3), "maisons/maison_coquillage": (1.05, 1.1),
          "maisons/maison_pilotis": (1.3, 1.5), "maisons/tour_ancienne": (1.0, 1.2), "decor/puits": (0.65, 0.7),
          "decor/etal": (0.8, 0.9), "decor/banc": (0.6, 0.65), "decor/potager": (0.9, 0.95), "decor/corde_linge": (0.5, 1.05),
          "decor/lampe_champignon": (0.2, 0.3), "decor/champignon_geant": (0.45, 1.2), "decor/champignon_geant_violet": (0.4, 1.0),
          "decor/champignon_geant_ambre": (0.35, 0.8), "decor/fougere": (0.2, 0.3), "decor/nappe_mousse": (0.6, 0.7),
          "decor/corail": (0.25, 0.35), "decor/berceau_champignon": (0.4, 0.45)}
skipped = []


def put(rel, name, parent, x, z, face=None, rot=None, scale=1.0, props=None, allow_path=False, reach=4.5):
    rb, rc = RADIUS.get(rel, (0.8, 0.8))
    r, canopy = rb * scale, rc * scale
    spot = find(x, z, r, allow_path, reach, canopy)
    if spot is None:
        skipped.append(name)
        return None
    px, pz = spot
    y = ground(px, pz)
    if rot is None:
        rot = facing(px, pz, face[0], face[1]) if face else random.uniform(0, 360)
    TAKEN.append((px, pz, canopy))
    raw(name, parent, SC(rel), world=(px, y, pz), rot=rot, scale=scale, props=props)
    return (px, y, pz)


def house(rel, name, parent, bounds, prefer, face=None, scale=1.0, props=None):
    """une maison (ou un gros objet) posée au meilleur endroit libre de son quartier, au niveau de `prefer`"""
    rb, rc = RADIUS.get(rel, (0.8, 0.8))
    level = ground(*prefer)
    spot = find_in(bounds, rb * scale, rc * scale, prefer, level)
    if spot is None:
        skipped.append(name)
        return None
    px, pz = spot
    rot = facing(px, pz, face[0], face[1]) if face else random.uniform(0, 360)
    TAKEN.append((px, pz, rc * scale))
    raw(name, parent, SC(rel), world=(px, ground(px, pz), pz), rot=rot, scale=scale, props=props)
    return (px, pz)


def marker(name, parent, x, z):
    spot = find(x, z, 0.3, allow_path=True, reach=3.0) or (x, z)
    raw(name, parent, typ="Marker3D", world=(spot[0], ground(*spot) or 0.5, spot[1]))
    return "../" + name


def strs(xs):
    return "PackedStringArray(%s)" % ", ".join('"%s"' % x.replace('"', '\\"') for x in xs)


def snames(xs):
    return "Array[StringName]([%s])" % ", ".join('&"%s"' % x for x in xs)


def dialogue(did, lines, paroles=(), requires=(), forbids=(), once=False, sets=""):
    rid = "Dlg_" + did
    txt = '[sub_resource type="Resource" id="%s"]\nscript = ExtResource("%s")\nid = &"%s"\nlines = %s\n' % (rid, DIALOGUE, did, strs(lines))
    if paroles:
        txt += "paroles = %s\n" % snames(paroles)
    if requires:
        txt += "requires = %s\n" % snames(requires)
    if forbids:
        txt += "forbids = %s\n" % snames(forbids)
    if once:
        txt += "once = true\n"
    if sets:
        txt += 'sets_flag = &"%s"\n' % sets
    sub_res.append(txt)
    return rid


def dlist(rids):
    return 'Array[ExtResource("%s")]([%s])' % (DIALOGUE, ", ".join('SubResource("%s")' % r for r in rids))


def habitant(name, parent, x, z, form, home=None, routine=(), dialogues=(), chatter=(), extra=None):
    spot = find(x, z, 0.3, allow_path=True, reach=3.0) or (x, z)
    y = ground(*spot) or 0.5
    props = {"form": form}
    paths = []
    if home:
        props["home"] = 'NodePath("%s")' % home
        paths.append("home")
    if routine:
        props["routine"] = "[%s]" % ", ".join('NodePath("%s")' % r for r in routine)
        paths.append("routine")
    if dialogues:
        props["dialogues"] = dlist(dialogues)
    if chatter:
        props["chatter"] = strs(chatter)
    props.update(extra or {})
    raw(name, parent, HABITANT, world=(spot[0], y, spot[1]), rot=random.uniform(0, 360), props=props, paths=paths)


def group(name, parent="Ombre"):
    new_nodes.append('[node name="%s" type="Node3D" parent="%s"]\n' % (name, parent))
    return parent + "/" + name


random.seed(7)

# ================================================================ chemins de l'ombre (posés en premier : fixes)
C = group("Chemins")
raw("EscalierGeants", C, SC("decor/escalier_falaise"), world=(-19.2, 0.5, -7.4), rot=90,
    props={"snap_to_ground": "false", "follow_wake": "false", "footprint": "0.6"})
for x in range(-20, -14):
    TAKEN.append((x + 0.5, -7.4, 0.7))
raw("PontPecheurs", C, SC("decor/pont_corde"), world=(-20.5, 0.5, 0.9), rot=-90,
    props={"snap_to_ground": "false", "follow_wake": "false", "footprint": "0.5"})
raw("IlotCorail", C, SC("decor/ilot_corail"), world=(-26.6, 0.0, 0.9), rot=200,
    props={"snap_to_ground": "false", "follow_wake": "false", "footprint": "2.3"})
raw("LieuIlot", C, typ="Marker3D", world=(-25.8, 0.55, 1.6))
V0 = group("Village")
raw("Ponton", V0, SC("decor/ponton"), world=(-18.2, 0.0, 0.9), rot=-90, props={"snap_to_ground": "false", "follow_wake": "false"})
for x in (-17.6, -17.0):
    TAKEN.append((x, 0.9, 0.8))
raw("CabanePilotis", V0, SC("maisons/maison_pilotis"), world=(-19.4, 0.0, -10.3), rot=0,
    props={"snap_to_ground": "false", "follow_wake": "false"})
TAKEN.append((-19.4, -10.3, 1.5))
TAKEN.append((-18.2, -4.9, 1.0))  # le Compteur
put("decor/champignon_geant", "GeantEscalier1", C, -17.6, -9.4, scale=1.0, reach=1.5)
put("decor/champignon_geant_ambre", "GeantEscalier2", C, -18.8, -6.3)
BV = (-13.6, -8.6)
raw("Belvedere", C, typ="Node3D", world=(BV[0], 3.5, BV[1]))
ORIGINS[C + "/Belvedere"] = (BV[0], 3.5, BV[1])
put("decor/banc", "BancBelvedere", C + "/Belvedere", -13.2, -9.2, face=(-18, -7.4))
put("decor/lampe_champignon", "LampeBelvedere", C + "/Belvedere", -14.1, -9.7)
put("decor/nappe_mousse", "MousseBelvedere", C + "/Belvedere", -13.5, -8.4, scale=0.8)

# ================================================================ 1. le village des Pins (sol bas, ouest)
# entre les pins et la falaise nord ; la place du puits au milieu
H = "Ombre/Hameau"
VP = (-15.6, -7.4, -5.6, -1.2)
PLACE = (-11.6, -2.9)
put("decor/puits", "Puits", H, *PLACE, reach=2.0)
house("maisons/tour_ancienne", "TourAncienne", "Ombre/Village", VP, (-14.6, -4.4), face=PLACE)
house("maisons/maison_champignon", "Maison1", H, VP, (-9.2, -4.0), face=PLACE)
house("maisons/maison_souche", "Maison2", H, VP, (-14.3, -2.4), face=PLACE)
house("maisons/maison_coquillage", "Maison3", H, (-11.0, -7.6, 2.6, 5.6), (-9.0, 4.0), face=(-11.5, 0.5))
V = V0
put("decor/etal", "Etal", H, -12.6, -1.6, face=PLACE, reach=3.5)
put("decor/banc", "Banc", H, -10.6, -1.8, face=PLACE, reach=3.5)
put("decor/potager", "Jardin", H, -8.4, -2.0, rot=80, reach=2.5)
put("decor/corde_linge", "Fils", H, -12.0, -4.9, rot=0, reach=2.0)
for k, (x, z) in enumerate([(-12.6, -0.4), (-10.4, -3.2), (-13.4, -3.6), (-8.6, -3.4), (-9.6, 2.6)]):
    put("decor/lampe_champignon", "Lampe%d" % (k + 1), H, x, z, reach=1.5)
put("decor/banc", "Banc2", V, -15.0, -3.6, face=PLACE, reach=2.0)
for k, (x, z) in enumerate([(-15.2, -1.6), (-16.4, -6.3), (-17.6, 0.4), (-9.0, 5.2)]):
    put("decor/lampe_champignon", "LampeV%d" % (k + 1), V, x, z, reach=1.5)
LIEUX = {"LieuPuits": (-11.0, -2.2), "LieuMarche": (-12.4, -2.4), "LieuPotager": (-8.8, -1.0), "LieuLinge": (-12.0, -4.3),
         "LieuPonton": (-17.8, 0.9), "LieuBanc": (-14.6, -3.0), "LieuCrique": (-17.5, -5.0), "LieuAbri": (-11.6, 1.8)}
for n, (x, z) in LIEUX.items():
    marker(n, V, x, z)

# ================================================================ 2. la Grand-Place (plateau du milieu, autour de la grande lanterne)
GP = group("GrandPlace")
GPC = (1.5, 0.5)
GPB = (-7.0, 10.0, -4.2, 4.2)
put("decor/puits", "Fontaine", GP, -2.6, -2.2, scale=1.1, reach=2.5)
house("maisons/maison_champignon", "MaisonPlace1", GP, GPB, (-4.6, -0.4), face=GPC, scale=0.95)
house("maisons/maison_souche", "MaisonPlace2", GP, GPB, (7.6, -0.6), face=GPC, scale=0.95)
house("maisons/maison_coquillage", "MaisonPlace3", GP, GPB, (-1.0, -3.0), face=GPC, scale=0.95)
house("maisons/maison_coquillage", "MaisonPlace4", GP, GPB, (7.4, 1.6), face=GPC, scale=0.9)
E = H + "/Extension"  # 2e moitié : le hameau s'étend jusqu'à la place
house("maisons/maison_champignon", "Maison4", E, GPB, (-4.0, 1.6), face=GPC, scale=0.85)
house("maisons/maison_coquillage", "Maison5", E, GPB, (2.0, -3.2), face=GPC, scale=0.85)
put("decor/potager", "Jardin2", E, -5.6, 2.4, rot=20, reach=2.5)
put("decor/lampe_champignon", "Lampe6", E, -3.2, 2.6, reach=1.5)
for k, (x, z) in enumerate([(-3.0, 0.8), (4.6, -2.2), (5.2, 2.4), (0.0, 3.4)]):
    put("decor/etal", "Etal%d" % (k + 1), GP, x, z, face=GPC, reach=3.5)
for k, (x, z) in enumerate([(-1.8, 2.8), (3.6, 3.2), (0.4, -3.4)]):
    put("decor/banc", "BancPlace%d" % (k + 1), GP, x, z, face=GPC, reach=2.0)
for k, (x, z) in enumerate([(-3.6, -1.2), (2.6, -2.6), (6.0, 0.4), (-1.2, 2.0), (3.0, 2.6), (-5.6, -2.4), (6.6, -2.8)]):
    put("decor/lampe_champignon", "LampePlace%d" % (k + 1), GP, x, z, reach=1.5)
put("decor/corde_linge", "Guirlande", GP, 1.0, 3.6, rot=10, reach=2.0)
for n, (x, z) in {"LieuEtal1": (-2.4, 0.4), "LieuEtal2": (4.0, -1.6), "LieuEtal3": (4.6, 1.8), "LieuFontaine": (-2.0, -1.4),
                  "LieuBancs": (0.4, -2.8)}.items():
    marker(n, GP, x, z)

# ================================================================ 3. les Champs (sol bas, sud)
CH = group("Champs")
CHC = (4.0, 8.0)
CHB = (-6.0, 15.5, 5.0, 13.5)
house("maisons/maison_souche", "Ferme1", CH, CHB, (2.0, 6.2), face=CHC)
house("maisons/maison_champignon", "Ferme2", CH, CHB, (11.0, 7.0), face=CHC)
house("maisons/maison_coquillage", "Ferme3", CH, CHB, (13.0, 9.0), face=CHC)
house("maisons/maison_souche", "Ferme4", CH, CHB, (0.5, 11.8), face=CHC)
house("maisons/maison_champignon", "Maison7", CH, CHB, (-1.6, 12.2), face=CHC, scale=0.9)  # la jardinière
house("maisons/maison_souche", "Maison6", CH, CHB, (10.4, 5.4), face=CHC, scale=0.9)  # le tisserand
for k, (x, z) in enumerate([(-3.4, 6.4), (-1.0, 6.2), (5.0, 6.4), (7.6, 6.4), (8.6, 9.0), (-2.2, 9.8), (5.6, 12.0), (12.6, 11.0)]):
    put("decor/potager", "Champ%d" % (k + 1), CH, x, z, rot=random.choice([0, 90, 5, 85]), reach=2.0)
put("decor/puits", "PuitsChamps", CH, 3.0, 8.6, reach=2.0)
put("decor/corde_linge", "LingeChamps", CH, 3.6, 12.6, rot=-15, reach=2.0)
put("decor/banc", "BancChamps", CH, 0.0, 8.8, face=CHC, reach=2.0)
put("decor/potager", "Potager2", CH, -4.4, 10.6, rot=10, reach=2.0)
for k, (x, z) in enumerate([(-2.0, 8.0), (4.4, 7.4), (9.8, 8.0), (1.0, 10.4), (6.6, 10.6), (-5.0, 7.6), (12.0, 7.6)]):
    put("decor/lampe_champignon", "LampeChamps%d" % (k + 1), CH, x, z, reach=1.5)
for n, (x, z) in {"LieuChamp1": (-2.2, 7.4), "LieuChamp2": (7.0, 7.6), "LieuChamp3": (9.6, 10.0), "LieuPuitsChamps": (3.0, 9.6),
                  "LieuLingeChamps": (3.6, 11.8), "LieuPotager2": (-4.0, 9.8)}.items():
    marker(n, CH, x, z)

# ================================================================ 4. le Levant (sol bas, côte est)
LV = group("Levant")
LVC = (13.0, 0.0)
LVB = (11.0, 17.5, -4.0, 4.5)
house("maisons/maison_coquillage", "MaisonLevant1", LV, LVB, (15.6, -2.0), face=LVC, scale=0.9)
house("maisons/maison_coquillage", "MaisonLevant2", LV, LVB, (16.0, 1.6), face=LVC, scale=0.9)
house("maisons/maison_souche", "MaisonLevant3", LV, LVB, (13.0, -2.6), face=LVC, scale=0.9)
house("maisons/maison_champignon", "MaisonLevant4", LV, LVB, (14.0, 2.6), face=LVC, scale=0.85)
put("decor/etal", "EtalPoisson", LV, 12.6, 0.6, face=LVC, reach=2.0)
put("decor/banc", "BancLevant", LV, 15.8, -0.2, face=(18, 0), reach=2.0)
for k, (x, z) in enumerate([(14.4, 0.0), (12.2, -1.0), (16.6, -0.8), (12.6, 2.6)]):
    put("decor/lampe_champignon", "LampeLevant%d" % (k + 1), LV, x, z, reach=1.5)
for k, (x, z) in enumerate([(16.8, 3.2), (16.6, -3.0), (11.6, 3.8)]):
    put("decor/corail", "CorailLevant%d" % (k + 1), LV, x, z, scale=1.4, reach=1.5)
for n, (x, z) in {"LieuEtalPoisson": (12.4, -0.2), "LieuRive": (16.8, 0.4), "LieuBancLevant": (15.2, 0.6)}.items():
    marker(n, LV, x, z)

# ================================================================ 5. les Hauts (plateau nord)
HA = group("Hauts")
HAC = (2.0, -10.0)
HAB = (-8.0, 8.0, -14.5, -7.0)
house("maisons/tour_ancienne", "MaisonHaute3", HA, HAB, (3.0, -12.0), face=HAC, scale=0.95)
house("maisons/maison_champignon", "MaisonHaute1", HA, HAB, (-6.0, -9.0), face=HAC, scale=0.9)
house("maisons/maison_souche", "MaisonHaute2", HA, HAB, (5.4, -9.2), face=HAC, scale=0.9)
house("maisons/maison_coquillage", "MaisonHaute4", HA, HAB, (1.6, -9.0), face=HAC, scale=0.9)
put("decor/puits", "PuitsHauts", HA, 2.6, -10.6, reach=4.0)
put("decor/potager", "JardinHauts", HA, 4.6, -12.6, rot=15, reach=4.0)
for k, (x, z) in enumerate([(-4.6, -9.6), (2.0, -8.2), (4.0, -10.6), (-1.0, -12.6)]):
    put("decor/lampe_champignon", "LampeHaute%d" % (k + 1), HA, x, z, reach=1.5)
for n, (x, z) in {"LieuPuitsHauts": (2.0, -10.4), "LieuJardinHauts": (4.2, -11.8)}.items():
    marker(n, HA, x, z)

# ================================================================ la forêt de géants (partout où il reste de la place)
FO = group("Foret")
GREL = ["decor/champignon_geant", "decor/champignon_geant_violet", "decor/champignon_geant_ambre"]
ng = 0
for k, (x, z, t) in enumerate([(-15.4, -4.8, 0), (-12.2, -5.4, 1), (-8.6, -4.8, 2), (-9.0, -7.2, 0), (-12.4, -11.8, 1),
                               (-16.8, 9.0, 2), (-7.0, -13.2, 0), (-4.0, -6.8, 2), (8.8, -7.6, 1), (10.4, -12.6, 0),
                               (5.2, -14.0, 2), (-11.4, -9.4, 0), (-2.5, 12.6, 0), (12.8, 9.6, 1), (16.0, 9.0, 2),
                               (-19.6, -5.6, 2), (10.6, -3.4, 0), (-6.4, 4.6, 1), (14.8, -3.4, 2), (-7.6, 11.4, 1),
                               (-21.6, -10.6, 1), (-22.6, -12.4, 0), (8.0, 4.6, 2), (-5.6, -3.6, 1), (11.6, 12.0, 0)]):
    if put(GREL[t], "Geant%d" % (ng + 1), FO, x, z, scale=random.choice([0.9, 1.0, 1.1]), reach=2.5):
        ng += 1

# ================================================================ nature semée sur toute l'île (fougères, mousse)
NA = group("Nature")
xs = [c[0] for c in CELLS]
zs = [c[1] for c in CELLS]
nf = nm = 0
for k in range(500):
    x = random.uniform(min(xs), max(xs) + 1)
    z = random.uniform(min(zs), max(zs) + 1)
    if nf < 70 and free_spot(x, z, 0.3, allow_path=False, margin=0.1):
        put("decor/fougere", "Fougere%d" % nf, NA, x, z, scale=random.uniform(1.0, 1.4), reach=0.1)
        nf += 1
    elif nm < 22 and free_spot(x, z, 0.7, allow_path=False, margin=0.1):
        put("decor/nappe_mousse", "Mousse%d" % nm, NA, x, z, scale=random.uniform(0.8, 1.2), reach=0.1)
        nm += 1

# ================================================================ habitants et conversations
anc1 = dialogue("ancienne_1", [
    "Tu restes éteint. C'est bien, Petit-Jour.",
    "Avant les Soleils-Fixes, toute l'île était à nous. La place, les champs, les hauts.",
    "Chaque fois que tu allumes, une maison tombe en cendre. Rallume, et regarde.",
], ["anc_eteint", "anc_avant", "anc_cendre"], forbids=["bascule"], once=True, sets="sait_cicatrices")
anc2 = dialogue("ancienne_2", [
    "Ceux d'avant, les Grands-Aveugles, ne voyaient rien.",
    "Alors ils ont tout allumé. Le jour ne finissait plus.",
    "Celle-qui-a-soufflé, elle, voyait. Elle est partie vers le nord, de l'autre côté de l'eau.",
], ["anc_aveugles", "", "anc_nord"], forbids=["bascule"])
anc3 = dialogue("ancienne_3", [
    "Celui-qui-revient… Tu as éteint ta lumière pour de bon.",
    "Les petites ont besoin de sortir de la Bouche. La veilleuse de la porte brûle leur seuil.",
    "Reprends sa lumière, et reste dans le noir : elles te suivront jusqu'aux pins.",
], ["anc_revient", "anc_veilleuse", ""], requires=["bascule"], forbids=["pouponniere_libre"])
anc4 = dialogue("ancienne_4", [
    "Les petites ont vu les pins. Le village respire.",
    "Il reste d'autres îles, d'autres peuples. Ils ont peur, comme nous avions peur.",
], ["anc_respire", ""], requires=["pouponniere_libre"])
habitant("Ancienne", V, -14.0, -3.0, 3, home="../TourAncienne", routine=["../LieuBanc", "../LieuPuits", "../LieuMarche"],
         dialogues=[anc1, anc2, anc3, anc4], extra={"peek_time": "2.0", "trust_flag": '&"bascule"', "talk_height": "1.9"})

pec1 = dialogue("pecheur_1", [
    "Tu tombes toujours au même endroit. Près de l'eau, à la crique.",
    "Le vieux Compteur garde une pierre pour chaque fois.",
    "Moi, je repêche ce que la mer rapporte. Une barque, un jour. Je l'ai cachée sous les racines, à l'ouest.",
], ["pech_crique", "", "pech_barque"], once=True, sets="indice_barque")
pec2 = dialogue("pecheur_2", [
    "Mon frère guette sur l'îlot de corail, au bout du ponton.",
    "Le pont ne se voit que la nuit. Ne rallume pas au milieu : il n'aime pas ça.",
], ["pech_ilot", ""], requires=["dlg_pecheur_1"], sets="indice_ilot")
habitant("Pecheur", V, -17.2, -4.4, 4, home="../CabanePilotis", routine=["../LieuCrique", "../LieuPonton"],
         dialogues=[pec1, pec2], chatter=["Le poisson de nuit ne mord qu'à la lueur douce.", "Pas de lumière près de mes filets, Petit-Jour."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.1"})
jar1 = dialogue("jardiniere_1", [
    "Ce qui pousse dans le noir éclaire juste assez.",
    "Les grands champignons tiennent la falaise. La nuit, leurs racines font des marches.",
    "Mais toi, avec ta lumière, tu n'y vois que des cailloux.",
], ["jard_noir", "jard_marches", ""], sets="indice_racines")
habitant("Jardiniere", CH, -2.0, 11.0, 5, home="../Maison7", routine=["../LieuPotager2", "../LieuChamp1", "../LieuPuitsChamps"],
         dialogues=[jar1], chatter=["Ne marche pas sur les pousses, elles dorment.", "Les fruits bleus sont pour les petites."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
tis1 = dialogue("tisserand_1", [
    "Chaque maison, je la retisse fil à fil.",
    "Quand un Soleil-Fixe s'allume, tout brûle en un instant. Pour retisser, il me faut des nuits.",
    "Si tu reprends la lumière d'une lanterne, je recommence. C'est long. Mais je recommence.",
], ["tiss_fil", "tiss_brule", "tiss_recommence"], sets="sait_retisser")
habitant("Tisserand", CH, 9.6, 6.6, 6, home="../Maison6", routine=["../LieuLingeChamps", "../LieuChamp2"],
         dialogues=[tis1], chatter=["Ce fil-là vient de la lune.", "Encore une maison à reprendre…"],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("Enfant2", V, -10.6, -2.6, 1, home="../../Hameau/Maison1", routine=["../LieuPuits", "../LieuPotager", "../LieuMarche"],
         chatter=["Tu as une lumière sur la tête. Ça pique les yeux.", "On joue à qui reste dans le noir le plus longtemps. Tu joues ?",
                  "Grand-mère dit qu'il ne faut pas te parler."],
         extra={"size": "0.9", "peek_time": "2.5", "trust_flag": '&"first_bribe"', "talk_height": "1.5"})
habitant("Petite3", V, -12.4, -2.0, 0, home="../../Hameau/Maison2", routine=["../LieuMarche", "../LieuPuits"], extra={"size": "0.8"})

# --- la Grand-Place
mar1 = dialogue("marchande_1", [
    "Tu vois la grande lanterne, au milieu ? Avant, c'était notre fontaine.",
    "Le jour où on l'allume, toute la place brûle. Les étals, les maisons, tout.",
    "Alors on vend vite, tant qu'il fait noir.",
], ["march_fontaine", "march_place", ""], sets="sait_grande_lanterne")
habitant("Marchande", GP, -3.0, 0.8, 5, home="../MaisonPlace1", routine=["../LieuEtal1", "../LieuEtal2", "../LieuFontaine"],
         dialogues=[mar1], chatter=["Des fruits de lune ! Qui veut des fruits de lune ?", "Celui-là brille plus fort. Il est mûr."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.0", "peek_time": "3.0"})
habitant("Conteur", GP, 0.6, -2.4, 3, home="../MaisonPlace2", routine=["../LieuBancs", "../LieuFontaine"],
         chatter=["On raconte qu'un Petit-Jour a appris à s'éteindre. On raconte beaucoup de choses.",
                  "La nuit dernière, les étoiles étaient basses. Bon signe."],
         extra={"size": "1.05", "trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("TisserandPlace", GP, 4.6, 2.0, 6, home="../MaisonPlace3", routine=["../LieuEtal3", "../LieuBancs"],
         chatter=["Une guirlande de plus pour la place.", "Ne touche pas, c'est tissé avec du clair d'eau."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
for k, (x, z) in enumerate([(-1.0, 1.6), (2.4, 2.4), (-2.2, -2.4)]):
    habitant("EnfantPlace%d" % (k + 1), GP, x, z, 1 if k != 2 else 0, home="../MaisonPlace%d" % (k + 1),
             routine=["../LieuFontaine", "../LieuEtal%d" % (k + 1), "../LieuBancs"],
             chatter=["Attrape-moi si tu peux !", "Tu ne brûles pas, toi, aujourd'hui ?"],
             extra={"size": "0.85" if k != 2 else "0.75", "peek_time": "3.0", "trust_flag": '&"first_bribe"', "talk_height": "1.5"})

# --- les Champs
pay1 = dialogue("paysan_1", [
    "Nos champs ne poussent que la nuit. Le jour, ils dorment sous la terre.",
    "Les deux Soleils du sud brûlent tout ce qui dépasse.",
    "Si tu les allumes, on recommencera. On recommence toujours.",
], ["pays_nuit", "pays_soleils", ""], sets="sait_champs")
habitant("Paysan", CH, 2.0, 7.6, 3, home="../Ferme1", routine=["../LieuChamp1", "../LieuChamp2", "../LieuPuitsChamps"],
         dialogues=[pay1], chatter=["Encore trois rangs à arroser.", "Les pousses violettes sont têtues."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("Paysanne", CH, 8.4, 8.2, 5, home="../Ferme2", routine=["../LieuChamp2", "../LieuChamp3", "../LieuLingeChamps"],
         chatter=["Il fait doux, ce soir.", "On récolte à la lune pleine."], extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("TisseuseChamps", CH, 4.6, 11.6, 6, home="../Ferme4", routine=["../LieuLingeChamps", "../LieuPuitsChamps"],
         chatter=["Le linge sèche mieux sous les étoiles."], extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
for k, (x, z) in enumerate([(-1.0, 8.0), (6.0, 8.6), (0.8, 10.4)]):
    habitant("PetiteChamps%d" % (k + 1), CH, x, z, 0 if k != 1 else 1, home="../Ferme%d" % (k + 2 if k < 2 else 1),
             routine=["../LieuChamp%d" % (k + 1), "../LieuPuitsChamps"],
             chatter=["On cherche des vers luisants !", "Chut, les pousses dorment."],
             extra={"size": "0.8", "peek_time": "3.0", "trust_flag": '&"first_bribe"', "talk_height": "1.4"})

# --- le Levant
pec3 = dialogue("pecheuse_1", [
    "De ce côté, le soleil se levait. Avant les Soleils-Fixes, c'était la seule lumière qu'on aimait.",
    "La cascade, là-haut, cache quelque chose. Les Grands-Aveugles y gardaient leurs papiers.",
], ["levant_soleil", "levant_cascade"], sets="indice_cascade_levant")
habitant("Pecheuse", LV, 13.4, 0.4, 4, home="../MaisonLevant2", routine=["../LieuEtalPoisson", "../LieuRive", "../LieuBancLevant"],
         dialogues=[pec3], chatter=["Le poisson-lune brille plus fort quand il a peur.", "La mer parle, si on l'écoute."],
         extra={"trust_flag": '&"bascule"', "talk_height": "2.1"})
habitant("PecheurLevant", LV, 15.0, -1.2, 4, home="../MaisonLevant4", routine=["../LieuRive", "../LieuEtalPoisson"],
         chatter=["Mes filets sont pleins de reflets.", "Chut. Ils mordent."], extra={"size": "0.95", "trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("EnfantLevant", LV, 13.8, 1.4, 1, home="../MaisonLevant1", routine=["../LieuRive", "../LieuBancLevant"],
         chatter=["J'ai trouvé un coquillage qui chante !"],
         extra={"size": "0.85", "peek_time": "3.0", "trust_flag": '&"first_bribe"', "talk_height": "1.5"})

# --- les Hauts
gar1 = dialogue("gardien_hauts_1", [
    "Ici, en haut, on voit venir la lumière avant tout le monde.",
    "Le Soleil du sommet est le plus vieux. C'est lui qui a chassé nos grands-parents.",
], ["hauts_voir", "hauts_sommet"], sets="sait_sommet")
habitant("GardienHauts", HA, 2.8, -9.6, 3, home="../MaisonHaute3", routine=["../LieuPuitsHauts", "../LieuJardinHauts"],
         dialogues=[gar1], chatter=["Le vent du nord sent la brume.", "Les géants poussent d'un doigt par nuit."],
         extra={"size": "1.1", "trust_flag": '&"bascule"', "talk_height": "2.1"})
habitant("JardiniereHauts", HA, 4.4, -11.4, 5, home="../MaisonHaute2", routine=["../LieuJardinHauts", "../LieuPuitsHauts"],
         chatter=["Les champignons d'en haut sont les plus sucrés."], extra={"trust_flag": '&"bascule"', "talk_height": "2.0"})
habitant("PetiteHauts", HA, -4.4, -9.0, 0, home="../MaisonHaute1", routine=["../LieuPuitsHauts"],
         chatter=["C'est haut, ici !"], extra={"size": "0.8", "trust_flag": '&"first_bribe"', "talk_height": "1.4"})

# --- le belvédère et l'îlot (chemins de l'ombre)
veil = dialogue("veilleur_1", [
    "Tu as monté les marches des géants. Peu de Petit-Jour savent qu'elles existent.",
    "D'ici, on voit toute la ville. Et les Soleils-Fixes qui la mangent.",
    "Celui du sommet est le pire. Quand il brûle, sa lumière descend jusqu'à la mer.",
], ["veil_marches", "", "veil_sommet"], sets="vu_belvedere")
habitant("Veilleur", C + "/Belvedere", -13.2, -8.2, 3, dialogues=[veil],
         chatter=["Regarde la ville respirer.", "Les marches t'attendront toujours, la nuit."],
         extra={"shy": "false", "follows": "false", "size": "1.15", "wander_radius": "0.6", "talk_height": "2.1"})
guet = dialogue("guetteur_1", [
    "Tu as marché sur l'eau, Petit-Jour. Le pont n'est là que pour ceux qui voient la nuit.",
    "De mon île, je vois le Phare. Ils sont là-bas aussi, sous la brume.",
    "Ceux du Phare n'ont pas d'yeux. Ils écoutent. Si tu vas les voir, va doucement. Et éteint.",
], ["guet_pont", "guet_phare", "guet_doucement"], sets="indice_phare")
raw("Guetteur", C, HABITANT, world=(-27.0, 0.55, 0.4), props={
    "form": 4, "routine": '[NodePath("../LieuIlot")]', "dialogues": dlist([guet]),
    "chatter": strs(["La mer est calme quand les Soleils dorment."]),
    "shy": "false", "follows": "false", "wander_radius": "0.8", "talk_height": "2.1"}, paths=["routine"])

# l'Enfant du hameau : ses conversations
enf1 = dialogue("enfant_1", [
    "Tu ne m'as pas brûlé.",
    "Il y a un endroit secret derrière l'eau qui tombe. On n'y va que quand tout est éteint.",
], ["enf_brule", "enf_secret"], requires=["first_bribe"], sets="indice_cascade")

# ================================================================ assemblage
print("non placés :", skipped)
HW = {n: placed["Ombre/Hameau/" + n] for n in ("Maison1", "Maison2", "Maison3") if "Ombre/Hameau/" + n in placed}
out_blocks = []
for b in kept:
    p = node_path(b)
    if p in ("Ombre/Hameau/Enfant", "Ombre/Hameau/Petite1", "Ombre/Hameau/Petite2"):
        home = {"Ombre/Hameau/Enfant": "Maison2", "Ombre/Hameau/Petite1": "Maison1", "Ombre/Hameau/Petite2": "Maison3"}[p]
        hw = HW[home]
        spot = find(hw[0] + 0.6, hw[2] + 1.8, 0.3, allow_path=True, reach=3.0) or (hw[0], hw[2] + 1.8)
        w = (spot[0], ground(*spot) or 0.5, spot[1])
        loc = (w[0] - HAMEAU[0], w[1] - HAMEAU[1], w[2] - HAMEAU[2])
        b = re.sub(r"transform = Transform3D\([^)]*\)", "transform = " + xform(loc), b)
        b = re.sub(r'home = NodePath\("[^"]*"\)', 'home = NodePath("../%s")' % home, b)
        b = re.sub(r"wander_radius = [0-9.]+\n", "", b)
        if p == "Ombre/Hameau/Enfant":
            b = b.replace("form = 1\n", "form = 1\ndialogues = %s\ntalk_height = 1.6\n" % dlist([enf1]))
        if p == "Ombre/Hameau/Petite1":
            b = b.replace("home =", 'routine = [NodePath("../Puits")]\nhome =').replace(
                'node_paths=PackedStringArray("home")', 'node_paths=PackedStringArray("home", "routine")')
    out_blocks.append(b)

hameau_nodes = [n for n in new_nodes if 'parent="Ombre/Hameau"' in n]
ext_nodes = [n for n in new_nodes if 'parent="Ombre/Hameau/Extension"' in n]
rest = [n for n in new_nodes if n not in hameau_nodes and n not in ext_nodes]
final = []
for b in out_blocks:
    final.append(b)
    if node_path(b) == "Ombre/Hameau":
        final.extend(hameau_nodes)
    if node_path(b) == "Ombre/Hameau/Extension":
        final.extend(ext_nodes)
final.extend(rest)

header = header.rstrip("\n")
last_ext = [m.end() for m in re.finditer(r"\[ext_resource [^\n]*\]", header)][-1]
header = header[:last_ext] + "\n" + "\n".join(ext_lines) + header[last_ext:]
header += "\n\n" + "\n".join(sub_res)
txt = header.rstrip("\n") + "\n\n" + "\n".join(b.rstrip("\n") + "\n" for b in final)
open(P, "w", encoding="utf-8").write(txt)
print("ok :", len(new_nodes), "nœuds,", len(sub_res), "conversations ; non placés :", skipped)
