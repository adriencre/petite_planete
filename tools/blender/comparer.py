# Rendus orthographiques du robot au cadrage exact des 3 vues de référence.
# À concaténer après helpers.py (utilise `sc`). Produit rendu_{face,profil,dos}.png dans DOSSIER.
import bpy, math
from mathutils import Vector

DOSSIER = r"C:\Users\adrie\AppData\Local\Temp\claude\b5f7239256edd7b0\9f49c985-6ebd-40c5-8dfe-cd5f837f6461\scratchpad"
# (pixel x de l'axe du robot, pixel y des pieds, mm par pixel) mesurés sur chaque référence
VUES = {
    "face": dict(cx=547, pieds=1493, mmpx=1.358, pos=Vector((0, -10, 0)), droite=Vector((1, 0, 0))),
    "profil": dict(cx=540, pieds=1459, mmpx=1.387, pos=Vector((-10, 0, 0)), droite=Vector((0, -1, 0))),
    "dos": dict(cx=557, pieds=1485, mmpx=1.356, pos=Vector((0, 10, 0)), droite=Vector((-1, 0, 0))),
}
W, H = 1152, 1536

for n in ("CmpCam", "CmpSun", "CmpFill"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
sun = bpy.data.objects.new("CmpSun", bpy.data.lights.new("CmpSun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.5; sun.data.color = (1.0, 0.92, 0.82); sun.rotation_euler = (0.7, 0.0, -0.5)
fill = bpy.data.objects.new("CmpFill", bpy.data.lights.new("CmpFill", "SUN")); sc.collection.objects.link(fill)
fill.data.energy = 1.5; fill.rotation_euler = (1.1, 0.0, 2.6)
cam = bpy.data.objects.new("CmpCam", bpy.data.cameras.new("CmpCam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.film_transparent = True
if not sc.world:
    sc.world = bpy.data.worlds.new("w")
sc.world.color = (0.8, 0.75, 0.78)
for nom, v in VUES.items():
    s = v["mmpx"] / 1000.0
    cam.data.ortho_scale = H * s
    # point du monde au centre de l'image
    centre_lat = (W / 2 - v["cx"]) * s
    centre_z = (v["pieds"] - H / 2) * s
    cible = v["droite"] * centre_lat + Vector((0, 0, centre_z))
    cam.location = cible + v["pos"]
    cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = DOSSIER + "\\rendu_%s.png" % nom
    bpy.ops.render.render(write_still=True, scene=sc.name)
print("COMPARER OK")
