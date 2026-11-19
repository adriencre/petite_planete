"""Seconde étude du Phare, avec les cadrages de la première maquette."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import SORTIE, anneau, boite, main, montant, objet, piece, profil


def retirer(groupe, prefixes):
    for o in list(groupe.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)


def nervure(nom, direction, sections, materiaux, groupe):
    """Une section octogonale irrégulière qui monte en se cintrant."""
    angle = math.radians(direction)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    tangent = Vector((-radial.y, radial.x, 0))
    contour = [(-1, -.48), (-.48, -1), (.58, -1), (1, -.46),
               (1, .45), (.62, 1), (-.48, 1), (-1, .42)]
    sommets = []
    for z, rayon, derive, rayon_section, largeur in sections:
        centre = radial*rayon + tangent*derive + Vector((0,0,z))
        sommets.extend(centre + radial*x*rayon_section + tangent*y*largeur
                        for x,y in contour)
    faces = [tuple(reversed(range(8)))]
    for i in range(len(sections)-1):
        a = i*8
        for j in range(8):
            b, c = a+j, a+(j+1)%8
            faces.append((b,c,c+8,b+8))
    faces.append(tuple(range(len(sommets)-8,len(sommets))))
    o = objet(nom, sommets, faces, materiaux[0], groupe)
    o.data.materials.append(materiaux[1])
    for face in o.data.polygons:
        if (face.index - 1) % 8 in (0, 2, 5):
            face.material_index = 1
    return o


def assise(nom, z, limites, matiere, groupe, profondeur):
    xmin, xmax, ymin, ymax = limites
    coins = [(xmin+.5,ymin), (xmax-.62,ymin), (xmax,ymin+.52), (xmax,ymax-.48),
             (xmax-.44,ymax), (xmin+.61,ymax), (xmin,ymax-.43), (xmin,ymin+.55)]
    sommets = [(x*1.025,y*1.025,z-profondeur) for x,y in coins] + [(x,y,z) for x,y in coins]
    faces = [tuple(reversed(range(8))), tuple(range(8,16))]
    faces.extend((i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8))
    return objet(nom, sommets, faces, matiere, groupe)


def reconstruire(palette):
    ivoire, sable, creme, terre, toit, bronze, or_pale, nuit, _, bleu = palette
    coque = bpy.data.collections["Phare · enveloppe"]
    optique = bpy.data.collections["Phare · galerie et optique"]
    racine = coque.objects["Origine sur le plateau"]
    avant = set(bpy.data.objects)
    retirer(coque, ("Plinthe taillée", "Arête claire du soubassement", "Contrefort",
                    "Marche du seuil", "Aile", "Vitre du bureau", "Appui du bureau",
                    "Toit d’Iris", "Joue de la lucarne", "Auvent de la lucarne",
                    "Jambage", "Rein de l'arche", "Clef de voûte"))
    retirer(optique, ("Nervure", "Coiffe", "Faîte", "Balustre", "Console sous",
                     "Bord de la galerie", "Main courante", "Traverse basse", "Corniche facettée"))

    for o in coque.objects:
        if o.name.startswith("Verre bleu de la baie") and o.location.z < 7:
            o.location.z += .43
            o.scale.z = 1.55

    # Le parvis se prolonge sous l'aile. Trois marches décalées remontent du plateau.
    assise("Soubassement · première strate", .10, (-3.62,6.65,-4.34,2.95), sable, coque, .40)
    assise("Soubassement · seconde strate", .26, (-3.48,6.54,-3.95,2.84), ivoire, coque, .18)
    assise("Soubassement · dalle haute", .35, (-3.25,6.26,-3.74,2.62), creme, coque, .10)
    for i, (y, largeur) in enumerate([(-4.52,3.65), (-4.21,3.46), (-3.92,3.22)]):
        hauteur = .12+.09*i
        boite("Emmarchement du parvis", (-.10,y,hauteur/2+.02), (largeur,.50,hauteur), creme, coque, .055)
    for s in (-1,1):
        for i, (z, largeur) in enumerate([(.80,.76), (1.67,.68), (2.54,.55)]):
            boite("Jambage du portail", (s*(1.17+.08*(2-i)),-3.57,z),
                  (largeur,.71,.86), creme if i%2==0 else ivoire, coque, .07)
        montant("Épaulement du portail", (s*1.16,-3.54,2.58), (s*.63,-3.48,3.21), .28, creme, coque, 5)
    boite("Clé du portail", (0,-3.50,3.23), (1.48,.69,.41), sable, coque, .08)

    # Un étage en balcon sur un soubassement aveugle. Les baies donnent sur l'est et le port.
    assise("Aile · socle en pierre", 3.91, (2.67,6.27,-2.14,2.32), ivoire, coque, 3.58)
    boite("Aile · bandeau de pierre", (4.39,.10,3.98), (3.98,4.71,.21), sable, coque, .09)
    boite("Aile · mur nord", (4.45,2.15,4.97), (3.72,.30,1.91), ivoire, coque, .06)
    for x in (2.90, 6.02):
        boite("Aile · pile sur le port", (x,-1.98,4.95), (.52,.42,1.93), creme, coque, .05)
    boite("Aile · allège de la baie sud", (4.46,-1.99,4.22), (2.64,.45,.50), ivoire, coque)
    boite("Aile · baie sur la chaussée", (4.46,-1.97,5.16), (2.62,.12,1.41), bleu, coque)
    for x in (4.01,4.91):
        boite("Aile · meneau en pierre", (x,-2.06,5.11), (.16,.23,1.60), creme, coque, .027)
    boite("Aile · allège en retour", (6.20,.08,4.20), (.37,4.19,.47), ivoire, coque)
    boite("Aile · baie sur le cap Est", (6.17,.08,5.18), (.13,4.03,1.48), bleu, coque)
    for y in (-1.86,-.61,.75,2.01):
        boite("Aile · meneau côté mer", (6.24,y,4.99), (.26,.22,1.60), creme, coque, .035)
    # Le toit est bas et solidaire de la tour. Quatre panneaux bordent la lucarne.
    def hauteur_toit(x):
        return 6.73 - .24*(x-2.62)

    for xmin,xmax,ymin,ymax in [(2.62,6.63,-2.35,-.68), (2.62,6.63,1.10,2.56),
                               (2.62,4.44,-.68,1.10), (5.81,6.63,-.68,1.10)]:
        haut = [(x,y,hauteur_toit(x)) for x,y in
                [(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)]]
        piece("Toit bas en cuivre", [(x,y,z-.20) for x,y,z in haut]+haut, toit, coque)
    for y in (-.78,1.20):
        montant("Joue de la lucarne", (4.42,y,6.15), (5.91,y,6.08), .13, creme, coque, 4)
    haut = [(4.29,-.84,6.73), (5.38,-.84,6.83), (5.38,1.28,6.83), (4.29,1.28,6.73)]
    piece("Auvent de la lucarne", [(x,y,z-.15) for x,y,z in haut]+haut, toit, coque)
    for o in list(coque.objects):
        if o.name.startswith(("Montant de l’échelle", "Échelon de service")):
            bpy.data.objects.remove(o, do_unlink=True)
    for x in (3.53,3.89):
        montant("Échelle de service", (x,.34,6.40), (x,.34,13.67), .044, bronze, coque)
    for i in range(23):
        z = 6.54+i*.31
        montant("Échelon", (3.53,.34,z), (3.89,.34,z), .026, bronze, coque)

    # Deux appuis montent du socle. Le troisième est à l'arrière. Le côté ouest reste ouvert.
    nervure("Nervure · face sur le port", -119, [
        (-.14,4.56,-.76,.47,.59), (1.40,4.29,-.64,.58,.59), (3.52,3.69,-.33,.57,.45),
        (6.35,3.36,-.18,.45,.40), (9.82,3.24,.05,.39,.37), (12.90,3.24,.14,.40,.42),
        (14.72,2.98,.36,.28,.38), (16.67,2.31,.49,.28,.33), (17.90,1.23,.54,.28,.35),
    ], (creme,ivoire), optique)
    nervure("Nervure · face sur le cap Est", -22, [
        (-.16,4.63,.23,.48,.61), (2.20,4.34,.31,.56,.57), (4.40,3.62,.28,.47,.44),
        (7.60,3.24,.27,.42,.41), (10.76,3.16,.26,.36,.36), (13.10,3.08,.25,.35,.36),
        (14.95,2.70,.18,.30,.34), (16.63,2.13,.13,.29,.32), (17.87,1.17,.07,.27,.34),
    ], (creme,ivoire), optique)
    nervure("Nervure · contrefiche arrière", 79, [
        (11.89,2.82,.16,.31,.42), (13.47,2.98,.31,.31,.37), (15.30,2.64,.27,.26,.34),
        (17.13,1.82,.19,.27,.32), (17.92,1.11,.15,.26,.37),
    ], (creme,ivoire), optique)
    profil("Galerie · corniche de pierre", [(2.96,13.07),(3.26,13.23),(3.74,13.36),
                                            (3.82,13.49),(3.72,13.62)], creme, optique)
    anneau("Galerie · filet sous le garde-corps", 3.82,.12,13.47,13.54, sable,optique)
    anneau("Galerie · main courante", 3.72,.065,14.30,14.36, bronze,optique,16)
    anneau("Galerie · câble tendu", 3.72,.026,13.96,13.987, bronze,optique,16)
    for i in range(16):
        a = i*math.tau/16-math.pi/8
        x,y = 3.68*math.cos(a),3.68*math.sin(a)
        montant("Galerie · potelet", (x,y,13.57),(x,y,14.36),.044,bronze,optique)
    profil("Coiffe basse en cuivre", [(1.59,17.69),(1.62,17.83),(1.20,18.03),(.39,18.29)],
           toit,optique)
    profil("Faîte · pointe d’Iris", [(.38,18.24),(.29,18.38),(.045,18.72)], or_pale,optique)
    lentille = optique.objects["Axe optique"]
    lentille.scale = (1.18,1.18,1)
    lentille.rotation_euler.z = math.radians(-22)

    for o in set(bpy.data.objects) - avant:
        o.parent = racine


if __name__ == "__main__":
    main(sortie=SORTIE.with_name("phare_ile_02_v2"), variante=reconstruire)
