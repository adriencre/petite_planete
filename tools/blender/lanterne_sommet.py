"""Lanterne du sommet (île 1) — découpe du modèle Meshy pour le jeu.

La forme et la texture de Meshy sont gardées. Le script
  1. importe, met à l'échelle (HAUTEUR, origine au pied), avant = -Y Blender (= +Z Godot) ;
  2. sépare le `Coeur` (la boule d'or, pour qu'elle brille), la `Cage` (cuivre vert-de-gris)
     et le reste (socle, côtes, poteau, câble) ;
  3. pose le repère `Prise` sur la prise de cuivre du socle ;
  4. exporte assets/models/lanterne_sommet.glb et rend une planche avec le robot.
Le jeu la pose à l'échelle 1,6 (comme la grande lanterne) : HAUTEUR × 1,6 ≈ 5 m.
Elle utilise scripts/lanterne_fleur.gd (pas de pétales : seuls le cœur et la prise comptent).

Lancer :  blender -b --factory-startup --python tools/blender/lanterne_sommet.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "lanterne_sommet_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "lanterne_sommet.blend")
GLB = os.path.join(RACINE, "assets", "models", "lanterne_sommet.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

HAUTEUR = 3.15         # m avant l'échelle 1,6 du jeu (≈ 5 m)
ECHELLE_JEU = 1.6

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=SOURCE)
src = next(o for o in sc.objects if o.type == "MESH")
for o in list(sc.objects):
    if o is not src:
        bpy.data.objects.remove(o)
src.parent = None
me = src.data
me.transform(src.matrix_world)
src.matrix_world = Matrix.Identity(4)
zs = [v.co.z for v in me.vertices]
me.transform(Matrix.Scale(HAUTEUR / (max(zs) - min(zs)), 4) @ Matrix.Translation((0, 0, -min(zs))))
me.update()
MAT = me.materials[0]
MAT.name = "lanterne_sommet"

bm = bmesh.new()
bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.faces.ensure_lookup_table()
pieces, vu = [], set()
for f in bm.faces:
    if f.index in vu:
        continue
    pile, grp = [f], []
    vu.add(f.index)
    while pile:
        g = pile.pop()
        grp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in vu:
                    vu.add(h.index)
                    pile.append(h)
    pieces.append(grp)
bm.faces.index_update()


def boite(faces):
    pts = [v.co for f in faces for v in f.verts]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


infos = [boite(g) for g in pieces]


def centre(k):
    return (infos[k][0] + infos[k][1]) / 2


def taille(k):
    return infos[k][1] - infos[k][0]


# la boule : pièce compacte (presque aussi large que haute), près de l'axe, entre 35 et 75 % de la hauteur
def score_boule(k):
    t, c = taille(k), centre(k)
    if not (0.35 * HAUTEUR < c.z < 0.75 * HAUTEUR) or math.hypot(c.x, c.y) > 0.06 * HAUTEUR:
        return -1
    if min(t) < 0.12 * HAUTEUR:
        return -1
    return min(t) / max(t)


boule = max(range(len(pieces)), key=score_boule)
assert score_boule(boule) > 0.6, "boule introuvable : le modèle source a changé ?"
C = centre(boule)
R = max(taille(boule)) * 0.5
# la cage : tout ce qui tient dans une sphère un peu plus grande que la boule (bandes, anneau, calottes)
cage = [k for k in range(len(pieces)) if k != boule
        and all((Vector(p) - C).length < R * 2.4 for p in (infos[k][0], infos[k][1]))]
y_avant = min(infos[k][0].y for k in range(len(pieces)))
prise = [k for k in range(len(pieces)) if infos[k][0].y < y_avant + 0.03 * HAUTEUR
         and infos[k][1].z < 0.2 * HAUTEUR and max(taille(k)) < 0.12 * HAUTEUR]
reste = [k for k in range(len(pieces)) if k != boule and k not in cage]
print(f"PIECES {len(pieces)} : boule {boule} (rayon {R:.2f} m, à {C.z:.2f} m), {len(cage)} de cage, {len(prise)} de prise, {len(reste)} du pied")


def extraire(nom, ks):
    idx = {f.index for k in ks for f in pieces[k]}
    b2 = bm.copy()
    b2.faces.ensure_lookup_table()
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.index not in idx], context="FACES")
    for f in b2.faces:
        f.smooth = False
    m = bpy.data.meshes.new(nom)
    b2.to_mesh(m)
    b2.free()
    m.materials.append(MAT)
    o = bpy.data.objects.new(nom, m)
    sc.collection.objects.link(o)
    return o


def vide(nom, taille_=0.15, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille_
    sc.collection.objects.link(o)
    return o


RACINE_OBJ = vide("LanterneSommet", 0.4, "PLAIN_AXES")
o_pied = extraire("pied", reste)
o_pied.parent = RACINE_OBJ
o_cage = extraire("Cage", cage)
o_cage.data.transform(Matrix.Translation(-C))
o_cage.location = C
o_cage.parent = RACINE_OBJ
o_coeur = extraire("Coeur", [boule])
o_coeur.data.transform(Matrix.Translation(-C))
o_coeur.location = C
o_coeur.parent = RACINE_OBJ
if prise:
    cp = sum((centre(k) for k in prise), Vector()) / len(prise)
else:
    cp = Vector((0, y_avant, 0.08 * HAUTEUR))
o_prise = vide("Prise", 0.1)
o_prise.location = cp
o_prise.parent = RACINE_OBJ
print(f"PRISE à {tuple(round(x, 3) for x in cp)} (× {ECHELLE_JEU} : à {cp.z * ECHELLE_JEU:.2f} m du sol) ; boule à {C.z * ECHELLE_JEU:.2f} m en jeu")

bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ planche : à l'échelle du jeu, avec le robot
RACINE_OBJ.scale = (ECHELLE_JEU,) * 3
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    arm = next(o for o in sc.objects if o not in avant and o.type == "ARMATURE")
    arm.location = (1.0, -2.6, 0.0)
except Exception as e:
    print("ROBOT non importé :", e)
bpy.ops.mesh.primitive_plane_add(size=40)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.5, 0.62, 0.36, 1)
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
cible = Vector((0.3, -1.0, 2.3))
a, e = math.radians(-70), math.radians(18)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 11.0
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1000, 1100
sc.render.filepath = os.path.join(CAPTURES, "lanterne_sommet_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
