"""Colimaçon contre le mur du Phare, planchers à trémie et garde-corps (visite en 1re personne).

Les trois volées tournent dans le sens horaire en suivant la face intérieure de la tour.
Sous la partie basse d'une volée, la maçonnerie descend jusqu'au sol : on ne passe pas dessous.
Chaque plancher est percé au-dessus de la volée qui y monte, avec un garde-corps.
"""
import math

from mathutils import Vector

from phare_ile_02 import montant, mur, objet, profil

# (hauteur, rayon extérieur) des assises de la tour, voir phare_ile_02.construire_phare.
ASSISES = [(.24, 3.97), (1.24, 3.88), (2.72, 3.78), (3.40, 3.73), (4.15, 3.70), (4.84, 3.62),
           (7.42, 3.45), (9.18, 3.35), (10.72, 3.25), (12.47, 3.13), (13.30, 3.03)]
EPAISSEUR_MUR = .32
REZ, BUREAU, CARTES, GALERIE = .35, 4.10, 8.95, 13.62
# Nom, bas, haut, angle de départ, angle d'arrivée (degrés, sens horaire), marches, rayon intérieur.
VOLEE_REZ = ("Volée du rez", REZ, BUREAU, 40.0, -76.0, 17, 2.00)
VOLEE_BUREAU = ("Volée du bureau", BUREAU, CARTES, -90.0, -260.0, 22, 1.80)
VOLEE_CARTES = ("Volée des cartes", CARTES, GALERIE, 50.0, -128.5, 21, 1.58)
# Sous cette hauteur au-dessus du sol de départ, la marche est pleine jusqu'au sol.
HAUTEUR_PLEINE = 2.6
# Le plancher du dessus s'ouvre dès que la marche passe sous cette garde (robot 1,90 m).
GARDE_TETE = 2.05
HAUTEUR_RAMPE = .95
BANDES_RAMPE = 4


def rayon_tour(z):
    """Rayon des sommets de l'octogone intérieur de la tour à la hauteur z."""
    z = min(max(z, ASSISES[0][0]), ASSISES[-1][0])
    for (z0, r0), (z1, r1) in zip(ASSISES, ASSISES[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0) - EPAISSEUR_MUR
    return ASSISES[-1][1] - EPAISSEUR_MUR


def rayon_mur(angle, z):
    """Distance du centre à la face intérieure de la tour dans la direction `angle` (degrés)."""
    apotheme = rayon_tour(z) * math.cos(math.pi / 8)
    ecart = (angle % 45 + 22.5) % 45 - 22.5  # écart au milieu du pan le plus proche
    return apotheme / math.cos(math.radians(ecart))


def polaire(r, angle, z):
    a = math.radians(angle)
    return Vector((r * math.cos(a), r * math.sin(a), z))


def bloc(nom, a, b, r_int, r_ext_a, r_ext_b, bas_a, bas_b, haut_a, haut_b, matiere, groupe):
    """Secteur entre deux angles : r_ext peut suivre le mur, bas et haut peuvent pencher.
    `r_int` est un rayon, ou un couple (rayon en a, rayon en b)."""
    r_int_a, r_int_b = r_int if isinstance(r_int, tuple) else (r_int, r_int)
    contour = [(r_int_a, a, bas_a, haut_a), (r_ext_a, a, bas_a, haut_a),
               (r_ext_b, b, bas_b, haut_b), (r_int_b, b, bas_b, haut_b)]
    # Le dessus doit tourner dans le sens trigonométrique pour que les normales montent.
    if b < a:
        contour.reverse()
    dessous = [polaire(r, ang, z) for r, ang, z, _ in contour]
    dessus = [polaire(r, ang, z) for r, ang, _, z in contour]
    return objet(nom, dessous + dessus, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
                                         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], matiere, groupe)


def marches(volee):
    """(indice, angle a, angle b, dessus de la marche) pour chaque marche de la volée."""
    _, bas, haut, depart, arrivee, nombre, _ = volee
    for i in range(nombre):
        a = depart + (arrivee - depart) * i / nombre
        b = depart + (arrivee - depart) * (i + 1) / nombre
        yield i, a, b, bas + (haut - bas) * (i + 1) / nombre


def debut_tremie(volee, sol_dessus, epaisseur):
    """Angle à partir duquel le plancher du dessus doit être ouvert au-dessus de la volée."""
    for i, a, _, z in marches(volee):
        if z > sol_dessus - epaisseur - GARDE_TETE:
            return a
    return volee[4]


def fin_de_chute(volee, sol_dessus, chute=.5):
    """Angle à partir duquel les marches arrivent à moins de `chute` du plancher : plus de garde-corps,
    on passe librement du palier à la pièce."""
    for i, a, _, z in marches(volee):
        if z > sol_dessus - chute:
            return a
    return volee[4]


def construire_volee(volee, clair, pierre, bronze, groupe, collisions, rampe_interieure=True):
    """Marches pleines ou en porte-à-faux, rampe de collision et main courante côté vide."""
    nom, bas, haut, _, _, nombre, r_int = volee
    hauteur = (haut - bas) / nombre
    for i, a, b, z in marches(volee):
        ra, rb = rayon_mur(a, z) + .04, rayon_mur(b, z) + .04
        pleine = z - bas < HAUTEUR_PLEINE
        bas_a = bas if pleine else z - hauteur - .34
        bas_b = bas if pleine else z - .34
        bloc(f"{nom} · marche", a, b, r_int, ra, rb, bas_a, bas_b, z, z,
             clair if i % 4 else pierre, groupe)
        # La collision suit le nez des marches : le robot monte sans buter. Elle est découpée en
        # bandes : un seul quadrilatère prendrait la pente du bord intérieur (43°) sur toute la largeur.
        for k in range(BANDES_RAMPE):
            r0a, r1a = (r_int + (ra - r_int) * t for t in (k / BANDES_RAMPE, (k + 1) / BANDES_RAMPE))
            r0b, r1b = (r_int + (rb - r_int) * t for t in (k / BANDES_RAMPE, (k + 1) / BANDES_RAMPE))
            bloc(f"{nom} · rampe-colonly", a, b, (r0a, r0b), r1a, r1b, bas_a, bas_b, z - hauteur, z,
                 None, collisions)
        # Ni en bas (pas de chute) ni sur les deux dernières marches : le palier reste ouvert sur la pièce.
        if not rampe_interieure or z - bas < .45 or haut - z < .5:
            continue
        r = r_int + .05
        z_suivante = z + hauteur if i < nombre - 1 else z
        montant(f"{nom} · main courante", polaire(r, a, z + HAUTEUR_RAMPE),
                polaire(r, b, z_suivante + HAUTEUR_RAMPE), .045, bronze, groupe, 5)
        if i % 3 == 0:
            montant(f"{nom} · potelet", polaire(r, a, z), polaire(r, a, z + HAUTEUR_RAMPE),
                    .04, bronze, groupe, 5)
        bloc(f"{nom} · garde-corps-colonly", a, b, r - .04, r + .04, r + .04,
             z, z, z + HAUTEUR_RAMPE + .03, z_suivante + HAUTEUR_RAMPE + .03, None, collisions)


def construire_plancher(nom, z, epaisseur, r_int, tremie, matiere, groupe, collisions, pas=3):
    """Disque central plein, puis couronne jusqu'au mur sauf sur `tremie` (angles a, b, a > b)."""
    profil(f"{nom} · cœur", [(r_int + .02, z - epaisseur), (r_int + .02, z)], matiere, groupe, 48)
    profil(f"{nom} · cœur-colonly", [(r_int + .02, z - epaisseur), (r_int + .02, z)], None, collisions, 24)
    for a, b in secteurs_hors_tremie(tremie, pas):
        ra, rb = rayon_mur(a, z) + .05, rayon_mur(b, z) + .05
        bloc(f"{nom} · dalle", a, b, r_int, ra, rb, z - epaisseur, z - epaisseur, z, z, matiere, groupe)
        bloc(f"{nom} · dalle-colonly", a, b, r_int, ra, rb, z - epaisseur, z - epaisseur, z, z,
             None, collisions)


def dans_tremie(angle, tremie):
    """Vrai si `angle` (degrés) tombe dans la trémie (debut, fin), dans un sens ou dans l'autre."""
    bas, haut = sorted(tremie)
    return any(bas <= angle + k * 360 <= haut for k in (-2, -1, 0, 1))


def secteurs_hors_tremie(tremie, pas=3):
    """Secteurs (a, b) qui font le tour sans la trémie, coupés exactement à ses bords."""
    bornes = sorted(set(list(range(0, 361, pas)) + [t % 360 for t in tremie]))
    return [(a, b) for a, b in zip(bornes, bornes[1:]) if not dans_tremie((a + b) / 2, tremie)]


def garde_corps_tremie(nom, z, r_int, tremie, bronze, groupe, collisions, cote_vide=True, radial=True,
                       r_ext=None, fin_lisse=None):
    """Garde-corps sur le bord intérieur de la trémie et en travers de son départ."""
    haut_tremie, bas_tremie = tremie
    fin = bas_tremie if fin_lisse is None else fin_lisse
    z_rampe = z + HAUTEUR_RAMPE
    if cote_vide:
        nombre = max(2, round(abs(haut_tremie - fin) / 6))
        for i in range(nombre):
            a = haut_tremie + (fin - haut_tremie) * i / nombre
            b = haut_tremie + (fin - haut_tremie) * (i + 1) / nombre
            montant(f"{nom} · lisse", polaire(r_int, a, z_rampe), polaire(r_int, b, z_rampe),
                    .045, bronze, groupe, 5)
            montant(f"{nom} · potelet", polaire(r_int, a, z), polaire(r_int, a, z_rampe),
                    .04, bronze, groupe, 5)
            bloc(f"{nom} · garde-corps-colonly", a, b, r_int - .04, r_int + .04, r_int + .04,
                 z, z, z_rampe + .03, z_rampe + .03, None, collisions)
    if radial:
        r_mur = r_ext or rayon_mur(haut_tremie, z)
        debut, fin = polaire(r_int, haut_tremie, z_rampe), polaire(r_mur, haut_tremie, z_rampe)
        montant(f"{nom} · lisse", debut, fin, .045, bronze, groupe, 5)
        for t in (0, .5):
            p = debut.lerp(fin, t)
            montant(f"{nom} · potelet", (p.x, p.y, z), p, .04, bronze, groupe, 5)
        a, b = haut_tremie + .6, haut_tremie - .6
        bloc(f"{nom} · garde-corps-colonly", a, b, r_int, r_mur + .05, r_mur + .05,
             z, z, z_rampe + .03, z_rampe + .03, None, collisions)


def murs_de_tour(collisions, depuis=4.15):
    """Collision de la face intérieure de la tour au-dessus du rez.

    Verticale au rayon du bas de chaque assise : le haut de la capsule du robot (1,90 m) ne frotte
    pas contre le fruit du mur, qui ne rentre que de quelques centimètres."""
    for (bas, rb), (haut, rh) in zip(ASSISES, ASSISES[1:]):
        if bas < depuis:
            continue
        for cote in range(8):
            mur(f"Tour {cote}-colonly", rb, rb, bas, haut, cote, (0, 1), None, collisions)
