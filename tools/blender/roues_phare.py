"""Exporte les trois roues de la salle des machines, centrées sur leur axe."""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import MODELES, anneau, boite, collection, mat, montant, objet, origine, profil

MODULE = .08
ROUES = (("menante", 12), ("intermediaire", 16), ("menee", 10))


def denture(dents, bronze, cuivre, groupe):
    """Couronne à développante, avec un pas et un angle de pression communs."""
    primitif = MODULE * dents / 2
    pression = math.radians(20)
    base = primitif * math.cos(pression)
    fond = primitif - .107
    sommet = primitif + .070
    pas = math.tau / dents
    jeu = .012 / primitif

    def largeur(rayon):
        angle = math.acos(min(1, base / rayon))
        return pas / 4 + math.tan(pression) - pression - math.tan(angle) + angle - jeu

    flanc = [(largeur(base), fond)]
    for i in range(5):
        rayon = base + (sommet - base) * i / 4
        flanc.append((largeur(rayon), rayon))
    contour = []
    for dent in range(dents):
        centre = pas * (dent + .5)
        contour.extend((centre - angle, rayon) for angle, rayon in flanc)
        contour.extend((centre + angle, rayon) for angle, rayon in reversed(flanc))
    sommets = []
    for hauteur, interieur in [(-.091, True), (-.091, False), (.091, False), (.091, True)]:
        sommets.extend((r * math.cos(a), r * math.sin(a), hauteur)
                       for a, rayon in contour for r in [primitif - .118 if interieur else rayon])
    n = len(contour)
    faces = []
    for j in range(4):
        suivant = (j + 1) % 4
        for i in range(n):
            k = (i + 1) % n
            faces.append((j * n + i, j * n + k, suivant * n + k, suivant * n + i))
    couronne = objet("Denture", sommets, faces, bronze, groupe)
    couronne.data.materials.append(cuivre)
    for face in couronne.data.polygons:
        if face.index // n == 2:
            face.material_index = 1
    return primitif


def construire(nom, dents, palette):
    groupe = collection(nom)
    bronze, cuivre, laiton, huile = palette
    rayon = denture(dents, bronze, cuivre, groupe)
    anneau("Épaulement", rayon - .092, .047, .086, .123, cuivre, groupe, dents * 2)
    profil("Moyeu graissé", [(.141, -.139), (.149, .11), (.124, .147)], huile, groupe, 12)
    anneau("Virole", .128, .034, .145, .162, laiton, groupe, 12)
    for indice in range(4):
        a = math.tau * indice / 4
        d = Vector((math.cos(a), math.sin(a), 0))
        montant("Rayon", d * .105, d * (rayon - .089), .047, bronze, groupe, 6, .07)
    boite("Index du clavetage", (rayon - .13, 0, .131), (.077, .037, .017), laiton, groupe, .008)
    pivot = origine("Axe", (0, 0, 0), groupe)
    pivot.rotation_euler.x = math.pi / 2
    for piece in groupe.objects:
        if piece != pivot:
            piece.parent = pivot
    return groupe


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    palette = (
        mat("Bronze des dents", (.31, .23, .14), .48, .48),
        mat("Cuivre patiné", (.14, .30, .29), .38, .47),
        mat("Laiton des repères", (.78, .52, .20), .46, .32),
        mat("Acier huilé", (.14, .17, .18), .56, .48),
    )
    for nom, dents in ROUES:
        groupe = construire(nom, dents, palette)
        bpy.ops.object.select_all(action="DESELECT")
        for piece in groupe.objects:
            piece.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(MODELES / "ile02" / f"roue_{nom}.glb"),
                                  export_format="GLB", use_selection=True, export_apply=True)


if __name__ == "__main__":
    main()
