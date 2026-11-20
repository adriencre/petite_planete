"""Génère le décor modulaire des grottes et de la crypte de l'île du Phare."""

from math import atan2, cos, pi, sin
from pathlib import Path
from random import Random

import bmesh
import bpy
from mathutils import Vector


RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "assets/models/ile02"
RENDUS = RACINE / "captures/grottes_crypte"
SOURCE = RACINE / "tools/blender/sources/grottes_crypte"
rng = Random(29)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Grottes et crypte du berceau"
scene.unit_settings.system = "METRIC"


def collection(nom):
    groupe = bpy.data.collections.new(nom)
    scene.collection.children.link(groupe)
    return groupe


def mat(nom, couleur, metal=0.0, emission=0.0):
    valeurs = [int(couleur[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = tuple(v / 12.92 if v < 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in valeurs)
    m = bpy.data.materials.new(nom)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = m.diffuse_color
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = 0.68
    p.inputs["Emission Color"].default_value = (*rgb, 1)
    p.inputs["Emission Strength"].default_value = emission
    return m


roches = [mat(f"Calcaire {i+1}", c) for i, c in enumerate(
    ("777E86", "93979A", "ADA9A0", "C5BCA7", "DACBB1", "8D8981"))]
dalles = [mat(f"Dalle {i+1}", c) for i, c in enumerate(("8C8E88", "AAA597", "B4AE9F", "9D9B91"))]
sable = mat("Sable humide", "A49C88")
eau = mat("Eau résiduelle", "547F83", 0.25)
fonte = mat("Fonte bleu noir", "33434A", 0.55)
gaine = mat("Gaine tressée", "3E5057", 0.12)
patine = mat("Cuivre oxydé", "50877D", 0.35)
laiton = mat("Laiton frotté", "D5A66C", 0.55)
email = mat("Émail ivoire", "F5E5BF", 0.0, 0.12)
verre = mat("Verre ambré", "FFBF6C", 0.0, 2.2)
algues = [mat("Varech", "4F6259"), mat("Algues sèches", "746F4C")]

socle = collection("01 · Estran et portail")
parcours = collection("02 · Galerie")
crypte = collection("03 · Crypte et ligne du berceau")
coupe = collection("04 · Voûtes et parois de coupe")
studio = collection("05 · Éclairage et caméras Blender")


def ranger(objet, groupe):
    for ancien in list(objet.users_collection):
        ancien.objects.unlink(objet)
    groupe.objects.link(objet)
    return objet


def boite(nom, position, dimensions, matiere, groupe, chanfrein=0.04, angle=0.0):
    maillage = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for sommet in bm.verts:
        sommet.co = tuple(c * d for c, d in zip(sommet.co, dimensions))
    bm.to_mesh(maillage)
    bm.free()
    objet = bpy.data.objects.new(nom, maillage)
    groupe.objects.link(objet)
    objet.location = position
    objet.rotation_euler.z = angle
    objet.data.materials.append(matiere)
    if chanfrein:
        mod = objet.modifiers.new("Arêtes usées", "BEVEL")
        mod.width = chanfrein
        mod.segments = 1
    return objet


def cylindre(nom, a, b, rayon, matiere, groupe, sommets=12):
    a, b = Vector(a), Vector(b)
    axe = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=sommets, radius=rayon, depth=axe.length,
                                        location=(a + b) / 2)
    objet = ranger(bpy.context.object, groupe)
    objet.name = nom
    objet.rotation_euler = axe.to_track_quat("Z", "Y").to_euler()
    objet.data.materials.append(matiere)
    return objet


def roche(nom, position, dimensions, groupe):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, location=position)
    objet = ranger(bpy.context.object, groupe)
    objet.name = nom
    objet.scale = dimensions
    objet.rotation_euler.z = rng.uniform(-0.35, 0.35)
    for matiere in roches:
        objet.data.materials.append(matiere)
    indice = rng.randrange(1, len(roches) - 1)
    for face in objet.data.polygons:
        face.material_index = max(0, min(5, indice + rng.choice((-1, 0, 0, 0, 1))))
    return objet


def anneau_voute(nom, x, y, rayon, naissance, groupe, profondeur):
    for i in range(9):
        a = pi * (i + 0.042) / 9
        b = pi * (i + 0.958) / 9
        points = [(rayon, a), (rayon + 0.42, a), (rayon + 0.42, b), (rayon, b)]
        sommets = [(x + r * cos(t), yy, naissance + r * sin(t))
                   for yy in (y - profondeur / 2, y + profondeur / 2) for r, t in points]
        maillage = bpy.data.meshes.new(nom)
        maillage.from_pydata(sommets, [], [(0, 1, 2, 3), (7, 6, 5, 4), (4, 5, 1, 0),
                                          (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3)])
        maillage.update()
        objet = bpy.data.objects.new(nom, maillage)
        groupe.objects.link(objet)
        maillage.materials.append(roches[4] if i == 4 else rng.choice(roches[2:5]))
        mod = objet.modifiers.new("Joints taillés", "BEVEL")
        mod.width = 0.045
        mod.segments = 1


def point(nom, position, couleur, puissance, rayon):
    data = bpy.data.lights.new(nom, "POINT")
    data.energy = puissance
    data.color = couleur
    data.shadow_soft_size = rayon
    objet = bpy.data.objects.new(nom, data)
    studio.objects.link(objet)
    objet.location = position


def luminaire(x, y, z, groupe):
    boite("Patte de fixation", (x, y, z - 0.23), (0.65, 0.42, 0.16), fonte, groupe)
    cylindre("Verre de service", (x, y, z - 0.13), (x, y, z + 0.20), 0.17, verre, groupe)
    for h in (-0.14, 0.21):
        cylindre("Bague du fanal", (x, y, z + h - 0.045), (x, y, z + h + 0.045),
                 0.23, laiton, groupe, 8)
    for i in range(4):
        a = i * pi / 2
        xx, yy = x + 0.195 * cos(a), y + 0.195 * sin(a)
        cylindre("Montant du fanal", (xx, yy, z - 0.14), (xx, yy, z + 0.24), 0.022, fonte, groupe, 6)
    point("Rebond chaud", (x, y - 0.24, z + 0.10), (1.0, 0.66, 0.36), 95, 0.55)


# Origine au seuil. La galerie remonte dans le rocher suivant +Y.
def denivele_approche(y):
    return min(0.0, y + 1.4) * 0.029


seuil = boite("Socle d’estran", (0, -2.9, -0.26), (9.8, 6.2, 0.50), sable, socle, 0.08)
bm = bmesh.new()
bm.from_mesh(seuil.data)
bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                      dist=0.00001, plane_co=(0, -1.4 - seuil.location.y, 0), plane_no=(0, 1, 0))
for sommet in bm.verts:
    sommet.co.z += denivele_approche(sommet.co.y + seuil.location.y)
bm.to_mesh(seuil.data)
bm.free()
for i in range(17):
    x = rng.choice((-1, 1)) * rng.uniform(2.15, 4.6)
    y = rng.uniform(-5.6, 0.0)
    roche("Éboulis de l’estran", (x, y, 0.05 + denivele_approche(y)),
          (rng.uniform(0.26, 0.9), rng.uniform(0.18, 0.65), rng.uniform(0.13, 0.40)), socle)
for x in (-3.3, 3.1):
    cuvette = boite("Cuvette de marée", (x, -4.2, 0.002 + denivele_approche(-4.2)),
                    (1.65, 1.15, 0.03), eau, socle, 0.015, x / 10)
    cuvette.rotation_euler.x = 0.029
    for i in range(8):
        x_algue, y_algue = x + rng.uniform(-0.9, 0.9), rng.uniform(-4.9, -3.6)
        boite("Laisse de mer", (x_algue, y_algue, 0.025 + denivele_approche(y_algue)),
              (rng.uniform(0.12, 0.35), 0.05, 0.03), rng.choice(algues), socle, 0.012, rng.random() * pi)

for signe in (-1, 1):
    for i in range(4):
        boite("Piédroit du portail", (signe * 1.98, 0, 0.25 + i * 0.45),
              (0.61, 0.94, 0.43), roches[2 + i % 3], socle, 0.055)
    for i in range(7):
        roche("Strate du seuil", (signe * (3.9 + rng.uniform(-0.27, 0.27)), 0.96, 0.29 + i * 0.55),
              (1.43 + rng.uniform(0, 0.35), 1.31, 0.63), socle)
anneau_voute("Claveau du portail", 0, 0, 1.69, 1.80, socle, 0.94)
luminaire(-2.42, -0.73, 2.06, socle)

for i in range(12):
    y = i * 0.83 - 0.94
    x = 0.3 * max(y - 2, 0)
    for j in range(4):
        y_dalle = 7.92 if i == 11 else y
        longueur = 0.305 if i == 11 else 0.825
        boite("Dalle sous la galerie", (x + (j - 1.5) * 0.86, y_dalle, -0.085),
              (0.85, longueur, 0.18), rng.choice(dalles), parcours, 0.035)
    for signe in (-1, 1):
        groupe = parcours if signe == -1 else coupe
        boite("Chasse-roue de pierre", (x + signe * 1.87, y, 0.13),
              (0.34, 0.81, 0.38), roches[3], parcours, 0.065)
        if y < 0.65:
            continue
        for niveau in range(5):
            roche("Calcaire lité", (x + signe * (2.43 + rng.uniform(-0.18, 0.16)), y,
                                   0.43 + niveau * 0.65),
                  (0.81, 0.78, 0.59), groupe)
    if y >= 0.65:
        roche("Dalle de voûte", (x, y, 4.04), (2.74, 0.69, 0.61), coupe)

for y in (3.0, 6.35):
    x = 0.3 * (y - 2)
    for signe in (-1, 1):
        boite("Contrefort", (x + signe * 1.99, y, 0.92), (0.41, 0.65, 1.88),
              roches[2], parcours if signe < 0 else coupe, 0.07)
    anneau_voute("Arc de confortement", x, y, 1.79, 1.85, coupe, 0.61)
    luminaire(x - 1.66, y - 0.15, 1.88, parcours)

# La salle s'élargit autour d'une auge technique fermée par des grilles.
cx = 3.05
for i in range(10):
    for j in range(10):
        x, y = cx + (j - 4.5) * 0.82, 8.5 + i * 0.86
        if j in (4, 5) and i >= 3:
            continue
        boite("Dalle de crypte", (x, y, -0.09), (0.81, 0.85, 0.19), rng.choice(dalles), crypte, 0.03)
for signe in (-1, 1):
    for i in range(8):
        for niveau in range(4):
            boite("Assise maçonnée", (cx + signe * 4.22, 9 + i * 1.04, 0.42 + niveau * 0.84),
                  (0.64, 1.02, 0.82), rng.choice(roches[1:5]),
                  crypte if signe < 0 else coupe, 0.09)
    for y in (10.15, 13.5, 16.1):
        groupe = crypte if signe < 0 else coupe
        for h, largeur, hauteur in ((0.16, 0.92, 0.32), (1.85, 0.52, 3.14), (3.49, 0.84, 0.35)):
            boite("Pilier de la crypte", (cx + signe * 3.93, y, h),
                  (largeur, largeur, hauteur), roches[3], groupe, 0.06)
        luminaire(cx + signe * 3.48, y, 2.15, groupe)
for i in range(8):
    for niveau in range(4):
        boite("Mur du fond", (cx + (i - 3.5) * 1.03, 16.98, 0.42 + 0.84 * niveau),
              (1.01, 0.69, 0.82), rng.choice(roches[1:5]), crypte, 0.065)
for depart, arrivee, groupe in ((-1.45, 0.0, crypte), (3.60, 7.45, coupe)):
    largeur = (arrivee - depart) / 3
    for i in range(3):
        for niveau in range(4):
            boite("Épaulement de l’entrée", (depart + largeur * (i + 0.5), 8.38, 0.42 + niveau * 0.84),
                  (largeur - 0.022, 0.59, 0.82), rng.choice(roches[1:5]), groupe, 0.055)
for y in (9.32, 12.7, 16.25):
    anneau_voute("Nervure de la crypte", cx, y, 3.8, 1.67, coupe, 0.53)


def cable(points, rayon):
    courbe = bpy.data.curves.new("Ligne du berceau", "CURVE")
    courbe.dimensions = "3D"
    courbe.resolution_u = 12
    courbe.bevel_depth = rayon
    courbe.bevel_resolution = 2
    courbe.use_fill_caps = True
    spline = courbe.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for noeud, coord in zip(spline.bezier_points, points):
        noeud.co = coord
        noeud.handle_left_type = noeud.handle_right_type = "AUTO"
    objet = bpy.data.objects.new("Câble principal", courbe)
    crypte.objects.link(objet)
    courbe.materials.append(gaine)


boite("Fond de l’auge", (cx, 14.1, -0.68), (1.65, 5.97, 0.23), fonte, crypte)
for signe in (-1, 1):
    boite("Longeron de l’auge", (cx + signe * 0.79, 14.08, -0.19), (0.11, 5.97, 0.39), patine, crypte)
for i in range(21):
    y = 10.83 + i * 0.28
    if 14.25 < y < 15.17:
        for signe in (-1, 1):
            boite("Traverse autour du câble", (cx + signe * 0.58, y, 0.016),
                  (0.41, 0.064, 0.075), fonte, crypte, 0.012)
    else:
        boite("Traverse ajourée", (cx, y, 0.016), (1.57, 0.064, 0.075), fonte, crypte, 0.012)
for j in (-0.42, 0.42):
    boite("Raidisseur de la grille", (cx + j, 13.62, 0.016), (0.043, 5.8, 0.075), patine, crypte, 0.009)

cable([(cx, 16.91, 2.23), (cx, 16.31, 2.23), (cx, 15.52, 1.85), (cx, 14.99, 0.77),
       (cx, 14.49, -0.25), (cx, 12.04, -0.37), (cx + 0.12, 11.12, -0.37),
       (cx + 0.73, 10.56, -0.48), (cx + 3.79, 10.24, -0.62)], 0.245)
for i in range(11):
    y = 16.25 + i * 0.041
    cylindre("Gaine annelée du manchon", (cx, y - 0.012, 2.23), (cx, y + 0.012, 2.23),
             0.268, fonte, crypte, 16)
for y, largeur, rayon, matiere in ((16.57, 0.32, 0.37, patine), (16.72, 0.13, 0.52, fonte),
                                  (16.60, 0.075, 0.42, laiton)):
    cylindre("Traversée étanche", (cx, y - largeur / 2, 2.23), (cx, y + largeur / 2, 2.23),
             rayon, matiere, crypte, 16)
for i in range(8):
    a = i * pi / 4
    x, z = cx + 0.461 * cos(a), 2.23 + 0.461 * sin(a)
    cylindre("Boulon de la bride", (x, 16.58, z), (x, 16.68, z), 0.052, laiton, crypte, 6)
for i in range(4):
    y = 11.44 + i * 0.94
    cylindre("Selle de guidage", (cx, y, -0.37), (cx, y + 0.105, -0.37), 0.277, patine, crypte)

# Plaque face à l'arrivée, lisible sur le rendu de détail.
plaque_x, plaque_y, plaque_z = cx - 1.67, 14.55, 1.30
for x in (plaque_x - 0.74, plaque_x + 0.74):
    boite("Pied de plaque", (x, plaque_y + 0.12, 0.62), (0.16, 0.23, 1.23), patine, crypte)
    boite("Sabot boulonné", (x, plaque_y + 0.12, 0.06), (0.36, 0.37, 0.15), fonte, crypte)
boite("Cadre de la plaque", (plaque_x, plaque_y, plaque_z), (2.64, 0.13, 0.92), patine, crypte, 0.06)
boite("Champ de la plaque", (plaque_x, plaque_y - 0.069, plaque_z), (2.49, 0.026, 0.77), fonte, crypte, 0.012)
for x in (plaque_x - 1.14, plaque_x + 1.14):
    for z in (plaque_z - 0.31, plaque_z + 0.31):
        cylindre("Rivet de plaque", (x, plaque_y - 0.106, z), (x, plaque_y - 0.075, z), 0.031, laiton, crypte, 8)
for texte, h, taille, matiere in (
    ("LIGNE DU BERCEAU", 0.20, 0.235, email),
    ("PRIORITAIRE", -0.025, 0.17, laiton),
    ("NE JAMAIS COUPER", -0.24, 0.137, email),
):
    lettrage = bpy.data.curves.new(texte, "FONT")
    lettrage.body = texte
    lettrage.align_x = "CENTER"
    lettrage.align_y = "CENTER"
    lettrage.size = taille
    lettrage.extrude = 0.0015
    lettrage.materials.append(matiere)
    objet = bpy.data.objects.new(texte, lettrage)
    crypte.objects.link(objet)
    objet.location = (plaque_x, plaque_y - 0.089, plaque_z + h)
    objet.rotation_euler.x = pi / 2

# Traces de service : bande de repérage, agrafes et rail de levage.
for i in range(8):
    boite("Repère de l’auge", (cx + 0.98, 11.25 + i * 0.65, 0.013),
          (0.21, 0.13, 0.017), laiton, crypte, 0.008)
boite("Traverse de manutention", (cx, 14.9, 4.62), (7.79, 0.24, 0.34), fonte, coupe)
for x in (cx - 3.45, cx + 3.45):
    boite("Ancrage de manutention", (x, 14.9, 4.46), (0.64, 0.63, 0.55), patine, coupe, 0.05)
for i in range(10):
    x = cx - 3.3 + 0.72 * i
    boite("Traces du niveau d'eau", (x, 16.60, 0.45 + rng.uniform(-0.03, 0.03)),
          (rng.uniform(0.14, 0.49), 0.025, rng.uniform(0.023, 0.066)), rng.choice(algues), crypte, 0.01)

# Treuil manuel de manutention et petites fixations laissées par les gardiens.
tx, ty = cx + 2.66, 15.21
boite("Socle du treuil", (tx, ty, 0.17), (1.47, 0.99, 0.31), roches[2], crypte, 0.12)
for x in (tx - 0.48, tx + 0.48):
    boite("Joue du treuil", (x, ty, 0.51), (0.16, 0.66, 0.60), patine, crypte, 0.075)
    for y in (ty - 0.33, ty + 0.33):
        cylindre("Goujon du treuil", (x, y, 0.31), (x, y, 0.39), 0.06, laiton, crypte, 6)
cylindre("Axe du treuil", (tx - 0.65, ty, 0.67), (tx + 0.74, ty, 0.67), 0.105, fonte, crypte)
for i in range(12):
    x = tx - 0.30 + 0.052 * i
    cylindre("Tours de cordage", (x, ty, 0.67), (x + 0.05, ty, 0.67), 0.225, gaine, crypte, 16)
for x in (tx - 0.38, tx + 0.38):
    cylindre("Flasque du treuil", (x - 0.055, ty, 0.67), (x + 0.055, ty, 0.67), 0.30, patine, crypte)
cylindre("Bras de manivelle", (tx + 0.67, ty, 0.67), (tx + 0.67, ty - 0.35, 0.46), 0.049, fonte, crypte)
cylindre("Poignée de manivelle", (tx + 0.65, ty - 0.35, 0.46), (tx + 0.88, ty - 0.35, 0.46),
         0.067, laiton, crypte)
for i in range(5):
    x = cx - 3.25 + i * 0.19
    boite("Cales de remplacement", (x, 15.96, 0.12), (0.17, 0.50, 0.22),
          roches[3 + i % 2], crypte, 0.045, rng.uniform(-0.17, 0.17))


def camera(nom, position, cible, echelle):
    data = bpy.data.cameras.new(nom)
    data.type = "ORTHO"
    data.ortho_scale = echelle
    objet = bpy.data.objects.new(nom, data)
    studio.objects.link(objet)
    objet.location = position
    objet.rotation_euler = (Vector(cible) - objet.location).to_track_quat("-Z", "Y").to_euler()
    return objet


def area(nom, position, cible, couleur, watts, taille):
    data = bpy.data.lights.new(nom, "AREA")
    data.energy, data.size, data.color = watts, taille, couleur
    objet = bpy.data.objects.new(nom, data)
    studio.objects.link(objet)
    objet.location = position
    objet.rotation_euler = (Vector(cible) - objet.location).to_track_quat("-Z", "Y").to_euler()


area("Jour de l’estran", (1, -8, 12), (0, 0, 0), (0.73, 0.86, 1.0), 2300, 9)
area("Lumière de coupe", (8, 4, 13), (1, 8, 0), (0.62, 0.78, 1.0), 1900, 10)
area("Rebond de la crypte", (0, 11.8, 6.7), (cx, 15, 1), (1.0, 0.80, 0.58), 790, 5)
scene.world = bpy.data.worlds.new("Air marin")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.075, 0.10, 0.15, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.34
scene.render.engine = "CYCLES"
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 840
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"

vues = [
    ("01_entree", camera("Entrée depuis l’estran", (5, -15, 7), (0, 0.0, 1.35), 13.2), False),
    ("02_coupe", camera("Coupe du parcours", (23, -17, 25), (1.65, 5.3, 0.8), 28), True),
    ("03_crypte", camera("Gros plan sur la ligne", (10, 6.3, 6.0), (2.87, 14.28, 1.35), 9.2), True),
]

def exporter(groupe, nom):
    """Fusionne les géométries évaluées pour l'export sans aplatir la source."""
    deps = bpy.context.evaluated_depsgraph_get()
    copies = []
    for objet in groupe.objects:
        mesh = bpy.data.meshes.new_from_object(objet.evaluated_get(deps))
        mesh.transform(objet.matrix_world)
        copie = bpy.data.objects.new(objet.name, mesh)
        copies.append(copie)
    bpy.ops.object.select_all(action="DESELECT")
    for copie in copies:
        groupe.objects.link(copie)
        copie.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    copies[0].name = nom
    bpy.ops.export_scene.gltf(filepath=str(SORTIE / f"{nom}.glb"), use_selection=True)
    maillage = copies[0].data
    bpy.data.objects.remove(copies[0], do_unlink=True)
    bpy.data.meshes.remove(maillage)


# Chaque GLB partage l'origine du seuil et peut être placé indépendamment.
for groupe, nom in ((socle, "entree_grottes"), (parcours, "galerie_grottes"),
                    (crypte, "crypte_berceau"), (coupe, "voutes_crypte")):
    exporter(groupe, nom)

SOURCE.mkdir(parents=True, exist_ok=True)
RENDUS.mkdir(parents=True, exist_ok=True)
scene.camera = vues[1][1]
coupe.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / "grottes_crypte.blend"))
for nom, vue, ouverte in vues:
    coupe.hide_render = ouverte
    scene.camera = vue
    scene.render.filepath = str(RENDUS / f"{nom}.png")
    bpy.ops.render.render(write_still=True)
