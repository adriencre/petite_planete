"""La ville haute de la Colonie : la maison commune, le parvis des Trois-Soleils et l'habillage de la peur.

Exécuté par colonie_du_lagon.py (exec dans ses globales), comme grotte_aube.py.
Décisions : ILE_03_COLONIE.md, § G2 (précisé le 2026-11-22).
"""
import zlib

from mathutils import Matrix

COMMUNE_SECTEUR = 14
# Le parvis est centré sur ce rayon ; la maison commune s'ouvre au fond, côté terre.
R_PARVIS = 42.8
# Motif des Trois-Soleils, rangée du haut = la plus proche de la porte (● = allumée).
MOTIF = ("●○●", "○○○", "○●○")
# Grille des lanternes dans le repère du parvis (x vers le secteur suivant, y vers la porte).
COLONNES = (-3.0, 0.0, 3.0)
RANGEES = (2.7, -.1, -2.9)
# Emprise du parvis et de la maison (repère du parvis).
PARVIS = (-5.2, 5.2, -4.4, 5.0)
FACADE = 5.0
SALLE = 10.6
FOND = 14.2
# Le bureau d'Ysolde : demi-largeur, et la porte qui le relie à la salle (x de PORTE_BUREAU[0] à [1]).
BUREAU = 3.5
PORTE_BUREAU = (1.2, 3.0)


def repere_du_secteur(i, rayon):
    a = math.radians((angles[i]+angles[i+1])/2)
    centre = (rayon*math.cos(a), rayon*.84*math.sin(a))
    return centre, math.atan2(math.sin(a)*.84, math.cos(a))-math.pi/2


PARVIS_CENTRE, PARVIS_ANGLE = repere_du_secteur(COMMUNE_SECTEUR, R_PARVIS)


def vers_monde(a, b, h=0):
    c, s = math.cos(PARVIS_ANGLE), math.sin(PARVIS_ANGLE)
    return (PARVIS_CENTRE[0]+a*c-b*s, PARVIS_CENTRE[1]+a*s+b*c, h)


def vers_parvis(x, y):
    c, s = math.cos(PARVIS_ANGLE), math.sin(PARVIS_ANGLE)
    dx, dy = x-PARVIS_CENTRE[0], y-PARVIS_CENTRE[1]
    return dx*c+dy*s, -dx*s+dy*c


def altitude(x, y):
    # Hauteur du terrain de l'anneau sous un point du monde.
    depart = Vector((x, y, 60))
    for triangles in triangles_du_sol:
        for triangle in triangles:
            impact = intersect_ray_tri(*triangle, verticale, depart, True)
            if impact is not None:
                return impact.z
    return None


def _niveau_du_parvis():
    hauts = []
    for a in [PARVIS[0]+k*(PARVIS[1]-PARVIS[0])/10 for k in range(11)]:
        for b in [PARVIS[2]+k*(FOND-PARVIS[2])/12 for k in range(13)]:
            z = altitude(*vers_monde(a, b)[:2])
            if z is not None:
                hauts.append(z)
    return max(hauts)+.1


Z_PARVIS = _niveau_du_parvis()


def dans_parvis(x, y, marge=.6):
    # Vrai sur l'emprise du parvis, de ses marches et de la maison : la friche n'y pousse pas.
    a, b = vers_parvis(x, y)
    return PARVIS[0]-marge < a < PARVIS[1]+marge and PARVIS[2]-2.6 < b < FOND+marge


def hors_friche(i, t, r, marge=.45):
    if dans_grotte(i, t, r, marge):
        return True
    a = point(i, r, 0)
    b = point(i+1, r, 0)
    return dans_parvis(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)


def piece_parvis(nom):
    global origine, angle
    commencer(nom)
    origine, angle = (*PARVIS_CENTRE, Z_PARVIS), PARVIS_ANGLE


def autour(obj, pivot):
    # Origine de l'objet sur son pivot, axes alignés sur la façade : Godot peut l'animer simplement.
    px, py, pz = vers_monde(*pivot[:2], Z_PARVIS+pivot[2])
    obj.data.transform(Matrix.Translation((-px, -py, -pz)))
    obj.data.transform(Matrix.Rotation(-PARVIS_ANGLE, 4, "Z"))
    obj.location = (px, py, pz)
    obj.rotation_euler.z = PARVIS_ANGLE
    return obj


def cylindre(x, y, z, rayon, hauteur, ton, cotes=10, axe="z", rayon2=None):
    # Cylindre facetté le long de z (debout) ou de y (posé contre la façade).
    rayon2 = rayon if rayon2 is None else rayon2
    cercle = [(math.cos(k*math.tau/cotes), math.sin(k*math.tau/cotes)) for k in range(cotes)]
    if axe == "z":
        prisme([(x+rayon*u, y+rayon*v, z) for u, v in cercle],
               [(x+rayon2*u, y+rayon2*v, z+hauteur) for u, v in cercle], ton)
    else:
        bas = [(x+rayon*u, y, z+rayon*v) for u, v in reversed(cercle)]
        haut = [(x+rayon2*u, y-hauteur, z+rayon2*v) for u, v in reversed(cercle)]
        prisme(bas, haut, ton)


def engrenage(x, y, z, rayon, epaisseur, dents, ton):
    # Roue dentée vue de face (dans le plan x-z), épaisseur vers -y.
    contour = []
    for k in range(dents*2):
        r = rayon if k % 2 == 0 else rayon*.8
        for d in (-.22, .22):
            t = (k+.5+d)*math.pi/dents
            contour.append((x+r*math.cos(t), z+r*math.sin(t)))
    extrusion_facade(ccw(contour), y-epaisseur, y, ton)


# ----------------------------------------------------------------------------- le parvis

def parvis_trois_soleils():
    x0, x1, y0, y1 = PARVIS
    hauteur_bas = min(altitude(*vers_monde(a, b)[:2]) for a in (x0, 0, x1) for b in (y0, y1))-Z_PARVIS

    # Le plateau : un massif de pierre mis à niveau, son bord bas fait mur de soutènement.
    piece_parvis("Parvis_trois_soleils")
    # Il file sous le socle de la maison : pas de joint ouvert au pied de la façade.
    boite((x0+x1)/2, (y0+y1+.6)/2, hauteur_bas-1.2, x1-x0, y1-y0+.6, -hauteur_bas+1.2, "pierre")
    # Corniche de soutènement, lit de sable et bandeau sombre au pied.
    for cote in (-1, 1):
        boite(cote*(x1+.07), (y0+y1)/2, -.24, .16, y1-y0+.3, .18, "creme")
    terminer(True)

    # Le dallage : grandes dalles décalées, deux tons, joints légèrement creux.
    piece_parvis("Dallage_du_parvis")
    dalles = random.Random(41)
    rangs = 9
    for r in range(rangs):
        b0 = y0+.05+r*(y1-y0-.1)/rangs
        b1 = b0+(y1-y0-.1)/rangs
        decale = .55 if r % 2 else 0
        bornes = [x0+.05]+[x0+.05+decale+k*1.1 for k in range(1, 10) if x0+.05+decale+k*1.1 < x1-.3]+[x1-.05]
        for a0, a1 in zip(bornes, bornes[1:]):
            ton = dalles.choices(("pave_use", "sable", "craie", "terre_claire"), weights=(5, 3, 2, 1))[0]
            boite((a0+a1)/2, (b0+b1)/2, 0, a1-a0-.05, b1-b0-.05, .03+dalles.uniform(0, .012), ton)
    # Les rosaces : chaque emplacement de lanterne est marqué d'un cercle de pierres sombres.
    for x in COLONNES:
        for y in RANGEES:
            for k in range(10):
                t = k*math.tau/10
                cx, cy = x+.86*math.cos(t), y+.86*math.sin(t)
                cylindre(cx, cy, .02, .17, .035, "pierre", 6)
            cylindre(x, y, .02, .62, .03, "strate", 10)
            cylindre(x, y, .03, .52, .03, "creme", 10)
    # Une herbe timide dans les joints du parvis abandonné.
    for _ in range(46):
        a, b = dalles.uniform(x0+.4, x1-.4), dalles.uniform(y0+.3, y1-.4)
        if min(math.hypot(a-x, b-y) for x in COLONNES for y in RANGEES) < 1.15:
            continue
        for _ in range(dalles.randint(2, 4)):
            t = dalles.uniform(0, math.tau)
            h = dalles.uniform(.1, .26)
            morceau([(a-.03*math.sin(t), b+.03*math.cos(t), .03), (a+.03*math.sin(t), b-.03*math.cos(t), .03),
                     (a+h*.5*math.cos(t), b+h*.5*math.sin(t), h)], [(0, 1, 2)],
                    dalles.choice(("herbe_olive", "herbe_tendre", "herbe_sombre")))
    terminer()

    # Les câbles : de chaque lanterne, une gaine de cuivre file dans un caniveau jusqu'au pupitre.
    piece_parvis("Cables_du_parvis")
    for colonne, x in enumerate(COLONNES):
        xc = x+.68
        boite(xc, (RANGEES[-1]+3.7)/2, .02, .26, 3.7-RANGEES[-1], .025, "ombre")
        for k, y in enumerate(RANGEES):
            # Branche de la prise de la lanterne vers le caniveau de sa colonne.
            boite(x+.37, y, .045, .62, .07, .03, "cuivre")
            # Trois gaines côte à côte dans le caniveau, une par lanterne de la colonne.
            boite(xc-.07+k*.07, (y+3.7)/2, .045, .045, 3.7-y, .03, ("cuivre", "or", "miel")[k])
        # Plaques de visite rivetées sur le caniveau.
        for y in (-1.5, 1.3):
            boite(xc, y, .05, .36, .34, .02, "cuivre")
            for dx in (-.13, .13):
                cylindre(xc+dx, y, .07, .025, .012, "or", 6)
    # Le collecteur longe le pied du perron jusqu'au pupitre des voyants.
    boite(.53, 3.7, .02, 6.6, .3, .025, "ombre")
    for k in range(9):
        boite(.53, 3.6+k*.022, .045, 6.6, .018, .03, ("cuivre", "or", "miel")[k % 3])
    terminer()

    # Le perron vers la rue : marches visibles, rampe de collision dessous.
    bas = altitude(*vers_monde(0, y0-2.2)[:2])-Z_PARVIS
    n = max(2, math.ceil(-bas/.17))
    longueur = n*.36
    piece_parvis("Marches_du_parvis")
    marches(-2.1, 2.1, y0-longueur, y0, bas, 0, n, "craie", plein=bas-1.0)
    for cote in (-1, 1):
        # Joues des marches : un rampant de pierre qui suit la volée, couronné de crème.
        xa, xb = sorted((cote*2.1, cote*2.46))
        ya, yb = y0-longueur, y0
        socle = [(xa, ya, bas-1.0), (xb, ya, bas-1.0), (xb, yb, -1.0), (xa, yb, -1.0)]
        prisme(socle, [(a, b, (bas if b < yb-.01 else 0)+.38) for a, b, _ in socle], "pierre")
        dessus = [(xa-.04, ya, bas+.38), (xb+.04, ya, bas+.38), (xb+.04, yb, .38), (xa-.04, yb, .38)]
        prisme(dessus, [(a, b, c+.08) for a, b, c in dessus], "creme")
    terminer()
    piece_parvis("Rampe_du_parvis")
    rampe(-2.1, 2.1, y0-longueur-.4, y0+.05, bas-.12, .03)
    terminer("-colonly")

    # Le parapet : un muret à hauteur de Semeur, ouvert sur le perron.
    piece_parvis("Parapet_du_parvis")
    def muret(a0, b0, a1, b1):
        l = math.hypot(a1-a0, b1-b0)
        cx, cy = (a0+a1)/2, (b0+b1)/2
        if abs(a1-a0) > abs(b1-b0):
            boite(cx, cy, 0, l, .34, .78, "craie")
            boite(cx, cy, .78, l+.12, .46, .1, "creme")
            for k in range(int(l/1.4)+1):
                boite(a0+k*(a1-a0)/max(1, int(l/1.4)), cy, 0, .44, .44, .95, "pierre")
        else:
            boite(cx, cy, 0, .34, l, .78, "craie")
            boite(cx, cy, .78, .46, l+.12, .1, "creme")
            for k in range(int(l/1.4)+1):
                boite(cx, b0+k*(b1-b0)/max(1, int(l/1.4)), 0, .44, .44, .95, "pierre")
    muret(x0+.17, y0+.17, x0+.17, y1-.2)
    muret(x1-.17, y0+.17, x1-.17, y1-.2)
    # Les murets avant commencent après le pilier d'angle, déjà posé par les murets latéraux.
    muret(x0+.6, y0+.17, -2.3, y0+.17)
    muret(2.3, y0+.17, x1-.6, y0+.17)
    terminer(True)

    # Les projecteurs de la Commandante, sur potences aux angles du fond, braqués sur le parvis :
    # ils ne cachent pas la grille vue de dessus.
    piece_parvis("Projecteurs_du_parvis")
    for cote in (-1, 1):
        x, y = cote*(x1-.62), y1-.75
        cylindre(x, y, 0, .3, .45, "pierre", 8, rayon2=.24)
        cylindre(x, y, .45, .11, 5.0, "ombre", 8, rayon2=.08)
        tige((x, y, 5.3), (x-cote*.8, y-.8, 5.45), .06, "ombre")
        tige((x, y, 4.4), (x-cote*.6, y-.6, 5.35), .035, "ombre")
        # Le phare du projecteur : un fût incliné vers le centre du parvis, la vitre vers le bas.
        a = Vector((x-cote*.8, y-.8, 5.25))
        cible = Vector((-cote*1.5, -1.5, 0))
        axe = (cible-a).normalized()
        tige(tuple(a-axe*.35), tuple(a+axe*.55), .34, "ardoise")
        tige(tuple(a+axe*.55), tuple(a+axe*.62), .3, "or")
        tige(tuple(a-axe*.42), tuple(a-axe*.35), .26, "ombre")
        # Câble noir qui redescend en boucle vers le caniveau.
        for k in range(6):
            p = (x, y-.14, 4.2-k*.62)
            q = (x+(.05 if k % 2 else -.05), y-.14, 4.2-(k+1)*.62)
            tige(p, q, .022, "ombre")
    terminer(True)


# ----------------------------------------------------------------------------- la maison commune

def fenetre_muree(x, y, z, largeur, hauteur, briques=random.Random(7)):
    # Haute fenêtre cintrée dont l'ouverture a été comblée de briques, mortier plus clair.
    demi = largeur/2
    arc = [(x+demi*math.cos(t*math.pi/6), z+hauteur+.42*math.sin(t*math.pi/6)) for t in range(7)]
    cadre = [(x-demi-.14, z), (x+demi+.14, z)]+[(a+(.14 if a > x+.01 else -.14 if a < x-.01 else 0), b+.14)
                                                 for a, b in arc]
    extrusion_facade(cadre, y-.12, y+.02, "creme")
    extrusion_facade([(x-demi, z+.06), (x+demi, z+.06)]+arc, y-.09, y-.06, "sable")
    rang = 0
    h = z+.08
    while h < z+hauteur+.38:
        decale = .14 if rang % 2 else 0
        a = x-demi+.02-decale
        while a < x+demi-.02:
            b = min(a+.3, x+demi-.02)
            a0 = max(a, x-demi+.02)
            haut_arc = z+hauteur+.42*math.sqrt(max(0, 1-((a0+b)/2-x)**2/demi**2))-.04
            if b-a0 > .06 and h+.13 < haut_arc:
                ton = briques.choices(("ocre", "tuile", "saumon", "pierre"), weights=(5, 2, 2, 1))[0]
                boite((a0+b)/2, y-.11, h, b-a0-.03, .06, .13, ton)
            a += .3
        h += .155
        rang += 1
    boite(x, y-.2, z-.14, largeur+.5, .4, .14, "pierre")


def lanterne_murale(x, y, z, ton="or"):
    # Petite lanterne à potence : fixée à la façade, le globe vers la rue (-y).
    boite(x, y-.04, z-.1, .14, .08, .5, "ombre")
    tige((x, y-.06, z+.3), (x, y-.38, z+.36), .028, "ombre")
    cylindre(x, y-.42, z+.02, .08, .05, "ombre", 6)
    cylindre(x, y-.42, z+.07, .1, .24, ton, 6, rayon2=.085)
    cylindre(x, y-.42, z+.31, .12, .07, "ombre", 6, rayon2=.04)


def chaise_semeur(x, y, sens, haute=False):
    # Chaise à la taille des Semeurs : assise à 1 m, haut dossier ; sens = côté du dossier (±1 en y).
    for dx in (-.3, .3):
        for dy in (-.28, .28):
            tige((x+dx*1.1, y+dy*1.1, .12), (x+dx, y+dy, 1.0), .05, "chene")
    boite(x, y, .96, .78, .74, .12, "chene")
    boite(x, y, 1.06, .66, .62, .05, "corail" if haute else "toit_sauge")
    dos = 2.6 if haute else 2.15
    for dx in (-.31, .31):
        tige((x+dx, y+sens*.3, 1.0), (x+dx, y+sens*.38, dos), .05, "bois")
    boite(x, y+sens*.36, dos-.55, .7, .08, .5, "chene")
    if haute:
        extrusion_facade(ccw([(x-.36, dos-.05), (x+.36, dos-.05), (x, dos+.3)]),
                         y+sens*.4-.04, y+sens*.4+.04, "or")


def maison_commune():
    L = 12.4
    demi = L/2
    h = 6.6

    def piece(nom):
        piece_parvis(nom)

    # Les socles sont construits centrés : leur repère est posé au milieu de la salle, puis du bureau.
    commencer("Socle_maison_commune")
    globals()["origine"] = vers_monde(0, (FACADE+SALLE)/2, Z_PARVIS)
    globals()["angle"] = PARVIS_ANGLE
    bloc_chanfreine(L+.6, SALLE-FACADE+.6, -2.6, 2.6, .34, "pierre")
    terminer(True)
    commencer("Socle_bureau_commune")
    globals()["origine"] = vers_monde(0, (SALLE+FOND)/2, Z_PARVIS)
    globals()["angle"] = PARVIS_ANGLE
    bloc_chanfreine(2*BUREAU+.8, FOND-SALLE+.5, -2.6, 2.6, .3, "pierre")
    normales(terminer(True))

    # Sol intérieur : dallage en damier dans la salle, plancher dans le bureau.
    piece("Sol_maison_commune")
    for k in range(int(L/.9)):
        for m in range(6):
            a = -demi+.3+k*.9+.45
            b = FACADE+.35+m*.9+.45
            if a < demi-.3 and b < SALLE-.25:
                boite(a, b, 0, .87, .87, .035, ("sable", "pave_use")[(k+m) % 2])
    for k in range(10):
        boite(-BUREAU+.6+k*(2*BUREAU-.8)/10+.03, (SALLE+FOND)/2, 0, (2*BUREAU-.8)/10-.02, FOND-SALLE-.5, .03,
              "chene" if k % 3 else "bois")
    # Le tapis du bureau, vert sauge bordé d'or.
    boite(-.3, 12.45, .032, 3.8, 2.4, .02, "toit_sauge")
    for b in (11.25, 13.65):
        boite(-.3, b, .036, 3.8, .08, .02, "or")
    # Le tapis du conseil sous la table, contre le mur nord : le milieu de la salle reste libre.
    boite(-3.0, 7.9, .036, 2.8, 4.0, .02, "corail")
    for b in (5.9, 9.9):
        boite(-3.0, b, .04, 2.8, .1, .02, "or")
    terminer()

    def murs(z, hauteur, partie):
        # partie : "avant" (façade et mur sud, qui s'effacent), "fond" (mur du fond et mur nord), "tout".
        e = .42
        if partie in ("avant", "tout"):
            # Façade percée de la grande porte (x de -1.4 à 1.4).
            # Les murs latéraux courent sur toute la profondeur ; façade et fond s'arrêtent entre eux.
            for cote in (-1, 1):
                boite(cote*(demi-e+1.4)/2, FACADE+e/2, z, demi-e-1.4, e, hauteur, "craie")
            if z+hauteur > 4.1:
                haut = max(z, 4.1)
                boite(0, FACADE+e/2, haut, 2.8, e, z+hauteur-haut, "craie")
            boite(demi-e/2, (FACADE+SALLE)/2, z, e, SALLE-FACADE, hauteur, "craie")
        if partie in ("fond", "tout"):
            boite(-demi+e/2, (FACADE+SALLE)/2, z, e, SALLE-FACADE, hauteur, "craie")
            # Mur du fond, ouvert vers le bureau par une porte large (PORTE_BUREAU).
            p0, p1 = PORTE_BUREAU
            for a0, a1 in ((-demi+e, p0), (p1, demi-e)):
                boite((a0+a1)/2, SALLE-e/2, z, a1-a0, e, hauteur, "craie")
            if z+hauteur > 3.2:
                haut = max(z, 3.2)
                boite((p0+p1)/2, SALLE-e/2, haut, p1-p0, e, z+hauteur-haut, "craie")

    piece("Soubassement_maison_commune")
    murs(.03, 1.1, "tout")
    terminer(True)

    # Les murs côté parvis et côté sud s'effacent quand le robot entre.
    piece("Murs_hauts_maison_commune")
    murs(1.13, h-1.13, "avant")
    # Pilastres, bandeau d'étage et corniche à denticules sur la façade.
    for a in (-demi+.25, -3.6, -1.75, 1.75, 3.6, demi-.25):
        boite(a, FACADE-.06, .03, .46, .2, h, "creme")
        boite(a, FACADE-.1, .03, .62, .3, .55, "pierre")
    boite(0, FACADE-.08, 4.55, L+.1, .26, .22, "creme")
    boite(0, FACADE-.12, h-.1, L+.5, .4, .36, "creme")
    for k in range(31):
        boite(-demi+.1+k*L/30.4, FACADE-.36, h-.26, .16, .2, .16, "creme")
    # Les hautes fenêtres de la façade et du mur sud, murées par peur du noir.
    for a in (-4.7, -2.65, 2.65, 4.7):
        fenetre_muree(a, FACADE, 1.35, 1.05, 2.55)
    globals()["angle"] = PARVIS_ANGLE+math.pi/2
    for b in (6.6, 9.0):
        fenetre_muree(b, -demi, 1.35, 1.05, 2.55)
    globals()["angle"] = PARVIS_ANGLE
    # Encadrement de la grande porte : piédroits, arc brisé, clef de voûte.
    for cote in (-1, 1):
        boite(cote*1.55, FACADE-.1, .03, .32, .34, 4.1, "creme")
    # L'arc en claveaux alternés, au-dessus du linteau.
    for t in range(9):
        a0, a1 = t*math.pi/9, (t+1)*math.pi/9
        claveau = [(1.4*math.cos(a0), 4.1+.62*math.sin(a0)), (1.85*math.cos(a0), 4.1+.98*math.sin(a0)),
                   (1.85*math.cos(a1), 4.1+.98*math.sin(a1)), (1.4*math.cos(a1), 4.1+.62*math.sin(a1))]
        extrusion_facade(ccw(claveau), FACADE-.27, FACADE+.02, "creme" if t % 2 else "sable")
    boite(0, FACADE-.1, 4.0, 2.9, .34, .14, "creme")
    extrusion_facade(ccw([(1.4*math.cos(t*math.pi/9), 4.1+.62*math.sin(t*math.pi/9)) for t in range(10)]),
                     FACADE-.08, FACADE+.02, "peche")
    boite(0, FACADE-.32, 4.95, .42, .2, .3, "pierre")
    # Les dix lanternes de la façade : la peur, même ici.
    for a in (-5.6, -4.7, -3.65, -2.65, -1.75, 1.75, 2.65, 3.65, 4.7, 5.6):
        lanterne_murale(a, FACADE-.1, 4.9 if abs(a) in (2.65, 4.7) else 3.9)
    terminer()

    # Le mur du fond et le mur nord restent debout : le plan de l'archipel y est accroché.
    piece("Murs_du_fond_maison_commune")
    murs(1.13, h-1.13, "fond")
    boite(0, SALLE-.1, h-.1, L+.5, .4, .36, "creme")
    boite(-demi+.1, (FACADE+SALLE)/2, h-.1, .4, SALLE-FACADE+.4, .36, "creme")
    globals()["angle"] = PARVIS_ANGLE-math.pi/2
    for b in (-6.6, -9.0):
        fenetre_muree(b, -demi, 1.35, 1.05, 2.55)
    globals()["angle"] = PARVIS_ANGLE
    # Vu de l'intérieur : les fenêtres du mur nord, murées elles aussi, et un lambris de chêne.
    globals()["angle"] = PARVIS_ANGLE+math.pi/2
    for b in (6.6, 9.0):
        fenetre_muree(b, demi-.42, 1.35, 1.05, 2.55)
    globals()["angle"] = PARVIS_ANGLE
    boite(-demi+.44, (FACADE+SALLE)/2, .03, .05, SALLE-FACADE-.84, 1.35, "chene")
    boite(-demi+.46, (FACADE+SALLE)/2, 1.35, .09, SALLE-FACADE-.84, .08, "bois")
    for a0, a1 in ((-demi+.42, PORTE_BUREAU[0]), (PORTE_BUREAU[1], demi-.42)):
        boite((a0+a1)/2, SALLE-.44, .03, a1-a0, .05, 1.35, "chene")
        boite((a0+a1)/2, SALLE-.46, 1.35, a1-a0, .09, .08, "bois")
    # Le cadre du plan de l'archipel (l'image est posée par Godot) et la frise des îles.
    boite(-.7, SALLE-.48, 1.7, 3.0, .08, 2.1, "chene")
    boite(-.7, SALLE-.53, 1.8, 2.8, .04, 1.9, "creme")
    for k in range(4):
        tige((-2.0+k*.86, SALLE-.56, 3.86), (-2.0+k*.86, SALLE-.5, 3.76), .02, "or")
    # Deux bannières de la Colonie, cuivre et or, à gauche du plan.
    for a in (-4.8, -2.9):
        boite(a, SALLE-.5, 2.0, .72, .04, 2.6, "tuile")
        extrusion_facade(ccw([(a-.36, 2.0), (a+.36, 2.0), (a, 1.62)]), SALLE-.52, SALLE-.48, "tuile")
        pilier(a, SALLE-.54, 2.95, .14, .02, "or")
        tige((a-.45, SALLE-.55, 4.6), (a+.45, SALLE-.55, 4.6), .03, "cuivre")
    terminer()

    # Le bureau d'Ysolde : une pièce basse derrière la salle. Son mur sud s'efface avec ceux de la salle.
    hb = 4.4

    def murs_bureau(z, hauteur, partie):
        if partie in ("sud", "tout"):
            boite(BUREAU-.2, (SALLE+FOND)/2, z, .4, FOND-SALLE, hauteur, "peche")
        if partie in ("fond", "tout"):
            boite(-BUREAU+.2, (SALLE+FOND)/2, z, .4, FOND-SALLE, hauteur, "peche")
            boite(0, FOND-.2, z, 2*BUREAU-.8, .4, hauteur, "peche")
    piece("Soubassement_bureau_commune")
    murs_bureau(.03, 1.1, "tout")
    terminer(True)
    piece("Murs_hauts_bureau_commune")
    murs_bureau(1.13, hb-1.13, "sud")
    boite(BUREAU-.2, (SALLE+FOND)/2, hb-.1, .5, FOND-SALLE+.2, .3, "creme")
    terminer()
    piece("Murs_du_fond_bureau_commune")
    murs_bureau(1.13, hb-1.13, "fond")
    boite(-BUREAU+.2, (SALLE+FOND)/2, hb-.1, .5, FOND-SALLE+.2, .3, "creme")
    boite(0, FOND-.2, hb-.1, 2*BUREAU+.4, .5, .3, "creme")
    globals()["angle"] = PARVIS_ANGLE+math.pi
    fenetre_muree(0, -FOND, 1.2, .9, 1.8)
    globals()["angle"] = PARVIS_ANGLE
    # Côté intérieur : lambris de chêne et carte des tournées de lanternes au-dessus des casiers.
    boite(-BUREAU+.42, (SALLE+FOND)/2, .03, .04, FOND-SALLE-.8, 1.3, "chene")
    boite(0, FOND-.42, .03, 2*BUREAU-.8, .04, 1.3, "chene")
    boite(-BUREAU+.44, 12.4, 2.95, .03, 1.6, 1.0, "creme")
    for k in range(9):
        cylindre(-BUREAU+.46, 11.9+(k % 3)*.5, 3.1+(k//3)*.3, .05, .02, "or" if k % 4 else "tuile", 6, axe="y")
    terminer()

    # Toits : croupe d'ardoise sur la salle, appentis sur le bureau, lanterneau d'or au faîte.
    piece("Toit_maison_commune")
    def croupe(cx, cy, z, l, p, hauteur, ton):
        bas = [(cx-l/2, cy-p/2, z), (cx+l/2, cy-p/2, z), (cx+l/2, cy+p/2, z), (cx-l/2, cy+p/2, z)]
        retrait = p/2
        haut = [(cx-l/2+retrait, cy, z+hauteur), (cx+l/2-retrait, cy, z+hauteur)]
        morceau(bas+haut, [(3, 2, 1, 0), (0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5)], ton)
    croupe(0, (FACADE+SALLE)/2, h+.08, L+1.1, SALLE-FACADE+1.1, 2.6, "ardoise")
    for t in (.28, .56):
        for sens in (-1, 1):
            p = (SALLE-FACADE+1.1)/2*(1-t)
            l = L+1.1-(SALLE-FACADE+1.1)*t
            boite(0, (FACADE+SALLE)/2+sens*p, h+.08+2.6*t+.02, l, .08, .06, "ombre")
    boite(0, (FACADE+SALLE)/2, h+2.66, L+1.1-(SALLE-FACADE+1.1)+.2, .26, .12, "creme")
    r = BUREAU+.3
    bas = [(-r, SALLE-.2, hb+.4), (r, SALLE-.2, hb+.4), (r, FOND+.4, hb-.1), (-r, FOND+.4, hb-.1)]
    prisme(bas, [(a, b, c+.2) for a, b, c in bas], "cuivre")
    for a in (-3.0, -1.5, 0, 1.5, 3.0):
        bande = [(a-.03, SALLE-.2, hb+.6), (a+.03, SALLE-.2, hb+.6), (a+.03, FOND+.4, hb+.1), (a-.03, FOND+.4, hb+.1)]
        prisme(bande, [(x, y, z+.03) for x, y, z in bande], "miel")
    # Fronton triangulaire au-dessus de la porte, à l'avant de la croupe.
    fronton = [(-2.9, h+.2), (2.9, h+.2), (0, h+1.95)]
    extrusion_facade(ccw(fronton), FACADE-.5, FACADE-.1, "creme")
    extrusion_facade(ccw([(-2.45, h+.38), (2.45, h+.38), (0, h+1.67)]), FACADE-.55, FACADE-.5, "peche")
    # Les trois soleils sculptés au fronton.
    for k, a in enumerate((-1.0, 0, 1.0)):
        zc = h+.82+(.22 if k == 1 else 0)
        cylindre(a, FACADE-.55, zc, .2, .08, "or", 10, axe="y")
        for r in range(8):
            t = r*math.tau/8
            tige((a+.25*math.cos(t), FACADE-.6, zc+.25*math.sin(t)),
                 (a+.36*math.cos(t), FACADE-.6, zc+.36*math.sin(t)), .03, "or")
    terminer()

    # Le beffroi civique : tour carrée à l'angle nord-est, lanterne d'or sous une flèche d'ardoise.
    piece("Beffroi_civique")
    # Il se dresse derrière la salle, contre le bureau, et descend sous le terrain.
    bx, by, c = -BUREAU-1.45, SALLE+1.65, 1.4
    boite(bx, by, -2.6, 2*c, 2*c, 13.2, "craie")
    for sx in (-1, 1):
        for sy in (-1, 1):
            boite(bx+sx*(c-.2), by+sy*(c-.2), -2.6, .4, .4, 13.2, "creme")
    for z in (3.4, 7.0):
        boite(bx, by, z, 2*c+.16, 2*c+.16, .2, "creme")
    boite(bx, by, 10.6, 2*c+.5, 2*c+.5, .38, "cuivre")
    for sx in (-1, 1):
        for sy in (-1, 1):
            boite(bx+sx*(c-.4), by+sy*(c-.4), 10.98, .32, .32, 2.2, "ardoise")
    pilier(bx, by, 11.3, .8, 1.3, "or", .5)
    pilier(bx, by, 12.6, .55, .2, "creme")
    toit(bx, by, 13.18, 2*c+.9, 2*c+.9, 2.7, "ardoise")
    boite(bx, by, 13.1, 2*c+.8, 2*c+.8, .12, "creme")
    # Deux projecteurs ajoutés tard, braqués sur la ville.
    for sens in (-1, 1):
        tige((bx+sens*(c+.25), by-1.0, 9.6), (bx+sens*(c+.85), by-1.6, 9.9), .26, "ardoise")
        tige((bx+sens*(c+.85), by-1.6, 9.9), (bx+sens*(c+.92), by-1.67, 9.93), .22, "or")
    terminer()

    # La salle du conseil : la grande table contre le mur nord, le passage de la porte au bureau reste libre.
    piece("Mobilier_maison_commune")
    for a in (-3.5, -2.5):
        for b in (6.9, 8.9):
            boite(a, b, .03, .16, .16, 1.25, "bois")
    boite(-3.0, 7.9, 1.28, 1.5, 2.8, .14, "chene")
    boite(-3.0, 7.9, 1.18, 1.3, 2.6, .1, "bois")
    # Chaises face à face de part et d'autre (repère tourné : le dossier part vers l'extérieur de la table).
    globals()["angle"] = PARVIS_ANGLE+math.pi/2
    for b in (7.2, 8.6):
        chaise_semeur(b, 4.35, 1)
        chaise_semeur(b, 1.65, -1)
    globals()["angle"] = PARVIS_ANGLE
    # Le siège de la Commandante, en bout de table, dos au mur du fond.
    chaise_semeur(-3.0, 9.75, 1, haute=True)
    # Lampadaires alignés le long du mur nord : la salle ne devait jamais être sombre.
    for b in (5.9, 7.2, 8.5, 9.8):
        x = -demi+.75
        cylindre(x, b, .03, .22, .1, "ombre", 8)
        cylindre(x, b, .13, .05, 2.4, "ombre", 6)
        cylindre(x, b, 2.53, .2, .4, "or", 6, rayon2=.16)
        cylindre(x, b, 2.93, .24, .1, "ombre", 6, rayon2=.06)
    # Caisses de lanternes de rechange dans l'angle sud, près de l'entrée, une ouverte.
    for k, (a, b) in enumerate(((5.1, 5.9), (5.1, 6.8), (5.15, 6.35))):
        z = .03 if k < 2 else .73
        boite(a, b, z, .9, .82, .7, "bois")
        boite(a, b, z+.7, .94, .86, .05, "chene")
    terminer(True)

    piece("Objets_maison_commune")
    # Sur la table : chandeliers, encrier, registres et la grande carte roulée.
    for b in (6.85, 8.95):
        cylindre(-3.0, b, 1.42, .1, .05, "or", 8)
        cylindre(-3.0, b, 1.47, .035, .45, "or", 6)
        cylindre(-3.0, b, 1.92, .06, .16, "creme", 6)
    for k, ton in enumerate(("tuile", "toit_sauge", "miel")):
        boite(-3.1+k*.04, 7.5, 1.42+k*.07, .44, .62, .07, ton)
    tige((-3.2, 8.0, 1.48), (-3.1, 8.75, 1.48), .07, "creme")
    tige((-3.21, 7.96, 1.48), (-3.2, 8.0, 1.48), .08, "chene")
    cylindre(-2.6, 8.3, 1.42, .08, .1, "ombre", 6)
    tige((-2.6, 8.3, 1.52), (-2.5, 8.45, 1.86), .01, "creme")
    # Les lanternes de rechange qui dépassent de la caisse ouverte.
    for k in range(3):
        cylindre(5.0+k*.12, 6.35+(k-1)*.18, 1.48, .08, .22, "or", 6, rayon2=.07)
    terminer()

    # Le bureau d'Ysolde : table de travail au milieu, casiers à l'ouest, coffre et portemanteau à l'est.
    # On entre par l'angle sud-est et on arrive devant la table sans rien enjamber.
    piece("Mobilier_bureau_commune")
    for a in (-1.7, .5):
        for b in (12.0, 12.7):
            boite(a, b, .03, .14, .14, 1.15, "bois")
    boite(-.6, 12.35, 1.18, 2.5, 1.1, .1, "chene")
    boite(-.6, 11.82, .2, 2.4, .08, .98, "bois")
    chaise_semeur(-.6, 13.3, 1)
    # Portemanteau et long manteau de la Commandante, coffre bardé de cuivre.
    cylindre(2.75, 13.4, .03, .22, .08, "ombre", 8)
    cylindre(2.75, 13.4, .11, .05, 2.6, "chene", 6)
    for k in range(4):
        t = k*math.tau/4+.4
        tige((2.75, 13.4, 2.55), (2.75+.28*math.cos(t), 13.4+.28*math.sin(t), 2.75), .025, "chene")
    manteau = [(2.45, 13.22, .9), (3.05, 13.22, .9), (2.95, 13.17, 2.55), (2.55, 13.17, 2.55)]
    prisme(manteau, [(a, b+.22, c) for a, b, c in manteau], "corail")
    boite(2.75, 13.1, 2.3, .34, .06, .3, "or")
    boite(2.65, 12.4, .03, .6, 1.1, .7, "chene")
    for b in (11.95, 12.85):
        boite(2.65, b, .03, .64, .08, .74, "cuivre")
    boite(2.34, 12.4, .38, .03, .16, .14, "or")
    # Casiers le long du mur ouest, rouleaux d'archives dans les cases.
    for k in range(3):
        boite(-2.8, 11.6+k*.62, .03, .5, .58, 2.7, "chene")
        for z in (.7, 1.4, 2.1):
            boite(-2.8, 11.6+k*.62, z, .5, .58, .05, "bois")
    terminer(True)

    piece("Papiers_bureau_commune")
    papiers = random.Random(5)
    for k in range(3):
        for z in (.75, 1.45, 2.15):
            for m in range(papiers.randint(2, 4)):
                b = 11.45+k*.62+m*.1
                tige((-2.97, b, z+.06), (-2.6, b, z+.06), .045, papiers.choice(("creme", "sable", "craie")))
    # Les ordres d'Ysolde sur la table, côté visiteur (l'image est posée par Godot), sa plume, sa lampe éteinte.
    boite(-1.1, 12.2, 1.285, .6, .8, .015, "creme")
    tige((-.4, 12.15, 1.3), (-.05, 12.3, 1.36), .012, "or")
    cylindre(.3, 12.6, 1.28, .12, .05, "ombre", 8)
    cylindre(.3, 12.6, 1.33, .03, .35, "ombre", 6)
    cylindre(.3, 12.6, 1.68, .15, .16, "or", 8, rayon2=.07)
    # La corbeille de Tavin : des lettres froissées, une dépliée sur le dessus.
    cylindre(1.4, 13.2, .03, .3, .55, "bois", 10, rayon2=.36)
    for k in range(6):
        t = k*math.tau/6
        pilier(1.4+.17*math.cos(t), 13.2+.17*math.sin(t), .5+papiers.uniform(0, .1), .11, .14, "creme", .06)
    for k in range(3):
        t = papiers.uniform(0, math.tau)
        pilier(1.1+.45*math.cos(t), 12.95+.25*math.sin(t), .03, .1, .13, "creme", .05)
    terminer()

    # La grande porte : deux vantaux sur leurs gonds, la serrure à trois crans, le verrou.
    for nom, cote in (("Porte_commune_gauche", -1), ("Porte_commune_droite", 1)):
        piece(nom)
        x0, x1 = (-1.38, -.01) if cote < 0 else (.01, 1.38)
        boite((x0+x1)/2, FACADE+.12, .03, x1-x0, .12, 4.0, "bois")
        for z in (.5, 1.85, 3.2):
            boite((x0+x1)/2, FACADE+.04, z, x1-x0-.1, .05, .14, "chene")
        for k in range(4):
            a = x0+.17+k*(x1-x0-.34)/3
            for z in (.57, 1.92, 3.27):
                cylindre(a, FACADE+.015, z+.07, .035, .03, "or", 6, axe="y")
        # Penture de cuivre côté gonds.
        a = x0 if cote < 0 else x1
        for z in (.8, 3.0):
            boite(a-cote*.4, FACADE+.03, z, .8, .04, .09, "cuivre")
        obj = normales(terminer())
        autour(obj, (cote*1.38, FACADE+.12, .03))

    piece("Serrure_commune")
    # Le boîtier de la serrure, à cheval sur les deux vantaux, et ses trois fenêtres de crans.
    boite(0, FACADE-.04, 1.25, .9, .1, 2.05, "cuivre")
    boite(0, FACADE-.1, 1.3, .78, .04, 1.95, "ombre")
    for z in (1.6, 2.25, 2.9):
        cylindre(0, FACADE-.12, z, .05, .04, "or", 6, axe="y")
    obj = normales(terminer())
    autour(obj, (0, FACADE-.04, 1.25))
    for k, z in enumerate((1.6, 2.25, 2.9)):
        piece(f"Cran_commune_{k+1}")
        globals()["origine"] = (0, 0, 0)
        globals()["angle"] = 0
        engrenage(0, 0, 0, .29, .07, 9, "or")
        cylindre(0, -.07, 0, .09, .05, "cuivre", 8, axe="y")
        # Une encoche peinte : on voit le cran tourner.
        boite(0, -.075, .12, .05, .01, .12, "tuile")
        obj = normales(terminer())
        x, y, zz = vers_monde(0, FACADE-.12, Z_PARVIS+z)
        obj.location = (x, y, zz)
        obj.rotation_euler.z = PARVIS_ANGLE
    # Le verrou barre les deux vantaux sous la serrure ; il glisse quand les trois crans ont tourné.
    piece("Verrou_commune")
    boite(0, FACADE-.2, .95, 2.2, .1, .14, "ombre")
    boite(-1.05, FACADE-.22, .9, .14, .14, .24, "cuivre")
    boite(1.05, FACADE-.22, .9, .14, .14, .24, "cuivre")
    obj = normales(terminer())
    autour(obj, (0, FACADE-.2, .95))

    # Le pupitre des voyants : incliné pour se lire de haut, relié au collecteur du parvis.
    piece("Pupitre_voyants")
    px, py = 2.6, 3.85
    boite(px, py, 0, .5, .5, 1.25, "pierre")
    boite(px, py, 1.2, .64, .64, .08, "creme")
    plateau = [(px-.62, py-.55, 1.3), (px+.62, py-.55, 1.3), (px+.62, py+.35, 1.75), (px-.62, py+.35, 1.75)]
    prisme(plateau, [(a, b, c+.08) for a, b, c in plateau], "cuivre")
    cadre = [(px-.56, py-.5, 1.385), (px+.56, py-.5, 1.385), (px+.56, py+.3, 1.795), (px-.56, py+.3, 1.795)]
    prisme(cadre, [(a, b, c+.015) for a, b, c in cadre], "ombre")
    # Le faisceau sort au pied du pupitre, longe le perron et monte dans une goulotte jusqu'à la serrure.
    boite(px, py+.33, .02, .22, .16, 1.22, "cuivre")
    boite((px+1.66)/2, FACADE-.38, .02, px-1.66+.2, .2, .06, "cuivre")
    boite(px, (py+.33+FACADE-.38)/2, .02, .2, FACADE-.38-py-.33+.2, .06, "cuivre")
    boite(1.86, FACADE-.36, .02, .18, .14, 2.3, "cuivre")
    boite(1.86, FACADE-.43, .02, .1, .02, 2.3, "or")
    for z in (.5, 1.2, 1.9):
        boite(1.86, FACADE-.36, z, .24, .18, .06, "ombre")
    boite(1.12, FACADE-.36, 2.2, 1.5, .14, .14, "cuivre")
    terminer(True)
    # Neuf voyants, un par lanterne, dans l'ordre du parvis (rangée du haut = près de la porte).
    for r in range(3):
        for c in range(3):
            piece(f"Voyant_commune_{r*3+c+1}")
            # Sur le plateau incliné : la rangée du haut du motif est la plus éloignée du joueur.
            t = (2-r+.5)/3
            a = px-.36+c*.36
            b = py-.5+.8*t
            z = 1.4+.41*t
            cylindre(a, b, z, .11, .05, "ombre", 10)
            cylindre(a, b, z+.03, .085, .06, "verre", 10, rayon2=.07)
            normales(terminer())


# ----------------------------------------------------------------------------- la peur dans la ville haute

# Façades de la ville haute, relevées par colonie_du_lagon.py pendant la construction des secteurs :
# (nom, centre, rotation, largeur, profondeur, hauteur, fenêtres, x de la porte, secteur, rive).
# Une fenêtre = (x, z du vitrage, largeur, hauteur, recul du vitrage devant la façade).
facades_ville_haute = []
# Repères des affiches et des morceaux du plan d'éclairage (nom, x, y, z monde).
reperes_affiches = []
# De la crête vers le sud, la peur grandit : 1 = premières lanternes, 3 = tout est muré.
INTENSITE = {11: 1, 12: 2, 13: 2, 14: 3, 15: 3, 16: 3}


def noter_maison(nom, centre, rotation, l, p, h, etage, secteur, rive):
    fenetres = [(x, z+.16, .77, 1.06, .17) for x in (-l*.32, l*.32) for z in ([1.65, 4.6] if etage else [1.65])]
    facades_ville_haute.append((nom, centre, rotation, l, p, h, fenetres, 0, secteur, rive))


def noter_logis(nom, centre, rotation, forme, secteur, rive):
    largeur, profondeur, h = variantes_fermees[forme][:3]
    if forme == "balcon":
        fenetres = [(1.13, 1.58, .98, .93, .11), (0, 3.95, 1.23, .93, .11)]
        porte = -.89
    else:
        fenetres = [(x, 1.70, .53, .93, .11) for x in (-1.64, 1.64)]+[(x, 4.27, .75, .93, .11) for x in (-.91, .91)]
        porte = 0
    facades_ville_haute.append((nom, centre, rotation, largeur, profondeur, h, fenetres, porte, secteur, rive))


def briques(x, y, z, l, h, graine):
    # Panneau de briques maçonné dans une baie, joints décalés, mortier clair derrière.
    tirage = random.Random(graine)
    boite(x, y+.01, z, l+.08, .05, h, "sable")
    rang = 0
    hh = z+.03
    while hh < z+h-.04:
        a = x-l/2-(.12 if rang % 2 else 0)
        while a < x+l/2:
            a0, a1 = max(a, x-l/2), min(a+.26, x+l/2)
            if a1-a0 > .05:
                boite((a0+a1)/2, y-.02, hh, a1-a0-.025, .05, min(.11, z+h-hh-.01),
                      tirage.choices(("ocre", "tuile", "saumon", "pierre"), weights=(5, 2, 2, 1))[0])
            a += .26
        hh += .135
        rang += 1


def projecteur_mural(x, y, z, sens, ton="ardoise"):
    # Projecteur sur potence, fixé au mur (y), tourné vers la rue (-y) et vers le bas.
    boite(x, y-.05, z-.5, .2, .1, .7, "ombre")
    tige((x, y-.08, z), (x+sens*.15, y-1.0, z+.1), .045, "ombre")
    tige((x, y-.08, z-.45), (x+sens*.1, y-.85, z+.05), .03, "ombre")
    a = Vector((x+sens*.15, y-1.0, z))
    axe = Vector((sens*.15, -.55, -.75)).normalized()
    tige(tuple(a-axe*.28), tuple(a+axe*.36), .23, ton)
    tige(tuple(a+axe*.36), tuple(a+axe*.41), .2, "or")
    tige(tuple(a-axe*.34), tuple(a-axe*.28), .17, "ombre")


def habiller_facade(nom, centre, rotation, l, p, h, fenetres, porte, secteur, rive):
    global origine, angle
    intensite = INTENSITE[secteur]
    commencer(nom+"_peur")
    origine, angle = centre, rotation
    y = -p/2
    # Fenêtres murées : une au début, toutes celles du bas ensuite, toutes au bout de la ville.
    for k, (x, z, lv, hv, recul) in enumerate(fenetres):
        if intensite == 3 or (intensite == 2 and z < 3) or (intensite == 1 and k == 0):
            briques(x, y-recul-.02, z, lv, hv, zlib.crc32(f"{nom}{k}".encode()))
    # Une rangée de lanternes murales sous l'étage, une seconde sous le toit quand la peur grandit.
    rangs = {1: [(2.95, 4)], 2: [(2.95, 6)], 3: [(2.95, 6), (h-.55, 4)]}[intensite]
    for z, n in rangs:
        xs = [-l/2+.45+k*(l-.9)/(n-1) for k in range(n)]
        xs = [x for x in xs if abs(x-porte) > 1.05 or z > 3.2]
        # Pas de lanterne devant une fenêtre de la même hauteur.
        xs = [x for x in xs if all(abs(x-fx) > fl/2+.3 or not (fz-.3 < z < fz+fh+.3)
                                   for fx, fz, fl, fh, _ in fenetres)]
        for x in xs:
            lanterne_murale(x, y-.02, z)
        # La gaine noire qui relie les lanternes et redescend vers un boîtier au sol.
        if len(xs) > 1:
            boite((xs[0]+xs[-1])/2, y-.05, z+.48, xs[-1]-xs[0], .05, .05, "ombre")
    xb = l/2-.35
    boite(xb, y-.06, 2.95+.48-2.3, .05, .05, 2.35, "ombre")
    boite(xb, y-.12, .5, .34, .18, .44, "ardoise")
    boite(xb, y-.22, .62, .2, .02, .14, "or")
    if intensite >= 2:
        projecteur_mural(-l/2+.3, y, h-.35, 1)
    if intensite == 3:
        projecteur_mural(l/2-.3, y, h-.35, -1, "cuivre")
        # Lanterne de seuil sur un piquet, devant la porte.
        x = porte+1.2*(1 if porte <= 0 else -1)
        cylindre(x, y-1.1, 0, .18, .12, "pierre", 6)
        cylindre(x, y-1.1, .12, .045, 1.5, "ombre", 6)
        cylindre(x, y-1.1, 1.62, .13, .3, "or", 6, rayon2=.11)
        cylindre(x, y-1.1, 1.92, .16, .08, "ombre", 6, rayon2=.05)
    normales(terminer())


def point_facade(facade, a, z):
    nom, centre, rotation, l, p, h = facade[:6]
    c, s = math.cos(rotation), math.sin(rotation)
    b = -p/2-.1
    return Vector((centre[0]+a*c-b*s, centre[1]+a*s+b*c, centre[2]+z))


def cable_pendu(a, b, fleche, lanternes=0):
    # Câble noir en chaînette entre deux façades, lanternes pendues le long.
    n = 12
    points = []
    for k in range(n+1):
        t = k/n
        p = a.lerp(b, t)
        p.z -= fleche*4*t*(1-t)
        points.append(p)
    for p, q in zip(points, points[1:]):
        tige(tuple(p), tuple(q), .028, "ombre")
    for k in range(lanternes):
        t = (k+1)/(lanternes+1)
        p = a.lerp(b, t)
        p.z -= fleche*4*t*(1-t)
        tige(tuple(p), tuple(p-Vector((0, 0, .35))), .015, "ombre")
        c = p-Vector((0, 0, .35))
        cylindre(c.x, c.y, c.z-.32, .12, .3, "or", 6, rayon2=.1)
        cylindre(c.x, c.y, c.z-.04, .14, .06, "ombre", 6, rayon2=.04)


def cables_de_rue():
    global origine, angle
    commencer("Cables_de_la_ville_haute")
    origine, angle = (0, 0, 0), 0
    par_secteur = {}
    for f in facades_ville_haute:
        par_secteur.setdefault(f[8], {})[f[9]] = f
    secteurs = sorted(par_secteur)
    for i in secteurs:
        ext, lag = par_secteur[i].get("exterieure"), par_secteur[i].get("lagon")
        if ext and lag:
            # D'une rive à l'autre de la promenade, au ras des toits : de plus en plus de lanternes.
            for decal in ((-1.2,) if INTENSITE[i] < 3 else (-1.6, 1.4)):
                a = point_facade(ext, decal, ext[5]-.3)
                b = point_facade(lag, -decal, lag[5]-.3)
                cable_pendu(a, b, 1.1, 1+INTENSITE[i])
    # Le long de la rue, d'une maison à la suivante, de chaque côté.
    for rive in ("exterieure", "lagon"):
        suite = [par_secteur[i][rive] for i in secteurs if rive in par_secteur[i]]
        for f, g in zip(suite, suite[1:]):
            if abs(f[8]-g[8]) != 1:
                continue
            sens = 1 if rive == "exterieure" else -1
            a = point_facade(f, sens*(f[3]/2-.2), f[5]-.9)
            b = point_facade(g, -sens*(g[3]/2-.2), g[5]-.9)
            if (a-b).length < 16:
                cable_pendu(a, b, .7, 2 if INTENSITE[g[8]] >= 2 else 0)
    normales(terminer())


def colonne_affiches(nom, i, a, b, faces):
    # Colonne d'affichage des Semeurs sur la promenade : fût octogonal, corniche, dôme d'ardoise.
    # faces : {nom du repère : angle de la face (radians, 0 = côté lagon)} pour les affiches posées par Godot.
    global origine, angle
    centre, rot = repere_du_secteur(i, 36)
    c, s = math.cos(rot), math.sin(rot)
    x, y = centre[0]+a*c-b*s, centre[1]+a*s+b*c
    z = altitude(x, y)
    commencer(nom)
    origine, angle = (x, y, z), rot
    cylindre(0, 0, -.4, .78, .55, "pierre", 8)
    cylindre(0, 0, .15, .66, .14, "creme", 8)
    cylindre(0, 0, .29, .58, 2.9, "craie", 8)
    cylindre(0, 0, 3.19, .72, .2, "creme", 8)
    cylindre(0, 0, 3.39, .62, .12, "cuivre", 8)
    cylindre(0, 0, 3.51, .66, .55, "ardoise", 8, rayon2=.12)
    cylindre(0, 0, 4.06, .1, .3, "or", 6, rayon2=.03)
    # Restes d'anciennes affiches, déchirées, sur les faces sans affiche lisible.
    restes = random.Random(len(nom)*31+i)
    pans = [k for k in range(8) if all(abs((((k+.5)*math.tau/8)-t+math.pi) % math.tau-math.pi) > .5
                                       for t in faces.values())]
    for k in pans:
        t = (k+.5)*math.tau/8
        u, v = math.cos(t), math.sin(t)
        for _ in range(restes.randint(1, 2)):
            h0 = restes.uniform(.6, 2.4)
            l = restes.uniform(.18, .34)
            hh = restes.uniform(.25, .6)
            dx = restes.uniform(-.1, .1)
            n = Vector((u, v, 0))
            tg = Vector((-v, u, 0))
            p0 = n*.555+tg*(dx-l/2)
            p1 = n*.555+tg*(dx+l/2)
            pts = [(p0.x, p0.y, h0), (p1.x, p1.y, h0+restes.uniform(-.05, .05)),
                   (p1.x, p1.y, h0+hh), (p0.x, p0.y, h0+hh*restes.uniform(.6, 1))]
            morceau(pts, [(0, 1, 2, 3)], restes.choice(("creme", "sable", "peche")))
    # Une lanterne tout en haut : même la colonne devait rester éclairée.
    for k in range(4):
        t = k*math.tau/4
        tige((.62*math.cos(t), .62*math.sin(t), 3.3), (.95*math.cos(t), .95*math.sin(t), 3.4), .03, "ombre")
        cylindre(.95*math.cos(t), .95*math.sin(t), 3.0, .09, .25, "or", 6, rayon2=.075)
    normales(terminer(True))
    for repere, t in faces.items():
        u, v = math.cos(t), math.sin(t)
        px, py = .6*u, .6*v
        reperes_affiches.append((repere, x+px*c-py*s, y+px*s+py*c, z+1.75, rot+t))


def panneau_du_parvis():
    # Panneau d'affichage officiel à droite du perron : l'affiche 4 et le dernier morceau du plan.
    piece_parvis("Panneau_du_parvis")
    x, y = 3.4, PARVIS[2]-.25
    z0 = altitude(*vers_monde(x, y)[:2])-Z_PARVIS
    for dx in (-1.05, 1.05):
        boite(x+dx, y, z0-.3, .16, .16, 3.0, "chene")
    boite(x, y+.04, z0+.9, 2.3, .08, 1.6, "chene")
    boite(x, y-.01, z0+.98, 2.14, .04, 1.44, "bois")
    toit(x, y+.05, z0+2.55, 2.6, .55, .3, "ardoise")
    # Un vieux reste d'affiche, sous les deux affiches lisibles posées par Godot.
    morceau([(x-1.0, y-.04, z0+1.0), (x-.72, y-.04, z0+1.0), (x-.68, y-.04, z0+1.3), (x-1.0, y-.04, z0+1.22)],
            [(0, 1, 2, 3)], "sable")
    normales(terminer(True))
    for repere, dx in (("affiche_4", 0.0),):
        reperes_affiches.append((repere, *vers_monde(x+dx, y-.04, Z_PARVIS+z0+1.7)[:3], PARVIS_ANGLE-math.pi/2))
    # La stèle de la rue, à gauche du perron : trois soleils gravés.
    piece_parvis("Stele_trois_soleils")
    x = -3.3
    z0 = altitude(*vers_monde(x, y)[:2])-Z_PARVIS
    bloc = [(x-.5, y-.2, z0-.3), (x+.5, y-.2, z0-.3), (x+.5, y+.2, z0-.3), (x-.5, y+.2, z0-.3)]
    prisme(bloc, [(a, b, z0+1.5) for a, b, _ in bloc], "craie")
    boite(x, y, z0+1.5, 1.14, .5, .12, "creme")
    for k, dx in enumerate((-.28, 0, .28)):
        zc = z0+1.05+(.12 if k == 1 else 0)
        cylindre(x+dx, y-.2, zc, .1, .04, "or", 8, axe="y")
        for r in range(6):
            t = r*math.tau/6
            tige((x+dx+.13*math.cos(t), y-.22, zc+.13*math.sin(t)),
                 (x+dx+.19*math.cos(t), y-.22, zc+.19*math.sin(t)), .015, "or")
    normales(terminer(True))


def affiche_murale(nom, facade, a, z, repere):
    # Cadre de planches cloué au mur d'une maison, pour une affiche posée par Godot.
    global origine, angle
    commencer(nom)
    origine, angle = facade[1], facade[2]
    y = -facade[4]/2
    boite(a, y-.04, z-.75, 1.0, .06, 1.45, "chene")
    for dx in (-.42, .42):
        for dz in (-.6, .6):
            cylindre(a+dx, y-.07, z+dz, .03, .02, "or", 6, axe="y")
    normales(terminer())
    p = point_facade(facade, a, z)
    reperes_affiches.append((repere, p.x, p.y, p.z, facade[2]-math.pi/2))


def borne_de_recharge():
    # Borne des Semeurs au bout de la passerelle du quai : fût de pierre, prise de cuivre, cœur d'or.
    global origine, angle
    commencer("Borne_de_recharge")
    origine, angle = (-9.55, -29.2, 1.12), 0
    cylindre(0, 0, 0, .42, .18, "pierre", 8, rayon2=.38)
    cylindre(0, 0, .18, .3, 1.05, "craie", 8, rayon2=.25)
    cylindre(0, 0, 1.23, .36, .12, "creme", 8)
    # Cage de cuivre autour du cœur, qui luit quand la borne recharge (Godot).
    for k in range(6):
        t = k*math.tau/6
        tige((.26*math.cos(t), .26*math.sin(t), 1.35), (.2*math.cos(t), .2*math.sin(t), 1.85), .025, "cuivre")
    cylindre(0, 0, 1.85, .28, .1, "cuivre", 8, rayon2=.1)
    cylindre(0, 0, 1.95, .06, .14, "or", 6, rayon2=.02)
    # La prise, à hauteur de poignet du robot, tournée vers l'arrivée (le sud du ponton).
    boite(0, -.29, .62, .24, .1, .3, "cuivre")
    boite(0, -.34, .7, .12, .02, .14, "ombre")
    # Trois traits gravés : « plein ».
    for k in range(3):
        boite(0, -.25, .98+k*.07, .16-k*.03, .02, .025, "or")
    normales(terminer(True))
    # Le cœur doré qui s'allume est le « Cristal » de scenes/ile03/borne_recharge.tscn (pierre_soleil.gd).
    reperes_affiches.append(("borne_prise", -9.55, -29.2-.34, 1.12+.7, -math.pi/2))


def habiller_ville_haute():
    avant = set(bpy.data.objects)
    for facade in facades_ville_haute:
        habiller_facade(*facade)
    cables_de_rue()
    # Les affiches dans l'ordre de la descente : la plus ancienne en entrant, la plus récente au parvis.
    colonne_affiches("Colonne_affiches_11", 11, 4.4, .9, {"affiche_1": math.pi+.4})
    proj = next((f for f in facades_ville_haute if f[8] == 12 and f[9] == "exterieure"), None)
    if proj:
        affiche_murale("Cadre_affiche_2", proj, -proj[3]*.16, 2.0, "affiche_2")
    colonne_affiches("Colonne_affiches_13", 13, 0, 1.2, {"affiche_3": math.pi+.4})
    panneau_du_parvis()
    borne_de_recharge()
    for obj in set(bpy.data.objects)-avant:
        normales(obj)


# ----------------------------------------------------------------------------- repères pour Godot

def morceaux_du_plan():
    # Décidé le 2026-11-22 : les trois morceaux du plan d'éclairage sont posés dans les maisons ouvertes de
    # la ville basse, sur un meuble, à portée du robot (sur les colonnes, on ne les voyait pas).
    # Repère : position, puis direction (radians, Blender) vers le haut de la feuille posée à plat.
    def poser(nom, centre, rot, a, b, h):
        c, s = math.cos(rot), math.sin(rot)
        x, y = centre[0]+a*c-b*s, centre[1]+a*s+b*c
        return nom, x, y, centre[2]+h
    hauteur = lambda i: (hauteurs[i]+hauteurs[i+1])/2
    # A : sur la table de la maison du quai, la feuille tournée vers le fond de la pièce.
    reperes_affiches.append((*poser("morceau_A", (-8, -23.4, hauteur(0)), 0, -1.85, 1.05, 1.595), math.pi/2))
    # B : sur le comptoir des couturières, entre le mètre ruban et les coupons.
    c3, r3 = repere_du_secteur(3, 45)
    reperes_affiches.append((*poser("morceau_B", (*c3, hauteur(3)), r3, .55, 1.75, 1.555), r3+math.pi/2))
    # C : sur le bureau du maître, à l'école, la feuille tournée vers le tableau.
    c4, r4 = repere_du_secteur(4, 45)
    reperes_affiches.append((*poser("morceau_C", (*c4, hauteur(4)), r4, 4.5, -2.15, 1.655), r4))


def reperes_ville_haute():
    # Coordonnées Godot (x, y = hauteur, z = -y Blender) des emplacements à câbler dans la scène.
    reperes = []
    for r, y in enumerate(RANGEES):
        for c, x in enumerate(COLONNES):
            reperes.append((f"lanterne_{r*3+c+1}_{'motif' if MOTIF[r][c] == '●' else 'leurre'}",
                            *vers_monde(x, y, Z_PARVIS)))
    reperes.append(("porte_centre", *vers_monde(0, FACADE, Z_PARVIS)))
    reperes.append(("pupitre_voyants", *vers_monde(2.6, 3.85, Z_PARVIS+1.6)))
    reperes.append(("affiche_5_porte", *vers_monde(0, FACADE-.12, Z_PARVIS+3.3)))
    reperes.append(("plan_archipel", *vers_monde(-.7, SALLE-.56, Z_PARVIS+2.75)))
    reperes.append(("ordres_ysolde", *vers_monde(-1.1, 12.2, Z_PARVIS+1.3)))
    reperes.append(("lettres_tavin", *vers_monde(1.4, 13.2, Z_PARVIS+.65)))
    with open(racine/"tools/blender/sources/ville_haute_reperes.txt", "w", encoding="utf-8") as f:
        f.write(f"# angle du parvis (rotation Y Godot, radians) : {PARVIS_ANGLE:.4f}\n")
        for nom, x, y, z in reperes:
            f.write(f"{nom}\t{x:.3f}\t{z:.3f}\t{-y:.3f}\n")
        # Affiches et borne : position, puis direction (radians, repère Blender) de la normale sortante.
        for nom, x, y, z, t in reperes_affiches:
            f.write(f"{nom}\t{x:.3f}\t{z:.3f}\t{-y:.3f}\t{t:.4f}\n")


def construire_ville_haute():
    avant = set(bpy.data.objects)
    parvis_trois_soleils()
    maison_commune()
    habiller_ville_haute()
    morceaux_du_plan()
    # Normales vers l'extérieur sur tout ce qui vient d'être construit (Godot cache les faces arrière).
    for obj in set(bpy.data.objects)-avant:
        normales(obj)
    reperes_ville_haute()
