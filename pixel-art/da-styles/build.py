# 4 directions artistiques pour le jeu (robot dans une station spatiale).
# Même scène 128x96, mêmes formes : seuls la palette et les choix de rendu changent.
import os, sys
sys.path.insert(0, "/Users/adriencrepel/.claude/skills/pixel-art-studio/scripts")
from pixelstudio import Sprite, mix
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 128, 96

STYLES = [
    dict(key="1-neon", name="1 · Néon nocturne", desc="Sombre, contrasté, lumières cyan/magenta",
         outline="#05060d", dither=False, grime=0.0, glow=True,
         bg="#0b0d1a", floor=["#1b1f33", "#232842"], seam="#11142a", rivet="#3a4268",
         wall=["#0b0d1a", "#262c4a", "#363f68", "#4f5a8c"], hazard=None,
         acc="#3ff0ff", acc2="#ff3fa4",
         robot=["#4a5274", "#8a94b8", "#d4dcf2"], eye="#3ff0ff",
         drone=["#2b1a3a", "#5a2f6e", "#8c4fa8"], deye="#ff3fa4",
         alien=["#2e1a5c", "#5f35a8", "#9a6ae0"], aeye="#3ff0ff"),
    dict(key="2-retro", name="2 · Rétro 8-bit", desc="Peu de couleurs, aplats francs, style console",
         outline="#000000", dither=False, grime=0.0, glow=False,
         bg="#000000", floor=["#585858", "#585858"], seam="#000000", rivet="#a8a8a8",
         wall=["#000000", "#0040b8", "#0040b8", "#3cbcfc"], hazard=("#f8b800", "#000000"),
         acc="#f8b800", acc2="#e40058",
         robot=["#787878", "#bcbcbc", "#fcfcfc"], eye="#e40058",
         drone=["#7c0000", "#e40058", "#e40058"], deye="#fcfcfc",
         alien=["#005800", "#00a800", "#b8f818"], aeye="#fcfcfc"),
    dict(key="3-rouille", name="3 · Rouille & alarme", desc="Industriel, sale, inquiétant, lumière rouge",
         outline="#0d0908", dither=True, grime=0.05, glow=True,
         bg="#120c0c", floor=["#35302b", "#3f3933"], seam="#1f1a17", rivet="#5e564a",
         wall=["#1a1512", "#3e3830", "#575044", "#787060"], hazard=("#c88a2e", "#1a1512"),
         acc="#ff3b2f", acc2="#e8a33a",
         robot=["#4d463c", "#857c69", "#c2b9a0"], eye="#ff3b2f",
         drone=["#2c2a26", "#4a4740", "#6e6a5e"], deye="#ff3b2f",
         alien=["#2f3d1a", "#5a7a2a", "#9cbf4a"], aeye="#e8a33a"),
    dict(key="4-pastel", name="4 · Pastel doux", desc="Clair, propre, mignon, contours colorés",
         outline="#3b3a5c", dither=False, grime=0.0, glow=False,
         bg="#3b3a5c", floor=["#cfdaea", "#dce5f2"], seam="#aab7cf", rivet="#8e9cba",
         wall=["#5b6b94", "#8fa3c7", "#aabbdc", "#e1e9f5"], hazard=("#ffb3c6", "#8fa3c7"),
         acc="#5fd9bd", acc2="#ff9eb5",
         robot=["#a0abc8", "#e0e6f2", "#ffffff"], eye="#5fd9bd",
         drone=["#d99a4e", "#ffc46b", "#ffe3a8"], deye="#ff7f9e",
         alien=["#5fae5a", "#8fd97a", "#c8f5a8"], aeye="#3b3a5c"),
]


def char(st, w, h, draw):
    """Petit sprite avec contour, rendu en image PIL (contour 1px => marge de 1)."""
    s = Sprite(w + 2, h + 2)
    draw(s, st)
    if st["outline"]:
        s.outline(st["outline"])
    return s.composite()


def draw_robot(s, st):
    d, m, l = st["robot"]
    o = st["outline"]
    s.rect(4, 13, 6, 15, o); s.rect(10, 13, 12, 15, o)           # chenilles
    s.rect(4, 13, 6, 13, d); s.rect(10, 13, 12, 13, d)
    s.rect(3, 8, 13, 13, m)                                      # corps
    s.rect(3, 12, 13, 13, d)                                     # ombre bas du corps
    s.rect(4, 8, 12, 8, l)
    s.rect(7, 10, 9, 11, st["acc2"])                             # voyant poitrine
    s.rect(4, 2, 12, 7, l)                                       # tête
    s.rect(4, 6, 12, 7, m)
    s.px(4, 2, None); s.px(12, 2, None)
    s.rect(5, 4, 11, 5, d)                                       # visière
    s.rect(8, 4, 9, 5, st["eye"])                                # œil
    s.px(8, 1, d); s.px(8, 0, st["acc"])                         # antenne
    s.rect(14, 9, 16, 11, d); s.px(16, 10, st["acc"])            # blaster
    s.rect(1, 9, 2, 11, m)                                       # bras gauche


def draw_drone(s, st):
    d, m, l = st["drone"]
    s.ellipse(3, 3, 12, 12, d)
    s.ellipse(3, 2, 12, 10, m)
    s.rect(6, 3, 8, 3, l)                                        # reflet en haut
    s.rect(6, 6, 9, 8, st["outline"]); s.rect(7, 6, 8, 7, st["deye"])  # œil
    s.rect(0, 6, 2, 7, d); s.rect(13, 6, 15, 7, d)               # bras d'hélice
    s.rect(0, 4, 2, 4, l); s.rect(13, 4, 15, 4, l)               # hélices


def draw_alien(s, st):
    d, m, l = st["alien"]
    for x in (2, 5, 11, 14):                                     # pattes
        s.line(x, 10, x - 1 if x < 8 else x + 1, 14, d)
    s.ellipse(2, 2, 15, 12, d)
    s.ellipse(3, 2, 14, 10, m)
    s.ellipse(5, 3, 9, 5, l)                                     # dos éclairé
    s.rect(5, 7, 6, 8, st["aeye"]); s.rect(11, 7, 12, 8, st["aeye"])
    s.rect(7, 10, 10, 10, st["outline"])                         # bouche


def draw_card(s, st):
    s.rect(1, 1, 7, 5, st["acc"]); s.rect(1, 1, 7, 2, st["acc2"]); s.rect(2, 4, 3, 4, st["outline"])


def scene(st):
    s = Sprite(W, H)
    s.rect(0, 0, W - 1, H - 1, st["bg"])
    f0, f1 = st["floor"]
    # sol : dalles 16x16, damier subtil, joints, rivets
    for ty in range(2, 6):
        for tx in range(8):
            x0, y0 = tx * 16, ty * 16
            s.rect(x0, y0, x0 + 15, y0 + 15, f0 if (tx + ty) % 2 else f1)
            s.line(x0, y0, x0 + 15, y0, st["seam"]); s.line(x0, y0, x0, y0 + 15, st["seam"])
            for rx, ry in ((2, 2), (13, 2), (2, 13), (13, 13)):
                s.px(x0 + rx, y0 + ry, st["rivet"])
    if st["dither"]:  # assombrit le bas de la pièce
        s.dither(0, 80, W - 1, 95, st["seam"], f0, mix=0.35)
    if st["grime"]:
        s.noise(0, 32, W - 1, 95, st["seam"], density=st["grime"], seed=3)
        s.noise(0, 32, W - 1, 95, st["rivet"], density=st["grime"] / 3, seed=7)
    # mur : dessus sombre + face avec panneaux
    top, face, face_l, light = st["wall"]
    s.rect(0, 0, W - 1, 7, top)
    s.rect(0, 8, W - 1, 31, face)
    s.line(0, 8, W - 1, 8, light)
    for x0 in range(0, W, 16):
        s.rect(x0 + 2, 12, x0 + 13, 25, face_l)
        s.line(x0 + 2, 12, x0 + 13, 12, light)
        s.line(x0, 9, x0, 31, top)
    if st["hazard"]:  # bande de danger en bas du mur
        a, b = st["hazard"]
        for x in range(W):
            s.line(x, 28, x, 30, a if (x // 3) % 2 == 0 else b)
    s.line(0, 31, W - 1, 31, top)
    # porte (au centre) + terminal (à droite)
    s.rect(56, 8, 71, 31, top); s.rect(58, 10, 69, 31, st["seam"])
    s.line(63, 10, 63, 31, top); s.rect(60, 9, 67, 9, st["acc2"])
    s.rect(98, 13, 109, 24, top); s.rect(100, 15, 107, 21, st["acc"])
    s.line(101, 17, 105, 17, top); s.line(101, 19, 104, 19, top)
    if st["glow"]:  # halo de lumière au sol sous la porte et le terminal
        for c in (*st["floor"], st["seam"], st["rivet"]):  # teinte le sol devant la porte
            s.rect(55, 32, 72, 35, mix(c, st["acc2"], 0.30), only=c)
            s.rect(57, 36, 70, 38, mix(c, st["acc2"], 0.15), only=c)
    # ombres portées, puis personnages
    sh = st["seam"]
    for (x, y, w) in ((25, 66, 12), (90, 68, 12), (95, 85, 14)):
        s.ellipse(x, y, x + w, y + 3, sh)
    img = s.composite()
    for (fn, w, h, x, y) in ((draw_robot, 17, 16, 22, 52), (draw_drone, 16, 13, 86, 50),
                             (draw_alien, 17, 15, 93, 73), (draw_card, 9, 7, 40, 82)):
        img.alpha_composite(char(st, w, h, fn), (x, y))
    return img


SCALE = 4
boards = []
for st in STYLES:
    img = scene(st)
    img.save(f"{OUT}/{st['key']}.png")
    img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(f"{OUT}/{st['key']}_x{SCALE}.png")
    boards.append((st, img.resize((W * SCALE, H * SCALE), Image.NEAREST)))

# planche comparative 2x2 avec titres
pad, head = 24, 52
try:
    f1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
    f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
except OSError:
    f1 = f2 = ImageFont.load_default()
cw, ch = W * SCALE, H * SCALE
sheet = Image.new("RGB", (pad + 2 * (cw + pad), pad + 2 * (ch + head + pad)), "#e9e6df")
d = ImageDraw.Draw(sheet)
for i, (st, im) in enumerate(boards):
    x = pad + (i % 2) * (cw + pad)
    y = pad + (i // 2) * (ch + head + pad)
    d.text((x, y), st["name"], fill="#1a1a1a", font=f1)
    d.text((x, y + 28), st["desc"], fill="#555555", font=f2)
    sheet.paste(im, (x, y + head))
sheet.save(f"{OUT}/comparatif.png")
print("ok")
