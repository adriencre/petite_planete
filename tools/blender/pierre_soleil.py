"""Pierre-soleil (île 1) — découpe du modèle Meshy.

On ne remodélise rien. Le script
  1. importe le .glb de Meshy, le met à l'échelle (HAUTEUR) et le pose sur z = 0,
  2. sépare le `Cristal` (la pièce la plus haute) pour que le jeu le fasse briller,
  3. garde tout le reste dans `Socle` (pierre, griffes de bois, mousse),
  4. exporte assets/models/pierre_soleil_meshy.glb et rend une planche avec le robot.
(L'ancienne assets/models/pierre_soleil.glb, faite à la main, sert encore à scenes/ile_test.tscn.)

Lancer :  blender -b --factory-startup --python tools/blender/pierre_soleil.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "pierre_soleil_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "pierre_soleil.blend")
GLB = os.path.join(RACINE, "assets", "models", "pierre_soleil_meshy.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

HAUTEUR = 1.6   # m, du sol à la pointe du cristal (l'antenne du robot arrive vers 1,9 m)

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
zs = [v.co.z for v in me.vertices]
me.transform(Matrix.Scale(HAUTEUR / (max(zs) - min(zs)), 4) @ Matrix.Translation((0, 0, -min(zs))))
me.update()
MAT = me.materials[0]
MAT.name = "pierre_soleil"

bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.faces.ensure_lookup_table()
pieces, vu = [], set()
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
    pieces.append(grp)
haut = [max(v.co.z for f in g for v in f.verts) for g in pieces]
cristal = max(range(len(pieces)), key=lambda k: haut[k])
print(f"PIECES {len(pieces)} ; cristal = pièce {cristal}, {len(pieces[cristal])} faces, pointe à {haut[cristal]:.2f} m")
bm.faces.index_update()


def extraire(nom, garder):
    idx = {f.index for k in garder for f in pieces[k]}
    b2 = bm.copy()
    b2.faces.ensure_lookup_table()
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.index not in idx], context="FACES")
    for f in b2.faces:
        f.smooth = False
    m = bpy.data.meshes.new(nom)
    b2.to_mesh(m)
    b2.free()
    m.materials.append(MAT)
    o = bpy.data.objects.new(nom, m)
    sc.collection.objects.link(o)
    return o


racine = bpy.data.objects.new("PierreSoleil", None)
racine.empty_display_type = "PLAIN_AXES"
sc.collection.objects.link(racine)
socle = extraire("Socle", [k for k in range(len(pieces)) if k != cristal])
socle.parent = racine
cr = extraire("Cristal", [cristal])
pts = [v.co for v in cr.data.vertices]
centre = Vector((sum(p.x for p in pts), sum(p.y for p in pts), sum(p.z for p in pts))) / len(pts)
cr.data.transform(Matrix.Translation(-centre))
cr.location = centre
cr.parent = racine
print(f"CRISTAL centre à {tuple(round(c, 2) for c in centre)}")
bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ planche avec le robot
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    neufs = [o for o in sc.objects if o not in avant]
    bpy.context.view_layer.update()
    arm = next(o for o in neufs if o.type == "ARMATURE")
    arm.location = (0.0, -0.75, 0.0)
except Exception as e:
    print("ROBOT non importé :", e)
bpy.ops.mesh.primitive_plane_add(size=30)
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
cible = Vector((0, -0.3, 0.9))
a, e = math.radians(-35), math.radians(18)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 5.0
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1000, 900
sc.render.filepath = os.path.join(CAPTURES, "pierre_soleil_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
