"""Atelier des robots (île 1) — la salle creusée dans la falaise, derrière la cascade.

On part de la salle en coupe de Meshy (sol + deux murs, sans plafond) et on
  1. la met à l'échelle (LARGEUR = une case du terrain), sol sur z = 0 ;
  2. la tourne pour que le mur à l'ogive regarde -Y Blender (= +Z Godot, le sud, vers le rebord caché) ;
  3. perce l'ogive (Meshy ne l'a que sculptée) pour en faire un vrai passage ;
  4. ajoute les murs manquants et un couvercle de roche : de dehors, c'est un bloc de falaise plein ;
  5. coupe le tout à HAUTEUR_MURS : `Base` (sol + bas des murs) et `Toit` (haut des murs + couvercle),
     que le jeu efface quand le robot est dedans (comme l'abri) ; repères `Centre` et `Entree` ;
  6. exporte assets/models/atelier_salle.glb et rend une planche (fermée / ouverte, robot pour l'échelle).

Lancer :  blender -b --factory-startup --python tools/blender/atelier_salle.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "atelier_salle_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "atelier_salle.blend")
GLB = os.path.join(RACINE, "assets", "models", "atelier_salle.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

LARGEUR = 6.0          # m : une case du terrain
HAUTEUR_MURS = 1.4     # m au-dessus du sol : ce qui reste quand le haut s'efface
PORTE_LARG = 1.5       # m, passage percé dans l'ogive
PORTE_HAUT = 2.6
EP_MUR = 0.6           # épaisseur des murs ajoutés

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=SOURCE)
src = next(o for o in sc.objects if o.type == "MESH")
for o in list(sc.objects):
    if o is not src:
        bpy.data.objects.remove(o)
src.parent = None
me = src.data
me.transform(src.matrix_world)
src.matrix_world = Matrix.Identity(4)
MAT = me.materials[0]
MAT.name = "atelier_salle"

# ------------------------------------------------------------------ 1-2. échelle, rotation, sol à z = 0
xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
ech = LARGEUR / max(max(xs) - min(xs), max(ys) - min(ys))
cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
# chez Meshy : mur à l'ogive vers -X, mur du fond vers +Y ; on tourne de +90° : ogive vers -Y, fond vers -X
me.transform(Matrix.Rotation(math.pi / 2, 4, "Z") @ Matrix.Scale(ech, 4) @ Matrix.Translation((-cx, -cy, 0)))
me.update()
# le sol : la hauteur la plus fréquente des faces horizontales tournées vers le haut, dans la moitié basse
zs_all = [v.co.z for v in me.vertices]
zmin, zmax = min(zs_all), max(zs_all)
hauteurs = {}
for p in me.polygons:
    if p.normal.z > 0.95 and p.center.z < (zmin + zmax) / 2:
        k = round(p.center.z, 2)
        hauteurs[k] = hauteurs.get(k, 0.0) + p.area
z_sol = max(hauteurs, key=hauteurs.get)
me.transform(Matrix.Translation((0, 0, -z_sol)))
me.update()
zs_all = [v.co.z for v in me.vertices]
Z_HAUT = max(zs_all)
Z_BAS = min(zs_all)
D = LARGEUR / 2
print(f"SALLE {LARGEUR:.1f} m de côté, murs jusqu'à {Z_HAUT:.2f} m, socle jusqu'à {Z_BAS:.2f} m sous le sol")

bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
uv = bm.loops.layers.uv.active


# matériaux des ajouts : roche en strates (comme les falaises du terrain) et mousse du dessus
def mat_uni(nom, hexa):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    c = tuple(int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    c = tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*c, 1)
    bsdf.inputs["Roughness"].default_value = 1.0
    return m


STRATES = [mat_uni("roche_rose", "#E8AFA4"), mat_uni("roche_ocre", "#E8BF8E"), mat_uni("roche_creme", "#F2DEC6"),
           mat_uni("roche_rose_fonce", "#D69790")]
MOUSSE = mat_uni("mousse", "#9DBB68")
MATS = [MAT] + STRATES + [MOUSSE]      # indices : 0 texture Meshy, 1-4 strates, 5 mousse


def boite(bm_, mn, mx, mi):
    v = [bm_.verts.new((x, y, z)) for z in (mn.z, mx.z) for y in (mn.y, mx.y) for x in (mn.x, mx.x)]
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        bm_.faces.new([v[i] for i in f]).material_index = mi


def mur_strates(bm_, mn, mx):
    """Un mur de roche en strates horizontales, comme les falaises du terrain."""
    hs = [0.7, 0.5, 0.9, 0.45, 0.8, 0.6, 0.75, 0.5, 0.9]
    z, i = mn.z, 0
    while z < mx.z - 1e-3:
        h = min(hs[i % len(hs)], mx.z - z)
        boite(bm_, Vector((mn.x, mn.y, z)), Vector((mx.x, mx.y, z + h)), 1 + (i % 4))
        z += h
        i += 1


# ------------------------------------------------------------------ 3. percer l'ogive (mur sud, -Y)
# l'ogive de Meshy n'est que sculptée : on cherche son cadre de bois (pièce haute contre le mur sud)
bm.faces.ensure_lookup_table()
morceaux, vu = [], set()
for f in bm.faces:
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
    morceaux.append(grp)
cadres = []
for grp in morceaux:
    pts = [v.co for f in grp for v in f.verts]
    if max(p.y for p in pts) < -D * 0.4 and max(p.z for p in pts) > 1.2 and (max(p.x for p in pts) - min(p.x for p in pts)) > 0.8:
        cadres.append((max(p.z for p in pts), (min(p.x for p in pts) + max(p.x for p in pts)) / 2))
cx_porte = max(cadres)[1] if cadres else 0.0
x0, x1 = cx_porte - PORTE_LARG / 2, cx_porte + PORTE_LARG / 2
# on trace les bords du passage dans le maillage, puis on retire tout ce qui est dedans (bois compris)
for co, no in (((x0, 0, 0), (1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, 0, PORTE_HAUT), (0, 0, 1)), ((0, -D * 0.4, 0), (0, 1, 0))):
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no)
dans = [f for f in bm.faces if x0 - 1e-4 < f.calc_center_median().x < x1 + 1e-4 and 0.02 < f.calc_center_median().z < PORTE_HAUT
        and f.calc_center_median().y < -D * 0.4]
bmesh.ops.delete(bm, geom=dans, context="FACES")
# épaisseur du mur à cet endroit, pour refermer les côtés du passage
ys = [v.co.y for v in bm.verts if x0 - 0.3 < v.co.x < x1 + 0.3 and 0.3 < v.co.z < PORTE_HAUT - 0.3 and v.co.y < -D * 0.4]
y_ext, y_int = (min(ys), max(ys)) if ys else (-D, -D + 0.6)
ep = 0.05
boite(bm, Vector((x0 - ep, y_ext - 0.02, 0)), Vector((x0, y_int + 0.02, PORTE_HAUT)), 4)      # jambage gauche
boite(bm, Vector((x1, y_ext - 0.02, 0)), Vector((x1 + ep, y_int + 0.02, PORTE_HAUT)), 4)      # jambage droit
boite(bm, Vector((x0 - ep, y_ext - 0.02, PORTE_HAUT)), Vector((x1 + ep, y_int + 0.02, PORTE_HAUT + ep)), 4)  # linteau
print(f"PORTE percée : {len(dans)} faces retirées, x {x0:.2f} -> {x1:.2f}, mur de {y_int - y_ext:.2f} m d'épaisseur")

# ------------------------------------------------------------------ 4. murs manquants (nord, est) + couvercle
mur_strates(bm, Vector((-D, D - EP_MUR, Z_BAS)), Vector((D, D, Z_HAUT)))            # nord (+Y)
mur_strates(bm, Vector((D - EP_MUR, -D, Z_BAS)), Vector((D, D - EP_MUR, Z_HAUT)))   # est (+X)
boite(bm, Vector((-D, -D, Z_HAUT - 0.05)), Vector((D, D, Z_HAUT + 0.35)), 3)        # couvercle (crème)
boite(bm, Vector((-D + 0.25, -D + 0.25, Z_HAUT + 0.35)), Vector((D - 0.25, D - 0.25, Z_HAUT + 0.5)), 5)  # mousse


# ------------------------------------------------------------------ 5. Base / Toit
def vers_objet(b, nom):
    m = bpy.data.meshes.new(nom)
    b.to_mesh(m)
    for mm in MATS:
        m.materials.append(mm)
    for p in m.polygons:
        p.use_smooth = False
    o = bpy.data.objects.new(nom, m)
    sc.collection.objects.link(o)
    return o


def moitie(nom, haut):
    b = bm.copy()
    u = b.loops.layers.uv.active
    bmesh.ops.bisect_plane(b, geom=b.verts[:] + b.edges[:] + b.faces[:], plane_co=(0, 0, HAUTEUR_MURS),
                           plane_no=(0, 0, 1), clear_outer=not haut, clear_inner=haut)
    bords = [e for e in b.edges if e.is_boundary and all(abs(v.co.z - HAUTEUR_MURS) < 1e-4 for v in e.verts)]
    avant = set(b.faces)
    if bords:
        bmesh.ops.holes_fill(b, edges=bords, sides=0)
    for f in b.faces:
        if f not in avant:   # tranche des murs coupés : roche rose foncée
            f.material_index = 4
    o = vers_objet(b, nom)
    print(f"{nom.upper()} : {len(b.faces)} faces")
    b.free()
    return o


SALLE = bpy.data.objects.new("AtelierSalle", None)
sc.collection.objects.link(SALLE)
o_base = moitie("Base", False)
o_toit = moitie("Toit", True)
o_base.parent = o_toit.parent = SALLE
for nom, pos in (("Centre", (0, 0, 0)), ("Entree", (cx_porte, -D, 0))):
    e = bpy.data.objects.new(nom, None)
    e.empty_display_type = "ARROWS"
    e.location = pos
    sc.collection.objects.link(e)
    e.parent = SALLE
bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ 6. planche : fermée (gauche), ouverte (droite)
def copie(dx, avec_toit):
    corr = {}
    for o in [SALLE] + list(SALLE.children_recursive):
        if not avec_toit and o is o_toit:
            continue
        c = o.copy()
        c.hide_render = False
        sc.collection.objects.link(c)
        corr[o] = c
    for o, c in corr.items():
        if o.parent:
            c.parent = corr[o.parent]
    corr[SALLE].location.x = dx


SALLE.hide_render = True
for o in SALLE.children_recursive:
    o.hide_render = True
copie(0.0, True)
copie(8.5, False)
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    arm = next(o for o in sc.objects if o not in avant and o.type == "ARMATURE")
    arm.location = (8.5 + cx_porte, -0.5, 0.0)
except Exception as e:
    print("ROBOT non importé :", e)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01))
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
cible = Vector((4.25, 0, 1.5))
a, e = math.radians(-90), math.radians(42)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 21.0
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.filepath = os.path.join(CAPTURES, "atelier_salle_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
