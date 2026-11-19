"""Ajoute les clips Meshy de l'échelle au GLB du robot, en conservant ses données existantes."""
import json
import math
import struct
from pathlib import Path


RACINE = Path(__file__).resolve().parents[2]
ROBOT = RACINE / "assets/models/robot_meshy.glb"
SOURCE = RACINE / "tools/blender/sources/meshy/robot_rig/robot_echelle.glb"
CLIPS = {
    "Ladder_Mount_Start": "echelle_prise",
    "Ladder_Climb_Loop": "echelle_cycle",
    "Ladder_Climb_Finish": "echelle_sortie",
}
DIMENSIONS = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}


def ouvrir_glb(chemin):
    donnees = chemin.read_bytes()
    assert donnees[:4] == b"glTF"
    longueur, type_json = struct.unpack_from("<I4s", donnees, 12)
    longueur_bin, type_bin = struct.unpack_from("<I4s", donnees, 20 + longueur)
    assert type_json == b"JSON" and type_bin == b"BIN\x00"
    modele = json.loads(donnees[20:20 + longueur])
    return modele, bytearray(donnees[28 + longueur:28 + longueur + longueur_bin])


def lire_accesseur(modele, binaire, index):
    a = modele["accessors"][index]
    v = modele["bufferViews"][a["bufferView"]]
    assert a["componentType"] == 5126 and "sparse" not in a and v["buffer"] == 0
    dimensions = DIMENSIONS[a["type"]]
    pas = v.get("byteStride", 4 * dimensions)
    debut = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return [struct.unpack_from("<" + "f" * dimensions, binaire, debut + pas * i)
            for i in range(a["count"])]


def ecrire_accesseur(modele, binaire, type_donnees, valeurs):
    dimensions = DIMENSIONS[type_donnees]
    debut = len(binaire)
    for valeur in valeurs:
        binaire.extend(struct.pack("<" + "f" * dimensions, *valeur))
    vue = len(modele["bufferViews"])
    modele["bufferViews"].append({"buffer": 0, "byteOffset": debut, "byteLength": len(binaire) - debut})
    a = {"bufferView": vue, "componentType": 5126, "count": len(valeurs), "type": type_donnees}
    if dimensions == 1:
        a["min"] = [min(v[0] for v in valeurs)]
        a["max"] = [max(v[0] for v in valeurs)]
    modele["accessors"].append(a)
    return len(modele["accessors"]) - 1


def redresser_bassin(q):
    x, y, z, w = q
    lacet = math.atan2(2 * (x * z + y * w), 1 - 2 * (x * x + y * y))
    retenu = .22 * math.sin(lacet)
    s, c = math.sin((retenu - lacet) / 2), math.cos((retenu - lacet) / 2)
    return c * x + s * z, c * y + s * w, c * z - s * x, c * w - s * y


def ajuster_pose(nom, os, propriete, temps, valeurs):
    debut, fin = temps[0][0], temps[-1][0]
    if os == "Hips" and propriete == "translation":
        # Le joueur porte le déplacement entre les paliers. Le clip garde ses oscillations.
        arrivee = valeurs[-1]
        origine = valeurs[0]
        valeurs = [tuple(v - (b - a) * ((t - debut) / (fin - debut)) for v, a, b in zip(p, origine, arrivee))
                   for (t,), p in zip(temps, valeurs)]
    if os == "Hips" and nom == "echelle_prise" and propriete == "rotation":
        # La prise Meshy tourne sur elle-même. Le cadrage du phare oriente déjà le robot.
        valeurs = [redresser_bassin(q) for q in valeurs]
    if nom != "echelle_cycle" or len(valeurs) < 6:
        return valeurs

    # Fermer la boucle au dernier appui sur les mêmes poses qu'au premier.
    cible = valeurs[0]
    for i in range(len(valeurs) - 5, len(valeurs)):
        p = (i - len(valeurs) + 6) / 5
        p = p * p * (3 - 2 * p)
        valeur = valeurs[i]
        if propriete == "rotation" and sum(a * b for a, b in zip(valeur, cible)) < 0:
            valeur = tuple(-a for a in valeur)
        melange = tuple(a + (b - a) * p for a, b in zip(valeur, cible))
        if propriete == "rotation":
            norme = math.sqrt(sum(v * v for v in melange))
            melange = tuple(v / norme for v in melange)
        valeurs[i] = melange
    return valeurs


def verifier_os(source, dest):
    for cle, defaut in [("translation", [0, 0, 0]), ("scale", [1, 1, 1])]:
        assert max(abs(x - y) for x, y in zip(source.get(cle, defaut), dest.get(cle, defaut))) < .01
    qa = source.get("rotation", [0, 0, 0, 1])
    qb = dest.get("rotation", [0, 0, 0, 1])
    assert abs(sum(x * y for x, y in zip(qa, qb))) > .9999, source["name"]


def retirer_anciens_clips(modele, binaire):
    clips = [a for a in modele["animations"] if a["name"] in CLIPS.values()]
    if not clips:
        return
    indices = {s[k] for a in clips for s in a["samplers"] for k in ("input", "output")}
    premier = min(indices)
    vues = {modele["accessors"][i]["bufferView"] for i in indices}
    premiere_vue = min(vues)
    # Les pistes ajoutées occupent la fin du fichier après tous les éléments du robot.
    assert indices == set(range(premier, len(modele["accessors"])))
    assert vues == set(range(premiere_vue, len(modele["bufferViews"])))
    debut = modele["bufferViews"][premiere_vue]["byteOffset"]
    del binaire[debut:]
    del modele["bufferViews"][premiere_vue:]
    del modele["accessors"][premier:]
    modele["animations"] = [a for a in modele["animations"] if a["name"] not in CLIPS.values()]


def assembler():
    source, donnees = ouvrir_glb(SOURCE)
    modele, binaire = ouvrir_glb(ROBOT)
    correspondance = {n["name"]: i for i, n in enumerate(modele["nodes"])}
    animations = {a["name"]: a for a in source["animations"]}
    retirer_anciens_clips(modele, binaire)
    for nom_meshy, nom in CLIPS.items():
        clip = animations[nom_meshy]
        samplers, canaux, temps_ecrits = [], [], {}
        for canal in clip["channels"]:
            cible = canal["target"]
            os_source = source["nodes"][cible["node"]]
            propriete = cible["path"]
            indice_os = correspondance[os_source["name"]]
            verifier_os(os_source, modele["nodes"][indice_os])
            sampler = clip["samplers"][canal["sampler"]]
            interpolation = sampler.get("interpolation", "LINEAR")
            assert interpolation in ("LINEAR", "STEP")
            temps = lire_accesseur(source, donnees, sampler["input"])
            valeurs = lire_accesseur(source, donnees, sampler["output"])
            valeurs = ajuster_pose(nom, os_source["name"], propriete, temps, valeurs)
            if sampler["input"] not in temps_ecrits:
                temps_ecrits[sampler["input"]] = ecrire_accesseur(modele, binaire, "SCALAR", temps)
            sortie = ecrire_accesseur(modele, binaire, source["accessors"][sampler["output"]]["type"], valeurs)
            canaux.append({"sampler": len(samplers), "target": {"node": indice_os, "path": propriete}})
            samplers.append({"input": temps_ecrits[sampler["input"]], "output": sortie, "interpolation": interpolation})
        modele["animations"].append({"name": nom, "samplers": samplers, "channels": canaux})
    modele["buffers"][0]["byteLength"] = len(binaire)
    en_tete = json.dumps(modele, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    en_tete += b" " * (-len(en_tete) % 4)
    resultat = (struct.pack("<4sII", b"glTF", 2, 28 + len(en_tete) + len(binaire))
                + struct.pack("<I4s", len(en_tete), b"JSON") + en_tete
                + struct.pack("<I4s", len(binaire), b"BIN\x00") + binaire)
    provisoire = ROBOT.with_suffix(".glb.tmp")
    provisoire.write_bytes(resultat)
    provisoire.replace(ROBOT)


if __name__ == "__main__":
    assembler()
