"""Monte du bureau à la salle des cartes puis à la galerie du Phare."""
import functools
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from phare_ile_02 import (RACINE_PHARE, SORTIE, anneau, boite, camera, collection, main,
                           mat, montant, mur, origine, piece, profil)
from bureau_iris import construire_bureau
from salle_machines_phare import construire_interieur

BUREAU = 4.10
CARTES = 8.95
GALERIE = 13.62


def polaire(r, angle, z):
    a=math.radians(angle)
    return Vector((r*math.cos(a),r*math.sin(a),z))


def secteur(nom, angle_a, angle_b, r_int, r_ext, z_a, z_b, profondeur, matiere, groupe):
    dessus=[polaire(r_int,angle_a,z_a),polaire(r_ext,angle_a,z_a),
            polaire(r_ext,angle_b,z_b),polaire(r_int,angle_b,z_b)]
    return piece(nom,[v-Vector((0,0,profondeur)) for v in dessus]+dessus,matiere,groupe)


def escalier(groupe, physiques, depart, arrivee, bas, haut, clair, pierre, bronze,
             ouverture_debut, ouverture_fin):
    nombre=math.ceil((haut-bas)/.22)
    for i in range(nombre):
        a=depart+(arrivee-depart)*i/nombre
        b=depart+(arrivee-depart)*(i+1)/nombre
        za=bas+(haut-bas)*i/nombre
        zb=bas+(haut-bas)*(i+1)/nombre
        secteur("Marche rayonnante",a,b,1.62,2.89,zb,zb,.235,clair if i%4 else pierre,groupe)
        secteur("Rampe rayonnante-colonly",a,b,1.62,2.89,za,zb,.18,None,physiques)
        for r in (1.64,2.86):
            if r<2 and ((ouverture_debut and i<2) or (ouverture_fin and i>=nombre-2)):
                continue
            montant("Main courante cintrée",polaire(r,a,za+1.02),polaire(r,b,zb+1.02),.047,bronze,groupe,5)
            if i%3==0:
                montant("Potelet",polaire(r,a,za+.04),polaire(r,a,za+1.02),.041,bronze,groupe,5)
            secteur("Garde-corps rayonnant-colonly",a,b,r-.048,r+.048,za+1.02,zb+1.02,.96,None,physiques)
    # Le noyau ouvert reçoit le bâti de la chaîne à l'extérieur de la circulation.


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
    escalier(groupe_escalier,collisions,200,437,BUREAU,CARTES,creme,sable,bronze,True,True)
    escalier(groupe_haut,collisions,463,740,CARTES,GALERIE,creme,sable,bronze,True,True)

    # Les deux volées partagent ce palier. La porte se trouve en retrait, face au nord.
    for a in range(437,463,2):
        secteur("Dalle du palier des cartes",a,a+2,1.26,2.89,CARTES-.012,CARTES-.012,.20,creme,groupe_salle)
        secteur("Palier des cartes-colonly",a,a+2,1.26,2.89,CARTES,CARTES,.20,None,collisions)
    for a in range(437,463,3):
        b=min(a+3,463)
        secteur("Balustrade du palier des cartes-colonly",a,b,2.84,2.91,9.96,9.96,.91,None,collisions)
        montant("Balustrade du palier",polaire(2.87,a,9.96),polaire(2.87,b,9.96),.053,bronze,groupe_salle,5)
    profil("Plancher de la salle des cartes",[(1.73,8.76),(1.73,CARTES)],sable,groupe_salle)
    profil("Cartes-sol-colonly",[(1.73,8.76),(1.73,CARTES)],None,collisions)
    for cote in range(8):
        portions=[(0,.105),(.895,1)] if cote==2 else [(0,1)]
        for j,portion in enumerate(portions):
            mur(f"Cartes-mur-{cote}-{j}-colonly",1.77,1.77,CARTES,11.45,cote,portion,None,collisions)
            if cote in (0,1,2,3,4,5):
                mur("Mur en coupe des cartes",1.77,1.77,CARTES,11.38,cote,portion,ivoire,groupe_salle)
    for x in (-.56,.56):
        boite("Jambage des cartes",(x,1.49,10.22),(.23,.35,2.53),creme,groupe_salle,.03)
    boite("Linteau des cartes",(0,1.49,11.47),(1.35,.38,.22),creme,groupe_salle,.035)
    porte=origine("PorteCartes",(0,1.52,CARTES),groupe_salle)
    vantail=boite("Vantail des archives",(0,0,1.20),(.98,.14,2.38),bois,groupe_salle,.06)
    vantail.parent=porte
    serrure=boite("Plaque de serrure",(.27,.084,1.19),(.15,.06,.24),bronze,groupe_salle,.021)
    serrure.parent=porte

    boite("Pupitre du registre",(0,-.71,10.02),(1.42,.66,.14),bois,groupe_salle,.043)
    boite("Pupitre-colonly",(0,-.71,9.46),(1.42,.64,1.03),None,collisions)
    boite("Reliure du registre",(0,-.71,10.125),(.71,.49,.066),livre,groupe_salle,.024)
    for x in (-.175,.175):
        page=boite("Page du registre",(x,-.71,10.177),(.334,.454,.045),papier,groupe_salle,.016)
        page.rotation_euler.y=math.radians(x*22)
        for y in (-.82,-.76,-.70,-.64,-.58):
            boite("Ligne portée au registre",(x,y,10.207),(.23,.012,.002),bois,groupe_salle)
    boite("Cabinet des rouleaux",(-.91,-.36,9.55),(.40,.90,1.15),bois,groupe_salle,.043)
    for y in (-.60,-.42,-.24):
        montant("Carte roulée",(-.91,y,10.13),(-.91,y,10.53),.076,papier,groupe_salle,8)

    # Rose des vents, à côté du pupitre. Les angles de navigation seront reliés aux îles.
    rose=origine("Rose des relèvements",(-1.17,-.38,10.78),groupe_salle)
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

    coupe=bpy.data.objects["Coupe"]
    optique=bpy.data.collections["Phare · galerie et optique"]
    niveaux=bpy.data.collections["Phare · quatre niveaux"]
    for o in list(niveaux.objects):
        if o.name.startswith("Sommet"):
            bpy.data.objects.remove(o,do_unlink=True)
    for o in list(optique.objects):
        if o.name.startswith("Galerie · corniche"):
            bpy.data.objects.remove(o,do_unlink=True)
        elif o.parent==coupe:
            o.parent=galerie
    # Le passage de l'escalier reste ouvert sous la galerie, avec un anneau extérieur continu.
    for a in range(380,740,6):
        b=a+6
        trémie=a>=590
        r_int=2.88 if trémie else 1.61
        secteur("Dalle rayonnante de la galerie",a,b,r_int,3.79,GALERIE,GALERIE,.29,creme,groupe_galerie)
        secteur("Terrasse-colonly",a,b,r_int,3.79,GALERIE,GALERIE,.28,None,collisions)
        secteur("Garde-corps du large-colonly",a,b,3.74,3.81,14.42,14.42,.77,None,collisions)
        # À la fin de l'escalier, l'ouverture reste libre pour accéder à l'anneau.
        if trémie and b<=728:
            secteur("Bord de la trémie-colonly",a,b,2.89,2.96,14.42,14.42,.76,None,collisions)
            montant("Main courante de la trémie",polaire(2.92,a,14.42),polaire(2.92,b,14.42),
                    .058,bronze,groupe_galerie,5)
    profil("Pierre sous la couronne",[(1.63,13.39),(1.64,13.62)],sable,groupe_galerie,48)
    profil("Emprise de la mécanique-colonly",[(1.70,13.52),(1.70,14.70)],None,collisions,20)

    # La lunette donne sur le sud-ouest et le ravitailleur, à côté du passage de service.
    pied=Vector((-1.63,-2.43,GALERIE))
    for dx,dy in ((-.35,.06),(.27,-.22),(.13,.35)):
        montant("Pied de la lunette",pied+Vector((dx,dy,0)),pied+Vector((0,0,1.22)),.057,bronze,groupe_galerie)
    axe=pied+Vector((0,0,1.31))
    direction=Vector((-.50,-.86,.08)).normalized()
    montant("Fût de la lunette",axe-direction*.36,axe+direction*.61,.13,toit,groupe_galerie,10)
    montant("Bague de l’objectif",axe+direction*.58,axe+direction*.72,.172,or_pale,groupe_galerie,12)
    montant("Verre de la lunette",axe+direction*.72,axe+direction*.73,.145,bleu,groupe_galerie,12)

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
