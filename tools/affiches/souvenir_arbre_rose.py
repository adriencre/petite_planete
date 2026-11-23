"""Les images du souvenir de la lampe-mère (G3) : le disque de verre peint, comme une lanterne magique.

Cinq tableaux, projetés l'un après l'autre sur le mur blanc du jardin du haut pendant le chant :
  1. des Semeurs arrivent, l'un porte un tout petit arbre rose dans un pot ;
  2. ils creusent ;
  3. ils plantent l'arbre, à genoux ;
  4. ils chantent autour, les têtes-lanternes levées ;
  5. l'arbre a grandi, immense et rose ; les Semeurs sont tout petits dessous.
Fond noir = pas de lumière (l'écran est en mélange additif) ; disque de lumière chaude, silhouettes sombres
teintées comme du verre peint. Lancer : python tools/affiches/souvenir_arbre_rose.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parents[2]
T = 768
LUMIERE = (255, 214, 150)
VERRE = (120, 58, 72)          # silhouettes : prune
ROSE = (255, 150, 175)
TETE = (255, 236, 190)


def fond():
    img = Image.new("RGB", (T, T), (0, 0, 0))
    d = ImageDraw.Draw(img)
    # disque de lumière, plus chaud au centre ; un anneau de laiton sombre autour
    for k in range(60, 0, -1):
        r = T * .46 * k / 60
        f = .55 + .45 * (1 - k / 60)
        d.ellipse((T/2-r, T/2-r, T/2+r, T/2+r), fill=tuple(int(c*f) for c in LUMIERE))
    d.ellipse((T*.04, T*.04, T*.96, T*.96), outline=(70, 45, 30), width=10)
    # le sol
    d.rectangle((0, T*.72, T, T), fill=(150, 96, 70))
    masque = Image.new("L", (T, T), 0)
    ImageDraw.Draw(masque).ellipse((T*.045, T*.045, T*.955, T*.955), fill=255)
    noir = Image.new("RGB", (T, T), (0, 0, 0))
    return Image.composite(img, noir, masque), masque


def semeur(d, x, sol, h=1.0, pose="debout", lanterne=True):
    """Un Semeur : très grand, très fin, une tête-lanterne ronde qui luit."""
    H = 230 * h
    l = 14 * h
    if pose == "genou":
        H *= .62
    corps = [(x-l, sol), (x+l, sol), (x+l*.7, sol-H*.78), (x-l*.7, sol-H*.78)]
    d.polygon(corps, fill=VERRE)
    # bras longs
    if pose == "chante":
        d.line((x-l*.5, sol-H*.7, x-l*4, sol-H*1.0), fill=VERRE, width=int(7*h))
        d.line((x+l*.5, sol-H*.7, x+l*4, sol-H*1.0), fill=VERRE, width=int(7*h))
    elif pose == "creuse":
        d.line((x+l*.5, sol-H*.7, x+l*3.5, sol-H*.35), fill=VERRE, width=int(7*h))
        d.line((x+l*3.5, sol-H*.35, x+l*5.0, sol+4), fill=VERRE, width=int(5*h))   # la bêche
        d.polygon([(x+l*4.6, sol-8), (x+l*5.6, sol-8), (x+l*5.3, sol+10), (x+l*4.9, sol+10)], fill=VERRE)
    else:
        d.line((x-l*.6, sol-H*.7, x-l*1.4, sol-H*.3), fill=VERRE, width=int(7*h))
        d.line((x+l*.6, sol-H*.7, x+l*1.4, sol-H*.3), fill=VERRE, width=int(7*h))
    # cou et tête-lanterne
    d.line((x, sol-H*.78, x, sol-H*.9), fill=VERRE, width=int(5*h))
    r = 17 * h
    cy = sol - H*.9 - r
    d.ellipse((x-r-4, cy-r-4, x+r+4, cy+r+4), fill=VERRE)
    if lanterne:
        d.ellipse((x-r*.7, cy-r*.7, x+r*.7, cy+r*.7), fill=TETE)
    return (x+l*1.4, sol-H*.3)


def petit_arbre(d, x, sol, taille=1.0, pot=True):
    if pot:
        d.polygon([(x-16, sol), (x+16, sol), (x+22, sol-26), (x-22, sol-26)], fill=VERRE)
        sol -= 26
    d.line((x, sol, x, sol-40*taille), fill=VERRE, width=5)
    for dx, dy, r in ((0, -48, 20), (-14, -40, 14), (14, -40, 14)):
        d.ellipse((x+dx*taille-r*taille, sol+dy*taille-r*taille, x+dx*taille+r*taille, sol+dy*taille+r*taille), fill=ROSE)


def notes(d, x, y):
    for k, (dx, dy) in enumerate(((0, 0), (40, -30), (85, -10))):
        cx, cy = x+dx, y+dy
        d.ellipse((cx-9, cy-7, cx+9, cy+7), fill=VERRE)
        d.line((cx+8, cy, cx+8, cy-34), fill=VERRE, width=4)


def grand_arbre(d, x, sol):
    d.polygon([(x-26, sol), (x+26, sol), (x+12, sol-250), (x-12, sol-250)], fill=VERRE)
    for dx, dy, r in ((0, -330, 120), (-120, -270, 85), (120, -270, 85), (-60, -380, 80), (70, -390, 80)):
        d.ellipse((x+dx-r, sol+dy-r, x+dx+r, sol+dy+r), fill=ROSE)
    for dx, dy, r in ((-40, -300, 40), (60, -320, 34), (0, -390, 30)):
        d.ellipse((x+dx-r, sol+dy-r, x+dx+r, sol+dy+r), fill=(255, 185, 200))


def tableau(n):
    img, masque = fond()
    d = ImageDraw.Draw(img)
    sol = T * .72
    if n == 1:
        semeur(d, T*.3, sol, 1.0)
        main = semeur(d, T*.5, sol, 1.05)
        petit_arbre(d, main[0]+6, main[1]+30, .9)
        semeur(d, T*.68, sol, .95)
    elif n == 2:
        semeur(d, T*.36, sol, 1.0, "creuse")
        semeur(d, T*.6, sol, 1.0, "creuse")
        d.ellipse((T*.44, sol-12, T*.58, sol+22), fill=(70, 40, 35))
        petit_arbre(d, T*.78, sol, .9)
    elif n == 3:
        semeur(d, T*.36, sol, 1.0, "genou")
        semeur(d, T*.64, sol, 1.0, "genou")
        petit_arbre(d, T*.5, sol, 1.1, pot=False)
    elif n == 4:
        for k, x in enumerate((.22, .38, .62, .78)):
            semeur(d, T*x, sol, .92 + .05*(k % 2), "chante")
        petit_arbre(d, T*.5, sol, 1.2, pot=False)
        notes(d, T*.36, T*.2)
    else:
        grand_arbre(d, T*.52, sol)
        for x in (.3, .42, .7):
            semeur(d, T*x, sol, .45)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    noir = Image.new("RGB", (T, T), (0, 0, 0))
    img = Image.composite(img, noir, masque)
    img.save(RACINE/f"assets/affiches/souvenir_arbre_rose_{n}.png")


if __name__ == "__main__":
    for n in range(1, 6):
        tableau(n)
    print("5 images dans assets/affiches/souvenir_arbre_rose_*.png")
