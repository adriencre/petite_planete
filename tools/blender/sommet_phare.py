"""Monte du bureau à la salle des cartes puis à la galerie du Phare."""
import functools
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from phare_ile_02 import (RACINE_PHARE, SORTIE, anneau, boite, camera, collection, main,
                           mat, montant, mur, origine, piece, profil)
from bureau_iris import construire_bureau
from salle_machines_phare import construire_interieur
from escalier_phare import (VOLEE_BUREAU, VOLEE_CARTES, construire_plancher, construire_volee,
                            dans_tremie, debut_tremie, garde_corps_tremie, rayon_mur)

BUREAU = 4.10
CARTES = 8.95
GALERIE = 13.62
ANGLE_PORTE_CARTES = -13
OUVERTURE_ECHELLE = (690, 714)
# Rayon (sommet de l'octogone) du noyau de la salle des cartes : la volée tourne autour.
NOYAU = 1.55


def polaire(r, angle, z):
    a=math.radians(angle)
    return Vector((r*math.cos(a),r*math.sin(a),z))


def secteur(nom, angle_a, angle_b, r_int, r_ext, z_a, z_b, profondeur, matiere, groupe):
    dessus=[polaire(r_int,angle_a,z_a),polaire(r_ext,angle_a,z_a),
            polaire(r_ext,angle_b,z_b),polaire(r_int,angle_b,z_b)]
    return piece(nom,[v-Vector((0,0,profondeur)) for v in dessus]+dessus,matiere,groupe)


def construire_sommet(palette,racine,solides,collisions):
    ivoire,sable,creme,terre,toit,bronze,or_pale,nuit,ambre,bleu=palette
    bois=mat("Frêne des archives",(.43,.28,.17))
    livre=mat("Cuir bleu du registre",(.19,.29,.32))
    papier=mat("Tranches du registre",(.88,.74,.53))
    anciens=set(collisions.objects)
    groupe_salle=collection("Phare · cartes et archives")
    groupe_escalier=collection("Phare · montée des cartes")
    groupe_haut=collection("Phare · montée de la galerie")
    groupe_galerie=collection("Phare · plateforme sommitale")
    salle=origine("EtageCartes",(0,0,0),groupe_salle)
    montee=origine("MonteeCartes",(0,0,0),groupe_escalier)
    haut=origine("MonteeGalerie",(0,0,0),groupe_haut)
    galerie=origine("GalerieHaute",(0,0,0),groupe_galerie)
    for o in (salle,montee,haut,galerie):
        o.parent=racine
    construire_volee(VOLEE_BUREAU,creme,sable,bronze,groupe_escalier,collisions)
    # Côté intérieur, la volée longe le mur de la salle des cartes : pas de main courante.
    construire_volee(VOLEE_CARTES,creme,sable,bronze,groupe_haut,collisions,rampe_interieure=False)

    debut_cartes = set(groupe_salle.objects)
    avant_murs = set(collisions.objects)
    for cote in range(8):
        portions=[(0,.105),(.895,1)] if cote==2 else [(0,1)]
        for j,portion in enumerate(portions):
            mur(f"Cartes-mur-{cote}-{j}-colonly",NOYAU,NOYAU,CARTES,11.45,cote,portion,None,collisions)
            mur("Mur en coupe des cartes",NOYAU,NOYAU,CARTES,11.38,cote,portion,ivoire,groupe_salle)
        # Au-dessus du plafond, le noyau monte jusqu'à la galerie : la volée reste un couloir.
        mur("Noyau sous la galerie",NOYAU,NOYAU,11.38,GALERIE-.28,cote,(0,1),ivoire,groupe_salle)
        mur(f"Noyau-{cote}-colonly",NOYAU,NOYAU,11.38,GALERIE-.28,cote,(0,1),None,collisions)
    profil("Plafond de la salle des cartes",[(NOYAU-.25,11.30),(NOYAU-.25,11.45)],sable,groupe_salle)
    porte=origine("PorteCartes",(0,NOYAU*math.cos(math.pi/8)-.115,CARTES),groupe_salle)
    for x in (-.50,.50):
        boite("Jambage des cartes",(x,-.03,1.27),(.19,.35,2.53),creme,groupe_salle,.03).parent=porte
    boite("Linteau des cartes",(0,-.03,2.52),(1.19,.38,.22),creme,groupe_salle,.035).parent=porte
    vantail=boite("Vantail des archives",(0,0,1.20),(.98,.14,2.38),bois,groupe_salle,.06)
    vantail.parent=porte
    serrure=boite("Plaque de serrure",(.27,.084,1.19),(.15,.06,.24),bronze,groupe_salle,.021)
    serrure.parent=porte
    for sens in (-1, 1):
        boite("Cartouche des cartes", (0,.089*sens,1.81), (.87,.048,.28),
              bronze,groupe_salle,.028).parent=porte

    boite("Pupitre du registre",(0,-.62,10.02),(1.20,.62,.14),bois,groupe_salle,.043)
    boite("Pupitre-colonly",(0,-.62,9.46),(1.20,.60,1.03),None,collisions)
    boite("Reliure du registre",(0,-.62,10.125),(.71,.49,.066),livre,groupe_salle,.024)
    boite("Cabinet des rouleaux",(-.80,-.30,9.55),(.36,.80,1.15),bois,groupe_salle,.043)
    for y in (-.60,-.42,-.24):
        montant("Carte roulée",(-.80,y,10.13),(-.80,y,10.53),.076,papier,groupe_salle,8)

    # Rose des vents, à côté du pupitre. Les angles de navigation seront reliés aux îles.
    rose=origine("Rose des relèvements",(-1.08,-.38,10.78),groupe_salle)
    rose.rotation_euler.z=-math.pi/2
    panneau=boite("Panneau des relèvements",(0,0,0),(.83,.11,.86),sable,groupe_salle,.046)
    panneau.parent=rose
    for i in range(8):
        a=i*math.tau/8
        r=.31 if i%2==0 else .21
        branche=montant("Branche de la rose",(0,.068,0),(r*math.cos(a),.068,r*math.sin(a)),
                        .019,bronze,groupe_salle,5)
        branche.parent=rose
    marque=anneau("Cercle des relèvements",.33,.028,-.008,.008,bronze,groupe_salle,24)
    marque.location=(0,.074,0)
    marque.rotation_euler.x=math.pi/2
    marque.parent=rose

    # La porte fait face au débouché de la première volée, à 77 degrés.
    bpy.context.view_layer.update()
    orientation = Matrix.Rotation(math.radians(ANGLE_PORTE_CARTES), 4, "Z")
    for o in (set(groupe_salle.objects) - debut_cartes) | (set(collisions.objects) - avant_murs):
        if o.parent is None:
            o.matrix_world = orientation @ o.matrix_world
    porte.parent = racine
    # Le plafond et le haut du noyau ne servent qu'en 1re personne : la coupe les efface vue de dessus.
    coupe=bpy.data.objects["Coupe"]
    for o in list(groupe_salle.objects):
        if o.name.startswith(("Plafond de la salle des cartes","Noyau sous la galerie")):
            o.parent=coupe

    # Le plancher des cartes ferme le plafond du bureau ; il s'ouvre au-dessus de la volée.
    tremie = (debut_tremie(VOLEE_BUREAU, CARTES, .22), VOLEE_BUREAU[4])
    construire_plancher("Plancher des cartes", CARTES, .22, VOLEE_BUREAU[6], tremie, sable,
                        groupe_salle, collisions)
    garde_corps_tremie("Garde-corps des cartes", CARTES, VOLEE_BUREAU[6], tremie, bronze,
                       groupe_salle, collisions, cote_vide=False)

    coupe=bpy.data.objects["Coupe"]
    optique=bpy.data.collections["Phare · galerie et optique"]
    niveaux=bpy.data.collections["Phare · quatre niveaux"]
    for o in list(niveaux.objects):
        if o.name.startswith("Sommet"):
            bpy.data.objects.remove(o,do_unlink=True)
    for o in list(optique.objects):
        if o.name.startswith("Galerie · corniche"):
            bpy.data.objects.remove(o,do_unlink=True)
        elif o.name.startswith(("Galerie · main courante", "Galerie · câble tendu")):
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.name.startswith("Galerie · potelet") and o.location.x > 3.0 and -1.90 < o.location.y < -.60:
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.parent==coupe:
            o.parent=galerie
    # La galerie couvre la tour ; la trémie de la volée des cartes s'ouvre dans l'épaisseur du mur.
    haut_tremie, bas_tremie = debut_tremie(VOLEE_CARTES, GALERIE, .29), VOLEE_CARTES[4]
    BORD_TREMIE = 2.80
    bornes=sorted(set(list(range(0,361,3))+[t%360 for t in (haut_tremie,bas_tremie)]))
    for a,b in zip(bornes,bornes[1:]):
        ouvert=dans_tremie((a+b)/2,(haut_tremie,bas_tremie))
        # Au-dessus de la trémie, la dalle ne garde que l'anneau extérieur : la tête du robot
        # dépasse le haut du mur en arrivant.
        anneaux=[(BORD_TREMIE,BORD_TREMIE,3.79)] if ouvert \
            else [(1.50,1.50,3.79)]
        for r_a,r_b,r_ext in anneaux:
            dessus=[polaire(r_a,a,GALERIE),polaire(r_ext,a,GALERIE),polaire(r_ext,b,GALERIE),polaire(r_b,b,GALERIE)]
            for nom,matiere,groupe in (("Dalle de la galerie",creme,groupe_galerie),("Terrasse-colonly",None,collisions)):
                piece(nom,[v-Vector((0,0,.29)) for v in dessus]+dessus,matiere,groupe)
        if not OUVERTURE_ECHELLE[0] <= a+360 < OUVERTURE_ECHELLE[1]:
            secteur("Garde-corps du large-colonly",a,b,3.74,3.81,14.42,14.42,.77,None,collisions)
            # Main courante plate, lisse basse et socle de pierre ; balustres tous les 6°.
            secteur("Garde-corps · main courante",a,b,3.63,3.79,14.40,14.40,.06,bronze,groupe_galerie)
            secteur("Garde-corps · lisse basse",a,b,3.68,3.75,13.80,13.80,.05,bronze,groupe_galerie)
            secteur("Garde-corps · socle",a,b,3.64,3.80,13.71,13.71,.09,creme,groupe_galerie)
            if a % 6 == 0:
                montant("Garde-corps · balustre",polaire(3.715,a,13.80),polaire(3.715,a,14.34),
                        .021,or_pale,groupe_galerie,4)
    tremie=(haut_tremie,bas_tremie)
    garde_corps_tremie("Garde-corps de la trémie",GALERIE,BORD_TREMIE+.05,tremie,bronze,
                       groupe_galerie,collisions,radial=False)
    garde_corps_tremie("Garde-corps de la trémie",GALERIE,1.62,tremie,bronze,
                       groupe_galerie,collisions,cote_vide=False,r_ext=BORD_TREMIE+.05)
    boite("Seuil de l’échelle", (3.53,-1.25,GALERIE-.09), (.72,1.08,.18), creme,groupe_galerie,.02)
    boite("Seuil de l’échelle-colonly", (3.53,-1.25,GALERIE-.09), (.72,1.08,.18),None,collisions)
    profil("Pierre sous la couronne",[(1.63,13.39),(1.64,13.62)],sable,groupe_galerie,48)
    profil("Emprise de la mécanique-colonly",[(1.50,GALERIE),(1.50,14.70)],None,collisions,20)

    # La lunette donne sur le sud-ouest et le ravitailleur, au-delà de la sortie de l'escalier.
    pied=Vector((-2.62,-1.835,GALERIE))
    tete=pied+Vector((0,0,1.17))
    for i in range(3):
        sol=pied+polaire(.40,30+120*i,0)
        montant("Pied de la lunette",sol,tete,.032,bronze,groupe_galerie,5,.022)
        montant("Sabot de la lunette",sol,sol+Vector((0,0,.05)),.045,or_pale,groupe_galerie,5)
        milieu=sol.lerp(tete,.42)
        montant("Entretoise de la lunette",milieu,pied.lerp(tete,.42),.014,or_pale,groupe_galerie,4)
    profil("Tête du pied de la lunette",[(.05,1.10),(.10,1.16),(.09,1.21)],or_pale,groupe_galerie,8
           ).location=(pied.x,pied.y,GALERIE)
    # Le tube pivote autour de son point d'appui (Pivot de lunette_iris.tscn, 1,31 m au-dessus du pied).
    axe=pied+Vector((0,0,1.31))
    direction=Vector((-.50,-.86,.08)).normalized()
    for debut,fin,rayon,matiere,nom in (
            (-.80,-.70,.042,bronze,"Fût de la lunette · oculaire"),
            (-.70,-.46,.058,or_pale,"Fût de la lunette · tirage"),
            (-.46,.30,.082,toit,"Fût de la lunette"),
            (-.03,.03,.096,or_pale,"Fût de la lunette · collier"),
            (-.50,-.44,.094,or_pale,"Fût de la lunette · bague arrière"),
            (.28,.46,.108,or_pale,"Bague de l’objectif"),
            (.455,.462,.094,bleu,"Verre de la lunette")):
        montant(nom,axe+direction*debut,axe+direction*fin,rayon,matiere,groupe_galerie,10)
    montant("Fût de la lunette · fourche",axe-Vector((0,0,.10)),axe-Vector((0,0,.02)),.05,bronze,groupe_galerie,6)

    for groupe,pivot in ((groupe_salle,salle),(groupe_escalier,montee),(groupe_haut,haut),(groupe_galerie,galerie)):
        for o in list(groupe.objects):
            if o!=pivot and o.parent is None:
                o.parent=pivot
    for o in set(collisions.objects)-anciens:
        o.parent=solides


def vues_sommet(scene,photos,robot,_vues):
    for o in bpy.data.objects["Coupe"].children_recursive:
        o.hide_render=True
        o.hide_set(True)
    robot.location=RACINE_PHARE+Vector((2.48,.72,GALERIE))
    vue=camera("Coupe verticale du Phare",RACINE_PHARE+Vector((18,-26,24)),
                RACINE_PHARE+Vector((0,0,8.8)),38,photos)
    sommet=camera("Lentille et galerie",RACINE_PHARE+Vector((8,-13,22.3)),
                  RACINE_PHARE+Vector((0,0,15.20)),52,photos)
    cartes=camera("Salle des cartes",RACINE_PHARE+Vector((2.34,-4.78,12.85)),
                  RACINE_PHARE+Vector((-.15,-.15,9.73)),36,photos)
    scene.camera=vue
    scene.render.filepath="//phare_coupe_verticale.png"
    return [(vue,"phare_coupe_verticale"),(sommet,"phare_galerie"),(cartes,"phare_salle_des_cartes")]


if __name__=="__main__":
    etage=functools.partial(construire_bureau,suite=construire_sommet)
    main(sortie=SORTIE.with_name("phare_ile_02_sommet"),
         variante=functools.partial(construire_interieur,etage=etage),cadrages=vues_sommet)
