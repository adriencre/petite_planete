"""Berceau (île 1, dans l'abri) — nettoyage du modèle Meshy.

On ne remodélise rien : la forme et la texture de Meshy sont gardées. Le script
  1. importe le .glb de Meshy (pièces non soudées : coque, matelas, lampe, câble...),
  2. le met à l'échelle (LONGUEUR), posé sur z = 0, l'encoche de sortie vers -Y Blender (= +Z Godot),
  3. retire le câble de Meshy (il fait le tour du berceau) et la prise du pied : le berceau n'a
     qu'une ligne, à la tête, et le jeu tire son câble jusqu'au mur,
  4. détache la `Lampe` (cristal + cage) pour pouvoir l'allumer au réveil,
  5. pose les repères `Couche` (milieu du matelas), `Tete` (oreiller) et `Prise` (départ du câble),
  6. enregistre un .blend, exporte assets/models/berceau.glb et rend une planche de test.

Lancer :  blender -b --factory-startup --python tools/blender/berceau.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "berceau_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "berceau.blend")
GLB = os.path.join(RACINE, "assets", "models", "berceau.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

LONGUEUR = 2.3   # m, longueur de la coque (le robot fait ~1,90 m)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = "Berceau"

# ------------------------------------------------------------------ 1. import + échelle
bpy.ops.import_scene.gltf(filepath=SOURCE)
src = next(o for o in sc.objects if o.type == "MESH")
for o in list(sc.objects):
    if o is not src:
        bpy.data.objects.remove(o)
src.parent = None
me = src.data
me.transform(src.matrix_world)
src.matrix_world = Matrix.Identity(4)
xs = [v.co.x for v in me.vertices]
zs = [v.co.z for v in me.vertices]
ech = LONGUEUR / (max(xs) - min(xs))
# demi-tour : chez Meshy l'encoche est vers +Y et la tête vers +X
me.transform(Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(ech, 4) @ Matrix.Translation((0, 0, -min(zs))))
me.update()
MAT = me.materials[0]
MAT.name = "berceau"

# ------------------------------------------------------------------ 2. pièces
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


def boite(faces):
    pts = [v.co for f in faces for v in f.verts]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


infos = [boite(g) for g in pieces]
# la coque : la pièce de plus grande surface (le câble a plus de faces, mais c'est un tube fin)
coque = max(range(len(pieces)), key=lambda k: sum(f.calc_area() for f in pieces[k]))
# l'échelle se règle sur la coque seule (le câble de Meshy dépasse aux deux bouts)
k_ech = LONGUEUR / (infos[coque][1].x - infos[coque][0].x)
bmesh.ops.scale(bm, vec=(k_ech, k_ech, k_ech), verts=bm.verts)
infos = [boite(g) for g in pieces]
mnC, mxC = infos[coque]
H = mxC.z                      # hauteur du bord de la coque
tete_x = mnC.x                 # après le demi-tour, la tête est vers -X


def taille(k):
    return infos[k][1] - infos[k][0]


# le câble de Meshy : la pièce fine qui fait le tour (aussi longue que la coque, large, basse)
cable = [k for k in range(len(pieces)) if k != coque and taille(k).x > 0.6 * LONGUEUR and taille(k).z > 0.25 * H]
# tout ce qui est accroché au pied (prise + bout de câble), au-delà de la coque côté +X
pied = [k for k in range(len(pieces)) if k not in cable and k != coque and infos[k][0].x > mxC.x - 0.45 and taille(k).y < 0.15
        and infos[k][1].x > mxC.x - 0.12 and taille(k).z < 0.5]
# la lampe : les petites pièces en hauteur, au-dessus du bord (cage, cristal), sans la tige
lampe = [k for k in range(len(pieces)) if infos[k][0].z > H + 0.08 and taille(k).z < 0.4]
# la prise de la tête : petite pièce au bout -X, à mi-hauteur
prise = [k for k in range(len(pieces)) if infos[k][0].x < tete_x + 0.08 and max(taille(k)) < 0.2 and k not in lampe]
matelas = [k for k in range(len(pieces)) if k not in (cable + pied + lampe + prise) and k != coque
           and taille(k).x > 0.5 * LONGUEUR and taille(k).z < 0.1 and infos[k][1].z < H]
print(f"PIECES {len(pieces)} ; coque {len(pieces[coque])} faces ; câble {cable} ; pied {pied} ; lampe {lampe} ; prise {prise} ; matelas {matelas}")
print(f"TAILLE {mxC.x - mnC.x:.2f} x {mxC.y - mnC.y:.2f} m, bord à {H:.2f} m")
assert cable and lampe, "classement raté : le modèle source a changé ?"


def extraire(nom, ks):
    garder = {f for k in ks for f in pieces[k]}
    b2 = bm.copy()
    b2.faces.ensure_lookup_table()
    idx = {f.index for f in garder}
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


def vide(nom, pos, taille_=0.2, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille_
    o.location = pos
    sc.collection.objects.link(o)
    return o


bm.faces.index_update()
BERCEAU = vide("Berceau", (0, 0, 0), 0.5, "PLAIN_AXES")
corps_k = [k for k in range(len(pieces)) if k not in cable + pied + lampe]
o_corps = extraire("Corps", corps_k)
o_corps.parent = BERCEAU
o_lampe = extraire("Lampe", lampe)
mnL = Vector((min(infos[k][0].x for k in lampe), min(infos[k][0].y for k in lampe), min(infos[k][0].z for k in lampe)))
mxL = Vector((max(infos[k][1].x for k in lampe), max(infos[k][1].y for k in lampe), max(infos[k][1].z for k in lampe)))
centre_l = (mnL + mxL) / 2
o_lampe.data.transform(Matrix.Translation(-centre_l))
o_lampe.location = centre_l
o_lampe.parent = BERCEAU

z_couche = max(infos[k][1].z for k in matelas) if matelas else H * 0.7
p_couche = vide("Couche", ((mnC.x + mxC.x) / 2, (mnC.y + mxC.y) / 2, z_couche))
p_tete = vide("Tete", (mnC.x + 0.45, (mnC.y + mxC.y) / 2, z_couche))
if prise:
    c = sum(((infos[k][0] + infos[k][1]) / 2 for k in prise), Vector()) / len(prise)
else:
    c = Vector((mnC.x, (mnC.y + mxC.y) / 2, H * 0.6))
p_prise = vide("Prise", c)
for o in (p_couche, p_tete, p_prise):
    o.parent = BERCEAU
print(f"COUCHE à z = {z_couche:.2f} m ; lampe à {tuple(round(x, 2) for x in centre_l)} ; prise à {tuple(round(x, 2) for x in c)}")

bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)

# ------------------------------------------------------------------ 3. .blend + .glb
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ 4. planche de test
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    neufs = [o for o in sc.objects if o not in avant]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in neufs if o.type == "MESH" for c in o.bound_box]
    zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
    xm = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    ym = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    piv = vide("robot_echelle", (0, 0, 0), 0.2, "PLAIN_AXES")
    for o in neufs:
        if o.parent is None:
            o.parent = piv
    k = 1.9 / (zmax - zmin)
    piv.matrix_world = Matrix.Translation((0.3, -1.5, 0)) @ Matrix.Scale(k, 4) @ Matrix.Translation((-xm, -ym, -zmin))
except Exception as e:
    print("ROBOT non importé :", e)

bpy.ops.mesh.primitive_plane_add(size=40)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.75, 0.7, 0.6, 1)
sol.data.materials.append(ms)
soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.0
soleil.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.collection.objects.link(soleil)
monde = bpy.data.worlds.new("monde")
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.68, 0.78, 1)
monde.node_tree.nodes["Background"].inputs[1].default_value = 1.0
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


def photo(nom, cible, dist, azimut, elevation, taille_px, focale=50):
    cam.data.lens = focale
    a, e = math.radians(azimut), math.radians(elevation)
    cible = Vector(cible)
    cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = taille_px
    sc.render.filepath = os.path.join(CAPTURES, nom)
    bpy.ops.render.render(write_still=True)
    print("RENDU", sc.render.filepath)


photo("berceau_planche.png", (0, -0.4, 0.6), 7.5, -70, 35, (1400, 1000), 50)
