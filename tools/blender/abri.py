"""Abri (île 1) — découpe du modèle Meshy pour la vue de dessus.

On ne remodélise rien : la forme et la texture de Meshy sont gardées. Le script
  1. importe le .glb de Meshy (un maillage, pièces non soudées : coque creuse, côtes, cadre, sol...),
  2. le met à l'échelle (HAUTEUR, socle posé sur z = 0, porte vers -Y Blender = +Z Godot),
  3. le coupe à HAUTEUR_MURS au-dessus du sol intérieur : `Base` (socle, sol, murs bas) et `Toit`
     (tout le haut, que le jeu efface quand le robot est dedans),
  4. jette la peau intérieure de la coque (anguleuse chez Meshy), épaissit la peau extérieure
     pour des murs ronds, et bouche les côtes coupées,
  5. détache la `Veilleuse` (enfant du toit) et pose les repères `Porte` et `Centre`,
  6. enregistre un .blend, exporte assets/models/abri.glb et rend une planche de test.

Lancer (Blender à part, sans toucher à la session ouverte) :
  blender -b --factory-startup --python tools/blender/abri.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "abri_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "abri.blend")
GLB = os.path.join(RACINE, "assets", "models", "abri.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

HAUTEUR = 5.2          # m, du bas du socle à la pointe (le robot fait ~1,90 m)
HAUTEUR_MURS = 1.1     # m au-dessus du sol intérieur : ce qui reste quand le toit s'efface
EPAISSEUR = 0.16       # m, épaisseur des murs (la peau intérieure de Meshy, anguleuse, est jetée)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = "Abri"

# ------------------------------------------------------------------ 1. import + échelle
bpy.ops.import_scene.gltf(filepath=SOURCE)
src = next(o for o in sc.objects if o.type == "MESH")
for o in list(sc.objects):
    if o is not src:
        bpy.data.objects.remove(o)
src.parent = None
me = src.data
me.transform(src.matrix_world)
src.matrix_world = Matrix.Identity(4)
zs = [v.co.z for v in me.vertices]
ech = HAUTEUR / (max(zs) - min(zs))
me.transform(Matrix.Scale(ech, 4) @ Matrix.Translation((0, 0, -min(zs))))
me.update()
MAT = me.materials[0]
MAT.name = "abri"
MAT.use_backface_culling = False

# ------------------------------------------------------------------ 2. pièces (composantes soudées)
maitre = bmesh.new()
maitre.from_mesh(me)
bmesh.ops.remove_doubles(maitre, verts=maitre.verts, dist=1e-5)
COMP = maitre.faces.layers.int.new("piece")
maitre.faces.ensure_lookup_table()
pieces, vu = [], set()
for f in maitre.faces:
    if f.index in vu:
        continue
    pile, grp = [f], []
    vu.add(f.index)
    while pile:
        g = pile.pop()
        grp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in vu:
                    vu.add(h.index)
                    pile.append(h)
    pieces.append(grp)


def boite(faces):
    pts = [v.co for f in faces for v in f.verts]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


fermee, infos = {}, {}
for k, grp in enumerate(pieces):
    for f in grp:
        f[COMP] = k
    fermee[k] = not any(e.is_boundary for f in grp for e in f.edges)
    infos[k] = boite(grp)


def uv_creme():
    """Un point de la texture bien crème (le plus clair de la coque), pour colorer la tranche des murs."""
    import numpy as np
    img = next(n.image for n in MAT.node_tree.nodes if n.type == "TEX_IMAGE" and n.image)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    uvl = maitre.loops.layers.uv.active
    meilleur, score = None, -1.0
    for f in pieces[COQUE][::3]:
        u = sum((l[uvl].uv for l in f.loops), Vector((0, 0))) / len(f.loops)
        r, g, b, _ = px[min(h - 1, int(u.y % 1 * h)), min(w - 1, int(u.x % 1 * w))]
        if min(r, g, b) > score:
            meilleur, score = u.copy(), min(r, g, b)
    return meilleur


# la coque : la plus grosse pièce ouverte (son seul bord est le trou de la porte)
COQUE = max((k for k in infos if not fermee[k]), key=lambda k: len(pieces[k]))
UV_CREME = uv_creme()
# le cadre de la porte : pièce fermée, haute et étroite, tout devant
def est_cadre(k):
    mn, mx = infos[k]
    return (fermee[k] and mx.z - mn.z > 0.25 * HAUTEUR and mx.x - mn.x < 0.45 * (infos[COQUE][1].x - infos[COQUE][0].x)
            and abs(mn.x + mx.x) < 0.5 and (mn.y + mx.y) / 2 < infos[COQUE][0].y * 0.6)


CADRE = min((k for k in infos if est_cadre(k)), key=lambda k: infos[k][0].y)
porte_y = infos[CADRE][0].y
porte_haut = infos[CADRE][1].z
# le sol intérieur : la plus grande dalle fermée, plate, au-dessus du socle
plates = [k for k in infos if fermee[k] and infos[k][1].z - infos[k][0].z < 0.05 * HAUTEUR
          and infos[k][1].x - infos[k][0].x > 0.5 * (infos[COQUE][1].x - infos[COQUE][0].x)]
SOL = max(plates, key=lambda k: infos[k][1].z)
Z_SOL = infos[SOL][1].z
Z_COUPE = Z_SOL + HAUTEUR_MURS
# la veilleuse : petites pièces devant la coque, au-dessus de la porte, sans la toucher
VEILLEUSE = [k for k in infos if fermee[k] and k != CADRE and infos[k][1].y < infos[CADRE][1].y
             and infos[k][0].z > porte_haut and abs(infos[k][0].x + infos[k][1].x) < 0.4
             and max(infos[k][1] - infos[k][0]) < 0.8]
# largeur libre de la porte : l'écart entre les deux montants du cadre, à 0,5 m du sol
xs = []
for f in pieces[CADRE]:
    for e in f.edges:
        a_, b_ = e.verts[0].co, e.verts[1].co
        if (a_.z - Z_SOL - 0.5) * (b_.z - Z_SOL - 0.5) < 0:
            xs.append(a_.lerp(b_, (Z_SOL + 0.5 - a_.z) / (b_.z - a_.z)).x)
porte_x0, porte_x1 = max(x for x in xs if x < 0), min(x for x in xs if x > 0)
mn, mx = infos[COQUE]
print(f"PIECES {len(pieces)} ; coque = {len(pieces[COQUE])} faces ; veilleuse = {len(VEILLEUSE)} pièces")
print(f"TAILLE coque {mx.x - mn.x:.2f} x {mx.y - mn.y:.2f} m, hauteur totale {HAUTEUR:.2f} m")
print(f"PORTE {porte_x1 - porte_x0:.2f} m de large entre les montants, cadre haut de {porte_haut - Z_SOL:.2f} m (sol intérieur à z = {Z_SOL:.2f})")
print(f"COUPE à z = {Z_COUPE:.2f} m")
assert VEILLEUSE, "veilleuse introuvable : le modèle source a changé ?"


def vers_dehors(f):
    """Vrai si la face regarde vers l'extérieur de l'abri (et pas vers la pièce)."""
    c = f.calc_center_median()
    return f.normal.dot(c - AXE) > 0.15 * (c - AXE).length


mnC, mxC = infos[COQUE]
AXE = Vector(((mnC.x + mxC.x) / 2, (mnC.y + mxC.y) / 2, Z_SOL))
maitre.normal_update()
dedans = [f for f in pieces[COQUE] if not vers_dehors(f)]
print(f"COQUE : {len(pieces[COQUE]) - len(dedans)} faces dehors gardées, {len(dedans)} faces dedans jetées")
bmesh.ops.delete(maitre, geom=dedans, context="FACES")
# il reste parfois des éclats de la peau intérieure : on ne garde que le plus grand morceau de coque
reste = [f for f in maitre.faces if f[COMP] == COQUE]
vus, iles = set(), []
for f in reste:
    if f in vus:
        continue
    pile, ile = [f], []
    vus.add(f)
    while pile:
        g = pile.pop()
        ile.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h not in vus and h[COMP] == COQUE:
                    vus.add(h)
                    pile.append(h)
    iles.append(ile)
iles.sort(key=len, reverse=True)
print("COQUE : morceaux restants", [len(i) for i in iles])
bmesh.ops.delete(maitre, geom=[f for ile in iles[1:] for f in ile], context="FACES")


# ------------------------------------------------------------------ 3. découpe
def vers_objet(bm, nom):
    m = bpy.data.meshes.new(nom)
    bm.to_mesh(m)
    m.materials.append(MAT)
    o = bpy.data.objects.new(nom, m)
    sc.collection.objects.link(o)
    return o


def boucher(bm, comp, uv):
    """Bouche les pièces fermées coupées par le plan (côtes, cadre) ; la coque reste ouverte."""
    aretes = [e for e in bm.edges if e.is_boundary and fermee[e.link_faces[0][comp]]
              and all(abs(v.co.z - Z_COUPE) < 1e-4 for v in e.verts)]
    if not aretes:
        return 0
    avant = set(bm.faces)
    bmesh.ops.holes_fill(bm, edges=aretes, sides=0)
    neuves = [f for f in bm.faces if f not in avant]
    for f in neuves:   # une seule couleur par bouchon : celle de la pièce, prise sur un voisin
        voisin = next(x for l in f.loops for x in l.vert.link_loops if x.face in avant)
        f[comp] = voisin.face[comp]
        for l in f.loops:
            l[uv] = voisin[uv]
    return len(neuves)


def epaissir(bm, comp, uv):
    """Sort la peau extérieure de la coque, lui donne une épaisseur régulière vers l'intérieur
    (murs ronds, tranche fermée) et la remet. Les faces ajoutées sont crème."""
    peau = bm.copy()
    c2 = peau.faces.layers.int["piece"]
    bmesh.ops.delete(peau, geom=[f for f in peau.faces if f[c2] != COQUE], context="FACES")
    o = vers_objet(peau, "_coque")
    peau.free()
    md = o.modifiers.new("epaisseur", "SOLIDIFY")
    md.thickness, md.offset, md.use_rim, md.use_even_offset = EPAISSEUR, -1.0, True, False
    bpy.context.view_layer.update()
    m2 = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[comp] == COQUE], context="FACES")
    avant = set(bm.faces)
    bm.from_mesh(m2)
    n = 0
    for f in bm.faces:
        if f in avant:
            continue
        f[comp] = COQUE
        if not vers_dehors(f):   # peau intérieure et tranche : crème uni
            n += 1
            for l in f.loops:
                l[uv].uv = UV_CREME
    vieux = o.data
    bpy.data.objects.remove(o)
    bpy.data.meshes.remove(vieux)
    bpy.data.meshes.remove(m2)
    return n


def moitie(nom, haut):
    bm = maitre.copy()
    comp = bm.faces.layers.int["piece"]
    uv = bm.loops.layers.uv.active
    if haut:   # la veilleuse devient un objet à part
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[comp] in VEILLEUSE], context="FACES")
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, Z_COUPE),
                           plane_no=(0, 0, 1), clear_outer=not haut, clear_inner=haut)
    n = boucher(bm, comp, uv)
    t = epaissir(bm, comp, uv)
    for f in bm.faces:
        f.smooth = False
    o = vers_objet(bm, nom)
    print(f"{nom.upper()} : {len(bm.faces)} faces ({n} bouchons, {t} faces de mur intérieur)")
    bm.free()
    return o


def vide(nom, pos, taille=0.3, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille
    o.location = pos
    sc.collection.objects.link(o)
    return o


ABRI = vide("Abri", (0, 0, 0), 0.6, "PLAIN_AXES")
o_base = moitie("Base", False)
o_toit = moitie("Toit", True)
o_base.parent = o_toit.parent = ABRI

bm = maitre.copy()
comp = bm.faces.layers.int["piece"]
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[comp] not in VEILLEUSE], context="FACES")
pts = [v.co for v in bm.verts]
centre_v = Vector((sum(p.x for p in pts), sum(p.y for p in pts), sum(p.z for p in pts))) / len(pts)
bmesh.ops.translate(bm, verts=bm.verts, vec=-centre_v)
o_veil = vers_objet(bm, "Veilleuse")
bm.free()
o_veil.location = centre_v
o_veil.parent = o_toit
print(f"VEILLEUSE à {tuple(round(c, 2) for c in centre_v)}")

mnS, mxS = infos[SOL]
p_porte = vide("Porte", ((porte_x0 + porte_x1) / 2, porte_y, Z_SOL))
p_centre = vide("Centre", ((mnS.x + mxS.x) / 2, (mnS.y + mxS.y) / 2, Z_SOL))
p_porte.parent = p_centre.parent = ABRI
print(f"SOL intérieur {mxS.x - mnS.x:.2f} x {mxS.y - mnS.y:.2f} m ; centre {tuple(round(c, 2) for c in p_centre.location)}")

maitre.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)

# ------------------------------------------------------------------ 4. .blend + .glb
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")


# ------------------------------------------------------------------ 5. planche de test
def copie(dx, avec_toit):
    corr = {}
    for o in [ABRI] + list(ABRI.children_recursive):
        if not avec_toit and (o is o_toit or o is o_veil):
            continue
        c = o.copy()
        sc.collection.objects.link(c)
        corr[o] = c
    for o, c in corr.items():
        if o.parent:
            c.parent = corr[o.parent]
    corr[ABRI].location.x = dx
    return corr


def robot(pos, rot_z=0.0):
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    neufs = [o for o in sc.objects if o not in avant]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in neufs if o.type == "MESH" for c in o.bound_box]
    zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
    xm = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    ym = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    piv = vide("robot_echelle", (0, 0, 0), 0.2, "PLAIN_AXES")
    for o in neufs:
        if o.parent is None:
            o.parent = piv
    k = 1.9 / (zmax - zmin)
    piv.matrix_world = (Matrix.Translation(pos) @ Matrix.Rotation(rot_z, 4, "Z") @ Matrix.Scale(k, 4)
                        @ Matrix.Translation((-xm, -ym, -zmin)))
    return piv


ECART = 9.0
ABRI.hide_render = True
for o in ABRI.children_recursive:
    o.hide_render = True
ferme = copie(0.0, True)
ouvert = copie(ECART, False)
for c in list(ferme.values()) + list(ouvert.values()):
    c.hide_render = False
try:
    robot((p_porte.location.x, p_porte.location.y - 1.6, 0.0))                                # devant la porte
    robot((ECART + p_centre.location.x + 0.9, p_centre.location.y - 0.3, Z_SOL), math.radians(30))   # dedans
except Exception as e:
    print("ROBOT non importé :", e)

bpy.ops.mesh.primitive_plane_add(size=80)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.5, 0.62, 0.36, 1)
sol.data.materials.append(ms)
soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.0
soleil.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.collection.objects.link(soleil)
monde = bpy.data.worlds.new("monde")
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.68, 0.78, 1)
monde.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.world = monde
cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
sc.collection.objects.link(cam)
sc.camera = cam
for moteur in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
    try:
        sc.render.engine = moteur
        break
    except TypeError:
        continue
sc.view_settings.view_transform = "Standard"


def photo(nom, cible, dist, azimut, elevation, taille, focale=50):
    cam.data.lens = focale
    a, e = math.radians(azimut), math.radians(elevation)
    cible = Vector(cible)
    cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = taille
    sc.render.filepath = os.path.join(CAPTURES, nom)
    bpy.ops.render.render(write_still=True)
    print("RENDU", sc.render.filepath)


photo("abri_planche.png", (ECART / 2, 0, 1.8), 30.0, -80, 28, (2000, 1000), 60)
photo("abri_ferme.png", (0, -0.5, 2.2), 17.0, -65, 14, (1200, 1000), 50)
photo("abri_ouvert_dessus.png", (ECART, 0, 0.5), 17.0, -90, 58, (1200, 1000), 50)
