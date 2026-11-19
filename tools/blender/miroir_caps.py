"""Prépare les deux géométries Meshy et exporte les trois pièces de la station."""

from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phare_ile_02 import MODELES, RACINE, boite, collection, importer, mat, montant, objet

SOURCES = RACINE / "tools/blender/sources/miroir_caps"
SORTIE = MODELES / "ile02"
PIED_BATI = Vector((-.031, 0, -.476318))
AXE_MANIVELLE = Vector((.258, -.308, -.159))
ECHELLE_BATI = 1.276
PIED_TETE = .476318
ECHELLE_TETE = 1.06


def composantes(maillage):
    """Attribue un numéro de pièce à chaque sommet relié par des arêtes."""
    voisins = [[] for _ in maillage.vertices]
    for arete in maillage.edges:
        a, b = arete.vertices
        voisins[a].append(b)
        voisins[b].append(a)
    numeros = [-1] * len(voisins)
    for index in range(len(voisins)):
        if numeros[index] != -1:
            continue
        numeros[index] = index
        file = [index]
        while file:
            for voisin in voisins[file.pop()]:
                if numeros[voisin] == -1:
                    numeros[voisin] = index
                    file.append(voisin)
    return numeros


def copier_faces(nom, faces, points, transformation, palette, couleur, groupe):
    indices = sorted({index for face in faces for index in face.vertices})
    indice_local = {index: i for i, index in enumerate(indices)}
    piece = objet(nom, [transformation(points[i]) for i in indices],
                  [[indice_local[i] for i in face.vertices] for face in faces], None, groupe)
    for matiere in palette:
        piece.data.materials.append(matiere)
    for polygone, source in zip(piece.data.polygons, faces):
        polygone.material_index = couleur(source)
    return piece


def exporter(nom, groupe):
    bpy.ops.object.select_all(action="DESELECT")
    for piece in groupe.objects:
        piece.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(SORTIE / f"miroir_{nom}.glb"),
                              export_format="GLB", use_selection=True, export_apply=True)


def preparer_bati(source, groupes, palette):
    maillage = source.data
    points = [source.matrix_world @ sommet.co for sommet in maillage.vertices]
    numeros = composantes(maillage)
    morceaux = {}
    for numero, point in zip(numeros, points):
        morceaux.setdefault(numero, []).append(point)
    mobiles = {
        numero for numero, morceau in morceaux.items()
        if min(p.x for p in morceau) > .19 and max(p.y for p in morceau) < -.29
        and -.08 < max(p.z for p in morceau) < .06 and len(morceau) > 70
    }
    assert len(mobiles) == 2, "Le bras et la poignée Meshy doivent rester séparés."
    fixes, manivelle = [], []
    for face in maillage.polygons:
        destination = manivelle if numeros[face.vertices[0]] in mobiles else fixes
        destination.append(face)

    def teinte(f):
        x, y, z = source.matrix_world @ f.center
        if z > .345 or (y < -.257 and -.26 < x < .20 and -.135 < z < .278):
            return 2
        return 1 if z < -.36 else 0

    copier_faces("Bâti", fixes, points, lambda p: (p - PIED_BATI) * ECHELLE_BATI,
                 palette, teinte, groupes["bati"])
    montant("Pignon dans le carter", (-.022, -.33, .707), (-.022, -.393, .707),
            .142, palette[3], groupes["bati"], nombre=12)
    montant("Moyeu du pignon", (-.022, -.388, .707), (-.022, -.423, .707),
            .049, palette[2], groupes["bati"], nombre=8)
    copier_faces("Manivelle", manivelle, points, lambda p: (p - AXE_MANIVELLE) * ECHELLE_BATI,
                 palette, lambda f: 4 if (source.matrix_world @ f.center).x > .31 else 3,
                 groupes["manivelle"])


def preparer_tete(source, groupe, palette):
    maillage = source.data
    points = [source.matrix_world @ sommet.co for sommet in maillage.vertices]

    def teinte(f):
        z = (source.matrix_world @ f.center).z
        return 3 if z < -.225 else 2

    # Le miroir pointe vers +Y dans Blender, soit -Z dans Godot.
    copier_faces("Tête du miroir", list(maillage.polygons), points,
                 lambda p: Vector((-p.x, -p.y, p.z + PIED_TETE)) * ECHELLE_TETE,
                 palette, teinte, groupe)
    # Le verre reste plan et se loge dans la feuillure du cadre Meshy.
    contour = [(-.18, .355), (-.289, .463), (-.289, .843), (-.18, .947),
               (.18, .947), (.289, .843), (.289, .463), (.18, .355)]
    objet("Verre du miroir", [(x, .105, z) for x, z in contour],
          [tuple(range(len(contour)))], palette[5], groupe)
    montant("Bras du contrepoids", (0, -.055, .56), (0, -.34, .43),
            .046, palette[3], groupe)
    boite("Contrepoids", (0, -.34, .39), (.23, .18, .19), palette[2], groupe, .035)


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    sources = collection("Géométries Meshy")
    groupes = {nom: collection(nom) for nom in ("bati", "manivelle", "tete")}
    palette = [
        mat("Pierre ivoire", (.76, .59, .42)),
        mat("Pierre dorée", (.58, .40, .29)),
        mat("Cuivre patiné", (.10, .29, .31), .43, .45),
        mat("Bronze ambré", (.48, .27, .12), .53, .43),
        mat("Bois blond", (.44, .26, .12)),
        mat("Face du miroir", (.68, .82, .79), .48, .23),
    ]
    bati = next(o for o in importer(SOURCES / "bati.glb", sources) if o.type == "MESH")
    tete = next(o for o in importer(SOURCES / "tete.glb", sources) if o.type == "MESH")
    preparer_bati(bati, groupes, palette)
    preparer_tete(tete, groupes["tete"], palette)
    for nom, groupe in groupes.items():
        exporter(nom, groupe)
    print("Pivot de la manivelle dans Blender :", tuple((AXE_MANIVELLE - PIED_BATI) * ECHELLE_BATI))


if __name__ == "__main__":
    main()
