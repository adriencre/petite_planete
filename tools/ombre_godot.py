# Scènes Godot du kit de l'ombre modélisé dans Blender (blender/peuple.blend → *_modele.glb).
# - une scène par objet : le modèle + ses collisions + ses lumières (éditables dans Godot) ;
# - les habitants : le modèle + leurs animations (même ossature pour tous) ;
# - scenes/mockups/ombre_planche.tscn : la planche de validation (tout le kit, de nuit).
# Usage : python tools/ombre_godot.py
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ombre_kit import Scene, xform, write_materials, ROOT  # noqa: E402

TEAL, AMBER, VIOLET, ROSE = (0.5, 1.0, 0.88), (1.0, 0.76, 0.45), (0.75, 0.6, 1.0), (1.0, 0.6, 0.78)

# nom : (dossier, collisions, lumières)
#   collision : ("cyl", rayon, hauteur, pos) | ("box", (x, y, z), pos)
#   lumière : (pos, couleur, énergie, portée)
KIT = {
    "MaisonChampignon": ("maisons", [("cyl", 0.92, 1.7, (0, 0.85, 0)), ("cyl", 1.65, 1.1, (0, 2.2, 0))],
                         [((0, 1.0, 1.25), TEAL, 0.6, 2.6), ((0, 1.35, 0), TEAL, 0.7, 3.2), ((0.6, 0.85, 1.0), AMBER, 0.55, 2.2)]),
    "MaisonSouche": ("maisons", [("cyl", 1.0, 1.8, (0, 0.9, 0)), ("cyl", 1.2, 1.3, (0, 2.2, 0))],
                     [((-0.65, 1.15, 0.6), AMBER, 0.5, 2.4), ((-0.55, 1.2, 1.05), AMBER, 0.45, 2.0), ((0, 3.0, 0), TEAL, 0.4, 2.0)]),
    "MaisonCoquillage": ("maisons", [("cyl", 1.05, 1.4, (0, 0.7, 0))],
                         [((0.62, 0.75, 1.0), VIOLET, 0.5, 2.2), ((0.3, 0.6, 1.2), TEAL, 0.4, 2.2), ((0.05, 2.9, 0), VIOLET, 0.4, 2.0)]),
    "MaisonPilotis": ("maisons", [("box", (2.1, 0.12, 1.8), (0, 0.92, 0)), ("box", (1.6, 0.95, 1.3), (0, 1.45, -0.1)),
                                  ("box", (1.2, 0.06, 0.6), (1.5, 0.86, 0.4))],
                      [((0.8, 1.75, 0.8), AMBER, 0.55, 2.4), ((-0.4, 1.55, 0.85), AMBER, 0.4, 2.0), ((1.5, 1.0, 0.15), TEAL, 0.4, 2.0)]),
    "TourAncienne": ("maisons", [("cyl", 1.0, 0.7, (0, 0.35, 0)), ("cyl", 0.72, 2.0, (0, 1.7, 0)), ("cyl", 1.2, 0.8, (0, 2.9, 0))],
                     [((0, 4.1, 0), AMBER, 0.6, 3.0), ((0, 2.45, 0), VIOLET, 0.6, 3.0), ((0, 1.2, 0.95), TEAL, 0.4, 2.0)]),
    "LampeChampignon": ("decor", [], [((0, 0.52, 0), TEAL, 0.6, 2.2)]),
    "Puits": ("decor", [("cyl", 0.65, 0.6, (0, 0.3, 0))], [((0, 0.6, 0), TEAL, 0.7, 2.5)]),
    "Etal": ("decor", [("box", (1.4, 0.65, 0.7), (0, 0.33, 0))], [((-0.66, 1.3, 0.15), AMBER, 0.45, 2.0), ((0, 0.95, 0), TEAL, 0.25, 1.6)]),
    "CordeLinge": ("decor", [], []),
    "Potager": ("decor", [("box", (1.7, 0.2, 1.1), (0, 0.1, 0))], [((0, 0.45, 0), TEAL, 0.35, 1.8)]),
    "Banc": ("decor", [("box", (1.2, 0.45, 0.4), (0, 0.22, 0))], []),
    "Ponton": ("decor", [("box", (0.9, 0.06, 2.5), (0, 0.5, 1.12))], [((0.42, 1.05, 2.24), AMBER, 0.5, 2.2)]),
    # le tablier pend un peu : deux rampes douces, qui repartent à la hauteur des deux bouts
    "PontCorde": ("decor", [("ramp", 0.8, -0.14, 2.0, (0, 0.02, -0.1)), ("ramp", 0.8, 0.14, 2.1, (0, -0.12, 1.9))], []),
    "EscalierRacines": ("decor", [("box", (0.85, 0.2, 0.36), (0, 0.1 + 0.2 * j, 0.32 * j)) for j in range(5)], []),
    "BerceauChampignon": ("decor", [("cyl", 0.4, 0.3, (0, 0.15, 0))], [((0, 0.35, 0), ROSE, 0.4, 1.5)]),
    "ChampignonGeant": ("decor", [("cyl", 0.35, 3.6, (0, 1.8, 0))], [((0, 3.4, 0), TEAL, 0.9, 4.5)]),
    "ChampignonGeantViolet": ("decor", [("cyl", 0.3, 2.6, (0, 1.3, 0))], [((0, 2.4, 0), VIOLET, 0.8, 3.5)]),
    "ChampignonGeantAmbre": ("decor", [("cyl", 0.25, 1.8, (0, 0.9, 0))], [((0, 1.65, 0), AMBER, 0.6, 2.5)]),
    "Fougere": ("decor", [], []),
    "Corail": ("decor", [], []),
    "NappeMousse": ("decor", [], []),
    "PinNuit": ("decor", [("cyl", 0.25, 1.6, (0, 0.8, 0))], []),
    # chemins de l'ombre : une rampe (largeur, montée, longueur, départ) + un palier en haut
    "EscalierFalaise": ("decor", [("ramp", 1.0, 3.05, 4.8, (0, 0, 0))], []),
    "IlotCorail": ("decor", [("cyl", 2.1, 0.6, (0, 0.2, 0))],
                   [((-0.6, 1.25, 0.9), TEAL, 0.6, 3.0), ((0, 1.0, 0), ROSE, 0.5, 3.5)]),
}
PEUPLE = ["Enfant", "Petite", "Ancienne", "Pecheur", "Jardiniere", "Tisserand", "Compteur"]


def snake(name):
    return "".join("_" + c.lower() if c.isupper() and i else c.lower() for i, c in enumerate(name))


def kit_scene(name):
    sub, cols, lights = KIT[name]
    s = Scene(name, "StaticBody3D" if cols else "Node3D", "res://scripts/ombre/ombre_objet.gd")
    fp = 0.3
    for c in cols:
        if c[0] == "cyl":
            fp = max(fp, c[1])
        elif c[0] == "box":
            fp = max(fp, max(c[1][0], c[1][2]) / 2)
    s.nodes[0] += "footprint = %.2f" % (fp + 0.35) + chr(10)
    s.instance("Modele", "res://assets/ombre/%s/%s_modele.glb" % (sub, snake(name)))
    for c in cols:
        if c[0] == "cyl":
            s.collision_cyl(c[1], c[2], c[3])
        elif c[0] == "ramp":
            w, rise, run, start = c[1], c[2], c[3], c[4]
            length = math.hypot(rise, run)
            ang = math.degrees(math.atan2(rise, run))
            sid = s.mesh("BoxShape3D", size="Vector3(%.2f, 0.2, %.3f)" % (w, length))
            center = (start[0], start[1] + rise / 2 - 0.1, start[2] + run / 2)
            s.node("Rampe%d" % len(s.nodes), "CollisionShape3D", ".", transform=xform(center, (-ang, 0, 0)), shape='SubResource("%s")' % sid)
        else:
            s.collision_box(c[1], c[2])
    for k, (pos, col, e, r) in enumerate(lights):
        s.light("Lumiere%d" % (k + 1), ".", pos, col, e, r)
    s.save("assets/ombre/%s/%s.tscn" % (sub, snake(name)))


# ---------------------------------------------------------------- habitants : animations
def v3(t):
    return "Vector3(%.4g, %.4g, %.4g)" % tuple(t)


class Anim:
    def __init__(self, name, length, loop=True):
        self.name, self.length, self.loop, self.tracks = name, length, loop, []

    def track(self, path, keys):
        self.tracks.append((path, keys))

    def text(self, sid):
        s = '[sub_resource type="Animation" id="%s"]\nresource_name = "%s"\nlength = %.3g\n' % (sid, self.name, self.length)
        if self.loop:
            s += "loop_mode = 1\n"
        for i, (path, keys) in enumerate(self.tracks):
            s += 'tracks/%d/type = "value"\ntracks/%d/imported = false\ntracks/%d/enabled = true\n' % (i, i, i)
            s += 'tracks/%d/path = NodePath("%s")\ntracks/%d/interp = 2\ntracks/%d/loop_wrap = true\n' % (i, path, i, i)
            s += "tracks/%d/keys = {\n" % i
            s += '"times": PackedFloat32Array(%s),\n' % ", ".join("%.3g" % k[0] for k in keys)
            s += '"transitions": PackedFloat32Array(%s),\n' % ", ".join("1" for _ in keys)
            s += '"update": 0,\n"values": [%s]\n}\n' % ", ".join(v3(k[1]) for k in keys)
        return s + "\n"


def anims(name, piv):
    """mêmes gestes pour tous, sur les pivots de chacun (Corps_<Nom>…)"""
    M = "Modele/" + name
    P = {
        "Corps": M + "/Corps_" + name,
    }
    P["Tete"] = P["Corps"] + "/Tete_" + name
    P["BrasG"] = P["Corps"] + "/BrasG_" + name
    P["BrasD"] = P["Corps"] + "/BrasD_" + name
    P["PiedG"] = M + "/PiedG_" + name
    P["PiedD"] = M + "/PiedD_" + name
    if "Pousse" in piv:
        P["Pousse"] = P["Tete"] + "/Pousse_" + name
    Z = (0, 0, 0)

    def pos(a, n, offs):
        base = piv[n]
        a.track(P[n] + ":position", [(t, tuple(b + o for b, o in zip(base, off))) for t, off in offs])

    def rot(a, n, keys):
        if n in P:
            a.track(P[n] + ":rotation", keys)

    out = []
    a = Anim("idle", 2.4)
    pos(a, "Corps", [(0, Z), (1.2, (0, 0.015, 0)), (2.4, Z)])
    rot(a, "Tete", [(0, Z), (0.8, (0.03, 0, 0.08)), (1.6, (0, 0, -0.05)), (2.4, Z)])
    rot(a, "Pousse", [(0, (0, 0, 0.2)), (1.2, (0, 0, -0.2)), (2.4, (0, 0, 0.2))])
    rot(a, "BrasG", [(0, Z), (1.2, (0, 0, 0.06)), (2.4, Z)])
    rot(a, "BrasD", [(0, Z), (1.2, (0, 0, -0.06)), (2.4, Z)])
    out.append(a)
    w = Anim("marche", 0.6)
    pos(w, "Corps", [(0, Z), (0.15, (0, 0.04, 0)), (0.3, Z), (0.45, (0, 0.04, 0)), (0.6, Z)])
    rot(w, "Corps", [(0, (0, 0, 0.07)), (0.3, (0, 0, -0.07)), (0.6, (0, 0, 0.07))])
    rot(w, "Tete", [(0, (0.06, 0, -0.04)), (0.3, (0.06, 0, 0.04)), (0.6, (0.06, 0, -0.04))])
    rot(w, "BrasG", [(0, (0.6, 0, 0)), (0.3, (-0.6, 0, 0)), (0.6, (0.6, 0, 0))])
    rot(w, "BrasD", [(0, (-0.6, 0, 0)), (0.3, (0.6, 0, 0)), (0.6, (-0.6, 0, 0))])
    rot(w, "Pousse", [(0, (0.3, 0, 0)), (0.3, (0.1, 0, 0)), (0.6, (0.3, 0, 0))])
    pos(w, "PiedG", [(0, (0, 0, 0.07)), (0.15, (0, 0.04, 0)), (0.3, (0, 0, -0.07)), (0.6, (0, 0, 0.07))])
    pos(w, "PiedD", [(0, (0, 0, -0.07)), (0.3, (0, 0, 0.07)), (0.45, (0, 0.04, 0)), (0.6, (0, 0, -0.07))])
    out.append(w)
    h = Anim("cache", 0.5, loop=False)
    pos(h, "Corps", [(0, Z), (0.5, (0, -0.07, 0))])
    h.track(P["Corps"] + ":scale", [(0, (1, 1, 1)), (0.5, (1.08, 0.82, 1.08))])
    rot(h, "Tete", [(0, Z), (0.5, (0.3, 0, 0))])
    rot(h, "BrasG", [(0, Z), (0.5, (-2.3, 0, -0.35))])
    rot(h, "BrasD", [(0, Z), (0.5, (-2.3, 0, 0.35))])
    rot(h, "Pousse", [(0, Z), (0.5, (0.6, 0, 0))])
    out.append(h)
    s = Anim("salut", 1.4, loop=False)
    rot(s, "BrasG", [(0, Z), (0.3, (-0.7, 0, 2.3)), (0.5, (-0.7, 0, 1.9)), (0.7, (-0.7, 0, 2.4)), (0.9, (-0.7, 0, 1.9)), (1.4, Z)])
    rot(s, "Tete", [(0, Z), (0.3, (0, 0, -0.12)), (1.1, (0, 0, -0.12)), (1.4, Z)])
    pos(s, "Corps", [(0, Z), (0.2, (0, 0.05, 0)), (0.4, Z), (1.4, Z)])
    out.append(s)
    p = Anim("parle", 0.9)
    rot(p, "Tete", [(0, Z), (0.3, (-0.06, 0, 0.05)), (0.6, (0.04, 0, -0.04)), (0.9, Z)])
    rot(p, "BrasD", [(0, Z), (0.45, (-0.5, 0, -0.3)), (0.9, Z)])
    pos(p, "Corps", [(0, Z), (0.45, (0, 0.012, 0)), (0.9, Z)])
    out.append(p)
    return out


def peuple_scene(name, piv):
    al = anims(name, piv)
    s = "[gd_scene load_steps=%d format=3]\n\n" % (len(al) + 4)
    s += '[ext_resource type="Script" path="res://scripts/ombre/ombre_objet.gd" id="1_mat"]\n'
    s += '[ext_resource type="PackedScene" path="res://assets/ombre/peuple/%s_modele.glb" id="2_glb"]\n\n' % snake(name)
    for a in al:
        s += a.text("Anim_" + a.name)
    s += '[sub_resource type="AnimationLibrary" id="AnimLib"]\n_data = {\n'
    s += ",\n".join('&"%s": SubResource("Anim_%s")' % (a.name, a.name) for a in al) + "\n}\n\n"
    s += '[node name="%s" type="Node3D"]\nscript = ExtResource("1_mat")\n\n' % name
    s += '[node name="Modele" parent="." instance=ExtResource("2_glb")]\n\n'
    s += '[node name="Animation" type="AnimationPlayer" parent="."]\nlibraries = {\n&"": SubResource("AnimLib")\n}\nautoplay = &"idle"\n\n'
    s += ('[node name="Halo" type="OmniLight3D" parent="."]\ntransform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.7, 0.45)\n'
          'light_color = Color(0.5, 1, 0.88, 1)\nlight_energy = 0.4\nomni_range = 1.6\nomni_attenuation = 1.6\n')
    with open(os.path.join(ROOT, "assets/ombre/peuple/%s.tscn" % snake(name)), "w", encoding="utf-8") as f:
        f.write(s)
    print("ok peuple/%s.tscn" % snake(name))


# ---------------------------------------------------------------- planche de validation
def night(s):
    env = s.mesh("Environment", background_mode=1, background_color="Color(0.04, 0.06, 0.13, 1)",
                 ambient_light_source=2, ambient_light_color="Color(0.35, 0.42, 0.7, 1)", ambient_light_energy=0.6,
                 ssao_enabled="true", ssao_radius=0.8, ssao_intensity=1.4,
                 glow_enabled="true", glow_intensity=0.8, glow_bloom=0.08, glow_hdr_threshold=0.9)
    s.node("WorldEnvironment", "WorldEnvironment", ".", environment='SubResource("%s")' % env)
    s.node("Lune", "DirectionalLight3D", ".", transform=xform((0, 10, 0), (-50, -30, 0)),
           light_color="Color(0.62, 0.72, 1, 1)", light_energy=0.6, shadow_enabled="true", shadow_blur=2.0)


def label(s, name, text, pos, size=48):
    font = s.ext_res("FontFile", "res://assets/fonts/Caveat.ttf")
    s.node(name, "Label3D", ".", transform=xform(pos, (-60, 0, 0)), font='ExtResource("%s")' % font, font_size=size,
           pixel_size=0.006, outline_size=10, modulate="Color(0.8, 0.95, 1, 1)", outline_modulate="Color(0, 0, 0, 0.6)", text='"%s"' % text)


def planche():
    s = Scene("OmbrePlanche")
    s.node("ToutVisible", "Node", ".", script='ExtResource("%s")' % s.ext_res("Script", "res://scripts/ombre/ombre_tout_visible.gd"))
    night(s)
    g = s.node("Sol", "StaticBody3D", ".")
    s.part("Dalle", s.box(46, 1.0, 30), "mousse", g, pos=(0, -0.5, 0))
    sid = s.mesh("BoxShape3D", size="Vector3(46, 1, 30)")
    s.node("Forme", "CollisionShape3D", g, transform=xform((0, -0.5, 0)), shape='SubResource("%s")' % sid)
    I = lambda name, rel, pos, rot=0: s.instance(name, "res://assets/ombre/%s.tscn" % rel, transform=xform(pos, (0, rot, 0)))
    noms = {"MaisonChampignon": "maison-champignon", "MaisonSouche": "souche creuse", "MaisonCoquillage": "coquillage",
            "MaisonPilotis": "cabane sur pilotis", "TourAncienne": "tour de l'ancienne", "LampeChampignon": "lampe",
            "Puits": "puits", "Etal": "étal du marché", "CordeLinge": "corde à linge", "Potager": "potager", "Banc": "banc",
            "Ponton": "ponton", "PontCorde": "pont de corde", "EscalierRacines": "escalier de racines", "BerceauChampignon": "berceau",
            "ChampignonGeant": "champignon géant", "ChampignonGeantViolet": "géant violet", "ChampignonGeantAmbre": "géant ambré",
            "Fougere": "fougère", "Corail": "corail", "NappeMousse": "mousse", "PinNuit": "pin",
            "EscalierFalaise": "escalier des géants", "IlotCorail": "îlot de corail",
            "Enfant": "l'enfant", "Petite": "la petite", "Ancienne": "l'ancienne", "Pecheur": "le pêcheur",
            "Jardiniere": "la jardinière", "Tisserand": "le tisserand", "Compteur": "le Compteur"}
    # rangée 1 : maisons
    maisons = ["MaisonChampignon", "MaisonSouche", "MaisonCoquillage", "MaisonPilotis", "TourAncienne"]
    for i, n in enumerate(maisons):
        x = -16 + i * 7.5
        I(n, "maisons/" + snake(n), (x, 0, -8))
        label(s, "Nom" + n, noms[n], (x, 0.05, -4.6))
    # rangée 2 : habitants (+ le robot)
    for i, n in enumerate(PEUPLE):
        x = -9 + i * 2.2
        I(n, "peuple/" + snake(n), (x, 0, 1.5))
        label(s, "Nom" + n, noms[n], (x, 0.05, 2.6), 36)
    s.instance("Robot", "res://scenes/robot.tscn", transform=xform((-11.5, 0, 1.5)))
    label(s, "NomRobot", "le robot", (-11.5, 0.05, 2.6), 36)
    # rangée 3 : village et nature
    deco = [n for n in KIT if n not in maisons]
    for i, n in enumerate(deco):
        x = -19 + (i % 9) * 4.6
        z = 7.5 + (i // 9) * 5.0
        I(n, "decor/" + snake(n), (x, 0, z))
        label(s, "Nom" + n, noms[n], (x, 0.05, z + 1.8), 36)
    s.node("Camera", "Camera3D", ".", transform=xform((0, 30, 34), (-42, 0, 0)), fov=40.0, current="true")
    s.save("scenes/mockups/ombre_planche.tscn")


if __name__ == "__main__":
    write_materials()
    piv = json.load(open(os.path.join(ROOT, "tools", "pivots.json")))
    for n in KIT:
        kit_scene(n)
    for n in PEUPLE:
        peuple_scene(n, piv[n])
    planche()
