"""Aube au coin noir (île 3) : le modèle Meshy (concept/ile_03/aube_concept_a.png, image → 3D meshy-t2 +
texture meshy-n1, 2026-11-22) mis à l'échelle, posé au sol et exporté pour Godot.

Une petite fille assise, genoux serrés, faite de mousse et de fleurs, avec sa lanterne sous un tissu.
Hauteur assise : ~0,85 m (une enfant de Semeurs ; les adultes font 2,5 à 3 m).

Lancer :  blender -b --factory-startup --python tools/blender/aube_coin_noir.py
"""
from pathlib import Path

import bpy
from mathutils import Vector

RACINE = Path(__file__).resolve().parents[2]
SOURCE = RACINE / "tools/blender/sources/meshy/aube/aube_meshy.glb"
SORTIE = RACINE / "assets/models/ile03/aube_coin_noir.glb"
APERCU = RACINE / "concept/ile_03/aube_coin_noir.png"
HAUTEUR = 0.85

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
    o.name = "Aube_mousse"
    for m in o.data.materials:
        m.name = "aube_mousse"
print("dimensions", [round(v, 3) for v in (haut - bas) * k])

bpy.ops.export_scene.gltf(filepath=str(SORTIE), export_format="GLB")

# Aperçu : trois quarts face, lumière douce.
scene = bpy.context.scene
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (1.1, -1.5, 1.0)
cam.rotation_euler = (Vector((0, 0, .4)) - cam.location).to_track_quat("-Z", "Y").to_euler()
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
