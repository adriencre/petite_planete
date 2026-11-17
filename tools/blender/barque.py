"""Barque des Semeurs (île 1, crique ouest ; sert ensuite dans tout l'archipel) — découpe du modèle Meshy.

La forme et la texture de Meshy sont gardées. Le script
  1. importe, met à l'échelle (LONGUEUR), proue vers -Y Blender (= +Z Godot, l'avant du jeu) ;
  2. place l'origine sur la ligne de flottaison (FLOTTAISON de la hauteur de la coque) : posée à y = 0
     dans le jeu, elle est à flot sur la mer ;
  3. sépare la `Coque` et la `Lanterne` (cage + cristal, à la proue) ; les rames de Meshy sont retirées
     (la barque avance à la lumière : le robot branche son câble dans la `Prise`) ;
  4. pose les repères `Siege` (le banc où le robot s'assoit) et `Prise` (à sa droite, sur le bord) ;
  5. exporte assets/models/barque.glb et rend une planche avec le robot.

Lancer :  blender -b --factory-startup --python tools/blender/barque.py
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
SOURCE = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "barque_meshy.glb")
BLEND = os.path.join(RACINE, "tools", "blender", "sources", "barque.blend")
GLB = os.path.join(RACINE, "assets", "models", "barque.glb")
CAPTURES = os.path.join(RACINE, "captures")
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")

LONGUEUR = 3.8      # m, de la poupe au bout de la lanterne
FLOTTAISON = 0.35   # part de la hauteur de coque sous l'eau

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
xs = [v.co.x for v in me.vertices]
# chez Meshy la proue est vers +X : on la tourne vers -Y
me.transform(Matrix.Rotation(-math.pi / 2, 4, "Z") @ Matrix.Scale(LONGUEUR / (max(xs) - min(xs)), 4))
me.update()
MAT = me.materials[0]
MAT.name = "barque"

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
mn_all = Vector((min(i[0].x for i in infos), min(i[0].y for i in infos), min(i[0].z for i in infos)))
mx_all = Vector((max(i[1].x for i in infos), max(i[1].y for i in infos), max(i[1].z for i in infos)))
L = mx_all.y - mn_all.y
# les rames : longues pièces fines qui dépassent sur les côtés (le long de X après la rotation)
rames = [k for k in range(len(pieces)) if infos[k][1].x - infos[k][0].x > 0.22 * L and infos[k][1].y - infos[k][0].y < 0.15 * L
         and max(abs(infos[k][0].x), abs(infos[k][1].x)) > 0.3 * L]
# la coque : la plus grosse pièce hors rames ; sa largeur sert de repère
coque = max((k for k in range(len(pieces)) if k not in rames), key=lambda k: len(pieces[k]))
demi_larg = max(abs(infos[k][1].x) for k in range(len(pieces)) if k not in rames and infos[k][1].z < mx_all.z * 0.9)
# la lanterne : tout ce qui est au-delà de la proue (y très négatif), sous la crosse en spirale
y_proue = mn_all.y + 0.1 * L
lanterne = [k for k in range(len(pieces)) if k not in rames and infos[k][1].y < y_proue + 0.04 * L and k != coque]
reste = [k for k in range(len(pieces)) if k not in rames and k not in lanterne]
print(f"PIECES {len(pieces)} : {len(rames)} rames, {len(lanterne)} de lanterne, {len(reste)} de coque ; longueur {L:.2f} m")
assert len(rames) == 2 and lanterne, "classement raté : le modèle source a changé ?"

# ligne de flottaison : FLOTTAISON de la hauteur de la coque (sans la crosse ni la lanterne)
z_fond = infos[coque][0].z
z_bord = sorted(i[1].z for k, i in enumerate(infos) if k in reste)[len(reste) // 2]
z_eau = z_fond + FLOTTAISON * (z_bord - z_fond)
cx = (mn_all.x + mx_all.x) / 2
cy = (mn_all.y + mx_all.y) / 2
bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((-cx, -cy, -z_eau)))
infos = [boite(g) for g in pieces]
print(f"FLOTTAISON : fond à {-(z_eau - z_fond):.2f} m sous l'eau")


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


def vide(nom, taille=0.2, forme="ARROWS"):
    o = bpy.data.objects.new(nom, None)
    o.empty_display_type, o.empty_display_size = forme, taille
    sc.collection.objects.link(o)
    return o


def recentrer(o, monde):
    o.data.transform(monde.inverted())
    o.matrix_world = monde


BARQUE = vide("Barque", 0.5, "PLAIN_AXES")
extraire("Coque", reste).parent = BARQUE
lant = extraire("Lanterne", lanterne)
mn = Vector((min(infos[k][0].x for k in lanterne), min(infos[k][0].y for k in lanterne), min(infos[k][0].z for k in lanterne)))
mx = Vector((max(infos[k][1].x for k in lanterne), max(infos[k][1].y for k in lanterne), max(infos[k][1].z for k in lanterne)))
recentrer(lant, Matrix.Translation((mn + mx) / 2))
lant.parent = BARQUE
siege = vide("Siege", 0.2)
siege.location = (0, 0.15 * L, infos[coque][0].z + 0.45 * (z_bord - z_fond))
siege.parent = BARQUE
# la prise : sur le bord intérieur, à droite du robot assis (il regarde la proue, vers -Y)
prise = vide("Prise", 0.1)
prise.location = (-(demi_larg - 0.12), 0.15 * L - 0.35, siege.location.z + 0.05)
prise.parent = BARQUE
bm.free()
bpy.data.objects.remove(src)
bpy.data.meshes.remove(me)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB", use_active_scene=True)
print("EXPORT", GLB, f"{os.path.getsize(GLB) / 1e6:.1f} Mo")

# ------------------------------------------------------------------ planche : sur l'eau, robot sur le quai
try:
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=ROBOT)
    arm = next(o for o in sc.objects if o not in avant and o.type == "ARMATURE")
    arm.location = (1.9, 0.3, 0.0)
except Exception as e:
    print("ROBOT non importé :", e)
bpy.ops.mesh.primitive_plane_add(size=40)
eau = bpy.context.object
me_eau = bpy.data.materials.new("eau")
me_eau.use_nodes = True
b = next(n for n in me_eau.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.25, 0.65, 0.7, 1)
b.inputs["Alpha"].default_value = 0.75
me_eau.blend_method = "BLEND" if hasattr(me_eau, "blend_method") else None
eau.data.materials.append(me_eau)
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
cible = Vector((0.6, 0, 0.5))
a, e = math.radians(-35), math.radians(28)
cam.location = cible + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * 8.0
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.render.filepath = os.path.join(CAPTURES, "barque_planche.png")
bpy.ops.render.render(write_still=True)
print("RENDU", sc.render.filepath)
