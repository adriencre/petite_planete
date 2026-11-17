"""Grande lanterne (île 1, au centre du niveau 1) — découpe du modèle Meshy pour le jeu.

Même principe que tools/blender/lanterne_tulipe.py : la forme et la texture de Meshy sont gardées.
  1. import, mise à l'échelle (HAUTEUR, origine au pied), avant = -Y Blender (= +Z Godot) ;
  2. séparation en pièces : pétales (dix, sur deux rangs), cœur (le bouton au centre), pied ;
  3. un pivot `PetaleN` à la base de chaque pétale (X local = charnière) ;
  4. le repère `Prise` au centre de la prise de cuivre, sur la face avant du bassin ;
  5. export assets/models/lanterne_grande.glb + planche de test (fermée -> ouverte).
Le jeu la pose à l'échelle 1,6 (comme la tulipe) : HAUTEUR × 1,6 ≈ 4,5 m.
Noms attendus par scripts/lanterne_fleur.gd : `Petale*` (Node3D), `Coeur` (mesh), `Prise` (Node3D).

Lancer :  blender -b --factory-startup --python tools/blender/grande_lanterne.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "grande_lanterne_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "grande_lanterne.blend")
GLB = os.path.join(RACINE, "assets", "models", "lanterne_grande.glb")
CAPTURES = os.path.join(RACINE, "captures")

HAUTEUR = 2.8          # m avant l'échelle 1,6 du jeu
ANGLE_OUVERT = 1.15    # rad, la valeur de lanterne_fleur.gd (_ouvrir)
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
MAT.name = "lanterne_grande"

# ------------------------------------------------------------------ pièces
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
# la fleur : tout ce qui commence au-dessus de 65 % de la hauteur (au-dessus de la collerette)
fleur = [k for k in range(len(pieces)) if infos[k][0].z > 0.66 * HAUTEUR]
AXE = Vector((0, 0, 0))
for k in fleur:
    AXE += (infos[k][0] + infos[k][1]) / 2
AXE /= max(len(fleur), 1)
AXE.z = 0


def ecart_axe(k):
    c = (infos[k][0] + infos[k][1]) / 2
    return math.hypot(c.x - AXE.x, c.y - AXE.y)


coeur = [k for k in fleur if ecart_axe(k) < 0.04 * HAUTEUR]
petales = [k for k in fleur if k not in coeur]
# la prise : petites pièces collées à la face avant (-Y) du bassin, en bas
y_avant = min(infos[k][0].y for k in range(len(pieces)))
prise = [k for k in range(len(pieces)) if infos[k][0].y < y_avant + 0.03 * HAUTEUR
         and infos[k][1].z < 0.2 * HAUTEUR and max(infos[k][1] - infos[k][0]) < 0.12 * HAUTEUR]
pied = [k for k in range(len(pieces)) if k not in fleur]
print(f"PIECES {len(pieces)} : {len(petales)} pétales, {len(coeur)} du cœur, {len(prise)} de la prise, {len(pied)} du pied")
assert petales and coeur, "classement raté : le modèle source a changé ?"


def angle_de(k):
    c = (infos[k][0] + infos[k][1]) / 2 - AXE
    return math.atan2(c.y, c.x)


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


def vide(nom, taille=0.15, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille
    sc.collection.objects.link(o)
    return o


def recentrer(o, monde):
    o.data.transform(monde.inverted())
    o.matrix_world = monde


RACINE_OBJ = vide("LanterneGrande", 0.4, "PLAIN_AXES")
o_pied = extraire("pied", pied)
o_pied.parent = RACINE_OBJ
o_coeur = extraire("Coeur", coeur)
mn = Vector((min(infos[k][0].x for k in coeur), min(infos[k][0].y for k in coeur), min(infos[k][0].z for k in coeur)))
mx = Vector((max(infos[k][1].x for k in coeur), max(infos[k][1].y for k in coeur), max(infos[k][1].z for k in coeur)))
recentrer(o_coeur, Matrix.Translation((mn + mx) / 2))
o_coeur.parent = RACINE_OBJ

PIVOTS = []
for i, k in enumerate(sorted(petales, key=angle_de)):
    faces = pieces[k]
    mn, mx = infos[k]
    a = angle_de(k)
    seuil = mn.z + 0.06 * (mx.z - mn.z)
    bas = [v.co for f in faces for v in f.verts if v.co.z <= seuil]
    charniere = sum(bas, Vector()) / len(bas)
    piv = vide(f"Petale{i}")
    piv.matrix_world = Matrix.Translation(charniere) @ Matrix.Rotation(a - math.pi / 2, 4, "Z")
    piv.parent = RACINE_OBJ
    m = extraire(f"petale_mesh{i}", [k])
    recentrer(m, piv.matrix_world)
    m.parent = piv
    m.matrix_parent_inverse = Matrix.Identity(4)
    m.matrix_basis = Matrix.Identity(4)
    PIVOTS.append(piv)
    print(f"PETALE {i} : angle {math.degrees(a):+.0f}°, charnière à {charniere.z:.2f} m, longueur {mx.z - mn.z:.2f} m")

if prise:
    c = sum(((infos[k][0] + infos[k][1]) / 2 for k in prise), Vector()) / len(prise)
else:
    c = Vector((AXE.x, y_avant, 0.08 * HAUTEUR))
o_prise = vide("Prise", 0.1)
o_prise.location = c
o_prise.parent = RACINE_OBJ
print(f"PRISE à {tuple(round(x, 3) for x in c)} (× {ECHELLE_JEU} dans le jeu : à {c.z * ECHELLE_JEU:.2f} m du sol)")

bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ planche : fermée, mi-ouverte, ouverte
PAS = 2.2
for i, v in enumerate((0.0, 0.5, 1.0)):
    corr = {}
    for o in [RACINE_OBJ] + list(RACINE_OBJ.children_recursive):
        cp = o.copy()
        sc.collection.objects.link(cp)
        corr[o] = cp
    for o, cp in corr.items():
        if o.parent:
            cp.parent = corr[o.parent]
    corr[RACINE_OBJ].location.x = i * PAS
    for p in PIVOTS:
        corr[p].matrix_basis = corr[p].matrix_basis @ Matrix.Rotation(-ANGLE_OUVERT * v, 4, "X")
RACINE_OBJ.hide_render = True
for o in RACINE_OBJ.children_recursive:
    o.hide_render = True
soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.0
soleil.rotation_euler = (math.radians(55), 0, math.radians(-30))
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
cible = Vector((PAS, 0, HAUTEUR * 0.55))
a, e = math.radians(-80), math.radians(22)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 9.5
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1500, 800
sc.render.filepath = os.path.join(CAPTURES, "lanterne_grande_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
