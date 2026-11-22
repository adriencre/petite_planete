"""Construit la Colonie en quartiers éditables et exporte son décor pour Godot."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri

racine = Path(__file__).resolve().parents[2]
dossier = racine / "concept/ile_03"
bpy.ops.wm.read_factory_settings(use_empty=True)
hasard = random.Random(314)
palette = {
    "craie": "F9D6A7", "ocre": "EAA875", "peche": "F5B596", "pierre": "C58678",
    "strate": "A96F71", "sable": "EFD2A0", "sauge": "ACC695", "bois": "976E61",
    "ardoise": "547C87", "tuile": "CA7868", "cuivre": "AB7862", "creme": "FFF0C6",
    "ombre": "415F68", "verre": "A3DFD8", "or": "FFCB6D", "rose": "F5AEBB",
    "corail": "DE909E", "ecume": "A6E2D6", "mer": "67BCBA",
    "miel": "D99F5E", "saumon": "E5A18B", "chene": "BC8460",
    "toit_sauge": "93AC92", "vitre_fumee": "739895",
    "herbe_sombre": "738D68", "herbe_tendre": "B6C77C", "herbe_olive": "96AA68",
    "herbe_seche": "D7BF7A", "mousse": "A7B67E", "mousse_sombre": "8D9E73",
    "terre_claire": "DBBB8F", "pave_use": "DBC2A1", "fissure": "A2916F",
    "feuille": "9FBF87", "feuille_ombre": "779775",
}
materiaux = {}
for nom, hexa in palette.items():
    mat = bpy.data.materials.new(nom)
    couleur = [((int(hexa[i:i+2], 16)/255 + .055)/1.055)**2.4 for i in (0, 2, 4)]
    mat.diffuse_color = (*couleur, 1)
    mat.use_nodes = True
    surface = next(noeud for noeud in mat.node_tree.nodes if noeud.type == "BSDF_PRINCIPLED")
    surface.inputs["Base Color"].default_value = (*couleur, 1)
    surface.inputs["Roughness"].default_value = .78
    materiaux[nom] = mat

# Verre des vitrines : translucide pour laisser voir l'étalage depuis la rue.
vitrine_verre = materiaux["verre"].copy()
vitrine_verre.name = "vitrine"
surface = next(n for n in vitrine_verre.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
surface.inputs["Alpha"].default_value = .28
surface.inputs["Roughness"].default_value = .15
vitrine_verre.surface_render_method = "BLENDED"
materiaux["vitrine"] = vitrine_verre

# Un maillage par élément architectural ou portion de rue, avec matériaux par face.
def commencer(nom):
    global sommets, faces, teintes, origine, angle, element
    sommets, faces, teintes = [], [], []
    origine, angle, element = (0, 0, 0), 0, nom

def morceau(points, polygones, couleur):
    base = len(sommets)
    x, y, z = origine
    c, s = math.cos(angle), math.sin(angle)
    sommets.extend((x+a*c-b*s, y+a*s+b*c, z+h) for a,b,h in points)
    for face in polygones:
        faces.append(tuple(base+i for i in face))
        teintes.append(couleur)

def terminer(collision=False):
    # True : maillage + collision ; "-colonly" : collision seule (rampes sous les marches).
    nom = element + (collision if isinstance(collision, str) else "-col" if collision else "")
    mesh = bpy.data.meshes.new(nom)
    mesh.from_pydata(sommets, [], faces)
    obj = bpy.data.objects.new(nom, mesh)
    bpy.context.collection.objects.link(obj)
    noms = list(dict.fromkeys(teintes))
    for cle in noms:
        mesh.materials.append(materiaux[cle])
    for face, cle in zip(mesh.polygons, teintes):
        face.material_index = noms.index(cle)
    return obj

def prisme(bas, haut, couleur):
    n = len(bas)
    morceau(bas+haut, [tuple(reversed(range(n))), tuple(range(n, 2*n))]+
            [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)], couleur)

def boite(x,y,z,l,p,h,couleur):
    base = [(x+a*l/2,y+b*p/2,z) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    prisme(base, [(a,b,d+h) for a,b,d in base], couleur)

def pilier(x,y,z,r,h,couleur,r2=None):
    r2 = r if r2 is None else r2
    cercle = [(math.cos(i*math.tau/8),math.sin(i*math.tau/8)) for i in range(8)]
    prisme([(x+r*a,y+r*b,z) for a,b in cercle],[(x+r2*a,y+r2*b,z+h) for a,b in cercle],couleur)

def toit(x,y,z,l,p,h,couleur):
    pts=[(x+a*l/2,y+b*p/2,z) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    morceau(pts+[(x-l/2,y,z+h),(x+l/2,y,z+h)],[(3,2,1,0),(0,1,5,4),(5,2,3,4),(3,0,4),(1,2,5)],couleur)

def arbre(x, y, z, taille, teintes):
    pilier(x,y,z,.31,taille,"bois",.16)
    for dx,dy,dz,r in [(0,0,0,1.75), (.78,.32,.43,1.37), (-.7,-.2,.62,1.2)]:
        base = z + taille + dz - .86
        pilier(x+dx,y+dy,base,r*.66,.58,teintes[0],r)
        pilier(x+dx,y+dy,base+.58,r,1.08,teintes[1],r*.36)


def lumineux(x,y,z):
    pilier(x,y,z,.21,3.3,"ombre")
    pilier(x,y,z+3.3,.48,.85,"or",.39)
    pilier(x,y,z+4.15,.52,.28,"ardoise",.17)

def maison(nom,centre,rotation,l,p,h,ton,toiture,etage=False):
    global origine,angle
    commencer(nom)
    origine,angle=centre,rotation
    boite(0,0,-1.9,l+.35,p+.35,2.15,"pierre")
    boite(0,0,.25,l,p,h,ton)
    boite(0,0,h+.15,l+.28,p+.28,.27,"creme")
    toit(0,0,h+.42,l+.95,p+.9,2.1,toiture)
    boite(l*.29,p*.2,h+1,.7,.8,2,"ocre")
    boite(l*.29,p*.2,h+3,.9,1,.24,"creme")
    boite(0,-p/2,.26,1.65,.24,3,"ombre")
    boite(0,-p/2-.18,3.28,2.25,.76,.18,toiture)
    for cote in [-1,1]:
        x=cote*l*.32
        for z in ([1.65,4.6] if etage else [1.65]):
            boite(x,-p/2,z,1.06,.19,1.38,"ombre")
            boite(x,-p/2-.13,z+.16,.77,.08,1.06,"verre")
            boite(x,-p/2-.13,z-.12,1.45,.46,.16,"creme")
            boite(x-.72,-p/2-.1,z,.27,.14,1.32,toiture)
    terminer(True)

def bloc_chanfreine(l, p, z, h, chanfrein, couleur):
    x, y = l/2, p/2
    c = chanfrein
    contour = [(-x+c,-y), (x-c,-y), (x,-y+c), (x,y-c),
               (x-c,y), (-x+c,y), (-x,y-c), (-x,-y+c)]
    prisme([(a,b,z) for a,b in contour], [(a,b,z+h) for a,b in contour], couleur)

def extrusion_facade(profil, avant, arriere, couleur):
    # Le profil est parcouru dans le sens antihoraire vu depuis la rue.
    n = len(profil)
    points = [(x,y,z) for y in (avant, arriere) for x,z in profil]
    cotes = [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    morceau(points, [tuple(range(n)), tuple(reversed(range(n,2*n)))] + cotes, couleur)

def portail(x, y, couleur):
    # Le vantail se loge sous un linteau polygonal, avec joint et poignée en cuivre.
    cadre = [(-.98,.24), (.98,.24), (.98,2.56), (.58,3.17),
             (-.58,3.17), (-.98,2.56)]
    panneau = [(-.76,.28), (.76,.28), (.76,2.51), (.44,2.97),
               (-.44,2.97), (-.76,2.51)]
    extrusion_facade([(x+a,z) for a,z in cadre], y-.19, y+.04, "creme")
    extrusion_facade([(x+a,z) for a,z in panneau], y-.235, y-.18, couleur)
    boite(x,y-.246,.29,.035,.04,2.67,"bois")
    boite(x+.27,y-.30,1.53,.23,.14,.075,"or")
    boite(x,y-.15,.12,2.03,.58,.16,"sable")

def fenetre(x, y, z, largeur, volet, obturee=False):
    for cote in (-1,1):
        boite(x+cote*(largeur/2-.055),y-.105,z,.11,.25,1.15,"creme")
    for hauteur in (z,z+1.04):
        boite(x,y-.105,hauteur,largeur-.22,.25,.11,"creme")
    boite(x,y-.072,z+.11,largeur-.22,.07,.93,"chene" if obturee else "vitre_fumee")
    boite(x,y-.116,z+.11,.07,.05,.93,"bois")
    for signe in (-1,1):
        boite(x+signe*(largeur/2+.12),y-.14,z+.04,.24,.15,1.06,volet)
    boite(x,y-.13,z-.12,largeur+.2,.38,.12,"sable")

def maison_fermee(nom, centre, rotation, architecture):
    largeur, profondeur, h, mur, couverture, volet, forme = architecture
    global angle
    collection = bpy.data.collections.new(nom)
    bpy.context.scene.collection.children.link(collection)
    facade = -profondeur/2

    def placer(objet):
        objet.location = centre
        objet.rotation_euler.z = rotation

    if forme in modeles_fermes:
        modele = modeles_fermes[forme]
        for piece in modele.objects:
            suffixe = piece.name.removeprefix(modele.name)
            objet = bpy.data.objects.new(nom + suffixe, piece.data)
            collection.objects.link(objet)
            placer(objet)
        return

    modeles_fermes[forme] = collection

    def poser(collision=False):
        objet = terminer(collision)
        bpy.context.collection.objects.unlink(objet)
        collection.objects.link(objet)
        placer(objet)

    commencer(nom + "_socle")
    bloc_chanfreine(largeur+.28, profondeur+.26, -1.9, 2.15, .32, "pierre")
    poser(True)

    commencer(nom + "_murs")
    bloc_chanfreine(largeur, profondeur, .25, h-.25, .36, mur)
    poser(True)

    commencer(nom + "_toiture")
    bloc_chanfreine(largeur+.27, profondeur+.24, h-.18, .23, .34, "creme")
    if forme == "terrasse":
        bloc_chanfreine(largeur+.41, profondeur+.38, h+.05, .25, .37, couverture)
        for cote in (-1,1):
            boite(cote*(largeur/2-.09),0,h+.3,.20,profondeur-.58,.62,mur)
        boite(0,-profondeur/2+.19,h+.3,largeur+.02,.20,.62,mur)
        boite(0,profondeur/2-.19,h+.3,largeur+.02,.20,.62,mur)
        boite(largeur*.23,profondeur*.18,h+.3,1.12,1.05,1.15,"ocre")
        boite(largeur*.23,profondeur*.18,h+1.45,1.32,1.25,.16,couverture)
    else:
        demi = largeur/2+.26
        crete = h + (1.8 if forme == "pignon" else 1.36)
        profil = [(-demi,h+.04), (demi,h+.04), (demi,h+.34),
                  (demi*.63,h+.86), (.25,crete), (-.22,crete),
                  (-demi*.63,h+.86), (-demi,h+.34)]
        extrusion_facade(profil, facade-.27, -facade+.27, couverture)
        for y in (facade-.22, 0, -facade+.22):
            liseret = [(x*1.013, z+.02 if z > h+.04 else z-.06) for x,z in profil]
            extrusion_facade(liseret, y-.045, y+.045, "creme" if y else couverture)
        boite(largeur*.32,profondeur*.18,h+.58,.62,.61,1.08,"ocre")
        boite(largeur*.32,profondeur*.18,h+1.66,.81,.8,.16,"creme")
    poser()

    commencer(nom + "_menuiseries")
    x_porte = -.89 if forme in ("pignon","balcon") else 0
    portail(x_porte, facade, volet)
    if x_porte:
        fenetre(1.13,facade,1.47,1.2,volet)
    else:
        for x in (-1.64,1.64):
            fenetre(x,facade,1.59,.75,volet,forme=="contreforts")
    poser()

    commencer(nom + "_fenetre_arriere")
    angle = math.pi
    fenetre(0,facade,1.78,1.28,volet,forme=="contreforts")
    poser()

    if forme in ("balcon","contreforts"):
        commencer(nom + "_etage")
        if forme == "balcon":
            z = 3.57
            boite(0,facade-.42,z,3.9,1.11,.25,"sable")
            for x in (-1.62,1.62):
                bas = [(x-.16,facade-.10,z-.58),(x+.16,facade-.10,z-.58),
                       (x+.16,facade+.04,z-.58),(x-.16,facade+.04,z-.58)]
                prisme(bas, [(a,facade-.76 if b<facade else b,z) for a,b,_ in bas], "ocre")
            for x in (-1.78,-.89,0,.89,1.78):
                boite(x,facade-.89,z+.25,.09,.09,.86,"chene")
            boite(0,facade-.89,z+1.08,3.73,.13,.1,"chene")
            for x in (-1.78,1.78):
                boite(x,facade-.4125,z+1.08,.13,.825,.1,"chene")
            fenetre(0,facade,z+.27,1.45,volet)
        else:
            for x in (-2.18,2.18):
                bas = [(x-.21,facade-.36,.24),(x+.21,facade-.36,.24),
                       (x+.21,facade+.03,.24),(x-.21,facade+.03,.24)]
                prisme(bas, [(a,b+.25 if b<facade else b,4.95) for a,b,_ in bas], "ocre")
            for x in (-.91,.91):
                fenetre(x,facade,4.16,.97,volet,True)
        poser()

def panneau_rampant(x1,z1,x2,z2,avant,arriere,epaisseur,ton):
    extrusion_facade([(x1,z1-epaisseur),(x2,z2-epaisseur),(x2,z2),(x1,z1)],
                     avant,arriere,ton)

def couverture_du_quai():
    # Les nervures suivent la coque cintrée du toit jusqu'aux rives en cuivre.
    coque = [(-3.88,3.60),(-3.52,4.24),(-2.68,4.93),(-1.45,5.42),
             (0,5.60),(1.45,5.42),(2.68,4.93),(3.52,4.24),(3.88,3.60)]
    extrusion_facade([(-3.88,3.43),(3.88,3.43)]+list(reversed(coque)),
                     -3.06,3.09,"toit_sauge")
    for y in (-3.08,-1.55,0,1.55,3.06):
        for (x,z),(xx,zz) in zip(coque,coque[1:]):
            panneau_rampant(x,z+.055,xx,zz+.055,y-.055,y+.055,.095,"cuivre")
    # Oculus octogonal, encastré dans le tympan qui domine le ponton.
    for rayon,y,ton in ((.59,-3.10,"chene"),(.47,-3.14,"creme"),(.37,-3.17,"vitre_fumee")):
        cercle=[(rayon*math.cos(i*math.tau/8),4.56+rayon*math.sin(i*math.tau/8)) for i in range(8)]
        extrusion_facade(cercle,y,y+.05,ton)
    boite(0,-3.19,4.22,.052,.05,.68,"cuivre")
    boite(0,-3.19,4.53,.67,.05,.052,"cuivre")
    for x in (-1.54,1.54):
        boite(x,-3.91,.12,.19,.21,2.81,"chene")
        boite(x,-3.91,.12,.33,.34,.36,"pierre")
        signe = 1 if x<0 else -1
        profil=[(x,2.12),(x+signe*.61,2.83),(x+signe*.37,2.83),(x,2.49)]
        extrusion_facade(profil if signe>0 else list(reversed(profil)),-4.01,-3.83,"chene")
    boite(0,-3.91,2.84,3.46,.24,.20,"bois")
    avant=[(-1.85,-4.14,3.03),(1.85,-4.14,3.03),(1.85,-2.77,3.53),(-1.85,-2.77,3.53)]
    prisme(avant,[(x,y,z+.11) for x,y,z in avant],"cuivre")
    for x in (-1.77,-.89,0,.89,1.77):
        bande=[(x-.028,-4.15,3.15),(x+.028,-4.15,3.15),(x+.028,-2.77,3.65),(x-.028,-2.77,3.65)]
        prisme(bande,[(a,b,c+.025) for a,b,c in bande],"miel")

def couverture_des_couturieres():
    # Le versant long s'interrompt sur une claire-voie au-dessus de la table.
    profil=[(-3.85,3.42),(3.85,3.42),(3.85,3.75),(-.94,5.84),
            (-.94,4.65),(-3.85,3.75)]
    extrusion_facade(profil,-2.98,3.03,"ocre")
    for x1,z1,x2,z2,rangs in ((-3.89,3.78,-.94,4.71,4),(-.97,5.91,3.89,3.78,7)):
        for i in range(rangs):
            t,u=i/rangs,(i+1)/rangs
            x,xx=x1+(x2-x1)*t,x1+(x2-x1)*u
            z,zz=z1+(z2-z1)*t,z1+(z2-z1)*u
            # Chaque rang de tuiles porte des joints décalés.
            bornes=[-3.13]+[y+i%2*.37 for y in (-2.6,-1.65,-.7,.25,1.2,2.15)]+[3.17]
            for j,(y,yy) in enumerate(zip(bornes,bornes[1:])):
                ton=("tuile","saumon","tuile","cuivre")[(i*3+j)%4]
                panneau_rampant(x,z,xx,zz,y+.012,yy-.012,.105,ton)
    boite(-.975,0,4.76,.11,5.84,.95,"vitre_fumee")
    for y in (-2.89,-1.45,0,1.45,2.89):
        boite(-1.045,y,4.74,.09,.09,1.01,"creme")
    boite(-1.045,0,5.23,.09,5.84,.075,"creme")
    # Le store de boutique couvre toute la façade ; la toile porte une pièce cousue.
    for i in range(13):
        ton="corail" if i%2==0 else "creme"
        x=-3.32+i*.51
        # Store haut et court : la vitrine reste visible depuis la caméra plongeante.
        base=[(x,-3.77,2.81),(x+.51,-3.77,2.81),(x+.51,-2.85,3.43),(x,-2.85,3.43)]
        prisme(base,[(a,b,c+.045) for a,b,c in base],ton)
        extrusion_facade([(x,2.83),(x+.035,2.64),(x+.255,2.54),(x+.475,2.64),(x+.51,2.83)],
                         -3.80,-3.74,ton)
    morceau([(-2.72,-3.62,2.967),(-2.40,-3.62,2.967),(-2.40,-3.38,3.129),(-2.72,-3.38,3.129)],
            [(0,1,2,3)],"saumon")
    for x in (-3.27,3.27):
        boite(x,-3.76,-.6,.12,.13,3.41,"bois")
    # Enseigne : une bobine de fil géante pendue à une potence, aiguille piquée dedans.
    boite(3.3,-3.02,3.2,.16,.08,.8,"ombre")
    tige((3.3,-3.02,3.85),(3.3,-4.58,3.85),.035,"ombre")
    tige((3.3,-3.02,3.3),(3.3,-3.8,3.85),.025,"ombre")
    pilier(3.3,-4.58,3.81,.05,.08,"ombre")
    y,z=-4.35,3.12
    for dx in (-.03,.03):
        tige((3.3+dx*4,y,3.85),(3.3+dx*4,y,z+.3),.016,"ombre")
    for signe in (-1,1):
        tige((3.3+signe*.20,y,z),(3.3+signe*.25,y,z),.40,"chene")
    tige((3.08,y,z),(3.52,y,z),.13,"bois")
    tige((3.11,y,z),(3.49,y,z),.24,"corail")
    tige((3.3,y-.27,z+.36),(3.3,y+.24,z-.33),.022,"ardoise")
    boucle(3.3,y-.27,z+.40,.03,.03,.012,"ardoise")

def vitrine(cx):
    # Grande baie à petits carreaux entre le montant de porte et le poteau d'angle.
    boite(cx,-2.66,1.15,1.88,.06,2.0,"vitrine")
    boite(cx,-2.78,1.06,2.06,.5,.12,"creme")
    boite(cx,-2.74,3.06,2.0,.34,.13,"chene")
    for signe in (-1,1):
        boite(cx+signe*.95,-2.74,1.15,.12,.34,1.98,"chene")
    for x in (cx-.31,cx+.31):
        boite(x,-2.71,1.15,.06,.1,1.95,"creme")
    for z in (1.82,2.48):
        boite(cx,-2.71,z,1.86,.1,.06,"creme")

def tige(debut, fin, rayon, ton):
    # Section hexagonale pour les poignées, les outils et les cordages.
    a,b = Vector(debut),Vector(fin)
    axe = (b-a).normalized()
    repere = Vector((0,0,1)) if abs(axe.z)<.9 else Vector((0,1,0))
    u = axe.cross(repere).normalized()*rayon
    v = axe.cross(u)
    cercle = [u*math.cos(i*math.tau/6)+v*math.sin(i*math.tau/6) for i in range(6)]
    prisme([tuple(a+d) for d in cercle],[tuple(b+d) for d in cercle],ton)

def boucle(x,y,z,rx,ry,rayon,ton):
    points=[(x+rx*math.cos(i*math.tau/16),y+ry*math.sin(i*math.tau/16),z) for i in range(16)]
    for i,point in enumerate(points):
        tige(point,points[(i+1)%16],rayon,ton)

def siege(x,y,dossier):
    for dx,dy in ((-.25,-.23),(.25,-.23),(-.25,.23),(.25,.23)):
        tige((x+dx*1.21,y+dy*1.22,.15),(x+dx,y+dy,.85),.052,"chene")
    boite(x,y,.82,.68,.64,.12,"chene")
    if dossier:
        for dx in (-.25,.25):
            tige((x+dx,y+.23,.91),(x+dx,y+.33,1.62),.045,"bois")
        boite(x,y+.31,1.38,.61,.09,.20,"chene")

def accessoires_du_port():
    # Poêle en fonte, porte du foyer, marmite à couvercle et anse relevée.
    x,y=2.15,1.81
    for dx in (-.32,.32):
        for dy in (-.23,.23):
            pilier(x+dx,y+dy,.14,.078,.32,"ardoise")
    pilier(x,y,.40,.50,.73,"ardoise",.45)
    pilier(x,y,1.13,.52,.09,"ombre")
    boite(x,y-.44,.56,.45,.08,.37,"ombre")
    boite(x+.14,y-.51,.74,.18,.07,.05,"cuivre")
    pilier(x,y,1.22,.25,.31,"cuivre",.31)
    pilier(x,y,1.53,.335,.055,"chene",.24)
    pilier(x,y,1.585,.066,.072,"ombre")
    for signe in (-1,1):
        tige((x+signe*.31,y,1.46),(x+signe*.19,y,1.83),.026,"ombre")
    tige((x-.19,y,1.83),(x+.19,y,1.83),.026,"ombre")
    pilier(x+.14,y+.35,1.16,.092,1.52,"ardoise")
    # Carte côtière déroulée et compas à deux branches.
    boite(-2.12,1.03,1.593,.94,.70,.018,"creme")
    trace=[(-2.52,.88),(-2.37,.99),(-2.23,.96),(-2.14,1.13),(-1.95,1.08),(-1.77,1.26)]
    for a,b in zip(trace,trace[1:]):
        tige((*a,1.618),(*b,1.618),.012,"vitre_fumee")
    for fin in ((-1.78,.84,1.626),(-1.94,.84,1.626)):
        tige((-1.88,1.10,1.66),fin,.018,"cuivre")
    # Cordage lové sous la table et flotteurs de liège sur le montant.
    for i in range(4):
        boucle(-2.1,1.16,.18+i*.057,.42-i*.018,.34-i*.013,.035,"miel")
    for i in range(3):
        x=-2.70+i*.16
        tige((x,.55,1.43),(x,.55,1.03-i*.06),.012,"bois")
        pilier(x,.55,.83-i*.06,.063,.21,"ocre",.045)
    # Vaisselle creuse sur les tablettes ouvertes.
    for x in (2.00,2.47,2.88):
        pilier(x,.17,1.51,.105,.13,"creme",.14)
        pilier(x,.17,1.64,.115,.006,"cuivre")
        boucle(x,.17,1.65,.135,.135,.017,"creme")
    for i in range(3):
        pilier(2.46,.18,1.045+i*.038,.22,.034,"verre",.25)

def accessoires_de_couture():
    # Mannequin sur pied, exposé dans la vitrine de droite.
    x,y=2.25,-1.95
    for dx,dy in ((-.33,-.23),(.33,-.23),(0,.34)):
        tige((x,y,.35),(x+dx,y+dy,.16),.048,"chene")
    pilier(x,y,.28,.064,.92,"cuivre")
    anneaux=[(1.12,.31,.19),(1.38,.37,.24),(1.62,.25,.18),
             (1.91,.40,.24),(2.11,.43,.21),(2.20,.13,.12),(2.31,.12,.11)]
    contours=[[(x+l*math.cos(i*math.tau/12),y+p*math.sin(i*math.tau/12),z)
               for i in range(12)] for z,l,p in anneaux]
    for bas,haut in zip(contours,contours[1:]):
        prisme(bas,haut,"sable")
    for a,b in zip(anneaux,anneaux[1:]):
        tige((x,y-a[2]-.008,a[0]),(x,y-b[2]-.008,b[0]),.012,"chene")
    boucle(x,y,1.64,.265,.193,.024,"corail")
    pilier(x,y,2.31,.063,.11,"chene",.037)
    # Ciseaux ouverts, tambour à broder et coussin à épingles.
    for signe in (-1,1):
        boucle(-1.72+signe*.063,-1.73,1.51,.045,.070,.016,"cuivre")
        a=(-1.72+signe*.063,-1.67,1.51)
        b=(-1.72-signe*.073,-1.32,1.515)
        tige(a,b,.021,"ardoise")
    pilier(-1.72,-1.59,1.527,.024,.012,"or")
    pilier(-2.56,-.43,1.48,.18,.026,"creme")
    boucle(-2.56,-.43,1.52,.185,.185,.021,"chene")
    pilier(-1.81,-.45,1.48,.11,.072,"corail",.085)
    for i in range(3):
        tige((-1.84+i*.036,-.45,1.53),(-1.87+i*.055,-.44,1.68),.009,"ardoise")
    # Un lé pend du rayonnage, les autres tissus attendent sur leurs rouleaux.
    for i,ton in enumerate(("sauge","saumon","creme")):
        y=-.30+i*.40
        tige((2.58,y,.84),(3.02,y,.84),.145,ton)
        tige((2.55,y,.84),(2.59,y,.84),.046,"bois")
    for i in range(5):
        x=2.565+.038*(i%2)
        boite(x,.37+i*.078,.38,.043,.085,.92,"corail" if i in (0,4) else "creme")
    # Sur le comptoir : mètre ruban enroulé, coupons pliés, boîte à boutons.
    boucle(.15,1.78,1.56,.16,.16,.02,"corail")
    tige((.31,1.78,1.56),(.62,1.62,1.555),.012,"corail")
    for i,ton in enumerate(("sauge","peche","creme")):
        boite(1.35,1.85,1.555+i*.075,.62,.48,.07,ton)
    boite(2.0,1.8,1.555,.36,.28,.14,"cuivre")
    boite(2.0,1.8,1.7,.38,.30,.03,"chene")
    # Bobines rangées sur les étagères derrière le comptoir.
    for z in (2.06,2.66):
        for i in range(8):
            x=-.35+i*.36
            ton=("corail","sauge","or","creme","saumon","ardoise","peche","rose")[(i+int(z*3))%8]
            pilier(x,2.36,z+.06,.1,.05,"bois")
            pilier(x,2.36,z+.11,.075,.25,ton)
            pilier(x,2.36,z+.36,.1,.05,"bois")
    # Cabine d'essayage : rideau rayé, à demi tiré, et miroir au mur.
    tige((-3.06,.9,3.0),(-1.5,.9,3.0),.03,"cuivre")
    tige((-1.5,.9,3.0),(-1.5,2.48,3.0),.03,"cuivre")
    for i in range(3):
        x=-3.0+i*.3
        boite(x,.9+(i%2)*.07,.4,.29,.05,2.58,"corail" if i%2==0 else "creme")
    for i in range(5):
        y=1.05+i*.3
        boite(-1.5+(i%2)*.07,y,.4,.05,.29,2.58,"corail" if i%2==0 else "creme")
    boite(-3.03,1.7,.9,.05,.66,1.5,"chene")
    boite(-3.0,1.7,.98,.04,.52,1.34,"verre")

def foyer_visitable(centre, rotation, atelier=False):
    global angle

    def piece(nom):
        global origine, angle
        commencer(nom.replace("maison_du_quai", "des_couturieres") if atelier else nom)
        origine, angle = centre, rotation

    piece("Socle_maison_du_quai")
    bloc_chanfreine(7.12,5.78,-1.65,1.77,.26,"pierre")
    if atelier:
        bas = [(-1.12,-4.36,-.33),(1.12,-4.36,-.33),(1.12,-2.65,-.33),(-1.12,-2.65,-.33)]
        prisme(bas, [(x,y,-.19 if y < -4 else .12) for x,y,_ in bas], "sable")
    terminer(True)

    def murs(z, hauteur, vitrines=False):
        for cote in (-1,1):
            boite(cote*3.24,0,z,.36,5,hauteur,"craie")
            if vitrines:
                # Au-dessus des vitrines, seul le bandeau de façade reste maçonné.
                boite(cote*2.23,-2.66,3.15,2.38,.32,.34,"craie")
            else:
                boite(cote*2.23,-2.66,z,2.38,.32,hauteur,"craie")
        boite(0,2.66,z,6.85,.32,hauteur,"craie")

    piece("Soubassement_maison_du_quai")
    murs(.12,1.03)
    terminer(True)

    piece("Murs_hauts_maison_du_quai")
    murs(1.15,2.34,atelier)
    boite(0,-2.66,3.15,2.1,.32,.34,"craie")
    for x in (-1.12,1.12):
        boite(x,-2.83,.12,.19,.19,3.02,"creme")
    boite(0,-2.83,3.02,2.43,.21,.17,"creme")
    if atelier:
        for cx in (-2.165,2.165):
            vitrine(cx)
    else:
        fenetre(-2.19,-2.85,1.63,1.03,"cuivre")
        fenetre(2.19,-2.85,1.63,1.03,"cuivre")
    for x in (-3.21,3.21):
        boite(x,-2.83,.13,.21,.18,3.33,"chene")
    for x in (-2.22,2.22):
        boite(x,-2.83,.77,2.32,.15,.14,"chene")
    # Vantail déjà entrouvert vers l'intérieur après le départ.
    morceau([(1,-2.54,.16),(1,-.91,.16),(1,-.91,2.99),(1,-2.54,2.99),
             (.87,-2.54,.16),(.87,-.91,.16),(.87,-.91,2.99),(.87,-2.54,2.99)],
            [(4,5,6,7),(3,2,1,0),(0,1,5,4),(7,6,2,3),(4,7,3,0),(1,2,6,5)], "chene")
    boite(.82,-1.23,1.53,.18,.14,.075,"or")
    # La façade sur le ponton est visible dès l'arrivée du robot.
    angle = rotation - math.pi/2
    fenetre(.49,-3.43,1.66,1.44,"cuivre")
    angle = rotation + math.pi
    fenetre(.61,-2.83,1.66,1.22,"cuivre")
    terminer()

    piece("Toit_maison_du_quai")
    if atelier:
        couverture_des_couturieres()
    else:
        couverture_du_quai()
    terminer()

    if atelier:
        piece("Mobilier_des_couturieres")
        for x in (-2.78,-1.66):
            for y in (-2.17,-.22):
                boite(x,y,.12,.16,.16,1.22,"bois")
        boite(-2.22,-1.19,1.34,1.54,2.36,.14,"chene")
        # Comptoir de vente adossé au fond, étagères à bobines au-dessus.
        boite(.9,1.8,.12,3.0,.85,1.32,"chene")
        boite(.9,1.76,1.44,3.2,1.0,.11,"bois")
        for z in (2.06,2.66):
            boite(.9,2.36,z,3.1,.28,.06,"chene")
        for x in (-.6,2.4):
            boite(x,2.42,1.55,.1,.14,1.3,"bois")
        for x in (-3.06,-1.5):
            pilier(x,.9,.12,.04,2.9,"cuivre")
        pilier(-1.5,2.48,.12,.04,2.9,"cuivre")
        for y in (-.61,.95):
            boite(2.83,y,.12,.46,.09,1.25,"chene")
        for h in (.32,.65,1.29):
            boite(2.83,.17,h,.49,1.65,.08,"chene")
        pilier(2.25,-1.95,.12,.25,.16,"bois")
        siege(-.89,-.68,False)
        terminer(True)
        piece("Mannequin_et_outils")
        accessoires_de_couture()
        for i in range(12):
            boite(-2.82+i*.514,0,.122,.503,5.11,.02,"sable" if i%3 else "terre_claire")
        terminer()
        piece("Ouvrage_et_linge")
        # Une veste déployée sur la table, avec une manche et un coude rapiécé.
        patron=[(-.30,-.56),(.31,-.54),(.27,.13),(.54,-.03),(.69,.15),
                (.34,.44),(.13,.48),(.05,.36),(-.07,.35),(-.16,.48),
                (-.35,.45),(-.64,.24),(-.52,.02),(-.27,.13)]
        bas=[(-2.25+x,-1.23+y,1.481) for x,y in patron]
        prisme(bas,[(x,y,1.517) for x,y,z in bas],"toit_sauge")
        for i in range(4):
            pilier(-2.24,-1.58+i*.18,1.519,.023,.009,"miel")
        boite(-2.72,-.97,1.516,.21,.23,.012,"corail")
        for i in range(4):
            boite(-2.81+i*.047,-1.07,1.528,.018,.05,.011,"creme")
        for i,ton in enumerate(("corail","sauge","ocre")):
            x=-2.64+i*.30
            pilier(x,-2.11,1.48,.10,.04,"bois")
            pilier(x,-2.11,1.52,.074,.17,ton)
            pilier(x,-2.11,1.69,.10,.035,"bois")
        for i,ton in enumerate(("corail","creme","sauge","peche")):
            boite(2.82,.17,1.37+i*.09,.39,1.12-i*.07,.088,ton)
        terminer()
    else:
        piece("Mobilier_maison_du_quai")
        # Table haute et banc simple, disposés de part et d'autre de l'allée.
        for x in (-2.73,-1.47):
            for y in (.72,1.56):
                boite(x,y,.12,.14,.14,1.33,"bois")
        boite(-2.1,1.14,1.45,1.69,1.18,.14,"chene")
        siege(-2.05,2.04,True)
        boite(2.15,1.81,.12,1.18,1.08,.08,"pierre")
        for x in (1.82,3.06):
            boite(x,.2,.12,.10,.43,1.89,"chene")
        boite(2.44,.39,.14,1.25,.07,1.84,"bois")
        boite(-2.32,-1.23,.12,1.21,2.45,.44,"chene")
        terminer(True)

        piece("Poele_et_objets_du_port")
        accessoires_du_port()
        terminer(True)
        piece("Sol_et_objets_maison_du_quai")
        for i in range(9):
            boite(0,-2.41+i*.59,.12,6.13,.575,.021,"sable" if i%3 else "terre_claire")
        boite(0,1.25,.147,1.88,1.94,.048,"corail")
        for x in (-.78,.78):
            boite(x,1.25,.19,.09,1.94,.012,"creme")
        pilier(-2.66,1.51,1.59,.105,.18,"cuivre",.13)
        pilier(-2.66,1.51,1.77,.103,.004,"ombre")
        boite(2.44,.2,.92,1.37,.42,.12,"bois")
        boite(2.44,.2,1.38,1.37,.42,.1,"bois")
        boite(-2.32,-1.23,.56,1.15,2.37,.23,"creme")
        boite(-2.32,-1.45,.71,1.18,1.87,.10,"toit_sauge")
        boite(-2.32,-.34,.79,.78,.36,.14,"creme")
        terminer()

    piece("Valise_des_couturieres" if atelier else "Premiere_valise")
    x,y,z = (1.85,-1.0,.14) if atelier else (1.85,-1.42,.14)
    boite(x,y,z,1.13,.53,.68,"cuivre")
    for x_sangle in (x-.36,x+.36):
        boite(x_sangle,y,z+.02,.094,.557,.696,"or")
    if atelier:
        boite(x-.36,y-.29,z+.47,.13,.033,.19,"corail")
    for dx in (-.18,.18):
        boite(x+dx,y,z+.68,.07,.11,.18,"bois")
    boite(x,y,z+.84,.42,.115,.06,"bois")
    boite(x,y-.274,z+.28,.43,.027,.25,"creme")
    # Lettres gravées sur l'étiquette orientée vers l'entrée.
    for lettre, segments in enumerate(("N","E","F")):
        bx = x-.115 + lettre*.115
        boite(bx,y-.292,z+.32,.013,.015,.152,"bois")
        if segments == "N":
            boite(bx+.065,y-.292,z+.32,.013,.015,.152,"bois")
            extrusion_facade([(bx,z+.45),(bx+.011,z+.459),(bx+.076,z+.337),
                              (bx+.065,z+.327)], y-.300,y-.288,"bois")
        else:
            for dz in ((.32,.39,.46) if segments == "E" else (.39,.46)):
                boite(bx+.031,y-.292,z+dz,.078,.015,.013,"bois")
    terminer()

def fenetre_haute(x, y, z, largeur, hauteur):
    # Haute fenêtre de classe à imposte cintrée, petits bois et appui de pierre.
    demi = largeur/2
    arc = [(x+demi*math.cos(t*math.pi/6), z+hauteur+.42*math.sin(t*math.pi/6)) for t in range(7)]
    cadre = [(x-demi-.12,z), (x+demi+.12,z)] + [(a+(.12 if a>x else -.12 if a<x else 0), b+.12)
             for a,b in arc]
    extrusion_facade(cadre, y-.12, y+.02, "creme")
    extrusion_facade([(x-demi,z+.1),(x+demi,z+.1)]+arc, y-.16, y-.12, "vitre_fumee")
    boite(x,y-.19,z+.1,.07,.06,hauteur+.36,"creme")
    for h in (z+hauteur*.42, z+hauteur):
        boite(x,y-.19,h,largeur,.06,.07,"creme")
    boite(x,y-.2,z-.12,largeur+.42,.38,.14,"pierre")

def ecole(centre, rotation):
    # École de village : long bâtiment bas, clocheton, préau de bois et cour à marelle.
    global origine, angle

    def piece(nom):
        global origine, angle
        commencer(nom)
        origine, angle = centre, rotation

    L, P, h = 11, 7, 4.6
    piece("Socle_ecole")
    bloc_chanfreine(L+.5,P+.5,-1.9,2.15,.3,"pierre")
    # Perron de pierre devant la porte, où l'ancien corps s'est assis.
    boite(0,-4.15,-.9,6.2,1.3,1.13,"pierre")
    bas=[(-1.2,-5.4,-.4),(1.2,-5.4,-.4),(1.2,-4.8,-.4),(-1.2,-4.8,-.4)]
    prisme(bas,[(x,y,-.05 if y<-5 else .23) for x,y,_ in bas],"sable")
    terminer(True)

    def murs(z, hauteur, fond=None):
        # fond=None : tous les murs ; True : seulement les murs nord et ouest ; False : les autres.
        if fond is not True:
            boite(-(L/2-.18),0,z,.36,P,hauteur,"peche")
            for cote in (-1,1):
                boite(cote*3.36,-(P/2-.18),z,4.28,.36,hauteur,"peche")
        if fond is not False:
            boite(L/2-.18,0,z,.36,P,hauteur,"peche")
            boite(0,P/2-.18,z,L,.36,hauteur,"peche")

    def bandeau(fond):
        # Corniche en couronne : on garde l'intérieur ouvert vers le ciel.
        if fond:
            boite(L/2-.18,0,h,.6,P+.3,.24,"creme")
            boite(0,P/2-.18,h,L+.3,.6,.24,"creme")
        else:
            boite(-(L/2-.18),0,h,.6,P+.3,.24,"creme")
            boite(0,-(P/2-.18),h,L+.3,.6,.24,"creme")

    piece("Soubassement_ecole")
    murs(.25,1.1)
    terminer(True)

    # Les murs côté rue et côté caméra s'effacent quand le robot entre.
    piece("Murs_hauts_ecole")
    murs(1.35,h-1.35,False)
    boite(0,-(P/2-.18),3.45,2.44,.36,h-3.45,"peche")
    for x in (-1.22,1.22):
        boite(x,-P/2-.06,.25,.22,.2,3.3,"creme")
    boite(0,-P/2-.06,3.45,2.66,.24,.26,"creme")
    for x in (-4.2,-2.5,2.5,4.2):
        fenetre_haute(x,-P/2,1.55,1.05,1.75)
    # Deux vantaux grands ouverts vers l'intérieur.
    for signe in (-1,1):
        boite(signe*1.08,-P/2+.78,.27,.09,1.12,3.12,"bois")
        boite(signe*1.02,-P/2+1.12,1.62,.06,.14,.08,"or")
    angle = rotation - math.pi/2
    fenetre_haute(0,-L/2,1.55,1.05,1.75)
    angle = rotation
    bandeau(False)
    terminer()

    # Les murs nord et ouest restent debout : le tableau et les patères y sont accrochés.
    piece("Murs_du_fond_ecole")
    murs(1.35,h-1.35,True)
    bandeau(True)
    angle = rotation + math.pi
    for x in (-3.9,-1.3,1.3,3.9):
        fenetre_haute(x,-P/2,1.55,1.05,1.75)
    terminer()

    piece("Toit_ecole")
    toit(0,0,h+.24,L+1.0,P+1.0,2.5,"ardoise")
    # Faîtage clair et rangs d'ardoises plus sombres.
    boite(0,0,h+2.66,L+1.1,.3,.12,"creme")
    for t in (.25,.5,.75):
        for signe in (-1,1):
            y=signe*(P+1.0)/2*(1-t)
            boite(0,y,h+.24+2.5*t+.03,L+1.02,.07,.05,"ombre")
    # Clocheton : socle, quatre poteaux, cloche de cuivre et flèche d'ardoise.
    z=h+2.2
    boite(0,0,z,1.2,1.2,.7,"creme")
    for dx in (-.45,.45):
        for dy in (-.45,.45):
            boite(dx,dy,z+.7,.14,.14,1.05,"bois")
    pilier(0,0,z+.95,.34,.5,"cuivre",.13)
    pilier(0,0,z+1.45,.07,.12,"cuivre")
    base=[(a*.72,b*.72,z+1.75) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    prisme(base,[(a*.04,b*.04,z+2.75) for a,b,_ in base],"ardoise")
    # Le toit du préau, côté caméra, s'efface avec celui de l'école.
    pan=[(-8.25,-3.3,3.15),(-5.5,-3.3,3.95),(-5.5,3.3,3.95),(-8.25,3.3,3.15)]
    prisme(pan,[(x,y,z+.14) for x,y,z in pan],"cuivre")
    for y in (-2.8,-1.4,0,1.4,2.8):
        bande=[(-8.25,y-.03,3.29),(-5.5,y-.03,4.09),(-5.5,y+.03,4.09),(-8.25,y+.03,3.29)]
        prisme(bande,[(a,b,c+.03) for a,b,c in bande],"miel")
    terminer()

    piece("Preau_de_l_ecole")
    # Toit en appentis appuyé sur le pignon sud, quatre poteaux de bois.
    # La maison d'Aube occupe le côté nord : le préau s'ouvre vers les couturières.
    for y in (-2.9,-.95,.95,2.9):
        boite(-7.85,y,-.9,.24,.24,4.1,"chene")
    boite(-7.85,0,3.15,.32,6.2,.22,"chene")
    # Un long banc et des cartables oubliés sous le préau.
    for y in (.9,2.6):
        boite(-6.6,y,-.6,.5,.2,1.3,"bois")
    boite(-6.6,1.75,.7,.6,2.3,.1,"chene")
    for i,ton in enumerate(("corail","ardoise","miel")):
        boite(-6.55,1.05+i*.6,.8,.24,.42,.36,ton)
        boite(-6.55,1.05+i*.6,1.16,.06,.2,.1,"bois")
    terminer(True)

    piece("Cour_de_l_ecole")
    # Marelle peinte à la craie, du « 1 » jusqu'au ciel en demi-lune.
    cases=[(0,0),(0,1),(0,2),(-.5,3),(.5,3),(0,4),(-.5,5),(.5,5)]
    def sol(x):
        return .036+(x-2)*.019+.025
    for dx,rang in cases:
        x=1.7+rang*.64
        boite(x,-6.0+dx*1.24,-.1,.58,.58,sol(x)+.1,"creme")
    xc=1.7+6*.64-.3
    ciel=[(xc+.4*math.sin(t*math.pi/6),-6.0+.4*math.cos(t*math.pi/6)) for t in range(7)]
    prisme([(a,b,-.1) for a,b in ciel],[(a,b,sol(xc)) for a,b in ciel],"corail")
    pilier(2.3,-6.55,sol(2.3)-.04,.09,.07,"corail")
    terminer()

    piece("Mobilier_ecole")
    # Estrade le long du mur nord, sous le tableau.
    boite(L/2-1.0,0,.25,1.3,P-.8,.3,"chene")
    # Pupitres doubles à hauteur de Semeur, tournés vers le tableau, banc attaché derrière.
    for x in (-3.9,-2.0,2.2):
        for y in (-1.75,1.75):
            for dy in (-.95,.95):
                boite(x,y+dy,.25,.6,.14,.92,"bois")
            plateau=[(x-.38,y-1.1,1.24),(x+.38,y-1.1,1.12),(x+.38,y+1.1,1.12),(x-.38,y+1.1,1.24)]
            prisme(plateau,[(a,b,c+.09) for a,b,c in plateau],"chene")
            if (x,y)==(2.2,1.75):
                # Banc renversé en arrière : quelqu'un est parti en courant.
                boite(x-1.25,y,.27,.08,2.2,.48,"chene")
                for dy in (-.8,.8):
                    boite(x-1.0,y+dy,.27,.5,.42,.12,"bois")
                continue
            boite(x-.72,y,.25,.42,2.1,.5,"bois")
            boite(x-.72,y,.75,.48,2.2,.08,"chene")
    # Bureau du maître sur l'estrade, près de la fenêtre.
    for dy in (-.7,.7):
        boite(L/2-1.0,-2.0+dy,.55,.7,.16,1.0,"bois")
    boite(L/2-1.0,-2.0,1.55,.95,1.8,.1,"chene")
    terminer(True)

    def sur_pupitre(x0, x, y, l, p, e, ton):
        # Objet plat posé sur le plateau incliné du pupitre centré en x0.
        def z(xx):
            return 1.33-(xx-(x0-.38))/.76*.12+.005
        bas=[(x+a*l/2,y+b*p/2,z(x+a*l/2)) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        prisme(bas,[(a,b,c+e) for a,b,c in bas],ton)

    piece("Affaires_de_classe")
    # La classe a été quittée en pleine journée : cahiers ouverts, ardoises, craies.
    for x0,y,ton in ((-2.0,-2.3,"rose"),(-2.0,1.2,"verre"),(2.2,-1.2,"or"),(2.2,2.3,"sauge")):
        sur_pupitre(x0,x0,y,.42,.62,.02,"creme")
        sur_pupitre(x0,x0+.01,y,.44,.03,.025,ton)
    for x0,y in ((-3.9,1.2),(-2.0,-1.2),(2.2,-2.3)):
        sur_pupitre(x0,x0-.05,y,.4,.52,.03,"chene")
        sur_pupitre(x0,x0-.05,y,.32,.44,.035,"ombre")
        sur_pupitre(x0,x0+.2,y+.3,.05,.16,.06,"creme")
    # Bureau du maître : cloche à main et pile de cahiers.
    pilier(L/2-1.0,-2.55,1.65,.13,.2,"cuivre",.05)
    tige((L/2-1.0,-2.55,1.85),(L/2-1.0,-2.55,2.0),.035,"bois")
    for k,ton in enumerate(("corail","sauge","miel","rose","verre")):
        boite(L/2-1.0+(k%2)*.03,-1.55,1.65+k*.045,.4,.55,.045,ton)
    # Feuilles mortes et poussière entrées par la porte ouverte.
    feuilles=random.Random(22)
    for k in range(18):
        fx,fy=feuilles.uniform(-1.6,1.6),-P/2+.5+feuilles.uniform(0,1.8)**1.6
        t=feuilles.uniform(0,math.pi)
        f=[(fx+.14*math.cos(t+a*math.pi/2)*(1 if a%2==0 else .55),fy+.14*math.sin(t+a*math.pi/2)*(1 if a%2==0 else .55),.275) for a in range(4)]
        prisme(f,[(a,b,c+.012) for a,b,c in f],feuilles.choice(("miel","ocre","corail","herbe_seche")))
    for x,y,l,p in ((0,-P/2+1.0,2.2,1.4),(-.6,-P/2+2.0,1.3,.9)):
        boite(x,y,.272,l,p,.004,"terre_claire")
    terminer()

    piece("Pupitre_Aube")
    # La place d'Aube : le dernier pupitre près de la fenêtre côté rue.
    xa,ya=-3.9,-2.3
    # Le bois gravé au canif : une maison, un soleil et des petits traits.
    for a,b,c,d in ((-.15,-.2,.1,-.2),(.1,-.2,.1,0),(.1,0,-.15,0),(-.15,0,-.15,-.2),(-.15,0,-.02,.13),(-.02,.13,.1,0)):
        a,b,c,d=.27+a*.45,b*.45,.27+c*.45,d*.45
        za=1.33-(a+.38)/.76*.12+.006
        zb=1.33-(c+.38)/.76*.12+.006
        tige((xa+a,ya+.3+b,za),(xa+c,ya+.3+d,zb),.008,"ombre")
    # Son ardoise couverte de petits bonshommes : ses amis cachés.
    sur_pupitre(xa,xa,ya-.05,.46,.6,.03,"chene")
    sur_pupitre(xa,xa,ya-.05,.38,.52,.035,"ombre")
    for k in range(5):
        bx,by=xa-.12+(k%2)*.22,ya-.25+k*.1
        sur_pupitre(xa,bx,by,.035,.035,.04,"creme")
        sur_pupitre(xa,bx-.045,by,.06,.012,.04,"creme")
        sur_pupitre(xa,bx-.09,by-.015,.035,.012,.04,"creme")
        sur_pupitre(xa,bx-.09,by+.015,.035,.012,.04,"creme")
    terminer()

    # Le dessin « ma cachette sous l'escalier » est posé par la scène Godot (page_lisible.gd).

    piece("Tableau_et_dessins")
    # Repère tourné : x local = le long du mur nord, y local = vers l'intérieur.
    angle = rotation + math.pi/2
    y=-L/2+.37
    # Le tableau de la comptine : lignes à la craie et quatre ronds de couleur.
    boite(0,y,1.35,4.6,.08,2.3,"chene")
    boite(0,y+.05,1.45,4.4,.06,2.1,"ombre")
    # La comptine et les quatre ronds sont dessinés à la craie sur une image (tools/affiches/tableau_comptine.html),
    # posée sur l'ardoise par la scène Godot.
    boite(0,y+.06,1.3,4.5,.18,.07,"chene")
    for i in range(3):
        boite(-1.6+i*.3,y+.13,1.36,.18,.05,.05,("creme","rose","or")[i])
    # Frise de dessins d'enfants punaisés au-dessus du tableau.
    for i in range(6):
        cx = -2.6+i*1.04
        boite(cx,y+.02,3.78,.72,.03,.56,"creme")
        for j,ton in enumerate(("corail","sauge","or")):
            boite(cx-.18+j*.17,y+.04,3.88+(i+j)%3*.09,.14,.02,.14,ton)
        pilier(cx,y+.04,4.28,.025,.02,"corail")
    # Patères, manteaux et cartables sur le mur ouest.
    angle = rotation + math.pi
    yo=-P/2+.37
    boite(2.4,yo+.05,2.55,4.2,.1,.14,"chene")
    for i in range(8):
        x=.6+i*.52
        tige((x,yo+.09,2.6),(x,yo+.29,2.72),.03,"cuivre")
        if i%2==0:
            boite(x,yo+.23,1.6,.4,.2,1.0,("corail","sauge","rose","ocre")[i//2])
        else:
            boite(x,yo+.21,1.85,.32,.16,.38,("miel","ardoise","cuivre","corail")[i//2])
            tige((x-.1,yo+.21,2.23),(x,yo+.21,2.64),.012,"bois")
    angle = rotation
    for i in range(16):
        boite(-5.1+i*.68,0,.25,.66,P-.72,.02,"sable" if i%3 else "terre_claire")
    terminer()

def rampe(x0, x1, y0, y1, z0, z1, epaisseur=.3):
    # Plan incliné le long de y (de y0 à z0 jusqu'à y1 à z1), pour la collision des escaliers.
    bas=[(x0,y0,z0-epaisseur),(x1,y0,z0-epaisseur),(x1,y1,z1-epaisseur),(x0,y1,z1-epaisseur)]
    prisme(bas,[(x,y,z+epaisseur) for x,y,z in bas],"pierre")

def marches(x0, x1, y0, y1, z0, z1, n, ton, plein=None):
    # Marches visibles ; plein donne le bas du massif sous chaque marche (sinon une simple volée).
    for k in range(n):
        ya, yb = y0+(y1-y0)*k/n, y0+(y1-y0)*(k+1)/n
        zh = z0+(z1-z0)*(k+1)/n
        bas = plein if plein is not None else zh-.32
        boite((x0+x1)/2,(ya+yb)/2,bas,abs(x1-x0),abs(yb-ya),zh-bas,ton)

def maison_aube(centre, rotation):
    # Maison étroite et haute : cave à hauteur du sol, étage avec la chambre d'Aube,
    # escalier extérieur au sud, cour close à l'arrière, traversée par le tuyau des câbles.
    global origine, angle

    def piece(nom):
        global origine, angle
        commencer(nom)
        origine, angle = centre, rotation

    L, P = 5.2, 6.0
    xi, yi = L/2-.3, P/2-.3        # faces intérieures
    zc, zp, ze, zm, zh = .25, 2.45, 2.6, 3.7, 5.8   # cave, plancher, étage, bandeau, corniche
    enduit, volet = "ardoise", "creme"
    sx0, sx1 = -1.5, -.5           # soupirail dans le mur du fond, côté cour
    tx0, tx1 = 1.25, 2.3           # trémie de l'escalier intérieur, le long du mur nord
    ty0, ty1 = -2.0, 1.0

    piece("Socle_Aube")
    bloc_chanfreine(L+.4,P+.4,-1.9,2.15,.28,"pierre")
    terminer(True)

    def murs_cave(z0, z1, haut, fond=None):
        # Mur du fond percé du soupirail ; le linteau n'existe que dans la partie haute.
        # fond=True : murs nord et ouest (loin de la caméra) ; False : murs sud et rue.
        if fond is not True:
            boite(-(L/2-.15),0,z0,.3,P,z1-z0,"pierre")
            boite(0,-(P/2-.15),z0,L,.3,z1-z0,"pierre")
        if fond is not False:
            boite(L/2-.15,0,z0,.3,P,z1-z0,"pierre")
            for a,b in ((-L/2,sx0),(sx1,L/2)):
                boite((a+b)/2,P/2-.15,z0,b-a,.3,z1-z0,"pierre")
            if haut:
                boite((sx0+sx1)/2,P/2-.15,2.3,sx1-sx0,.3,z1-2.3,"pierre")

    piece("Cave_bas_Aube")
    murs_cave(zc,1.0,False)
    for i in range(10):
        boite(-L/2+.3+i*.46+.23,0,zc,.45,P-.6,.02,"terre_claire" if i%3 else "fissure")
    terminer(True)

    piece("Cave_haut_Aube")
    murs_cave(1.0,zp,True,False)
    terminer(True)
    piece("Cave_fond_Aube")
    murs_cave(1.0,zp,True,True)
    terminer(True)

    piece("Mobilier_cave_Aube")
    # Caisses, tonneaux et réserve de lanternes neuves : la peur s'entassait jusque dans la cave.
    for x,y,t in ((-1.75,-1.75,.9),(-1.75,-.85,.7),(-.8,-1.85,.8)):
        boite(x,y,zc,t,t,t,"bois")
        boite(x,y,zc+t,t+.04,t+.04,.05,"chene")
    for x in (-1.85,-1.2):
        pilier(x,.6,zc,.36,1.05,"chene",.33)
        pilier(x,.6,zc+1.05,.37,.05,"ombre")
    for z in (.9,1.6):
        boite(.45,2.45,zc+z,1.4,.42,.06,"chene")
        for i in range(4):
            pilier(-.05+i*.34,2.45,zc+z+.06,.12,.32,"or",.1)
            pilier(-.05+i*.34,2.45,zc+z+.38,.13,.06,"ardoise",.05)
    # La grille du soupirail, dévissée par Aube, posée contre le mur.
    for i in range(5):
        tige((-2.1+i*.16,2.55,zc),(-2.0+i*.16,2.2,zc+1.7),.025,"ombre")
    tige((-2.12,2.52,zc+.2),(-1.4,2.52,zc+.2),.03,"ombre")
    tige((-2.03,2.25,zc+1.5),(-1.31,2.25,zc+1.5),.03,"ombre")
    terminer(True)

    piece("Escalier_cave_Aube")
    marches(tx0,tx1,-2.4,ty1,zc,ze,11,"chene")
    for y in (-2.4,-.7,ty1):
        boite(tx0+.05,y,zc,.1,.1,max(.1,zc+(y+2.4)/3.4*(ze-zc)-zc),"bois")
    terminer()
    piece("Rampe_cave_Aube")
    rampe(tx0,tx1,-2.4,ty1,zc,ze)
    terminer("-colonly")

    piece("Plancher_Aube")
    # Plancher de l'étage, ouvert sur la trémie de l'escalier.
    for a,b,c,d in ((-L/2,tx0,-P/2,P/2),(tx0,L/2,-P/2,ty0),(tx0,L/2,ty1,P/2)):
        boite((a+b)/2,(c+d)/2,zp,b-a,d-c,ze-zp,"bois")
    for i in range(11):
        x, ton = -xi+i*.42+.21, "sable" if i%3 else "miel"
        if x+.2 <= tx0:
            boite(x,0,ze,.4,P-.6,.015,ton)
        else:
            for a,b in ((-yi,ty0),(ty1,yi)):
                boite(x,(a+b)/2,ze,.4,b-a,.015,ton)
    terminer(True)

    def murs_etage(z0, z1, fond=None):
        if fond is not True:
            boite(-(L/2-.15),0,z0,.3,P,z1-z0,enduit)
            boite(0,-(P/2-.15),z0,L,.3,z1-z0,enduit)
        if fond is not False:
            boite(L/2-.15,0,z0,.3,P,z1-z0,enduit)
            boite(0,P/2-.15,z0,L,.3,z1-z0,enduit)

    piece("Etage_bas_Aube")
    murs_etage(ze,zm)
    # Cloison entre la chambre (devant) et la pièce commune, porte ouverte.
    for a,b in ((-xi,-.6),(.6,tx0)):
        boite((a+b)/2,0,ze,b-a,.14,zm-ze,"craie")
    # Garde-corps autour de la trémie.
    boite(tx0,(ty0+ty1)/2,ze,.08,ty1-ty0,1.0,"chene")
    boite((tx0+tx1)/2,ty0,ze,tx1-tx0,.08,1.0,"chene")
    terminer(True)

    piece("Murs_hauts_Aube")
    murs_etage(zm,zh,False)
    for a,b in ((-xi,-.6),(.6,tx0)):
        boite((a+b)/2,0,zm,b-a,.14,1.2,"craie")
    boite(0,0,zm+1.2,1.2,.14,.3,"craie")
    for x0,y0,l,p in ((0,-(P/2-.2),L+.24,.4),(-(L/2-.2),0,.4,P+.24)):
        boite(x0,y0,zh,l,p,.2,"creme")
    # Façade sur la rue : volets clos, la maison est fermée de l'intérieur.
    for x in (-1.25,1.25):
        fenetre(x,-P/2,3.4,1.0,volet,True)
    # Porte de l'étage sur le palier sud, close ; la barre est mise à l'intérieur.
    angle = rotation - math.pi/2
    origine = (centre[0], centre[1], centre[2]+ze-.24)
    portail(-.9,-L/2,"chene")
    origine = centre
    fenetre(1.6,-L/2,3.4,.9,volet,True)
    angle = rotation
    boite(-xi+.08,.9,ze+1.3,.12,1.9,.16,"bois")
    for y in (.1,1.7):
        boite(-xi+.04,y,ze+1.22,.1,.12,.32,"ombre")
    terminer(True)

    # Murs nord et ouest de l'étage : ils restent debout, les lanternes y sont pendues.
    piece("Murs_fond_Aube")
    murs_etage(zm,zh,True)
    for x0,y0,l,p in ((0,P/2-.2,L+.24,.4),(L/2-.2,0,.4,P+.24)):
        boite(x0,y0,zh,l,p,.2,"creme")
    angle = rotation + math.pi
    fenetre(0,-P/2,3.4,1.0,volet,True)
    angle = rotation
    terminer(True)

    piece("Toit_Aube")
    # Pignon sur rue, toit raide d'ardoise ; lucarne de la chambre côté sud.
    profil=[(-3.05,zh+.15),(3.05,zh+.15),(0,zh+3.3)]
    extrusion_facade(profil,-P/2-.35,P/2+.35,"toit_sauge")
    for t in (.2,.4,.6,.8):
        for signe in (-1,1):
            x=signe*3.05*(1-t)
            boite(x,0,zh+.15+3.15*t+.02,.08,P+.72,.05,"ombre")
    boite(0,0,zh+3.25,.3,P+.8,.12,"creme")
    # Lucarne : petit toit, vitre où Aube a collé ses dessins.
    angle = rotation - math.pi/2
    ly, lz = 1.4, zh+.55
    boite(ly,-2.0,lz,1.3,1.1,1.25,enduit)
    morceau([(ly-.75,-2.6,lz+1.2),(ly+.75,-2.6,lz+1.2),(ly+.75,-1.4,lz+1.55),(ly-.75,-1.4,lz+1.55),
             (ly,-2.6,lz+1.8),(ly,-1.4,lz+2.0)],
            [(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)],"toit_sauge")
    boite(ly,-2.58,lz+.2,.95,.06,.85,"creme")
    boite(ly,-2.62,lz+.28,.8,.04,.7,"vitre_fumee")
    for i,(dx,dz,ton) in enumerate(((-.2,.55,"rose"),(.18,.5,"or"),(.02,.22,"corail"))):
        boite(ly+dx,-2.65,lz+dz,.24,.02,.2,"creme")
        boite(ly+dx,-2.66,lz+dz+.05,.1,.02,.1,ton)
    angle = rotation
    # Cheminée côté nord.
    boite(1.6,1.6,zh+1.2,.6,.6,2.4,"pierre")
    boite(1.6,1.6,zh+3.6,.72,.72,.12,"creme")
    terminer()

    piece("Mobilier_etage_Aube")
    # Chambre d'Aube, côté rue : lit d'enfant, bureau, étagère.
    boite(-1.7,-1.65,ze,1.1,2.0,.45,"chene")
    boite(-1.7,-1.65,ze+.45,1.04,1.94,.18,"creme")
    boite(-1.7,-.75,ze+.45,1.1,.12,1.1,"chene")
    for x in (-.2,1.0):
        boite(x,-2.4,ze,.1,.42,.95,"chene")
    boite(.4,-2.4,ze+.95,1.4,.5,.07,"chene")
    boite(.4,-1.85,ze,.5,.5,.55,"bois")
    boite(-2.05,-.35,ze,.4,.4,.55,"chene")
    # Pièce commune, côté cour : grande table, deux chaises de Semeurs.
    for dx in (-.8,.8):
        for dy in (-.45,.45):
            boite(-.8+dx,1.55+dy,ze,.12,.12,1.4,"bois")
    boite(-.8,1.55,ze+1.4,2.0,1.2,.1,"chene")
    for x in (-1.6,0.1):
        boite(x,2.45,ze,.6,.5,.85,"bois")
        boite(x,2.65,ze+.85,.6,.1,1.0,"bois")
    terminer(True)

    piece("Objets_Aube")
    # Le carnet ouvert sur le bureau, les crayons, la boîte à musique et sa petite prise.
    boite(.2,-2.4,ze+1.02,.32,.24,.02,"creme")
    boite(.2,-2.4,ze+1.04,.01,.24,.01,"bois")
    for i,ton in enumerate(("rose","verre","or")):
        tige((.48+i*.05,-2.5,ze+1.03),(.5+i*.05,-2.3,ze+1.03),.012,ton)
    bx, by, bz = .8, -2.42, ze+1.02
    boite(bx,by,bz,.34,.24,.16,"corail")
    boite(bx,by,bz+.16,.36,.26,.03,"chene")
    tige((bx-.1,by,bz+.22),(bx+.1,by,bz+.22),.035,"cuivre")
    tige((bx+.18,by,bz+.08),(bx+.25,by,bz+.08),.012,"cuivre")
    tige((bx+.25,by,bz+.08),(bx+.25,by,bz+.16),.012,"cuivre")
    pilier(bx-.05,by+.13,bz+.05,.03,.02,"or")
    # Dessins d'Aube punaisés partout sur la cloison et le mur de la rue.
    for i,(x,z) in enumerate(((-2.0,1.3),(-1.55,1.7),(-1.1,1.35),(-2.0,2.05),(-1.3,2.1),(.9,1.4),(.95,1.85))):
        z = ze+z
        boite(x,-.09,z,.3,.02,.24,"creme")
        boite(x-.04,-.11,z+.06,.12,.01,.1,("corail","sauge","or","rose","verre","peche","ocre")[i])
    for i in range(4):
        y, z = -1.75+i*.42, ze+1.5+(i%2)*.35
        boite(xi-.03,y,z,.02,.32,.26,"creme")
        boite(xi-.05,y,z+.06,.01,.12,.1,("rose","or","sauge","verre")[i])
    # Sa lanterne de chevet, recouverte d'un tissu pour faire le noir.
    pilier(-2.05,-.35,ze+.55,.12,.3,"or",.1)
    pilier(-2.05,-.35,ze+.54,.24,.42,"saumon",.06)
    # Sa petite valise « Nef », fermée, devant la porte de la chambre.
    boite(-1.0,-.35,ze,.6,.3,.42,"cuivre")
    boite(-1.0,-.52,ze+.18,.2,.02,.1,"creme")
    boite(-1.0,-.35,ze+.42,.2,.06,.06,"bois")
    # Côté pièce commune : les deux grandes valises des parents et dix lanternes alignées.
    for i in range(2):
        boite(-1.75+i*.7,.4,ze,.62,.35,.62,"cuivre")
        boite(-1.75+i*.7,.21,ze+.3,.24,.02,.12,"creme")
    for i in range(10):
        pilier(-1.9+i*.36,2.55,ze+1.85+(i%2)*.2,.1,.26,"or",.08)
        tige((-1.9+i*.36,2.55,ze+2.11+(i%2)*.2),(-1.9+i*.36,2.55,ze+2.5),.01,"ombre")
    # Une barre de bois condamne la porte de l'étage, de l'intérieur.
    terminer()

    piece("Palier_Aube")
    # Volée de pierre en porte-à-faux contre le mur sud, puis un palier massif percé
    # d'une petite porte d'enfant : le passage d'Aube vers la cour.
    marches(-4.0,-2.6,-4.4,-.2,-.25,ze,10,"pierre")
    for x in (-3.9,-2.7):
        boite(x,1.4,-.25,.2,3.2,2.35,"pierre")
    boite(-3.3,1.4,2.1,1.4,3.2,ze-2.1,"pierre")
    boite(-3.3,1.4,ze,1.5,3.3,.1,"sable")
    for y in (-.2,3.0):
        pilier(-3.98,y,ze,.06,1.0,"ombre")
    tige((-3.98,-.2,ze+1.0),(-3.98,3.0,ze+1.0),.04,"ombre")
    terminer()
    piece("Palier_Aube_creux")
    # Le passage reste visible de dessus quand le palier s'efface.
    boite(-3.3,1.4,-.2,1.0,3.2,.02,"terre_claire")
    for y in (-.25,3.05):
        for x in (-3.83,-2.77):
            boite(x,y,-.2,.1,.12,2.32,"chene")
        boite(-3.3,y,2.02,1.16,.14,.12,"chene")
    terminer()
    piece("Palier_Aube_collision")
    rampe(-4.0,-2.6,-4.4,-.2,-.25,ze,.35)
    boite(-3.3,1.4,2.1,1.4,3.2,ze+.25-2.1,"pierre")
    for x in (-3.9,-2.7):
        boite(x,1.4,-.25,.2,3.2,2.35,"pierre")
    boite(-3.98,1.4,ze,.1,3.2,1.0,"pierre")
    terminer("-colonly")

    piece("Cour_Aube")
    # Murets bas : la cour se voit de la caméra, mais le robot ne peut pas les sauter.
    for x0,y0,l,p in ((-4.0+.15,5.0,.3,4.0),(2.75,4.95,.3,4.1),(-.62,7.0-.15,6.75,.3)):
        boite(x0,y0,-.6,l,p,2.3,"craie")
        boite(x0,y0,1.7,l+.1,p+.1,.1,"tuile")
    # Un petit arbre et des pots, des ronds dessinés à la craie au sol.
    arbre(1.8,6.1,-.1,1.8,("feuille_ombre","feuille"))
    for x in (-3.3,-2.8):
        pilier(x,6.55,-.2,.22,.45,"tuile",.27)
    for i in range(5):
        pilier(.2+math.cos(i*1.26)*.9,4.9+math.sin(i*1.26)*.6,-.08,.18,.1,"creme")
    terminer(True)

    piece("Tuyau_Aube")
    # Gros tuyau des câbles de lanternes : il sort du mur de la cour et bouche le soupirail.
    # Un tronçon cassé, tombé à côté, laisse une ouverture à hauteur d'Aube.
    cx = (sx0+sx1)/2
    plancher=[(cx-.55,5.6,-.1),(cx+.55,5.6,-.1),(cx+.55,P/2,zc),(cx-.55,P/2,zc)]
    prisme([(x,y,z-.15) for x,y,z in plancher],plancher,"cuivre")
    for signe in (-1,1):
        boite(cx+signe*.62,(P/2+5.6)/2,-.2,.14,5.6-P/2,2.55,"cuivre")
    for y in (3.2,4.0,4.8,5.5):
        for signe in (-1,1):
            boite(cx+signe*.71,y,-.2,.06,.14,2.6,"ombre")
    boite(cx,6.88,-.2,1.38,.25,2.6,"cuivre")
    # Le tronçon tombé, couché dans l'herbe le long du muret.
    boite(-2.6,4.7,-.15,.8,1.3,.8,"cuivre")
    boite(-2.6,4.7,.65,.82,1.32,.06,"ombre")
    # Les câbles noirs qui montent vers les lanternes de la rue.
    for i in range(3):
        tige((cx-.3+i*.3,6.9,2.3),(cx-.6+i*.5,7.4,4.2),.035,"ombre")
    terminer(True)
    piece("Couvercle_tuyau_Aube")
    arc=[(cx-.69,2.35),(cx-.5,2.6),(cx,2.72),(cx+.5,2.6),(cx+.69,2.35)]
    for (xa,za),(xb,zb) in zip(arc,arc[1:]):
        panneau_rampant(xa,za+.1,xb,zb+.1,P/2,5.6,.12,"cuivre")
    for y in (3.2,4.0,4.8,5.5):
        for (xa,za),(xb,zb) in zip(arc,arc[1:]):
            panneau_rampant(xa,za+.16,xb,zb+.16,y-.07,y+.07,.06,"ombre")
    terminer()

modeles_fermes = {}
variantes_fermees = {
    "pignon": (5.5, 4.1, 3.95, "craie", "miel", "chene", "pignon"),
    "terrasse": (5.2, 3.9, 3.6, "peche", "saumon", "cuivre", "terrasse"),
    "contreforts": (5.2, 3.9, 6.05, "ocre", "tuile", "bois", "contreforts"),
    "balcon": (5.2, 3.9, 5.64, "craie", "toit_sauge", "chene", "balcon"),
}

def logis_de_decor(numero, centre, rotation, rive):
    variantes = ("terrasse", "pignon") if numero < 8 else ("contreforts", "balcon")
    # Alterner les silhouettes et décaler l'alternance entre les deux rangées.
    forme = variantes[(numero + (rive == "exterieure")) % 2]
    nom = f"Logis_{rive}_{numero:02d}_{forme}"
    maison_fermee(nom, centre, rotation, variantes_fermees[forme])

# Du quai occidental à la digue orientale, le profil passe par la crête nord.
hauteurs=[1,1.2,2,2.8,3.3,3.5,4.4,6.4,8.8,10,10,9.4,8.1,7.2,6,4.8,3.6,2,1]
# Sens horaire en plan, départ au sud-est. Miroir pour placer le départ à l'ouest.
def point(i, rayon, h):
    a=math.radians(angles[i])
    return (rayon*math.cos(a), rayon*.84*math.sin(a), h)
# Laisser une passe ouverte au sud entre les deux extrémités.
angles=[-99-i*342/(len(hauteurs)-1) for i in range(len(hauteurs))]
interieurs=[26,25,28,27,24,25,28,26,25,27,24,26,25,28,27,25,26,27,26]
exterieurs=[45,52,55,56,53,57,58,57,61,65,62,58,60,56,59,57,54,50,43]
friche = random.Random(872)
bandes = ((interieurs,[33]*19,"sable"), ([33]*19,[39]*19,"craie"), ([39]*19,exterieurs,"sauge"))

def quadrilatere(i, interieur, exterieur):
    j = i + 1
    return [point(i,interieur[i],hauteurs[i]), point(i,exterieur[i],hauteurs[i]),
            point(j,exterieur[j],hauteurs[j]), point(j,interieur[j],hauteurs[j])]

triangles_du_sol = []
for indice in range(len(angles)-1):
    triangles = []
    for interieur, exterieur, _ in bandes:
        a,b,c,d = map(Vector,quadrilatere(indice,interieur,exterieur))
        triangles.extend(((a,d,c),(a,c,b)))
    triangles_du_sol.append(triangles)
verticale = Vector((0,0,-1))

def sol_du_secteur(i, t, rayon, relief=.025):
    a = point(i, rayon, hauteurs[i])
    b = point(i+1, rayon, hauteurs[i+1])
    x, y, z = (a[k]+(b[k]-a[k])*t for k in range(3))
    depart = Vector((x,y,z+15))
    for triangle in triangles_du_sol[i]:
        impact = intersect_ray_tri(*triangle, verticale, depart, True)
        if impact is not None:
            return x, y, impact.z+relief
    return x, y, z+relief

def tache_au_sol(i, t, rayon, largeur, profondeur, couleur, relief=.025, cotes=7):
    contours = []
    for coin in range(cotes):
        a = coin*math.tau/cotes
        variation = friche.uniform(.72, 1.12)
        contours.append(sol_du_secteur(i, t+largeur*math.cos(a)*variation,
                        rayon+profondeur*math.sin(a)*variation, relief))
    morceau(contours, [tuple(range(cotes))], couleur)

def touffe(i, t, rayon, hauteur, nombre=7):
    x, y, z = sol_du_secteur(i,t,rayon)
    teintes = ("herbe_sombre", "herbe_olive", "herbe_tendre", "herbe_seche")
    for _ in range(nombre):
        a = friche.uniform(0, math.tau)
        dx, dy = math.cos(a), math.sin(a)
        h = hauteur*friche.uniform(.46,1)
        base_x, base_y = x+friche.uniform(-.13,.13), y+friche.uniform(-.13,.13)
        ecart = friche.uniform(.032,.072)
        points = [(base_x-dy*ecart,base_y+dx*ecart,z-.045),
                  (base_x+dy*ecart,base_y-dx*ecart,z-.045),
                  (base_x+dx*h*.24+dy*ecart*.55,base_y+dy*h*.24-dx*ecart*.55,z+h*.57),
                  (base_x+dx*h*.24-dy*ecart*.55,base_y+dy*h*.24+dx*ecart*.55,z+h*.57),
                  (base_x+dx*h*.58,base_y+dy*h*.58,z+h)]
        couleur = friche.choices(teintes, weights=(2,5,4,1))[0]
        morceau(points, [(0,1,2,3),(3,2,4)], couleur)

def rue_enfrichee(i):
    commencer(f"Rues_enfrichees_{i:02d}")
    for bord in (33.65,38.4):
        for position in (.14,.31,.49,.66,.84):
            t = position + friche.uniform(-.035,.035)
            r = bord+friche.uniform(-1.05,1.05)
            tache_au_sol(i,t,r,.085,friche.uniform(.38,.78),"terre_claire")
            tache_au_sol(i,t+.012,r+.16,.064,.42,"mousse",.036)
            for _ in range(friche.randint(4,8)):
                touffe(i,t+friche.uniform(-.064,.064),r+friche.uniform(-.64,.64),
                       friche.uniform(.26,.65))
        # Quelques pavés restent visibles entre les plaques d'herbe.
        for position in (.16,.37,.61,.85):
            t = position + friche.uniform(-.055,.055)
            r = bord + (36-bord)*friche.uniform(.22,.78)
            tache_au_sol(i,t,r,.043,.61,"fissure",.041,6)
            tache_au_sol(i,t-.004,r,.037,.54,"pave_use",.06,6)
            if friche.random() < .67:
                touffe(i,t+.043,r,friche.uniform(.20,.34),5)
    for t in (() if i == 0 else (friche.uniform(.2,.39), friche.uniform(.61,.8))):
        rayon = friche.uniform(39.1,41.3)
        tache_au_sol(i,t,rayon,.11,.85,"mousse_sombre")
        for _ in range(10):
            touffe(i,t+friche.uniform(-.09,.09),rayon+friche.uniform(-.66,.66),
                   friche.uniform(.28,.72))
    terminer()

def bordures_sauvages(i):
    commencer(f"Friche_des_talus_{i:02d}")
    for r, ext in ((max(interieurs[i:i+2])+.95, False),
                   (min(exterieurs[i:i+2])-1.06, True)):
        if ext and i == 0:
            continue
        for t in (.16,.35,.55,.75,.88):
            rayon = r+friche.uniform(-.23,.33)
            tache_au_sol(i,t,rayon,.091,.61,"mousse_sombre")
            for _ in range(7):
                touffe(i,t+friche.uniform(-.079,.079),rayon+friche.uniform(-.52,.52),
                       friche.uniform(.34,.86))
            if ext and r > 48 and friche.random() < .58:
                x,y,z = sol_du_secteur(i,t,rayon)
                taille = friche.uniform(.36,.79)
                pilier(x,y,z-.04,taille*.72,taille*.42,"herbe_sombre",taille)
                pilier(x,y,z+taille*.38,taille,taille*.73,"feuille",taille*.28)
    terminer()

for i in range(len(angles)-1):
    j=i+1
    commencer("Terrasse_%02d"%i)
    for ra,rb,couleur in bandes:
        pts=quadrilatere(i,ra,rb)
        morceau(pts,[(0,3,2),(0,2,1)],couleur)
    # Couronnes géologiques continues, y compris les coupes aux deux bouts de la passe.
    for rayons,sens in [(interieurs,1),(exterieurs,-1)]:
        for haut,bas,ton in [(0,-.65,"ocre"),(-.65,-2.4,"pierre"),(-2.4,-3.1,"sable"),(-3.1,-16,"strate")]:
            pts=[point(k,rayons[k],hauteurs[k]+z) for k,z in [(i,haut),(j,haut),(j,bas),(i,bas)]]
            morceau(pts,[(0,1,2,3) if sens==-1 else (3,2,1,0)],ton)
    for k in ([0] if i==0 else [j] if j==18 else []):
        pts=[point(k,r,hauteurs[k]+z) for r,z in [(interieurs[k],0),(exterieurs[k],0),(exterieurs[k],-16),(interieurs[k],-16)]]
        morceau(pts,[(0,1,2,3) if k==0 else (3,2,1,0)],"pierre")
    terminer(True)
    a=math.radians((angles[i]+angles[j])/2)
    z=(hauteurs[i]+hauteurs[j])/2
    def adresse(r):
        return (r*math.cos(a),r*.84*math.sin(a),z)
    angle_rue=math.atan2(math.sin(a)*.84,math.cos(a))-math.pi/2
    if i in (8,9,10):
        commencer("Verriere_%02d"%i)
        origine,angle=adresse(45),angle_rue
        boite(0,0,-1,11,7,1.5,"pierre")
        boite(0,0,.5,10.8,6.8,3.7,"verre")
        toit(0,0,4.2,11,7,2,"verre")
        for x in (-5.5,-3.3,-1.1,1.1,3.3,5.5):
            for y in (-3.45,3.45):
                boite(x,y,.5,.17,.2,3.8,"ardoise")
            toit(x,0,4.25,.19,7.15,2,"ardoise")
        terminer(True)
        commencer("Verger_%02d"%i)
        origine,angle=adresse(55),angle_rue
        arbre(-2,0,0,friche.uniform(2.2,3.5),("feuille_ombre","feuille"))
        tons_arbre = ("corail","rose") if i == 9 else ("herbe_olive","herbe_tendre")
        arbre(2,1,0,friche.uniform(2.9,4.4),tons_arbre)
        terminer()
    else:
        noms={0:"Maison_du_quai",3:"Maison_des_couturieres",4:"Ecole",5:"Maison_Aube",6:"Maison_de_la_cour",11:"Maison_des_verriers",12:"Maison_commune",13:"Maison_du_palier",14:"Maison_des_trois_soleils"}
        public=i in (4,12)
        largeur = 11 if public else hasard.uniform(6.4,8.7)
        enduit = hasard.choice(["ocre","craie","peche"])
        if i == 0:
            foyer_visitable((-8,-23.4,z),0)
        elif i == 3:
            foyer_visitable(adresse(45),angle_rue,atelier=True)
        elif i == 4:
            ecole(adresse(45),angle_rue)
        elif i == 5:
            maison_aube(adresse(45),angle_rue)
        elif i in noms:
            maison(noms[i], adresse(45), angle_rue, largeur, 7, 7 if public else 4.4+(i>10)*2,
                   enduit, "ardoise" if i>10 or public else "tuile", i>10 or public)
        else:
            logis_de_decor(i, adresse(45), angle_rue, "exterieure")
        if i == 12:
            commencer("Beffroi_civique")
            origine,angle=adresse(45),angle_rue
            boite(4,1,0,3.3,3.3,10.8,"craie")
            boite(4,1,10.8,3.8,3.8,.4,"cuivre")
            for dx in (-1.3,1.3):
                for dy in (-1.3,1.3):
                    boite(4+dx,1+dy,11.2,.32,.32,2.2,"ardoise")
            pilier(4,1,11.6,.82,1.2,"or",.48)
            toit(4,1,13.4,4.2,4.2,2.7,"ardoise")
            terminer(True)
        if 1<=i<=16 and i not in (4,12):
            logis_de_decor(i, adresse(30), angle_rue + math.pi, "lagon")
    commencer("Promenade_%02d"%i)
    origine,angle=adresse(36),angle_rue
    lumineux(-3,2.8,0)
    if 11<=i<=15:
        lumineux(2.8,2.8,0)
        lumineux(2.8,-2.8,0)
    for x in (-2.5,2.5):
        boite(x,-2,0,.35,.6,.75,"pierre")
    boite(0,-2,.75,5.5,.7,.18,"bois")
    terminer()
    rue_enfrichee(i)
    bordures_sauvages(i)
commencer("Ponton_du_carillon")
origine=(-8,-34,0)
boite(0,0,.48,4.4,15,.62,"bois")
for y in (-6,-2,2,6):
    for x in (-2.08,2.08):
        pilier(x,y,-2,.23,3.7,"bois")
        pilier(x,y,1.52,.26,.14,"creme")
terminer(True)

commencer("Planches_du_ponton")
origine=(-8,-34,0)
for i in range(27):
    boite(0,-7+i*.54,1.10,4.46,.51,.025,"ocre" if i%4==0 else "sable")
terminer()

commencer("Passerelle_de_la_maison_du_quai")
# Le tablier prolonge le ponton dans l'axe de la porte.
tablier = [(-9.16,-27.75,1.10),(-6.84,-27.75,1.10),
           (-6.84,-26.02,1.22),(-9.16,-26.02,1.22)]
prisme([(x,y,z-.24) for x,y,z in tablier],tablier,"bois")
terminer(True)

commencer("Planches_de_la_passerelle")
for i in range(6):
    boite(-8,-27.60+i*.285,1.11+i*.020,2.30,.272,.022,"sable" if i%3 else "ocre")
terminer()

commencer("Bagages_du_ponton")
origine=(-8,-34,1.1)
for x,y in [(-1.5,-2),(-1.4,-.8),(1.4,3)]:
    boite(x,y,0,.85,1.1,.7,"cuivre")
    for dy in (-.34,.34):
        boite(x,y+dy,.01,.87,.1,.71,"or")
terminer()

commencer("Carillon_des_marees")
origine=(-8,-34,1.1)
for x in (.75,1.90):
    boite(x,0,0,.15,.22,3.42,"chene")
    boite(x,0,0,.29,.31,.24,"pierre")
boite(1.325,0,3.36,1.57,.34,.23,"chene")
for i in range(3):
    x = .99+i*.335
    z = 2.20+i*.18
    pilier(x,0,z,.105,.62+i*.07,"or",.068)
    pilier(x,0,z+.62+i*.07,.025,3.36-z-.62-i*.07,"cuivre")
    pilier(x,0,z-.11,.041,.15,"bois")
terminer()

commencer("Echelle_de_maree")
origine=(-6.06,-36.67,0)
boite(0,0,-1.55,.43,.28,3.1,"chene")
boite(0,-.16,-1.34,.337,.055,2.79,"creme")
for i in range(8):
    z = -.76+i*.286
    boite(-.028,-.196,z,.205 if i%2==0 else .13,.022,.023,"ombre")
boite(0,-.199,1.22,.26,.026,.041,"or")
boite(-.038,-.199,-1.11,.195,.029,.033,"ombre")
lune = [(.083+.043*math.cos(i*math.tau/12),-1.02+.043*math.sin(i*math.tau/12)) for i in range(12)]
extrusion_facade(lune,-.216,-.196,"ombre")
terminer()
commencer("Port_englouti")
boite(0,0,-3.2,50,45,.35,"sable")
for x,y in [(-7,-6),(-7,3),(5,7),(6,-4)]:
    boite(x,y,-3,6,4,.55,"pierre")
    boite(x-2.8,y,-2.5,.4,4,1.7,"ocre")
    boite(x,y+1.8,-2.5,6,.4,1.2,"ocre")
for y in range(-10,11,2):
    boite(-1,y,-2.86,3.6,1.9,.18,"craie")
terminer(True)
commencer("Portes_de_l_ecluse")
for x in (-2,2):
    boite(x,-29,-3,1.1,8,4.6,"pierre")
    pilier(x,-29,1.6,.32,1.35,"ardoise")
boite(0,-29,-2.4,3.2,.5,3.4,"bois")
terminer(True)
commencer("Recifs_et_bancs_de_sable")
for i in range(18):
    a=math.radians(angles[i])
    for n in range(4):
        r=exterieurs[i]+hasard.uniform(.2,4.8)
        x=r*math.cos(a)+hasard.uniform(-2,2)
        y=r*.84*math.sin(a)+hasard.uniform(-2,2)
        largeur=hasard.uniform(.8,2.6)
        pilier(x,y,-1.7,largeur,hasard.uniform(1.7,3.2),"ocre" if n%3 else "pierre",largeur*.65)
terminer()
chemin=racine/"assets/models/ile03/colonie_du_lagon.glb"
bpy.ops.export_scene.gltf(filepath=str(chemin),export_format='GLB')
# Le plan d'eau du rendu est remplacé en jeu par une surface translucide.
commencer("Mer_de_presentation")
boite(0,0,-.35,500,500,.3,"mer")
terminer()
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(18,-116,115))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,2))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=135
camera.data.clip_end=500
scene.camera=camera
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.world=bpy.data.worlds.new("Ciel creme")
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs[0].default_value=(.86,.94,1,1)
scene.world.node_tree.nodes.get("Background").inputs[1].default_value=.85
bpy.ops.object.light_add(type='SUN',rotation=(.54,-.45,-.3))
bpy.context.object.data.energy=2.6
bpy.context.object.data.angle=.12
# L'eau laisse deviner les anciennes fondations à travers la surface.
eau=materiaux["mer"]
eau.use_nodes=True
noeuds=eau.node_tree
melange=noeuds.nodes.new("ShaderNodeMixShader")
melange.inputs[0].default_value=.33
transparent=noeuds.nodes.new("ShaderNodeBsdfTransparent")
noeuds.links.new(noeuds.nodes.get("Principled BSDF").outputs[0],melange.inputs[1])
noeuds.links.new(transparent.outputs[0],melange.inputs[2])
noeuds.links.new(melange.outputs[0],noeuds.nodes.get("Material Output").inputs[0])
noeuds.nodes.get("Principled BSDF").inputs["Base Color"].default_value=eau.diffuse_color
scene.view_settings.view_transform='AgX'
bpy.context.preferences.filepaths.save_version=0
scene.render.resolution_x=1500
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.filepath=str(dossier/"colonie_du_lagon.png")
bpy.ops.wm.save_as_mainfile(filepath=str(dossier/"colonie_du_lagon.blend"))
bpy.ops.render.render(write_still=True)
