"""Prépare les quatre maillages bruts Meshy de la Colonie et exporte leurs GLB.

Blender en arrière-plan : --python tools/blender/maisons_fermees_colonie.py.
Les modèles exportés font une unité dans chaque axe, avec le socle à zéro.
La scène Godot définit les dimensions de chaque instance et sa collision.
"""

from pathlib import Path
import sys

import bpy
from mathutils import Vector

RACINE = Path(__file__).resolve().parents[2]
SOURCES = RACINE / "tools/blender/sources/meshy/maisons_colonie"
MODELES = RACINE / "assets/models/ile03/maisons_fermees"
APERCUS = RACINE / "concept/ile_03/maisons_fermees"
PALETTE = (
    ("Pierre crème", (.80, .65, .46)),
    ("Nervures claires", (.91, .77, .57)),
    ("Socle ocre", (.64, .36, .13)),
    ("Coque pêche", (.72, .35, .24)),
    ("Bois bleu passé", (.19, .32, .30)),
    ("Métal bruni", (.21, .18, .14)),
    ("Toit ocre", (.64, .38, .15)),
    ("Lanterne dorée", (.72, .44, .15)),
    ("Verre ambré", (1.0, .72, .32)),
    ("Auvent ocre", (.87, .49, .16)),
)


def materiau(nom, couleur):
    mat = bpy.data.materials.new(nom)
    mat.diffuse_color = (*couleur, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*couleur, 1)
    shader.inputs["Roughness"].default_value = .88
    return mat


def teinte_quai(position, normale):
    """Repères relevés sur les vues orthographiques du maillage du quai."""
    x, y, z = position
    en_facade = y < -.30
    if en_facade:
        # Vantail en retrait sous un linteau à angles coupés.
        largeur_porte = .09 - max(0, z-.39)*.42
        if z < .487 and abs(x+.113) < largeur_porte and -.366 < y < -.305:
            return 4
        # Lames des volets et coins supérieurs de la baie.
        if .204 < z < .416 and abs(x-.255) < .100-max(0, z-.38)*.50 and y < -.337:
            return 4
        # Le globe est en avant du mur, sous la potence.
        if -.335 < x < -.258 and y < -.44 and .294 < z < .481:
            return 8 if .336 < z < .419 else 7
        if -.31 < x < -.242 and y < -.40 and .43 < z < .499:
            return 5
        if -.241 < x < .030 and y < -.414 and .552 < z < .605:
            return 9
    if z < .094:
        return 2
    # La coque frontale s'élève au-dessus de la grande arche. Les côtés ont
    # une rive plus basse. Les nervures et les gouttières suivent le relief du toit.
    rive = .56 + max(0, .115-abs(x+.10)*.46) if y < -.31 else .539
    if z > rive:
        nervure_centrale = -.118 < x < -.058
        nervure_transverse = abs(y-.018) < .021 or (
            x > -.06 and abs(y + .52*x + .05) < .028
        )
        gouttiere = x > .428 or (y > .402 and z < .624)
        if nervure_centrale or gouttiere or (nervure_transverse and normale.z > .10):
            return 1
        return 3
    if en_facade and .14 < z < .685 and (
        abs(x-(-.41+(max(0, z-.46)*1.45))) < .031
        or abs(x-(.08+(max(0, z-.46)*.23))) < .030
    ):
        return 1
    return 0


def teinte(nom, position, normale):
    if nom == "quai":
        return teinte_quai(position, normale)
    x, y, z = position
    if z < .095:
        return 2
    seuil_toit = {"mitoyenne": .69, "angle": .72, "ville_haute": .73}[nom]
    if z > seuil_toit and (normale.z > .26 or z > seuil_toit + .105):
        return 6 if nom == "mitoyenne" else 3
    if y < -.36 and normale.y < -.63:
        if abs(x) < .109 and .095 < z < .32:
            return {"angle": 4, "mitoyenne": 2, "ville_haute": 3}[nom]
        if nom == "mitoyenne" and .45 < z < .59 and .09 < abs(x) < .26:
            return 2
        if nom == "angle" and .49 < z < .63 and abs(x) < .28:
            return 4
        if nom == "ville_haute" and .46 < z < .51 and abs(x) > .12:
            return 5
    return 1 if normale.z > .30 else 0


def preparer(nom):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCES / f"{nom}.glb"))
    objet, = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    bpy.context.view_layer.objects.active = objet
    objet.name = "Maison " + nom.replace("_", " ")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    reduction = objet.modifiers.new("Réduction du maillage source", "DECIMATE")
    reduction.ratio = min(1, 18000 / len(objet.data.polygons))
    bpy.ops.object.modifier_apply(modifier=reduction.name)

    sommets = objet.data.vertices
    minimum = Vector(tuple(min(v.co[i] for v in sommets) for i in range(3)))
    maximum = Vector(tuple(max(v.co[i] for v in sommets) for i in range(3)))
    dimensions = maximum - minimum
    origine = (maximum + minimum) / 2
    origine.z = minimum.z
    for sommet in sommets:
        sommet.co = tuple((sommet.co[i] - origine[i]) / dimensions[i] for i in range(3))
    # Les coordonnées Blender -Y correspondent à l'avant +Z dans Godot.
    objet.data.update()
    objet.data.materials.clear()
    for nom_mat, couleur in PALETTE:
        objet.data.materials.append(materiau(nom_mat, couleur))
    for polygone in objet.data.polygons:
        polygone.use_smooth = False
        polygone.material_index = teinte(nom, polygone.center, polygone.normal)

    MODELES.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(MODELES / f"maison_{nom}.glb"),
                              export_format="GLB", use_selection=True)
    print(f"{nom} : {len(objet.data.polygons)} faces")
    return objet, dimensions


def apercu(nom, objet, dimensions):
    # Réaffiche les proportions du maillage source pour la lecture du modèle.
    objet.scale = dimensions / max(dimensions)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Fond clair")
    if nom == "quai":
        scene.world.use_nodes = True
        fond = scene.world.node_tree.nodes.get("Background")
        fond.inputs["Color"].default_value = (.63, .68, .76, 1)
        fond.inputs["Strength"].default_value = .65
    else:
        scene.world.color = (.27, .27, .27)
    cible = Vector((0, 0, objet.scale.z/2))
    bpy.ops.object.camera_add(location=(1.55, -2.6, 1.9))
    camera = bpy.context.object
    camera.rotation_euler = (cible-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.38
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN", rotation=(.55, -.45, -.35) if nom != "quai" else (.52, -.38, .26))
    bpy.context.object.data.energy = 2.4
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 5
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 480
    scene.render.resolution_y = 480
    scene.render.filepath = str(APERCUS / f"modele_{nom}.png")
    bpy.ops.render.render(write_still=True)


types = ("quai", "mitoyenne", "angle", "ville_haute")
choix = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else types
for type_maison in choix:
    if type_maison not in types:
        raise ValueError(f"Maison inconnue : {type_maison}")
    apercu(type_maison, *preparer(type_maison))
