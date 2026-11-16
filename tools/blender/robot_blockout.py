# Blockout du robot « Graine » : volumes simples aux bonnes cotes (concaténer après helpers.py + robot_cotes.py).
clear_scene()
G = mat("blockout", "#c98a56", 0.6)
N = mat("blockout_noyau", "#4a3e48", 0.6)
L = mat("blockout_lumiere", "#ffe0a8", 0.3, emit="#ffc06a", strength=5.0)

E = {"Robot": empty("Robot")}
for name, p in PIVOTS.items():
    e = empty(name)
    par = PARENT[name]
    e.parent = E[par]
    e.location = p - (PIVOTS[par] if par in PIVOTS else V((0, 0, 0)))
    E[name] = e


def at(o, piv):
    o.data.transform(Matrix.Translation(-PIVOTS[piv]))
    o.parent = E[piv]
    o.location = (0, 0, 0)
    return o


def el(name, c, r, m, piv):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    for v in bm.verts:
        v.co = V((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2])) + V(c)
    return at(obj_from_bm(name, bm, m), piv)


def rd(name, a, b, r, m, piv):
    return at(tube(name, [V(a), V(b)], [r, r * 0.9], m, None, 12), piv)


# tête, cou, antenne
el("tete", TETE[0], TETE[1], G, "Tete")
el("fente", TETE[0] + V((0, -0.11, 0.0)), (0.09, 0.02, 0.012), L, "Tete")
rd("cou", (0, 0, 1.6), (0, -0.01, 1.7), 0.02, N, "Tete")
ant = bez(V((0, 0.06, 1.88)), V((0, 0.0, 2.08)), V((0, -0.24, 2.0)), 16) + bez(V((0, -0.24, 2.0)), V((0, -0.27, 1.97)), V((0, -0.27, 1.91)), 6)[1:]
at(tube("antenne", ant, [0.008] * len(ant), N, None, 8), "Tete")
el("cloche", (0, -0.27, 1.885), (0.03, 0.03, 0.035), L, "Tete")
# torse : cœur + épaulettes + taille
el("torse", TORSE[0], TORSE[1], G, "Torse")
for s in (-1, 1):
    el("epaulette", (s * 0.19, 0.0, 1.56), (0.085, 0.08, 0.06), G, "Torse")
rd("colonne", (0, 0, 1.18), (0, 0, 1.3), 0.03, N, "Torse")
# jupe : cône pointu vers le bas
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.06, radius2=0.12, depth=0.33, matrix=Matrix.Translation((0, 0, 1.07)))
at(obj_from_bm("jupe", bm, G), "Bassin")
# bras et jambes
for s, c in ((-1, "D"), (1, "G")):
    sh, el_, wr = PIVOTS["Epaule_" + c], PIVOTS["Coude_" + c], PIVOTS["Poignet_" + c]
    el("rot_epaule", sh, (0.04, 0.04, 0.04), N, "Epaule_" + c)
    rd("humerus", sh, el_, 0.018, G, "Epaule_" + c)
    el("rot_coude", el_, (0.032, 0.032, 0.032), N, "Coude_" + c)
    rd("avant_bras", el_, wr, 0.03, G, "Coude_" + c)
    rd("main", wr, wr + V((0, -0.02, -MAIN_LONG)), 0.022, G, "Poignet_" + c)
    if c == "D":
        el("enrouleur", el_.lerp(wr, 0.4) + V((-0.045, 0, 0)), (0.025, 0.05, 0.05), N, "Coude_D")
    hp, kn, an = PIVOTS["Hanche_" + c], PIVOTS["Genou_" + c], PIVOTS["Cheville_" + c]
    rd("cuisse", hp, kn, 0.035, G, "Hanche_" + c)
    el("rot_genou", kn, (0.04, 0.04, 0.04), N, "Genou_" + c)
    rd("tibia", kn, an, 0.04, G, "Genou_" + c)
    el("rot_cheville", an, (0.03, 0.03, 0.03), N, "Cheville_" + c)
    f = PIED
    el("pied", an + V((0, -(f["long_avant"] - f["long_arriere"]) / 2, -0.1)), (f["larg"], (f["long_avant"] + f["long_arriere"]) / 2, f["haut"] / 1.6), G, "Cheville_" + c)
print("BLOCKOUT OK")
