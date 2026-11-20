"""Décor du jardin d’Iris et rendu au-dessus du plateau de l’île 2."""

from math import cos, pi, sin
from pathlib import Path
from random import Random

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


RACINE = Path(__file__).resolve().parents[2]
MODELES = RACINE / "assets/models/ile02"
CAPTURES = RACINE / "captures/jardin_iris"
ORIGINE = Vector((-12, 10.5, 5.58))
BANC = Vector((-1.02, 1.72, 0.12))
ANGLE = -138 * pi / 180  # Le modèle du banc fait face à -Y dans Blender.
ARBRE = Vector((3.12, 1.83, 0.08))
RNG = Random(318)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(nom, hexad, rugosite=0.88, metal=0):
    rgb = [int(hexad[i:i+2], 16) / 255 for i in (0, 2, 4)]
    rvb = [v / 12.92 if v < 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    m = bpy.data.materials.new(nom)
    m.diffuse_color = (*rvb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = m.diffuse_color
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    return m


bois = [mat("Bois délavé " + str(i), c) for i, c in enumerate(("827267", "A58B73", "B9A087", "977D69"))]
pierre = [mat("Calcaire " + str(i), c) for i, c in enumerate(("9F9C8C", "BBB6A3", "C8C1AB", "AAA68F"))]
terre = [mat("Argile sèche " + str(i), c) for i, c in enumerate(("9F7760", "BA8D6E", "AB7F65", "C09677", "84624F"))]
ecorce = [mat("Écorce du rosier " + str(i), c) for i, c in enumerate(("70554D", "8D695E", "A67B72", "BE9488", "976F68"))]
aubier = mat("Aubier exposé", "C8A27F")
patine = mat("Cuivre verdi", "648F80", 0.43, 0.43)
bronze = mat("Bronze des attaches", "8E7962", 0.44, 0.60)
fonte = mat("Fer oxydé", "575E5B", 0.51, 0.48)
sec = [mat("Herbe sèche " + str(i), c) for i, c in enumerate(("A09362", "BFB077", "CAAE8A"))]


def maillage(nom, sommets, faces, materiaux, indices=None):
    me = bpy.data.meshes.new(nom)
    me.from_pydata(sommets, [], faces)
    for m in materiaux:
        me.materials.append(m)
    if indices is not None:
        for p, i in zip(me.polygons, indices):
            p.material_index = i
    o = bpy.data.objects.new(nom, me)
    scene.collection.objects.link(o)
    return o


def bloc(nom, pos, taille, m, chanfrein=.04, angle=0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = tuple(a*b for a,b in zip(v.co, taille))
    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(nom, mesh)
    scene.collection.objects.link(o)
    o.location = pos
    o.rotation_euler.z = angle
    mesh.materials.append(m)
    if chanfrein:
        mod = o.modifiers.new("Arêtes irrégulières", "BEVEL")
        mod.width = chanfrein
        mod.segments = 1
    return o


def tube(nom, points, rayons, mats, n=8, bout=None, irreg=0):
    points = [Vector(p) for p in points]
    v, f, ids = [], [], []
    profil = [RNG.uniform(1-irreg, 1+irreg) for _ in range(n)]
    for k, (p, r) in enumerate(zip(points, rayons)):
        d = (points[min(k+1,len(points)-1)] - points[max(k-1,0)]).normalized()
        ref = Vector((0, 1, 0)) if abs(d.y) < .90 else Vector((1, 0, 0))
        a = d.cross(ref).normalized()
        b = d.cross(a)
        for j in range(n):
            t = 2*pi*j/n
            v.append(p + r * profil[j] * (cos(t)*a + sin(t)*b))
        if k:
            for j in range(n):
                a0 = (k-1)*n
                b0 = k*n
                suivant = (j+1)%n
                f.append((a0+j,a0+suivant,b0+suivant,b0+j))
                ids.append(j % len(mats))
    f.extend((tuple(reversed(range(n))), tuple(range(len(v)-n,len(v)))))
    ids.extend((0, len(mats) if bout else 0))
    return maillage(nom,v,f,[*mats,bout] if bout else mats,ids)


def regrouper(nom, objets):
    deps = bpy.context.evaluated_depsgraph_get()
    copies = []
    for objet in objets:
        mesh = bpy.data.meshes.new_from_object(objet.evaluated_get(deps))
        mesh.transform(objet.matrix_world)
        copies.append(bpy.data.objects.new(nom, mesh))
    bpy.ops.object.select_all(action="DESELECT")
    for o in copies:
        scene.collection.objects.link(o)
        o.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    groupe = copies[0]
    groupe.name = nom
    groupe.data.name = nom
    for o in objets:
        bpy.data.objects.remove(o, do_unlink=True)
    return groupe


pieces = []
for x in (-0.89, .89):
    pieces.append(bloc("Joue taillée", (x,.015,.31), (.39,.88,.71), pierre[1], .069))
    pieces.append(bloc("Socle de joue", (x,.015,.08), (.55,.99,.23), pierre[0], .059))
    pieces.append(bloc("Montant du dossier", (x,.34,.96), (.13,.15,.87), bronze,.022))
for j,y in enumerate((-.31,-.10,.11,.32)):
    pieces.append(bloc("Lame de l’assise", (0,y,.673), (2.43,.193,.125), bois[j], .031))
    for x in (-.88,.88):
        pieces.append(tube("Clou à tête mate", [(x,y,.732),(x,y,.749)], [.034,.031], [fonte], 8))
for j in range(3):
    lame = bloc("Planche du dossier", (0,.365+j*.027,.91+j*.19), (2.43,.108,.165), bois[j], .026)
    lame.rotation_euler.x = -.14
    pieces.append(lame)
    for x in (-.88,.88):
        y,z = .31+j*.027,.91+j*.19
        pieces.append(tube("Clou du dossier", [(x,y,z),(x,y-.014,z)], [.03,.026], [fonte], 7))
banc = regrouper("BancIris", pieces)
banc.matrix_world = Matrix.Translation(BANC) @ Matrix.Rotation(ANGLE, 4, "Z")

def branche(nom, points, rayons, n=7):
    return tube(nom, [ARBRE+Vector(p) for p in points], rayons, ecorce, n, aubier, .25)


arbre = [
    branche("Tronc vrillé", [(0,0,-.14),(.01,0,.24),(-.12,.02,.66),
            (.05,.08,1.17),(.22,.04,1.75),(.30,.17,2.25),(.42,.22,2.70)],
            [.40,.32,.247,.195,.145,.095,.056], 10),
    branche("Fourche d’est", [(.16,.08,1.41),(.49,.03,1.83),(.96,-.10,2.08),
            (1.29,-.06,2.26),(1.61,.02,2.19)], [.162,.127,.074,.046,.029]),
    branche("Pointe d’est", [(.94,-.10,2.08),(1.01,-.31,2.41),(1.22,-.42,2.66)],
            [.069,.041,.017], 6),
    branche("Fourche ouest", [(-.04,.07,1.10),(-.49,.17,1.53),(-.88,.15,1.85),
            (-1.32,.31,2.04),(-1.54,.53,2.30)], [.159,.122,.077,.042,.020]),
    branche("Rameau fendu", [(-.81,.16,1.83),(-.97,-.01,2.16),(-1.13,-.23,2.43)],
            [.075,.045,.022], 6),
    branche("Cime brisée", [(.27,.14,2.10),(.19,.03,2.54),(-.05,-.17,2.85),
            (-.23,-.26,3.22)], [.086,.061,.037,.021], 6),
    branche("Bois arraché", [(.29,.14,2.12),(.55,.43,2.43),(.70,.62,2.54)],
            [.080,.062,.045], 6),
    branche("Rameau bas", [(-.43,.16,1.52),(-.67,.5,1.58),(-.83,.76,1.72)],
            [.085,.047,.018], 6),
]
for i in range(6):
    a = i*pi/3 + RNG.uniform(-.20,.20)
    x,y = cos(a), sin(a)
    arbre.append(branche("Racine sèche", [(x*.14,y*.14,.26),(x*.36,y*.36,.08),(x*.72,y*.72,-.06)],
                         [.18,.107,.031], 6))
arbre = regrouper("ArbreRoseMort", arbre)


def mottes_de_terre():
    graines = [Vector((-.81 + i*.40 + RNG.uniform(-.14,.14),
                       -.46 + j*.31 + RNG.uniform(-.14,.14)))
                for j in range(4) for i in range(5)]
    bord = [Vector(p) for p in ((-.93,-.56),(.93,-.56),(.93,.56),(-.93,.56))]
    for graine in graines:
        polygone = bord
        for autre in graines:
            if autre == graine:
                continue
            axe = autre - graine
            milieu = (autre + graine) * .5
            coupe = []
            for a, b in zip(polygone[-1:]+polygone[:-1], polygone):
                da, db = (a-milieu).dot(axe), (b-milieu).dot(axe)
                if (da <= 0) != (db <= 0):
                    coupe.append(a.lerp(b, da / (da-db)))
                if db <= 0:
                    coupe.append(b)
            polygone = coupe
        if len(polygone) < 3:
            continue
        centre = sum(polygone, Vector((0,0))) / len(polygone)
        sommets = [(*centre.lerp(p,.94), .471+RNG.uniform(-.011,.008)) for p in polygone]
        sommets.append((*centre, .480+RNG.uniform(-.009,.012)))
        n = len(polygone)
        yield maillage("Motte fendue", sommets, [(i,(i+1)%n,n) for i in range(n)],
                       terre, [RNG.randrange(4) for _ in range(n)])


def bac(x, y, angle, nom):
    pieces = []
    for bx in (-.85,.85):
        for by in (-.45,.45):
            pieces.append(bloc("Patin du bac", (bx,by,.12), (.28,.25,.26), pierre[0], .043))
    pieces.append(bloc("Terre sous les crevasses", (0,0,.322), (1.94,1.14,.26), terre[4], .025))
    for i in range(2):
        z = .24 + i * .235
        for by in (-.64,.64):
            pieces.append(bloc("Planche du bac", (0,by,z), (2.10,.15,.217), bois[(i+1)%4], .024))
        for bx in (-1.00,1.00):
            pieces.append(bloc("Joue du bac", (bx,0,z), (.17,1.17,.217), bois[i], .025))
    for bx in (-.96,.96):
        for by in (-.65,.65):
            pieces.append(bloc("Ferrure d’angle", (bx,by,.352), (.17,.18,.45), fonte, .018))
    pieces.extend(mottes_de_terre())
    groupe = regrouper(nom, pieces)
    groupe.matrix_world = Matrix.Translation((x,y,.065)) @ Matrix.Rotation(angle,4,"Z")
    return groupe


bacs = [bac(1.70,.06,.12,"BacOuest"),bac(4.36,-.05,-.14,"BacEst"),bac(4.91,1.83,.22,"BacDuFond")]

pieces = [
    tube("Cuve de l’arrosoir", [(0,0,.025),(0,0,.095),(0,0,.42),(0,0,.50)], [.23,.28,.25,.20], [patine],10),
    tube("Jonc de pied", [(0,0,.035),(0,0,.082)], [.249,.257], [bronze],10),
    tube("Col", [(0,0,.49),(0,0,.56)], [.105,.105], [bronze],10),
    tube("Fond de l’ouverture", [(0,0,.555),(0,0,.561)], [.076,.076], [fonte],10),
    tube("Bec", [(.20,0,.18),(.35,0,.23),(.53,0,.34),(.65,0,.47)], [.085,.069,.048,.043], [patine],8),
    tube("Pomme percée", [(.63,0,.435),(.73,0,.52),(.777,0,.56)], [.042,.074,.092], [bronze],10),
    tube("Poignée cintrée", [(-.09,0,.49),(-.20,0,.67),(-.39,0,.68),
          (-.46,0,.52),(-.40,0,.32),(-.25,0,.23)], [.039]*6, [patine],8),
]
arrosoir = regrouper("Arrosoir", pieces)
arrosoir.matrix_world = Matrix.Translation((2.91,-.65,.079)) @ Matrix.Rotation(-.38,4,"Z")

pieces = []
for i in range(12):
    x = -.98 + i*.48
    y = -.63 + .26*sin(i*.53)
    pieces.append(bloc("Dalle éparse", (x,y,.105), (RNG.uniform(.41,.59),RNG.uniform(.44,.74),.13),
                       RNG.choice(pierre), .055,RNG.uniform(-.25,.25)))
for i in range(7):
    x = 1.31+i*.76
    pieces.append(bloc("Pierre de bordure", (x,2.83+.08*sin(i),.115), (.68,.39,.32),
                       pierre[i%4], .075,RNG.uniform(-.09,.09)))
for i in range(22):
    x, y = RNG.uniform(.65,5.65), RNG.uniform(.55,2.65)
    if abs(x-ARBRE.x) < .43 and abs(y-ARBRE.y) < .43:
        continue
    for j in range(3):
        dx,dy=RNG.uniform(-.13,.13),RNG.uniform(-.11,.11)
        pts=[(x-.027,y,.086),(x+.031,y,.086),(x+dx,y+dy,.14+RNG.uniform(.03,.14))]
        pieces.append(maillage("Tige sèche",pts,[(0,1,2)],[RNG.choice(sec)]))
details = regrouper("DallesEtPierresDuJardin",pieces)

decor = [banc, arbre, *bacs, arrosoir, details]
bpy.ops.object.select_all(action="DESELECT")
for o in decor:
    o.select_set(True)
bpy.context.view_layer.objects.active = banc
bpy.ops.export_scene.gltf(filepath=str(MODELES/"jardin_iris.glb"),use_selection=True,export_apply=True)

avant = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(MODELES/"terrain_ile_02.glb"))
terrain = set(scene.objects)-avant
sommets, faces = [], []
for o in terrain:
    if "colonly" in o.name:
        o.hide_render = True
    if o.type == "MESH" and "-col" in o.name:
        faces.extend(tuple(i+len(sommets) for i in p.vertices) for p in o.data.polygons)
        sommets.extend(o.matrix_world @ v.co for v in o.data.vertices)
sol = BVHTree.FromPolygons(sommets, faces)
for o in [banc, arbre, *bacs, arrosoir]:
    p = ORIGINE + (ARBRE if o == arbre else o.location)
    contact, _, _, _ = sol.ray_cast(p+Vector((0,0,1.2)),(0,0,-1),1.6)
    assert contact and abs(p.z-contact.z) < .14, (o.name,p,contact)
for i in range(39):
    p = Vector((-17+i*.29, 7.8, 7))
    contact,n,_,_ = sol.ray_cast(p,(0,0,-1),3)
    assert contact and 5.56 < contact.z < 5.83 and n.z > .9, (p,contact)
regard = Vector((sin(ANGLE), -cos(ANGLE), 0))
oeil = ORIGINE + BANC + Vector((0,0,1.38))
for hauteur in (0, -.04, -.09):
    direction = Vector((regard.x,regard.y,hauteur))
    contact, _, _, _ = sol.ray_cast(oeil,direction,75)
    assert contact is None, (oeil,contact)
print("Contrôle : appuis du mobilier, 39 points de passage et trois rayons au cap 318°.")

for o in decor:
    o.matrix_world = Matrix.Translation(ORIGINE) @ o.matrix_world
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1200, 820
scene.world = bpy.data.worlds.new("Ciel marin")
scene.world.use_nodes = True
fond = scene.world.node_tree.nodes["Background"]
fond.inputs[0].default_value = (.38,.52,.71,1)
fond.inputs[1].default_value = .55
bpy.ops.object.light_add(type="SUN",rotation=(.55,-.56,-.55))
bpy.context.object.data.energy = 2.6
bpy.ops.mesh.primitive_plane_add(size=160,location=(0,0,-.18))
bpy.context.object.data.materials.append(mat("Mer", "729BA4", .35))
bpy.ops.object.camera_add()
scene.camera = bpy.context.object
scene.camera.data.type = "ORTHO"
CAPTURES.mkdir(parents=True,exist_ok=True)
for fichier, cible, recul, echelle in (
    ("01_jardin_sur_ile", (-10.15,11.1,6.15),(9,-9,15.3),13.3),
    ("02_arbre_et_bacs", (-8.78,11.80,6.61),(6,-9,5.3),6.9),
    ("03_banc_iris", (-13.02,12.38,6.26),(-4,4.5,4.2),5.6),
):
    cible = Vector(cible)
    scene.camera.location = cible+Vector(recul)
    scene.camera.rotation_euler = (cible-scene.camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera.data.ortho_scale = echelle
    scene.render.filepath = str(CAPTURES/f"{fichier}.png")
    bpy.ops.render.render(write_still=True)
