"""Ancien corps de l'école (île 3) : le robot assis sur un petit banc devant la porte,
qui tient entre ses mains le dessin d'Aube déjà trouvé au Phare (la fenêtre à l'aube).

Même méthode que le corps assis de la galerie (chaussee_anciens_corps.py) : pose « assis »
du robot jouable, figée et sans squelette. La mousse est ajoutée dans Godot
(shaders/mousse_ancien.gdshader), sauf sur la feuille.

Lancer :  blender -b --factory-startup --python tools/blender/ancien_corps_ecole.py
"""
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

RACINE = Path(__file__).resolve().parents[2]
ROBOT = RACINE / "assets/models/robot_meshy.glb"
DESSIN = RACINE / "assets/affiches/dessin_aube_fenetre.png"
SORTIE = RACINE / "assets/models/ile03/ancien_corps_ecole.glb"
APERCU = RACINE / "concept/ile_03/ancien_corps_ecole.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def matiere(nom, hexa):
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    couleur = [((int(hexa[i:i+2], 16)/255 + .055)/1.055)**2.4 for i in (0, 2, 4)]
    surface = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    surface.inputs["Base Color"].default_value = (*couleur, 1)
    surface.inputs["Roughness"].default_value = .85
    return mat


def objet(nom, sommets, faces, mat, uv=None):
    mesh = bpy.data.meshes.new(nom)
    mesh.from_pydata(sommets, [], faces)
    if uv:
        couche = mesh.uv_layers.new(name="UVMap")
        for boucle in mesh.loops:
            couche.data[boucle.index].uv = uv[boucle.vertex_index]
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(nom, mesh)
    scene.collection.objects.link(obj)
    return obj


def pave(x, y, z, l, p, h):
    pts = [(x+a*l/2, y+b*p/2, z+c*h) for c in (0, 1) for a, b in ((-1,-1),(1,-1),(1,1),(-1,1))]
    faces = [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    return pts, faces


# 1. Le robot dans la pose assise, figé.
avant = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(ROBOT), bone_heuristic="BLENDER")
robot = list(set(scene.objects) - avant)
armature = next(o for o in robot if o.type == "ARMATURE")
ad = armature.animation_data
for piste in ad.nla_tracks:
    piste.mute = True
ad.action = bpy.data.actions["assis"]
ad.action_slot = ad.action.slots[0]
scene.frame_set(1)
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pieces = []
for o in robot:
    if o.type == "MESH" and o.parent == armature:
        mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        mesh.transform(Matrix.Translation((-0.124, 0, 0.029)) @ o.matrix_world)
        fige = bpy.data.objects.new("Ancien corps de l'ecole", mesh)
        scene.collection.objects.link(fige)
        pieces.append(fige)
for o in robot:
    bpy.data.objects.remove(o, do_unlink=True)

# 2. Petit banc d'écolier, à hauteur du robot (assise à 0,33 m comme à la galerie).
bois, chene = matiere("bois", "976E61"), matiere("chene", "BC8460")
sommets, faces = [], []
for x, y, z, l, p, h in [(-.3,.12,0,.07,.3,.29), (.3,.12,0,.07,.3,.29), (0,.12,.29,.78,.36,.05)]:
    pts, fs = pave(x, y, z, l, p, h)
    faces += [tuple(len(sommets)+i for i in f) for f in fs]
    sommets += pts
banc = objet("Petit banc", sommets[:-8], faces[:-6], bois)
dessus = objet("Assise du banc", sommets[-8:], [tuple(i-16 for i in f) for f in faces[-6:]], chene)
pieces += [banc, dessus]

# 3. La feuille entre les mains, inclinée vers le haut pour qu'on la voie de la caméra.
papier = bpy.data.materials.new("Dessin d'Aube")
papier.use_nodes = True
noeuds = papier.node_tree
image = noeuds.nodes.new("ShaderNodeTexImage")
image.image = bpy.data.images.load(str(DESSIN))
surface = next(n for n in noeuds.nodes if n.type == "BSDF_PRINCIPLED")
surface.inputs["Roughness"].default_value = .9
noeuds.links.new(image.outputs["Color"], surface.inputs["Base Color"])
papier.use_backface_culling = False
largeur, hauteur = .34, .245
haut, bas = (-.19, .53), (-.36, .40)  # (y, z) du bord haut et du bord bas
feuille = objet("Feuille", [(-largeur/2, *bas), (largeur/2, *bas), (largeur/2, *haut), (-largeur/2, *haut)],
                [(0, 1, 2, 3)], papier, uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
pieces.append(feuille)

bpy.ops.object.select_all(action="DESELECT")
for o in pieces:
    o.select_set(True)
bpy.context.view_layer.objects.active = pieces[0]
SORTIE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(SORTIE), use_selection=True, export_animations=False, export_apply=True)

# 4. Aperçu de contrôle, vu de trois quarts plongeant.
bpy.ops.object.camera_add(location=(1.1, -1.7, 1.6))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -.1, .5)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
bpy.ops.object.light_add(type="SUN", rotation=(.6, -.3, -.4))
bpy.context.object.data.energy = 3
scene.world = bpy.data.worlds.new("Fond")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.86, .94, 1, 1)
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.render.resolution_x, scene.render.resolution_y = 700, 700
scene.render.filepath = str(APERCU)
bpy.ops.render.render(write_still=True)
print("Ancien corps de l'école exporté :", SORTIE)
