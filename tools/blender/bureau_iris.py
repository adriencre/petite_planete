"""Ajoute le bureau au Phare et rend l'étage à la caméra du robot."""
import functools
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import (RACINE_PHARE, SORTIE, boite, camera, collection, lumiere, main, mat,
                           montant, mur, origine, profil)
from salle_machines_phare import construire_interieur, empreinte


def construire_bureau(palette, racine, solides, collisions, suite=None):
    ivoire, sable, creme, terre, toit, bronze, or_pale, nuit, _, bleu = palette
    groupe = collection("Phare · bureau d’Iris")
    bureau = origine("EtageIris", (0,0,0), groupe)
    bureau.parent = racine
    bois = mat("Frêne miel du bureau", (.50,.34,.19))
    bois_fonce = mat("Veines brunes du frêne", (.31,.19,.10))
    papier = mat("Papier crème des relevés", (.94,.83,.64))
    encre = mat("Encre brune des relevés", (.35,.24,.15))
    tissu = mat("Tissu lavande des dossiers", (.38,.31,.40))
    sol = 4.10
    nouvelles_collisions = set(collisions.objects)

    # Le palier s'ouvre vers la tour. La bordure suit le vide de l'escalier.
    boite("Passage du palier au bureau", (3.59,-1.65,4.015),(2.08,1.00,.17),sable,groupe,.028)
    boite("Passage-colonly",(3.59,-1.65,4.015),(2.08,1.00,.17),None,collisions)
    profil("Dalle octogonale du bureau", [(3.41,3.94),(3.43,4.05),(3.38,sol)],
           ivoire,groupe)
    profil("Bureau-sol-colonly", [(3.40,3.94),(3.40,sol)],None,collisions)
    for cote in range(8):
        # À l'est, l'ouverture diagonale est alignée sur le passage de l'escalier.
        portions = [(0,1)]
        if cote == 7:
            portions = [(0,.52)]
        elif cote == 0:
            portions = [(.23,1)]
        for i,portion in enumerate(portions):
            mur(f"Bureau-mur-{cote}-{i}-colonly",3.62,3.50,sol,6.15,cote,portion,None,collisions)
            if cote in (1,3,4):
                mur("Mur en coupe du bureau",3.54,3.50,sol,5.94,cote,portion,ivoire,groupe)
                mur("Plinthe couleur terre cuite",3.55,3.55,4.19,4.32,cote,portion,terre,groupe)
    # La baie de veille ouvre également la façade extérieure côté Large.
    coque = bpy.data.collections["Phare · enveloppe"]
    coupe = bpy.data.objects["Coupe"]
    bpy.context.view_layer.update()
    for o in list(coque.objects):
        if o.name.startswith("Assise taillée"):
            c = empreinte(o)
            if abs(c.x) < .2 and c.y > 3.0 and 5.9 < c.z < 6.4:
                bpy.data.objects.remove(o, do_unlink=True)
    for bas, haut, portions in [
        (4.84,5.02,[(0,1)]), (5.02,6.06,[(0,.21),(.79,1)]), (6.06,7.42,[(0,1)]),
    ]:
        rb = 3.62-(bas-4.84)*.17/2.58
        rh = 3.62-(haut-4.84)*.17/2.58
        for portion in portions:
            mur("Assise autour de la baie du Large",rb,rh,bas,haut,2,portion,ivoire,coque).parent=coupe
    # La baie est lisible dans la coupe depuis le bureau.
    mur("Allège de la baie du Large",3.54,3.54,sol,4.97,2,(0,1),ivoire,groupe)
    for segment in [(0,.21),(.79,1)]:
        mur("Piédroit de la baie du Large",3.54,3.54,4.97,6.15,2,segment,ivoire,groupe)
    boite("Appui vers le Large",(0,3.10,4.97),(1.72,.44,.14),creme,groupe,.043)
    boite("Vitre du Large",(0,3.05,5.50),(1.50,.057,1.06),bleu,groupe,.022)
    boite("Traverse de la baie",(0,3.02,5.63),(1.60,.095,.054),bronze,groupe,.018)
    for x in (-.48,.48):
        boite("Meneau de la baie",(x,3.02,5.52),(.079,.101,1.14),creme,groupe,.019)
    for x,t in [(3.56,1.85),(5.37,1.54)]:
        boite("Bord du palier-colonly",(x,-2.18,4.62),(t,.09,1.04),None,collisions)
    for x in (2.92,3.57,4.19):
        montant("Potelet du passage", (x,-2.17,4.10),(x,-2.17,4.95),.045,bronze,groupe)
    montant("Main courante du passage", (2.91,-2.17,4.95),(4.32,-2.17,4.95),.064,bronze,groupe,6)
    boite("Bord intérieur du palier-colonly",(3.80,-1.10,4.63),(1.55,.072,1.06),None,collisions)
    boite("Bord est du palier-colonly",(6.14,-1.65,4.63),(.11,.99,1.06),None,collisions)

    # La porte indique la chambre. Son accès par la lucarne sera fait depuis la galerie.
    boite("Refend gauche de la chambre",(2.83,-.87,5.47),(.49,.32,2.73),ivoire,groupe,.035)
    boite("Refend droit de la chambre",(4.54,-.87,5.47),(.18,.32,2.73),ivoire,groupe,.033)
    boite("Encadrement de la chambre",(3.75,-.91,5.45),(1.48,.24,2.70),creme,groupe,.056)
    boite("Porte de la chambre d’Iris",(3.75,-1.06,5.36),(1.20,.14,2.49),bois_fonce,groupe,.046)
    for x in (3.38,3.68,3.98):
        boite("Planche de la porte",(x,-1.14,5.35),(.23,.032,2.37),bois,groupe,.014)
    montant("Loquet de la chambre",(4.12,-1.12,5.35),(4.12,-1.27,5.35),.065,bronze,groupe)
    o=boite("Dessin épinglé d’Aube",(3.68,-1.163,5.84),(.34,.018,.29),papier,groupe,.011)
    o.rotation_euler.y=math.radians(-7)
    for x,z in [(3.62,5.82),(3.75,5.86)]:
        montant("Trait du dessin", (x,-1.177,z-.06),(x+.04,-1.177,z+.06),.008,encre,groupe,5)

    # Iris travaille face au large. Le côté sud de la table reste libre pour les lectures.
    boite("Table des relevés",(-.22,1.13,5.38),(3.04,1.18,.16),bois,groupe,.060)
    for x in (-1.48,1.03):
        for y in (.70,1.56):
            boite("Pied de la table",(x,y,4.73),(.19,.19,1.21),bois_fonce,groupe,.026)
    boite("Table-colonly",(-.22,1.13,4.77),(3.00,1.09,1.34),None,collisions)
    for i,(x,y,l,h) in enumerate([(-1.23,.89,.48,.32),(-.35,.91,.52,.37),
                                     (.42,.75,.50,.32),(.87,1.22,.30,.22)]):
        feuille=boite("Relevé d’Iris",(x,y,5.469),(l,h,.016),papier,groupe,.011)
        feuille.rotation_euler.z=math.radians((-1)**i*(4+2*i))
        for j in range(3):
            boite("Ligne d’encre",(x-.025,y-.071+j*.06,5.48),(l*.66,.012,.003),encre,groupe)
    boite("Tiroir des observations",(-1.07,1.07,5.19),(1.17,.97,.24),bois_fonce,groupe,.032)
    montant("Poignée du tiroir",(-1.20,.565,5.18),(-.95,.565,5.18),.035,bronze,groupe)
    boite("Banquette sous la fenêtre",(-1.55,2.17,4.72),(1.62,.59,.19),bois,groupe,.043)
    boite("Coussin lavande",(-1.55,2.17,4.84),(1.39,.50,.11),tissu,groupe,.034)
    boite("Banquette-colonly",(-1.55,2.17,4.46),(1.56,.54,.72),None,collisions)
    for i in range(6):
        boite("Dossier fermé",(.91+.14*i,2.11,5.29),(.104,.38,.57),tissu if i%3 else terre,groupe,.015)
    boite("Console des archives",(1.28,2.14,4.96),(1.06,.55,.16),bois,groupe,.031)
    boite("Console-colonly",(1.28,2.14,4.55),(1.06,.53,.91),None,collisions)
    profil("Tasse d’Iris",[(.12,5.47),(.135,5.51),(.16,5.72),(.132,5.72),(.10,5.53)],
           bleu,groupe,10).location=(.28,1.49,0)
    boite("Presse-papiers en bronze",(-.35,1.26,5.52),(.25,.19,.10),or_pale,groupe,.028)

    for o in list(groupe.objects):
        if o!=bureau:
            o.parent=bureau
    for o in set(collisions.objects)-nouvelles_collisions:
        o.parent=solides
    if suite:
        suite(palette, racine, solides, collisions)


def cadrages_bureau(scene, photos, robot, _vues):
    for o in bpy.data.objects["Coupe"].children_recursive:
        o.hide_render=True
        o.hide_set(True)
    robot.location=RACINE_PHARE+Vector((.13,-.87,4.10))
    lampe=lumiere("Lumière douce du bureau","AREA",170,(1,.83,.59),
                  RACINE_PHARE+Vector((1.7,-1.0,10)),RACINE_PHARE+Vector((0,0,4.1)),photos)
    lampe.size=5
    angle=math.radians(40)
    cible=robot.location+Vector((0,0,1))
    jeu=camera("Caméra de jeu au bureau",cible+Vector((0,-9*math.cos(angle),9*math.sin(angle))),
               cible,28,photos)
    jeu.data.sensor_fit="VERTICAL"
    jeu.data.sensor_height=32
    jeu.data.lens=16/math.tan(math.radians(30))
    vue=camera("Coupe du bureau et de son palier",RACINE_PHARE+Vector((10,-15,17)),
               RACINE_PHARE+Vector((1.75,-.08,4.77)),51,photos)
    scene.camera=vue
    scene.render.filepath="//coupe_bureau_iris.png"
    return [(vue,"coupe_bureau_iris"),(jeu,"bureau_iris_camera_jeu")]


if __name__=="__main__":
    main(sortie=SORTIE.with_name("phare_ile_02_bureau"),
         variante=functools.partial(construire_interieur,etage=construire_bureau),cadrages=cadrages_bureau)
