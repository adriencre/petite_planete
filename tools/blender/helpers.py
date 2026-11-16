import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix, noise

OUT = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5\assets\models"
os.makedirs(OUT, exist_ok=True)
sc = bpy.data.scenes.get("ILE_test") or bpy.data.scenes.new("ILE_test")
bpy.context.window.scene = sc


def clear_scene():
    for o in list(sc.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, hexcol, rough=0.8, emit=None, strength=0.0, double=False):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*srgb(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        b.inputs["Emission Strength"].default_value = strength
    else:
        b.inputs["Emission Strength"].default_value = 0.0
    m.use_backface_culling = not double
    return m


def obj_from_bm(name, bm, m=None, smooth=True, parent=None, mats=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    for mm in (mats or ([m] if m else [])):
        me.materials.append(mm)
    if parent:
        o.parent = parent
    return o


def empty(name):
    o = bpy.data.objects.new(name, None)
    sc.collection.objects.link(o)
    return o


def tube(name, pts, radii, m, parent=None, ring=10, cap=True):
    bm = bmesh.new()
    prev = None
    first = last = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = t.orthogonal().normalized()
        b = t.cross(a)
        row = [bm.verts.new(p + radii[i] * (math.cos(2 * math.pi * j / ring) * a + math.sin(2 * math.pi * j / ring) * b)) for j in range(ring)]
        if prev:
            for j in range(ring):
                bm.faces.new((prev[j], prev[(j + 1) % ring], row[(j + 1) % ring], row[j]))
        else:
            first = row
        prev = row
    last = prev
    if cap:
        bm.faces.new(list(reversed(first)))
        bm.faces.new(last)
    return obj_from_bm(name, bm, m, parent=parent)


def bez(p0, p1, p2, n=16):
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in [i / n for i in range(n + 1)]]


def taper(n, r0, r1):
    return [r0 + (r1 - r0) * i / n for i in range(n + 1)]


def blob(name, center, radius, m, parent=None, squash=(1, 1, 1), seed=0, rough=0.25, sub=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=radius)
    off = Vector((seed * 1.3, seed * 2.1, seed * 0.7))
    for v in bm.verts:
        n = noise.noise(v.co * (2.0 / max(radius, 0.01)) + off)
        v.co = v.co * (1 + rough * n)
        v.co = Vector((v.co.x * squash[0], v.co.y * squash[1], v.co.z * squash[2])) + Vector(center)
    return obj_from_bm(name, bm, m, parent=parent)


def lathe(name, profile, m, seg=48, parent=None, keep=None):
    """profile: list of (z, r). keep(theta, z, r) -> bool to keep a face (by its center)."""
    bm = bmesh.new()
    rows = []
    for z, r in profile:
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * j / seg), r * math.sin(2 * math.pi * j / seg), z)) for j in range(seg)])
    for k in range(len(rows) - 1):
        zc = (profile[k][0] + profile[k + 1][0]) / 2
        rc = (profile[k][1] + profile[k + 1][1]) / 2
        for j in range(seg):
            th = 2 * math.pi * (j + 0.5) / seg
            if keep and not keep(th, zc, rc):
                continue
            bm.faces.new((rows[k][j], rows[k][(j + 1) % seg], rows[k + 1][(j + 1) % seg], rows[k + 1][j]))
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    return obj_from_bm(name, bm, m, parent=parent)


def smooth_profile(pts, n=60):
    """Catmull-Rom through (z, r) control points."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = [Vector(x) for x in P[i - 1:i + 3]]
        steps = max(2, n // (len(pts) - 1))
        for s in range(steps):
            t = s / steps
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append((q.x, q.y))
    out.append(pts[-1])
    return out


def export(root, fname):
    bpy.ops.object.select_all(action="DESELECT")
    for o in [root] + list(root.children_recursive):
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, fname), export_format="GLB",
                              use_selection=True, use_active_scene=True, export_apply=True)


# --------- palette ----------
M_nacre = mat("nacre", "#f4e3df", 0.35, double=True)
M_bois = mat("semeur_bois", "#ead5c0", 0.8)
M_cote = mat("semeur_cote", "#d9bca7", 0.85)
M_or = mat("or_lumiere", "#fff0c8", 0.3, emit="#ffc463", strength=7.0)
M_eteint = mat("lumiere_eteinte", "#e8e4ee", 0.15)
M_mousse = mat("mousse", "#86b86c", 1.0)
M_mousse2 = mat("mousse_claire", "#b5cf72", 1.0)
M_tronc = mat("tronc", "#b98d84", 0.9)
M_feuil_rose = mat("feuillage_rose", "#f3a9bb", 0.9)
M_feuil_vert = mat("feuillage_vert", "#9ccc6c", 0.9)
M_pierre = mat("pierre_claire", "#e9d2c6", 0.9)
M_tige = mat("tige", "#8fbd63", 0.9)
M_bouton_or = mat("bouton_or", "#ffd98a", 0.4, emit="#ffbf55", strength=1.5)
M_fleur_rose = mat("fleur_rose", "#ff8fb1", 0.8)
M_fleur_blanche = mat("fleur_blanche", "#fff6f0", 0.8)
