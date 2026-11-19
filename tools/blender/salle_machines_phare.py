"""Parvis, salle des machines et escalier du Phare. Lance Blender, pas Godot.

Exécution : blender -b --python tools/blender/salle_machines_phare.py
Produit le modèle Godot et un aperçu de la coupe dans concept/phare_ile_02_rez/.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import (MODELES, RACINE_PHARE, SORTIE, anneau, boite, camera, collection,
                           lumiere, main, mat, montant, mur, origine, piece, profil)
from phare_ile_02_v2 import reconstruire, retirer


def empreinte(objet):
    """Centre local du maillage, pour regrouper les assises en coupe."""
    return objet.matrix_local @ (sum((Vector(p) for p in objet.bound_box), Vector()) / 8)


def pente(nom, x0, x1, y0, y1, z0, z1, groupe):
    """Faces fermées, sommet orienté vers le haut pour la collision."""
    bas_y, haut_y = sorted((y0,y1))
    bas_z, haut_z = (z0,z1) if y0 < y1 else (z1,z0)
    dessus = [(x0,bas_y,bas_z), (x1,bas_y,bas_z),
              (x1,haut_y,haut_z), (x0,haut_y,haut_z)]
    return piece(nom, [(x,y,z-.16) for x,y,z in dessus]+dessus, None, groupe)


def vol_coupe(coque, niveaux, optique, racine):
    groupe = collection("Phare · éléments dévoilés en coupe")
    coupe = origine("Coupe", (0,0,0), groupe)
    coupe.parent = racine
    noms_a_masquer = ("Jambage du portail", "Épaulement du portail", "Clé du portail",
                      "Toit bas", "Joue de la lucarne", "Auvent de la lucarne",
                      "Échelle de service", "Échelon")
    bpy.context.view_layer.update()
    for o in list(coque.objects):
        if o.type != "MESH":
            continue
        centre = empreinte(o)
        if o.name.startswith(noms_a_masquer) or centre.z >= 3.85:
            o.parent = coupe
        elif o.name.startswith("Assise taillée") and (centre.y < -.85 or centre.x > 1.9):
            o.parent = coupe
    # Les dalles d'étage du prototype servaient à dimensionner la tour.
    # L'étage reçoit son propre palier dans l'aile ; le rez reste entièrement lisible.
    for o in list(niveaux.objects):
        if o.name.startswith(("Étage 1", "Étage 2", "Dalle de l'aile")):
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.name.startswith("Sommet"):
            o.parent = coupe
    for o in list(optique.objects):
        if o.parent == racine:
            o.parent = coupe
    return coupe


def construire_interieur(palette, etage=None):
    reconstruire(palette)
    ivoire, sable, creme, terre, _, bronze, or_pale, nuit, _, _ = palette
    pave = mat("Dalles de l'atelier", (.48,.35,.25))
    dalle_claire = mat("Pierre d'usure", (.60,.50,.34))
    suie = mat("Pigment des relevés mécaniques", (.29,.20,.15))
    bois = mat("Bois blond des Semeurs", (.47,.30,.17))
    coque = bpy.data.collections["Phare · enveloppe"]
    optique = bpy.data.collections["Phare · galerie et optique"]
    niveaux = bpy.data.collections["Phare · quatre niveaux"]
    atelier = bpy.data.collections["Phare · organes mécaniques"]
    racine = coque.objects["Origine sur le plateau"]
    racine.name = "Phare"
    salle = collection("Phare · salle des machines")
    collisions = collection("Phare · collisions")
    beaux = origine("SalleDesMachines", (0,0,0), salle)
    solides = origine("Collisions", (0,0,0), collisions)
    beaux.parent = solides.parent = racine

    # Le socle plein de la maquette devient un vrai volume dans l'aile.
    retirer(coque, ("Aile · socle en pierre",))
    for nom, position, taille in [
        ("Aile · mur bas est", (6.16,.0875,2.12), (.39,4.235,3.54)),
        ("Aile · mur bas au nord", (4.73,2.39,2.12), (3.24,.37,3.54)),
        ("Aile · mur bas au sud", (4.62,-2.23,2.12), (3.46,.37,3.54)),
    ]:
        o = boite(nom, position, taille, ivoire, coque, .07)
        o.parent = racine
    # Le passage vers l'escalier est intégré au premier rang de la tour.
    bpy.context.view_layer.update()
    for o in list(coque.objects):
        if not o.name.startswith("Assise taillée"):
            continue
        c = empreinte(o)
        if c.z < 3.80 and c.x > 2.6 and abs(c.y) < .25:
            bpy.data.objects.remove(o, do_unlink=True)
    for bas, haut, rb, rh in [(.24,1.24,3.97,3.88), (1.24,2.72,3.88,3.78),
                              (2.72,3.40,3.78,3.73), (3.40,4.15,3.73,3.70)]:
        portions = [(0,.025), (.77,1)] if haut <= 2.72 else [(0,1)]
        for segment in portions:
            o = mur("Paroi entre atelier et aile", rb,rh,bas,haut,0,segment,ivoire,coque)
            o.parent = racine
    # Une embrasure sud dans la pierre et un jour continu jusqu'à l'atelier.
    for s in (-1,1):
        o = boite("Joue intérieure du portail", (s*1.19,-3.31,1.61), (.30,1.14,2.53),
                  sable, coque, .075)
        o.rotation_euler.z = s*math.radians(9)
        o.parent = racine
    o = boite("Intrados du portail", (0,-3.26,2.99), (2.24,1.15,.37), sable, coque, .09)
    o.parent = racine
    coupe = vol_coupe(coque,niveaux,optique,racine)
    for o in list(coque.objects):
        if o.name.startswith(("Joue intérieure", "Intrados", "Aile · mur bas au sud")):
            o.parent = coupe

    for o in atelier.objects:
        if o.name.startswith("Maillon") and o.location.z > 3.85:
            o.parent = coupe

    # Dalles de passage et trois empreintes sous les axes de la machine.
    profil("Sol en pierre des machines", [(3.47,.331),(3.47,.354)], sable, salle)
    for y in (-2.6,-1.96,-1.32,-.68,-.04):
        boite("Dalle traversante", (0,y,.355), (1.72,.60,.029), pave, salle, .018)
    for y in (-1.62,-.96,-.30,.36,1.02,1.68):
        boite("Dalle du passage latéral", (2.52,y,.356), (.94,.61,.028), pave,salle,.015)
    for x,y,r in [(-1.15,.68,.92), (-.66,1.88,.64), (1.1,1.82,.75)]:
        o = anneau("Trace circulaire d'usure", r,.077,.356,.361,dalle_claire,salle,18)
        o.location = (x,y,0)
        for d in (-1,1):
            boite("Marque d'appui", (x+d*r*.55,y,.362), (.14,.061,.009), suie,salle)

    # L'établi et le chevalet dessinent la limite arrière de la circulation.
    boite("Établi du gardien", (-.60,2.53,1.11), (2.68,.55,.19), bois,salle,.055)
    for x in (-1.68,.46):
        boite("Pied de l'établi", (x,2.53,.72), (.21,.37,.75), bois,salle,.027)
    for i in range(3):
        boite("Cale de maintenance", (-1.23+i*.18,2.48,1.25), (.11,.26,.079), or_pale,salle,.017)
    boite("Plaque du schéma", (-.68,2.96,2.19), (2.33,.095,1.19), sable,salle,.036)
    for x,z,r in [(-1.37,2.25,.36), (-.77,2.05,.28), (-.23,2.29,.29)]:
        o = anneau("Roue du schéma peint", r,.042,-.006,.006,suie,salle,14)
        o.location = (x,2.902,z)
        o.rotation_euler.x = math.pi/2
        montant("Rayon du relevé", (x-r*.58,2.891,z),(x+r*.58,2.891,z),.014,suie,salle,4)
        montant("Rayon du relevé", (x,2.891,z-r*.58),(x,2.891,z+r*.58),.014,suie,salle,4)
    boite("Pied du bâti de chaîne", (1.62,.60,.51), (.67,.70,.31), sable,salle,.053)
    for x in (1.29,1.96):
        montant("Montant du bâti de chaîne", (x,.70,.62),(x,.70,3.62),.074,bronze,salle,4)
    boite("Support d'axe de chaîne", (1.60,.70,3.57), (.82,.25,.14), bronze,salle,.025)

    # Escalier en U. Deux rampes de collision suivent exactement le nez des marches.
    boite("Sol de l'aile", (4.50,.10,.15), (3.52,4.57,.40), sable,salle,.048)
    boite("Palier vers le bureau", (5.38,-1.65,4.005), (1.52,1.00,.19), creme,salle,.035)
    boite("Palier haut-colonly", (5.38,-1.65,4.005), (1.52,1.00,.19), None,collisions)
    for x in (4.67, 6.08):
        montant("Potelet du palier", (x,-2.13,4.10),(x,-2.13,4.96), .048,bronze,salle)
    for z in (4.51, 4.96):
        montant("Barre d'arrêt du palier", (4.67,-2.13,z),(6.08,-2.13,z), .068,bronze,salle)
    boite("Palier du demi-tour", (4.83,1.85,2.13), (2.62,.81,.19), creme,salle,.042)
    boite("Demi-tour-colonly", (4.83,1.85,2.13), (2.62,.81,.19), None,collisions)
    for indice,(x, depart, arrivee, bas, haut) in enumerate(
        [(4.10,-.84,1.445,.35,2.225),(5.45,1.445,-1.15,2.225,4.10)]
    ):
        for pas in range(9):
            t = (pas+.5)/9
            y = depart+(arrivee-depart)*t
            z = bas+(haut-bas)*(pas+1)/9
            boite("Marche de pierre", (x,y,z-.108), (1.39,abs(arrivee-depart)/9+.011,.216),
                  creme if pas%3 else ivoire,salle,.024)
        pente(f"Volée {indice+1}-colonly",x-.70,x+.70,depart,arrivee,bas,haut,collisions)
        # Garde-corps du côté du vide, avec sa collision en pente.
        bord = x+(.70 if indice==0 else -.70)
        a,b = (0,.81) if indice==0 else (.17,1)
        y_a, y_b = (depart+(arrivee-depart)*t for t in (a,b))
        z_a, z_b = (bas+(haut-bas)*t for t in (a,b))
        montant("Main courante du palier", (bord,y_a,z_a+.91),(bord,y_b,z_b+.91),
                .061,bronze,salle,5)
        for t in (a,(a+b)/2,b):
            y = depart+(arrivee-depart)*t
            z = bas+(haut-bas)*t
            montant("Potelet d'escalier",(bord,y,z),(bord,y,z+.91),.052,bronze,salle,5)
        pente(f"Garde-corps {indice+1}-colonly",bord-.025,bord+.025,y_a,y_b,z_a+.88,z_b+.88,collisions)

    # Collision du seuil, du sol et de la coque. Les vitres et le toit restent décoratifs.
    pente("Parvis-colonly",-2.06,2.06,-4.86,-3.28,.08,.35,collisions)
    profil("Sol de la tour-colonly", [(3.65,.15),(3.65,.35)], None,collisions)
    boite("Sol de l'aile-colonly",(4.58,.09,.15),(3.7,4.61,.4),None,collisions)
    for source,nom in [("Aile · mur bas est","Mur aile est"), ("Aile · mur bas au nord","Mur aile nord"),
                       ("Aile · mur bas au sud","Mur aile sud")]:
        o = coque.objects[source]
        boite(nom+"-colonly",o.location,o.dimensions,None,collisions)
    for cote in range(8):
        portions = [(0,1)]
        if cote == 6:
            portions = [(0,.14),(.86,1)]
        if cote == 0:
            portions = [(0,.13),(.77,1)]
        for indice, portion in enumerate(portions):
            mur(f"Mur de tour {cote}-{indice}-colonly",3.97,3.70,.21,3.94 if etage else 4.17,cote,portion,None,collisions)
    boite("Butée du futur bureau-colonly",(5.26,-2.17,4.69),(1.86,.13,1.17),None,collisions)
    boite("Établi-colonly",(-.60,2.53,.77),(2.62,.51,.84),None,collisions)
    boite("Bâti de chaîne-colonly",(1.62,.69,.48),(.64,.68,.27),None,collisions)

    for o in list(salle.objects):
        if o!=beaux:
            o.parent=beaux
    for o in list(collisions.objects):
        if o!=solides:
            o.parent=solides
    if etage:
        etage(palette, racine, solides, collisions)
    # Fusion des volumes de collision pour un seul corps statique à l'import.
    bpy.ops.object.select_all(action="DESELECT")
    volumes = list(solides.children)
    for o in volumes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = volumes[0]
    bpy.ops.object.join()
    collision = bpy.context.object
    collision.name = "Volumes_Physiques-colonly"
    # Le modèle exporté utilise son origine locale ; le .blend garde le vrai plateau autour.
    chemin = MODELES/"ile02/phare.glb"
    chemin.parent.mkdir(parents=True,exist_ok=True)
    racine.location = (0,0,0)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [racine]+list(racine.children_recursive):
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", use_selection=True,
                              export_apply=True, export_animations=False)
    racine.location = RACINE_PHARE
    collision.hide_render = True
    collision.hide_set(True)


def cadrages_salle(scene, photos, robot, vues):
    # L'aperçu applique la même coupe que le bâtiment traversé dans Godot.
    for o in bpy.data.objects["Coupe"].children_recursive:
        o.hide_render = True
        o.hide_set(True)
    robot.location = RACINE_PHARE + Vector((-.18,-1.38,.35))
    lampe = lumiere("Retour chaud sur l’établi", "AREA", 185, (1,.77,.49),
                     RACINE_PHARE+Vector((-.55,.1,5)), RACINE_PHARE+Vector((-.60,1,.35)),photos)
    lampe.size = 4
    cible = robot.location+Vector((0,0,1))
    angle = math.radians(40)
    vue_jeu = camera("04 · Caméra du robot dans la salle",
                     cible+Vector((0,-9*math.cos(angle),9*math.sin(angle))),cible,28,photos)
    vue_jeu.data.sensor_fit = "VERTICAL"
    vue_jeu.data.sensor_height = 32
    vue_jeu.data.lens = 16/math.tan(math.radians(30))
    vue = camera("05 · Coupe du rez et de l’escalier",RACINE_PHARE+Vector((10,-13,12)),
                 RACINE_PHARE+Vector((1.15,0,1.5)),46,photos)
    scene.camera = vue
    scene.render.filepath = "//coupe_salle_machines.png"
    return [(vue,"coupe_salle_machines"), (vue_jeu,"salle_machines_camera_jeu")]


if __name__=="__main__":
    main(sortie=SORTIE.with_name("phare_ile_02_rez"),variante=construire_interieur,cadrages=cadrages_salle)
