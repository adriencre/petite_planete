"""Rendus de présentation de la ville haute (parvis des Trois-Soleils, maison commune).

Usage : blender -b concept/ile_03/colonie_du_lagon.blend -P tools/blender/rendu_ville_haute.py -- [vues…] [--echantillons N]
Vues : ensemble, parvis, porte, interieur, dessus. Sorties : concept/ile_03/ville_haute_<vue>.png.
Les lanternes-tulipes du jeu sont posées sur les 9 emplacements, les 3 du motif allumées (rendu seulement).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

racine = Path(__file__).resolve().parents[2]
args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
echantillons = 96
if "--echantillons" in args:
    k = args.index("--echantillons")
    echantillons = int(args[k+1])
    del args[k:k+2]
vues = args or ["ensemble", "rue", "parvis", "jeu", "porte", "interieur", "bureau", "colonne", "borne"]

# Repères écrits par ville_haute.py (coordonnées Godot : x, hauteur, -y Blender).
reperes = {}
angle_parvis = 0.0
for ligne in (racine/"tools/blender/sources/ville_haute_reperes.txt").read_text(encoding="utf-8").splitlines():
    if ligne.startswith("#"):
        angle_parvis = float(ligne.split(":")[1])
        continue
    nom, x, h, z = ligne.split("\t")[:4]
    reperes[nom] = Vector((float(x), -float(z), float(h)))

scene = bpy.context.scene
collection = bpy.data.collections.new("Presentation_ville_haute")
scene.collection.children.link(collection)

# Les lanternes du parvis, importées une fois puis dupliquées.
bpy.ops.import_scene.gltf(filepath=str(racine/"assets/models/lanterne_tulipe.glb"))
modele = [o for o in bpy.context.selected_objects]
for o in modele:
    for c in o.users_collection:
        c.objects.unlink(o)
    collection.objects.link(o)
racine_modele = next(o for o in modele if o.parent is None)
coeur_eteint = next(o for o in modele if o.name.startswith("Coeur")).active_material
coeur_allume = coeur_eteint.copy()
surface = next(n for n in coeur_allume.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
surface.inputs["Emission Color"].default_value = (1.0, .72, .32, 1)
surface.inputs["Emission Strength"].default_value = 9.0

voyant_allume = bpy.data.materials.new("voyant_allume")
voyant_allume.use_nodes = True
surface = next(n for n in voyant_allume.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
surface.inputs["Base Color"].default_value = (1.0, .75, .35, 1)
surface.inputs["Emission Color"].default_value = (1.0, .72, .3, 1)
surface.inputs["Emission Strength"].default_value = 6.0


def dupliquer(position, allumee):
    copies = {}
    for o in modele:
        c = o.copy()
        collection.objects.link(c)
        copies[o] = c
    for o, c in copies.items():
        if o.parent in copies:
            c.parent = copies[o.parent]
    tete = copies[racine_modele]
    tete.location = position
    tete.rotation_euler.z = angle_parvis+math.pi
    if allumee:
        # Comme en jeu (lanterne_fleur.gd) : chaque pétale pivote de -1,15 rad autour de son axe X.
        for c in copies.values():
            if c.name.startswith("Petale"):
                c.matrix_basis = c.matrix_basis @ Matrix.Rotation(-1.15, 4, "X")
        for c in copies.values():
            if c.name.startswith("Coeur"):
                c.material_slots[0].link = "OBJECT"
                c.material_slots[0].material = coeur_allume
        lumiere = bpy.data.lights.new("lueur", "POINT")
        lumiere.energy = 420
        lumiere.color = (1.0, .78, .45)
        lumiere.shadow_soft_size = .25
        objet = bpy.data.objects.new("Lueur_lanterne", lumiere)
        objet.location = position+Vector((0, 0, 1.55))
        collection.objects.link(objet)


for nom, position in reperes.items():
    if nom.startswith("lanterne_"):
        dupliquer(position, nom.endswith("motif"))
for o in modele:
    o.hide_render = True

# Les voyants du motif sont allumés sur le pupitre, comme une fois l'énigme résolue.
for k in (1, 3, 8):
    o = bpy.data.objects.get(f"Voyant_commune_{k}")
    if o:
        for slot in o.material_slots:
            if slot.material and slot.material.name.startswith("verre"):
                slot.link = "OBJECT"
                slot.material = voyant_allume

# Lumière : soleil de fin d'après-midi, ciel clair, AgX.
soleil = next((o for o in scene.objects if o.type == "LIGHT" and o.data.type == "SUN"), None)
if soleil:
    soleil.rotation_euler = (math.radians(48), 0, math.radians(-62))
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

centre = (reperes["lanterne_5_leurre"]+reperes["porte_centre"])/2
porte = reperes["porte_centre"]
# Direction « vers la porte » dans le plan, et « vers la droite » quand on fait face à la porte.
avant = Vector((math.cos(angle_parvis+math.pi/2), math.sin(angle_parvis+math.pi/2), 0))
droite = Vector((math.cos(angle_parvis), math.sin(angle_parvis), 0))
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


masques_interieur = ("Toit_maison_commune", "Murs_hauts_maison_commune", "Murs_hauts_bureau_commune")
for vue in vues:
    for nom in masques_interieur:
        if nom in bpy.data.objects:
            bpy.data.objects[nom].hide_render = vue in ("interieur", "bureau")
    if vue == "ensemble":
        cadrer(centre-avant*44-droite*20+Vector((0, 0, 34)), centre+avant*3, 32)
    elif vue == "parvis":
        cadrer(centre-avant*19-droite*9+Vector((0, 0, 13)), centre+avant*1.5+Vector((0, 0, 1.5)), 30)
    elif vue == "porte":
        cadrer(porte-avant*7.5-droite*4.2+Vector((0, 0, 3.4)), porte+droite*1.0+Vector((0, 0, 1.9)), 32)
    elif vue == "interieur":
        salle = porte+avant*4.2
        cadrer(salle-avant*9+droite*11+Vector((0, 0, 14)), salle+avant*1.5, 30)
    elif vue == "bureau":
        bureau = porte+avant*6.9
        cadrer(bureau+droite*7.5-avant*1.5+Vector((0, 0, 9.5)), bureau+Vector((0, 0, .6)), 30)
    elif vue == "jeu":
        # Comme la caméra du jeu : au sud du robot, plongée d'environ 40°.
        cadrer(centre+Vector((0, -15, 13)), centre+Vector((0, 0, .5)), 30)
    elif vue == "rue":
        # Depuis la crête, la descente de la ville haute vers le parvis.
        cadrer(Vector((12, 38, 27)), Vector((36, 4, 5)), 26)
    elif vue == "colonne":
        a = reperes["affiche_1"]
        cadrer(a+Vector((-5.5, 3.5, 2.6)), a+Vector((0, 0, -.2)), 35)
    elif vue == "borne":
        b = reperes["borne_prise"]
        cadrer(b+Vector((2.6, -4.2, 2.2)), b+Vector((0, 1.2, -.1)), 32)
    elif vue == "dessus":
        cadrer(centre-avant*7+Vector((0, 0, 28)), centre+avant*1, None, ortho=26)
    scene.render.filepath = str(racine/f"concept/ile_03/ville_haute_{vue}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDU", vue, scene.render.filepath)
