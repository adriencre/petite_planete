"""Prépare un objet Meshy simple (sans pièce mobile) pour le jeu : échelle, posé au sol, centré, avant
vers -Y Blender (= +Z Godot), export dans assets/models/ et planche à côté du robot.

Lancer :  blender -b --factory-startup --python tools/blender/accessoire.py -- <source.glb> <nom> <hauteur_m> [rotation_deg]
  ex.  ... -- tools/blender/sources/meshy/moule_meshy.glb moule 2.6
  rotation_deg : tourne l'objet (autour de la verticale) si Meshy ne l'a pas fait face à l'avant.
"""
import bpy, math, os, sys
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
args = sys.argv[sys.argv.index("--") + 1:]
SOURCE = os.path.join(RACINE, args[0]) if not os.path.isabs(args[0]) else args[0]
NOM = args[1]
HAUTEUR = float(args[2])
ROT = math.radians(float(args[3])) if len(args) > 3 else 0.0
GLB = os.path.join(RACINE, "assets", "models", NOM + ".glb")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

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
xs, ys, zs = ([v.co[i] for v in me.vertices] for i in range(3))
me.transform(Matrix.Rotation(ROT, 4, "Z") @ Matrix.Scale(HAUTEUR / (max(zs) - min(zs)), 4)
             @ Matrix.Translation((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs))))
me.update()
for p in me.polygons:
    p.use_smooth = False
me.materials[0].name = NOM
src.name = NOM.capitalize()
xs, ys = [v.co.x for v in me.vertices], [v.co.y for v in me.vertices]
print(f"{NOM.upper()} : {max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f} x {HAUTEUR:.2f} m")
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# planche : l'objet et le robot (1,90 m) à côté
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    arm = next(o for o in sc.objects if o not in avant and o.type == "ARMATURE")
    arm.location = (max(xs) + 0.7, -0.4, 0)
except Exception as e:
    print("ROBOT non importé :", e)
bpy.ops.mesh.primitive_plane_add(size=30)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.8, 0.74, 0.62, 1)
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
cible = Vector((max(xs) * 0.5, 0, HAUTEUR * 0.45))
a, e = math.radians(-70), math.radians(25)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * (HAUTEUR * 2.6 + 3.0)
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1100, 900
sc.render.filepath = os.path.join(RACINE, "captures", NOM + "_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
