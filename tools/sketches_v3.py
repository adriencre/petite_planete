# Croquis du carnet v3 (trait blanc sur fond transparent, teinté à l'encre dans le jeu).
# python tools/sketches_v3.py
import math, random
from PIL import Image, ImageDraw

OUT = "assets/textures/story/"
ICONS = "assets/ui/map_icons/"
W = (255, 255, 255, 255)


def shaky(d, pts, width=4, jitter=1.6, seed=0, closed=False):
    rnd = random.Random(seed)
    if closed:
        pts = pts + [pts[0]]
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 6))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-jitter, jitter), y0 + (y1 - y0) * t + rnd.uniform(-jitter, jitter)))
    out.append(pts[-1])
    d.line(out, fill=W, width=width, joint="curve")


def arc_pts(cx, cy, rx, ry, a0, a1, n=40):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def jellyfish():
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # cloche
    shaky(d, arc_pts(128, 112, 62, 52, 180, 360), 5, seed=1)
    shaky(d, [(66, 112), (82, 118), (98, 112), (114, 119), (128, 112), (142, 119), (158, 112), (174, 118), (190, 112)], 4, seed=2)
    # cœur lumineux + petits rayons (elle brille)
    shaky(d, arc_pts(128, 92, 14, 12, 0, 360, 24), 3, seed=3)
    for a in range(0, 360, 45):
        r0, r1 = 20, 28
        x, y = math.cos(math.radians(a)), math.sin(math.radians(a))
        shaky(d, [(128 + x * r0, 92 + y * r0 * 0.85), (128 + x * r1, 92 + y * r1 * 0.85)], 2, jitter=0.6, seed=a)
    # tentacules ondulants
    for i, x0 in enumerate([84, 104, 128, 152, 172]):
        pts = [(x0 + math.sin(t / 9 + i) * 7, 120 + t) for t in range(0, 100, 6)]
        shaky(d, pts, 3, jitter=0.8, seed=10 + i)
    # petits points de brume autour
    rnd = random.Random(7)
    for _ in range(14):
        x, y = rnd.uniform(20, 236), rnd.uniform(20, 236)
        if math.hypot(x - 128, y - 130) > 90:
            d.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=W)
    im.save(OUT + "sketch_lueur_meduse.png")


def body():
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # sol + mousse
    shaky(d, [(30, 206), (226, 206)], 4, seed=1)
    for x in range(44, 216, 14):
        shaky(d, [(x, 206), (x + 4, 198), (x + 8, 206)], 2, jitter=0.5, seed=x)
    # corps assis, affaissé
    shaky(d, [(96, 204), (100, 146), (156, 146), (160, 204)], 5, seed=2)
    # bras pendants
    shaky(d, [(100, 154), (84, 190), (90, 200)], 4, seed=3)
    shaky(d, [(156, 154), (170, 190), (164, 200)], 4, seed=4)
    # tête penchée en avant
    head = [(104, 104), (160, 92), (170, 138), (114, 150)]
    shaky(d, head, 5, seed=5, closed=True)
    shaky(d, [(118, 116), (154, 108), (158, 126), (122, 134)], 3, seed=6, closed=True)  # visière éteinte
    # antenne tombante
    shaky(d, [(140, 96), (152, 72), (170, 64)], 3, seed=7)
    d.ellipse([166, 58, 178, 70], outline=W, width=3)
    # « ? » discret du robot, à côté
    shaky(d, arc_pts(206, 92, 11, 11, 200, 400, 16), 3, seed=8)
    shaky(d, [(206, 103), (206, 113)], 3, seed=9)
    d.ellipse([203, 120, 209, 126], fill=W)
    im.save(OUT + "sketch_body.png")


def body_icon():
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    shaky(d, [(18, 50), (20, 32), (44, 32), (46, 50)], 4, jitter=0.4, seed=1)
    shaky(d, [(20, 14), (42, 10), (46, 28), (24, 32)], 4, jitter=0.4, seed=2, closed=True)
    im.save(ICONS + "body.png")


def page_icon():
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    shaky(d, [(16, 10), (42, 10), (50, 18), (50, 54), (16, 54)], 4, jitter=0.4, seed=1, closed=True)
    for y in (24, 32, 40):
        shaky(d, [(23, y), (43, y)], 3, jitter=0.4, seed=y)
    im.save(ICONS + "page.png")


def dark_icon():
    # petit croissant de lune : « vu dans le noir »
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    outer = arc_pts(32, 32, 22, 22, 60, 300, 30)
    inner = arc_pts(42, 28, 16, 16, 260, 100, 24)
    shaky(d, outer + inner, 4, jitter=0.4, seed=3, closed=True)
    for (x, y) in [(50, 46), (54, 18)]:
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=W)
    im.save(ICONS + "dark.png")


def night_sketch():
    # vieux croquis-indice : un robot antenne éteinte, sous la lune, entouré de Lueurs ; une touche « N » dans le coin
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    shaky(d, [(40, 214), (216, 214)], 4, seed=1)
    # robot debout, tête un peu baissée
    shaky(d, [(104, 212), (106, 160), (150, 160), (152, 212)], 5, seed=2)
    shaky(d, [(98, 112), (154, 108), (158, 156), (102, 160)], 5, seed=3, closed=True)
    shaky(d, [(110, 126), (146, 123), (148, 142), (112, 145)], 3, seed=4, closed=True)
    # antenne : ampoule vide (éteinte), barrée d'un petit trait
    shaky(d, [(128, 110), (128, 84)], 3, seed=5)
    d.ellipse([120, 70, 136, 86], outline=W, width=3)
    # lune
    shaky(d, arc_pts(196, 56, 22, 22, 60, 300, 30) + arc_pts(206, 52, 16, 16, 260, 100, 24), 4, jitter=0.6, seed=6, closed=True)
    # Lueurs tout autour (petits cercles avec rayons)
    rnd = random.Random(11)
    for (x, y) in [(56, 120), (72, 168), (184, 140), (200, 186), (60, 70), (172, 96), (86, 196)]:
        r = rnd.uniform(4, 7)
        d.ellipse([x - r, y - r, x + r, y + r], outline=W, width=2)
        for a in range(0, 360, 90):
            dx, dy = math.cos(math.radians(a + 45)), math.sin(math.radians(a + 45))
            shaky(d, [(x + dx * (r + 3), y + dy * (r + 3)), (x + dx * (r + 7), y + dy * (r + 7))], 2, jitter=0.3, seed=x + a)
    # la touche N, griffonnée en bas à gauche
    shaky(d, [(18, 22), (58, 20), (60, 60), (20, 62)], 3, jitter=0.8, seed=12, closed=True)
    shaky(d, [(30, 52), (30, 30), (48, 52), (48, 30)], 4, jitter=0.5, seed=13)
    im.save(OUT + "sketch_night.png")


night_sketch()
dark_icon()
jellyfish()
body()
body_icon()
page_icon()
print("ok")
