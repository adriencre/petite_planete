"""Aube au coin noir (île 3) : le modèle Meshy (concept/ile_03/aube_squelette_concept.png, image → 3D
meshy-t2 + texture meshy-n1, 2026-11-22) mis à l'échelle, posé au sol et exporté pour Godot.

Décidé le 2026-11-22 : la statue de mousse passait pour une enfant vivante. Aube est un petit squelette
de Semeur assis, genoux serrés, la tête en cage où pousse une fleur corail, un nœud corail, de la mousse,
et sa lanterne éteinte sous un tissu saumon. Hauteur assise, cage comprise : ~1,15 m (une enfant de
Semeurs ; les adultes font 2,5 à 3 m). L'ancienne version : tools/blender/sources/meshy/aube/aube_meshy.glb.

Lancer :  blender -b --factory-startup --python tools/blender/aube_coin_noir.py
"""
from pathlib import Path

import bpy
from mathutils import Vector

RACINE = Path(__file__).resolve().parents[2]
SOURCE = RACINE / "tools/blender/sources/meshy/aube/aube_squelette_meshy.glb"
SORTIE = RACINE / "assets/models/ile03/aube_coin_noir.glb"
APERCU = RACINE / "concept/ile_03/aube_coin_noir.png"
HAUTEUR = 1.15

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
objets = [o for o in bpy.context.scene.objects if o.type == "MESH"]
racine = bpy.data.objects.new("Aube", None)
bpy.context.collection.objects.link(racine)
for o in objets:
    if o.parent is None:
        o.parent = racine
bpy.context.view_layer.update()

coins = [o.matrix_world @ Vector(c) for o in objets for c in o.bound_box]
bas = Vector((min(c.x for c in coins), min(c.y for c in coins), min(c.z for c in coins)))
haut = Vector((max(c.x for c in coins), max(c.y for c in coins), max(c.z for c in coins)))
k = HAUTEUR / (haut.z - bas.z)
centre = (bas + haut) / 2
racine.scale = (k, k, k)
racine.location = (-centre.x * k, -centre.y * k, -bas.z * k)
bpy.context.view_layer.update()
for o in objets:
    o.name = "Aube_squelette"
    for m in o.data.materials:
        m.name = "aube_squelette"
print("dimensions", [round(v, 3) for v in (haut - bas) * k])

bpy.ops.export_scene.gltf(filepath=str(SORTIE), export_format="GLB")

# Aperçu : trois quarts face, lumière douce.
scene = bpy.context.scene
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (1.4, -1.9, 1.3)
cam.rotation_euler = (Vector((0, 0, .55)) - cam.location).to_track_quat("-Z", "Y").to_euler()
soleil = bpy.data.objects.new("Soleil", bpy.data.lights.new("Soleil", "SUN"))
soleil.data.energy = 3
soleil.rotation_euler = (.7, .2, .6)
scene.collection.objects.link(soleil)
scene.world = bpy.data.worlds.new("Fond")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.85, .82, .78, 1)
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError:
    pass
scene.render.resolution_x = scene.render.resolution_y = 700
scene.render.filepath = str(APERCU)
bpy.ops.render.render(write_still=True)
