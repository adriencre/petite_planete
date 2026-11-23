"""Écrit les scènes Godot du jardin du haut à partir des repères de Blender (ILE_03_COLONIE.md, G3).

  python tools/godot/jardin_du_haut_scenes.py

- scenes/ile03/porte_jardin.tscn : la porte de service du jardin, barrée de l'intérieur (porte_barree.gd) ;
- scenes/ile_03_maquette.tscn : (ré)écrit la marée du lagon (maree_lagon.gd), l'écluse (ecluse_jardin.gd)
  et ses repères (carillon, cloche-relais, arrivée), la lampe-mère (lampe_mere.gd) et l'écran du souvenir,
  la porte de service, la plaque du carillon, le dessin d'Aube du belvédère et la zone de caméra du jardin.
Les repères viennent de tools/blender/sources/jardin_du_haut_reperes.txt (coordonnées Godot), écrits par
tools/blender/jardin_du_haut.py. Relancer le script remplace ses propres blocs (ressources « jh_* » et
nœuds listés dans NOEUDS_GENERES) : ne pas retoucher ces nœuds à la main, modifier ce script.
"""
import math
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
reperes = {}
for ligne in (RACINE/"tools/blender/sources/jardin_du_haut_reperes.txt").read_text(encoding="utf-8").splitlines():
    if ligne.startswith("#"):
        continue
    champs = ligne.split("\t")
    reperes[champs[0]] = tuple(float(v) for v in champs[1:4])

# La géométrie de l'anneau (tools/blender/colonie_du_lagon.py), pour orienter le mur et les zones.
ANGLES = [-99-i*342/18 for i in range(19)]
INTERIEURS = [26, 25, 28, 27, 24, 25, 28, 26, 25, 27, 24, 26, 25, 28, 27, 25, 26, 27, 26]
R_MUR = 32.2
Z_JARDIN = 10.1


def point_godot(i, rayon):
    a = math.radians(ANGLES[i])
    return (rayon*math.cos(a), -rayon*.84*math.sin(a))     # (x, z) Godot


def f(v):
    return f"{v:.5g}"


def unitaire(x, z):
    n = math.hypot(x, z)
    return (x/n, z/n)


def repere_horizontal(p, avant):
    # Repère dont l'axe Z local est `avant` (horizontal, (x, z)), Y vers le haut.
    nx, nz = avant
    valeurs = (nz, 0, -nx, 0, 1, 0, nx, 0, nz, *p)
    return "Transform3D(" + ", ".join(f(v) for v in valeurs) + ")"


def debout(p, n):
    # Feuille verticale (page_lisible.gd) : Y local = normale sortante, Z local = vers le bas.
    nx, _, nz = n
    valeurs = (nz, nx, 0, 0, 0, -1, -nx, nz, 0, *p)
    return "Transform3D(" + ", ".join(f(v) for v in valeurs) + ")"


def a_plat(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return "Transform3D(" + ", ".join(f(v) for v in (c, 0, s, 0, 1, 0, -s, 0, c, *p)) + ")"


def vec(p):
    return "Vector3(" + ", ".join(f(v) for v in p) + ")"


# ----------------------------------------------------------------------------- la porte de service
# Repère de la porte : X le long du mur, Z vers la rue, origine au sol du jardin, au milieu du mur.
p8, p9 = point_godot(8, R_MUR+.4), point_godot(9, R_MUR+.4)
axe_x = unitaire(p9[0]-p8[0], p9[1]-p8[1])
porte = reperes["porte_service"]
vers_rue = unitaire(porte[0], porte[2])
axe_z = (-axe_x[1], axe_x[0])
if axe_z[0]*vers_rue[0]+axe_z[1]*vers_rue[1] < 0:
    # On retourne X (et donc Z) : le repère reste direct (pas de miroir).
    axe_x = (-axe_x[0], -axe_x[1])
    axe_z = (-axe_x[1], axe_x[0])
LARGEUR = math.hypot(p9[0]-p8[0], p9[1]-p8[1])*.24
(RACINE/"scenes/ile03/porte_jardin.tscn").write_text(f'''[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/porte_barree.gd" id="porte_script"]

[sub_resource type="StandardMaterial3D" id="chene"]
albedo_color = Color(0.737, 0.518, 0.376, 1)
roughness = 0.8

[sub_resource type="StandardMaterial3D" id="bois"]
albedo_color = Color(0.592, 0.431, 0.38, 1)
roughness = 0.85

[sub_resource type="StandardMaterial3D" id="cuivre"]
albedo_color = Color(0.671, 0.471, 0.384, 1)
roughness = 0.5

[sub_resource type="BoxMesh" id="battant_mesh"]
material = SubResource("chene")
size = Vector3({f(LARGEUR-.1)}, 3.1, 0.12)

[sub_resource type="BoxMesh" id="planche_mesh"]
material = SubResource("bois")
size = Vector3(0.05, 2.9, 0.02)

[sub_resource type="BoxMesh" id="ferrure_mesh"]
material = SubResource("cuivre")
size = Vector3({f(LARGEUR-.4)}, 0.12, 0.03)

[sub_resource type="BoxShape3D" id="battant_forme"]
size = Vector3({f(LARGEUR-.1)}, 3.1, 0.2)

[sub_resource type="BoxMesh" id="barre_mesh"]
material = SubResource("bois")
size = Vector3({f(LARGEUR+.6)}, 0.16, 0.14)

[node name="PorteJardin" type="Node3D" node_paths=PackedStringArray("charniere", "barre", "point_dehors", "point_dedans", "pose_barre")]
script = ExtResource("porte_script")
charniere = NodePath("Charniere")
barre = NodePath("Barre")
point_dehors = NodePath("PointDehors")
point_dedans = NodePath("PointDedans")
pose_barre = NodePath("PoseBarre")
distance = 1.6
angle_ouverte = 95.0

[node name="Charniere" type="Node3D" parent="."]
position = Vector3({f(-LARGEUR/2+.05)}, 0.02, -0.25)

[node name="Battant" type="MeshInstance3D" parent="Charniere"]
position = Vector3({f(LARGEUR/2-.05)}, 1.55, 0)
mesh = SubResource("battant_mesh")

[node name="PlancheA" type="MeshInstance3D" parent="Charniere/Battant"]
position = Vector3({f(-LARGEUR/4)}, 0, 0.07)
mesh = SubResource("planche_mesh")

[node name="PlancheB" type="MeshInstance3D" parent="Charniere/Battant"]
position = Vector3(0, 0, 0.07)
mesh = SubResource("planche_mesh")

[node name="PlancheC" type="MeshInstance3D" parent="Charniere/Battant"]
position = Vector3({f(LARGEUR/4)}, 0, 0.07)
mesh = SubResource("planche_mesh")

[node name="FerrureHaut" type="MeshInstance3D" parent="Charniere/Battant"]
position = Vector3(0, 1.0, 0.075)
mesh = SubResource("ferrure_mesh")

[node name="FerrureBas" type="MeshInstance3D" parent="Charniere/Battant"]
position = Vector3(0, -1.0, 0.075)
mesh = SubResource("ferrure_mesh")

[node name="Corps" type="StaticBody3D" parent="Charniere/Battant"]

[node name="Forme" type="CollisionShape3D" parent="Charniere/Battant/Corps"]
shape = SubResource("battant_forme")

[node name="Barre" type="MeshInstance3D" parent="."]
position = Vector3(0, 1.7, -0.45)
mesh = SubResource("barre_mesh")

[node name="PointDehors" type="Marker3D" parent="."]
position = Vector3(0, -0.5, 1.5)

[node name="PointDedans" type="Marker3D" parent="."]
position = Vector3(0, 0, -1.3)

[node name="PoseBarre" type="Marker3D" parent="."]
transform = Transform3D(0.0872, 0.9962, 0, -0.9962, 0.0872, 0, 0, 0, 1, {f(LARGEUR/2+.7)}, {f((LARGEUR+.6)/2)}, -0.55)
''', encoding="utf-8")

# ----------------------------------------------------------------------------- la Colonie
chemin = RACINE/"scenes/ile_03_maquette.tscn"
scene = chemin.read_text(encoding="utf-8")
NOEUDS_GENERES = ["MareeLagon", "EcluseJardin", "LampeMere", "CentreSouvenir", "EcranSouvenir", "PorteJardin",
                  "PlaqueCarillon", "DessinBelvedere", "ZoneJardin"]


def retirer_blocs(texte):
    # Retire les blocs écrits par une version précédente de ce script.
    blocs = texte.split("\n[")
    gardes = [blocs[0]]
    for b in blocs[1:]:
        entete = b.split("\n", 1)[0]
        if ' id="jh_' in entete and (entete.startswith("ext_resource") or entete.startswith("sub_resource")):
            continue
        if entete.startswith("node ") and any(f'name="{n}"' in entete or f'parent="{n}"' in entete
                                               or f'parent="{n}/' in entete for n in NOEUDS_GENERES):
            continue
        gardes.append(b)
    return "\n[".join(gardes)


scene = retirer_blocs(scene).rstrip("\n") + "\n"
ressources = [
    '[ext_resource type="Script" path="res://scripts/maree_lagon.gd" id="jh_maree"]',
    '[ext_resource type="Script" path="res://scripts/ecluse_jardin.gd" id="jh_ecluse"]',
    '[ext_resource type="Script" path="res://scripts/lampe_mere.gd" id="jh_lampe"]',
    '[ext_resource type="Script" path="res://scripts/page_lisible.gd" id="jh_page"]',
    '[ext_resource type="Script" path="res://scripts/zone_camera.gd" id="jh_zone"]',
    '[ext_resource type="Shader" path="res://shaders/souvenir_projete.gdshader" id="jh_shader"]',
    '[ext_resource type="PackedScene" path="res://scenes/ile03/porte_jardin.tscn" id="jh_porte"]',
    '[ext_resource type="AudioStream" path="res://assets/audio/chant_semeurs.wav" id="jh_chant"]',
    '[ext_resource type="Texture2D" path="res://assets/affiches/dessin_aube_serres.png" id="jh_dessin"]',
] + [f'[ext_resource type="Texture2D" path="res://assets/affiches/souvenir_arbre_rose_{n}.png" id="jh_souvenir_{n}"]'
     for n in range(1, 6)]
sous_ressources = ['''[sub_resource type="ShaderMaterial" id="jh_ecran_mat"]
render_priority = 1
shader = ExtResource("jh_shader")
shader_parameter/melange = 0.0
shader_parameter/force = 0.0
shader_parameter/eclat = 0.85''', '''[sub_resource type="QuadMesh" id="jh_ecran"]
size = Vector2(5.4, 5.4)''']

# La zone de caméra : une boîte par secteur du jardin, alignée sur la bande entre la falaise et le mur.
formes_zone = []
for i in (8, 9, 10):
    coins = [point_godot(i, INTERIEURS[i]), point_godot(i+1, INTERIEURS[i+1]),
             point_godot(i, R_MUR), point_godot(i+1, R_MUR)]
    cx = sum(c[0] for c in coins)/4
    cz = sum(c[1] for c in coins)/4
    a, b = point_godot(i, (INTERIEURS[i]+R_MUR)/2), point_godot(i+1, (INTERIEURS[i+1]+R_MUR)/2)
    tangente = unitaire(b[0]-a[0], b[1]-a[1])
    longueur = math.hypot(b[0]-a[0], b[1]-a[1])+.6
    profondeur = R_MUR-min(INTERIEURS[i], INTERIEURS[i+1])+.4
    sous_ressources.append(f'''[sub_resource type="BoxShape3D" id="jh_zone_{i}"]
size = Vector3({f(longueur)}, 6, {f(profondeur)})''')
    # X le long du secteur, Z en travers.
    tx, tz = tangente
    formes_zone.append(f'''
[node name="Secteur{i}" type="CollisionShape3D" parent="ZoneJardin"]
transform = Transform3D({f(tx)}, 0, {f(tz)}, 0, 1, 0, {f(-tz)}, 0, {f(tx)}, {f(cx)}, {f(Z_JARDIN+2)}, {f(cz)})
shape = SubResource("jh_zone_{i}")''')

lampe = reperes["lampe_mere"]
mur = reperes["mur_projection"]
vers_robot = unitaire(lampe[0]-mur[0], lampe[2]-mur[2])
prise = reperes["lampe_prise"]
ecran_p = (mur[0]+vers_robot[0]*.08, mur[1], mur[2]+vers_robot[1]*.08)
centre_vue = ((lampe[0]+mur[0])/2, Z_JARDIN+2.6, (lampe[2]+mur[2])/2)
carillon = (-6.7, 3.7, 34.0)
belv = reperes["belvedere"]
vers_lagon = unitaire(-belv[0], -belv[2])
dessin_p = (belv[0]+vers_lagon[0]*.75, Z_JARDIN+.62, belv[2]+vers_lagon[1]*.75)
texte_plaque = ("Gravé dans le cuivre, sous le carillon des marées :\\n\\n"
                "« Quand il chante, l'eau ouvre le chemin des serres. »")
texte_dessin = ("Un dessin d'Aube, posé sur le banc du belvédère : les serres vues d'en haut, les arbres roses "
                "qui penchent tous vers une grande lampe, et la mer avec des petits toits dessous.\\n\\n"
                "« Les arbres regardent la grande lampe. Moi, d'en haut, je regarde les maisons sous l'eau. »")
noeuds = [f'''
[node name="MareeLagon" type="Node" parent="." node_paths=PackedStringArray("mer")]
script = ExtResource("jh_maree")
mer = NodePath("../Mer")

[node name="EcluseJardin" type="Node3D" parent="." node_paths=PackedStringArray("colonie", "carillon", "cloche_relais", "arrivee")]
script = ExtResource("jh_ecluse")
colonie = NodePath("../Colonie")
carillon = NodePath("Carillon")
cloche_relais = NodePath("ClocheRelais")
arrivee = NodePath("Arrivee")

[node name="Carillon" type="Marker3D" parent="EcluseJardin"]
position = {vec(carillon)}

[node name="ClocheRelais" type="Marker3D" parent="EcluseJardin"]
position = {vec(reperes["cloche_relais"])}

[node name="Arrivee" type="Marker3D" parent="EcluseJardin"]
position = {vec(reperes["arrivee_jardin"])}

[node name="CentreSouvenir" type="Marker3D" parent="."]
position = {vec(centre_vue)}

[node name="EcranSouvenir" type="MeshInstance3D" parent="."]
transform = {repere_horizontal(ecran_p, vers_robot)}
visible = false
cast_shadow = 0
mesh = SubResource("jh_ecran")
material_override = SubResource("jh_ecran_mat")

[node name="LampeMere" type="Node3D" parent="." node_paths=PackedStringArray("colonie", "ecran", "centre_vue")]
transform = {repere_horizontal((prise[0], prise[1], prise[2]), vers_robot)}
script = ExtResource("jh_lampe")
colonie = NodePath("../Colonie")
ecran = NodePath("../EcranSouvenir")
images = [{", ".join(f'ExtResource("jh_souvenir_{n}")' for n in range(1, 6))}]
chant = ExtResource("jh_chant")
centre_vue = NodePath("../CentreSouvenir")

[node name="PorteJardin" parent="." instance=ExtResource("jh_porte")]
transform = Transform3D({f(axe_x[0])}, 0, {f(axe_x[1])}, 0, 1, 0, {f(axe_z[0])}, 0, {f(axe_z[1])}, {f(porte[0])}, {f(Z_JARDIN)}, {f(porte[2])})

[node name="PlaqueCarillon" type="Node3D" parent="."]
transform = {debout(reperes["plaque_carillon"], (0, 0, 1))}
script = ExtResource("jh_page")
texte = "{texte_plaque}"
distance_lecture = 2.2
taille_feuille = Vector2(0.8, 0.5)
ramasser = false
intensite_lueur = 0.5

[node name="DessinBelvedere" type="Node3D" parent="."]
transform = {a_plat(dessin_p, math.atan2(vers_lagon[0], vers_lagon[1]))}
script = ExtResource("jh_page")
texte = "{texte_dessin}"
distance_lecture = 1.8
hauteur_lecture = 1.8
taille_feuille = Vector2(0.42, 0.3)
image = ExtResource("jh_dessin")
appel_fort = true
hauteur_rayon = 3.0

[node name="ZoneJardin" type="Area3D" parent="."]
script = ExtResource("jh_zone")
orientation = 0.0
distance = 11.0
angle = 50.0
priorite = 3
''' + "".join(formes_zone) + "\n"]

# Ressources externes après les dernières, sous-ressources avant le premier nœud, nœuds avant les connexions.
NL = chr(10)
lignes = scene.split(NL)
derniere_ext = max(i for i, l in enumerate(lignes) if l.startswith("[ext_resource"))
lignes[derniere_ext+1:derniere_ext+1] = ressources
scene = NL.join(lignes)
premier_noeud = scene.index("[node ")
scene = scene[:premier_noeud] + (NL*2).join(sous_ressources) + NL*2 + scene[premier_noeud:]
if NL + "[connection" in scene:
    premiere_connexion = scene.index(NL + "[connection")+1
    scene = scene[:premiere_connexion] + "".join(noeuds).lstrip(NL) + NL + scene[premiere_connexion:]
else:
    scene = scene.rstrip(NL) + NL + "".join(noeuds)
chemin.write_text(scene, encoding="utf-8")
print("Jardin du haut écrit :", chemin.relative_to(RACINE), "et scenes/ile03/porte_jardin.tscn")
