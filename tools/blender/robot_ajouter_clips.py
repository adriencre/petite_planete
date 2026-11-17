"""Ajoute des clips Meshy au robot jouable (assets/models/robot_meshy.glb) sans toucher aux autres.

Le robot garde son maillage, son squelette et ses animations (attente, marche, course, brancher...).
Chaque fichier de CLIPS est un .glb d'animation Meshy (même squelette) ; ses actions sont renommées
selon NOMS (dans l'ordre où Meshy les a générées), puis tout est réexporté avec une piste NLA par clip.

Lancer :  blender -b --factory-startup --python tools/blender/robot_ajouter_clips.py
"""
import bpy, os, re

try:
    RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    RACINE = r"C:\Users\adrie\OneDrive\Bureau\petite-planete-v5"
ROBOT = os.path.join(RACINE, "assets", "models", "robot_meshy.glb")
SOURCES = os.path.join(RACINE, "tools", "blender", "sources", "meshy", "robot_rig")
# fichier Meshy -> {nom du clip chez Meshy : nom dans le jeu}
CLIPS = {
    "robot_reveil.glb": {"Sleep_Normally": "dormir", "Wake_Up_and_Look_Up": "reveil", "Stand_Up1": "se_lever",
                         "Look_Around_Dumbfounded": "regarder_autour", "Stand_To_Side_Lying": "effondrement"},
    "robot_recharger.glb": {"Formal_Bow": "recharger"},
    "robot_assis.glb": {"Chair_Sit_Idle_M": "assis"},
    "robot_ramer.glb": {"*": "ramer"},   # généré par text-to-motion : un seul clip, nom quelconque
}
HEURISTIQUE = "BLENDER"   # le même pour tous les imports, sinon les os ne s'alignent pas

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 30


def importer(chemin):
    avant_obj, avant_act = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=chemin, bone_heuristic=HEURISTIQUE)
    objs = [o for o in bpy.data.objects if o not in avant_obj]
    acts = [a for a in bpy.data.actions if a not in avant_act]
    return objs, acts


objs, gardees = importer(ROBOT)
arm = next(o for o in objs if o.type == "ARMATURE")
print("ROBOT", arm.name, "actions :", [a.name for a in gardees])

nouvelles = []
for fichier, noms in CLIPS.items():
    o2, acts = importer(os.path.join(SOURCES, fichier))
    arm2 = next(o for o in o2 if o.type == "ARMATURE")
    # le squelette doit être identique (mêmes os, même repos), sinon les clips seraient tordus
    ecart = max((arm.data.bones[b.name].matrix_local - b.matrix_local).to_translation().length
                + sum(abs(x) for x in (arm.data.bones[b.name].matrix_local.to_quaternion().rotation_difference(
                    b.matrix_local.to_quaternion())).to_euler())
                for b in arm2.data.bones)
    print(f"{fichier} : {len(acts)} actions {[a.name for a in acts]} ; écart de squelette {ecart:.5f}")
    assert ecart < 1e-2, "squelette différent : il faudrait recibler les clips"
    for a in acts:
        nom = next((v for k, v in noms.items() if k == "*" or a.name == k or k in a.name.split("|")), None)
        if nom is None or nom in {g.name for g in gardees}:
            continue
        a.name = nom
        a.use_fake_user = True
        nouvelles.append(a)
    manquants = set(noms.values()) - {a.name for a in nouvelles} - {g.name for g in gardees}
    assert not manquants, f"clips introuvables : {manquants}"
    for o in o2:
        bpy.data.objects.remove(o, do_unlink=True)

# une piste NLA par clip sur le robot, rien d'actif
ad = arm.animation_data or arm.animation_data_create()
ad.action = None
for t in list(ad.nla_tracks):
    ad.nla_tracks.remove(t)
for a in gardees + nouvelles:
    t = ad.nla_tracks.new()
    t.name = a.name
    s = t.strips.new(a.name, int(a.frame_range[0]), a)
    if hasattr(s, "action_slot") and getattr(a, "slots", None) and len(a.slots):
        s.action_slot = a.slots[0]
    print(f"CLIP {a.name:20s} {a.frame_range[1] - a.frame_range[0]:6.1f} images = {(a.frame_range[1] - a.frame_range[0]) / 30:.1f} s")

bpy.ops.export_scene.gltf(filepath=ROBOT, export_format="GLB", export_animation_mode="NLA_TRACKS",
                          export_force_sampling=True, export_frame_range=False)
print("EXPORT", ROBOT, f"{os.path.getsize(ROBOT) / 1e6:.1f} Mo")
