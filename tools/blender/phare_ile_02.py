"""Construit la maquette du Phare et rend trois vues dans concept/phare_ile_02/.

Exécution : blender -b -t 8 --python tools/blender/phare_ile_02.py
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector


RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "concept/phare_ile_02"
MODELES = RACINE / "assets/models"
TAU = math.tau
RACINE_PHARE = Vector((0, 10.5, 8.1))


def collection(nom):
    groupe = bpy.data.collections.new(nom)
    bpy.context.scene.collection.children.link(groupe)
    return groupe


def ranger(objet, groupe):
    for ancienne in list(objet.users_collection):
        ancienne.objects.unlink(objet)
    groupe.objects.link(objet)
    return objet


def mat(nom, couleur, metal=0.0, rugosite=0.75):
    materiau = bpy.data.materials.new(nom)
    materiau.diffuse_color = (*couleur, 1)
    materiau.use_nodes = True
    surface = next(n for n in materiau.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    surface.inputs["Base Color"].default_value = (*couleur, 1)
    surface.inputs["Metallic"].default_value = metal
    surface.inputs["Roughness"].default_value = rugosite
    return materiau


def objet(nom, sommets, faces, matiere, groupe):
    maillage = bpy.data.meshes.new(nom)
    maillage.from_pydata(sommets, [], faces)
    maillage.update()
    resultat = bpy.data.objects.new(nom, maillage)
    groupe.objects.link(resultat)
    if matiere:
        maillage.materials.append(matiere)
    return resultat


def piece(nom, points, matiere, groupe):
    return objet(nom, points, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], matiere, groupe)


def boite(nom, centre, taille, matiere, groupe, chanfrein=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    o = ranger(bpy.context.object, groupe)
    o.name = nom
    o.dimensions = taille
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if matiere:
        o.data.materials.append(matiere)
    if chanfrein:
        biseau = o.modifiers.new("Arêtes taillées", "BEVEL")
        biseau.width = chanfrein
        biseau.segments = 1
    return o


def cercle(rayon, z, nombre=8, phase=-math.pi / 8):
    return [Vector((rayon * math.cos(phase + i * TAU / nombre),
                    rayon * math.sin(phase + i * TAU / nombre), z)) for i in range(nombre)]


def profil(nom, anneaux, matiere, groupe, nombre=8, fermer=True):
    sommets = [point for rayon, z in anneaux for point in cercle(rayon, z, nombre)]
    faces = []
    for rang in range(len(anneaux) - 1):
        for i in range(nombre):
            a = rang * nombre + i
            b = rang * nombre + (i + 1) % nombre
            faces.append((a, b, b + nombre, a + nombre))
    if fermer:
        faces.extend((tuple(reversed(range(nombre))),
                      tuple(range(len(sommets) - nombre, len(sommets)))))
    return objet(nom, sommets, faces, matiere, groupe)


def anneau(nom, rayon, largeur, bas, haut, matiere, groupe, nombre=8):
    interieur = rayon - largeur
    return profil(nom, [(interieur, haut), (interieur, bas), (rayon, bas), (rayon, haut),
                        (interieur, haut)], matiere, groupe, nombre, fermer=False)


def montant(nom, a, b, rayon, matiere, groupe, nombre=6, bout=None):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=nombre, radius1=rayon,
                                    radius2=rayon if bout is None else bout,
                                    depth=(b - a).length, location=(a + b) / 2)
    o = ranger(bpy.context.object, groupe)
    o.name = nom
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(matiere)
    return o


def mur(nom, rayon_bas, rayon_haut, bas, haut, cote, portion, matiere, groupe):
    u, v = portion
    j = (cote + 1) % 8
    points = []
    for rayon, z in [(rayon_bas, bas), (rayon_haut, haut)]:
        exterieur = cercle(rayon, z)
        interieur = cercle(rayon - 0.32, z)
        a, b = exterieur[cote], exterieur[j]
        c, d = interieur[cote], interieur[j]
        points.extend([a.lerp(b, u), a.lerp(b, v), c.lerp(d, v), c.lerp(d, u)])
    return piece(nom, points, matiere, groupe)


def importer(chemin, groupe):
    existants = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(chemin))
    nouveaux = set(bpy.data.objects) - existants
    formes_os = {os.custom_shape for o in nouveaux if o.type == "ARMATURE"
                 for os in o.pose.bones if os.custom_shape}
    objets_visibles = nouveaux - formes_os
    for o in objets_visibles:
        ranger(o, groupe)
    return objets_visibles


def origine(nom, position, groupe):
    pivot = bpy.data.objects.new(nom, None)
    groupe.objects.link(pivot)
    pivot.location = position
    return pivot


def construire_phare(palette):
    ivoire, sable, creme, terre, toit, bronze, or_pale, nuit, vitre, verre_bleu = palette
    coque = collection("Phare · enveloppe")
    niveaux = collection("Phare · quatre niveaux")
    optique = collection("Phare · galerie et optique")
    atelier = collection("Phare · organes mécaniques")
    racine = origine("Origine sur le plateau", RACINE_PHARE, coque)

    anneau("Plinthe taillée", 4.30, 0.82, -0.17, 0.17, sable, coque)
    anneau("Arête claire du soubassement", 4.08, 0.49, 0.16, 0.36, creme, coque)
    # La face sud (6) reçoit la porte. L'ouverture est dans le maillage.
    for cote in range(8):
        matiere = [ivoire, creme, ivoire, sable][cote % 4]
        for bas, haut, rb, rh in [(0.24, 1.24, 3.97, 3.88), (1.24, 2.72, 3.88, 3.78),
                                  (2.72, 3.40, 3.78, 3.73), (3.40, 4.15, 3.73, 3.70),
                                  (4.15, 4.84, 3.70, 3.62), (4.84, 7.42, 3.62, 3.45),
                                  (7.42, 9.18, 3.45, 3.35), (9.18, 10.72, 3.35, 3.25),
                                  (10.72, 12.47, 3.25, 3.13), (12.47, 13.30, 3.13, 3.03)]:
            portions = [(0, 1)]
            if cote == 6 and haut <= 3.40:
                portions = [(0, 0.14), (0.86, 1)] if haut <= 2.72 else [(0, 0.24), (0.76, 1)]
            if cote in (3, 5, 7) and bas in (4.84, 9.18):
                portions = [(0, 0.26), (0.74, 1)]
            for segment in portions:
                mur("Assise taillée", rb, rh, bas, haut, cote, segment,
                    terre if bas == 4.15 else matiere, coque)
    # Les deux contreforts sous la galerie prolongent les strates du rocher.
    for signe in (-1, 1):
        for bas, haut, rayon_bas, rayon_haut in [
            (0.05, 1.06, 4.27, 4.13), (1.06, 2.03, 4.12, 3.91),
            (2.03, 2.96, 3.90, 3.67), (2.96, 4.05, 3.66, 3.36),
            (4.05, 5.31, 3.35, 3.12), (5.31, 6.85, 3.11, 2.93),
        ]:
            d = Vector((signe * .78, -.626, 0))
            t = Vector((-d.y, d.x, 0))
            points = []
            for z, r in [(bas, rayon_bas), (haut, rayon_haut)]:
                points.extend(d*(r+dr) + t*dt + Vector((0,0,z))
                              for dr, dt in [(-.52,-.33), (0,-.25), (0,.25), (-.52,.33)])
            piece("Contrefort · bloc biseauté", points, sable if bas in (.05, 2.03) else ivoire, coque)
    # Clé de voûte et jambages en gros blocs, à l’échelle des Semeurs.
    for signe in (-1, 1):
        for i in range(3):
            boite("Jambage de l'entrée", (signe * 1.12, -3.63 + 0.055*i, 0.53 + 0.82*i),
                  (0.43, 0.66, 0.79), creme if i != 1 else sable, coque, 0.05)
        montant("Rein de l'arche", (signe * 1.13, -3.46, 2.42),
                (signe * 0.62, -3.43, 3.10), 0.25, creme, coque, 4)
    boite("Clef de voûte", (0, -3.45, 3.27), (1.34, 0.55, 0.41), creme, coque, 0.08)
    for i in range(3):
        boite("Marche du seuil", (0, -4.08 + i * 0.30, 0.06 + i * 0.05),
              (2.86, 0.58, 0.12 + i * 0.10), sable, coque, 0.035)
    for cote in (3, 5, 7):
        direction = (cercle(1, 0)[cote] + cercle(1, 0)[(cote + 1) % 8]).normalized()
        angle = math.atan2(direction.y, direction.x) - math.pi / 2
        for rayon, z in [(3.27, 4.86), (2.89, 9.21)]:
            o = boite("Appui de baie", (*tuple(direction.xy * rayon), z),
                      (1.52, 0.50, 0.17), creme, coque, 0.045)
            o.rotation_euler.z = angle
            o = boite("Verre bleu de la baie", (*tuple(direction.xy * (rayon - 0.20)), z + 0.82),
                      (1.29, 0.08, 1.60), verre_bleu, coque)
            o.rotation_euler.z = angle
            o = boite("Traverse en bronze", (*tuple(direction.xy * (rayon - 0.15)), z + 0.89),
                      (1.34, 0.10, 0.09), bronze, coque)
            o.rotation_euler.z = angle

    # Les dalles laissent un vide dans le tiers est pour les paliers et la chaîne.
    for nom, z, rayon in [("Rez · salle des machines", 0.34, 3.65), ("Étage 1 · bureau d’Iris", 4.10, 3.34),
                           ("Étage 2 · salle des cartes", 8.95, 3.03), ("Sommet · galerie", 13.30, 3.85)]:
        if z < 1 or z > 10:
            profil(nom, [(rayon, z - 0.19), (rayon, z)], sable, niveaux)
        else:
            sommets = [v for v in cercle(rayon, z) if v.x < rayon * .7]
            sommets.extend([Vector((rayon * .28, rayon * .61, z)), Vector((rayon * .28, -rayon * .61, z))])
            sommets.sort(key=lambda p: math.atan2(p.y, p.x + rayon * .25))
            objet(nom, sommets, [tuple(range(len(sommets)))], sable, niveaux)

    # Dépendance en retrait : elle prolonge le bureau et porte la lucarne.
    boite("Aile d’Iris · fondation", (4.01, 0.42, 0.24), (4.15, 4.74, .48), sable, coque, .12)
    for nom, position, taille in [
        ("Aile · mur est", (5.96, .42, 3.15), (.36, 4.56, 6.2)),
        ("Aile · mur nord", (4.35, 2.68, 3.15), (3.55, .36, 6.2)),
        ("Aile · mur sud ouest", (3.36, -1.84, 3.15), (1.65, .36, 6.2)),
        ("Aile · mur sud est", (5.56, -1.84, 3.15), (1.15, .36, 6.2)),
        ("Aile · allège", (4.65, -1.84, 2.64), (1.06, .36, 5.2)),
        ("Aile · linteau", (4.65, -1.84, 6.19), (1.06, .36, .24)),
    ]:
        boite(nom, position, taille, ivoire, coque, .06)
    boite("Vitre du bureau", (4.65, -1.84, 5.69), (1.04, .10, .90), verre_bleu, coque)
    boite("Appui du bureau", (4.65, -1.95, 5.22), (1.34, .62, .16), creme, coque, .04)
    boite("Dalle de l'aile", (4.50, .42, 4.03), (3.65, 4.3, .17), sable, niveaux)
    for i, (x1, x2, z1, z2) in enumerate([(2.25, 4.08, 6.26, 7.68), (4.08, 6.43, 7.68, 6.26)]):
        dessus = [(x1, -2.22, z1), (x2, -2.22, z2), (x2, 3.07, z2), (x1, 3.07, z1)]
        if i == 0:
            piece("Toit d’Iris · versant ouest", [(x, y, z-.13) for x, y, z in dessus] + dessus, toit, coque)
        else:
            # Le versant est est ouvert sous la lucarne.
            points = lambda x, y: (x, y, z1 + (z2-z1) * (x-x1)/(x2-x1))
            for xa, xb, ya, yb in [(x1, x2, -2.22, -.58), (x1, x2, 1.02, 3.07),
                                    (x1, 4.63, -.58, 1.02), (5.67, x2, -.58, 1.02)]:
                dessus = [points(xa, ya), points(xb, ya), points(xb, yb), points(xa, yb)]
                piece("Toit d’Iris · versant est", [(x, y, z-.13) for x, y, z in dessus] + dessus, toit, coque)
    for y in (-.58, 1.02):
        montant("Joue de la lucarne", (4.58, y, 7.36), (5.79, y, 7.36), .13, creme, coque, 4)
    dessus = [(4.54,-.72,7.62), (5.86,-.72,7.46), (5.86,1.15,7.46), (4.54,1.15,7.62)]
    piece("Auvent de la lucarne", [(x,y,z-.14) for x,y,z in dessus] + dessus, toit, coque)
    for x in (3.42, 3.77):
        montant("Montant de l’échelle de service", (x, .35, 7.42), (x, .35, 13.62), .057, bronze, coque)
    for i in range(19):
        z = 7.60 + .32*i
        montant("Échelon de service", (3.42, .35, z), (3.77, .35, z), .032, bronze, coque)

    # Les grandes nervures se rejoignent au-dessus du verre optique.
    profil("Corniche facettée", [(3.03, 13.02), (3.62, 13.29), (3.89, 13.43),
                                  (3.85, 13.58)], creme, optique)
    anneau("Bord de la galerie", 3.89, .13, 13.55, 13.73, bronze, optique)
    anneau("Main courante de la galerie", 3.89, .12, 14.38, 14.49, bronze, optique)
    anneau("Traverse basse de la galerie", 3.89, .075, 13.89, 13.96, bronze, optique)
    bord = cercle(3.79, 0)
    for i, p in enumerate(bord):
        for q in [p, p.lerp(bord[(i+1) % 8], .5)]:
            montant("Balustre", (q.x, q.y, 13.60), (q.x, q.y, 14.43), .065, bronze, optique)
        montant("Console sous la galerie", (p.x*.75, p.y*.75, 12.52),
                (p.x*.99, p.y*.99, 13.44), .16, sable, optique, 5, .21)
        angle = math.atan2(p.y, p.x) + math.pi/8
        rayon_tangentiel = Vector((-math.sin(angle), math.cos(angle), 0))
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        centres = [(2.77, 13.59, .23), (2.74, 14.77, .18), (2.40, 16.45, .17), (1.76, 17.47, .25)]
        sommets = []
        for rayon, z, largeur in centres:
            milieu = radial*rayon + Vector((0, 0, z))
            sommets.extend(milieu + radial*dr + rayon_tangentiel*dt
                            for dr, dt in [(-largeur, -largeur), (largeur,-largeur),
                                           (largeur,largeur), (-largeur,largeur)])
        faces = [(3, 2, 1, 0)]
        for niveau in range(len(centres)-1):
            for j in range(4):
                a = niveau*4+j
                b = niveau*4+(j+1)%4
                faces.append((a,b,b+4,a+4))
        faces.append(tuple(range(len(sommets)-4, len(sommets))))
        objet("Nervure en pierre claire", sommets, faces, creme, optique)
    profil("Coiffe de cuivre patiné", [(1.89, 17.34), (1.84, 17.54), (.68, 18.13), (.27, 18.24)],
           toit, optique)
    profil("Faîte de la couronne", [(.18, 18.21), (.23, 18.34), (.10, 18.57)], or_pale, optique)
    anneau("Couronne de roulement", 1.50, .34, 13.66, 13.88, bronze, optique, 32)
    anneau("Couronne graduée", 1.48, .12, 13.89, 13.94, or_pale, optique, 48)
    for i in range(32):
        angle = i * TAU/32
        rayon = 1.42
        coche = boite("Graduation de la couronne", (rayon*math.cos(angle), rayon*math.sin(angle), 13.943),
                      (.13 if i%4 == 0 else .068, .031, .012), nuit, optique)
        coche.rotation_euler.z = angle
    rotor = origine("Axe de rotation de la lentille", (0, 0, 13.92), optique)
    # Lentille de phare en ruche : ceinture de verre, anneaux de prismes dessus et dessous,
    # deux œils de Fresnel sur l'axe du faisceau. Tout tourne avec le rotor.
    centre, ceinture = 1.64, .46

    def rayon_ruche(dz):
        return 1.05 - .38 * max(0, abs(dz) - ceinture) / .78

    pieces = [
        profil("Plateau tournant", [(1.32, 0), (1.32, .09), (1.18, .14)], bronze, optique, 32),
        profil("Piédestal de la lentille", [(.62, .14), (.44, .30), (.40, .42), (.56, .48)],
               creme, optique, 8),
        profil("Verre de la ceinture", [(1.05, centre - ceinture), (1.05, centre + ceinture)],
               vitre, optique, 16, fermer=False),
        profil("Coupole de la lentille", [(.70, centre + 1.20), (.56, centre + 1.34),
               (.30, centre + 1.44), (.06, centre + 1.48)], bronze, optique, 16),
        profil("Bouton de la coupole", [(.05, centre + 1.47), (.11, centre + 1.55),
               (.07, centre + 1.64), (.01, centre + 1.67)], or_pale, optique, 8),
        anneau("Bague basse de la lentille", .74, .10, centre - 1.24, centre - 1.15, bronze, optique, 16),
    ]
    # Anneaux de prismes : section en dent, du bord de la ceinture vers les bagues.
    for bas, haut, nombre in ((centre - 1.15, centre - ceinture, 3), (centre + ceinture, centre + 1.20, 5)):
        for i in range(nombre):
            z0 = bas + (haut - bas) * i / nombre
            z1 = bas + (haut - bas) * (i + 1) / nombre
            r = rayon_ruche((z0 + z1) / 2 - centre)
            pieces.append(profil("Anneau de prismes", [(r - .09, z0), (r + .03, (z0 + z1) / 2),
                                 (r - .09, z1), (r - .09, z0)], vitre, optique, 16, fermer=False))
    for z in (centre - ceinture, centre + ceinture, centre + 1.20):
        r = rayon_ruche(z - centre) + .04
        pieces.append(anneau("Cerclage de la lentille", r, .07, z - .025, z + .025, or_pale, optique, 16))
    # Montants en laiton qui suivent la ruche.
    hauteurs = [centre - 1.15, centre - ceinture, centre + ceinture, centre + .80, centre + 1.20]
    for i in range(8):
        a = i * TAU / 8 + TAU / 16
        for z0, z1 in zip(hauteurs, hauteurs[1:]):
            r0, r1 = rayon_ruche(z0 - centre) + .05, rayon_ruche(z1 - centre) + .05
            pieces.append(montant("Montant de la lentille", (r0*math.cos(a), r0*math.sin(a), z0),
                                  (r1*math.cos(a), r1*math.sin(a), z1), .028, bronze, optique, 5))
    for p in pieces:
        p.parent = rotor
    lentille = origine("Axe optique", (0, 0, centre), optique)
    lentille.parent = rotor
    lentille.rotation_euler = (math.radians(90), 0, math.radians(-25))
    for sens in (1, -1):
        oeil = origine("Œil de Fresnel", (0, 0, .96 * sens), optique)
        oeil.parent = lentille
        if sens < 0:
            oeil.rotation_euler.x = math.pi
        for p in (profil("Verre de Fresnel à facettes", [(.02, 0), (.36, 0), (.36, .04), (.29, .06),
                         (.28, .03), (.19, .09), (.18, .05), (.10, .12), (.08, .08), (.02, .14)],
                         vitre, optique, 16),
                  anneau("Monture de l’œil", .40, .06, -.02, .08, or_pale, optique, 16)):
            p.parent = oeil

    # Deux roues témoins et chaîne, indépendantes en vue des interactions.
    for x, z, r, dents in [(-1.16, .43, .93, 16), (.74, .43, .68, 12), (1.48, 2.34, .75, 14)]:
        roue = origine("Axe d’une roue démontable", (x, .53, z), atelier)
        mo = anneau("Jante de l’engrenage", r, r*.27, -.13, .13, bronze, atelier, dents*2)
        mo.parent = roue
        moyeu = profil("Moyeu", [(r*.23,-.18), (r*.23,.18)], or_pale, atelier, 8)
        moyeu.parent = roue
        for i in range(dents):
            a = i*TAU/dents
            d = Vector((math.cos(a), math.sin(a), 0))
            dent = boite("Dent de roue", d*(r+.04), (.19, .17, .25), bronze, atelier, .022)
            dent.rotation_euler.z = a
            dent.parent = roue
            if i%3 == 0:
                branche = montant("Rayon de la roue", d*(r*.17), d*(r*.81), .083, bronze, atelier, 4)
                branche.parent = roue
        if z > 1:
            roue.rotation_euler.x = math.pi/2
    for i in range(26):
        x = 1.38 + .13*(i%2)
        o = anneau("Maillon de la chaîne", .14, .046, -.034, .034, bronze, atelier, 8)
        o.location = (x, -.07, 2.45 + i*.224)
        o.rotation_euler = (0, math.pi/2, math.pi/2*(i%2))
    for nom, lieu in [("Repère · porte", (0,-4.25,.24)), ("Repère · réception ouest", (-2.50,0,15.68)),
                       ("Repère · lunette vers la mer", (-2.50,1.85,13.64)), ("Repère · lucarne", (5.27,.22,7.34))]:
        origine(nom, lieu, niveaux)
    for groupe in (coque, niveaux, atelier, optique):
        for o in list(groupe.objects):
            if o != racine and o.parent is None:
                o.parent = racine


def camera(nom, emplacement, cible, focale, groupe):
    donnees = bpy.data.cameras.new(nom)
    o = bpy.data.objects.new(nom, donnees)
    groupe.objects.link(o)
    o.location = emplacement
    o.rotation_euler = (Vector(cible) - o.location).to_track_quat("-Z", "Y").to_euler()
    donnees.lens = focale
    donnees.clip_end = 600
    return o


def lumiere(nom, type_lumiere, energie, couleur, position, cible, groupe):
    donnees = bpy.data.lights.new(nom, type_lumiere)
    donnees.energy = energie
    donnees.color = couleur
    o = bpy.data.objects.new(nom, donnees)
    groupe.objects.link(o)
    o.location = position
    o.rotation_euler = (Vector(cible)-o.location).to_track_quat("-Z", "Y").to_euler()
    return donnees


def main(sortie=SORTIE, variante=None, cadrages=None):
    sortie.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Île 2 · Étude du Phare"
    scene.unit_settings.system = "METRIC"
    palette = [
        mat("Calcaire ivoire", (.87, .75, .57)), mat("Pierre des assises", (.58, .47, .32)),
        mat("Pierre claire des nervures", (.94, .81, .61)), mat("Terre cuite pâle", (.64, .24, .16)),
        mat("Cuivre patiné bleu ardoise", (.12, .27, .33), .35, .54),
        mat("Bronze sombre", (.25, .15, .067), .63, .41),
        mat("Laiton pâle", (.83, .54, .20), .57, .26), mat("Creux des gravures", (.065, .049, .065)),
        mat("Verre ambré de la lentille", (.81, .55, .23), .30, .22),
        mat("Verre bleu ciel", (.14, .32, .42), .24, .28),
    ]
    construire_phare(palette)
    if variante:
        variante(palette)
    photos = collection("Cadrages et lumière")
    contexte = collection("Contexte · terrain et port du jeu")
    terrain = importer(MODELES/"ile02/terrain_ile_02.glb", contexte)
    for o in terrain:
        if "colonly" in o.name.lower():
            o.hide_render = True
            o.hide_set(True)
    maison = importer(MODELES/"ile02/maison_quai.glb", contexte)
    for o in maison:
        if o.parent is None:
            o.location += Vector((-12.6, -41, .60))
    mer = mat("Mer turquoise", (.085, .33, .38), .13, .39)
    boite("Mer à basse marée", (0,0,-.80), (800,800,.4), mer, contexte)
    chemin_scene = RACINE/"scenes/ile_02_maquette.tscn"
    source = chemin_scene.read_text()
    assert "0, 8.1, -10.5)" in source
    assert "0, 1, 7, 0, 49)" in source
    robot_groupe = collection("Échelle · robot du jeu")
    robot = importer(MODELES/"robot_meshy.glb", robot_groupe)
    x_robot, y_robot = 1.42, 4.91
    trouve, point, _, _, _, _ = scene.ray_cast(bpy.context.evaluated_depsgraph_get(),
                                               Vector((x_robot, y_robot, 10)), Vector((0,0,-1)))
    z_robot = point.z if trouve else RACINE_PHARE.z
    pivot = origine("Placement du robot", (x_robot, y_robot, z_robot), robot_groupe)
    for o in robot:
        if o.parent is None:
            o.parent = pivot
        if o.animation_data:
            o.animation_data_clear()
    pivot.rotation_euler.z = math.radians(157)
    bpy.context.view_layer.update()
    maillages = [o for o in robot if o.type == "MESH"]
    sommets_z = [(o.matrix_world @ Vector(v)).z for o in maillages for v in o.bound_box]
    facteur = 1.90 / (max(sommets_z) - min(sommets_z))
    pivot.scale *= facteur
    pivot.location.z += (z_robot - min(sommets_z))*facteur
    print(f"Robot : 1,90 m sur le plateau à {z_robot:.2f} m")

    # Lumière dorée du sud-ouest et ambiante bleu pâle de l'île.
    scene.world = bpy.data.worlds.new("Ciel bleu pastel")
    scene.world.use_nodes = True
    fond = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    fond.inputs["Color"].default_value = (.51, .68, .95, 1)
    fond.inputs["Strength"].default_value = .53
    soleil = lumiere("Soleil or doux", "SUN", 2.15, (1,.88,.72), (9,-36,58), (0,8,4), photos)
    soleil.angle = math.radians(5)
    lumiere("Retour bleu du large", "AREA", 950, (.58,.75,1), (17,20,26), (0,10,12), photos).size = 20

    port = camera("01 · Depuis le ponton", (7,-49,3.5), (0,10.5,15.5), 49, photos)
    ensemble = camera("02 · Silhouette à 40°", (37,-29,57), (1,10.5,12.4), 49, photos)
    angle = math.radians(40)
    cible = pivot.location + Vector((0,0,1))
    jeu = camera("03 · Caméra de jeu à l’entrée",
                 cible + Vector((0, -9*math.cos(angle), 9*math.sin(angle))), cible, 28, photos)
    jeu.data.sensor_fit = "VERTICAL"
    jeu.data.sensor_height = 32
    jeu.data.lens = 16/math.tan(math.radians(30))

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 960
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.camera = ensemble
    scene.render.filepath = "//phare_ile_02_ensemble.png"
    bpy.context.preferences.filepaths.save_version = 0
    for ecran in bpy.data.screens:
        for zone in ecran.areas:
            if zone.type == "VIEW_3D":
                zone.spaces.active.region_3d.view_perspective = "CAMERA"
                zone.spaces.active.shading.color_type = "MATERIAL"
    bpy.ops.file.pack_all()
    vues = [(ensemble, "phare_ile_02_ensemble"), (port, "phare_ile_02_depuis_le_port"),
            (jeu, "phare_ile_02_entree_camera_jeu")]
    if cadrages:
        vues = cadrages(scene, photos, pivot, (ensemble, port, jeu))
    bpy.ops.wm.save_as_mainfile(filepath=str(sortie/"phare_ile_02.blend"), compress=True)
    for cadrage, nom in vues:
        scene.camera = cadrage
        scene.render.filepath = str(sortie/(nom+".png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
