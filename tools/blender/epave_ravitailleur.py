"""Construit la coque affaissée du ravitailleur, visible sur le banc de sable."""

from pathlib import Path
import math
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import MODELES, anneau, boite, collection, mat, montant, objet, origine, profil


def construire():
    groupe = collection("Épave du ravitailleur")
    bois = [
        mat("Bois mouillé", (.31, .17, .09)),
        mat("Bois flotté", (.45, .29, .16)),
        mat("Frêne fendu", (.53, .36, .23)),
        mat("Varangues foncées", (.24, .15, .10)),
    ]
    bordure = mat("Bordage vert de mer", (.18, .37, .34))
    cuivre = mat("Cuivre noyé", (.14, .28, .26), .35)
    # Couples de la poupe à l'étrave : longueur, demi-largeur, hauteur de plat-bord.
    couples = [(-5.35, 1.49, .62), (-4.75, 2.01, .60), (-3.1, 2.12, .48),
               (-1.45, 2.08, .55), (.4, 1.96, .58), (2.53, 1.61, .67),
               (4.30, .90, .84), (5.64, .07, 1.07)]

    def profil(couple, cote, niveau):
        y, largeur, haut = couple
        x = cote * largeur * [.23, .70, .94, 1.0][niveau]
        z = [-.25, -.09, .14, haut][niveau] + x * .09
        return (x, y, z)

    for cote in (-1, 1):
        for i, (a, b) in enumerate(zip(couples, couples[1:])):
            for niveau in range(3):
                if cote == 1 and niveau == 2 and i in (1, 2, 3, 4):
                    continue
                points = [profil(a, cote, niveau), profil(b, cote, niveau),
                          profil(b, cote, niveau + 1), profil(a, cote, niveau + 1)]
                face = (0, 1, 2, 3) if cote == 1 else (3, 2, 1, 0)
                planche = objet("Bordage", points, [face],
                                bordure if niveau == 2 else bois[(i + niveau) % 3], groupe)
                epaisseur = planche.modifiers.new("Épaisseur des planches", "SOLIDIFY")
                epaisseur.thickness = .055
        for i in range(1, len(couples) - 1):
            couple = couples[i]
            for niveau in range(3):
                if cote == 1 and i in (3, 4) and niveau == 2:
                    continue
                montant("Membrure", profil(couple, cote, niveau), profil(couple, cote, niveau + 1),
                        .077, bois[3], groupe, nombre=5)

    for i in range(23):
        y = -5.08 + .28 * i
        largeur = min(3.76, 3.14 + (y + 5.08) * .47)
        boite("Planche de pont", (0, y, .325), (largeur, .264, .073), bois[i % 3], groupe, .012)
    montant("Mât cassé", (-1.1, 1.45, .21), (-.33, 4.08, 1.18), .16, bois[2], groupe, bout=.075)
    montant("Ferrure du mât", (-.63, 2.97, .77), (-.56, 3.18, .85), .151, cuivre, groupe)
    varech = mat("Varech dans la brèche", (.22, .38, .27))
    for i in range(9):
        y = 1.41 + i * .41
        taille = max(.22, 1.56 - (y - 1.4) * .29)
        x = -1.42 + (y - 1.4) * .29
        fente = .12 + (i % 3) * .09
        objet("Pont arraché", [(x,y,.34), (x+taille,y,.34), (x+taille-fente,y+.22,.32),
              (x+taille*.53,y+.27,.32), (x,y+.26,.36)], [(0,1,2,3,4)], bois[i % 3], groupe)
    for i in range(10):
        y = .8 + .38 * i
        x = .52 + .21 * math.sin(i * 1.8)
        objet("Amas de varech", [(x-.18,y,.05),(x+.22,y+.07,.055),(x+.14,y+.19,.15),
                                (x-.07,y+.31,.084)], [(0,1,2,3)], varech, groupe)
    construire_cabine(groupe, bois, bordure, cuivre)
    return groupe


def construire_cabine(groupe, bois, bordure, cuivre):
    papier = mat("Cartes mouillées", (.78, .65, .40))
    encre = mat("Encres de marine", (.29, .38, .34))
    toile = mat("Toile de couchette", (.39, .43, .46))
    drap = mat("Couverture rouille", (.52, .26, .19))
    laiton = mat("Laiton de la cabine", (.60, .35, .123), .45, .44)
    vitre = mat("Verre de veille", (.34, .50, .46), .12, .35)
    coupe = origine("CoupeCabine", (0, 0, 0), groupe)

    def piece_coupee(nom, centre, taille, couleur, chanfrein=.018):
        piece = boite(nom, centre, taille, couleur, groupe, chanfrein)
        piece.parent = coupe
        return piece

    # Entrée vers la proue, à laquelle le pont arrive de plain-pied.
    for cote in (-1, 1):
        x = cote * 1.75
        for i in range(6):
            z = .55 + i * .34
            boite("Bordé de la cabine", (x, -3.38, z), (.14, 3.78, .321),
                  bordure if i > 3 else bois[i % 3], groupe, .015)
        boite("Jambage de cabine", (cote * .76, -1.53, 1.57), (.16, .23, 2.48), bois[2], groupe, .023)
        for i in range(6):
            z = .57 + i * .34
            boite("Cloison avant", (cote * 1.26, -1.53, z), (.89, .16, .322),
                  bordure if i > 2 else bois[i % 3], groupe, .013)
    boite("Linteau du seuil", (0, -1.53, 2.72), (1.79, .24, .22), bois[2], groupe, .034)
    # La poupe est en coupe depuis la caméra ; les deux hublots demeurent visibles de la mer.
    for i in range(6):
        z = .56 + i * .34
        for x in (-1.36, 0, 1.36) if i in (3, 4) else (0,):
            largeur = .65 if i in (3, 4) else 3.41
            piece_coupee("Traverse de poupe", (x, -5.2, z), (largeur, .17, .321),
                          bois[i % 3] if i < 3 else bordure)
    for x in (-.69, .69):
        hublot = anneau("Hublot de poupe", .34, .065, -.047, .047, laiton, groupe, 12)
        hublot.rotation_euler.x = math.pi / 2
        hublot.location = (x, -5.30, 1.80)
        hublot.parent = coupe
        verre = profil("Verre trouble", [(.25, -.012), (.25, .012)], vitre, groupe, 12)
        verre.rotation_euler.x = math.pi / 2
        verre.location = (x, -5.22, 1.80)
        verre.parent = coupe
    for i, y in enumerate((-4.93, -4.48, -4.03, -3.58, -3.13, -2.68, -2.23)):
        if i in (2, 3):
            piece_coupee("Chevrons brisés", (-1.1, y, 2.74), (1.32, .18, .16), bois[3])
        else:
            planche = piece_coupee("Planche de toit", (-.12 if i % 2 else .12, y, 2.9 - .026 * i),
                          (3.73 if i < 4 else 3.08, .43, .13), bordure if i % 2 else bois[1])
            planche.rotation_euler.z = (-1 if i % 2 else 1) * .039
    for x in (-1.34, 1.34):
        piece_coupee("Longeron", (x, -3.38, 2.68), (.17, 3.8, .19), bois[2])

    # Un bureau en retrait de la circulation et une couchette à la taille d'un Semeur.
    boite("Table du capitaine", (-1.13, -3.93, 1.13), (1.06, 1.72, .155), bois[2], groupe, .037)
    for y in (-3.24, -4.61):
        boite("Pied sous le bureau", (-1.25, y, .73), (.23, .22, .72), bois[3], groupe, .022)
    for i, y in enumerate((-3.43, -3.78, -4.16)):
        tiroir = boite("Tiroir entrouvert", (-.598 + i * .043, y, .97),
                       (.22, .28, .19), bois[(i + 1) % 3], groupe, .015)
        boite("Poignée de tiroir", (tiroir.location.x + .114, y, .99),
              (.042, .116, .039), laiton, groupe, .009)
    for i in range(3):
        o = boite("Carte roulée", (-1.45 + i*.16, -4.37, 1.25), (.12, .31, .085), papier, groupe, .035)
        o.rotation_euler.z = math.radians(10 - i * 9)
    journal = boite("Journal de quart", (-1.17, -3.41, 1.219), (.56, .46, .042), papier, groupe, .011)
    journal.rotation_euler.z = -.12
    for i in range(4):
        trait = boite("Trait du journal", (-1.14, -3.26 - i * .072, 1.243),
                      (.30 - .028 * (i % 3), .013, .003), encre, groupe)
        trait.rotation_euler.z = -.12
    boite("Couchette", (1.11, -3.82, .68), (1.04, 2.62, .44), bois[3], groupe, .05)
    boite("Paillasse", (1.10, -3.83, .96), (.94, 2.42, .17), toile, groupe, .11)
    boite("Polaire repliée", (1.10, -3.09, 1.06), (.95, .88, .109), drap, groupe, .056)
    boite("Oreiller", (1.10, -4.75, 1.09), (.52, .45, .136), papier, groupe, .071)
    for i in range(3):
        boite("Pli de la couverture", (1.10, -2.84-i*.12, 1.12),
              (.83, .051, .031), drap, groupe, .012)
    boite("Étagère", (1.56, -4.8, 1.82), (.36, .72, .09), bois[2], groupe, .026)
    for i, hauteur in enumerate((.26, .32, .21)):
        bouteille = profil("Flacon de quart", [(.075, 0), (.08, hauteur - .09),
              (.038, hauteur - .03), (.038, hauteur)], vitre if i != 1 else cuivre, groupe, 7)
        bouteille.location = (1.56, -5.05 + i * .21, 1.87)
    for i in range(2):
        caisse = boite("Caisse de ravitaillement", (-1.30, -.35 + i * .56, .57),
                      (.72, .46, .41), bois[(i + 1) % 3], groupe, .038)
        caisse.rotation_euler.z = .12 - .2 * i
    # Une lanterne de quart éteinte et les fixations visibles du bordé.
    montant("Console de veille", (-1.67,-4.78,2.08),(-1.39,-4.78,2.08),.035,cuivre,groupe)
    veilleuse = profil("Verre de veilleuse", [(.10,1.77),(.12,1.85),(.079,2.0)], vitre, groupe, 7)
    veilleuse.location.xy = (-1.39,-4.78)
    for z in (1.75, 2.015):
        virole = profil("Virole de veilleuse", [(.11,z),(.11,z+.038)], laiton, groupe, 8)
        virole.location.xy = (-1.39,-4.78)
    for y in (-4.75, -3.63, -2.41, -1.78):
        for z in (.65, 1.33, 2.01):
            montant("Rivet dans le bordé", (1.82,y,z), (1.843,y,z), .029, cuivre, groupe, 6)

    # Passerelle improvisée du bord éventré au point de débarquement.
    for i in range(12):
        x = 1.7 + i * .238
        z = .343 + (x - 1.55) * .075
        boite("Planche de la passerelle", (x, .10, z), (.223, 1.38, .074),
              bois[(i + 1) % 3], groupe, .014).rotation_euler.y = -.075
    for y in (-.43, .59):
        montant("Longeron de passerelle", (1.59, y, .28), (4.47, y, .52), .082,
                bois[3], groupe, nombre=4)
        montant("Jambe de force", (4.14, y, -.55), (4.14, y, .58), .088, bois[3], groupe, nombre=5)
    montant("Bitte sur la passerelle", (4.21, .64, .51), (4.21, .64, 1.0), .092, cuivre, groupe)


def construire_cle():
    groupe = collection("Clé de la salle des cartes")
    laiton = mat("Laiton poli de la clé", (.84, .51, .18), .58, .34)
    bronze = mat("Creux du panneton", (.34, .21, .08), .44, .61)
    anneau("Anneau octogonal", .092, .027, -.017, .017, laiton, groupe, 8)
    boite("Tige", (.184, 0, 0), (.25, .041, .033), laiton, groupe, .007)
    boite("Panneton", (.29, -.049, 0), (.085, .079, .031), laiton, groupe, .006)
    boite("Dent", (.317, -.094, 0), (.029, .046, .027), laiton, groupe, .005)
    boite("Rainure", (.269, -.044, .017), (.024, .029, .006), bronze, groupe)
    return groupe


def exporter(groupe, nom):
    bpy.ops.object.select_all(action="DESELECT")
    for piece in groupe.objects:
        piece.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(MODELES / "ile02" / f"{nom}.glb"),
                              export_format="GLB", use_selection=True, export_apply=True)


if __name__ == "__main__":
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    exporter(construire(), "epave_ravitailleur")
    exporter(construire_cle(), "cle_salle_cartes")
