"""Met à jour le graphe graphify du projet, en y ajoutant ce que graphify ne sait pas lire : Godot.

graphify n'a pas d'extracteur GDScript ni .tscn. Ce script :
  1. lance `graphify update . --force` (Python, Markdown… sans LLM) ;
  2. lit scripts/, tests/, tools/ (.gd), scenes/ (.tscn) et shaders/ (.gdshader) ;
  3. ajoute fichiers, fonctions, signaux, commentaires ## et liens (appels, preload,
     scènes -> scripts / scènes instanciées / shaders / modèles) dans graphify-out/graph.json ;
  4. relance `graphify cluster-only .` pour recalculer communautés, rapport et graph.html.

Usage : python tools/graphify_godot.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
GRAPHE = RACINE / "graphify-out" / "graph.json"
DOSSIERS_GD = ["scripts", "tests", "tools"]
DOSSIER_SCENES = "scenes"
EXCLUS = ("scenes/archive/",)

RE_FUNC = re.compile(r"^(static\s+)?func\s+(\w+)\s*\(")
RE_SIGNAL = re.compile(r"^signal\s+(\w+)")
RE_CONST_LOAD = re.compile(r"^(?:const|var)\s+(\w+)\s*(?::=|=|:\s*\w+\s*=)\s*(?:pre)?load\(\"res://([^\"]+)\"\)")
RE_LOAD = re.compile(r"(?:pre)?load\(\"res://([^\"]+)\"\)")
RE_RES = re.compile(r"\"res://([^\"]+\.(?:gd|tscn|gdshader|glb|wav|ogg|mp3|png|tres))\"")
RE_EXTENDS = re.compile(r"^extends\s+(\w+|\"res://[^\"]+\")")
RE_CLASS = re.compile(r"^class_name\s+(\w+)")
RE_APPEL = re.compile(r"(?<![\w.])(\w+)\s*\(")
RE_APPEL_POINT = re.compile(r"(\w+)\.(\w+)\s*\(")
RE_EMIT = re.compile(r"(\w+)\.emit\(")
RE_CONNECT = re.compile(r"(\w+)\.connect\(\s*(\w+)")
RE_EXT = re.compile(r"^\[ext_resource[^\]]*type=\"(\w+)\"[^\]]*path=\"res://([^\"]+)\"[^\]]*id=\"([^\"]+)\"")
RE_NODE = re.compile(r"^\[node name=\"([^\"]+)\"(?:[^\]]*instance=ExtResource\(\"([^\"]+)\"\))?")
RE_SCRIPT_PROP = re.compile(r"^script = ExtResource\(\"([^\"]+)\"\)")

MOTS_CLES = {"if", "elif", "while", "for", "match", "return", "func", "await", "print", "push_warning",
             "push_error", "assert", "preload", "load", "range", "str", "int", "float", "bool", "len",
             "Vector2", "Vector3", "Color", "Transform3D", "Basis", "Quaternion", "Array", "Dictionary",
             "super", "abs", "min", "max", "clamp", "clampf", "lerp", "lerpf", "sin", "cos", "sqrt",
             "deg_to_rad", "randf", "randf_range", "randi", "is_instance_valid", "get_node", "get_tree",
             "smoothstep", "pow", "absf", "signf", "minf", "maxf", "floor", "ceil", "round"}


def ident(chemin: str, *suite: str) -> str:
    base = re.sub(r"[^0-9a-zA-Z]+", "_", chemin.rsplit(".", 1)[0] + "_" + chemin.rsplit(".", 1)[-1]).strip("_").lower()
    return "_".join([base] + [re.sub(r"\W+", "_", s).lower() for s in suite])


class Graphe:
    def __init__(self):
        self.noeuds: dict[str, dict] = {}
        self.liens: list[dict] = []

    def noeud(self, id_, label, fichier, ligne, type_="code", appelable=False):
        if id_ not in self.noeuds:
            n = {"id": id_, "label": label, "_origin": "godot", "file_type": type_,
                 "norm_label": label.lower(), "source_file": fichier, "source_location": f"L{ligne}"}
            if appelable:
                n["_callable"] = True
            self.noeuds[id_] = n
        return id_

    def lien(self, src, dst, relation, fichier, ligne, confiance="EXTRACTED"):
        self.liens.append({"source": src, "target": dst, "relation": relation, "_origin": "godot",
                           "confidence": confiance, "confidence_score": 1.0 if confiance == "EXTRACTED" else 0.6,
                           "source_file": fichier, "source_location": f"L{ligne}", "weight": 1.0})


def fichier_noeud(g: Graphe, chemin: str) -> str:
    return g.noeud(ident(chemin), Path(chemin).name, chemin, 1,
                   "code" if chemin.endswith((".gd", ".tscn", ".gdshader")) else "asset")


def lire_gd(g: Graphe, chemin: str, fonctions_globales: dict):
    lignes = (RACINE / chemin).read_text(encoding="utf-8", errors="replace").splitlines()
    f_id = fichier_noeud(g, chemin)
    alias: dict[str, str] = {}
    locales: dict[str, str] = {}
    courant = f_id
    doc: list[tuple[int, str]] = []
    corps: list[tuple[str, int, str]] = []  # (id fonction, ligne, texte)

    for i, brut in enumerate(lignes, 1):
        l = brut.strip()
        if l.startswith("##"):
            doc.append((i, l.lstrip("#").strip()))
            continue
        if brut and not brut[0].isspace():
            if doc:  # commentaire ## : la raison d'être de ce qui suit (ou du fichier, en tête)
                cible = f_id
                m = RE_FUNC.match(l)
                if m:
                    cible = ident(chemin, m.group(2))
                    g.noeud(cible, m.group(2) + "()", chemin, i, appelable=True)
                texte = " ".join(t for _, t in doc)
                r_id = g.noeud(ident(chemin, "rationale", str(doc[0][0])),
                               texte[:80] + ("…" if len(texte) > 80 else ""), chemin, doc[0][0], "rationale")
                g.lien(r_id, cible, "rationale_for", chemin, doc[0][0])
                doc = []
            courant = f_id
        m = RE_CLASS.match(l)
        if m:
            g.noeuds[f_id]["label"] = f"{m.group(1)} ({Path(chemin).name})"
        m = RE_EXTENDS.match(l)
        if m:
            base = m.group(1).strip('"')
            if base.startswith("res://"):
                g.lien(f_id, fichier_noeud(g, base[6:]), "inherits", chemin, i)
            else:
                g.lien(f_id, g.noeud("godot_" + base.lower(), base, "", 0, "concept"), "inherits", chemin, i)
        m = RE_SIGNAL.match(l)
        if m:
            s_id = g.noeud(ident(chemin, "signal", m.group(1)), f"signal {m.group(1)}", chemin, i)
            g.lien(f_id, s_id, "contains", chemin, i)
        m = RE_CONST_LOAD.match(l)
        if m:
            alias[m.group(1)] = m.group(2)
        m = RE_FUNC.match(l)
        if m:
            nom = m.group(2)
            courant = g.noeud(ident(chemin, nom), nom + "()", chemin, i, appelable=True)
            locales[nom] = courant
            fonctions_globales.setdefault(nom, []).append(courant)
            g.lien(f_id, courant, "contains", chemin, i)
            continue
        for cible in set(RE_RES.findall(l)):
            if any(cible.startswith(e) for e in EXCLUS):
                continue
            g.lien(courant, fichier_noeud(g, cible), "imports" if cible.endswith(".gd") else "references", chemin, i)
        corps.append((courant, i, l.split("#", 1)[0]))

    return f_id, alias, locales, corps


def lier_appels(g, chemin, alias, locales, corps, fonctions_globales, fonctions_par_fichier):
    vus = set()
    for src, i, texte in corps:
        for a, meth in RE_APPEL_POINT.findall(texte):
            if a in alias and alias[a] in fonctions_par_fichier and meth in fonctions_par_fichier[alias[a]]:
                cle = (src, fonctions_par_fichier[alias[a]][meth], "calls")
            elif meth not in MOTS_CLES and a not in alias and len(fonctions_globales.get(meth, [])) == 1 \
                    and fonctions_globales[meth][0] not in locales.values():
                cle = (src, fonctions_globales[meth][0], "indirect_call")
            else:
                continue
            if cle not in vus:
                vus.add(cle)
                g.lien(src, cle[1], cle[2], chemin, i, "EXTRACTED" if cle[2] == "calls" else "INFERRED")
        for nom in RE_APPEL.findall(texte):
            if nom in locales and nom not in MOTS_CLES and locales[nom] != src:
                cle = (src, locales[nom], "calls")
                if cle not in vus:
                    vus.add(cle)
                    g.lien(src, locales[nom], "calls", chemin, i)
        for _, cb in RE_CONNECT.findall(texte):
            if cb in locales and (src, locales[cb], "calls") not in vus:
                vus.add((src, locales[cb], "calls"))
                g.lien(src, locales[cb], "calls", chemin, i)


def lire_tscn(g: Graphe, chemin: str):
    f_id = fichier_noeud(g, chemin)
    ext: dict[str, str] = {}
    instancies: set[str] = set()
    noeud_courant = None
    for i, l in enumerate((RACINE / chemin).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = RE_EXT.match(l)
        if m:
            type_, res, rid = m.groups()
            ext[rid] = res
            if type_ in ("Shader", "PackedScene") or res.endswith((".glb", ".gd")):
                continue  # lié à l'usage (script = / instance=) ou plus bas
            continue
        m = RE_NODE.match(l)
        if m:
            noeud_courant = m.group(1)
            if m.group(2) and m.group(2) in ext:
                g.lien(f_id, fichier_noeud(g, ext[m.group(2)]), "instances", chemin, i)
                instancies.add(m.group(2))
            continue
        m = RE_SCRIPT_PROP.match(l)
        if m and m.group(1) in ext:
            g.lien(f_id, fichier_noeud(g, ext[m.group(1)]), "uses_script", chemin, i)
    for rid, res in ext.items():
        if rid not in instancies and res.endswith((".gdshader", ".glb")) and not any(res.startswith(e) for e in EXCLUS):
            g.lien(f_id, fichier_noeud(g, res), "references", chemin, 1)


def extraire() -> Graphe:
    g = Graphe()
    fonctions_globales: dict[str, list] = {}
    lus = []
    for d in DOSSIERS_GD:
        for p in sorted((RACINE / d).rglob("*.gd")):
            chemin = p.relative_to(RACINE).as_posix()
            lus.append((chemin, *lire_gd(g, chemin, fonctions_globales)))
    par_fichier = {c: loc for c, _, _, loc, _ in lus}
    for chemin, _, alias, locales, corps in lus:
        lier_appels(g, chemin, alias, locales, corps, fonctions_globales, par_fichier)
    for p in sorted((RACINE / DOSSIER_SCENES).rglob("*.tscn")):
        chemin = p.relative_to(RACINE).as_posix()
        if not any(chemin.startswith(e) for e in EXCLUS):
            lire_tscn(g, chemin)
    for p in sorted((RACINE / "shaders").rglob("*.gdshader")):
        fichier_noeud(g, p.relative_to(RACINE).as_posix())
    return g


def graphify(*args):
    print("$ graphify", *args)
    subprocess.run(["graphify", *args], cwd=RACINE, check=True)


def main():
    graphify("update", ".", "--force", "--no-cluster")
    data = json.loads(GRAPHE.read_text(encoding="utf-8"))
    data["nodes"] = [n for n in data["nodes"] if n.get("_origin") != "godot"]
    data["links"] = [e for e in data["links"] if e.get("_origin") != "godot"]
    g = extraire()
    existants = {n["id"] for n in data["nodes"]}
    data["nodes"] += [n for n in g.noeuds.values() if n["id"] not in existants]
    data["links"] += g.liens
    GRAPHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Godot : +{len(g.noeuds)} nœuds, +{len(g.liens)} liens")
    graphify("cluster-only", ".", "--no-label")


if __name__ == "__main__":
    sys.exit(main())
