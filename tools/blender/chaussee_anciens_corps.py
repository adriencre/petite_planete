"""Dalles d'estran, varech du corps tombé et pose assise du robot du phare."""

from math import cos, pi, sin
from pathlib import Path
from random import Random

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


RACINE = Path(__file__).resolve().parents[2]
MODELES = RACINE / "assets/models"
ILE = MODELES / "ile02"
CAPTURES = RACINE / "captures/chaussee_anciens_corps"
CAPTURES.mkdir(parents=True, exist_ok=True)

# Abscisse le long de l'estran : z Godot, x Godot, dessus des dalles, demi-largeur.
PROFIL = (
    (13.45, -14.05, 0.148, 1.22), (15.35, -13.55, 0.165, 1.41),
    (17.80, -11.76, 0.169, 1.37), (19.70, -8.47, 0.171, 1.43),
    (22.75, -7.16, 0.164, 1.60), (27.60, -7.03, 0.168, 1.68),
    (31.70, -7.36, 0.176, 1.52), (33.55, -7.16, 0.551, 1.53),
    (35.70, -7.02, 0.703, 1.41),
)
BALISES = ((-9.8, 18.0), (-4.2, 25.0), (-9.8, 32.0))
CORPS_TOMBE = (-4.87, 0.205, 31.70)
ANGLE_TOMBE = 3.27  # rotations Godot, autour de Y
CORPS_ASSIS = (-2.12, 13.62, -2.13)
ANGLE_ASSIS = -2.408554  # cap 318°, comme le banc d’Iris

rng = Random(271)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def matiere(nom, couleur, rugosite=0.88):
    teinte = [int(couleur[i:i+2], 16) / 255 for i in (0, 2, 4)]
    rgb = tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in teinte)
    mat = bpy.data.materials.new(nom)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = mat.diffuse_color
    bsdf.inputs["Roughness"].default_value = rugosite
    return mat


calcaire = [matiere("Calcaire " + str(i), couleur) for i, couleur in enumerate(
    ("9C9485", "B6AC99", "C5B6A0", "D0C2AB", "ABABA0", "8A8B7E", "D8CBB2"), 1)]
support = matiere("Pierre humide dans les joints", "716D60")
varech = [matiere("Varech " + str(i), c, 0.58) for i, c in enumerate(("526A53", "425D50", "7A7850"), 1)]
for mat in varech:
    mat.use_backface_culling = False


class Maillage:
    def __init__(self, nom):
        self.nom = nom
        self.sommets = []
        self.faces = []
        self.matieres = []
        self.indices = []

    def ajouter(self, sommets, faces, matieres):
        origine = len(self.sommets)
        self.sommets.extend(sommets)
        for face, mat in zip(faces, matieres):
            self.faces.append(tuple(origine + i for i in face))
            if mat not in self.matieres:
                self.matieres.append(mat)
            self.indices.append(self.matieres.index(mat))

    def objet(self):
        mesh = bpy.data.meshes.new(self.nom)
        mesh.from_pydata(self.sommets, [], self.faces)
        for mat in self.matieres:
            mesh.materials.append(mat)
        for face, indice in zip(mesh.polygons, self.indices):
            face.material_index = indice
        objet = bpy.data.objects.new(self.nom, mesh)
        scene.collection.objects.link(objet)
        return objet


def profil(z):
    for gauche, droite in zip(PROFIL, PROFIL[1:]):
        if z <= droite[0]:
            t = max(0, (z - gauche[0]) / (droite[0] - gauche[0]))
            return tuple(a + t * (b - a) for a, b in zip(gauche[1:], droite[1:]))
    return PROFIL[-1][1:]


def plaque(maillage, contour, haut, epaisseur, mat, biseau=0.055, nuance=None):
    cx = sum(x for x, _ in contour) / len(contour)
    cy = sum(y for _, y in contour) / len(contour)
    n = len(contour)
    retrait = [(x + (cx-x) * 0.10, y + (cy-y) * 0.10) for x, y in contour]
    pts = [(x, y, haut(y) - dz) for anneau, dz in
           [(contour, epaisseur), (contour, biseau), (retrait, 0)] for x, y in anneau]
    faces = [tuple(reversed(range(n)))]
    mats = [mat]
    for k in (0, n):
        for i in range(n):
            j = (i + 1) % n
            faces.append((k+i, k+j, k+n+j, k+n+i))
            mats.append(nuance if nuance and k == n and i % 3 == 0 else mat)
    faces.append(tuple(range(2*n, 3*n)))
    mats.append(mat)
    maillage.ajouter(pts, faces, mats)


def rectangle_chanfreine(x, y, demi_x, demi_y):
    a, b = demi_x, demi_y
    c = min(a, b) * rng.uniform(0.24, 0.47)
    return [(x+dx, y+dy) for dx,dy in (
        (-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),(a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c))]


def ruban(maillage, points, largeur, mat):
    sommets = []
    for i, (x, y, z) in enumerate(points):
        avant = points[max(0, i-1)]
        apres = points[min(len(points)-1, i+1)]
        lat = Vector((apres[1]-avant[1], avant[0]-apres[0], 0)).normalized()
        amplitude = largeur * (1.0 - 0.82 * i / (len(points)-1))
        sommets.extend(Vector((x,y,z)) + s * amplitude * lat for s in (-1, 1))
    faces = [(i,i+1,i+3,i+2) for i in range(0, len(sommets)-2, 2)]
    maillage.ajouter(sommets, faces, [mat] * len(faces))


pierres = Maillage("Dalles et épaulements")
granulats = Maillage("Galets, sédiments et varech")
socle = Maillage("Fond de la chaussée")
collision = Maillage("SolChaussee-colonly")
for (z0, x0, h0, l0), (z1, x1, h1, l1) in zip(PROFIL, PROFIL[1:]):
    sol = [(x0-l0,-z0,h0-0.005), (x0+l0,-z0,h0-0.005), (x1+l1,-z1,h1-0.005), (x1-l1,-z1,h1-0.005)]
    collision.ajouter(sol, [(3,2,1,0)], [support])
    enveloppe = [(x, y, h-dz) for dz in (0.049, 0.26) for x,y,h in sol]
    faces = [(3,2,1,0), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    socle.ajouter(enveloppe, faces, [support] * len(faces))

z = PROFIL[0][0]
rang = 0
while z < PROFIL[-1][0]-0.001:
    suivant = min(z + rng.uniform(0.67, 0.96), PROFIL[-1][0])
    milieu = (z + suivant) / 2
    x, h, largeur = profil(milieu)
    coupes = (-1, -0.40, 0.18, 0.66, 1) if rang % 2 else (-1, -0.65, -0.12, 0.44, 1)
    for a,b in zip(coupes, coupes[1:]):
        cx = (a+b)*largeur/2
        demi = (b-a)*largeur/2-0.022
        contour = rectangle_chanfreine(cx, -milieu, demi, (suivant-z)/2-0.014)
        contour = [(xx + profil(-yy)[0], yy) for xx,yy in contour]
        decalage = rng.uniform(-0.010, 0.016)
        plaque(pierres, contour, lambda yy: profil(-yy)[1] + decalage,
               0.23, rng.choice(calcaire[1:]), 0.035, rng.choice(calcaire))
    for signe in (-1, 1):
        xx = x + signe * (largeur - rng.uniform(-0.09,0.17))
        if rang % 2:
            for _ in range(3):
                centre = xx + rng.uniform(-0.16, 0.16), -milieu + rng.uniform(-0.28,0.28)
                plaque(granulats, rectangle_chanfreine(*centre, rng.uniform(.04,.14), rng.uniform(.04,.12)),
                       lambda yy: profil(-yy)[1] + 0.025, 0.075, rng.choice(calcaire[:5]), 0.016)
        if rang % 3 == 1:
            for _ in range(3):
                x0, y0 = xx + rng.uniform(-0.11, 0.09), -milieu + rng.uniform(-0.24,0.24)
                h0 = profil(-y0)[1] + 0.021
                ruban(granulats, [(x0,y0,h0),(x0+signe*.13,y0+.10,h0+.018),
                                  (x0+signe*.24,y0+.16,h0-.025)], 0.024, rng.choice(varech))
    rang += 1
    z = suivant

for x,z in BALISES:
    for i in range(8):
        a,b = i*pi/4+.026,(i+1)*pi/4-.026
        anneau = [(x+r*cos(t), -z+r*sin(t)) for r,t in ((.40,a),(.66,a),(.66,b),(.40,b))]
        plaque(pierres, anneau, lambda _: 0.139, 0.17, calcaire[1+i%4], 0.022)


def exporter(nom, objets):
    bpy.ops.object.select_all(action="DESELECT")
    for objet in objets:
        objet.select_set(True)
    bpy.context.view_layer.objects.active = objets[0]
    bpy.ops.export_scene.gltf(filepath=str(ILE / f"{nom}.glb"), use_selection=True,
                              export_animations=False, export_apply=True)


def importer(chemin, **options):
    avant = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(chemin), **options)
    return list(set(scene.objects) - avant)


def placer(objets, pos, angle):
    x,h,z = pos
    for o in objets:
        if o.parent not in objets:
            o.matrix_world = Matrix.Translation((x,-z,h)) @ Matrix.Rotation(angle,4,"Z") @ o.matrix_world


visuels = [p.objet() for p in (pierres, socle, granulats)]
sol = collision.objet()
exporter("chaussee_estran", [*visuels, sol])
sol.hide_render = True

tombe = importer(MODELES / "ancien_corps.glb")
coque = next(o for o in tombe if o.type == "MESH")
pts = [coque.matrix_world @ v.co for v in coque.data.vertices]
peau = BVHTree.FromPolygons(pts, [tuple(p.vertices) for p in coque.data.polygons])
algues = Maillage("Varech accroché au poignet")
for cx,cy,n in ((-0.62,-1.28,13),(-0.25,-0.88,8),(-0.09,-0.35,5)):
    for _ in range(n):
        x, y = cx + rng.uniform(-0.085, 0.085), cy + rng.uniform(-0.095, 0.095)
        dx,dy = rng.uniform(-0.21,0.22), rng.uniform(-0.24,0.24)
        points = []
        for i in range(5):
            t=i/4
            xx,yy = x+t*dx+0.035*sin(t*pi), y+t*dy
            contact, _, _, _ = peau.ray_cast((xx,yy,0.90),(0,0,-1),1.30)
            niveau = contact.z + 0.013 if contact else (points[-1][2] - 0.038 if points else 0.03)
            points.append((xx,yy,max(-0.08,niveau)))
        ruban(algues, points, rng.uniform(.010,.023), rng.choice(varech))
algues_objet = algues.objet()
exporter("varech_ancien_corps", [algues_objet])
placer([*tombe, algues_objet], CORPS_TOMBE, ANGLE_TOMBE)

robot = importer(MODELES / "robot_meshy.glb", bone_heuristic="BLENDER")
armature = next(o for o in robot if o.type == "ARMATURE")
ad = armature.animation_data
for piste in ad.nla_tracks:
    piste.mute = True
ad.action = bpy.data.actions["assis"]
ad.action_slot = ad.action.slots[0]
scene.frame_set(1)
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
assis = []
for objet in robot:
    if objet.type == "MESH" and objet.parent == armature:
        mesh = bpy.data.meshes.new_from_object(objet.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        mesh.transform(Matrix.Translation((-0.124, 0, 0.029)) @ objet.matrix_world)
        fige = bpy.data.objects.new("Ancien corps assis", mesh)
        scene.collection.objects.link(fige)
        assis.append(fige)
for objet in robot:
    bpy.data.objects.remove(objet, do_unlink=True)
appui = Maillage("Socle de pierre de la galerie")
plaque(appui, rectangle_chanfreine(0,0.18,0.37,0.25), lambda _: 0.331, 0.35, calcaire[1], 0.045, calcaire[2])
assis.append(appui.objet())
exporter("ancien_corps_galerie", assis)
placer(assis, CORPS_ASSIS, ANGLE_ASSIS)


def bvh(objets):
    sommets, faces = [], []
    for o in objets:
        faces.extend(tuple(i+len(sommets) for i in f.vertices) for f in o.data.polygons)
        sommets.extend(o.matrix_world @ v.co for v in o.data.vertices)
    return BVHTree.FromPolygons(sommets, faces)


terrain = importer(ILE / "terrain_ile_02.glb")
phare = importer(ILE / "phare.glb")
for o in terrain + phare:
    if "colonly" in o.name:
        o.hide_render = True
    if o in phare and "toit" in o.name.lower():
        o.hide_render = True
sol_galerie = bvh([o for o in phare if o.type == "MESH" and "-col" in o.name])
point, _, _, _ = sol_galerie.ray_cast((CORPS_ASSIS[0], -CORPS_ASSIS[2], 14), (0,0,-1), 0.7)
assert point is not None and abs(point.z - CORPS_ASSIS[1]) < 0.025, point
bv_chaussee = bvh([sol, *(o for o in terrain if o.type == "MESH" and "-col" in o.name)])
hauteurs_avant = {}
for i in range(112):
    z = PROFIL[0][0] + (PROFIL[-1][0] - PROFIL[0][0])*i/111
    x,h,_ = profil(z)
    for dx in (-.40, 0, .40):
        contact, normale, _, _ = bv_chaussee.ray_cast((x+dx,-z,h+2),(0,0,-1),2.20)
        assert contact is not None and abs(contact.z-h) < .12 and normale.z > .79, (x+dx,z,h,contact)
        if dx in hauteurs_avant:
            assert abs(contact.z - hauteurs_avant[dx]) < .095, (x+dx,z,contact)
        hauteurs_avant[dx] = contact.z
print("Contrôle : 336 sondes de sol sur la chaussée et l'assise de la galerie.")

lanternes = []
for x,z in BALISES:
    lot = importer(MODELES / "lanterne_tulipe.glb")
    placer(lot, (x,.1,z),0)
    lanternes.extend(lot)

scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 1120
scene.render.resolution_y = 800
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("Ciel marin")
scene.world.use_nodes = True
fond = scene.world.node_tree.nodes["Background"]
fond.inputs[0].default_value = (0.44,0.58,0.76,1)
fond.inputs[1].default_value = 0.52
bpy.ops.object.light_add(type="SUN", rotation=(0.50,-0.63,-0.42))
bpy.context.object.data.energy = 2.45
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-.38))
mer = bpy.context.object
mer.data.materials.append(matiere("Mer", "7399A3", 0.36))
bpy.ops.object.camera_add()
scene.camera = bpy.context.object
scene.camera.data.type = "ORTHO"
route = terrain + visuels + lanternes + tombe + [algues_objet, mer]
for nom, cible, recul, echelle, galerie in (
    ("01_chaussee", (-8.9,-24.5,0.30), (9,-9,18), 28.4, False),
    ("02_corps_estran", (-4.93,-30.95,.37), (5,-7,10), 5.8, False),
    ("03_corps_galerie", (-2.34,2.23,14.17), (-5,7,9), 4.8, True),
):
    for o in route:
        o.hide_render = galerie or "colonly" in o.name
    for o in phare + assis:
        o.hide_render = not galerie or "colonly" in o.name or "toit" in o.name.lower()
    cible = Vector(cible)
    scene.camera.location = cible + Vector(recul)
    scene.camera.rotation_euler = (cible - scene.camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera.data.ortho_scale = echelle
    scene.render.filepath = str(CAPTURES / f"{nom}.png")
    bpy.ops.render.render(write_still=True)
