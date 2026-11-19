"""Hangar de réparation, bouée et échelle de marée de l’île du Phare.

Blender Z monte et -Y regarde le quai. L'origine du hangar est son seuil fini.
Voir ILE_02_PHARE.md. Exports GLB dans assets/models/ile02.
"""
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "assets/models/ile02"
SOURCES = Path(__file__).parent / "sources/hangar_quai"
ALEA = random.Random(23)
bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(nom, hexcol, metal=0.0):
    m = bpy.data.materials.new(nom)
    srgb = [int(hexcol[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgba = tuple(c / 12.92 if c < 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb) + (1,)
    m.diffuse_color = rgba
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = rgba
    p.inputs["Roughness"].default_value = 0.73
    p.inputs["Metallic"].default_value = metal
    return m


pierre = [mat("Calcaire " + str(i), c) for i, c in enumerate(("ded0b7", "cec1ab", "ede4d1", "d9cbb8"))]
pins = [mat("Pin " + str(i), c) for i, c in enumerate(("c79b69", "d8b182", "e0bb8e", "b98756"))]
bleus = [mat("Bardage " + str(i), c) for i, c in enumerate(("81a6ae", "8bb2b9", "9abfc3", "749aa4"))]
ardoises = [mat("Ardoise " + str(i), c) for i, c in enumerate(("596f7d", "647e90", "708b98"))]
chene = mat("Chêne des membrures", "9c6540")
creme = mat("Peinture ivoire", "f3e3c5")
or_pale = mat("Laiton patiné", "d4aa61", .42)
fer = mat("Fonte bleutée", "485a61", .28)
cuivre = mat("Cuivre corail", "b96350", .36)
toile = mat("Toile écrue", "e9d2a7")
corde = mat("Corde tressée", "b48b5e")
verre = mat("Verre dépoli", "a9d6d1")
jaune = mat("Butées dorées", "e5b969")
ambre = mat("Cristal ambre", "f9bd6e")


def groupe(nom):
    objet = bpy.data.objects.new(nom, None)
    bpy.context.collection.objects.link(objet)
    return objet


def finir(objet, nom, materiau, parent):
    objet.name = nom
    objet.data.materials.append(materiau)
    objet.parent = parent
    return objet


def boite(nom, pos, taille, materiau, parent, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    objet = finir(bpy.context.object, nom, materiau, parent)
    objet.scale = taille
    objet.rotation_euler.y = angle
    return objet


def cylindre(nom, pos, rayon, haut, materiau, parent, faces=12, rayon_haut=None):
    bpy.ops.mesh.primitive_cone_add(vertices=faces, radius1=rayon,
                                   radius2=rayon if rayon_haut is None else rayon_haut,
                                   depth=haut, location=pos)
    return finir(bpy.context.object, nom, materiau, parent)


def barre(nom, a, b, section, materiau, parent):
    a, b = Vector(a), Vector(b)
    objet = boite(nom, (a + b) / 2, (*section, (b - a).length), materiau, parent)
    objet.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return objet


def rondin(nom, a, b, rayon, materiau, parent, faces=8):
    a, b = Vector(a), Vector(b)
    objet = cylindre(nom, (a + b) / 2, rayon, (b - a).length, materiau, parent, faces)
    objet.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return objet


def anneau(nom, pos, rayon, ep, materiau, parent):
    bpy.ops.mesh.primitive_torus_add(location=pos, major_segments=20, minor_segments=6,
                                    major_radius=rayon, minor_radius=ep)
    return finir(bpy.context.object, nom, materiau, parent)


def mesh(nom, sommets, faces, matiere, parent):
    donnees = bpy.data.meshes.new(nom)
    donnees.from_pydata(sommets, [], faces)
    objet = bpy.data.objects.new(nom, donnees)
    bpy.context.collection.objects.link(objet)
    return finir(objet, nom, matiere, parent)


def inscription(nom, contenu, pos, taille, matiere, parent):
    bpy.ops.object.text_add(location=pos, rotation=(math.pi / 2, 0, 0))
    texte = bpy.context.object
    texte.data.body = contenu
    texte.data.align_x = 'CENTER'
    texte.data.align_y = 'CENTER'
    texte.data.size = taille
    bpy.ops.object.convert(target='MESH')
    return finir(bpy.context.object, nom, matiere, parent)


def regrouper(racine):
    """Réunit les pièces répétées du même matériau dans chaque groupe de coupe."""
    lots = defaultdict(list)
    for objet in racine.children:
        lots[objet.data.materials[0]].append(objet)
    for matiere, objets in lots.items():
        bpy.ops.object.select_all(action='DESELECT')
        for objet in objets:
            objet.select_set(True)
        bpy.context.view_layer.objects.active = objets[0]
        if len(objets) > 1:
            bpy.ops.object.join()
        objets[0].name = racine.name + " · " + matiere.name


def export(nom, groupes):
    bpy.ops.object.select_all(action='DESELECT')
    for racine in groupes:
        for objet in (racine, *racine.children_recursive):
            objet.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(SORTIE / (nom + ".glb")), export_format="GLB",
                              use_selection=True, export_animations=False)


def coque(pos, longueur, largeur, matiere, parent, retournee):
    x, y, z = pos
    stations = [(-.50, .09), (-.39, .69), (-.23, .94), (0, 1), (.26, .91), (.43, .56), (.50, .02)]
    profils = [(-1, .31), (-.76, .12), (-.43, -.13), (0, -.21),
               (.43, -.13), (.76, .12), (1, .31)]
    facteur = -1 if retournee else 1
    sommets = [(x + px * demi * largeur / 2, y + py * longueur,
                z + facteur * (pz + .13 * (1 - demi)))
               for py, demi in stations for px, pz in profils]
    for j in range(len(profils) - 1):
        faces = [(i*7+j, (i+1)*7+j, (i+1)*7+j+1, i*7+j+1) for i in range(6)]
        mesh("Bordé de barque", sommets, faces, matiere if j in (0, 5) else pins[j % 3], parent)
    for j in (0, 6):
        for i in range(6):
            rondin("Lisse de coque", sommets[i*7+j], sommets[(i+1)*7+j], .054, creme, parent)
    if not retournee:
        for dy, demi in stations[2:5]:
            pts = [(x + px * demi * largeur / 2, y + dy * longueur, z + pz + .05) for px, pz in profils]
            for a, b in zip(pts, pts[1:]):
                barre("Membrure de réparation", a, b, (.07, .09), chene, parent)
        boite("Banc démonté", (x, y+.22, z+.20), (largeur*.78, .38, .11), pins[2], parent)


def caisse(x, y, z, parent, taille=.68):
    boite("Caisse d'accastillage", (x, y, z + taille/2), (taille, taille*.76, taille), pins[1], parent)
    for dx in (-.33, .33):
        boite("Renfort de caisse", (x + dx*taille, y - taille*.394, z+taille/2),
              (.084, .04, taille), chene, parent)
    boite("Gravure de rangement", (x, y-taille*.403,z+taille*.68), (.19,.018,.055), fer, parent)


def modele_meshy(nom, pos, longueur, matiere, parent, horizontal=False):
    fichier = SOURCES / (nom + ".glb")
    if not fichier.is_file():
        return
    avant = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(fichier))
    importes = set(bpy.data.objects) - avant
    objets = [o for o in importes if o.type == "MESH"]
    points = [objet.matrix_world @ Vector(point) for objet in objets for point in objet.bound_box]
    bas = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    haut = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    facteur = longueur / max(haut - bas)
    centre = (bas + haut) / 2
    centre.z = bas.z
    for objet in objets:
        matrice = objet.matrix_world.copy()
        objet.data = objet.data.copy()
        objet.data.transform(matrice)
        for sommet in objet.data.vertices:
            sommet.co = (sommet.co - centre) * facteur
            if horizontal and haut.z - bas.z > max(haut.x - bas.x, haut.y - bas.y):
                sommet.co = Vector((sommet.co.z - longueur / 2, sommet.co.y,
                                    -sommet.co.x + (haut.x - bas.x)*facteur/2))
        objet.parent = parent
        objet.matrix_parent_inverse = Matrix.Identity(4)
        objet.location = pos
        objet.rotation_euler = (0, 0, 0)
        objet.scale = (1, 1, 1)
        objet.data.materials.clear()
        objet.data.materials.append(matiere)
        for face in objet.data.polygons:
            face.material_index = 0
            face.use_smooth = False
    for objet in importes - set(objets):
        bpy.data.objects.remove(objet, do_unlink=True)


def hangar():
    fixe, coupe, toit = (groupe(n) for n in ("Atelier", "Coupe", "Toit"))
    # Assise, allée et chariots laissent le seuil à niveau avec le quai.
    boite("Assise de calcaire", (0, 0, -.15), (9.4, 8.92, .30), pierre[1], fixe)
    rampe = [(-1.81,-4.46,.044),(1.81,-4.46,.044),(1.81,-5.42,-.106),(-1.81,-5.42,-.106)]
    mesh("Rampe du seuil", rampe, [(0,3,2,1)], pierre[0], fixe)
    for k in range(23):
        x = -4.40 + k*.40
        boite("Plancher de pin", (x, 0, .014), (.391, 8.78, .06), pins[k % 4], fixe)
    for x in (-.86, .86):
        boite("Rail de mise sur ber", (x, -.47, .051), (.075, 7.4, .038), fer, fixe)
        for y in (-3.95, 3.23):
            boite("Butée du rail", (x, y, .085), (.16, .25, .12), or_pale, fixe)
    # Murs en planches et hautes fenêtres. La façade sud s'efface avec la toiture.
    for signe in (-1, 1):
        x = signe*4.51
        boite("Mur bahut latéral", (x, 0, .38), (.28, 8.9, .76), pierre[0], fixe)
        for j in range(22):
            y = -4.2 + j*.4
            baie = -2.2 < y < -.52 or .97 < y < 2.56
            boite("Soubassement en bois", (x, y, 1.23), (.21, .392, .98), bleus[j%4], fixe)
            bas_bardage = 3.98 if baie else 1.72
            boite("Bardage latéral haut", (x, y, (bas_bardage + 4.49)/2),
                  (.21, .392, 4.49-bas_bardage), bleus[j%4], coupe)
            if baie:
                boite("Allège de baie", (x, y, 1.81), (.21,.392,.18), bleus[j%4], coupe)
        for y in (-1.36, 1.77):
            boite("Jour de l’atelier", (x, y, 2.86), (.09, 1.62, 1.85), verre, coupe)
            for dy in (-.84, 0, .84):
                boite("Meneau", (x, y+dy, 2.86), (.32,.09,1.95), creme, coupe)
            for z in (1.90,2.85,3.82):
                boite("Traverse de baie", (x, y, z), (.38,1.76,.09), creme, coupe)
    for j in range(22):
        x = -4.24 + j*.405
        boite("Bardage du fond", (x, 4.36, 2.25), (.398, .20, 4.50), bleus[j%4], fixe)
        if abs(x) > 1.89:
            boite("Bardage du quai", (x, -4.36, .44), (.398,.23,.87), pierre[j%4], fixe)
            boite("Façade du quai", (x, -4.36, 2.65), (.398,.23,3.60), bleus[j%4], coupe)
    for x in (-4.52, -1.91, 1.91, 4.52):
        boite("Montant de façade", (x, -4.39, 2.26), (.20,.31,4.52), creme, coupe)
    for y in (-4.38, -.17, 4.34):
        barre("Entrait de ferme", (-4.55,y,4.48),(4.55,y,4.48),(.23,.25),chene,toit)
        barre("Poinçon", (0,y,4.46),(0,y,6.64),(.24,.23),chene,toit)
        for s in (-1, 1):
            barre("Arbalétrier", (s*4.7,y,4.39),(0,y,6.56),(.22,.27),chene,toit)
            barre("Contrefiche", (0,y,4.55),(s*2.68,y,5.45),(.16,.19),pins[0],toit)
    for y in (-4.38, 4.38):
        mesh("Pignon de bois", [(-4.56,y,4.51),(4.56,y,4.51),(0,y,6.64)],
             [(0,1,2)], bleus[3], toit)
    for s in (-1, 1):
        for j in range(6):
            d = j*.85+.43
            x, z = s*d*.906, 6.83-d*.423
            for k in range(9):
                y = -4.32+k*1.08
                boite("Ardoise en écaille", (x,y,z), (.92,1.10,.10), ALEA.choice(ardoises), toit, s*.436)
        barre("Rive peinte", (0,-4.92,6.89),(s*4.7,-4.92,4.70),(.19,.17),creme,toit)
        rondin("Gouttière", (s*4.77,-4.92,4.60),(s*4.77,4.92,4.60),.13,cuivre,toit)
    rondin("Faîtière", (0,-4.98,6.88),(0,4.98,6.88),.14,or_pale,toit)
    boite("Rail mural de porte", (0,-4.53,3.81), (8.1,.13,.14), fer, coupe)
    boite("Enseigne peinte", (0,-4.51,4.28), (3.47,.17,.53), bleus[3], coupe)
    inscription("Nom du hangar", "CHANTIER DU QUAI", (0,-4.61,4.28), .28, creme, coupe)
    for x in (-1.79, 1.79):
        boite("Butoir de porte", (x,-4.63,3.83), (.11,.12,.27), cuivre, coupe)
    for x in (-4.54,4.54):
        rondin("Descente de gouttière", (x,-4.57,.23),(x,-4.57,4.56),.077,cuivre,coupe)
    # À bâbord une coque sèche sur tréteaux. À tribord le chantier encore en cours.
    for x,y in ((-2.94,-1.04),(2.98,.22)):
        for dy in (-1.03,1.03):
            for dx in (-.48,.48):
                barre("Pied de tréteau", (x+dx*1.18,y+dy,.06),(x+dx*.71,y+dy,.53),(.13,.17),chene,fixe)
            boite("Traverse de ber", (x,y+dy,.54),(1.48,.29,.18),pins[1],fixe)
    coque((-2.94,-1.04,.92), 3.88, 1.74, cuivre, fixe, True)
    coque((2.98,.22,.82), 4.24, 1.72, bleus[3], fixe, False)
    # Établi au fond, outils à hauteur de Semeur et accastillage en cours de tri.
    for x in (-3.91,-1.24):
        for y in (3.26,4.08):
            boite("Pied d’établi", (x,y,.63), (.18,.18,1.16),chene,fixe)
    boite("Plateau d’établi", (-2.58,3.67,1.22),(3.03,1.12,.17),pins[2],fixe)
    boite("Étagère basse", (-2.58,3.70,.38),(2.77,.95,.10),pins[1],fixe)
    boite("Panneau d’outils", (-2.58,4.22,2.12),(3.07,.09,1.27),pins[1],fixe)
    for x in (-3.55,-3.17,-2.71,-2.37):
        barre("Manche d’outil", (x,4.11,1.75),(x+.09,4.10,2.38),(.09,.083),chene,fixe)
        boite("Fer d’outil", (x+.09,4.09,2.35),(.20,.12,.13),fer,fixe)
    for i in range(3):
        anneau("Couronne de corde", (-1.87,3.76,1.35+i*.052),.26-i*.024,.036,corde,fixe)
    boite("Étau", (-3.57,3.23,1.45),(.40,.33,.27),fer,fixe)
    rondin("Vis de l’étau", (-3.57,2.95,1.43),(-3.57,3.36,1.43),.055,or_pale,fixe)
    rondin("Poignée d’étau", (-3.78,2.97,1.43),(-3.33,2.97,1.43),.041,fer,fixe)
    for x,y,z,t in ((3.64,3.75,.05,.72),(2.89,3.88,.05,.67),(3.63,3.75,.77,.52),(-3.71,1.88,.05,.73)):
        caisse(x,y,z,fixe,t)
    for x in (2.0,2.42,2.84):
        barre("Planche de rechange", (x,3.76,.06),(x+.29,4.22,2.45),(.17,.085),pins[2],fixe)
    for y in (1.92,2.23):
        barre("Gaffe", (-4.14,y,.05),(-4.38,y+.67,3.25),(.073,.067),chene,fixe)
    for x in (-3.9,3.9):
        boite("Patère d’atelier", (x,4.23,2.77),(.23,.21,.13),or_pale,fixe)
    for x in (-2.55,2.54):
        rondin("Tringle de suspension", (x,-.16,4.48),(x,-.16,3.61),.027,fer,toit)
        cylindre("Abat-jour émaillé", (x,-.16,3.52),.33,.23,bleus[3],toit,12,.11)
        cylindre("Verre de lampe suspendue", (x,-.16,3.39),.12,.13,ambre,toit)
    modele_meshy("grappin", (3.84,2.22,.06), .94, fer, fixe)
    modele_meshy("toile_voile", (-2.75,3.60,1.31), .88, toile, fixe, horizontal=True)
    for racine in (fixe, coupe, toit):
        regrouper(racine)
    export("hangar_quai", (fixe, coupe, toit))
    return fixe, coupe, toit


def porte():
    parent = groupe("Vantail")
    for j in range(8):
        boite("Planche peinte", (-.796+j*.228,0,1.74),(.225,.16,3.45),bleus[j%4],parent)
    for z in (.20,1.91,3.33):
        boite("Traverse de vantail", (0,-.093,z),(1.80,.092,.17),creme,parent)
        for x in (-.75,.75):
            rondin("Rivet forgé", (x,-.155,z),(x,-.133,z),.052,fer,parent)
    barre("Écharpe du vantail", (-.72,-.109,.29),(.72,-.109,3.22),(.13,.09),creme,parent)
    for x in (-.67,.67):
        boite("Coulisse de porte", (x,-.07,3.55),(.25,.24,.31),fer,parent)
    rondin("Poignée en laiton", (.56,-.22,1.34),(.56,-.22,1.66),.048,or_pale,parent)
    export("vantail_hangar", (parent,))
    return parent


def bouee():
    parent = groupe("Bouee")
    for z, r1, r2, hauteur, matiere in ((-.18,.54,.88,.38,cuivre),(.08,.88,.85,.18,creme),
            (.27,.85,.60,.20,cuivre),(.43,.60,.45,.14,or_pale)):
        cylindre("Flotteur riveté", (0,0,z),r1,hauteur,matiere,parent,12,r2)
    for i in range(8):
        a = i*math.tau/8
        x,y = math.cos(a),math.sin(a)
        cylindre("Rivet du flotteur", (x*.67,y*.67,.38),.05,.085,or_pale,parent,6)
        if i%2 == 0:
            rondin("Montant de protection", (x*.42,y*.42,.45),(x*.30,y*.30,1.58),.065,fer,parent)
    cylindre("Socle optique", (0,0,.78),.40,.18,fer,parent,10)
    cristal = ambre.copy()
    cristal.name = "Feu de la bouée"
    cristal_bsdf = cristal.node_tree.nodes.get("Principled BSDF")
    cristal_bsdf.inputs["Emission Color"].default_value = (1.0,.49,.14,1)
    cristal_bsdf.inputs["Emission Strength"].default_value = 0.85
    cylindre("Cristal de la bouée", (0,0,1.14),.26,.66,cristal,parent,10,.22)
    cylindre("Chapeau conique", (0,0,1.57),.45,.30,or_pale,parent,10,.16)
    crochet = anneau("Œil de levage", (0,0,1.82),.118,.035,fer,parent)
    crochet.rotation_euler.x = math.pi/2
    for x in (-.55,.55):
        borne = anneau("Brague d’amarrage", (x,-.29,.38),.087,.036,fer,parent)
        borne.rotation_euler.x = math.pi/2
    export("bouee_quai", (parent,))
    return parent


def echelle_maree():
    parent = groupe("EchelleDeMaree")
    boite("Pierre de jauge", (0,0,-.22),(.99,.40,2.44),pierre[1],parent)
    boite("Patte scellée dans le quai", (0,.48,.30),(.78,.98,.31),pierre[1],parent)
    boite("Patte basse de la jauge", (0,.42,-.51),(.74,.86,.24),pierre[0],parent)
    boite("Bande peinte", (0,-.207,-.15),(.68,.022,1.81),creme,parent)
    for k in range(12):
        z = -.60+k*.10
        grand = k in (0,6,11)
        boite("Trait de marée", (-.06 if grand else .00,-.224,z),
              (.49 if grand else .34,.012,.04 if grand else .021),cuivre if k==11 else bleus[3],parent)
    inscription("Repère haut", "HAUTE", (0,-.231,.65),.225,fer,parent)
    inscription("Repère bas", "BASSE", (0,-.231,-.78),.195,fer,parent)
    boite("Tête chanfreinée", (0,0,1.01),(1.12,.48,.15),pierre[2],parent)
    export("echelle_maree_quai", (parent,))
    return parent


def rendre(nom, position, visee, largeur):
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=position)
    camera = bpy.context.object
    camera.rotation_euler = (Vector(visee)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = largeur
    scene.camera = camera
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'MATERIAL'
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.show_shadows = True
    shading.background_type = 'WORLD'
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Fond de présentation")
    scene.world.color = (.21,.28,.32)
    scene.view_settings.view_transform = 'Standard'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 860
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(RACINE / "captures" / (nom + ".png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    fixe, coupe, toit = hangar()
    vantail, flotteur, jauge = porte(), bouee(), echelle_maree()
    if "--rendus" in sys.argv:
        flotteur.location = (6,-2,0)
        jauge.location = (-5.7,-3.6,0)
        vantail.location = (-.92,-4.55,0)
        droit = groupe("Vantail droit")
        for original in vantail.children:
            copie = original.copy()
            bpy.context.collection.objects.link(copie)
            copie.parent = droit
        droit.location = (.92,-4.55,0)
        droit.scale.x = -1
        rendre("hangar_quai_exterieur", (11,-17,12), (0,-.25,2.8), 17.6)
        for racine in (toit,coupe,vantail,droit,flotteur,jauge):
            for objet in racine.children_recursive:
                objet.hide_render = True
        rendre("hangar_quai_interieur", (9,-14,19), (0,0,.9), 15.8)
