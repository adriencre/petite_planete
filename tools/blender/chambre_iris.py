"""Construit la chambre d'Iris, sa lucarne et l'accès extérieur depuis la galerie."""
import bpy

from phare_ile_02 import boite, collection, mat, montant, origine, piece, profil
from phare_ile_02_v2 import retirer
from salle_machines_phare import pente


DECALAGE_CHAMBRE = 3.30


def construire_chambre(palette, racine, solides, collisions):
    ivoire, pierre, creme, terre, cuivre, bronze, laiton, nuit, ambre, bleu = palette
    bois = bpy.data.materials["Frêne miel du bureau"]
    bois_fonce = bpy.data.materials["Veines brunes du frêne"]
    lin = mat("Lin lavande de la chambre", (.61, .52, .65))
    sauge = mat("Couverture de veille", (.35, .49, .42))
    groupe = collection("Phare · chambre d’Iris")
    chambre = origine("ChambreIris", (DECALAGE_CHAMBRE, 0, 0), groupe)
    toit = origine("ToitChambre", (0, 0, 0), groupe)
    facades = origine("FacadesChambre", (0, 0, 0), groupe)
    acces = origine("AccesChambreIris", (0, 0, 0), groupe)
    acces.parent = chambre.parent = racine
    toit.parent = facades.parent = chambre

    def bloc(nom, position, taille, matiere, parent=chambre, collision=True, biseau=.025):
        boite(nom, position, taille, matiere, groupe, biseau).parent = parent
        if collision:
            x, y, z = position
            if parent in (chambre, toit, facades):
                x += DECALAGE_CHAMBRE
            boite(nom + "-colonly", (x, y, z), taille, None, collisions).parent = solides

    # Le volume de la chambre prolonge le palier sans ouvrir la porte vue du bureau.
    bloc("Plancher de la chambre", (4.64, .88, 3.995), (3.14, 3.70, .21), bois)
    bloc("Cloison du couloir côté tour", (3.72, -.91, 5.20), (1.30, .19, 2.20), ivoire, facades)
    bloc("Cloison du couloir côté mer", (5.97, -.91, 5.20), (.48, .19, 2.20), ivoire, facades)
    bloc("Mur de la chambre côté tour", (3.12, 1.08, 5.32), (.16, 3.38, 2.44), ivoire)
    bloc("Raccord sous la passerelle", (3.12, -.80, 5.14), (.16, .38, 2.08), ivoire)
    bloc("Mur du fond", (4.64, 2.75, 5.25), (3.14, .18, 2.30), ivoire)
    for y, largeur in [(-.58, .52), (2.15, 1.12)]:
        bloc("Trumeau côté mer", (6.19, y, 5.25), (.18, largeur, 2.30), ivoire, facades)
    bloc("Allège côté mer", (6.19, .55, 4.59), (.18, 2.02, .98), ivoire, facades)
    bloc("Vitre de la chambre", (6.19, .55, 5.70), (.07, 2.02, 1.24), bleu, facades)
    for y in (-.46, .55, 1.56):
        bloc("Meneau de la chambre", (6.19, y, 5.72), (.17, .08, 1.30), bronze, facades, False)

    coque = bpy.data.collections["Phare · enveloppe"]
    retirer(coque, ("Toit bas", "Joue de la lucarne", "Auvent de la lucarne",
                    "Échelle de service", "Échelon", "Aile · mur nord",
                    "Aile · allège en retour", "Aile · baie sur le cap Est",
                    "Aile · meneau côté mer"))

    # Une vraie ouverture de toit longe la volée jusqu'à sa retombée dans la chambre.
    def panneau(nom, x0, x1, y0, y1, z0, z1):
        dessus = [(x0, y0, z0), (x1, y0, z1), (x1, y1, z1), (x0, y1, z0)]
        points = [(x, y, z - .14) for x, y, z in dessus] + dessus
        piece(nom, points, cuivre, groupe).parent = toit
        points_physiques = [(x + DECALAGE_CHAMBRE, y, z) for x, y, z in points]
        piece(nom + "-colonly", points_physiques, None, collisions).parent = solides

    panneau("Versant de cuivre côté mer", 4.79, 6.32, -.82, 2.82, 6.69, 6.24)
    panneau("Versant de cuivre côté tour", 3.03, 3.41, -.82, 2.82, 6.85, 6.75)
    panneau("Auvent haut de la lucarne", 3.40, 4.80, .65, 2.82, 7.55, 7.45)
    for x in (3.41, 4.79):
        montant("Joue de la lucarne", (x, -.79, 6.39), (x, .67, 7.47),
                .047, bois_fonce, groupe, 5).parent = toit
        montant("Pied de l’auvent", (x, .67, 6.68), (x, .67, 7.50),
                .062, bois_fonce, groupe, 5).parent = toit

    bloc("Palier du toit", (4.60, -1.42, 6.29), (2.56, 1.20, .18), cuivre, toit)
    bloc("Rebord du toit côté port", (4.60, -2.02, 6.73), (2.56, .10, .70), bronze, toit)
    bloc("Rebord du toit côté mer", (5.86, -1.42, 6.73), (.09, 1.20, .70), bronze, toit)
    bloc("Bord du toit devant le versant", (5.35, -.84, 6.73), (1.00, .08, .70), bronze, toit)
    for i in range(12):
        y = -.82 + (i + .5) * 2.74 / 12
        z = 6.38 - (i + 1) * 2.28 / 12
        bloc("Marche de la lucarne", (4.08, y, z + .085), (1.32, .235, .17),
             bois if i % 3 else bois_fonce, collision=False, biseau=.012)
    pente("Rampe de la lucarne-colonly", 3.42 + DECALAGE_CHAMBRE, 4.74 + DECALAGE_CHAMBRE, -.82, 1.92, 6.38, 4.10,
          collisions).parent = solides
    for x in (3.45, 4.72):
        montant("Main courante de la lucarne", (x, -.82, 7.18), (x, 1.27, 5.44),
                .042, bronze, groupe, 5).parent = toit
        montant("Potelet de la lucarne", (x, -.82, 6.40), (x, -.82, 7.18),
                .044, bronze, groupe, 5).parent = toit

    # La passerelle franchit la cage au-dessus du gabarit du robot.
    bloc("Passerelle depuis l’échelle", (5.55, -1.42, 6.29), (3.64, 1.20, .18), cuivre, acces)
    bloc("Garde-corps de la passerelle côté port", (5.55, -1.98, 6.75),
         (3.64, .09, .74), bronze, acces)
    bloc("Garde-corps de la passerelle côté tour", (5.17, -.77, 6.75),
         (2.88, .09, .74), bronze, acces)
    bloc("Couloir derrière la porte", (4.57, -1.54, 4.01), (3.40, 1.30, .18), bois, facades)
    # Les volumes de ce couloir restent entièrement à l'est de la cage.
    bloc("Paroi sud du couloir", (4.57, -2.20, 5.16), (3.40, .11, 2.12), ivoire, facades)
    bloc("Paroi au bout du couloir", (6.20, -1.54, 5.16), (.13, 1.30, 2.12), ivoire, facades)

    for y in (-.53, 2.04):
        montant("Console en bois sous la chambre", (6.23, y, 1.77), (8.17, y, 3.92),
                .20, bois_fonce, groupe, 4).parent = acces

    # Le plan vertical des barreaux fait face au bord de la galerie.
    for y in (-1.57, -.93):
        montant("Montant de l’échelle d’Iris", (4.06, y, 6.39), (4.06, y, 14.73),
                .044, bronze, groupe, 6).parent = acces
        for niveau in (6.42, 13.60):
            montant("Patte de fixation de l’échelle", (3.65, y, niveau), (4.06, y, niveau),
                    .054, bronze, groupe, 6).parent = acces
    for i in range(27):
        z = 6.57 + i * .31
        montant("Barreau de l’échelle d’Iris", (4.06, -1.57, z), (4.06, -.93, z),
                .031, bronze, groupe, 6).parent = acces

    # À droite de la descente, garder le couloir libre du premier au dernier pas.
    bloc("Cadre du lit d’Iris", (5.51, .48, 4.39), (1.12, 1.92, .32), bois_fonce)
    bloc("Tête du lit", (5.51, -.44, 4.72), (1.12, .12, .92), bois)
    bloc("Matelas de lin", (5.51, .49, 4.61), (1.02, 1.75, .20), lin, collision=False, biseau=.075)
    bloc("Couverture pliée", (5.51, .77, 4.73), (1.04, 1.13, .085), sauge, collision=False, biseau=.055)
    bloc("Oreiller", (5.51, -.10, 4.76), (.69, .37, .13), creme, collision=False, biseau=.057)
    bloc("Table de nuit", (5.76, 2.30, 4.45), (.68, .59, .70), bois)
    bloc("Tiroir de la table de nuit", (5.76, 1.996, 4.53), (.53, .035, .23), bois_fonce, collision=False)
    tasse = profil("Tasse de la chambre", [(.08, 4.80), (.11, 4.95), (.087, 4.95), (.065, 4.82)],
                   bleu, groupe, 10, fermer=False)
    tasse.location = (5.94, 2.45, 0)
    tasse.parent = chambre
    lanterne = profil("Lanterne éteinte", [(.13, 4.80), (.16, 4.84), (.10, 4.88),
                                         (.10, 5.10), (.16, 5.16), (.09, 5.23)], bronze, groupe, 8)
    lanterne.location = (5.95, 2.19, 0)
    lanterne.parent = chambre
    points = [(5.97, 2.22, 4.83), (6.02, 2.17, 4.79), (6.00, 2.09, 4.81), (5.91, 2.08, 4.82)]
    for a, b in zip(points, points[1:]):
        montant("Fil débranché", a, b, .012, nuit, groupe, 5).parent = chambre
    montant("Fiche posée", points[-1], (5.86, 2.08, 4.82), .027, laiton, groupe, 6).parent = chambre
