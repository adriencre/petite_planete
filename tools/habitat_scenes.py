# Génère les décors du kit d'habitat des Lueurs (jardin de champignons, place, fils de lumière).
# python tools/habitat_scenes.py   (on peut ensuite tout retoucher dans l'éditeur)
import math, random

OUT = "assets/lueurs/habitat/"
HEAD = '''[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/lueurs/lueur_habitat.gd" id="1_script"]
[ext_resource type="Material" path="res://assets/lueurs/materials/lueur_tisse.tres" id="2_tisse"]
[ext_resource type="Material" path="res://assets/lueurs/materials/lueur_plein.tres" id="3_plein"]
[ext_resource type="Material" path="res://assets/lueurs/materials/lueur_halo.tres" id="4_halo"]
[ext_resource type="Material" path="res://assets/lueurs/materials/lueur_cendre.tres" id="5_cendre"]
[ext_resource type="Material" path="res://assets/lueurs/materials/lueur_cendre_plein.tres" id="6_cendre_plein"]
'''


def tf(x, y, z, sx=1.0, sy=1.0, sz=1.0, yaw=0.0, roll=0.0):
    cy, sy_ = math.cos(yaw), math.sin(yaw)
    cr, sr = math.cos(roll), math.sin(roll)
    # rotation Y puis Z, échelle
    m = [[cy * cr, -cy * sr, sy_], [sr, cr, 0.0], [-sy_ * cr, sy_ * sr, cy]]
    m = [[m[r][0] * sx, m[r][1] * sy, m[r][2] * sz] for r in range(3)]
    v = [m[0][0], m[1][0], m[2][0], m[0][1], m[1][1], m[2][1], m[0][2], m[1][2], m[2][2], x, y, z]
    return "Transform3D(" + ", ".join("%.4f" % a for a in v) + ")"


def node(name, parent, mesh, t):
    return '\n[node name="%s" type="MeshInstance3D" parent="%s"]\ntransform = %s\ncast_shadow = 0\nmesh = SubResource("%s")\n' % (name, parent, t, mesh)


def garden():
    rnd = random.Random(3)
    s = HEAD + '''
[sub_resource type="CylinderMesh" id="Pied"]
material = ExtResource("3_plein")
top_radius = 0.025
bottom_radius = 0.035
height = 0.22
radial_segments = 6
rings = 0

[sub_resource type="SphereMesh" id="Chapeau"]
material = ExtResource("2_tisse")
radius = 0.1
height = 0.1
radial_segments = 10
rings = 3
is_hemisphere = true

[sub_resource type="CylinderMesh" id="PiedMort"]
material = ExtResource("6_cendre_plein")
top_radius = 0.025
bottom_radius = 0.035
height = 0.12
radial_segments = 6
rings = 0

[sub_resource type="SphereMesh" id="ChapeauMort"]
material = ExtResource("5_cendre")
radius = 0.1
height = 0.1
radial_segments = 10
rings = 3
is_hemisphere = true

[sub_resource type="QuadMesh" id="Halo"]
material = ExtResource("4_halo")
size = Vector2(1.6, 1.6)

[node name="JardinChampignons" type="Node3D"]
script = ExtResource("1_script")

[node name="Vivant" type="Node3D" parent="."]
'''
    spots = [(0, 0, 1.3), (0.28, 0.12, 0.9), (-0.22, 0.2, 1.0), (0.1, -0.3, 0.75), (-0.32, -0.18, 0.85), (0.4, -0.2, 0.6), (-0.05, 0.42, 0.7)]
    for i, (x, z, k) in enumerate(spots):
        s += node("Pied%d" % i, "Vivant", "Pied", tf(x, 0.11 * k, z, k, k, k))
        s += node("Chapeau%d" % i, "Vivant", "Chapeau", tf(x, 0.22 * k, z, k * 1.1, k, k * 1.1, roll=rnd.uniform(-0.15, 0.15)))
    s += node("Halo", "Vivant", "Halo", tf(0, 0.25, 0))
    s += '\n[node name="Effondre" type="Node3D" parent="."]\nvisible = false\n'
    for i, (x, z, k) in enumerate(spots[:5]):
        s += node("Pied%d" % i, "Effondre", "PiedMort", tf(x, 0.06 * k, z, k, k, k, roll=rnd.uniform(-0.6, 0.6)))
        s += node("Chapeau%d" % i, "Effondre", "ChapeauMort", tf(x + 0.05, 0.03, z, k, k * 0.6, k, roll=rnd.uniform(1.0, 1.6)))
    open(OUT + "jardin_champignons.tscn", "w", encoding="utf-8").write(s)


def plaza():
    s = HEAD + '''
[sub_resource type="SphereMesh" id="Pierre"]
material = ExtResource("3_plein")
radius = 0.09
height = 0.12
radial_segments = 6
rings = 3

[sub_resource type="CylinderMesh" id="Bassin"]
material = ExtResource("2_tisse")
top_radius = 0.75
bottom_radius = 0.75
height = 0.02
radial_segments = 16
rings = 0

[sub_resource type="QuadMesh" id="Halo"]
material = ExtResource("4_halo")
size = Vector2(3.0, 3.0)

[sub_resource type="SphereMesh" id="PierreMorte"]
material = ExtResource("6_cendre_plein")
radius = 0.09
height = 0.08
radial_segments = 6
rings = 3

[node name="PlaceLueurs" type="Node3D"]
script = ExtResource("1_script")

[node name="Vivant" type="Node3D" parent="."]
'''
    for i in range(9):
        a = math.tau * i / 9
        s += node("Pierre%d" % i, "Vivant", "Pierre", tf(math.cos(a) * 1.25, 0.05, math.sin(a) * 1.25))
    s += node("Bassin", "Vivant", "Bassin", tf(0, 0.02, 0))
    s += node("Halo", "Vivant", "Halo", tf(0, 0.3, 0))
    s += '\n[node name="Effondre" type="Node3D" parent="."]\nvisible = false\n'
    for i in range(0, 9, 2):
        a = math.tau * i / 9 + 0.2
        s += node("Pierre%d" % i, "Effondre", "PierreMorte", tf(math.cos(a) * 1.35, 0.03, math.sin(a) * 1.35))
    open(OUT + "place_lueurs.tscn", "w", encoding="utf-8").write(s)


def threads():
    # un fil de lumière qui pend entre deux points (on déplace les points du chemin dans l'éditeur)
    pts = []
    for i in range(7):
        t = i / 6
        pts += [0, 0, 0, 0, 0, 0, round(t * 3.0, 3), round(1.6 - math.sin(t * math.pi) * 0.45, 3), 0]
    s = '''[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/lueurs/lueur_trail.gd" id="1_trail"]

[sub_resource type="Curve3D" id="Courbe"]
_data = {
"points": PackedVector3Array(%s),
"tilts": PackedFloat32Array(%s)
}

[node name="FilsLumiere" type="Path3D"]
curve = SubResource("Courbe")
script = ExtResource("1_trail")
width = 0.06
''' % (", ".join(str(v) for v in pts), ", ".join(["0"] * 7))
    open(OUT + "fils_lumiere.tscn", "w", encoding="utf-8").write(s)


garden()
plaza()
threads()
print("ok")
