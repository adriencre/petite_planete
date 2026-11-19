"""Sépare le carter, la manivelle et la tête mobile du cric Meshy."""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from miroir_caps import composantes, copier_faces
from phare_ile_02 import MODELES, RACINE, boite, collection, importer, mat

SOURCE = RACINE / "tools/blender/sources/cric_phare/cric_meshy.glb"
PIED = Vector((.230, -.011, -.318))
AXE_MANIVELLE = Vector((0, -.121, -.203))
PIED_SELLETTE = Vector((.230, -.011, .194))


def a_echelle(point, origine):
    x, y, z = point - origine
    return Vector((x * .60, y * .60, z * .32))


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    source = next(o for o in importer(SOURCE, collection("Source Meshy")) if o.type == "MESH")
    maillage = source.data
    points = [source.matrix_world @ sommet.co for sommet in maillage.vertices]
    numeros = composantes(maillage)
    morceaux = {}
    for numero, point in zip(numeros, points):
        morceaux.setdefault(numero, []).append(point)
    manivelle = {numero for numero, points_piece in morceaux.items()
                 if min(p.x for p in points_piece) < -.32 and max(p.x for p in points_piece) < .012}
    sellette = {numero for numero, points_piece in morceaux.items() if min(p.z for p in points_piece) > .192}
    assert manivelle and sellette, "La génération doit fournir une poignée et une tête séparables."
    palette = [
        mat("Bronze patiné", (.13, .32, .31), .35, .52),
        mat("Bronze de la face", (.22, .40, .35), .38, .49),
        mat("Arêtes de laiton", (.58, .32, .12), .48, .40),
        mat("Bois de la poignée", (.42, .235, .09), .0, .72),
    ]
    groupes = {nom: collection(nom) for nom in ("carter", "manivelle", "sellette")}
    faces = {nom: [] for nom in groupes}
    for face in maillage.polygons:
        numero = numeros[face.vertices[0]]
        nom = "manivelle" if numero in manivelle else "sellette" if numero in sellette else "carter"
        faces[nom].append(face)

    def bronze(face):
        if len(morceaux[numeros[face.vertices[0]]]) < 42:
            return 2
        return 1 if face.normal.z > .36 else 0

    copier_faces("Carter du cric", faces["carter"], points, lambda p: a_echelle(p, PIED),
                 palette, bronze, groupes["carter"])
    copier_faces("Manivelle du cric", faces["manivelle"], points,
                 lambda p: a_echelle(p, AXE_MANIVELLE), palette,
                 lambda f: 3 if (source.matrix_world @ f.center).x < -.32 else 2, groupes["manivelle"])
    groupe_sellette = groupes["sellette"]
    copier_faces("Sellette du cric", faces["sellette"], points,
                 lambda p: a_echelle(p, PIED_SELLETTE), palette, lambda f: 2, groupe_sellette)
    boite("Pont de la fourche", (0, .09, .024), (.23, .15, .042), palette[0], groupe_sellette, .009)
    for cote in (-1, 1):
        boite("Griffe", (cote * .093, .181, .031), (.051, .16, .075),
              palette[2], groupe_sellette, .012)
    for nom, groupe in groupes.items():
        bpy.ops.object.select_all(action="DESELECT")
        for piece in groupe.objects:
            piece.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(MODELES / "ile02" / f"cric_{nom}.glb"),
                                  export_format="GLB", use_selection=True, export_apply=True)
    print("Manivelle :", tuple(a_echelle(AXE_MANIVELLE, PIED)))
    print("Sellette :", tuple(a_echelle(PIED_SELLETTE, PIED)))


if __name__ == "__main__":
    main()
