"""Rendus de contrôle du jardin du haut (G3) : écluse, halage, jardin clos, serres basses.

Usage : blender -b concept/ile_03/colonie_du_lagon.blend -P tools/blender/rendu_jardin_du_haut.py -- [vues…] [--echantillons N]
Vues : ensemble, ecluse, jardin, serres, halage, dessus, lampe. Sorties : concept/ile_03/jardin_du_haut_<vue>.png.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

racine = Path(__file__).resolve().parents[2]
args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
echantillons = 64
if "--echantillons" in args:
    k = args.index("--echantillons")
    echantillons = int(args[k+1])
    del args[k:k+2]
vues = args or ["ensemble", "ecluse", "jardin", "serres", "halage", "dessus", "lampe"]

# Repères écrits par jardin_du_haut.py (coordonnées Godot : x, hauteur, -y Blender).
reperes = {}
for ligne in (racine/"tools/blender/sources/jardin_du_haut_reperes.txt").read_text(encoding="utf-8").splitlines():
    if ligne.startswith("#"):
        continue
    nom, x, h, z = ligne.split("\t")[:4]
    reperes[nom] = Vector((float(x), -float(z), float(h)))

scene = bpy.context.scene
collection = bpy.data.collections.new("Presentation_jardin")
scene.collection.children.link(collection)

# La lampe-mère allumée (rendu seulement) : cœur émissif et lueur chaude.
coeur = bpy.data.objects.get("Coeur_lampe_mere")
if coeur:
    allume = bpy.data.materials.new("coeur_allume")
    allume.use_nodes = True
    surface = next(n for n in allume.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    surface.inputs["Base Color"].default_value = (1.0, .8, .45, 1)
    surface.inputs["Emission Color"].default_value = (1.0, .74, .38, 1)
    surface.inputs["Emission Strength"].default_value = 12.0
    for slot in coeur.material_slots:
        slot.link = "OBJECT"
        slot.material = allume
    lumiere = bpy.data.lights.new("lueur_lampe_mere", "POINT")
    lumiere.energy = 900
    lumiere.color = (1.0, .78, .48)
    lumiere.shadow_soft_size = .4
    objet = bpy.data.objects.new("Lueur_lampe_mere", lumiere)
    objet.location = coeur.location
    collection.objects.link(objet)

soleil = next((o for o in scene.objects if o.type == "LIGHT" and o.data.type == "SUN"), None)
if soleil:
    soleil.rotation_euler = (math.radians(48), 0, math.radians(-30))
    soleil.data.energy = 3.2
    soleil.data.angle = math.radians(4)
    soleil.data.color = (1.0, .95, .86)
fond = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
fond.inputs[0].default_value = (.80, .90, 1.0, 1)
fond.inputs[1].default_value = .9
scene.render.engine = "CYCLES"
scene.cycles.samples = echantillons
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    pass
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
camera = scene.camera


def cadrer(oeil, cible, focale=None, ortho=None):
    camera.location = oeil
    camera.rotation_euler = (cible-oeil).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = ortho
    else:
        camera.data.type = "PERSP"
        camera.data.lens = focale
    camera.data.clip_start = .1


ecluse = (reperes["sas_1_centre"]+reperes["sas_4_centre"])/2
lampe = reperes["lampe_mere"]
for vue in vues:
    if vue == "ensemble":
        # Depuis le sud du lagon, en hauteur : halage, écluse, jardin, citerne et serres.
        cadrer(Vector((4, -30, 34)), Vector((-2, 18, 6)), 30)
    elif vue == "ecluse":
        cadrer(ecluse+Vector((10, -24, 14)), ecluse+Vector((0, 0, 3)), 32)
    elif vue == "jardin":
        cadrer(lampe+Vector((-6, -20, 16)), lampe+Vector((-2, 0, 1)), 28)
    elif vue == "lampe":
        cadrer(lampe+Vector((-3.5, -9, 6)), lampe+Vector((0, 1.5, 3.5)), 30)
    elif vue == "serres":
        # Vue de dessus des serres basses : l'éventail des arbres penchés vers la lampe.
        cadrer(Vector((0, 26, 70)), Vector((0, 34, 8)), None, ortho=46)
    elif vue == "halage":
        cadrer(Vector((12, -12, 16)), Vector((-20, 2, 1)), 26)
    elif vue == "dessus":
        cadrer(Vector((0, 22, 80)), Vector((0, 22.5, 5)), None, ortho=70)
    scene.render.filepath = str(racine/f"concept/ile_03/jardin_du_haut_{vue}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDU", vue, scene.render.filepath)
