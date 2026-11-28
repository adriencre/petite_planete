"""Chorégraphie des mains en 1re personne -> assets/animations/gestes_mains.tres (AnimationLibrary).

Clip « tirer_fiche » (repère de la caméra, nœuds de Camera/Mains) : la main droite se tourne pour présenter
sa bobine, la main gauche vient pincer la fiche couchée sur le poignet, la décroche et tire le câble
jusque devant soi. Pendant tout le tirage, la main gauche est recalculée image par image à partir de la
fiche (même formule que joueur.gd : main gauche = fiche * pince⁻¹), donc elle ne glisse jamais.

Les repères des mains (pince, fiche au repos) viennent de assets/models/mains/reperes_mains.json,
écrit par tools/blender/mains_robot.py. Relancer ce script après une modification des mains.
Le .tres est régénéré en entier : retoucher plutôt les clés ci-dessous que le .tres à la main.

Exécution : python3 tools/godot/gestes_mains.py [--echantillons FICHIER.json]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
REPERES = json.loads((RACINE / "assets/models/mains/reperes_mains.json").read_text())
SORTIE = RACINE / "assets/animations/gestes_mains.tres"
IPS = 30

PINCE_G = np.array(REPERES["MainGauche"]["pince"])
FICHE_REPOS = np.array(REPERES["MainDroite"]["fiche_repos"])
FICHE_REPOS_LACET = REPERES["MainDroite"]["fiche_repos_lacet"]

# Clés (temps, position caméra, angles en degrés x/y/z, ordre YXZ de Godot).
MAIN_DROITE = [
    (0.00, (0.160, -0.190, -0.420), (15, 0, 0)),     # mains levées (joueur.gd, MAIN_D_LEVEE)
    (0.70, (0.085, -0.150, -0.420), (22, 18, 12)),   # elle ramène le poignet au milieu et le présente
    (1.70, (0.090, -0.155, -0.420), (20, 16, 10)),   # elle tient bon pendant qu'on tire
    (2.40, (0.160, -0.215, -0.400), (8, 8, 4)),      # elle s'écarte et laisse filer le câble
]
MAIN_GAUCHE_DEPART = ((-0.190, -0.230, -0.400), (0, -15, 0))  # MAIN_G_LEVEE
T_DEPART_G, T_APPROCHE, T_PINCE = 0.30, 0.90, 1.08
T_DECROCHE, T_FIN = 1.25, 2.40
FICHE_FIN = ((-0.050, -0.140, -0.420), (6, -15, 55))  # présentée devant soi, main tournée pouce en haut : on voit la fiche
POSES = {  # (temps, os d'AnimationPlayer, pose, fondu)
    "MainDroite/Modele/AnimationPlayer": [(0.0, "repos", 0.2)],
    # les doigts se referment pendant le dernier centimètre : ils touchent la fiche juste à T_PINCE
    "MainGauche/Modele/AnimationPlayer": [(T_DEPART_G, "ouverte", 0.3), (T_APPROCHE + 0.04, "pincer", T_PINCE - T_APPROCHE - 0.04)],
}


# ---------------------------------------------------------------- petite algèbre (repère Godot)

def rot(angles):
    x, y, z = (math.radians(a) for a in angles)
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return ry @ rx @ rz


def quat(m):
    """Matrice -> quaternion (x, y, z, w)."""
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = ((m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s)
    else:
        i = int(np.argmax(np.diag(m)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = math.sqrt(1.0 + m[i, i] - m[j, j] - m[k, k]) * 2
        q = [0.0] * 4
        q[i] = 0.25 * s
        q[j] = (m[j, i] + m[i, j]) / s
        q[k] = (m[k, i] + m[i, k]) / s
        q[3] = (m[k, j] - m[j, k]) / s
    q = np.array(q)
    return q / np.linalg.norm(q)


def mat_q(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(a, b, t):
    d = float(np.dot(a, b))
    if d < 0:
        b, d = -b, -d
    if d > 0.9995:
        q = a + (b - a) * t
        return q / np.linalg.norm(q)
    th = math.acos(d)
    return (math.sin((1 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)


def lisse(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def tf(pos, r):
    m = np.eye(4)
    m[:3, :3] = r
    m[:3, 3] = pos
    return m


def entre_cles(cles, t):
    """Position et rotation entre deux clés, avec un départ et une arrivée en douceur."""
    if t <= cles[0][0]:
        return tf(cles[0][1], rot(cles[0][2]))
    for (t0, p0, a0), (t1, p1, a1) in zip(cles, cles[1:]):
        if t <= t1:
            u = lisse((t - t0) / (t1 - t0))
            p = np.array(p0) + (np.array(p1) - np.array(p0)) * u
            return tf(p, mat_q(slerp(quat(rot(a0)), quat(rot(a1)), u)))
    return tf(cles[-1][1], rot(cles[-1][2]))


def melange(a, b, u):
    m = tf(a[:3, 3] + (b[:3, 3] - a[:3, 3]) * u, mat_q(slerp(quat(a[:3, :3]), quat(b[:3, :3]), u)))
    return m


# la main gauche tient la fiche dans l'axe de ses doigts (même valeur que PINCE_G dans joueur.gd)
PINCE = tf(PINCE_G, np.eye(3))
REPOS = tf(FICHE_REPOS, rot((0, FICHE_REPOS_LACET, 0)))


def fiche_monde(t):
    """La fiche dans le repère caméra."""
    d = entre_cles(MAIN_DROITE, t)
    if t <= T_PINCE:
        return d @ REPOS
    if t <= T_DECROCHE:  # elle sort de son agrafe : un petit cran vers le haut et l'arrière
        u = lisse((t - T_PINCE) / (T_DECROCHE - T_PINCE))
        return d @ REPOS @ tf(np.array([0, 0.014, 0.008]) * u, np.eye(3))
    depart = entre_cles(MAIN_DROITE, T_DECROCHE) @ REPOS @ tf((0, 0.014, 0.008), np.eye(3))
    fin = tf(FICHE_FIN[0], rot(FICHE_FIN[1]))
    u = lisse((t - T_DECROCHE) / (T_FIN - T_DECROCHE))
    m = melange(depart, fin, u)
    m[:3, 3] += np.array([-0.02, 0.035, 0.0]) * math.sin(math.pi * u)  # le câble se déroule en arc
    return m


def main_gauche(t):
    prise = fiche_monde(T_PINCE) @ np.linalg.inv(PINCE)
    if t >= T_PINCE:
        return fiche_monde(t) @ np.linalg.inv(PINCE)
    depart = tf(MAIN_GAUCHE_DEPART[0], rot(MAIN_GAUCHE_DEPART[1]))
    avant = prise @ tf((0, 0.03, 0.035), np.eye(3))  # au-dessus et en arrière, doigts ouverts
    if t <= T_DEPART_G:
        return depart
    if t <= T_APPROCHE:
        return melange(depart, avant, lisse((t - T_DEPART_G) / (T_APPROCHE - T_DEPART_G)))
    return melange(avant, prise, lisse((t - T_APPROCHE) / (T_PINCE - T_APPROCHE)))


def fiche_locale(t):
    return np.linalg.inv(entre_cles(MAIN_DROITE, t)) @ fiche_monde(t)


# ---------------------------------------------------------------- écriture du .tres

def nombres(v):
    return ", ".join(f"{x:.5g}" for x in v)


def pistes():
    temps = [i / IPS for i in range(int(round(T_FIN * IPS)) + 1)]
    sources = {"MainDroite": lambda t: entre_cles(MAIN_DROITE, t), "MainGauche": main_gauche,
               "MainDroite/Fiche": fiche_locale}
    out = []
    for chemin, f in sources.items():
        pos, rots, prec = [], [], None
        for t in temps:
            m = f(t)
            q = quat(m[:3, :3])
            if prec is not None and np.dot(prec, q) < 0:
                q = -q  # garder le plus court chemin entre deux clés
            prec = q
            pos += [t, 1, *m[:3, 3]]
            rots += [t, 1, *q]
        out.append(("position_3d", chemin, f"PackedFloat32Array({nombres(pos)})"))
        out.append(("rotation_3d", chemin, f"PackedFloat32Array({nombres(rots)})"))
    for chemin, appels in POSES.items():
        valeurs = ", ".join(f'{{"args": [&"{pose}", {fondu}], "method": &"play"}}' for _, pose, fondu in appels)
        cles = (f'{{\n"times": PackedFloat32Array({nombres([a[0] for a in appels])}),\n'
                f'"transitions": PackedFloat32Array({nombres([1] * len(appels))}),\n"values": [{valeurs}]\n}}')
        out.append(("method", chemin, cles))
    return out


def ecrire():
    lignes = ['[gd_resource type="AnimationLibrary" format=3]', "",
              '[sub_resource type="Animation" id="Animation_tirer_fiche"]',
              'resource_name = "tirer_fiche"', f"length = {T_FIN}"]
    for i, (genre, chemin, cles) in enumerate(pistes()):
        lignes += [f'tracks/{i}/type = "{genre}"', f"tracks/{i}/imported = false", f"tracks/{i}/enabled = true",
                   f'tracks/{i}/path = NodePath("{chemin}")', f"tracks/{i}/interp = 1",
                   f"tracks/{i}/loop_wrap = true", f"tracks/{i}/keys = {cles}"]
    lignes += ["", "[resource]", "_data = {", '&"tirer_fiche": SubResource("Animation_tirer_fiche")', "}", ""]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(lignes))
    print("écrit", SORTIE.relative_to(RACINE))


def echantillons(fichier):
    """Pour l'aperçu Blender : transformations (repère caméra Godot) toutes les 0,2 s."""
    out = []
    for i in range(int(T_FIN / 0.2) + 1):
        t = i * 0.2
        out.append({"t": round(t, 2), "MainDroite": entre_cles(MAIN_DROITE, t).tolist(),
                    "MainGauche": main_gauche(t).tolist(), "Fiche": fiche_monde(t).tolist(),
                    "pose_g": "pincer" if t >= T_PINCE - 0.05 else ("ouverte" if t >= T_DEPART_G else "repos")})
    Path(fichier).write_text(json.dumps(out))


if __name__ == "__main__":
    # contrôle : la main gauche tient bien la fiche pendant tout le tirage
    for t in np.linspace(T_PINCE, T_FIN, 12):
        assert np.allclose(main_gauche(t) @ PINCE, fiche_monde(t), atol=1e-6)
    ecrire()
    if "--echantillons" in sys.argv:
        echantillons(sys.argv[sys.argv.index("--echantillons") + 1])
