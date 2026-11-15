# Kit du monde de l'ombre (maquette, étape 0) : matériaux, maisons, décors, petit peuple.
# Chaque pièce est une scène .tscn faite de formes low-poly (éditable dans Godot).
# Usage : python tools/ombre_kit.py
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = "assets/ombre"


def path(*p):
    return os.path.join(ROOT, *p)


# ---------------------------------------------------------------- matériaux
SHADER = "res://assets/shaders/ombre.gdshader"
MATS = {
    # nom : (couleur, émission)
    "bois_nuit": ((0.24, 0.18, 0.27), 0.0),
    "ecorce": ((0.2, 0.15, 0.2), 0.0),
    "toit_mousse": ((0.13, 0.27, 0.27), 0.0),
    "champi_pied": ((0.7, 0.66, 0.72), 0.0),
    "champi_chapeau": ((0.14, 0.34, 0.42), 0.0),
    "champi_chapeau_violet": ((0.3, 0.2, 0.42), 0.0),
    "coquille": ((0.66, 0.54, 0.66), 0.0),
    "coquille_raie": ((0.45, 0.35, 0.52), 0.0),
    "pierre_nuit": ((0.24, 0.25, 0.36), 0.0),
    "mousse": ((0.14, 0.24, 0.25), 0.0),
    "fougere": ((0.2, 0.42, 0.38), 0.25),
    "mousse_claire": ((0.17, 0.3, 0.3), 0.0),
    "sentier": ((0.3, 0.29, 0.38), 0.0),
    "eau_nuit": ((0.05, 0.09, 0.15), 0.0),
    "pin_nuit": ((0.15, 0.27, 0.3), 0.0),
    "tissu_rouille": ((0.55, 0.3, 0.27), 0.0),
    "tissu_mousse": ((0.27, 0.38, 0.32), 0.0),
    "tissu_sable": ((0.62, 0.56, 0.46), 0.0),
    "tissu_prune": ((0.38, 0.24, 0.4), 0.0),
    "tissu_ocre": ((0.66, 0.5, 0.26), 0.0),
    "peau_ombre": ((0.3, 0.33, 0.56), 0.0),
    # lumières (émissives)
    "lueur": ((0.45, 1.0, 0.86), 2.2),
    "lueur_douce": ((0.4, 0.85, 0.8), 0.9),
    "lueur_ambre": ((1.0, 0.78, 0.48), 1.8),
    "lueur_violette": ((0.75, 0.6, 1.0), 1.6),
    "fenetre": ((0.55, 1.0, 0.88), 2.6),
    "joue": ((1.0, 0.6, 0.78), 0.7),
    "reflet": ((1.0, 1.0, 1.0), 3.0),
    "oeil": ((0.62, 1.0, 0.92), 0.9),
    "champi_chapeau_ambre": ((0.5, 0.3, 0.2), 0.0),
    "tissu_nuit": ((0.16, 0.2, 0.32), 0.0),
    "corde": ((0.5, 0.45, 0.4), 0.0),
    "lueur_rose": ((1.0, 0.6, 0.78), 1.4),
    "fenetre_ambre": ((1.0, 0.8, 0.5), 2.2),
}


def write_materials():
    os.makedirs(path(OUT, "materials"), exist_ok=True)
    for name, (c, e) in MATS.items():
        with open(path(OUT, "materials", name + ".tres"), "w", encoding="utf-8") as f:
            f.write('[gd_resource type="ShaderMaterial" load_steps=2 format=3]\n\n')
            f.write('[ext_resource type="Shader" path="%s" id="1"]\n\n' % SHADER)
            f.write("[resource]\nshader = ExtResource(\"1\")\n")
            f.write("shader_parameter/albedo = Color(%.3f, %.3f, %.3f, 1)\n" % c)
            f.write("shader_parameter/emission_strength = %.2f\n" % e)


# ---------------------------------------------------------------- scène
def basis(rot=(0, 0, 0), scale=(1, 1, 1)):
    rx, ry, rz = [math.radians(a) for a in rot]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Y = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Z = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

    # ordre Godot (YXZ) : R = Y * X * Z
    R = mul(mul(Y, X), Z)
    return [[R[i][j] * scale[j] for j in range(3)] for i in range(3)]


def xform(pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    b = basis(rot, scale)
    vals = [b[0][0], b[0][1], b[0][2], b[1][0], b[1][1], b[1][2], b[2][0], b[2][1], b[2][2], *pos]
    return "Transform3D(%s)" % ", ".join("%.4g" % v for v in vals)


class Scene:
    def __init__(self, root_name, root_type="Node3D", script=None):
        self.ext = []        # (type, path, id)
        self.sub = []        # (type, id, props)
        self.nodes = []      # texte
        self.root = root_name
        self._mesh_cache = {}
        hdr = '[node name="%s" type="%s"]\n' % (root_name, root_type)
        if script:
            hdr += 'script = ExtResource("%s")\n' % self.ext_res("Script", script)
        self.nodes.append(hdr)

    def ext_res(self, typ, p):
        for t, pp, i in self.ext:
            if pp == p:
                return i
        i = "%d_r" % (len(self.ext) + 1)
        self.ext.append((typ, p, i))
        return i

    def mat(self, name):
        return self.ext_res("Material", "res://%s/materials/%s.tres" % (OUT, name))

    def mesh(self, typ, **props):
        key = (typ, tuple(sorted(props.items())))
        if key in self._mesh_cache:
            return self._mesh_cache[key]
        i = "%s_%d" % (typ, len(self.sub) + 1)
        self.sub.append((typ, i, props))
        self._mesh_cache[key] = i
        return i

    def node(self, name, typ, parent=".", **props):
        s = '\n[node name="%s" type="%s" parent="%s"]\n' % (name, typ, parent)
        for k, v in props.items():
            s += "%s = %s\n" % (k, v)
        self.nodes.append(s)
        return name if parent == "." else parent + "/" + name

    def instance(self, name, scene_path, parent=".", **props):
        i = self.ext_res("PackedScene", scene_path)
        s = '\n[node name="%s" parent="%s" instance=ExtResource("%s")]\n' % (name, parent, i)
        for k, v in props.items():
            s += "%s = %s\n" % (k, v)
        self.nodes.append(s)

    def part(self, name, mesh_id, mat, parent=".", pos=(0, 0, 0), rot=(0, 0, 0), scale=1):
        return self.node(name, "MeshInstance3D", parent,
                         transform=xform(pos, rot, scale),
                         mesh='SubResource("%s")' % mesh_id,
                         **{"surface_material_override/0": 'ExtResource("%s")' % self.mat(mat)})

    # formes
    def cyl(self, top, bottom, h, seg=8):
        return self.mesh("CylinderMesh", top_radius=round(top, 3), bottom_radius=round(bottom, 3), height=round(h, 3), radial_segments=seg, rings=0)

    def sph(self, r, h=None, seg=8, rings=4):
        return self.mesh("SphereMesh", radius=round(r, 3), height=round(h if h else 2 * r, 3), radial_segments=seg, rings=rings)

    def box(self, x, y, z):
        return self.mesh("BoxMesh", size="Vector3(%.3f, %.3f, %.3f)" % (x, y, z))

    def light(self, name, parent=".", pos=(0, 0, 0), color=(0.45, 1.0, 0.86), energy=1.0, rng=3.0):
        return self.node(name, "OmniLight3D", parent, transform=xform(pos),
                         light_color="Color(%.2f, %.2f, %.2f, 1)" % color, light_energy=energy, omni_range=rng,
                         omni_attenuation=1.6)

    def collision_box(self, size, pos):
        sid = self.mesh("BoxShape3D", size="Vector3(%.2f, %.2f, %.2f)" % size)
        self.node("Collision%d" % len(self.nodes), "CollisionShape3D", ".", transform=xform(pos), shape='SubResource("%s")' % sid)

    def collision_cyl(self, r, h, pos):
        sid = self.mesh("CylinderShape3D", radius=r, height=h)
        self.node("Collision%d" % len(self.nodes), "CollisionShape3D", ".", transform=xform(pos), shape='SubResource("%s")' % sid)

    def save(self, rel):
        out = '[gd_scene load_steps=%d format=3]\n\n' % (len(self.ext) + len(self.sub) + 1)
        for t, p, i in self.ext:
            out += '[ext_resource type="%s" path="%s" id="%s"]\n' % (t, p, i)
        out += "\n"
        for t, i, props in self.sub:
            out += '[sub_resource type="%s" id="%s"]\n' % (t, i)
            for k, v in props.items():
                out += "%s = %s\n" % (k, v)
            out += "\n"
        out += "".join(self.nodes)
        full = path(rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(out)
        print("ok", rel)


# ---------------------------------------------------------------- petits éléments réutilisés
def door(s, parent, pos, rot_y, w=0.42, h=0.62):
    s.part("Porte", s.box(w, h, 0.08), "bois_nuit", parent, pos=(pos[0], pos[1] + h / 2, pos[2]), rot=(0, rot_y, 0))
    # arche et seuil lumineux
    s.part("Arche", s.cyl(w / 2, w / 2, 0.08, 8), "bois_nuit", parent, pos=(pos[0], pos[1] + h, pos[2]), rot=(90, rot_y, 0))
    s.part("Poignee", s.sph(0.03), "lueur", parent, pos=(pos[0] + 0.13 * math.cos(math.radians(rot_y)), pos[1] + h * 0.45, pos[2] - 0.13 * math.sin(math.radians(rot_y))), rot=(0, rot_y, 0))


def round_window(s, name, parent, pos, rot_y, r=0.15):
    s.part(name, s.cyl(r, r, 0.06, 8), "fenetre", parent, pos=pos, rot=(90, rot_y, 0))
    s.part(name + "Cadre", s.cyl(r + 0.05, r + 0.05, 0.04, 8), "bois_nuit", parent, pos=pos, rot=(90, rot_y, 0))


def facing(r, ang_deg, y):
    """point sur un cylindre de rayon r, à l'angle donné (0 = vers +z)"""
    a = math.radians(ang_deg)
    return (r * math.sin(a), y, r * math.cos(a))


# ---------------------------------------------------------------- maisons
def maison_champignon():
    s = Scene("MaisonChampignon", "StaticBody3D")
    s.collision_cyl(0.85, 2.6, (0, 1.3, 0))
    s.part("Pied", s.cyl(0.72, 0.85, 1.5, 8), "champi_pied", pos=(0, 0.75, 0))
    s.part("Socle", s.cyl(0.95, 1.05, 0.18, 8), "pierre_nuit", pos=(0, 0.09, 0))
    # chapeau : un cône large et bas + un dôme
    s.part("Chapeau", s.cyl(0.6, 1.55, 0.55, 9), "champi_chapeau", pos=(0, 1.75, 0))
    s.part("Dome", s.sph(0.95, 0.9, 9, 4), "champi_chapeau", pos=(0, 2.0, 0), scale=(1.0, 1.0, 1.0))
    # lamelles lumineuses sous le chapeau
    s.part("Lamelles", s.cyl(1.45, 0.75, 0.06, 9), "lueur_douce", pos=(0, 1.46, 0))
    # taches lumineuses
    for k, (a, y, r) in enumerate([(20, 2.2, 0.85), (110, 2.05, 1.1), (200, 2.25, 0.8), (290, 2.0, 1.15), (340, 2.35, 0.5), (160, 2.4, 0.4)]):
        p = facing(r, a, y)
        s.part("Tache%d" % k, s.sph(0.09, 0.07, 6, 3), "lueur", pos=p)
    door(s, ".", facing(0.78, 0, 0.18), 0)
    round_window(s, "Fenetre1", ".", facing(0.76, 60, 1.05), 60)
    round_window(s, "Fenetre2", ".", facing(0.76, -70, 0.85), -70, 0.12)
    # marche + petite lampe-champignon à la porte
    s.part("Marche", s.box(0.6, 0.1, 0.3), "pierre_nuit", pos=(0, 0.05, 1.0))
    s.instance("Lampe", "res://%s/decor/lampe_champignon.tscn" % OUT, transform=xform((0.55, 0, 1.0)))
    s.light("Interieur", ".", (0, 1.0, 1.1), energy=0.6, rng=2.5)
    s.save("%s/maisons/maison_champignon.tscn" % OUT)


def maison_souche():
    s = Scene("MaisonSouche", "StaticBody3D")
    s.collision_cyl(1.0, 2.4, (0, 1.2, 0))
    s.part("Tronc", s.cyl(0.85, 1.0, 1.7, 7), "ecorce", pos=(0, 0.85, 0))
    for k in range(5):  # racines
        a = k * 72 + 15
        p = facing(1.0, a, 0.15)
        s.part("Racine%d" % k, s.box(0.28, 0.3, 0.7), "ecorce", pos=p, rot=(18, a, 0))
    s.part("Rebord", s.cyl(0.95, 0.9, 0.12, 7), "bois_nuit", pos=(0, 1.75, 0))
    s.part("Toit", s.cyl(0.0, 1.2, 1.0, 7), "toit_mousse", pos=(0, 2.3, 0), rot=(0, 10, 0))
    s.part("Pointe", s.sph(0.1, 0.12, 6, 3), "lueur", pos=(0, 2.85, 0))
    s.part("Cheminee", s.cyl(0.1, 0.12, 0.5, 6), "pierre_nuit", pos=(0.45, 2.45, -0.3))
    door(s, ".", facing(0.9, 10, 0.08), 10)
    round_window(s, "Fenetre1", ".", facing(0.86, -55, 1.15), -55)
    round_window(s, "Fenetre2", ".", facing(0.86, 80, 1.3), 80, 0.12)
    s.part("RideauChaud", s.cyl(0.13, 0.13, 0.07, 8), "lueur_ambre", ".", pos=facing(0.88, -55, 1.15), rot=(90, -55, 0))
    # petit balcon et lanterne suspendue
    s.part("Balcon", s.box(0.9, 0.06, 0.4), "bois_nuit", pos=facing(1.05, 80, 1.0), rot=(0, 80, 0))
    s.part("Corde", s.box(0.015, 0.4, 0.015), "bois_nuit", pos=(-0.55, 1.45, 0.85))
    s.part("Lanterne", s.sph(0.1, 0.16, 6, 3), "lueur_ambre", pos=(-0.55, 1.2, 0.85))
    s.light("Interieur", ".", (0, 1.0, 1.1), energy=0.5, rng=2.5)
    s.light("LampeAmbre", ".", (-0.55, 1.2, 0.95), (1.0, 0.75, 0.45), 0.5, 2.0)
    s.save("%s/maisons/maison_souche.tscn" % OUT)


def maison_coquillage():
    s = Scene("MaisonCoquillage", "StaticBody3D")
    s.collision_cyl(0.95, 2.0, (0, 1.0, 0))
    # spirale : anneaux empilés qui rétrécissent et tournent
    y = 0.0
    r = 1.0
    for k in range(5):
        h = 0.42 - k * 0.04
        off = (0.08 * math.sin(k * 1.4), 0, 0.08 * math.cos(k * 1.4))
        s.part("Spire%d" % k, s.cyl(r * 0.82, r, h, 9), "coquille" if k % 2 == 0 else "coquille_raie",
               pos=(off[0], y + h / 2, off[2]), rot=(0, k * 23, 0))
        y += h
        r *= 0.78
    s.part("Pointe", s.cyl(0.0, r, 0.4, 9), "coquille", pos=(0.05, y + 0.2, 0.05))
    s.part("Perle", s.sph(0.11, 0.2, 8, 4), "lueur_violette", pos=(0.05, y + 0.45, 0.05))
    door(s, ".", facing(0.93, 20, 0.0), 20, 0.4, 0.55)
    round_window(s, "Fenetre1", ".", facing(0.7, -60, 0.95), -60, 0.12)
    # algues lumineuses au pied
    for k, a in enumerate([70, 130, 250]):
        p = facing(1.0, a, 0.25)
        s.part("Algue%d" % k, s.cyl(0.0, 0.06, 0.5, 5), "lueur_douce", pos=p, rot=(12, a, 0))
    s.light("Interieur", ".", (0.3, 0.8, 1.0), (0.75, 0.6, 1.0), 0.6, 2.5)
    s.save("%s/maisons/maison_coquillage.tscn" % OUT)


# ---------------------------------------------------------------- décor
def lampe_champignon():
    s = Scene("LampeChampignon")
    s.part("Pied", s.cyl(0.04, 0.06, 0.4, 6), "champi_pied", pos=(0, 0.2, 0), rot=(0, 0, 6))
    s.part("Chapeau", s.sph(0.17, 0.14, 8, 3), "lueur", pos=(0.02, 0.42, 0))
    s.part("Petit", s.sph(0.08, 0.07, 6, 3), "lueur_douce", pos=(0.14, 0.15, 0.06))
    s.light("Lumiere", ".", (0, 0.45, 0), energy=0.5, rng=1.8)
    s.save("%s/decor/lampe_champignon.tscn" % OUT)


def champignon_geant(name="ChampignonGeant", h=3.6, cap=1.6, mat="champi_chapeau", rel="champignon_geant"):
    s = Scene(name, "StaticBody3D")
    s.collision_cyl(0.3, h, (0, h / 2, 0))
    s.part("Pied", s.cyl(0.22, 0.38, h, 7), "champi_pied", pos=(0, h / 2, 0), rot=(0, 0, 3))
    s.part("Anneau", s.cyl(0.4, 0.3, 0.12, 7), "champi_pied", pos=(0.05, h * 0.62, 0))
    s.part("Chapeau", s.cyl(0.25, cap, cap * 0.32, 9), mat, pos=(0.12, h + cap * 0.1, 0))
    s.part("Dome", s.sph(cap * 0.62, cap * 0.5, 9, 4), mat, pos=(0.12, h + cap * 0.22, 0))
    s.part("Lamelles", s.cyl(cap * 0.95, 0.3, 0.05, 9), "lueur_douce", pos=(0.12, h - cap * 0.06, 0))
    for k in range(6):
        p = facing(cap * (0.45 + 0.1 * (k % 3)), k * 61, h + cap * 0.3)
        s.part("Tache%d" % k, s.sph(0.1, 0.07, 6, 3), "lueur", pos=(p[0] + 0.12, p[1], p[2]))
    s.light("Lumiere", ".", (0.12, h - 0.3, 0), energy=0.9, rng=4.5)
    s.save("%s/decor/%s.tscn" % (OUT, rel))


def puits():
    s = Scene("Puits", "StaticBody3D")
    s.collision_cyl(0.6, 0.8, (0, 0.4, 0))
    s.part("Margelle", s.cyl(0.6, 0.65, 0.55, 8), "pierre_nuit", pos=(0, 0.27, 0))
    s.part("Eau", s.cyl(0.48, 0.48, 0.02, 8), "lueur", pos=(0, 0.5, 0))
    for x in (-0.55, 0.55):
        s.part("Poteau%s" % ("G" if x < 0 else "D"), s.box(0.09, 1.2, 0.09), "bois_nuit", pos=(x, 0.8, 0))
    s.part("Toit", s.cyl(0.0, 0.7, 0.35, 4), "toit_mousse", pos=(0, 1.5, 0), rot=(0, 45, 0))
    s.part("Seau", s.cyl(0.1, 0.08, 0.15, 6), "bois_nuit", pos=(0, 1.0, 0))
    s.light("Reflet", ".", (0, 0.7, 0), energy=0.6, rng=2.2)
    s.save("%s/decor/puits.tscn" % OUT)


def etal():
    s = Scene("Etal", "StaticBody3D")
    s.collision_box((1.4, 0.8, 0.7), (0, 0.4, 0))
    s.part("Table", s.box(1.4, 0.08, 0.7), "bois_nuit", pos=(0, 0.6, 0))
    for x in (-0.62, 0.62):
        for z in (-0.28, 0.28):
            s.part("Pied%d%d" % (x > 0, z > 0), s.box(0.07, 0.6, 0.07), "bois_nuit", pos=(x, 0.3, z))
    for x in (-0.66, 0.66):
        s.part("Mat%s" % ("G" if x < 0 else "D"), s.box(0.06, 1.0, 0.06), "bois_nuit", pos=(x, 1.1, -0.3))
    s.part("Toile", s.box(1.55, 0.04, 0.9), "tissu_prune", pos=(0, 1.55, -0.05), rot=(-14, 0, 0))
    # fruits lumineux, paniers
    for k in range(7):
        s.part("Fruit%d" % k, s.sph(0.07, 0.12, 6, 3), ["lueur", "lueur_ambre", "lueur_violette"][k % 3],
               pos=(-0.5 + k * 0.16, 0.7, 0.1 * math.sin(k * 2.0)))
    s.part("Panier", s.cyl(0.22, 0.16, 0.18, 7), "tissu_sable", pos=(0.4, 0.73, -0.15))
    s.light("Lumiere", ".", (0, 0.9, 0.2), (0.9, 0.8, 0.6), 0.5, 2.0)
    s.save("%s/decor/etal.tscn" % OUT)


def corde_linge():
    s = Scene("CordeLinge")
    for x in (-1.0, 1.0):
        s.part("Poteau%s" % ("G" if x < 0 else "D"), s.box(0.08, 1.4, 0.08), "bois_nuit", pos=(x, 0.7, 0))
    s.part("Fil", s.box(2.0, 0.015, 0.015), "lueur_douce", pos=(0, 1.32, 0))
    for k, (x, mat, h) in enumerate([(-0.6, "tissu_rouille", 0.35), (-0.15, "tissu_sable", 0.28), (0.3, "tissu_mousse", 0.4), (0.7, "tissu_prune", 0.25)]):
        s.part("Linge%d" % k, s.box(0.3, h, 0.02), mat, pos=(x, 1.3 - h / 2, 0))
    s.save("%s/decor/corde_linge.tscn" % OUT)


def potager():
    s = Scene("Potager")
    s.part("Terre", s.box(1.6, 0.14, 1.0), "ecorce", pos=(0, 0.07, 0))
    for k in range(10):
        x = -0.6 + (k % 5) * 0.3
        z = -0.25 if k < 5 else 0.25
        s.part("Pousse%d" % k, s.sph(0.07 + 0.02 * (k % 2), 0.08, 6, 3), "lueur" if k % 3 else "lueur_violette", pos=(x, 0.2, z))
        s.part("Tige%d" % k, s.cyl(0.015, 0.015, 0.12, 4), "champi_pied", pos=(x, 0.15, z))
    for x in (-0.82, 0.82):
        s.part("Bord%s" % ("G" if x < 0 else "D"), s.box(0.06, 0.2, 1.05), "bois_nuit", pos=(x, 0.1, 0))
    s.save("%s/decor/potager.tscn" % OUT)


def fougere():
    s = Scene("Fougere")
    for k in range(5):
        a = k * 72
        p = facing(0.12, a, 0.16)
        s.part("Feuille%d" % k, s.box(0.07, 0.36, 0.02), "fougere", pos=p, rot=(28, a, 0))
    s.part("Bourgeon", s.sph(0.04, 0.05, 6, 3), "lueur_violette", pos=(0, 0.3, 0))
    s.save("%s/decor/fougere.tscn" % OUT)


def pin_nuit():
    s = Scene("PinNuit", "StaticBody3D")
    s.collision_cyl(0.25, 1.6, (0, 0.8, 0))
    s.part("Tronc", s.cyl(0.06, 0.1, 0.5, 6), "ecorce", pos=(0, 0.25, 0))
    s.part("Bas", s.cyl(0.0, 0.55, 1.1, 7), "pin_nuit", pos=(0, 0.95, 0))
    s.part("Haut", s.cyl(0.0, 0.42, 0.9, 7), "pin_nuit", pos=(0, 1.45, 0), rot=(0, 23, 0))
    # fils de lumière et lucioles accrochés aux branches
    for k, (a, y) in enumerate([(30, 0.8), (150, 1.0), (260, 1.3)]):
        p = facing(0.38, a, y)
        s.part("Goutte%d" % k, s.sph(0.04, 0.06, 6, 3), "lueur", pos=p)
    s.save("%s/decor/pin_nuit.tscn" % OUT)


# ---------------------------------------------------------------- petit peuple
def villageois(variant):
    """Un habitant : corps sombre veiné de lumière, gros yeux, un vêtement qui le distingue."""
    names = {"enfant": "Enfant", "ancienne": "Ancienne", "pecheur": "Pecheur", "jardiniere": "Jardiniere"}
    s = Scene(names[variant])
    sc = {"enfant": 1.05, "ancienne": 1.3, "pecheur": 1.42, "jardiniere": 1.35}[variant]
    root = s.node("Corps", "Node3D", ".", transform=xform((0, 0, 0), (0, 0, 0), sc))
    bend = 14 if variant == "ancienne" else 0
    # pieds
    for x in (-0.11, 0.11):
        s.part("Pied%s" % ("G" if x < 0 else "D"), s.box(0.12, 0.08, 0.17), "peau_ombre", root, pos=(x, 0.04, 0.03))
    # robe / corps (un tronc de cône)
    robe = {"enfant": "tissu_ocre", "ancienne": "tissu_prune", "pecheur": "tissu_mousse", "jardiniere": "tissu_sable"}[variant]
    s.part("Robe", s.cyl(0.2, 0.3, 0.5, 8), robe, root, pos=(0, 0.33, 0), rot=(bend * 0.4, 0, 0))
    s.part("Coeur", s.sph(0.06, 0.08, 6, 3), "lueur", root, pos=(0, 0.45, 0.2 + bend * 0.004))
    s.light("Halo", root, (0, 0.7, 0.45), (0.5, 1.0, 0.88), 0.45, 1.6)
    # tête : grosse et ronde, sombre, avec des veines lumineuses
    head_pos = (0, 0.8, 0.06 + bend * 0.012)
    tete = s.node("Tete", "Node3D", root, transform=xform(head_pos, (bend, 0, 0)))
    s.part("Crane", s.sph(0.27, 0.5, 10, 5), "peau_ombre", tete)
    for x in (-0.1, 0.1):
        s.part("Oeil%s" % ("G" if x < 0 else "D"), s.sph(0.07, 0.09, 8, 4), "lueur", tete, pos=(x, 0.02, 0.22))
    for k, (x, y, z) in enumerate([(-0.17, -0.07, 0.17), (0.17, -0.07, 0.17), (0.0, 0.2, 0.15)]):
        s.part("Veine%d" % k, s.sph(0.025, 0.03, 6, 3), "lueur_douce", tete, pos=(x, y, z))
    # bras
    for x in (-1, 1):
        s.part("Bras%s" % ("G" if x < 0 else "D"), s.cyl(0.04, 0.05, 0.32, 6), "peau_ombre", root,
               pos=(0.25 * x, 0.38, 0.02), rot=(0, 0, 22 * x))
        s.part("Main%s" % ("G" if x < 0 else "D"), s.sph(0.05, 0.08, 6, 3), "peau_ombre", root, pos=(0.31 * x, 0.23, 0.04))
    # accessoires
    if variant == "enfant":
        s.part("Echarpe", s.cyl(0.22, 0.24, 0.08, 8), "tissu_rouille", root, pos=(0, 0.58, 0.02))
        s.part("Pan", s.box(0.08, 0.22, 0.03), "tissu_rouille", root, pos=(0.12, 0.47, 0.2), rot=(10, 0, -12))
        s.part("Antenne", s.cyl(0.01, 0.015, 0.16, 4), "peau_ombre", tete, pos=(0.05, 0.3, 0), rot=(0, 0, -15))
        s.part("AntenneBout", s.sph(0.035, 0.05, 6, 3), "lueur", tete, pos=(0.08, 0.38, 0))
    elif variant == "ancienne":
        s.part("Capuche", s.cyl(0.08, 0.3, 0.38, 8), "tissu_prune", tete, pos=(0, 0.13, -0.05), rot=(-12, 0, 0))
        s.part("Chale", s.cyl(0.23, 0.32, 0.12, 8), "tissu_mousse", root, pos=(0, 0.55, 0.0))
        s.part("Baton", s.cyl(0.02, 0.025, 0.9, 5), "bois_nuit", root, pos=(0.36, 0.45, 0.12), rot=(0, 0, -4))
        s.part("BatonLueur", s.sph(0.06, 0.08, 6, 3), "lueur_ambre", root, pos=(0.38, 0.92, 0.12))
        s.light("LueurBaton", root, (0.38, 0.95, 0.15), (1.0, 0.78, 0.48), 0.4, 1.8)
    elif variant == "pecheur":
        s.part("Chapeau", s.cyl(0.18, 0.42, 0.14, 8), "tissu_ocre", tete, pos=(0, 0.22, 0))
        s.part("ChapeauHaut", s.cyl(0.14, 0.18, 0.12, 8), "tissu_ocre", tete, pos=(0, 0.33, 0))
        s.part("Canne", s.cyl(0.012, 0.02, 1.4, 5), "bois_nuit", root, pos=(-0.35, 0.75, 0.25), rot=(30, 0, 25))
        s.part("Fil", s.box(0.008, 0.5, 0.008), "lueur_douce", root, pos=(-0.68, 1.1, 0.62))
        s.part("Appat", s.sph(0.04, 0.06, 6, 3), "lueur", root, pos=(-0.68, 0.85, 0.62))
    elif variant == "jardiniere":
        s.part("Tablier", s.box(0.32, 0.36, 0.03), "tissu_rouille", root, pos=(0, 0.3, 0.27), rot=(-8, 0, 0))
        s.part("Fichu", s.cyl(0.16, 0.27, 0.12, 8), "tissu_mousse", tete, pos=(0, 0.18, -0.02))
        s.part("Panier", s.cyl(0.13, 0.1, 0.12, 7), "tissu_sable", root, pos=(-0.33, 0.25, 0.1))
        for k in range(3):
            s.part("Cueillette%d" % k, s.sph(0.05, 0.06, 6, 3), "lueur", root, pos=(-0.36 + 0.05 * k, 0.33, 0.08 + 0.03 * k))
    s.save("%s/peuple/%s.tscn" % (OUT, variant))


def build_all():
    write_materials()
    lampe_champignon()
    champignon_geant()
    champignon_geant("ChampignonGeantViolet", 2.6, 1.2, "champi_chapeau_violet", "champignon_geant_violet")
    puits()
    etal()
    corde_linge()
    potager()
    pin_nuit()
    fougere()
    maison_champignon()
    maison_souche()
    maison_coquillage()
    # l'enfant est modélisé dans Blender (blender/peuple.blend → tools/peuple_scene.py)
    for v in ("ancienne", "pecheur", "jardiniere"):
        villageois(v)




# ---------------------------------------------------------------- maquette
def mockup():
    s = Scene("OmbreMockup")
    s.node("ToutVisible", "Node", ".", script='ExtResource("%s")' % s.ext_res("Script", "res://scripts/ombre/ombre_tout_visible.gd"))
    env = s.mesh("Environment", background_mode=1, background_color="Color(0.04, 0.06, 0.13, 1)",
                 ambient_light_source=2, ambient_light_color="Color(0.35, 0.42, 0.7, 1)", ambient_light_energy=0.55,
                 ssao_enabled="true", ssao_radius=0.8, ssao_intensity=1.4,
                 glow_enabled="true", glow_intensity=0.9, glow_bloom=0.12, glow_hdr_threshold=0.8,
                 fog_enabled="true", fog_light_color="Color(0.1, 0.2, 0.3, 1)", fog_density=0.012)
    s.node("WorldEnvironment", "WorldEnvironment", ".", environment='SubResource("%s")' % env)
    s.node("Lune", "DirectionalLight3D", ".", transform=xform((0, 10, 0), (-50, -30, 0)),
           light_color="Color(0.62, 0.72, 1, 1)", light_energy=0.55, shadow_enabled="true", shadow_blur=2.0)
    # sol : plateau en blocs de mousse, une marche, un sentier de pierres, l'eau autour
    g = s.node("Sol", "Node3D")
    s.part("Eau", s.box(60, 0.1, 60), "eau_nuit", g, pos=(0, -0.55, 0))
    for k in range(40):  # reflets turquoise sur l'eau
        x = -14 + (k * 7.3) % 28
        z = -12 + (k * 5.1) % 26
        if abs(x) < 8.5 and abs(z) < 7.5:
            continue
        s.part("Reflet%d" % k, s.box(0.6 + (k % 3) * 0.3, 0.02, 0.06), "lueur_douce", g, pos=(x, -0.48, z))
    s.part("Plateau", s.box(16, 1.0, 13), "mousse", g, pos=(0, -0.5, 0))
    sol = s.node("SolPhysique", "StaticBody3D", ".")
    sid = s.mesh("BoxShape3D", size="Vector3(16, 1, 13)")
    s.node("Forme", "CollisionShape3D", sol, transform=xform((0, -0.5, 0)), shape='SubResource("%s")' % sid)
    for k in range(26):  # fougères lumineuses
        x = -7.2 + (k * 4.31) % 14.4
        z = -5.8 + (k * 3.37) % 11.6
        s.instance("Fougere%d" % k, "res://%s/decor/fougere.tscn" % OUT, transform=xform((x, 0, z), (0, k * 41, 0), 0.8 + 0.1 * (k % 4)))
    s.part("Falaise", s.box(16.2, 0.8, 13.2), "pierre_nuit", g, pos=(0, -0.9, 0))
    s.part("Terrasse", s.box(6, 0.5, 5), "mousse_claire", g, pos=(-4.5, 0.25, -3.5))
    s.part("TerrasseBord", s.box(6.1, 0.3, 5.1), "pierre_nuit", g, pos=(-4.5, 0.05, -3.5))
    for k in range(4):
        s.part("Marche%d" % k, s.box(0.9, 0.12 * (k + 1), 0.5), "pierre_nuit", g, pos=(-1.2, 0.06 * (k + 1), -1.7 - k * 0.0) if False else (-1.05 - k * 0.0, 0.06 * (k + 1), -0.6 - k * 0.45))
    # sentier : dalles lumineuses
    path_pts = [(3.5, 5.0), (2.6, 3.8), (1.6, 2.7), (0.6, 1.8), (-0.3, 0.9), (-1.0, 0.2), (1.9, 0.6), (3.0, 0.2), (4.0, -0.4), (5.0, -1.0)]
    for k, (x, z) in enumerate(path_pts):
        s.part("Dalle%d" % k, s.cyl(0.32, 0.36, 0.06, 6), "sentier", g, pos=(x, 0.03, z), rot=(0, k * 17, 0))
        if k % 2 == 0:
            s.part("DalleLueur%d" % k, s.sph(0.05, 0.04, 6, 3), "lueur_douce", g, pos=(x + 0.15, 0.07, z + 0.1))
    # mousse lumineuse semée au sol
    for k in range(70):
        x = -7.5 + (k * 3.77) % 15
        z = -6 + (k * 2.93) % 12
        s.part("Point%d" % k, s.sph(0.035, 0.03, 5, 2), "lueur" if k % 4 else "lueur_violette", g, pos=(x, 0.02, z))
    # décor
    I = lambda name, rel, pos, rot=0, sc=1: s.instance(name, "res://%s/%s.tscn" % (OUT, rel), transform=xform(pos, (0, rot, 0), sc))
    I("MaisonChampignon", "maisons/maison_champignon", (-4.8, 0.5, -3.6), 20)
    I("MaisonSouche", "maisons/maison_souche", (1.8, 0, -3.2), -15)
    I("MaisonCoquillage", "maisons/maison_coquillage", (4.8, 0, 2.6), -50)
    I("Puits", "decor/puits", (0.4, 0, 0.6))
    I("Etal", "decor/etal", (-2.6, 0, 1.6), 30)
    I("CordeLinge", "decor/corde_linge", (4.2, 0, -1.8), -20)
    I("Potager", "decor/potager", (-2.4, 0, 4.2), 10)
    I("Geant1", "decor/champignon_geant", (-6.8, 0, 2.2), 0, 1.1)
    I("Geant2", "decor/champignon_geant_violet", (6.6, 0, -4.8), 40)
    I("Geant3", "decor/champignon_geant", (-1.2, 0.5, -5.6), 80, 0.8)
    for k, (x, z) in enumerate([(-7.0, -5.5), (-6.2, -1.0), (7.0, 0.5), (6.6, 4.8), (3.6, -5.6), (-7.2, 5.4), (0.8, 5.6)]):
        I("Pin%d" % k, "decor/pin_nuit", (x, 0, z), k * 37, 0.9 + 0.15 * (k % 3))
    for k, (x, z) in enumerate([(-0.4, -2.6), (3.2, -1.0), (-3.6, 3.0), (2.4, 3.6), (5.6, 1.0)]):
        I("Lampe%d" % k, "decor/lampe_champignon", (x, 0, z), k * 50, 1.2)
    # habitants
    I("Enfant", "peuple/enfant", (1.3, 0, 1.6), -30)
    I("Ancienne", "peuple/ancienne", (-3.4, 0, -1.2), 40)
    I("Jardiniere", "peuple/jardiniere", (-1.6, 0, 4.4), 160)
    I("Pecheur", "peuple/pecheur", (6.8, 0, 2.6), 90)
    I("Enfant2", "peuple/enfant", (-1.9, 0, 2.2), 120, 0.85)
    # le robot (pour l'échelle), antenne éteinte
    s.instance("Robot", "res://scenes/robot.tscn", transform=xform((3.0, 0, 3.4), (0, -135, 0)))
    # une parole de lumière au-dessus de l'enfant
    font = s.ext_res("FontFile", "res://assets/fonts/Caveat.ttf")
    s.node("Parole", "Label3D", ".", transform=xform((1.3, 2.0, 1.6)), billboard=1, no_depth_test="true",
           font='ExtResource("%s")' % font, font_size=64, pixel_size=0.0035, outline_size=14,
           modulate="Color(0.55, 1, 0.9, 1)", outline_modulate="Color(0.55, 1, 0.9, 0.25)",
           text='"Grand-mère dit qu\'il ne faut pas\nte parler. Tu brûles, Petit-Jour ?"')
    s.node("Camera", "Camera3D", ".", transform=xform((11.5, 11.5, 11.5), (-38, 45, 0)), fov=32.0, current="true")
    s.save("scenes/mockups/ombre_mockup.tscn")


if __name__ == "__main__":
    # les maisons, décors et habitants viennent maintenant de Blender (tools/ombre_godot.py) ;
    # ce script ne fait plus que les matériaux et la maquette du village.
    write_materials()
    mockup()
