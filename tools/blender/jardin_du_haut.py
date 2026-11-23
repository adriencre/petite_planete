"""Le jardin du haut de la Colonie (G3) : chemin de halage, écluse à sas, jardin clos, serres basses.

Exécuté par colonie_du_lagon.py (exec dans ses globales), après ville_haute.py.
Décisions : ILE_03_COLONIE.md, § G3 (précisé le 2026-11-22).

1. LE CHEMIN DE HALAGE : un quai de pierre au pied de la falaise du lagon, du quai (secteur 0) jusqu'au
   pied de l'écluse (secteur 6). Il reste au-dessus de la marée haute.
2. L'ÉCLUSE : un avant-port, puis 4 sas en escalier le long de la falaise nord (secteurs 6 à 8). La marée
   haute met le lagon au niveau du 1er sas ; chaque sas monte de 2,1 m avec l'eau de la citerne. Les
   vannes-guillotines, le ponton, le levier, le flotteur et l'eau des sas sont des objets à part, origine
   sur leur pivot : Godot les anime.
3. LE JARDIN DU HAUT : enclos au bord de la falaise (secteurs 8 à 10, côté lagon), haut mur sur la rue,
   porte de service (la porte barrée est posée dans Godot), lampe-mère, premier arbre rose, établi des
   jardiniers, belvédère sur le vieux port, citerne de pluie visible de la ville et sa rigole.
4. LES SERRES BASSES : les verrières des secteurs 8 à 10 s'ouvrent sur la rue ; 7 arbres roses y penchent
   fortement vers la lampe-mère, en éventail.
"""

from mathutils import Matrix

palette.update({"enduit_blanc": "FBE8CF", "terreau": "8F6A55", "eau_canal": "7FCFC6"})
for _nom in ("enduit_blanc", "terreau", "eau_canal"):
    _mat = bpy.data.materials.new(_nom)
    _hexa = palette[_nom]
    _coul = [((int(_hexa[i:i+2], 16)/255 + .055)/1.055)**2.4 for i in (0, 2, 4)]
    _mat.diffuse_color = (*_coul, 1)
    _mat.use_nodes = True
    _bsdf = next(n for n in _mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    _bsdf.inputs["Base Color"].default_value = (*_coul, 1)
    _bsdf.inputs["Roughness"].default_value = .8
    materiaux[_nom] = _mat

# Les secteurs dont la bande côté lagon devient le jardin (plus de logis de décor).
SECTEURS_JARDIN = (8, 9, 10)
# Le jardin va de la falaise au mur, à ce rayon (la rue de crête commence vers 33).
R_MUR = 32.2
EPAISSEUR_MUR = .8
Z_JARDIN = 10.1
HAUT_MUR = 6.3
# Le chemin de halage : niveau (au-dessus de la marée haute, +0,5) et largeur.
Z_HALAGE = 1.0
LARGEUR_HALAGE = 1.9

# ------------------------------------------------------------------ repère de l'écluse
# L'écluse suit la corde de la falaise, du pied du secteur 6 au coin du secteur 9.
# u : le long de l'écluse (vers l'est, vers le haut) ; b : vers la falaise (b < 0 : côté lagon).
_A = Vector(point(6, interieurs[6], 0)[:2])
_B = Vector(point(9, interieurs[9], 0)[:2])
_AXE = (_B-_A).normalized()
ANGLE_ECLUSE = math.atan2(_AXE.y, _AXE.x)
LONGUEUR_ECLUSE = (_B-_A).length
# Avant-port, puis 4 sas. Niveaux d'eau bas de chaque sas (L) ; chaque sas monte de MONTEE.
AVANT_PORT = 4.6
LONG_SAS = 5.2
MONTEE = 2.1
NIVEAUX = [.5 + MONTEE*k for k in range(4)]            # 0,5 / 2,6 / 4,7 / 6,8 (haut : 8,9)
FRANC_BORD = 1.1                                        # pont du ponton au-dessus de l'eau
INDEX_FLOTTEUR = 2.9                                    # l'index doré, au-dessus du flotteur
# Eau des sas entre b = EAU_B[0] et EAU_B[1] ; mur côté lagon au-delà, mur côté falaise en deçà.
EAU_B = (-5.6, -1.6)
MUR_FACE = (-6.4, -5.6)
MUR_DOS = (-1.6, 1.4)
EPAISSEUR_VANNE = .7
HAUT_PORTIQUE = 5.6
# Course d'une vanne qui s'ouvre (Godot) : son bas passe au-dessus du robot debout sur le ponton.
LEVEE_VANNE = 5.8


def debut_sas(k):
    return AVANT_PORT + LONG_SAS*k


def haut_sas(k):
    # Haut des murs du sas k : 1,3 m au-dessus de son niveau haut ; le dernier affleure le jardin.
    return NIVEAUX[k]+MONTEE+1.3


def ecluse_monde(u, b, z=0):
    c, s = math.cos(ANGLE_ECLUSE), math.sin(ANGLE_ECLUSE)
    return (_A.x+u*c-b*s, _A.y+u*s+b*c, z)


def piece_ecluse(nom):
    global origine, angle
    commencer(nom)
    origine, angle = (_A.x, _A.y, 0), ANGLE_ECLUSE


def sur_pivot(obj, pivot, rotation):
    # Origine de l'objet sur son pivot (repère monde), axes tournés de `rotation` : Godot l'anime simplement.
    obj.data.transform(Matrix.Translation((-pivot[0], -pivot[1], -pivot[2])))
    obj.data.transform(Matrix.Rotation(-rotation, 4, "Z"))
    obj.location = pivot
    obj.rotation_euler.z = rotation
    return obj


def bord_falaise(i, t, decalage=0.0, z=None):
    # Point du bord de la falaise du lagon dans le secteur i (t de 0 à 1), décalé vers la terre.
    a = point(i, interieurs[i]+decalage, 0)
    b = point(i+1, interieurs[i+1]+decalage, 0)
    h = Z_JARDIN if z is None else z
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, h)


def au_rayon(i, t, rayon, z):
    a = point(i, rayon, 0)
    b = point(i+1, rayon, 0)
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, z)


def mur_droit(p, q, z0, z1, epaisseur, ton, trous=(), chaperon="tuile"):
    # Mur de p à q (repère monde), centré sur la ligne. trous : (t0, t1, hauteur) le long du mur.
    global origine, angle
    dx, dy = q[0]-p[0], q[1]-p[1]
    longueur = math.hypot(dx, dy)
    origine, angle = (p[0], p[1], 0), math.atan2(dy, dx)
    bords = [0.0]
    for t0, t1, _ in sorted(trous):
        bords += [t0*longueur, t1*longueur]
    bords.append(longueur)
    for k in range(0, len(bords), 2):
        if bords[k+1]-bords[k] > .01:
            boite((bords[k]+bords[k+1])/2, 0, z0, bords[k+1]-bords[k], epaisseur, z1-z0, ton)
    for t0, t1, h in trous:
        if z1-z0-h > .01:
            boite((t0+t1)*longueur/2, 0, z0+h, (t1-t0)*longueur, epaisseur, z1-z0-h, ton)
    if chaperon:
        boite(longueur/2, 0, z1, longueur+.1, epaisseur+.24, .22, chaperon)
    return longueur


def arbre_penche(x, y, z, taille, direction, inclinaison, teintes, grand=1.0, couronne=1.0):
    # Arbre rose penché : tronc en trois tronçons de plus en plus inclinés, couronne décalée du même côté.
    # direction : vecteur unitaire (repère local courant) vers où l'arbre penche ; inclinaison en degrés.
    dx, dy = direction
    p = Vector((x, y, z))
    rayons = (.34*grand, .27*grand, .2*grand, .14*grand)
    for k, part in enumerate((.25, .65, 1.0)):
        i = math.radians(inclinaison*part)
        pas = Vector((dx*math.sin(i), dy*math.sin(i), math.cos(i)))*taille/3
        tige(tuple(p), tuple(p+pas), rayons[k], "bois")
        p = p+pas
    # Racines du côté opposé : l'arbre tire sur le sol.
    for a in (-.6, 0, .6):
        rx = -dx*math.cos(a)+dy*math.sin(a)
        ry = -dy*math.cos(a)-dx*math.sin(a)
        tige((x, y, z+.25*grand), (x+rx*.9*grand, y+ry*.9*grand, z-.05), .09*grand, "bois")
    # Couronne : trois masses, la plus grosse en avant dans le sens du penchant.
    for avance, lat, dz, r in ((.25, 0, -.35, 1.25), (1.05, .35, -.55, 1.0), (-.25, -.45, -.15, .85)):
        g = grand*couronne
        cx = p.x+dx*avance*g-dy*lat*g
        cy = p.y+dy*avance*g+dx*lat*g
        base = p.z+dz*g
        pilier(cx, cy, base, r*.62*g, .5*g, teintes[0], r*g)
        pilier(cx, cy, base+.5*g, r*g, .95*g, teintes[1], r*.34*g)


# ------------------------------------------------------------------ 1. le chemin de halage

def chemin_de_halage():
    commencer("Chemin_de_halage")
    for i in range(6):
        j = i+1
        dedans = [point(k, interieurs[k]-LARGEUR_HALAGE, Z_HALAGE) for k in (i, j)]
        falaise = [point(k, interieurs[k]+.05, Z_HALAGE) for k in (i, j)]
        haut = [falaise[0], dedans[0], dedans[1], falaise[1]]
        bas = [(x, y, -2.6) for x, y, _ in haut]
        prisme(bas, haut, "pierre")
        # Bordure côté lagon, basse : on voit le vieux port par-dessus.
        a, b = Vector(dedans[0]), Vector(dedans[1])
        for t0 in (0.0, .5):
            q0 = a+(b-a)*(t0+.02)
            q1 = a+(b-a)*(t0+.48)
            n = Vector((-(q1-q0).y, (q1-q0).x, 0)).normalized()*.32
            # La normale vers la falaise : la bordure est posée juste à l'intérieur du bord.
            if n.dot(Vector(falaise[0])-a) < 0:
                n = -n
            prisme([tuple(q0), tuple(q1), tuple(q1+n), tuple(q0+n)],
                   [tuple(v+Vector((0, 0, .38))) for v in (q0, q1, q1+n, q0+n)], "creme")
    terminer(True)
    # Bornes d'amarrage, anneaux et touffes au pied de la falaise : décor sans collision.
    commencer("Halage_decor")
    for i in range(6):
        for t in (.3, .75):
            x, y, _ = bord_falaise(i, t, -LARGEUR_HALAGE+.55, Z_HALAGE)
            pilier(x, y, Z_HALAGE, .16, .42, "ardoise", .12)
            pilier(x, y, Z_HALAGE+.42, .2, .08, "ardoise")
        x, y, _ = bord_falaise(i, .52, .02, Z_HALAGE)
        boucle(x, y, Z_HALAGE+1.1, .18, .18, .035, "cuivre")
    terminer()


# ------------------------------------------------------------------ 2. l'écluse

def ecluse():
    # Le quai d'arrivée du halage, le long de l'avant-port, côté falaise.
    piece_ecluse("Quai_de_l_ecluse")
    boite(AVANT_PORT/2-.5, (EAU_B[1]+MUR_DOS[1])/2, -2.6, AVANT_PORT+1.0,
          MUR_DOS[1]-EAU_B[1], 2.6+Z_HALAGE, "pierre")
    # Jetée basse côté lagon de l'avant-port, pour fermer le bassin.
    boite(AVANT_PORT/2+.4, sum(MUR_FACE)/2, -2.6, AVANT_PORT-.8, MUR_FACE[1]-MUR_FACE[0], 2.6+.7, "pierre")
    terminer(True)

    # Murs des sas : côté lagon et côté falaise, en escalier. Fondations jusque sous l'eau.
    piece_ecluse("Murs_de_l_ecluse")
    for k in range(4):
        u0, u1 = debut_sas(k), debut_sas(k)+LONG_SAS
        haut = haut_sas(k)
        boite((u0+u1)/2, sum(MUR_FACE)/2, -3, u1-u0, MUR_FACE[1]-MUR_FACE[0], haut+3, "pierre")
        dos = haut if k < 3 else Z_JARDIN-.1
        boite((u0+u1)/2, sum(MUR_DOS)/2, -3, u1-u0, MUR_DOS[1]-MUR_DOS[0], dos+3, "pierre")
        # Chaperon clair et assises sombres sur la face visible depuis la ville.
        boite((u0+u1)/2, sum(MUR_FACE)/2, haut, u1-u0+.05, MUR_FACE[1]-MUR_FACE[0]+.12, .16, "creme")
        for z in [NIVEAUX[k]-1.2+.9*n for n in range(int((haut-NIVEAUX[k]+1.2)/.9))]:
            boite((u0+u1)/2, MUR_FACE[0]-.02, z, u1-u0, .05, .1, "strate")
        # Le fond du sas, visible quand l'eau est basse ; pas de collision (on ne reste pas coincé).
    # Les murs de tête, entre deux sas (la vanne coulisse dans leur rainure).
    for k in range(4):
        u = debut_sas(k)
        haut = haut_sas(k)
        for b0, b1 in ((MUR_FACE[0], EAU_B[0]), (EAU_B[1], MUR_DOS[1])):
            boite(u, (b0+b1)/2, -3, EPAISSEUR_VANNE, b1-b0, haut+3, "pierre")
    # Le mur d'amont du dernier sas, contre la falaise du jardin.
    u = debut_sas(3)+LONG_SAS
    boite(u, sum(EAU_B)/2, -3, EPAISSEUR_VANNE, EAU_B[1]-EAU_B[0], Z_JARDIN-.1+3, "pierre")
    terminer(True)

    piece_ecluse("Fonds_des_sas")
    for k in range(4):
        u0, u1 = debut_sas(k), debut_sas(k)+LONG_SAS
        boite((u0+u1)/2, sum(EAU_B)/2, NIVEAUX[k]-2.4, u1-u0, EAU_B[1]-EAU_B[0], .2, "sable")
        # Les échelles de service le long du mur côté lagon : décor.
        for n in range(int((haut_sas(k)-NIVEAUX[k]+2)/.35)):
            boite(u0+1.1, EAU_B[0]+.08, NIVEAUX[k]-2+n*.35, .5, .05, .05, "cuivre")
        for d in (-.25, .25):
            boite(u0+1.1+d, EAU_B[0]+.08, NIVEAUX[k]-2, .05, .05, haut_sas(k)-NIVEAUX[k]+2, "cuivre")
    terminer()

    # Les portiques des vannes : deux piliers, une poutre, deux poulies et des chaînes.
    piece_ecluse("Portiques_de_l_ecluse")
    for k in range(4):
        u = debut_sas(k)
        haut = haut_sas(k)
        # Assez hauts pour qu'une vanne levée (LEVEE_VANNE) laisse passer le robot debout sur le ponton.
        for b in (sum(MUR_FACE)/2, EAU_B[1]+.35):
            boite(u, b, haut, .55, .55, HAUT_PORTIQUE, "ardoise")
            boite(u, b, haut+HAUT_PORTIQUE, .7, .7, .14, "creme")
        boite(u, sum(EAU_B)/2, haut+HAUT_PORTIQUE-.15, .5, EAU_B[1]-EAU_B[0]+1.4, .38, "chene")
        for b in (EAU_B[0]+.8, EAU_B[1]-.8):
            cylindre(u-.26, b, haut+HAUT_PORTIQUE-.45, .32, .52, "cuivre", 10, axe="y")
            tige((u, b, haut+HAUT_PORTIQUE-.7), (u, b, haut+.4), .04, "ombre")
    terminer(True)

    # Les vannes-guillotines : une par mur de tête. Origine au milieu du bas de la vanne (Godot la lève).
    for k in range(4):
        u = debut_sas(k)
        bas = NIVEAUX[k]-2.5 if k > 0 else -1.9
        haut = NIVEAUX[k]+MONTEE+.35
        piece_ecluse(f"Vanne_sas_{k}")
        boite(u, sum(EAU_B)/2, bas, .26, EAU_B[1]-EAU_B[0]+.3, haut-bas, "bois")
        for z in [bas+.4+.9*n for n in range(int((haut-bas)/.9))]:
            boite(u, sum(EAU_B)/2, z, .3, EAU_B[1]-EAU_B[0]+.32, .12, "ardoise")
        boite(u, sum(EAU_B)/2, haut-.3, .32, EAU_B[1]-EAU_B[0]+.34, .3, "cuivre")
        obj = terminer(True)
        sur_pivot(obj, ecluse_monde(u, sum(EAU_B)/2, bas), ANGLE_ECLUSE)

    # L'eau des sas : origine à la surface, au niveau bas du sas (Godot la fait monter de MONTEE).
    for k in range(4):
        u0, u1 = debut_sas(k)+EPAISSEUR_VANNE/2, debut_sas(k)+LONG_SAS-EPAISSEUR_VANNE/2
        piece_ecluse(f"Eau_sas_{k+1}")
        boite((u0+u1)/2, sum(EAU_B)/2, NIVEAUX[k]-2.3, u1-u0, EAU_B[1]-EAU_B[0], 2.3, "eau_canal")
        obj = terminer()
        sur_pivot(obj, ecluse_monde((u0+u1)/2, sum(EAU_B)/2, NIVEAUX[k]), ANGLE_ECLUSE)

    # Le ponton flottant, au repos dans l'avant-port. Origine au centre du pont.
    global origine
    piece_ecluse("Ponton_ecluse")
    # Au repos, mer à 0 : le pont est au franc-bord. Repère local : z = 0 sur le pont.
    origine = (_A.x, _A.y, FRANC_BORD)
    cu, cb = AVANT_PORT/2-.2, sum(EAU_B)/2
    boite(cu, cb, -.55, 3.9, 3.5, .45, "bois")
    for du in (-1.6, 1.6):
        for db in (-1.4, 1.4):
            cylindre(cu+du, cb+db, -.75, .32, .5, "cuivre", 8)
    for n in range(8):
        boite(cu-1.82+n*.52, cb, -.1, .48, 3.55, .1, "sable" if n % 3 else "ocre")
    for du in (-1.75, 1.75):
        for db in (-1.55, 1.55):
            pilier(cu+du, cb+db, 0, .09, .5, "chene")
    for db in (-1.55, 1.55):
        boite(cu, cb+db, .45, 3.6, .08, .08, "chene")
    obj = terminer(True)
    sur_pivot(obj, ecluse_monde(cu, cb, FRANC_BORD), ANGLE_ECLUSE)

    # Le grand levier à crans, sur le ponton, côté vanne. Origine sur son axe (Godot le bascule).
    piece_ecluse("Levier_ecluse")
    lu, lb, lz = cu+1.45, cb+1.1, FRANC_BORD
    boite(lu, lb, lz, .5, .6, .55, "ardoise")
    # Le secteur à crans (fixe en vrai : il fait partie du socle ; ici collé au levier pour rester lisible).
    tige((lu, lb, lz+.55), (lu+.05, lb, lz+2.05), .075, "chene")
    boite(lu+.05, lb, lz+2.0, .16, .5, .14, "cuivre")
    obj = terminer()
    sur_pivot(obj, (*ecluse_monde(lu, lb)[:2], lz+.55), ANGLE_ECLUSE)
    piece_ecluse("Socle_du_levier")
    for n in range(5):
        a = math.radians(-35+n*17.5)
        boite(lu+math.sin(a)*.75, lb+.36, lz+.55+math.cos(a)*.75, .09, .06, .09, "or")
    boite(lu, lb+.36, lz+.5, .9, .05, .12, "cuivre")
    obj = terminer()
    sur_pivot(obj, (*ecluse_monde(lu, lb)[:2], lz+.55), ANGLE_ECLUSE)

    # Le flotteur dans son tube de verre, sur le quai, contre la vanne 0. Le verrou au-dessus.
    tu, tb = AVANT_PORT-.95, EAU_B[1]+.55
    piece_ecluse("Tube_du_flotteur")
    cylindre(tu, tb, Z_HALAGE, .42, .3, "pierre", 8, rayon2=.36)
    cylindre(tu, tb, Z_HALAGE+2.85, .36, .2, "pierre", 8)
    terminer(True)
    piece_ecluse("Verre_du_flotteur")
    cylindre(tu, tb, Z_HALAGE+.05, .26, 2.6, "vitrine", 10)
    for z in (Z_HALAGE, Z_HALAGE+1.3, Z_HALAGE+2.6):
        cylindre(tu, tb, z, .31, .1, "cuivre", 10)
    # Graduation : un trait doré au niveau de la marée haute, là où l'index touche le verrou.
    boite(tu, tb-.31, NIVEAUX[0]+INDEX_FLOTTEUR, .22, .03, .05, "or")
    terminer()
    piece_ecluse("Flotteur_ecluse")
    # Le flotteur est dans un puits sous le quai ; sa tige porte l'index doré qu'on voit dans le verre.
    cylindre(tu, tb, -.18, .2, .36, "or", 8, rayon2=.17)
    tige((tu, tb, .18), (tu, tb, INDEX_FLOTTEUR), .03, "cuivre")
    cylindre(tu, tb, INDEX_FLOTTEUR-.1, .16, .2, "or", 8)
    obj = terminer()
    sur_pivot(obj, (*ecluse_monde(tu, tb)[:2], 0.0), ANGLE_ECLUSE)
    piece_ecluse("Verrou_ecluse")
    vz = NIVEAUX[0]+INDEX_FLOTTEUR+.18
    boite(tu+.45, tb, vz-.06, 1.0, .14, .14, "cuivre")
    boite(tu+.92, tb, vz-.3, .14, .2, .5, "ardoise")
    obj = terminer()
    sur_pivot(obj, (*ecluse_monde(tu, tb)[:2], vz), ANGLE_ECLUSE)

    # La cloche-relais, à l'arrivée du halage : on l'entend de loin quand le carillon sonne.
    piece_ecluse("Cloche_relais")
    cu2, cb2 = -.1, .7
    boite(cu2, cb2, Z_HALAGE, .3, .3, 3.1, "chene")
    boite(cu2+.45, cb2, Z_HALAGE+3.0, 1.1, .22, .18, "chene")
    cylindre(cu2+.8, cb2, Z_HALAGE+2.25, .34, .55, "or", 10, rayon2=.16)
    tige((cu2+.8, cb2, Z_HALAGE+2.85), (cu2+.8, cb2, Z_HALAGE+3.0), .03, "cuivre")
    terminer(True)


# ------------------------------------------------------------------ 3. le jardin du haut

# Positions dans le jardin : (secteur, t, décalage depuis la falaise vers la terre).
LAMPE = (9, .55, 3.3)
PREMIER_ARBRE = (9, .18, 3.1)
ETABLI = (8, .3, 4.3)
PORTE_SERVICE = (8, .62)          # le long du mur, entre le secteur 8 et 9
BELVEDERE = (10, .42)
CITERNE = (10, .8, 3.6)


def position_lampe():
    return bord_falaise(LAMPE[0], LAMPE[1], LAMPE[2])


def jardin_du_haut():
    global origine, angle
    # Le massif du jardin : mis à niveau sur toute la bande côté lagon des secteurs 8 à 10.
    commencer("Jardin_du_haut_sol")
    for i in SECTEURS_JARDIN:
        j = i+1
        haut = [point(i, interieurs[i], Z_JARDIN), point(i, R_MUR, Z_JARDIN),
                point(j, R_MUR, Z_JARDIN), point(j, interieurs[j], Z_JARDIN)]
        prisme([(x, y, 7.6) for x, y, _ in haut], haut, "terre_claire")
    terminer(True)

    # Le haut mur sur la rue (enduit blanc côté jardin : la lampe y projette le souvenir).
    commencer("Mur_du_jardin")
    for i in SECTEURS_JARDIN:
        p = point(i, R_MUR+EPAISSEUR_MUR/2, 0)
        q = point(i+1, R_MUR+EPAISSEUR_MUR/2, 0)
        # La porte de service : 3,2 m de haut au-dessus du sol du jardin (le mur part de 3 m plus bas).
        trous = [(PORTE_SERVICE[1]-.12, PORTE_SERVICE[1]+.12, 3+3.2)] if i == PORTE_SERVICE[0] else []
        mur_droit(p, q, Z_JARDIN-3, Z_JARDIN+HAUT_MUR, EPAISSEUR_MUR, "enduit_blanc", trous)
    # Piliers aux angles : ils couvrent les jointures des pans (repère monde).
    origine, angle = (0, 0, 0), 0
    for k in (8, 9, 10, 11):
        x, y, _ = point(k, R_MUR+EPAISSEUR_MUR/2, 0)
        boite(x, y, Z_JARDIN-3, 1.15, 1.15, HAUT_MUR+3.35, "enduit_blanc")
        boite(x, y, Z_JARDIN+HAUT_MUR+.35, 1.35, 1.35, .2, "tuile")
    # Les murs de bout, de la falaise au mur de la rue.
    for k in (8, 11):
        mur_droit(point(k, interieurs[k]-.2, 0), point(k, R_MUR+EPAISSEUR_MUR, 0),
                  Z_JARDIN-3, Z_JARDIN+HAUT_MUR, EPAISSEUR_MUR, "enduit_blanc")
    terminer(True)
    # Le seuil de la porte de service, et deux marches qui descendent à la rue.
    commencer("Seuil_porte_jardin")
    sx, sy, _ = au_rayon(PORTE_SERVICE[0], PORTE_SERVICE[1], R_MUR+EPAISSEUR_MUR/2, 0)
    rue_x, rue_y, _ = au_rayon(PORTE_SERVICE[0], PORTE_SERVICE[1], R_MUR+EPAISSEUR_MUR+1.6, 0)
    z_rue = altitude(rue_x, rue_y) or Z_JARDIN-.6
    origine, angle = (sx, sy, 0), math.atan2(sy/.84, sx)-math.pi/2
    boite(0, 0, Z_JARDIN-3, 2.8, EPAISSEUR_MUR+.05, 3, "pierre")
    prisme([(-1.3, EPAISSEUR_MUR/2, z_rue-.3), (1.3, EPAISSEUR_MUR/2, z_rue-.3),
            (1.3, EPAISSEUR_MUR/2+1.5, z_rue-.3), (-1.3, EPAISSEUR_MUR/2+1.5, z_rue-.3)],
           [(-1.3, EPAISSEUR_MUR/2, Z_JARDIN), (1.3, EPAISSEUR_MUR/2, Z_JARDIN),
            (1.3, EPAISSEUR_MUR/2+1.5, z_rue+.02), (-1.3, EPAISSEUR_MUR/2+1.5, z_rue+.02)], "pierre")
    terminer(True)
    # Contreforts et soubassement côté rue (pierre) : le mur paraît plus vieux que la ville.
    commencer("Contreforts_du_jardin")
    for i in SECTEURS_JARDIN:
        for t in (.08, .5, .92):
            if i == PORTE_SERVICE[0] and abs(t-PORTE_SERVICE[1]) < .2:
                continue
            x, y, _ = au_rayon(i, t, R_MUR+EPAISSEUR_MUR+.35, 0)
            a = math.atan2(y/.84, x)
            origine, angle = (x, y, Z_JARDIN-2.5), a-math.pi/2
            prisme([(-.35, -.4, 0), (.35, -.4, 0), (.35, .55, 0), (-.35, .55, 0)],
                   [(-.3, -.4, 6.5), (.3, -.4, 6.5), (.3, -.35, 7.6), (-.3, -.35, 7.6)], "pierre")
            origine, angle = (0, 0, 0), 0
    terminer(True)

    # Le garde-corps au bord de la falaise, ouvert devant le dernier sas et le belvédère.
    commencer("Parapet_du_jardin")
    for i in SECTEURS_JARDIN:
        trous = []
        if i == 8:
            # Ouverture devant le sas du haut : de la fin du 3e sas au coin du secteur 9.
            t0 = max(0.0, min(1.0, (debut_sas(3)-17.0)/(LONGUEUR_ECLUSE-17.0)))
            trous.append((t0, 1.0, 1.0))
        if i == BELVEDERE[0]:
            trous.append((BELVEDERE[1]-.14, BELVEDERE[1]+.14, 1.0))
        p = bord_falaise(i, 0, .3)
        q = bord_falaise(i, 1, .3)
        mur_droit(p, q, Z_JARDIN, Z_JARDIN+1.0, .4, "pierre", trous, "creme")
    origine, angle = (0, 0, 0), 0
    for k in (9, 10):
        x, y, _ = bord_falaise(k, 0, .3)
        boite(x, y, Z_JARDIN, .6, .6, 1.15, "creme")
    terminer(True)

    lampe_mere()
    premier_arbre()
    etabli_des_jardiniers()
    belvedere()
    citerne_et_rigole()


def lampe_mere():
    # Grande lanterne des Semeurs, tournée vers le mur blanc. Socle à trappe (le cylindre musical),
    # prise au pied, mât, tête vitrée ; le disque de verre peint tourne dedans (Godot).
    global origine, angle
    x, y, z = position_lampe()
    vers_mur = math.atan2(y/.84, x)        # direction du mur (vers l'extérieur de l'anneau)
    commencer("Lampe_mere")
    origine, angle = (x, y, z), vers_mur-math.pi/2   # repère local : +y vers le mur
    cylindre(0, 0, 0, 1.05, .25, "pierre", 8, rayon2=1.0)
    cylindre(0, 0, .25, .85, 1.05, "craie", 8, rayon2=.78)
    cylindre(0, 0, 1.3, .92, .16, "creme", 8)
    # La trappe du mécanisme, côté jardin (tournée vers l'arrivée), et la prise du câble.
    boite(0, -.8, .45, .8, .08, .7, "cuivre")
    boite(0, -.86, .5, .62, .04, .58, "ombre")
    boite(.55, -.72, .28, .24, .1, .3, "cuivre")
    boite(.55, -.78, .35, .12, .02, .14, "ombre")
    # Le mât, cerclé de cuivre.
    cylindre(0, 0, 1.46, .3, 2.0, "ardoise", 8, rayon2=.22)
    for zz in (2.0, 2.8, 3.3):
        cylindre(0, 0, zz, .3, .1, "cuivre", 8)
    # La tête : cage de cuivre, verre, chapeau en cône, épi doré.
    cylindre(0, 0, 3.46, .95, .2, "cuivre", 10)
    for n in range(8):
        a = n*math.tau/8
        tige((.88*math.cos(a), .88*math.sin(a), 3.66), (.78*math.cos(a), .78*math.sin(a), 5.05), .05, "cuivre")
    cylindre(0, 0, 3.66, .84, 1.4, "vitrine", 10, rayon2=.74)
    cylindre(0, 0, 5.06, 1.05, .14, "cuivre", 10)
    cylindre(0, 0, 5.2, 1.0, .85, "toit_sauge", 10, rayon2=.12)
    cylindre(0, 0, 6.05, .09, .45, "or", 6, rayon2=.02)
    # L'objectif, tourné vers le mur : par là sortent les silhouettes.
    cylindre(0, .7, 4.35, .34, .55, "cuivre", 10, axe="y", rayon2=.28)
    terminer(True)
    # Le cœur de la lampe (luit dans Godot) et le disque de verre peint (tourne dans Godot).
    commencer("Coeur_lampe_mere")
    origine, angle = (x, y, z), vers_mur-math.pi/2
    cylindre(0, -.1, 3.8, .28, .95, "or", 8, rayon2=.18)
    obj = terminer()
    sur_pivot(obj, (x, y, z+4.25), vers_mur-math.pi/2)
    commencer("Disque_lampe_mere")
    origine, angle = (x, y, z), vers_mur-math.pi/2
    teintes = ("rose", "or", "ardoise", "corail", "creme", "rose", "or", "sauge")
    for n in range(8):
        a0, a1 = n*math.tau/8, (n+1)*math.tau/8
        morceau([(0, .3, 4.35), (.55*math.cos(a0), .3, 4.35+.55*math.sin(a0)),
                 (.55*math.cos(a1), .3, 4.35+.55*math.sin(a1))], [(0, 1, 2), (2, 1, 0)], teintes[n])
    obj = terminer()
    sur_pivot(obj, (*_local_vers_monde((x, y), vers_mur-math.pi/2, 0, .3), z+4.35), vers_mur-math.pi/2)
    commencer("Cylindre_musique")
    origine, angle = (x, y, z), vers_mur-math.pi/2
    cylindre(-.25, -.72, .8, .17, .5, "or", 10, axe="z")
    for n in range(10):
        a = n*math.tau/10
        boite(-.25+.18*math.cos(a), -.72+.18*math.sin(a), .85+(n % 4)*.1, .04, .04, .04, "cuivre")
    obj = terminer()
    sur_pivot(obj, (*_local_vers_monde((x, y), vers_mur-math.pi/2, -.25, -.72), z+.8), vers_mur-math.pi/2)
    origine, angle = (0, 0, 0), 0


def _local_vers_monde(centre, rotation, a, b):
    c, s = math.cos(rotation), math.sin(rotation)
    return (centre[0]+a*c-b*s, centre[1]+a*s+b*c)


def premier_arbre():
    # Le premier arbre rose : le plus vieux et le plus grand de l'île, à côté de la lampe.
    commencer("Premier_arbre_rose")
    x, y, z = bord_falaise(*PREMIER_ARBRE)
    lx, ly, _ = position_lampe()
    d = Vector((lx-x, ly-y)).normalized()
    # Muret circulaire autour du pied.
    for n in range(12):
        a = n*math.tau/12
        boite(x+1.35*math.cos(a), y+1.35*math.sin(a), z, .75, .75, .45, "pierre")
    cylindre(x, y, z, 1.25, .38, "terreau", 12)
    arbre_penche(x, y, z+.35, 4.4, (d.x, d.y), 10, ("corail", "rose"), grand=1.55)
    terminer(True)


def etabli_des_jardiniers():
    # Établi, arrosoirs, bêche, sécateurs, pots et étiquettes de plants (au nom de leur planète).
    global origine, angle
    x, y, z = bord_falaise(*ETABLI)
    commencer("Etabli_des_jardiniers")
    origine, angle = (x, y, z), math.atan2(y/.84, x)-math.pi/2
    boite(0, 0, 0, 2.6, 1.0, 1.05, "chene")
    boite(0, 0, 1.05, 2.8, 1.1, .1, "bois")
    boite(0, .1, .25, 2.4, .9, .06, "bois")
    # Pots retournés, sécateurs, carnet de culture ouvert.
    for n in range(3):
        cylindre(-.9+n*.3, -.1, 1.15, .13, .2, "tuile", 8, rayon2=.17)
    tige((.3, -.2, 1.17), (.62, -.05, 1.17), .025, "ardoise")
    tige((.3, -.05, 1.17), (.62, -.2, 1.17), .025, "ardoise")
    boite(.95, .05, 1.15, .5, .36, .03, "creme")
    boite(.95, .05, 1.18, .02, .36, .01, "ombre")
    terminer(True)
    commencer("Outils_des_jardiniers")
    origine, angle = (x, y, z), math.atan2(y/.84, x)-math.pi/2
    # Deux arrosoirs de cuivre.
    for ax, ay in ((-1.8, -.8), (-1.5, -1.3)):
        cylindre(ax, ay, 0, .28, .55, "cuivre", 10, rayon2=.24)
        tige((ax+.22, ay, .2), (ax+.75, ay, .62), .04, "cuivre")
        tige((ax-.2, ay, .5), (ax-.2, ay, .75), .03, "cuivre")
    # Bêche contre l'établi.
    tige((1.6, .35, 0), (1.5, .5, 1.55), .04, "chene")
    boite(1.62, .33, 0, .3, .05, .4, "ardoise")
    # Un carré de plants et ses étiquettes piquées.
    for n in range(5):
        tige((-1+n*.5, -1.7, 0), (-1+n*.5, -1.7, .45), .02, "bois")
        boite(-1+n*.5, -1.72, .4, .22, .02, .13, "creme")
    boite(0, -1.7, 0, 2.8, .9, .12, "terreau")
    terminer()
    origine, angle = (0, 0, 0), 0


def belvedere():
    # Balcon en encorbellement sur le lagon : on voit le vieux port d'en haut (prépare G4).
    global origine, angle
    i, t = BELVEDERE
    p = Vector(bord_falaise(i, 0, 0)[:2])
    q = Vector(bord_falaise(i, 1, 0)[:2])
    m = p+(q-p)*t
    tangente = (q-p).normalized()
    commencer("Belvedere")
    origine, angle = (m.x, m.y, Z_JARDIN), math.atan2(tangente.y, tangente.x)
    # Repère local : x le long de la falaise, -y vers le lagon (vérifié : le centre du lagon est en -y).
    sens = -1 if Vector((-tangente.y, tangente.x)).dot(-m) < 0 else 1
    boite(0, sens*1.3, -.35, 4.6, 2.9, .35, "pierre")
    for x in (-1.8, 0, 1.8):
        prisme([(x-.25, sens*.1, -.35), (x+.25, sens*.1, -.35), (x+.25, sens*2.4, -.35), (x-.25, sens*2.4, -.35)],
               [(x-.2, sens*.1, -2.2), (x+.2, sens*.1, -2.2), (x+.2, sens*.4, -2.2), (x-.2, sens*.4, -2.2)], "pierre")
    # Balustrade (sans le côté de la falaise).
    for x in [-2.2+n*.55 for n in range(9)]:
        pilier(x, sens*2.6, 0, .07, .95, "creme")
    for y in [sens*(.3+n*.55) for n in range(5)]:
        for x in (-2.2, 2.2):
            pilier(x, y, 0, .07, .95, "creme")
    boite(0, sens*2.6, .95, 4.6, .16, .1, "creme")
    for x in (-2.2, 2.2):
        boite(x, sens*1.45, .95, .16, 2.4, .1, "creme")
    # Banc de pierre, où Aube a laissé son dessin.
    boite(0, sens*.75, 0, 2.2, .55, .5, "pierre")
    boite(0, sens*.75, .5, 2.4, .65, .1, "creme")
    terminer(True)
    origine, angle = (0, 0, 0), 0
    return (m.x, m.y, sens)


def citerne_et_rigole():
    # La citerne de pluie : grande cuve de pierre sur la crête, visible de toute la ville. Son
    # déversoir tombe dans la rigole qui longe la falaise jusqu'au dernier sas.
    global origine, angle
    x, y, z = bord_falaise(*CITERNE)
    commencer("Citerne_de_pluie")
    cylindre(x, y, z, 2.55, 6.2, "pierre", 12, rayon2=2.4)
    cylindre(x, y, z+6.2, 2.65, .3, "creme", 12)
    for n in range(6):
        a = n*math.tau/6+.26
        cx, cy = x+2.55*math.cos(a), y+2.55*math.sin(a)
        boite(cx, cy, z, .5, .5, 5.2, "pierre")
    for zz in (1.6, 3.4, 5.0):
        cylindre(x, y, z+zz, 2.5, .1, "strate", 12)
    # Le bec du déversoir, vers la rigole (côté falaise).
    rx, ry, _ = bord_falaise(CITERNE[0], CITERNE[1], .78)
    d = Vector((rx-x, ry-y)).normalized()
    tige((x+d.x*2.3, y+d.y*2.3, z+5.6), (x+d.x*3.1, y+d.y*3.1, z+5.3), .2, "cuivre")
    terminer(True)
    commencer("Eau_citerne")
    cylindre(x, y, z+6.0, 2.35, .12, "eau_canal", 12)
    # La chute d'eau du déversoir.
    tige((x+d.x*3.15, y+d.y*3.15, z+5.25), (rx, ry, z+.2), .13, "eau_canal")
    terminer()

    # La rigole : du pied de la citerne au coin du secteur 9, puis le bec qui verse dans le sas du haut.
    trace = [bord_falaise(10, t, .78) for t in (CITERNE[1], .6, .3, 0)]
    trace += [bord_falaise(9, t, .78) for t in (.7, .35, 0)]
    commencer("Rigole")
    for a, b in zip(trace, trace[1:]):
        av, bv = Vector(a[:2]), Vector(b[:2])
        n = (bv-av).normalized()
        n = Vector((-n.y, n.x))*.32
        for cote in (-1, 1):
            o = n*cote
            prisme([(av.x+o.x, av.y+o.y, Z_JARDIN-.1), (bv.x+o.x, bv.y+o.y, Z_JARDIN-.1),
                    (bv.x+o.x*.7, bv.y+o.y*.7, Z_JARDIN-.1), (av.x+o.x*.7, av.y+o.y*.7, Z_JARDIN-.1)],
                   [(av.x+o.x, av.y+o.y, Z_JARDIN+.22), (bv.x+o.x, bv.y+o.y, Z_JARDIN+.22),
                    (bv.x+o.x*.7, bv.y+o.y*.7, Z_JARDIN+.22), (av.x+o.x*.7, av.y+o.y*.7, Z_JARDIN+.22)],
                   "pierre")
    # Le bec qui verse dans le dernier sas, par-dessus son mur d'amont.
    u = debut_sas(3)+LONG_SAS
    bx, by, _ = ecluse_monde(u-.6, sum(EAU_B)/2)
    tige(trace[-1], (bx, by, Z_JARDIN-.2), .22, "cuivre")
    terminer()
    commencer("Eau_rigole")
    for a, b in zip(trace, trace[1:]):
        av, bv = Vector(a[:2]), Vector(b[:2])
        n = (bv-av).normalized()
        n = Vector((-n.y, n.x))*.2
        morceau([(av.x-n.x, av.y-n.y, Z_JARDIN+.08), (bv.x-n.x, bv.y-n.y, Z_JARDIN+.08),
                 (bv.x+n.x, bv.y+n.y, Z_JARDIN+.08), (av.x+n.x, av.y+n.y, Z_JARDIN+.08)],
                [(0, 1, 2, 3)], "eau_canal")
    terminer()


# ------------------------------------------------------------------ 4. les serres basses

ARBRES_DES_SERRES = {8: ((-2.6, .9, 3.2), (2.4, -.2, 3.0)),
                     9: ((-3.2, .4, 3.1), (0.2, 1.1, 3.4), (3.4, .3, 3.0)),
                     10: ((-2.4, -.1, 3.1), (2.5, .9, 3.3))}
INCLINAISON_SERRES = 48


def serre_basse(i, centre, rotation):
    # Une verrière ouverte sur la rue (porte de 3 m), au sol de terre ; ses arbres roses penchent
    # fortement vers la lampe-mère, derrière le mur du jardin. Repère local : +y = vers l'extérieur.
    global origine, angle
    lx, ly, _ = position_lampe()
    commencer("Verriere_%02d" % i)
    origine, angle = centre, rotation
    boite(0, 0, -1, 11, 7, 1.5, "pierre")
    # Parois de verre (avec collision) : la porte au milieu de la face sur la rue.
    for x0, x1 in ((-5.4, -1.5), (1.5, 5.4)):
        boite((x0+x1)/2, -3.4, .5, x1-x0, .1, 3.7, "vitrine")
    boite(0, -3.4, 3.6, 3.0, .1, .6, "vitrine")
    boite(0, 3.4, .5, 10.8, .1, 3.7, "vitrine")
    for x in (-5.4, 5.4):
        boite(x, 0, .5, .1, 6.8, 3.7, "vitrine")
    # Le toit, travée par travée : côté rue (-y), la plupart des vitres sont tombées (on voit les arbres).
    cadres = (-5.5, -3.3, -1.5, 1.5, 3.3, 5.5)
    for n, (x0, x1) in enumerate(zip(cadres, cadres[1:])):
        for cote in (-1, 1):
            if cote == -1 and (n+i) % 5 != 0:
                continue
            morceau([(x0, cote*3.5, 4.2), (x1, cote*3.5, 4.2), (x1, 0, 6.2), (x0, 0, 6.2)],
                     [(0, 1, 2, 3), (3, 2, 1, 0)], "vitrine")
    # Les pignons vitrés.
    for x in (-5.5, 5.5):
        morceau([(x, -3.5, 4.2), (x, 3.5, 4.2), (x, 0, 6.2)], [(0, 1, 2), (2, 1, 0)], "vitrine")
    for x in cadres:
        for y in (-3.45, 3.45):
            boite(x, y, .5, .17, .2, 3.8, "ardoise")
        toit(x, 0, 4.25, .19, 7.15, 2, "ardoise")
    boite(0, -3.45, 3.55, 3.2, .22, .16, "ardoise")
    # Seuil : une marche douce de la rue au sol de la serre.
    prisme([(-1.5, -4.6, -.2), (1.5, -4.6, -.2), (1.5, -3.3, -.2), (-1.5, -3.3, -.2)],
           [(-1.5, -4.6, .1), (1.5, -4.6, .1), (1.5, -3.3, .5), (-1.5, -3.3, .5)], "pierre")
    terminer(True)
    # L'intérieur : allée, plates-bandes de terreau et les arbres penchés (décor, sans collision
    # pour les arbres : ils ne bloquent pas l'allée).
    commencer("Serre_interieur_%02d" % i)
    origine, angle = centre, rotation
    boite(0, -.2, .5, 1.6, 6.4, .04, "pave_use")
    for x0, x1 in ((-5.1, -1.0), (1.0, 5.1)):
        boite((x0+x1)/2, .5, .5, x1-x0, 5.4, .18, "terreau")
    c, s = math.cos(rotation), math.sin(rotation)
    for ax, ay, taille in ARBRES_DES_SERRES[i]:
        wx, wy = centre[0]+ax*c-ay*s, centre[1]+ax*s+ay*c
        d = Vector((lx-wx, ly-wy)).normalized()
        # La direction dans le repère local de la serre.
        dl = (d.x*c+d.y*s, -d.x*s+d.y*c)
        # Un anneau de pierre claire marque le pied : vu de dessus, la couronne est nettement à côté.
        for n in range(8):
            a = n*math.tau/8
            boite(ax+.75*math.cos(a), ay+.75*math.sin(a), .68, .42, .42, .16, "creme")
        arbre_penche(ax, ay, .68, taille, dl, INCLINAISON_SERRES, ("corail", "rose"), 1.15, .64)
    # Quelques pots et un banc de rempotage.
    for x, y in ((-4.6, -2.6), (4.5, -2.5), (4.7, 2.9)):
        cylindre(x, y, .5, .22, .35, "tuile", 8, rayon2=.28)
    terminer()
    origine, angle = (0, 0, 0), 0


# ------------------------------------------------------------------ plaque du carillon, repères

def plaque_du_carillon():
    # « Quand il chante, l'eau ouvre le chemin des serres. » : plaque gravée entre les montants
    # du portique du carillon (le texte est une page_lisible dans Godot).
    global origine, angle
    commencer("Plaque_du_carillon")
    origine, angle = (-8, -34, 1.1), 0
    boite(1.325, -.2, 1.05, .95, .06, .6, "cuivre")
    boite(1.325, -.235, 1.12, .8, .02, .46, "or")
    for k in range(3):
        boite(1.325, -.25, 1.22+k*.12, .6-k*.1, .01, .03, "ombre")
    terminer()
    origine, angle = (0, 0, 0), 0


def reperes_jardin(belvedere_info):
    # Coordonnées Godot (x, y = hauteur, z = -y Blender) pour câbler la scène G3.
    reperes = []
    reperes.append(("angle_ecluse", ANGLE_ECLUSE, 0, 0))
    for k in range(4):
        reperes.append((f"vanne_{k}", *ecluse_monde(debut_sas(k), sum(EAU_B)/2, 0)))
        u = debut_sas(k)+LONG_SAS/2
        reperes.append((f"sas_{k+1}_centre", *ecluse_monde(u, sum(EAU_B)/2, NIVEAUX[k])))
    reperes.append(("ponton_repos", *ecluse_monde(AVANT_PORT/2-.2, sum(EAU_B)/2, 0)))
    reperes.append(("arrivee_jardin", *ecluse_monde(debut_sas(3)+LONG_SAS/2, MUR_DOS[1]+.6, Z_JARDIN)))
    reperes.append(("flotteur", *ecluse_monde(AVANT_PORT-.95, EAU_B[1]+.55, 0)))
    reperes.append(("cloche_relais", *ecluse_monde(.7, .7, Z_HALAGE+2.4)))
    reperes.append(("levier", *ecluse_monde(AVANT_PORT/2+1.25, sum(EAU_B)/2+1.1, FRANC_BORD)))
    x, y, z = position_lampe()
    reperes.append(("lampe_mere", x, y, z))
    reperes.append(("lampe_prise", *bord_falaise(LAMPE[0], LAMPE[1], LAMPE[2]-.8)[:2], z+.35))
    reperes.append(("mur_projection", *au_rayon(LAMPE[0], LAMPE[1], R_MUR-.02, Z_JARDIN+3.2)))
    reperes.append(("premier_arbre", *bord_falaise(*PREMIER_ARBRE)))
    reperes.append(("porte_service", *au_rayon(PORTE_SERVICE[0], PORTE_SERVICE[1], R_MUR+EPAISSEUR_MUR/2, Z_JARDIN)))
    reperes.append(("belvedere", belvedere_info[0], belvedere_info[1], Z_JARDIN))
    reperes.append(("etabli", *bord_falaise(*ETABLI)))
    reperes.append(("plaque_carillon", -8+1.325, -34-.27, 1.1+1.35))
    with open(racine/"tools/blender/sources/jardin_du_haut_reperes.txt", "w", encoding="utf-8") as f:
        f.write("# Repères G3, coordonnées Godot : x, y (hauteur), z\n")
        f.write(f"# niveaux bas des sas : {NIVEAUX} ; montée {MONTEE} ; franc-bord du ponton {FRANC_BORD}\n")
        for nom, x, y, z in reperes:
            f.write(f"{nom}\t{x:.3f}\t{z:.3f}\t{-y:.3f}\n")


# La friche ne pousse pas dans le jardin.
_hors_friche_ville_haute = hors_friche


def hors_friche(i, t, r, marge=.45):
    if i in SECTEURS_JARDIN and r < R_MUR+EPAISSEUR_MUR+marge:
        return True
    return _hors_friche_ville_haute(i, t, r, marge)


def construire_jardin_du_haut():
    avant = set(bpy.data.objects)
    chemin_de_halage()
    ecluse()
    jardin_du_haut()
    plaque_du_carillon()
    info = belvedere_info_calcul()
    for obj in set(bpy.data.objects)-avant:
        normales(obj)
    reperes_jardin(info)


def belvedere_info_calcul():
    i, t = BELVEDERE
    p = Vector(bord_falaise(i, 0, 0)[:2])
    q = Vector(bord_falaise(i, 1, 0)[:2])
    m = p+(q-p)*t
    return (m.x, m.y)
