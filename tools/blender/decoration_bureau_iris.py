"""Habille le bureau avec les dix références Meshy et les documents du jeu."""
import functools
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import (RACINE, RACINE_PHARE, SORTIE, boite, camera, cercle, collection, importer,
                           lumiere, main, mat, montant, objet, origine)
from phare_ile_02_v2 import retirer
from salle_machines_phare import construire_interieur
from bureau_iris import construire_bureau, cadrages_bureau
from chambre_iris import construire_chambre
from sommet_phare import construire_sommet

SOURCES = RACINE / "tools/blender/sources/bureau_iris"
SOL = 4.10
TABLE = 5.46


def teinte(nom, x, y, z):
    """Aplats sur les pièces sculptées, définis dans leur boîte locale normalisée."""
    if nom == "siege":
        if z < .076 or z > .92:
            return "nacre"
        if .23 < x < .77 and ((.31 < z < .43 and .14 < y < .87) or
                              (.41 <= z < .635 and .44 < y < .865)):
            return "lavande"
    elif nom == "banquette":
        if .12 < x < .88 and .49 < z < .78 and .19 < y < .86:
            return "lavande"
    elif nom == "meuble_cartes":
        if x > .60 and .23 < z < .81 and y < .44:
            return "ardoise"
        if .10 < x < .57 and y < .47 and (.31 < z < .42 or .56 < z < .65):
            return "papier"
    elif nom == "porte_manteau":
        if .24 < x < .79 and .14 < z < .848:
            return "ocre"
        if z>.90 and .22<x<.83:
            return "bronze"
    elif nom == "etagere":
        if z > .29:
            return "lavande" if x<.58 else "ardoise"
        if z < .11:
            return "bronze"
    elif nom == "lampe":
        if .51 < z < .655 and y < .44:
            return "ambre"
        if z > .66:
            return "ardoise"
        return "nacre" if z < .18 else "bronze"
    elif nom == "tasse":
        return "nacre" if z>.83 and x<.76 else "ardoise"
    elif nom == "presse_papiers":
        if z>.34:
            return "ambre"
        return "nacre" if z < .11 else "bronze"
    elif nom == "carnets":
        if z < .12 and y < .37:
            return "bois"
        if .44 < x < .59 and y < .56:
            return "nacre"
        if y < .43 and (.20<z<.30 or .45<z<.55 or .72<z<.84):
            return "papier"
        return "lavande" if z>.68 or z<.42 else "ardoise"
    elif nom == "table" and y<.17 and .67<z<.82 and (.28<x<.39 or .62<x<.73):
        return "bronze"
    return "bois"


def placer(nom, etiquette, position, dimensions, angle, materiaux, groupe, parent):
    objets = importer(SOURCES / (nom + ".glb"), groupe)
    maillages = [o for o in objets if o.type == "MESH"]
    if len(maillages)!=1:
        raise RuntimeError(f"{nom} doit avoir un maillage unique.")
    o = maillages[0]
    bpy.context.view_layer.update()
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world.identity()
    for autre in objets-{o}:
        bpy.data.objects.remove(autre, do_unlink=True)
    sommets = [v.co.copy() for v in o.data.vertices]
    minimum = Vector(tuple(min(v[i] for v in sommets) for i in range(3)))
    maximum = Vector(tuple(max(v[i] for v in sommets) for i in range(3)))
    taille = maximum-minimum
    classes = list(materiaux)
    o.data.materials.clear()
    for m in materiaux.values():
        o.data.materials.append(m)
    for p in o.data.polygons:
        c = sum((sommets[i] for i in p.vertices), Vector()) / len(p.vertices)
        x,y,z = ((c[i]-minimum[i])/taille[i] for i in range(3))
        p.material_index = classes.index(teinte(nom,x,y,z))
        p.use_smooth=False
    for v in o.data.vertices:
        normalise = [(v.co[i]-minimum[i])/taille[i] for i in range(3)]
        v.co=[(normalise[i]-(.5 if i<2 else 0))*dimensions[i] for i in range(3)]
    o.data.update()
    o.name=etiquette
    o.parent=parent
    o.location=position
    o.rotation_euler=(0,0,math.radians(angle))
    o["source"]="Meshy T2.5"
    o["reference"]=nom
    return o


def dalles_bureau(groupe,parent):
    """Découpe chaque dalle dans le contour octogonal, en gardant un joint fin."""
    contour = [v.xy for v in cercle(3.32,0)]
    couleurs=[mat("Pierre chaude du sol "+str(i),c) for i,c in enumerate([
        (.73,.63,.49),(.69,.58,.45),(.77,.67,.54),(.73,.64,.53)])]
    for rang in range(-4,5):
        for colonne in range(-4,5):
            x=colonne*.94+(.45 if rang%2 else 0)
            y=rang*.79
            polygone=[Vector((x+dx,y+dy)) for dx,dy in
                      ((.07,.013),(.87,.013),(.927,.06),(.927,.73),
                       (.87,.777),(.07,.777),(.013,.73),(.013,.06))]
            for a,b in zip(contour,contour[1:]+contour[:1]):
                if not polygone:
                    break
                precedent=polygone[-1]
                distance_precedente=(b-a).cross(precedent-a)
                coupe=[]
                for point in polygone:
                    distance=(b-a).cross(point-a)
                    if (distance>=0)!=(distance_precedente>=0):
                        t=distance_precedente/(distance_precedente-distance)
                        coupe.append(precedent.lerp(point,t))
                    if distance>=0:
                        coupe.append(point)
                    precedent=point
                    distance_precedente=distance
                polygone=coupe
            if len(polygone)<3:
                continue
            points=[(v.x,v.y,SOL+.012) for v in polygone]
            o=objet("Dalle taillée",points,[tuple(range(len(points)))],
                    couleurs[(rang*3+colonne*7+rang*colonne)%4],groupe)
            o.parent=parent


def decorer(palette,racine,solides,collisions):
    groupe=collection("Phare · mobilier et accessoires d’Iris")
    ancien=bpy.data.collections["Phare · bureau d’Iris"]
    bureau=bpy.data.objects["EtageIris"]
    calcaire, sable, creme, terre, toit, bronze, or_pale, nuit, ambre, bleu=palette
    retirer(ancien,("Table des relevés","Pied de la table","Tiroir des observations","Poignée du tiroir",
                   "Relevé d’Iris","Ligne d’encre","Banquette sous la fenêtre","Coussin lavande",
                   "Dossier fermé","Console des archives","Tasse d’Iris","Presse-papiers en bronze",
                   "Trait du dessin"))
    retirer(collisions,("Banquette-colonly","Console-colonly"))
    matieres={
        "bois":mat("Frêne miel du mobilier",(.65,.405,.196)),
        "lavande":mat("Lavande des étoffes",(.45,.28,.48)),
        "ardoise":mat("Bleu ardoise du bureau",(.17,.26,.38),.14,.64),
        "ocre":mat("Ocre du ciré de quart",(.75,.41,.089),0,.69),
        "nacre":creme,
        "papier":mat("Crème des feuillets",(.89,.77,.54)),
        "bronze":bronze,
        "ambre":mat("Ambre du presse-papiers",(.83,.41,.087),.20,.35),
    }
    inventaire=[
        ("table","Table des relevés",(-.22,1.13,SOL),(3.04,1.18,1.36),0,None),
        ("siege","Siège de veille en côtes",(1.03,-.05,SOL),(.74,.83,1.56),154,(.72,.78,.75)),
        ("banquette","Banquette lavande",(2.40,.49,SOL),(1.54,.52,.74),-93,(1.58,.49,.62)),
        ("meuble_cartes","Meuble des cartes roulées",(-2.40,1.02,SOL),(1.34,.53,.93),73,(1.26,.47,.89)),
        ("porte_manteau","Porte-manteau et ciré de quart",(1.91,2.00,SOL),(.86,.43,1.67),-27,(.81,.38,1.52)),
        ("etagere","Étagère d’archives",(-1.87,2.03,5.42),(1.28,.36,.72),20,None),
        ("lampe","Lampe mécanique d’Iris",(.89,1.42,TABLE),(.34,.48,.55),24,None),
        ("tasse","Tasse bleue",(.34,1.51,TABLE),(.24,.177,.17),0,None),
        ("presse_papiers","Presse-papiers d’ambre",(-.35,1.46,TABLE),(.211,.204,.18),0,None),
        ("carnets","Carnets et crayon",(-1.15,1.43,TABLE),(.56,.41,.24),-8,None),
    ]
    for nom,etiquette,pos,dim,angle,forme in inventaire:
        placer(nom,etiquette,pos,dim,angle,matieres,groupe,bureau)
        if forme:
            bloc=boite(f"Mobilier {nom}-colonly",(pos[0],pos[1],pos[2]+forme[2]/2),
                       forme,None,collisions)
            bloc.rotation_euler.z=math.radians(angle)
            bloc.parent=solides
    dalles_bureau(groupe,bureau)
    construire_chambre(palette,racine,solides,collisions)
    construire_sommet(palette,racine,solides,collisions)


def vues_meublees(scene,photos,robot,vues):
    cadrages_bureau(scene,photos,robot,vues)
    for nom in ("EtageCartes","MonteeGalerie","GalerieHaute"):
        for o in bpy.data.objects[nom].children_recursive:
            o.hide_render=True
            o.hide_set(True)
    # Cadrage de décoration : seule la volée au-dessus du bureau est en coupe.
    for o in bpy.data.objects["MonteeCartes"].children_recursive:
        o.hide_render=True
        o.hide_set(True)
    vue=camera("Bureau meublé à la lumière du Large",
               RACINE_PHARE+Vector((6.45,-9.2,13.5)),
               RACINE_PHARE+Vector((.12,.78,4.92)),57,photos)
    scene.camera=vue
    scene.cycles.samples=18
    scene.render.filepath="//bureau_iris_meuble_blender.png"
    robot.hide_render=True
    for o in robot.children_recursive:
        o.hide_render=True
    lampe=lumiere("Lumière marine par la baie","AREA",290,(1,.89,.70),
                  RACINE_PHARE+Vector((-.55,4.36,7.1)),
                  RACINE_PHARE+Vector((-.28,.38,4.38)),photos)
    lampe.size=3.0
    return [(vue,"bureau_iris_meuble_blender")]


if __name__=="__main__":
    etage=functools.partial(construire_bureau,suite=decorer)
    main(sortie=SORTIE.with_name("bureau_iris_meuble"),
         variante=functools.partial(construire_interieur,etage=etage),cadrages=vues_meublees)
