"""La grotte d'Aube : « Là où mes amis dansent » (ILE_03_COLONIE.md §6).

Chargé par colonie_du_lagon.py (exec dans ses globales : point, morceau, boite, pilier, tige, prisme,
triangles_du_sol, intersect_ray_tri, palette… y sont déjà définis).

1. L'ENTRÉE, dans la ruelle entre l'école et la maison d'Aube : les pavés se sont effondrés, des marches
   taillées descendent vers une arche noire. Le sol du secteur 5 est découpé au bord des marches.
2. LA GROTTE, sous l'île (GROTTE_Z, bien plus bas que tout le reste) : marches, galerie qui serpente,
   salle ronde du coin noir où Aube est assise (modèle Meshy posé par scenes/ile03/coin_noir.tscn).
   On y passe par un fondu au noir (scripts/passage_grotte.gd) entre l'arche de l'entrée et celle de
   la grotte. Le sol et les parois ont des maillages de collision dédiés. Vue de dessus : la roche est coupée à plat (comme les maisons) ; un plafond invisible,
   posé dans Godot, ne sert qu'à faire l'ombre.
Les parois sont des anneaux facettés le long du chemin, colorés en strates sombres.
"""

from mathutils.geometry import tessellate_polygon

palette.update({"roche_sombre": "5E4F5C", "roche": "7D6873", "roche_claire": "9A8590",
                "terre_sombre": "7E6E62", "racine": "8A6A58", "eau_sombre": "4F7F86", "nuit": "231E2B"})
for _nom in ("roche_sombre", "roche", "roche_claire", "terre_sombre", "racine", "eau_sombre", "nuit"):
    _mat = bpy.data.materials.new(_nom)
    _hexa = palette[_nom]
    _coul = [((int(_hexa[i:i+2], 16)/255 + .055)/1.055)**2.4 for i in (0, 2, 4)]
    _mat.diffuse_color = (*_coul, 1)
    _mat.use_nodes = True
    _bsdf = next(n for n in _mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    _bsdf.inputs["Base Color"].default_value = (*_coul, 1)
    _bsdf.inputs["Roughness"].default_value = .85
    materiaux[_nom] = _mat

GROTTE_SECTEUR = 5
_g_hasard = random.Random(4242)

# ------------------------------------------------------------------ 1. l'entrée dans la ruelle

# Le trou : un rectangle dans la ruelle, les marches descendent vers l'ouest (x décroissant).
ENTREE_X0, ENTREE_X1 = -52.6, -49.2      # de l'arche (ouest) au haut des marches (est), à l'ouest du pignon de l'école
ENTREE_Y0, ENTREE_Y1 = 11.05, 13.35    # entièrement dans le secteur 5 (la limite avec le 4 passe vers y = 10,7)
ENTREE_MARCHES = 6
ENTREE_PROF = 1.30                         # profondeur du palier sous le sol


def _g_sol(i, x, y):
    depart = Vector((x, y, 40))
    for tri in triangles_du_sol[i]:
        impact = intersect_ray_tri(*tri, Vector((0, 0, -1)), depart, True)
        if impact is not None:
            return impact.z
    return hauteurs[i]


ENTREE_Z = _g_sol(GROTTE_SECTEUR, (ENTREE_X0+ENTREE_X1)/2, (ENTREE_Y0+ENTREE_Y1)/2)


def _g_dans_rect(x, y, marge=0.0):
    return ENTREE_X0-marge <= x <= ENTREE_X1+marge and ENTREE_Y0-marge <= y <= ENTREE_Y1+marge


def dans_grotte(i, t, r, marge=.45):
    # Vrai si le point (secteur i, t, rayon) tombe sur le trou de l'entrée : la friche n'y pousse pas.
    if i != GROTTE_SECTEUR:
        return False
    a = point(i, r, 0)
    b = point(i+1, r, 0)
    return _g_dans_rect(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, marge)


def _g_demi_plan(polygone, axe, bord, cote):
    """Découpe sans changer l’altitude du triangle de départ."""
    resultat = []
    for a, b in zip(polygone, polygone[1:]+polygone[:1]):
        da, db = (a[axe]-bord)*cote, (b[axe]-bord)*cote
        if da >= 0:
            resultat.append(a)
        if da*db < 0:
            milieu = a.lerp(b, da/(da-db))
            milieu[axe] = bord
            resultat.append(milieu)
    return resultat


def bande_herbe_trouee():
    # On garde les parties extérieures des deux triangles de la bande de sauge.
    limites = ((0, ENTREE_X0, 1), (0, ENTREE_X1, -1),
               (1, ENTREE_Y0, 1), (1, ENTREE_Y1, -1))
    for triangle in triangles_du_sol[GROTTE_SECTEUR][-2:]:
        reste = list(triangle)
        for axe, bord, cote in limites:
            exterieur = _g_demi_plan(reste, axe, bord, -cote)
            if len(exterieur) >= 3:
                _g_sol_face(exterieur, "sauge")
            reste = _g_demi_plan(reste, axe, bord, cote)
            if len(reste) < 3:
                break


def _entree():
    global origine, angle
    x0, x1, y0, y1, z = ENTREE_X0, ENTREE_X1, ENTREE_Y0, ENTREE_Y1, ENTREE_Z
    fond = z-ENTREE_PROF
    ym = (y0+y1)/2
    commencer("Entree_grotte_aube")
    origine, angle = (0, 0, 0), 0
    # Les parois de la fosse, taillées dans la roche (strates, un peu en retrait vers le bas).
    for k, (haut, bas, ton) in enumerate(((0, -.5, "ocre"), (-.5, -1.3, "pierre"), (-1.3, -2.2, "roche"))):
        r = .05*k
        zh, zb = z+haut, max(z+bas, fond-.05)
        boite((x0+x1)/2, y0-.15+r, zb, x1-x0+.3, .3, zh-zb, ton)
        boite((x0+x1)/2, y1+.15-r, zb, x1-x0+.3, .3, zh-zb, ton)
    # Le fond : un mur de roche percé d'une arche toute noire qui s'enfonce sous la ville.
    boite(x0-.15, ym, fond-.05, .3, y1-y0+.6, z-fond+.05, "roche")
    arche = [(ym+.85*math.cos(math.radians(a)), fond+1.45+.85*math.sin(math.radians(a))) for a in range(0, 181, 15)]
    arche = [(ym+.85, fond)] + arche + [(ym-.85, fond)]
    prisme([(x0+.02, y, zz) for y, zz in arche], [(x0+.03, y, zz) for y, zz in arche], "nuit")
    for (ya, za), (yb, zb) in zip(arche[1:-1], arche[2:-1]):
        tige((x0+.04, ya, za), (x0+.04, yb, zb), .06, "roche_claire")
    # Les marches, de l'est (haut) vers l'ouest (bas), et le palier devant l'arche.
    pas = (x1-x0-.9)/ENTREE_MARCHES
    for s in range(ENTREE_MARCHES):
        xa = x1-s*pas
        zt = z-(s+1)*ENTREE_PROF/ENTREE_MARCHES
        boite(xa-pas/2, ym, fond-.1, pas, y1-y0, zt-fond+.1, "pierre" if s % 2 else "roche_claire")
    boite(x0+.45, ym, fond-.1, .9, y1-y0, .1, "terre_sombre")
    terminer()

    # Rampe, palier et parois du passage, sans volume transversal au seuil.
    commencer("Collisions_entree_grotte_aube")
    sections = [
        (Vector((x0, y0, fond)), Vector((x0, y1, fond))),
        (Vector((x0+.9, y0, fond)), Vector((x0+.9, y1, fond))),
        (Vector((x1, y0, _g_sol(GROTTE_SECTEUR, x1, y0))),
         Vector((x1, y1, _g_sol(GROTTE_SECTEUR, x1, y1)))),
    ]
    _g_couloir_collision(sections, plafond=lambda p: _g_sol(GROTTE_SECTEUR, p.x, p.y))
    terminer("-colonly")

    # Des dalles disjointes encadrent la fosse ; deux se sont cassées sur ses bords.
    commencer("Paves_effondres_grotte_aube")
    for k in range(18):
        cote = k % 4
        u = _g_hasard.uniform(0, 1)
        if cote == 0:
            x, y = x0+u*(x1-x0), y0-.35
        elif cote == 1:
            x, y = x0+u*(x1-x0), y1+.35
        elif cote == 2:
            x, y = x1+.35, y0+u*(y1-y0)
        else:
            x, y = x0-.35, y0+u*(y1-y0)
        t = _g_hasard.uniform(.22, .34)
        h = _g_hasard.uniform(-.04, .05)
        dalle = [(x-t, y-t*.8, z+.01+h), (x+t, y-t*.8, z+.01-h), (x+t, y+t*.8, z+.01+h*.5), (x-t, y+t*.8, z+.01-h*.5)]
        prisme(dalle, [(a, b, c+.06) for a, b, c in dalle], "pave_use" if k % 3 else "fissure")
    for s, (dx, rot) in enumerate(((.4, .25), (1.2, -.3))):
        zt = z-(s*2+2)*ENTREE_PROF/ENTREE_MARCHES
        cx = x1-.5-dx
        bord = ym + (.78 if s == 0 else -.78)
        dalle = [(cx-.3, bord-.27, zt), (cx+.25, bord-.25+rot*.2, zt+.18),
                 (cx+.3, bord+.24, zt+.15), (cx-.28, bord+.25, zt)]
        prisme(dalle, [(a, b, c+.07) for a, b, c in dalle], "pave_use")
    terminer()


# ------------------------------------------------------------------ 2. la grotte, sous l'île

GROTTE_Z = -30.0                       # niveau du sol de la galerie
# Chemin (x, y, sol), du palier de l’arche à la salle.
GROTTE_CTRL = [
    (-51.55, 10.85, GROTTE_Z+1.30),
    (-49.70, 10.85, GROTTE_Z+1.30),    # palier de l’arche
    (-46.65, 11.45, GROTTE_Z-.10),     # arrivée au bas de la descente
    (-45.55, 12.65, GROTTE_Z-.15),
    (-44.9, 15.0, GROTTE_Z-.2),
    (-45.7, 17.4, GROTTE_Z-.25),
    (-47.0, 18.9, GROTTE_Z-.3),        # entrée de la salle
]
GROTTE_SALLE = Vector((-48.3, 20.4, GROTTE_Z-.3))
GROTTE_SALLE_RAYON = 2.25
GROTTE_HAUT = GROTTE_Z+2.5             # la roche est coupée à plat à cette hauteur (juste au-dessus du robot)


def _g_catmull(points, pas=.45):
    pts = [points[0]] + points + [points[-1]]
    dense = []
    for k in range(1, len(pts)-2):
        p0, p1, p2, p3 = (Vector(p) for p in pts[k-1:k+3])
        for s in range(16):
            u = s/16
            dense.append(.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u))
    dense.append(Vector(points[-1]))
    res, reste = [dense[0]], 0.0
    for a, b in zip(dense, dense[1:]):
        seg = (b.xy-a.xy).length
        d = pas-reste
        while d <= seg:
            res.append(a.lerp(b, d/seg if seg else 0))
            d += pas
        reste = seg-(d-pas)
    if (res[-1].xy-dense[-1].xy).length > .1:
        res.append(dense[-1])
    return res


GROTTE_PTS = _g_catmull(GROTTE_CTRL)
_N = len(GROTTE_PTS)


def _g_bruit(k, graine):
    return math.sin(k*.61+graine)*.6+math.sin(k*1.73+graine*2.1)*.4


def _g_demi(k):
    p = GROTTE_PTS[k]
    if p.z > GROTTE_Z+.05:
        return 1.12
    return 1.18+.12*_g_bruit(k, 1.0)


def _g_profil(k, cote):
    # Points de la paroi (écart à l'axe, hauteur au-dessus du sol), du sol jusqu'à la coupe.
    w = _g_demi(k)
    z0 = GROTTE_PTS[k].z
    h = GROTTE_HAUT-z0
    b = lambda g: .13*_g_bruit(k, g+cote*7)
    # En haut des marches la paroi est moins haute : les hauteurs se tassent sous la coupe.
    k_h = min(1.0, (h-.25)/2.4)
    return [(w, 0), (w+.14+b(1), .45*k_h), (w+.04+b(2), 1.1*k_h), (w+.26+b(3), 1.75*k_h),
            (w+.42+b(4), 2.4*k_h), (w+.62+b(5), h)]


def _g_ton(hauteur, k):
    if hauteur < .55:
        return "roche_sombre"
    if hauteur < 1.35:
        return "roche" if (k//3) % 2 else "roche_sombre"
    if hauteur < 2.2:
        return "roche_claire" if (k//4) % 2 else "roche"
    return "strate"


def _g_anneaux():
    # Pour chaque point du chemin : la normale horizontale et les points des deux parois.
    anneaux = []
    for k, p in enumerate(GROTTE_PTS):
        a = GROTTE_PTS[max(k-1, 0)]
        b = GROTTE_PTS[min(k+1, _N-1)]
        d = (b.xy-a.xy).normalized()
        n = Vector((-d.y, d.x))
        gauche = [Vector((p.x+n.x*e, p.y+n.y*e, p.z+h)) for e, h in _g_profil(k, 0)]
        droite = [Vector((p.x-n.x*e, p.y-n.y*e, p.z+h)) for e, h in _g_profil(k, 1)]
        anneaux.append((gauche, droite, n))
    return anneaux


def _g_salle_profil(theta):
    r = GROTTE_SALLE_RAYON+.25*math.sin(theta*3+1)+.15*math.sin(theta*5+2)
    h = GROTTE_HAUT-GROTTE_SALLE.z
    k_h = min(1.0, (h-.25)/2.6)
    return [(r, 0), (r+.18, .5*k_h), (r+.05, 1.2*k_h), (r+.3, 1.9*k_h), (r+.5, 2.6*k_h), (r+.7, h)]


def _g_face(points, direction, ton):
    """Oriente chaque triangle du côté jouable."""
    indices = []
    for k in range(1, len(points)-1):
        normale = (points[k]-points[0]).cross(points[k+1]-points[0])
        if normale.length_squared > 1e-12:
            indices.append((0, k, k+1) if normale.dot(direction) > 0 else (0, k+1, k))
    if indices:
        morceau([tuple(p) for p in points], indices, ton)


def _g_sol_face(points, ton="terre_sombre"):
    _g_face(points, Vector((0, 0, 1)), ton)


def _g_paroi_collision(a, b, vers, plafond=None):
    haut_a, haut_b = a.copy(), b.copy()
    haut_a.z = a.z+2.8 if plafond is None else max(a.z, plafond(a))
    haut_b.z = b.z+2.8 if plafond is None else max(b.z, plafond(b))
    _g_face([a, b, haut_b, haut_a], vers-(a+b)/2, "roche")


def _g_couloir_collision(sections, plafond=None):
    a, b = sections[0]
    _g_paroi_collision(a, b, sum(sections[1], Vector())/2, plafond)
    for (a, b), (c, d) in zip(sections, sections[1:]):
        _g_sol_face([a, b, d, c])
        milieu = (a+b+c+d)/4
        _g_paroi_collision(a, c, milieu, plafond)
        _g_paroi_collision(b, d, milieu, plafond)


def _g_contour_salle(anneau_final):
    """L’arc de la salle et ses deux raccords aux bords de la galerie."""
    gauche, droite = anneau_final[0][0], anneau_final[1][0]
    a, b = (p.xy-GROTTE_SALLE.xy for p in (gauche, droite))
    debut, fin = math.atan2(a.y, a.x), math.atan2(b.y, b.x)
    # Suivre le grand arc. Le petit arc laisse l’entrée entièrement ouverte.
    if (fin-debut) % math.tau < math.pi:
        gauche, droite = droite, gauche
        debut, fin = fin, debut
    amplitude = (fin-debut) % math.tau
    n_s = 24
    angles = [debut+amplitude*k/n_s for k in range(n_s+1)]
    contour = []
    for t in angles:
        profil = _g_salle_profil(t)
        contour.append([GROTTE_SALLE+Vector((r*math.cos(t), r*math.sin(t), h)) for r, h in profil])
    if gauche == anneau_final[0][0]:
        return [anneau_final[0], *contour, anneau_final[1]]
    return [anneau_final[1], *contour, anneau_final[0]]


def construire_grotte():
    global origine, angle
    _entree()
    anneaux = _g_anneaux()
    salle_xy = GROTTE_SALLE.xy
    fin = next(k for k, p in enumerate(GROTTE_PTS)
               if (p.xy-salle_xy).length < GROTTE_SALLE_RAYON)
    contour_salle = _g_contour_salle(anneaux[fin-1])
    bord_salle = [profil[0] for profil in contour_salle]
    sol_salle = [[bord_salle[i] for i in face] for face in tessellate_polygon([bord_salle])]

    commencer("Grotte_aube")
    origine, angle = (0, 0, 0), 0
    # Parois de la galerie : bandes entre anneaux successifs, colorées en strates.
    for k in range(fin-1):
        for cote in (0, 1):
            A, B = anneaux[k][cote], anneaux[k+1][cote]
            for s in range(len(A)-1):
                q = [tuple(A[s]), tuple(B[s]), tuple(B[s+1]), tuple(A[s+1])]
                hm = (A[s].z+A[s+1].z)/2-GROTTE_PTS[k].z
                morceau(q, [(0, 1, 2, 3), (3, 2, 1, 0)], _g_ton(hm, k))
        gA, dA = anneaux[k][0][0], anneaux[k][1][0]
        gB, dB = anneaux[k+1][0][0], anneaux[k+1][1][0]
        _g_sol_face([gA, dA, dB, gB], "pierre" if GROTTE_PTS[k].z > GROTTE_Z else "terre_sombre")
    # Le bout de départ : un mur de roche avec l'arche noire par où l'on est arrivé.
    g0, d0, n0 = anneaux[0]
    p0 = GROTTE_PTS[0]
    dir0 = (GROTTE_PTS[1].xy-p0.xy).normalized()
    dos = Vector((-dir0.x, -dir0.y, 0))*.15
    for s in range(len(g0)-1):
        morceau([tuple(g0[s]+dos), tuple(d0[s]+dos), tuple(d0[s+1]+dos), tuple(g0[s+1]+dos)], [(0, 1, 2, 3), (3, 2, 1, 0)], "roche")
    arche = [(.55*math.cos(math.radians(a)), 1.45+.55*math.sin(math.radians(a))) for a in range(0, 181, 15)]
    arche = [(.55, 0)] + arche + [(-.55, 0)]
    pts = [Vector((p0.x+n0.x*e, p0.y+n0.y*e, p0.z+h))+dos*.8 for e, h in arche]
    morceau([tuple(p) for p in pts], [tuple(range(len(pts))), tuple(reversed(range(len(pts))))], "nuit")

    # La salle et la galerie partagent le même bord, décor comme collisions.
    for A, B in zip(contour_salle, contour_salle[1:]):
        for k in range(len(A)-1):
            _g_face([A[k], B[k], B[k+1], A[k+1]], GROTTE_SALLE-(A[k]+B[k])/2, _g_ton(A[k].z-GROTTE_SALLE.z, k))
    for triangle in sol_salle:
        _g_sol_face(triangle, "mousse_sombre")
    terminer()

    commencer("Collisions_galerie_et_salle_aube")
    sections = [(gauche[0], droite[0]) for gauche, droite, _ in anneaux[:fin]]
    _g_couloir_collision(sections)
    for A, B in zip(contour_salle, contour_salle[1:]):
        a, b = A[0], B[0]
        bord = b-a
        vers = (a+b)/2 + Vector((-bord.y, bord.x, 0))
        _g_paroi_collision(a, b, vers)
    for triangle in sol_salle:
        _g_sol_face(triangle)
    terminer("-colonly")

    # La roche coupée à plat autour de la grotte (vue de dessus), avec un col qui cache les jointures.
    commencer("Roche_grotte_aube")
    pas_c = .45
    xs = [p.x for p in GROTTE_PTS]+[GROTTE_SALLE.x]
    ys = [p.y for p in GROTTE_PTS]+[GROTTE_SALLE.y]
    xa, xb = min(xs)-14, max(xs)+14
    ya, yb = min(ys)-14, max(ys)+14
    def ouvert(x, y):
        v = Vector((x, y))
        if (v-salle_xy).length < GROTTE_SALLE_RAYON+.65:
            return True
        for k in range(fin):
            if (v-GROTTE_PTS[k].xy).length < _g_demi(k)+.6:
                return True
        return False
    x = xa
    while x < xb:
        y = ya
        while y < yb:
            if not ouvert(x+pas_c/2, y+pas_c/2):
                ton = "roche_sombre"
                morceau([(x, y, GROTTE_HAUT), (x+pas_c, y, GROTTE_HAUT), (x+pas_c, y+pas_c, GROTTE_HAUT), (x, y+pas_c, GROTTE_HAUT)], [(0, 1, 2, 3)], ton)
            y += pas_c
        x += pas_c
    for k in range(fin-1):
        for cote in (0, 1):
            A, B = anneaux[k][cote][-1], anneaux[k+1][cote][-1]
            n = anneaux[k][2]*(1 if cote == 0 else -1)
            ext = Vector((n.x, n.y, 0))*1.3
            # le col déborde un peu le long du chemin pour fermer les virages
            le_long = (B-A).normalized()*.25
            A, B = A-le_long, B+le_long
            # pas de col au-dessus de la salle
            if min((A+ext).xy-salle_xy, (B+ext).xy-salle_xy, A.xy-salle_xy, B.xy-salle_xy, key=lambda v: v.length).length < GROTTE_SALLE_RAYON+.9:
                continue
            q = [tuple(A-Vector((0, 0, .02))), tuple(B-Vector((0, 0, .02))), tuple(B+ext-Vector((0, 0, .02))), tuple(A+ext-Vector((0, 0, .02)))]
            morceau(q, [(0, 1, 2, 3), (3, 2, 1, 0)], "roche_sombre")
    for A, B in zip(contour_salle, contour_salle[1:]):
        a, b = A[-1], B[-1]
        ea = Vector((a.x-GROTTE_SALLE.x, a.y-GROTTE_SALLE.y, 0)).normalized()*1.3
        eb = Vector((b.x-GROTTE_SALLE.x, b.y-GROTTE_SALLE.y, 0)).normalized()*1.3
        _g_sol_face([a, b, b+eb, a+ea], "roche_sombre")
    terminer()

    # Racines, rochers et flaques sur les bords du passage.
    commencer("Decor_grotte_aube")
    for k in range(6, fin-1, 3):
        for cote in (0, 1):
            if _g_hasard.random() < .45:
                continue
            haut = anneaux[k][cote][-1]
            n = anneaux[k][2]*(1 if cote == 0 else -1)
            long = _g_hasard.uniform(1.0, 2.2)
            ton = _g_hasard.choice(("racine", "racine", "saumon", "bois"))
            prec = (haut.x, haut.y, haut.z+.02)
            for s in range(1, 8):
                u = s/7
                pt = (haut.x-n.x*(.25+.55*u)+.07*math.sin(s*1.9+k), haut.y-n.y*(.25+.55*u)+.07*math.cos(s*1.3+k), haut.z-long*u)
                tige(prec, pt, .05*(1-u*.6), ton)
                prec = pt
            if _g_hasard.random() < .5:
                for s in range(3):
                    pilier(prec[0]+_g_hasard.uniform(-.1, .1), prec[1]+_g_hasard.uniform(-.1, .1), prec[2]-.05, .02, .12, ton, .005)
    for k in range(8, fin-2, 4):
        p = GROTTE_PTS[k]
        g, d, n = anneaux[k]
        cote = 1 if k % 8 else -1
        w = _g_demi(k)-.12
        bx, by = p.x+n.x*w*cote, p.y+n.y*w*cote
        pilier(bx, by, p.z, _g_hasard.uniform(.14, .24), _g_hasard.uniform(.4, .9), "roche_claire" if k % 3 else "roche", .02)
        pilier(bx+n.x*.2*cote, by+n.y*.2*cote, p.z, .1, .3, "roche", .02)
        for _ in range(4):
            pilier(p.x+_g_hasard.uniform(-.6, .6), p.y+_g_hasard.uniform(-.6, .6), p.z, .06, .05, "roche_claire", .03)
    for k in range(5, fin-1, 4):
        p = GROTTE_PTS[k]
        if p.z > GROTTE_Z+.02:
            continue
        cx, cy = p.x+_g_hasard.uniform(-.4, .4), p.y+_g_hasard.uniform(-.4, .4)
        r = _g_hasard.uniform(.25, .45)
        plaque = [(cx+r*math.cos(s*math.tau/7)*_g_hasard.uniform(.7, 1.2), cy+r*math.sin(s*math.tau/7)*_g_hasard.uniform(.7, 1.2), p.z+.008) for s in range(7)]
        prisme(plaque, [(x, y, z+.003) for x, y, z in plaque], _g_hasard.choice(("terre_claire", "roche_sombre", "mousse_sombre")))
    for k in (int(fin*.45), int(fin*.75)):
        p = GROTTE_PTS[k]
        flaque = [(p.x+.5*math.cos(s*math.tau/10)*(1+.22*math.sin(s*2.3)), p.y+.36*math.sin(s*math.tau/10), p.z+.012) for s in range(10)]
        prisme(flaque, [(x, y, z+.004) for x, y, z in flaque], "eau_sombre")
    # Dans la salle : un tapis de mousse et de fleurs roses, là où ses amis dansaient.
    for s in range(40):
        a = _g_hasard.uniform(0, math.tau)
        rr = _g_hasard.uniform(.2, GROTTE_SALLE_RAYON-.25)
        x, y = GROTTE_SALLE.x+rr*math.cos(a), GROTTE_SALLE.y+rr*math.sin(a)
        pilier(x, y, GROTTE_SALLE.z, _g_hasard.uniform(.1, .2), .05, "mousse", .05)
        if s % 2:
            pilier(x, y, GROTTE_SALLE.z+.05, .035, .04, _g_hasard.choice(("rose", "corail", "creme")), .014)
    terminer()

    # Repères pour la scène Godot (coordonnées Godot : x, z, -y).
    milieu_entree = (ENTREE_Y0+ENTREE_Y1)/2
    fond_entree = ENTREE_Z-ENTREE_PROF
    p_arrivee = GROTTE_CTRL[0]
    reperes = [
        ("arche_entree", ENTREE_X0+.60, fond_entree, milieu_entree),
        ("arrivee_entree", ENTREE_X0+1.82, fond_entree+0.62, milieu_entree),
        ("arche_grotte", GROTTE_PTS[0].x+.52, GROTTE_PTS[0].z, GROTTE_PTS[0].y),
        # Arrivée sur le palier, au-delà du volume de retour.
        ("arrivee_grotte", p_arrivee[0]+1.38, p_arrivee[2]+.13, p_arrivee[1]),
        ("salle", GROTTE_SALLE.x, GROTTE_SALLE.z, GROTTE_SALLE.y),
        ("entree_salle", GROTTE_PTS[fin-1].x, GROTTE_PTS[fin-1].z, GROTTE_PTS[fin-1].y),
        ("milieu_galerie", GROTTE_PTS[fin//2].x, GROTTE_PTS[fin//2].z, GROTTE_PTS[fin//2].y),
    ]
    with open(racine/"tools/blender/sources/grotte_aube_reperes.txt", "w", encoding="utf-8") as f:
        for nom, x, z, y in reperes:
            f.write(f"{nom} {x:.3f} {z:.3f} {-y:.3f}\n")
