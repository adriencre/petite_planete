"""Modèle de la Colonie à partir des emprises et collisions éditables de Godot.

Lancer Blender en arrière-plan avec --python tools/blender/terrain_ile_03.py.
Le relief, les accès et les pavages sont exportés ensemble. L'eau, les caméras
et l'éclairage servent uniquement aux rendus Blender.
"""
from pathlib import Path
import math
import random
import re

import bpy
from mathutils import Euler, Vector

RACINE = Path(__file__).resolve().parents[2]
SCENE = RACINE / "scenes/ile_03_maquette.tscn"
RENDUS = RACINE / "concept/ile_03"
MODELE = RACINE / "assets/models/ile03/terrain_ile_03.glb"
ALEA = random.Random(37)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "La Colonie — terrain"


def lire_sections(texte, etiquette):
    motif = rf'^\[{etiquette} ([^\n]+)\]\n([^\[]*)'
    for entete, contenu in re.findall(motif, texte, re.M):
        yield dict(re.findall(r'(\w+)="([^"]+)"', entete)), dict(
            ligne.split(" = ", 1) for ligne in contenu.splitlines() if " = " in ligne
        )


def composantes(valeur):
    return tuple(float(n) for n in valeur.split("(", 1)[1][:-1].split(","))


def reference(valeur):
    return valeur.split('"')[1]


texte = SCENE.read_text()
ressources = {a["id"]: p for a, p in lire_sections(texte, "sub_resource")}
noeuds = {
    ("" if a["parent"] == "." else a["parent"] + "/") + a["name"]: p
    for a, p in lire_sections(texte, "node") if "parent" in a
}


def boite(chemin):
    proprietes = noeuds[chemin]
    maillage = ressources[reference(proprietes["mesh"])]
    support = noeuds.get(chemin.rsplit("/", 1)[0], {}) if chemin.endswith("/Volume") else {}
    x, y, z = composantes(proprietes.get("position", support.get("position", "Vector3(0, 0, 0)")))
    sx, sy, sz = composantes(maillage["size"])
    rotation = composantes(support.get("rotation", "Vector3(0, 0, 0)"))
    return Vector((x, -z, y)), Vector((sx, sz, sy)), Euler((rotation[0], -rotation[2], rotation[1]))


def matiere(nom, teinte):
    mat = bpy.data.materials.new(nom)
    mat.diffuse_color = (*teinte, 1)
    mat.use_nodes = True
    surface = mat.node_tree.nodes.get("Principled BSDF")
    surface.inputs["Base Color"].default_value = (*teinte, 1)
    surface.inputs["Roughness"].default_value = .88
    return mat


def gamme(nom, teintes):
    return [matiere(f"{nom} {i + 1}", couleur) for i, couleur in enumerate(teintes)]


sols = [
    gamme("Sable humide", [(0.57, .40, .24), (.63, .47, .29), (.68, .51, .32), (.7, .54, .35)]),
    gamme("Terre ocre", [(.56, .36, .22), (.66, .46, .28), (.67, .49, .32), (.62, .42, .26)]),
    gamme("Argile pêche", [(.64, .35, .25), (.71, .43, .31), (.76, .48, .36), (.68, .4, .31)]),
    gamme("Herbe tendre", [(.31, .42, .20), (.40, .48, .23), (.46, .52, .27), (.38, .45, .22)]),
    gamme("Fond marin", [(.16, .29, .25), (.18, .32, .28), (.21, .35, .31), (.24, .38, .32)]),
]
roches = [
    gamme("Roche ocre", [(.55, .28, .20), (.63, .33, .23), (.69, .38, .27)]),
    gamme("Strate pêche", [(.74, .42, .30), (.80, .48, .35), (.70, .39, .30)]),
    gamme("Strate rose", [(.52, .24, .20), (.59, .30, .23), (.63, .31, .26)]),
]
dalles = gamme("Calcaire", [(.72, .54, .36), (.79, .63, .44), (.83, .67, .49), (.73, .57, .40)])
jardin = gamme("Jardin", [(.49, .50, .26), (.54, .54, .30), (.57, .57, .31)])
herbe_seche = gamme("Herbe sèche", [(.39,.39,.18), (.45,.45,.23), (.49,.49,.25)])
lichens = gamme("Lichen doré", [(.52,.43,.20), (.58,.49,.23)])
brins = gamme("Touffes", [(.26,.36,.15), (.36,.44,.18), (.47,.50,.23)])
ruines = gamme("Pierre engloutie", [(.28, .42, .36), (.32, .49, .43), (.35, .50, .46)])


class Volume:
    def __init__(self):
        self.sommets = []
        self.faces = []
        self.materiaux = []

    def face(self, points, mat):
        i = len(self.sommets)
        self.sommets.extend(points)
        self.faces.append(tuple(range(i, i + len(points))))
        self.materiaux.append(mat)

    def creer(self, nom):
        geo = bpy.data.meshes.new(nom)
        geo.from_pydata(self.sommets, [], self.faces)
        geo.update()
        obj = bpy.data.objects.new(nom, geo)
        scene.collection.objects.link(obj)
        materiaux = list(dict.fromkeys(self.materiaux))
        for mat in materiaux:
            geo.materials.append(mat)
        indices = {mat: i for i, mat in enumerate(materiaux)}
        for poly, mat in zip(geo.polygons, self.materiaux):
            poly.material_index = indices[mat]
        return obj


def limites(c, s):
    return c.x - s.x / 2, c.x + s.x / 2, c.y - s.y / 2, c.y + s.y / 2


terrasses = []
paves = []
acces = []
for chemin in noeuds:
    if chemin.startswith("Relief/") and chemin.endswith("/Volume"):
        c, s, _ = boite(chemin)
        groupe = chemin.split("/")[1]
        niveau = ("Quai", "VilleBasse", "VilleHaute", "Crete", "FondDuLagon").index(groupe)
        terrasses.append((*limites(c, s), c.z + s.z / 2, niveau))
    elif chemin.startswith("Acces/") and chemin.endswith("/Volume"):
        c, s, rotation = boite(chemin)
        matrice = rotation.to_matrix()
        acces.append((c, s, matrice.transposed()))
    elif chemin.startswith("SolsAmenages/") and "mesh" in noeuds[chemin] and not chemin.endswith("/Volume"):
        c, s, _ = boite(chemin)
        zone = chemin.split("/")[1]
        gamme_sol = ruines if zone == "VieuxPort" else jardin if "EmpriseSerre" in chemin or zone == "JardinDuHaut" else dalles
        paves.append((*limites(c, s), c.z, gamme_sol))


def echantillons(bords, pas):
    points = sorted({round(v, 4) for v in bords})
    return [
        a + (b-a)*i/math.ceil((b-a)/pas)
        for a, b in zip(points, points[1:]) for i in range(math.ceil((b-a)/pas))
    ] + points[-1:]


limites_sol = terrasses + paves
xs = echantillons([v for p in limites_sol for v in p[:2]], 1.65)
ys = echantillons([v for p in limites_sol for v in p[2:4]], 1.65)


def contient(zone, x, y):
    return zone[0] <= x <= zone[1] and zone[2] <= y <= zone[3]


cases = {}
for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
    for j, (y0, y1) in enumerate(zip(ys, ys[1:])):
        x, y = (x0+x1)/2, (y0+y1)/2
        zones = [t for t in terrasses if contient(t, x, y)]
        if zones:
            cases[i, j] = max(zones, key=lambda t: t[4])


def relief(x, y):
    return (math.sin(x*1.21 + y*.83)*.038 + math.cos(y*1.86 - x*.65)*.024)


def pres_acces(x, y, z, marge):
    for centre, taille, inverse in acces:
        local = inverse @ (Vector((x, y, z)) - centre)
        if (abs(local.x) < taille.x / 2 + marge
                and abs(local.y) < taille.y / 2 + marge
                and abs(local.z) < 1.1):
            return True
    return False


def cotes(i, j):
    x0, x1, y0, y1 = xs[i], xs[i+1], ys[j], ys[j+1]
    tour = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for k, direction in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
        yield tour[k], tour[(k+1) % 4], direction


# Les sommets du pourtour sont partagés par les plateaux et les falaises.
# Les normales cumulées adoucissent aussi les angles rentrants du lagon.
normales = {}
abords_paves = set()
for (i, j), case in cases.items():
    z = case[4]
    x, y = (xs[i]+xs[i+1])/2, (ys[j]+ys[j+1])/2
    pave = any(abs(p[4]-z) < .045 and contient(p, x, y) for p in paves)
    for a, b, (di, dj) in cotes(i, j):
        if pave:
            abords_paves.update((*point, z) for point in (a, b))
        voisin = cases.get((i+di, j+dj))
        if voisin and voisin[4] >= z:
            continue
        for point in (a, b):
            normales.setdefault((*point, z), set()).add((di, dj))

profils = {}
for (x, y, z), directions in sorted(normales.items()):
    normale = Vector((sum(dx for dx, _ in directions), sum(dy for _, dy in directions), 0))
    protege = (x, y, z) in abords_paves or pres_acces(x, y, z, 1.45)
    if normale.length and not protege:
        normale.normalize()
        amplitude = .30 + .27*math.sin(x*.64+y*.43) + .12*math.cos(y*.91-x*.53)
        if len(directions) > 1:
            amplitude -= .30
        profils[x, y, z] = (normale*amplitude, normale)


def bordure(x, y, z):
    position = Vector((x, y, z + relief(x, y)))
    profil = profils.get((x, y, z))
    return position + profil[0] if profil else position


def profil_falaise(point, haut, z, bas, fraction):
    pied = bordure(*point, bas)
    profil = profils.get((*point, z))
    position = haut.lerp(pied, fraction)
    if profil:
        x, y = point
        # Le talus s'élargit vers le bas. Les replats forment des lèvres continues.
        grain = math.sin(x*.49 + y*.57 + fraction*9)
        largeur = min(1.35, (z-bas)*.23)
        raccord = min(1, (1-fraction)*5) if bas > -2.7 else 1
        position += profil[1] * (largeur*fraction + .18*grain*math.sin(math.pi*fraction)) * raccord
        position.z += .13*grain*math.sin(math.pi*fraction)
    return position


def masse_vegetale(x, y):
    return math.sin(x*.39 + y*.21) + .58*math.cos(y*.62 - x*.31)


plateaux, falaises, vegetation, eboulis = Volume(), Volume(), Volume(), Volume()
dallage = Volume()
decor = random.Random(84)
for (i, j), (_, _, _, _, z, niveau) in cases.items():
    x0, x1, y0, y1 = xs[i], xs[i+1], ys[j], ys[j+1]
    x, y = (x0+x1)/2, (y0+y1)/2
    pave = next((p[5] for p in reversed(paves) if abs(p[4]-z)<.045 and contient(p,x,y)), None)
    masse = masse_vegetale(x, y)
    teintes = pave or sols[niveau]
    if niveau == 3 and not pave and masse < -.28:
        teintes = herbe_seche
    milieu = (x, y, z + relief(x,y) + (0.0 if pave else ALEA.uniform(-.035,.045)))
    if pave is dalles and min(x1-x0, y1-y0) > .34:
        joint = .018
        contour_dalle = [
            (x0+joint, y0+joint), (x1-joint, y0+joint),
            (x1-joint, y1-joint), (x0+joint, y1-joint),
        ]
        dessus_dalle = [(px, py, z + .07 + relief(px, py)) for px, py in contour_dalle]
        dessous_dalle = [(px, py, pz - .11) for px, py, pz in dessus_dalle]
        teinte_dalle = decor.choice(dalles)
        dallage.face(dessus_dalle, teinte_dalle)
        for bord in range(4):
            suivant = (bord + 1) % 4
            dallage.face([dessus_dalle[suivant], dessus_dalle[bord],
                          dessous_dalle[bord], dessous_dalle[suivant]], dalles[0])
    for a, b, (di, dj) in cotes(i, j):
        haut_a, haut_b = bordure(*a,z), bordure(*b,z)
        plateaux.face([haut_a, haut_b, milieu], ALEA.choice(teintes))
        if niveau == 3 and not pave and not pres_acces(x, y, z, 1.1):
            # Les plaques et les touffes prennent appui sur la face qui les porte.
            pa, pb, pm = map(Vector, (haut_a, haut_b, milieu))
            if (pb - pa).cross(pm - pa).length > .21:
                centre = pa*.24 + pb*.25 + pm*.51
                if masse < -.45 and decor.random() < .36:
                    bord = [centre.lerp(v, decor.uniform(.28, .53)) for v in (pa, pb, pm)]
                    leve = Vector((0, 0, .018))
                    vegetation.face([v + leve for v in bord], decor.choice(lichens))
                elif masse > .23 and decor.random() < .39:
                    for _ in range(decor.randint(3, 6)):
                        appui = centre.lerp(decor.choice((pa, pb, pm)), decor.uniform(.04, .25))
                        angle = decor.uniform(0, math.tau)
                        largeur = Vector((math.cos(angle), math.sin(angle), 0)) * decor.uniform(.022, .052)
                        pointe = appui + Vector((largeur.y, -largeur.x, decor.uniform(.095, .24)))
                        vegetation.face([appui-largeur, appui+largeur, pointe], decor.choice(brins))
        voisin = cases.get((i+di,j+dj))
        bas = voisin[4] if voisin else -2.75
        if bas >= z:
            continue
        hauteur = z-bas
        nb = max(1, round(hauteur/.76))
        degage = not pres_acces((a[0]+b[0])/2, (a[1]+b[1])/2, z, 1.2)
        ligne = [haut_a, haut_b]
        for strate in range(1, nb+1):
            # Une lèvre mince et une face large par strate, sans joints de briques.
            fraction = strate / nb
            avant = fraction - .19 / nb
            levre = [profil_falaise(p, h, z, bas, avant) for p, h in zip((a, b), (haut_a, haut_b))]
            suivante = [profil_falaise(p, h, z, bas, fraction) for p, h in zip((a, b), (haut_a, haut_b))]
            mat = roches[(strate-1) % len(roches)]
            teinte = mat[int(abs(math.sin(x*.41+y*.39+strate)) * (len(mat)-.01))]
            falaises.face([ligne[1], ligne[0], levre[0]], teinte)
            falaises.face([ligne[1], levre[0], levre[1]], teinte)
            falaises.face([levre[1], levre[0], suivante[0]], mat[0])
            falaises.face([levre[1], suivante[0], suivante[1]], mat[0])
            ligne = suivante
        if voisin is None and degage and math.dist(a, b) > .65 and decor.random() < .57:
            # Petits éboulis au pied des parois qui plongent dans l'eau.
            cx = (a[0]+b[0])/2 + di*decor.uniform(.22, .63)
            cy = (a[1]+b[1])/2 + dj*decor.uniform(.22, .63)
            rayon = decor.uniform(.23, .61)
            anneau = [
                Vector((cx + math.cos(t)*rayon, cy + math.sin(t)*rayon, -2.65))
                for t in (0, 1.1, 2.2, 3.5, 4.7, 5.6)
            ]
            sommet = Vector((cx + rayon*.18, cy - rayon*.2, -2.65 + rayon*1.4))
            for v1, v2 in zip(anneau, anneau[1:] + anneau[:1]):
                eboulis.face([v1, v2, sommet], decor.choice(roches[0]))

objets = [plateaux.creer("Terrasses et dallages"), falaises.creer("Falaises stratifiées"),
          vegetation.creer("Herbe rase et lichens"), eboulis.creer("Éboulis du rivage"),
          dallage.creer("Dalles du quai et des rues")]


def pierre(nom, centre, taille, rotation, teintes, chanfrein=.1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre, rotation=rotation)
    obj = bpy.context.object
    obj.name = nom
    obj.dimensions = taille
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for mat in teintes:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = ALEA.randrange(len(teintes))
    mod = obj.modifiers.new("Angles taillés", "BEVEL")
    mod.width = chanfrein
    mod.segments = 1
    return obj


digue = Volume()
pavage_acces = Volume()
for chemin in noeuds:
    if chemin.startswith("Acces/") and chemin.endswith("/Volume"):
        c,s,rot = boite(chemin)
        nom = chemin.split("/")[1]
        if nom in ("PalierDigue", "PalierJardin"):
            c.z += .025
        objets.append(pierre(nom,c,s,rot,[dalles[0]],.065))
        if min(s.x, s.y) >= 2:
            nx, ny = max(2, round(s.x/.95)), max(2, round(s.y/.95))
            dx, dy = s.x/nx, s.y/ny
            matrice = rot.to_matrix()
            for ix in range(nx):
                for iy in range(ny):
                    x, y = -s.x/2 + ix*dx, -s.y/2 + iy*dy
                    contour_dalle = [
                        c + matrice @ Vector((x+u,y+v,s.z/2+.006))
                        for u,v in [(.025,.025),(dx-.025,.025),(dx-.025,dy-.025),(.025,dy-.025)]
                    ]
                    pavage_acces.face(contour_dalle,ALEA.choice(dalles))
        if nom.startswith(("Canal_", "DigueEst")) or nom in ("PalierDigue", "PalierJardin"):
            # Le chemin du canal repose sur une digue taillée, avec un pied évasé.
            contour = [
                c + rot.to_matrix() @ Vector((dx*s.x/2, dy*s.y/2, -s.z/2))
                for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]
            ]
            for i, (a, b) in enumerate(zip(contour, contour[1:] + contour[:1])):
                bas = [
                    Vector((v.x + .13 * (v.x-c.x), v.y + .13 * (v.y-c.y), -2.75))
                    for v in (a, b)
                ]
                ligne = [a, b]
                for j in range(1, 5):
                    suivante = [v.lerp(w,j/4) for v,w in zip((a,b),bas)]
                    mat = roches[j % len(roches)]
                    digue.face([ligne[1],ligne[0],suivante[0]],mat[i % len(mat)])
                    digue.face([ligne[1],suivante[0],suivante[1]],mat[(i+1) % len(mat)])
                    ligne = suivante
    if chemin.startswith("SolsAmenages/VieuxPort/Fondations") and chemin.endswith("/Volume"):
        c,s,rot = boite(chemin)
        objets.append(pierre("Arase du vieux port",c,s,rot,ruines))

objets.append(digue.creer("Digue du canal"))
objets.append(pavage_acces.creer("Pavage des accès"))

for x,y,angle in [(-12,-.2,.19), (-5,-11,.03), (7,-11,-.12), (12,1,.12), (-9,2,-.13)]:
    c = Vector((x,y,-1.00))
    objets.append(pierre("Vestige du vieux port",c,(2.6,2.3,.96),Euler((0,0,angle)),ruines,.21))

# Exporter le terrain seul. Les collisions sont conservées dans la scène Godot.
MODELE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
for obj in objets:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(MODELE), export_format="GLB", use_selection=True, export_apply=True)

# Les vues Blender emploient une eau transparente teintée pour lire le bassin.
eau = matiere("Eau turquoise", (.08,.43,.43))
eau.use_nodes = True
arbre = eau.node_tree
arbre.nodes.clear()
sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
surface = arbre.nodes.new("ShaderNodeBsdfPrincipled")
surface.inputs["Base Color"].default_value = (.045,.46,.43,1)
surface.inputs["Roughness"].default_value = .24
transparent = arbre.nodes.new("ShaderNodeBsdfTransparent")
transparent.inputs[0].default_value = (.56,.90,.88,1)
melange = arbre.nodes.new("ShaderNodeMixShader")
melange.inputs[0].default_value = .32
arbre.links.new(transparent.outputs[0],melange.inputs[1])
arbre.links.new(surface.outputs[0],melange.inputs[2])
arbre.links.new(melange.outputs[0],sortie.inputs[0])
bpy.ops.mesh.primitive_plane_add(size=350, location=(0,0,-.18))
bpy.context.object.name = "Mer et lagon"
bpy.context.object.data.materials.append(eau)
bpy.ops.mesh.primitive_plane_add(size=350, location=(0,0,-3.15))
bpy.context.object.name = "Fond marin de présentation"
bpy.context.object.data.materials.append(matiere("Turquoise profond",(.055,.35,.37)))

scene.world = bpy.data.worlds.new("Ciel clair")
scene.world.use_nodes = True
fond = scene.world.node_tree.nodes.get("Background")
fond.inputs[0].default_value = (.62,.76,1,1)
fond.inputs[1].default_value = .6
bpy.ops.object.light_add(type="SUN", rotation=Euler((.58,-.50,-.39)))
bpy.context.object.data.energy = 2.4
bpy.context.object.data.color = (1,.83,.69)
bpy.context.object.data.angle = .10
scene.render.engine = "CYCLES"
scene.cycles.samples = 10
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
RENDUS.mkdir(parents=True, exist_ok=True)


def camera(nom, position, cible, taille):
    bpy.ops.object.camera_add(location=position)
    obj = bpy.context.object
    obj.name = nom
    obj.rotation_euler = (Vector(cible)-obj.location).to_track_quat("-Z","Y").to_euler()
    if taille:
        obj.data.type = "ORTHO"
        obj.data.ortho_scale = taille
    else:
        obj.data.lens = 29
    return obj


ensemble = camera("Île entière", (78,-106,91), (0,2,0), 107)
dessus = camera("Vue de dessus", (0,-17,104), (0,2,0), 105)
quai = camera("Arrivée au quai", (-30,-39,14), (-25,-22,2.2), None)
scene.camera = ensemble
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(RENDUS / "terrain_colonie.blend"), compress=True)
for cam, nom in [(ensemble,"colonie_ensemble.png"),(quai,"colonie_quai.png"), (dessus,"colonie_terrain_dessus.png")]:
    scene.camera = cam
    scene.render.filepath = str(RENDUS / nom)
    bpy.ops.render.render(write_still=True)
