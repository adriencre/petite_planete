"""Ancien corps (île 1, crique ouest) — le robot, abandonné depuis longtemps.

On part du robot jouable (assets/models/robot_meshy.glb : même maillage, même texture, donc exactement
la même écharpe et le même nœud) et on
  1. garde sa texture (le retexture Meshy « mousse » essayé le 2026-11-17 perdait l'écharpe : abandonné ;
     la mousse est ajoutée dans Godot par shaders/mousse_ancien.gdshader) ;
  2. le fige dans la dernière pose du clip « effondrement » (celle où le robot tombe quand sa batterie meurt) ;
  3. applique la pose au maillage et retire le squelette : un objet fixe, léger ;
  4. exporte assets/models/ancien_corps.glb et rend une planche (robot neuf / ancien corps).

Lancer :  blender -b --factory-startup --python tools/blender/ancien_corps.py
"""
import bpy, math, os
from mathutils import Vector

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "ancien_corps.blend")
GLB = os.path.join(RACINE, "assets", "models", "ancien_corps.glb")
CAPTURES = os.path.join(RACINE, "captures")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 30
bpy.ops.import_scene.gltf(filepath=ROBOT, bone_heuristic="BLENDER")
arm = next(o for o in sc.objects if o.type == "ARMATURE")
corps = [o for o in sc.objects if o.type == "MESH" and o.parent == arm]
autres = [o for o in sc.objects if o.type == "MESH" and o not in corps]
print("MAILLAGES", [o.name for o in corps], "hors squelette", [o.name for o in autres])

# 2) la pose : fin de « effondrement »
ad = arm.animation_data
for t in ad.nla_tracks:
    t.mute = True
act = bpy.data.actions["effondrement"]
ad.action = act
if hasattr(ad, "action_slot") and len(act.slots):
    ad.action_slot = act.slots[0]
sc.frame_set(int(act.frame_range[1]))
bpy.context.view_layer.update()

# 3) on fige : maillage déformé -> maillage fixe, sans squelette
for o in corps:
    dg = bpy.context.evaluated_depsgraph_get()
    fige = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    mw = o.matrix_world.copy()
    vieux = o.data
    o.modifiers.clear()
    o.parent = None
    o.matrix_world = mw
    o.data = fige
    o.vertex_groups.clear()
    bpy.data.meshes.remove(vieux)
for o in autres:   # l'antenne (pas dans le squelette) : on l'enlève, le corps est éteint
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.objects.remove(arm, do_unlink=True)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
racine = bpy.data.objects.new("AncienCorps", None)
sc.collection.objects.link(racine)
for o in corps:
    o.name = "Corps"
    mw = o.matrix_world.copy()
    o.parent = racine
    o.matrix_world = mw
pts = [o.matrix_world @ Vector(c) for o in corps for c in o.bound_box]
print(f"POSE couchée : {max(p.x for p in pts) - min(p.x for p in pts):.2f} x {max(p.y for p in pts) - min(p.y for p in pts):.2f} m, haut de {max(p.z for p in pts):.2f} m")
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True, export_animations=False)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# 4) planche : un robot neuf debout à côté, pour comparer
avant = set(sc.objects)
bpy.ops.import_scene.gltf(filepath=ROBOT, bone_heuristic="BLENDER")
neuf = next(o for o in sc.objects if o not in avant and o.type == "ARMATURE")
neuf.location = (2.2, 1.2, 0)
bpy.ops.mesh.primitive_plane_add(size=30)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.78, 0.72, 0.6, 1)
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
cible = Vector((0.3, 0.2, 0.4))
a, e = math.radians(-60), math.radians(35)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 5.6
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.render.filepath = os.path.join(CAPTURES, "ancien_corps_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
