# Boîte à outils Blender pour le monde de l'ombre (chargée par exec() depuis le MCP Blender).
# Chaque objet du kit vit dans sa propre collection ; export() en fait un .glb pour Godot.
import bpy, bmesh, math, os, json

PROJ = r"C:\Users\adrie\OneDrive\Bureau\petite-planete"

MATS = {
    "bois_nuit": ((0.24, 0.18, 0.27), 0.0), "ecorce": ((0.2, 0.15, 0.2), 0.0),
    "toit_mousse": ((0.13, 0.27, 0.27), 0.0), "champi_pied": ((0.7, 0.66, 0.72), 0.0),
    "champi_chapeau": ((0.14, 0.34, 0.42), 0.0), "champi_chapeau_violet": ((0.3, 0.2, 0.42), 0.0),
    "champi_chapeau_ambre": ((0.5, 0.3, 0.2), 0.0),
    "coquille": ((0.66, 0.54, 0.66), 0.0), "coquille_raie": ((0.45, 0.35, 0.52), 0.0),
    "pierre_nuit": ((0.24, 0.25, 0.36), 0.0), "mousse": ((0.14, 0.24, 0.25), 0.0),
    "mousse_claire": ((0.17, 0.3, 0.3), 0.0), "fougere": ((0.2, 0.42, 0.38), 0.25),
    "tissu_rouille": ((0.55, 0.3, 0.27), 0.0), "tissu_mousse": ((0.27, 0.38, 0.32), 0.0),
    "tissu_sable": ((0.62, 0.56, 0.46), 0.0), "tissu_prune": ((0.38, 0.24, 0.4), 0.0),
    "tissu_ocre": ((0.66, 0.5, 0.26), 0.0), "tissu_nuit": ((0.16, 0.2, 0.32), 0.0),
    "peau_ombre": ((0.3, 0.33, 0.56), 0.0), "corde": ((0.5, 0.45, 0.4), 0.0),
    "lueur": ((0.45, 1.0, 0.86), 2.2), "lueur_douce": ((0.4, 0.85, 0.8), 0.9),
    "lueur_ambre": ((1.0, 0.78, 0.48), 1.8), "lueur_violette": ((0.75, 0.6, 1.0), 1.6),
    "lueur_rose": ((1.0, 0.6, 0.78), 1.4),
    "fenetre": ((0.55, 1.0, 0.88), 2.6), "fenetre_ambre": ((1.0, 0.8, 0.5), 2.2),
    "oeil": ((0.62, 1.0, 0.92), 0.9), "joue": ((1.0, 0.6, 0.78), 0.7), "reflet": ((1.0, 1.0, 1.0), 3.0),
}


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    c, e = MATS[name]
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    lin = tuple(x ** 2.2 for x in c)
    b.inputs["Base Color"].default_value = (*lin, 1)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Emission Color"].default_value = (*lin, 1)
    b.inputs["Emission Strength"].default_value = e
    return m


class Kit:
    """Construit un objet du kit dans sa collection, sous une racine (empty) du même nom."""

    def __init__(self, name):
        self.name = name
        for c in bpy.context.view_layer.layer_collection.children:
            c.hide_viewport = True
        col = bpy.data.collections.get(name)
        if col is None:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        self.col = col
        lc = bpy.context.view_layer.layer_collection.children[name]
        lc.hide_viewport = False
        bpy.context.view_layer.active_layer_collection = lc
        self.root = self.empty(name, (0, 0, 0), None)
        self.n = 0

    # ---- hiérarchie
    def empty(self, name, loc, parent="root"):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.1
        self.col.objects.link(e)
        e.location = loc
        bpy.context.view_layer.update()
        p = self.root if parent == "root" else parent
        if p is not None:
            self._parent(e, p)
        return e

    def _parent(self, o, p):
        bpy.context.view_layer.update()
        mw = o.matrix_world.copy()
        o.parent = p
        o.matrix_world = mw

    def _finish(self, o, name, m, parent):
        self.n += 1
        o.name = name or ("P%d" % self.n)
        if o.data:
            o.data.name = o.name
            o.data.materials.clear()
            o.data.materials.append(mat(m))
            for p in o.data.polygons:
                p.use_smooth = False
        self._parent(o, parent or self.root)
        return o

    # ---- formes
    def prim(self, kind, m, loc, rot=(0, 0, 0), scale=(1, 1, 1), name=None, parent=None, **kw):
        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)
        getattr(bpy.ops.mesh, "primitive_%s_add" % kind)(location=loc, rotation=tuple(math.radians(a) for a in rot), **kw)
        o = bpy.context.object
        o.scale = scale
        return self._finish(o, name, m, parent)

    def box(self, m, loc, size, rot=(0, 0, 0), **k):
        return self.prim("cube", m, loc, rot, (size[0] / 2, size[1] / 2, size[2] / 2), size=2, **k)

    def cyl(self, m, loc, r, h, rot=(0, 0, 0), v=8, scale=None, **k):
        return self.prim("cylinder", m, loc, rot, scale or (r, r, h / 2), vertices=v, radius=1, depth=2, **k)

    def cone(self, m, loc, r1, r2, h, rot=(0, 0, 0), v=8, **k):
        return self.prim("cone", m, loc, rot, 1, vertices=v, radius1=r1, radius2=r2, depth=h, **k)

    def ball(self, m, loc, r, scale=(1, 1, 1), seg=8, rings=5, rot=(0, 0, 0), **k):
        return self.prim("uv_sphere", m, loc, rot, (r * scale[0], r * scale[1], r * scale[2]), segments=seg, ring_count=rings, radius=1, **k)

    def ico(self, m, loc, r, scale=(1, 1, 1), sub=1, rot=(0, 0, 0), **k):
        return self.prim("ico_sphere", m, loc, rot, (r * scale[0], r * scale[1], r * scale[2]), subdivisions=sub, radius=1, **k)

    def ring(self, m, loc, R, r, rot=(0, 0, 0), M=12, mm=4, **k):
        return self.prim("torus", m, loc, rot, 1, major_radius=R, minor_radius=r, major_segments=M, minor_segments=mm, **k)

    def lathe(self, m, prof, seg=12, loc=(0, 0, 0), name=None, parent=None, cap=False, twist=0.0, wobble=0.0, seed=1):
        """profil [(rayon, z)] tourné autour de z ; rayon 0 = pointe ; wobble = irrégularité"""
        import random
        rnd = random.Random(seed)
        bm = bmesh.new()
        rings = []
        for k, (r, z) in enumerate(prof):
            if r <= 1e-4:
                rings.append([bm.verts.new((0, 0, z))])
                continue
            ring = []
            for i in range(seg):
                a = 2 * math.pi * i / seg + twist * k
                rr = r * (1 + wobble * (rnd.random() - 0.5))
                ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            if len(a) == 1 and len(b) > 1:
                for i in range(seg):
                    bm.faces.new((a[0], b[(i + 1) % seg], b[i]))
            elif len(b) == 1 and len(a) > 1:
                for i in range(seg):
                    bm.faces.new((a[i], a[(i + 1) % seg], b[0]))
            elif len(a) > 1:
                for i in range(seg):
                    bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
        if cap and len(rings[0]) > 1:
            bm.faces.new(list(reversed(rings[0])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        self.n += 1
        nm = name or ("L%d" % self.n)
        me = bpy.data.meshes.new(nm)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(nm, me)
        self.col.objects.link(o)
        o.location = loc
        return self._finish(o, nm, m, parent)

    def stick(self, m, a, b, r, v=5, **k):
        """un bâton (cylindre) qui va du point a au point b"""
        from mathutils import Vector
        a, b = Vector(a), Vector(b)
        d = b - a
        o = self.cyl(m, tuple((a + b) / 2), r, d.length, v=v, **k)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
        return o

    # ---- petits éléments
    @staticmethod
    def around(r, ang, z):
        """point à l'angle `ang` (0° = devant, -y) sur un cercle de rayon r"""
        a = math.radians(ang - 90)
        return (r * math.cos(a), r * math.sin(a), z)

    def window(self, ang, z, r_wall, r=0.16, glass="fenetre", frame="ecorce", cross=True):
        p = self.around(r_wall, ang, z)
        rot = (90, 0, ang)
        self.cyl(glass, p, r, 0.06, rot=rot, v=10)
        self.ring(frame, p, r + 0.02, 0.035, rot=rot, M=14)
        if cross:
            self.box(frame, p, (2 * r, 0.025, 0.06), rot=(90, 0, ang))
            self.box(frame, p, (2 * r, 0.025, 0.06), rot=(90, 90, ang))

    def door(self, ang, r_wall, w=0.46, h=0.7, z0=0.12):
        p = self.around(r_wall + 0.05, ang, 0)
        a = math.radians(ang)
        tx, ty = math.cos(a), math.sin(a)   # tangente (gauche-droite de la porte)
        nx, ny = math.sin(a), -math.cos(a)  # normale vers l'extérieur
        self.box("ecorce", (p[0] - nx * 0.04, p[1] - ny * 0.04, z0 + h / 2), (w * 0.95, 0.06, h), rot=(0, 0, ang))
        for k in (-1, 0, 1):
            self.box("bois_nuit", (p[0] + tx * k * w / 3.2, p[1] + ty * k * w / 3.2, z0 + (h - w / 2) / 2 + 0.02),
                     (w / 3.2, 0.05, h - w / 2), rot=(0, 0, ang))
        self.cyl("bois_nuit", (p[0], p[1], z0 + h - w / 2), w / 2, 0.05, rot=(90, 0, ang), v=12)
        self.ring("ecorce", (p[0] + nx * 0.02, p[1] + ny * 0.02, z0 + h - w / 2), w / 2 + 0.02, 0.035, rot=(90, 0, ang), M=16)
        for s in (-1, 1):
            self.box("ecorce", (p[0] + tx * s * (w / 2 + 0.02) + nx * 0.02, p[1] + ty * s * (w / 2 + 0.02) + ny * 0.02, z0 + (h - w / 2) / 2),
                     (0.06, 0.06, h - w / 2), rot=(0, 0, ang))
        self.ball("lueur_ambre", (p[0] + tx * w * 0.3 + nx * 0.05, p[1] + ty * w * 0.3 + ny * 0.05, z0 + h * 0.42), 0.03, seg=6, rings=4)

    def lantern(self, loc, mat_glow="lueur_ambre", arm=0.25, ang=0):
        a = math.radians(ang)
        self.box("bois_nuit", (loc[0] - math.cos(a) * arm / 2, loc[1] - math.sin(a) * arm / 2, loc[2] + 0.22), (arm, 0.04, 0.04), rot=(0, 0, ang))
        self.box("bois_nuit", (loc[0], loc[1], loc[2] + 0.13), (0.015, 0.015, 0.16))
        self.ico(mat_glow, loc, 0.08, (1, 1, 1.35))
        self.cyl("bois_nuit", (loc[0], loc[1], loc[2] + 0.11), 0.08, 0.04, v=6)

    def mini_mushrooms(self, pts, base_z=0.0):
        for k, (x, y, h, s) in enumerate(pts):
            self.cyl("champi_pied", (x, y, base_z + h / 2), s * 0.35, h, v=6)
            self.ball(["lueur", "lueur_violette", "lueur_rose"][k % 3], (x, y, base_z + h), s, (1, 1, 0.6), seg=7, rings=4)


def export(name, sub):
    """exporte la collection `name` en assets/ombre/<sub>/<fichier>_modele.glb"""
    col = bpy.data.collections[name]
    bpy.ops.object.select_all(action="DESELECT")
    for c in bpy.context.view_layer.layer_collection.children:
        c.hide_viewport = c.name != name
    for o in col.objects:
        o.hide_set(False)
        o.select_set(True)
    fname = "".join("_" + ch.lower() if ch.isupper() and i else ch.lower() for i, ch in enumerate(name))
    d = os.path.join(PROJ, "assets", "ombre", sub)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, fname + "_modele.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_animations=False)
    return out


def pivots(name):
    """positions locales (Godot, y-up) des pivots d'un habitant, pour ses animations"""
    out = {}
    for n in ("Corps", "Tete", "BrasG", "BrasD", "PiedG", "PiedD", "Pousse"):
        o = bpy.data.objects.get(n + "_" + name)
        if o is None:
            continue
        x, y, z = o.location
        out[n] = (round(x, 4), round(z, 4), round(-y, 4))
    return out
