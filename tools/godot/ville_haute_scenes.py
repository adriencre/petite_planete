"""Écrit les scènes Godot de la rue des Trois-Soleils à partir des repères de Blender (ILE_03_COLONIE.md, G2).

  python tools/godot/ville_haute_scenes.py

- scenes/ile03/parvis_trois_soleils.tscn : les 9 lanternes, la porte (porte_trois_soleils.gd), l'affiche 5 ;
- scenes/ile03/borne_recharge.tscn : la borne du quai (pierre_soleil.gd) ;
- scenes/ile_03_maquette.tscn : (ré)écrit le parvis, la borne, les affiches, les documents de la maison
  commune, la coupe de visite et la caméra d'anneau (scripts/camera_anneau.gd). Les repères viennent de tools/blender/sources/ville_haute_reperes.txt
  (coordonnées Godot), écrits par tools/blender/ville_haute.py.
Relancer le script remplace ses propres blocs dans la Colonie (ressources « vh_* » et nœuds listés dans
NOEUDS_GENERES) : ne pas retoucher ces nœuds à la main dans l'éditeur, modifier ce script.
"""
import math
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
reperes, normales = {}, {}
angle = 0.0
for ligne in (RACINE/"tools/blender/sources/ville_haute_reperes.txt").read_text(encoding="utf-8").splitlines():
    if ligne.startswith("#"):
        angle = float(ligne.split(":")[1])
        continue
    champs = ligne.split("\t")
    reperes[champs[0]] = tuple(float(v) for v in champs[1:4])
    if len(champs) > 4:
        normales[champs[0]] = float(champs[4])

# Axes du parvis en Godot : x = vers le secteur suivant, y = vers la porte (Blender), et la normale « vers la rue ».
AXE_X = (math.cos(angle), 0.0, -math.sin(angle))
AXE_Y = (-math.sin(angle), 0.0, -math.cos(angle))
VERS_RUE = tuple(-v for v in AXE_Y)


def plus(p, *termes):
    x, y, z = p
    for k, v in termes:
        x, y, z = x+k*v[0], y+k*v[1], z+k*v[2]
    return (x, y, z)


def f(v):
    return f"{v:.5g}"


def debout(p, n):
    # Feuille verticale (page_lisible.gd) : Y local = normale sortante, Z local = vers le bas.
    nx, _, nz = n
    valeurs = (nz, nx, 0, 0, 0, -1, -nx, nz, 0, *p)
    return "Transform3D(" + ", ".join(f(v) for v in valeurs) + ")"


def a_plat(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return "Transform3D(" + ", ".join(f(v) for v in (c, 0, s, 0, 1, 0, -s, 0, c, *p)) + ")"


def normale_godot(t):
    return (math.cos(t), 0.0, -math.sin(t))


# ----------------------------------------------------------------------------- le parvis
porte = reperes["porte_centre"]
lanternes = []
for k in range(1, 10):
    nom = next(n for n in reperes if n.startswith(f"lanterne_{k}_"))
    lanternes.append((k, reperes[nom], nom.endswith("motif")))
motif = "".join("1" if m else "0" for _, _, m in lanternes)

texte_porte = ("Cloué sur la grande porte de la maison commune, d'une écriture pressée :\n\n"
               "Départ ce soir. Tous à la Nef.\nSauf : personnel de la Centrale, malades de l'île blanche.")
affiche_5 = plus(porte, (-.85, AXE_X), (0.0, AXE_Y), (2.9, (0, 1, 0)))
battants = plus(porte, (.12, AXE_Y), (2.0, (0, 1, 0)))

parvis = [f'''[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/porte_trois_soleils.gd" id="porte"]
[ext_resource type="PackedScene" path="res://assets/models/lanterne_tulipe.glb" id="tulipe"]
[ext_resource type="Script" path="res://scripts/lanterne_fleur.gd" id="fleur"]
[ext_resource type="Script" path="res://scripts/page_lisible.gd" id="page"]
[ext_resource type="Texture2D" path="res://assets/affiches/affiche_depart.png" id="depart"]

[sub_resource type="BoxShape3D" id="battants"]
size = Vector3(2.8, 4, 0.25)

[node name="ParvisTroisSoleils" type="Node3D" node_paths=PackedStringArray("lanternes", "battants_fermes", "affiche_porte")]
script = ExtResource("porte")
lanternes = [{", ".join(f'NodePath("Lanterne{k}")' for k, _, _ in lanternes)}]
motif = "{motif}"
battants_fermes = NodePath("BattantsFermes/Forme")
affiche_porte = NodePath("AfficheDepart")
''']
for k, p, m in lanternes:
    parvis.append(f'''
[node name="Lanterne{k}" parent="." instance=ExtResource("tulipe")]
transform = {a_plat(p, angle)}
script = ExtResource("fleur")
premiere_fois = false
index_zone = -1
distance_activation = 1.6
distance_appel = 4.0
''')
parvis.append(f'''
[node name="BattantsFermes" type="StaticBody3D" parent="."]
transform = {a_plat(battants, angle)}

[node name="Forme" type="CollisionShape3D" parent="BattantsFermes"]
shape = SubResource("battants")

[node name="AfficheDepart" type="Node3D" parent="."]
transform = {debout(affiche_5, VERS_RUE)}
script = ExtResource("page")
texte = "{texte_porte}"
distance_lecture = 2.2
taille_feuille = Vector2(0.7, 0.97)
image = ExtResource("depart")
ramasser = false
intensite_lueur = 0.6
appel_fort = true
hauteur_rayon = 3.5
''')
(RACINE/"scenes/ile03/parvis_trois_soleils.tscn").write_text("".join(parvis), encoding="utf-8")

# ----------------------------------------------------------------------------- la borne du quai
(RACINE/"scenes/ile03/borne_recharge.tscn").write_text('''[gd_scene format=3]

[ext_resource type="Script" path="res://scripts/pierre_soleil.gd" id="pierre"]

[sub_resource type="StandardMaterial3D" id="or"]
albedo_color = Color(1, 0.8, 0.43, 1)
roughness = 0.35

[sub_resource type="CylinderMesh" id="coeur"]
material = SubResource("or")
top_radius = 0.1
bottom_radius = 0.15
height = 0.38
radial_segments = 8
rings = 0

[node name="BorneRecharge" type="Node3D"]
script = ExtResource("pierre")
distance_activation = 1.8
distance_appel = 5.0
hauteur_rayon = 2.5
eclat_repos = 2.0
eclat_appel = 3.0
energie_lumiere = 1.6

[node name="Cristal" type="MeshInstance3D" parent="."]
position = Vector3(0, 1.57, 0)
mesh = SubResource("coeur")
''', encoding="utf-8")

# ----------------------------------------------------------------------------- la Colonie
chemin = RACINE/"scenes/ile_03_maquette.tscn"
scene = chemin.read_text(encoding="utf-8")
NOEUDS_GENERES = ["ParvisTroisSoleils", "BorneRecharge", "AfficheCommandante1", "MorceauPlanA", "AfficheCommandante2",
                  "AfficheCommandante3", "MorceauPlanB", "AfficheCommandante4", "MorceauPlanC", "PlanArchipel",
                  "OrdresYsolde", "LettresTavin", "InterieurCommune", "CameraAnneau", "CameraColonie",
                  "ZoneCrete", "ZoneVilleHauteNord", "ZoneVilleHauteSud", "ZoneParvis", "ZoneBureau"] +                  [f"ZoneRue{i:02d}" for i in range(6, 17)]


def retirer_blocs(texte):
    # Retire les blocs écrits par une version précédente de ce script.
    blocs = texte.split("\n[")
    gardes = [blocs[0]]
    for b in blocs[1:]:
        entete = b.split("\n", 1)[0]
        if ' id="vh_' in entete and (entete.startswith("ext_resource") or entete.startswith("sub_resource")):
            continue
        if entete.startswith("node ") and any(f'name="{n}"' in entete or f'parent="{n}"' in entete for n in NOEUDS_GENERES):
            continue
        if entete.startswith("connection") and 'from="InterieurCommune"' in entete:
            continue
        gardes.append(b)
    return "\n[".join(gardes)


scene = retirer_blocs(scene)

textures = {
    "affiche_1": "affiche_commandante_1", "affiche_2": "affiche_commandante_2",
    "affiche_3": "affiche_commandante_3", "affiche_4": "affiche_commandante_4",
    "morceau_A": "plan_eclairage_a", "morceau_B": "plan_eclairage_b", "morceau_C": "plan_eclairage_c",
    "plan_archipel": "plan_archipel_semeurs", "ordres_ysolde": "ordres_ysolde_commune", "lettres_tavin": "lettres_tavin",
}
ressources = ['[ext_resource type="PackedScene" path="res://scenes/ile03/parvis_trois_soleils.tscn" id="vh_parvis"]',
              '[ext_resource type="PackedScene" path="res://scenes/ile03/borne_recharge.tscn" id="vh_borne"]',
              '[ext_resource type="Script" path="res://scripts/camera_zones.gd" id="vh_camera"]',
              '[ext_resource type="Script" path="res://scripts/zone_camera.gd" id="vh_zone"]']
for cle, fichier in textures.items():
    ressources.append(f'[ext_resource type="Texture2D" path="res://assets/affiches/{fichier}.png" id="vh_{cle}"]')

plan = "« Éclairage réglementaire de la rue des Trois-Soleils », par ordre de la Commandante."
pages = [
    # (nœud, repère, texte, taille, distance, ramasser, lueur, position : "colonne" | "mur" | "plat")
    ("AfficheCommandante1", "affiche_1", "Affiche de la Commandante, n° 1 :\n\n« Une lanterne par foyer. »", (0.48, 0.67), 1.8, False, .6, "colonne"),
    ("MorceauPlanA", "morceau_A", "Sur la table de la maison du quai, un morceau d'affiche déchirée. " + plan + "\n\nEn haut, la porte de la maison commune. Dessous, la première rangée commence : un soleil, puis un rond. Le reste est arraché.", (0.45, 0.53), 1.6, False, .8, "plat"),
    ("AfficheCommandante2", "affiche_2", "Affiche de la Commandante, n° 2 :\n\n« La nuit, restez dans la lumière. »", (0.9, 1.25), 2.2, False, .6, "mur"),
    ("AfficheCommandante3", "affiche_3", "Ordre de la Commandante, n° 3 :\n\n« Jamais d'ombre. »", (0.48, 0.67), 1.8, False, .6, "colonne"),
    ("MorceauPlanB", "morceau_B", "Sur le comptoir des couturières, un autre morceau de la même affiche. " + plan + "\n\nIl reste le bout de la première rangée, côté droit : un soleil. Et toute la rangée du milieu : trois ronds.", (0.4, 0.47), 1.6, False, .8, "plat"),
    ("AfficheCommandante4", "affiche_4", "Ordre de la Commandante, n° 4 :\n\n« Toute ombre est un danger. Signalez les lanternes éteintes. »", (0.9, 1.25), 2.2, False, .6, "mur"),
    ("MorceauPlanC", "morceau_C", "Sur le bureau du maître, à l'école, le bas de l'affiche. " + plan + "\n\nLa dernière rangée : un rond, un soleil, un rond.\n« Soleil : allumée. Rond : éteinte. »", (0.4, 0.47), 1.6, False, .8, "plat"),
]
noeuds = [f'''
[node name="ParvisTroisSoleils" parent="." node_paths=PackedStringArray("colonie") instance=ExtResource("vh_parvis")]
colonie = NodePath("../Colonie")

[node name="BorneRecharge" parent="." instance=ExtResource("vh_borne")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -9.55, 1.12, 29.2)

[node name="CameraColonie" type="Node" parent="." node_paths=PackedStringArray("joueur")]
script = ExtResource("vh_camera")
joueur = NodePath("../Joueur")
''']
for nom, cle, texte, taille, distance, ramasser, lueur, pose in pages:
    p = reperes[cle]
    if pose == "plat":
        # Posé sur un meuble : le haut de la feuille tourné vers le fond de la pièce (5e colonne du repère).
        t = normales[cle]
        transformation = a_plat(plus(p, (.004, (0, 1, 0))), math.atan2(-math.cos(t), math.sin(t)))
        hauteur = "\nhauteur_lecture = 1.8"
    else:
        n = normale_godot(normales[cle])
        if pose == "colonne":
            p = plus(p, (-.05, n))   # au ras du pan octogonal de la colonne
        transformation = debout(p, n)
        hauteur = ""
    if cle.startswith("morceau_"):
        hauteur += ('\nassemblage = "plan_eclairage"'
                    '\ntitre_assemblage = "Le plan d\'éclairage de la rue des Trois-Soleils, recollé morceau par morceau."')
    noeuds.append(f'''
[node name="{nom}" type="Node3D" parent="."]
transform = {transformation}
script = ExtResource("9_ybcho")
texte = "{texte}"
distance_lecture = {distance}{hauteur}
taille_feuille = Vector2({taille[0]}, {taille[1]})
image = ExtResource("vh_{cle}")
ramasser = {"true" if ramasser else "false"}
intensite_lueur = {lueur}
appel_fort = true
''')

documents = [
    ("PlanArchipel", "plan_archipel", debout(reperes["plan_archipel"], VERS_RUE),
     "Au mur de la salle du conseil, le plan de l'archipel des Semeurs. Les îles ont leur nom : la Colonie, le Phare, l'île blanche, la Nef, la Centrale, l'île du Réveil. Au nord-ouest, une petite tache d'encre, là où il n'y a rien.",
     (2.7, 1.93), 3.0, 0.0, False, .3),
    ("OrdresYsolde", "ordres_ysolde", a_plat(plus(reperes["ordres_ysolde"], (.005, (0, 1, 0))), angle),
     "Le registre des ordres de la Commandante, sur son bureau :\n\n« Doubler les lanternes de la ville haute avant la saison sombre. »\n« Les malades seront envoyés à l'île blanche jusqu'à guérison. »\n« La Nef est réparée. Nous partons. »",
     (0.6, 0.78), 1.6, 1.6, True, 1.0),
    ("LettresTavin", "lettres_tavin", a_plat(plus(reperes["lettres_tavin"], (.02, (0, 1, 0))), angle),
     "Dans la corbeille d'Ysolde, trois billets froissés de l'ingénieur Tavin :\n\n« Commandante, la centrale ne tiendra pas une saison de plus à ce régime. »\n« Chaque lanterne que nous ajoutons, la brume semble la sentir. Elle s'épaissit autour. »\n« Le berceau du jardinier a sa propre ligne. Quoi qu'il arrive, il tiendra. »",
     (0.42, 0.55), 1.5, 1.6, True, 1.0),
]
for nom, cle, transform, texte, taille, distance, hauteur, ramasser, lueur in documents:
    noeuds.append(f'''
[node name="{nom}" type="Node3D" parent="."]
transform = {transform}
script = ExtResource("9_ybcho")
texte = "{texte}"
distance_lecture = {distance}
hauteur_lecture = {hauteur}
taille_feuille = Vector2({taille[0]}, {taille[1]})
image = ExtResource("vh_{cle}")
ramasser = {"true" if ramasser else "false"}
intensite_lueur = {lueur}
appel_fort = true
''')

# La coupe de visite : la salle et le bureau d'Ysolde, toit et murs côté caméra effacés en entrant.
hauteur_sol = reperes["lanterne_1_motif"][1]
salle = plus(porte, (2.8, AXE_Y), (1.5, (0, 1, 0)))
bureau = plus(porte, (7.4, AXE_Y), (1.5, (0, 1, 0)))
noeuds.append(f'''
[node name="InterieurCommune" type="Area3D" parent="." node_paths=PackedStringArray("toit", "murs_hauts")]
collision_layer = 0
monitorable = false
script = ExtResource("coupe_maison")
toit = NodePath("../Colonie/Toit_maison_commune")
murs_hauts = NodePath("../Colonie/Murs_hauts_maison_commune")
autres = Array[NodePath]([NodePath("../Colonie/Murs_hauts_bureau_commune")])

[node name="Salle" type="CollisionShape3D" parent="InterieurCommune"]
transform = {a_plat(salle, angle)}
shape = SubResource("vh_salle")

[node name="Bureau" type="CollisionShape3D" parent="InterieurCommune"]
transform = {a_plat(bureau, angle)}
shape = SubResource("vh_bureau")
''')
# ----------------------------------------------------------------------------- les zones de cadrage
# Un cadre stable par quartier (camera_zones.gd) : la caméra regarde ce qui intéresse le joueur et ne
# bouge plus tant qu'il y reste. Ville basse, quai et Coin noir gardent le cadrage de la scène.
HAUTEURS = [1, 1.2, 2, 2.8, 3.3, 3.5, 4.4, 6.4, 8.8, 10, 10, 9.4, 8.1, 7.2, 6, 4.8, 3.6, 2, 1]
ANGLES = [-99-i*342/18 for i in range(19)]


def secteur(i, rayon=41.0):
    # Centre (Godot) et rotation d'un secteur de l'anneau, comme dans colonie_du_lagon.py.
    a = math.radians((ANGLES[i]+ANGLES[i+1])/2)
    x, y = rayon*math.cos(a), rayon*.84*math.sin(a)
    rotation = math.atan2(math.sin(a)*.84, math.cos(a))-math.pi/2
    return (x, (HAUTEURS[i]+HAUTEURS[i+1])/2+6, -y), rotation


def vers_le_lagon(i):
    # Orientation (degrés) qui place la caméra entre le secteur et le centre du lagon.
    (x, _, z), _ = secteur(i)
    return math.degrees(math.atan2(-x, -z))


def orientation(v):
    return math.degrees(math.atan2(v[0], v[2]))


def vers_le_secteur_precedent(i):
    # Orientation (degrés) qui place la caméra dans l'axe de la rue, du côté d'où l'on arrive (secteur i-1) :
    # les deux rangées de maisons passent sur les côtés et ne masquent plus le robot.
    (x, _, z), _ = secteur(i, 36)
    (xp, _, zp), _ = secteur(i-1, 36)
    return math.degrees(math.atan2(xp-x, zp-z))


# Un tronçon de rue par secteur, de la crête au bout de la ville haute : la caméra tourne d'un petit cran
# (19°) en passant d'un tronçon au suivant, plus haut que d'habitude pour voir par-dessus les toits.
zones = [(f"ZoneRue{i:02d}", (i,), vers_le_secteur_precedent(i), 10.5, 56.0, 0) for i in range(8, 17)]


def entre(a, b, t):
    # Interpolation d'angles en degrés par le plus court chemin.
    d = (b-a+180) % 360-180
    return a+d*t


# Les secteurs 6 et 7 font la transition depuis le cadrage de la ville basse (45°, celui de la scène),
# pour ne pas faire un grand saut en arrivant sur la crête.
zones = [(f"ZoneRue{i:02d}", (i,), entre(45.0, vers_le_secteur_precedent(i), t), 9.0+1.5*t, 40.0+16*t, 0)
         for i, t in ((6, .4), (7, .75))] + zones
sous_zones = '''[sub_resource type="BoxShape3D" id="vh_zone_secteur"]
size = Vector3(15, 26, 34)

'''
for nom, secteurs, o, d, a, prio in zones:
    noeuds.append(f'''
[node name="{nom}" type="Area3D" parent="."]
script = ExtResource("vh_zone")
orientation = {o:.1f}
distance = {d}
angle = {a}
priorite = {prio}
''')
    for i in secteurs:
        centre, rot = secteur(i)
        noeuds.append(f'''
[node name="Secteur{i}" type="CollisionShape3D" parent="{nom}"]
transform = {a_plat(centre, rot)}
shape = SubResource("vh_zone_secteur")
''')
# Le parvis et la salle du conseil : vue de face, la porte en haut de l'écran comme sur le plan d'éclairage,
# un peu plus haut pour voir toute la grille. Le bureau d'Ysolde : vue depuis le sud, par le mur qui s'efface.
parvis_zone = plus(porte, (-1.1, AXE_Y), (4.0, (0, 1, 0)))
bureau_zone = plus(porte, (7.4, AXE_Y), (1.5, (0, 1, 0)))
noeuds.append(f'''
[node name="ZoneParvis" type="Area3D" parent="."]
script = ExtResource("vh_zone")
orientation = {orientation(VERS_RUE):.1f}
distance = 12.5
angle = 52.0
priorite = 1

[node name="Volume" type="CollisionShape3D" parent="ZoneParvis"]
transform = {a_plat(parvis_zone, angle)}
shape = SubResource("vh_zone_parvis")

[node name="ZoneBureau" type="Area3D" parent="."]
script = ExtResource("vh_zone")
orientation = {orientation(AXE_X):.1f}
distance = 9.0
angle = 55.0
priorite = 2

[node name="Volume" type="CollisionShape3D" parent="ZoneBureau"]
transform = {a_plat(bureau_zone, angle)}
shape = SubResource("vh_zone_bureau")
''')
sous_zones += '''[sub_resource type="BoxShape3D" id="vh_zone_parvis"]
size = Vector3(13.5, 20, 21)

[sub_resource type="BoxShape3D" id="vh_zone_bureau"]
size = Vector3(6.6, 4, 3.4)

'''

sous_ressources = sous_zones + '''[sub_resource type="BoxShape3D" id="vh_salle"]
size = Vector3(11.5, 3, 4.8)

[sub_resource type="BoxShape3D" id="vh_bureau"]
size = Vector3(6.2, 3, 3.0)

'''
connexions = '''[connection signal="body_entered" from="InterieurCommune" to="InterieurCommune" method="_robot_entre"]
[connection signal="body_exited" from="InterieurCommune" to="InterieurCommune" method="_robot_sort"]
'''

# Ressources externes après les dernières, sous-ressources avant le premier nœud, nœuds avant les connexions.
lignes = scene.split("\n")
derniere_ext = max(i for i, l in enumerate(lignes) if l.startswith("[ext_resource"))
lignes[derniere_ext+1:derniere_ext+1] = ressources
scene = "\n".join(lignes)
premier_noeud = scene.index("[node ")
scene = scene[:premier_noeud] + sous_ressources + scene[premier_noeud:]
premiere_connexion = scene.index("[connection")
scene = scene[:premiere_connexion] + "".join(noeuds).lstrip("\n") + "\n" + scene[premiere_connexion:]
scene = scene.rstrip("\n") + "\n" + connexions
chemin.write_text(scene, encoding="utf-8")
print("Colonie : parvis, borne, 10 documents et coupe de la maison commune ajoutés.")
