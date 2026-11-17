"""Lanterne-tulipe — découpe du modèle Meshy « Flower Lantern 3D » pour le jeu.

On ne remodélise rien : la forme et la texture de Meshy sont gardées telles quelles. Le script
  1. importe le .glb de Meshy (un seul maillage fusionné),
  2. le met à l'échelle (HAUTEUR, origine au pied),
  3. le sépare en morceaux non soudés et les classe : pétales extérieurs, cœur (bouton doré), pied,
  4. pose un pivot `PetaleN` à la base de chaque pétale (X local = charnière, comme lanterne_fleur),
  5. pose le repère `Prise` sur la prise peinte du socle (avant = -Y Blender = +Z Godot),
  6. enregistre un .blend, exporte un .glb et rend une planche de test (fermée -> ouverte).

Lancer (Blender à part, sans toucher à la session ouverte) :
  blender -b --factory-startup --python tools/blender/lanterne_tulipe.py
Noms attendus par scripts/lanterne_fleur.gd : `Petale*` (Node3D), `Coeur` (mesh), `Prise` (Node3D).
"""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy",
                      "Meshy_AI_Flower_Lantern_3D_1116164355_texture.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "lanterne_tulipe.blend")
GLB = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "lanterne_tulipe_test.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_final.glb")

HAUTEUR = 1.8          # m, comme la lanterne-fleur actuelle (robot ~1,90 m)
ANGLE_OUVERT = 1.15    # rad, la valeur de lanterne_fleur.gd (_ouvrir)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.name = "LanterneTulipe"

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
zs = [v.co.z for v in me.vertices]
ech = HAUTEUR / (max(zs) - min(zs))
me.transform(Matrix.Scale(ech, 4) @ Matrix.Translation((0, 0, -min(zs))))
me.update()
MAT = me.materials[0]
MAT.name = "lanterne_tulipe"


# ------------------------------------------------------------------ 2. morceaux non soudés
def morceaux(mesh):
    """Listes d'indices de faces, un groupe par morceau (les coutures d'UV sont recollées)."""
    par = list(range(len(mesh.vertices)))

    def racine(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    vu = {}
    for v in mesh.vertices:
        k = (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4))
        if k in vu:
            par[racine(v.index)] = racine(vu[k])
        else:
            vu[k] = v.index
    for e in mesh.edges:
        a, b = racine(e.vertices[0]), racine(e.vertices[1])
        if a != b:
            par[b] = a
    g = {}
    for p in mesh.polygons:
        g.setdefault(racine(p.vertices[0]), []).append(p.index)
    return list(g.values())


def boite(faces):
    pts = [me.vertices[i].co for f in faces for i in me.polygons[f].vertices]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


groupes = morceaux(me)
ext, coeur, pied = [], [], []      # listes de groupes de faces
for faces in groupes:
    mn, mx = boite(faces)
    bas, haut = mn.z / HAUTEUR, mx.z / HAUTEUR
    if haut > 0.97 and bas > 0.74:
        ext.append(faces)           # coque de pétale extérieur (monte jusqu'en haut)
    elif 0.90 < haut <= 0.97 and bas > 0.70:
        coeur.append(faces)         # bouton doré intérieur
    else:
        pied.append(faces)          # socle, tige, feuilles, calice, câble
print(f"MORCEAUX {len(groupes)} : {len(ext)} coques de pétale, {len(coeur)} du cœur, {len(pied)} du pied")
assert ext and coeur, "classement raté : le modèle source a changé ?"

# axe de la fleur = centre du cœur
mn, mx = boite([f for g in coeur for f in g])
AXE = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, 0))


def angle_de(faces):
    mn, mx = boite(faces)
    c = (mn + mx) / 2 - AXE
    return math.atan2(c.y, c.x)


# les coques d'un même pétale sont voisines en angle : on coupe aux grands trous
ext.sort(key=angle_de)
angles = [angle_de(g) for g in ext]
trous = [((angles[(i + 1) % len(ext)] - angles[i]) % math.tau, i) for i in range(len(ext))]
depart = (max(trous)[1] + 1) % len(ext)
ext = ext[depart:] + ext[:depart]
petales = [[ext[0]]]
for a, b in zip(ext, ext[1:]):
    if (angle_de(b) - angle_de(a)) % math.tau > math.radians(45):
        petales.append([])
    petales[-1].append(b)
petales = [[f for g in p for f in g] for p in petales]
print(f"PETALES {len(petales)} : angles {[round(math.degrees(angle_de(p))) for p in petales]}")


# ------------------------------------------------------------------ 3. objets
def extraire(nom, faces):
    garder = set(faces)
    m = me.copy()
    m.name = nom
    bm = bmesh.new()
    bm.from_mesh(m)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in garder], context="FACES")
    bm.to_mesh(m)
    bm.free()
    o = bpy.data.objects.new(nom, m)
    sc.collection.objects.link(o)
    return o


def vide(nom, taille=0.15, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille
    sc.collection.objects.link(o)
    return o


def recentrer(o, monde):
    """Donne à `o` la matrice `monde` sans déplacer sa géométrie."""
    o.data.transform(monde.inverted())
    o.matrix_world = monde


RACINE_OBJ = vide("LanterneTulipe", 0.4, "PLAIN_AXES")
o_pied = extraire("pied", [f for g in pied for f in g])
o_pied.parent = RACINE_OBJ

o_coeur = extraire("Coeur", [f for g in coeur for f in g])
mn, mx = boite([f for g in coeur for f in g])
recentrer(o_coeur, Matrix.Translation((mn + mx) / 2))   # grossit autour de son centre
o_coeur.parent = RACINE_OBJ

PIVOTS = []
for k, faces in enumerate(petales):
    mn, mx = boite(faces)
    a = angle_de(faces)
    # charnière : le bas du pétale (les 6 % les plus bas)
    seuil = mn.z + 0.06 * (mx.z - mn.z)
    bas = [me.vertices[i].co for f in faces for i in me.polygons[f].vertices if me.vertices[i].co.z <= seuil]
    charniere = sum(bas, Vector()) / len(bas)
    piv = vide(f"Petale{k}")
    # X local = charnière (tangente), tourner de -angle autour de X ouvre vers l'extérieur
    piv.matrix_world = Matrix.Translation(charniere) @ Matrix.Rotation(a - math.pi / 2, 4, "Z")
    piv.parent = RACINE_OBJ
    m = extraire(f"petale_mesh{k}", faces)
    recentrer(m, piv.matrix_world)
    m.parent = piv
    m.matrix_parent_inverse = Matrix.Identity(4)
    m.matrix_basis = Matrix.Identity(4)
    PIVOTS.append(piv)
    print(f"PETALE {k} : angle {math.degrees(a):+.0f}°, charnière {tuple(round(c, 3) for c in charniere)}, "
          f"longueur {mx.z - mn.z:.2f} m, {len(faces)} faces")


# ------------------------------------------------------------------ 4. la prise (peinte sur le socle)
def trouver_prise():
    """Cherche les pixels cuivre sur la face avant (-Y) du socle ; renvoie leur centre en 3D."""
    img = next((n.image for n in MAT.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
    socle = [f for g in pied for f in g if boite(g)[1].z < 0.25 * HAUTEUR]
    if img is None or not socle:
        return None
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    uv = me.uv_layers.active.data
    pts = []
    for f in socle:
        p = me.polygons[f]
        if p.normal.y > -0.9 or len(p.loop_indices) != 3:
            continue
        co = [me.vertices[i].co for i in p.vertices]
        tx = [uv[i].uv for i in p.loop_indices]
        n = 24
        for i in range(n + 1):
            for j in range(n + 1 - i):
                b0, b1 = i / n, j / n
                b2 = 1 - b0 - b1
                u = tx[0] * b0 + tx[1] * b1 + tx[2] * b2
                r, g, b, _ = px[min(h - 1, int(u.y % 1 * h)), min(w - 1, int(u.x % 1 * w))]
                if r - b > 0.22 and r > g * 1.25:      # cuivre, pas pierre
                    pts.append(co[0] * b0 + co[1] * b1 + co[2] * b2)
    if len(pts) < 20:
        return None
    return sum(pts, Vector()) / len(pts), len(pts)


trouve = trouver_prise()
if trouve:
    pos_prise, n = trouve
    print(f"PRISE trouvée par la texture ({n} points) : {tuple(round(c, 3) for c in pos_prise)}")
else:
    mn, mx = boite([f for g in pied for f in g])
    pos_prise = Vector((AXE.x, mn.y, 0.05))
    print(f"PRISE estimée (texture non concluante) : {tuple(round(c, 3) for c in pos_prise)}")
o_prise = vide("Prise", 0.1)
o_prise.location = pos_prise
o_prise.parent = RACINE_OBJ

# ------------------------------------------------------------------ 5. .blend + .glb
bpy.data.meshes.remove(me)   # le maillage fusionné d'origine n'est plus utile
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")


# ------------------------------------------------------------------ 6. planche de test
def ouvrir(pivots, v):
    for p in pivots:
        p.matrix_basis = p.matrix_basis @ Matrix.Rotation(-ANGLE_OUVERT * v, 4, "X")


def copie(dx, v, allume=False):
    """Une copie de la lanterne décalée de dx, ouverte à v (0 fermée, 1 ouverte)."""
    corr = {}
    for o in [RACINE_OBJ] + list(RACINE_OBJ.children_recursive):
        c = o.copy()
        sc.collection.objects.link(c)
        corr[o] = c
    for o, c in corr.items():
        if o.parent:
            c.parent = corr[o.parent]
    corr[RACINE_OBJ].location.x = dx
    ouvrir([corr[p] for p in PIVOTS], v)
    if allume:   # ce que fait le script du jeu : cœur doré lumineux, grossi x1,5
        c = corr[o_coeur]
        c.data = c.data.copy()
        c.data.materials.clear()
        c.data.materials.append(MAT_ALLUME)
        c.scale = (1.5, 1.5, 1.5)
        lum = bpy.data.lights.new("lueur", "POINT")
        lum.color, lum.energy, lum.shadow_soft_size = (1.0, 0.78, 0.4), 12, 0.2
        ol = bpy.data.objects.new("lueur", lum)
        sc.collection.objects.link(ol)
        ol.location = c.matrix_world.translation + Vector((dx, 0, 0.1))
    return corr


MAT_ALLUME = bpy.data.materials.new("coeur_allume")
MAT_ALLUME.use_nodes = True
_b = next(n for n in MAT_ALLUME.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_b.inputs["Base Color"].default_value = (1.0, 0.85, 0.5, 1)
_b.inputs["Emission Color"].default_value = (1.0, 0.57, 0.13, 1)
_b.inputs["Emission Strength"].default_value = 1.2

RACINE_OBJ.hide_render = True
for o in RACINE_OBJ.children_recursive:
    o.hide_render = True
PAS = 1.35
etats = [(0.0, False), (1 / 3, False), (2 / 3, False), (1.0, False), (1.0, True)]
copies = [copie(i * PAS, v, al) for i, (v, al) in enumerate(etats)]
for c in copies:
    for o in c.values():
        o.hide_render = False

# le robot, pour l'échelle
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    robot = [o for o in sc.objects if o not in avant]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in robot if o.type == "MESH" for c in o.bound_box]
    zmin, zmax = min(p.z for p in pts), max(p.z for p in pts)
    xm = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    print(f"ROBOT hauteur importée {zmax - zmin:.2f} m")
    tetes = [o for o in robot if o.parent is None]
    piv = vide("robot_echelle", 0.2, "PLAIN_AXES")
    for o in tetes:
        o.parent = piv
    k = 1.9 / (zmax - zmin)
    piv.matrix_world = Matrix.Translation((-PAS - xm * k, 0, -zmin * k)) @ Matrix.Scale(k, 4)
except Exception as e:   # la planche reste utile sans le robot
    print("ROBOT non importé :", e)

# sol, lumière, caméra
bpy.ops.mesh.primitive_plane_add(size=40)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
next(n for n in ms.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.42, 0.40, 0.38, 1)
sol.data.materials.append(ms)
soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.0
soleil.rotation_euler = (math.radians(55), 0, math.radians(-30))
sc.collection.objects.link(soleil)
monde = bpy.data.worlds.new("monde")
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1)
monde.node_tree.nodes["Background"].inputs[1].default_value = 0.9
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
print("MOTEUR", sc.render.engine)
sc.view_settings.view_transform = "Standard"


def photo(nom, cible, dist, azimut, elevation, taille, focale=50):
    cam.data.lens = focale
    a, e = math.radians(azimut), math.radians(elevation)
    cible = Vector(cible)
    cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = taille
    sc.render.filepath = os.path.join(CAPTURES, nom)
    bpy.ops.render.render(write_still=True)
    print("RENDU", sc.render.filepath)


milieu = (len(etats) - 2) * PAS / 2   # le robot est à -PAS
photo("lanterne_tulipe_planche.png", (milieu, 0, 0.95), 16.0, -86, 5, (2000, 800), 60)
fleur_z = o_coeur.matrix_world.translation.z
photo("lanterne_tulipe_ouverte.png", (3 * PAS, 0, fleur_z), 2.2, -60, 38, (1000, 1000), 55)
photo("lanterne_tulipe_allumee.png", (4 * PAS, 0, fleur_z), 2.2, -60, 38, (1000, 1000), 55)
photo("lanterne_tulipe_fermee.png", (0, 0, fleur_z), 1.9, -90, 8, (1000, 1000), 55)
# la prise, avec une bille rouge sur le repère `Prise`
bille_m = bpy.data.materials.new("repere")
bille_m.use_nodes = True
_r = next(n for n in bille_m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_r.inputs["Base Color"].default_value = (1, 0, 0, 1)
_r.inputs["Emission Color"].default_value = (1, 0, 0, 1)
_r.inputs["Emission Strength"].default_value = 3.0
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=pos_prise + Vector((0, -0.01, 0)))
bpy.context.object.data.materials.append(bille_m)
photo("lanterne_tulipe_prise.png", (0, 0, 0.12), 1.3, -75, 12, (1000, 700), 55)
