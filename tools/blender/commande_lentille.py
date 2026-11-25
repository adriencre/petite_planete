"""Pupitre de commande de la lentille, sur la galerie du Phare.

Socle de pierre ivoire, plateau de laiton incliné avec cadran gradué et compteur, volant à poignée de bois.
Export : assets/models/ile02/commande_lentille.glb. Nœuds animés dans Godot : « Manivelle » (tourne
autour de son axe Z Godot, vers le joueur) et « Aiguille » (tourne autour de son axe Y Godot, normal au plateau).
Le joueur se tient devant, côté -Y Blender (+Z Godot).

Exécution : Blender -b --python tools/blender/commande_lentille.py
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import MODELES, boite, collection, mat, montant, origine, profil

INCLINAISON = math.radians(28)
TETE = Vector((0, 0, .86))


def accrocher(piece, parent):
    """Rattache sans bouger (les pièces sont construites en coordonnées du pupitre)."""
    piece.parent = parent
    piece.matrix_parent_inverse = parent.matrix_world.inverted()
    return piece


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    groupe = collection("Commande de la lentille")
    ivoire = mat("Calcaire ivoire", (.87, .75, .57))
    creme = mat("Pierre claire des nervures", (.94, .81, .61))
    bronze = mat("Bronze sombre", (.25, .15, .067), .63, .41)
    laiton = mat("Laiton pâle", (.83, .54, .20), .57, .26)
    gravure = mat("Creux des gravures", (.065, .049, .065))
    bois = mat("Bois de la poignée", (.42, .235, .09), 0, .72)

    # Socle
    profil("Plinthe du pupitre", [(.34, 0), (.34, .07), (.29, .10)], ivoire, groupe)
    profil("Fût du pupitre", [(.27, .10), (.21, .64), (.23, .68)], creme, groupe)
    profil("Collier du pupitre", [(.24, .68), (.26, .74), (.19, .77)], bronze, groupe, 16)
    montant("Col du pupitre", (0, 0, .76), TETE, .10, bronze, groupe, 8)

    # Tête inclinée vers le joueur
    tete = origine("Tête du pupitre", TETE, groupe)
    tete.rotation_euler.x = INCLINAISON
    bpy.context.view_layer.update()
    locales = [
        boite("Plateau du pupitre", (0, 0, 0), (.58, .44, .05), laiton, groupe, .012),
        boite("Semelle du plateau", (0, 0, -.04), (.62, .48, .03), bronze, groupe, .008),
        profil("Émail du cadran", [(.165, .025), (.165, .034)], creme, groupe, 32),
        profil("Cerclage du cadran", [(.168, .05), (.168, .02), (.19, .02), (.19, .045), (.168, .05)],
               bronze, groupe, 32, fermer=False),
        boite("Boîtier du compteur", (0, .175, .045), (.20, .075, .04), bronze, groupe, .008),
        boite("Fenêtre du compteur", (0, .175, .066), (.15, .05, .004), creme, groupe),
    ]
    for i in range(36):
        a = i * math.tau / 36
        longue = i % 3 == 0
        r = .135 if longue else .145
        coche = boite("Graduation du cadran", (r * math.cos(a), r * math.sin(a), .036),
                      (.04 if longue else .022, .006, .003), gravure, groupe)
        coche.rotation_euler.z = a
        locales.append(coche)
    for piece in locales:
        piece.parent = tete

    aiguille = origine("Aiguille", (0, 0, .04), groupe)
    aiguille.parent = tete
    for piece in (boite("Lame de l’aiguille", (0, .055, 0), (.012, .13, .005), gravure, groupe),
                  boite("Contrepoids de l’aiguille", (0, -.035, 0), (.028, .03, .006), gravure, groupe),
                  profil("Moyeu de l’aiguille", [(.018, -.002), (.018, .008)], laiton, groupe, 8)):
        piece.parent = aiguille

    # Volant en façade : son axe pointe vers le joueur (-Y).
    centre = Vector((0, -.30, .50))
    montant("Arbre du volant", (0, -.18, .50), centre, .028, bronze, groupe, 8)
    manivelle = origine("Manivelle", centre, groupe)
    debout = Matrix.Rotation(math.pi / 2, 4, "X")
    pieces = [profil("Jante du volant", [(.155, -.018), (.175, -.018), (.175, .018), (.155, .018),
                                         (.155, -.018)], laiton, groupe, 12, fermer=False),
              profil("Moyeu du volant", [(.04, -.03), (.04, .03)], bronze, groupe, 8)]
    for piece in pieces:
        piece.data.transform(debout)
        piece.location = centre
    for i in range(6):
        a = i * math.tau / 6
        bout = Vector((.16 * math.cos(a), 0, .16 * math.sin(a)))
        pieces.append(montant("Rayon du volant", centre, centre + bout, .012, laiton, groupe, 5))
    poignee = centre + Vector((.165, 0, 0))
    pieces.append(montant("Poignée de bois", poignee, poignee + Vector((0, -.13, 0)), .022, bois, groupe, 8, .027))
    bpy.context.view_layer.update()
    for piece in pieces:
        accrocher(piece, manivelle)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(MODELES / "ile02" / "commande_lentille.glb"),
                              export_format="GLB", use_selection=True, export_apply=True)


if __name__ == "__main__":
    main()
