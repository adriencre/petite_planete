"""Thème d'Aube, version provisoire : la boîte à musique de sa chambre (ILE_03_COLONIE.md).

Quelques notes fragiles, en la mineur, comme une berceuse. La vraie musique sera faite sur acemusic.ai
(voir .agents/procedures/audio.md) et remplacera ce fichier en gardant son nom.

Lancer :  python tools/audio/theme_aube.py   ->  assets/audio/theme_aube.wav
"""
import numpy as np

from generer_sons import SR, boite_a_musique, ecrire, note, poser, reverb_circulaire

BPM = 63
TEMPS = 60.0 / BPM

# (note, début en temps, force). Deux phrases de quatre mesures ; la seconde se ralentit et s'arrête,
# comme un ressort qui se détend.
MELODIE = [
    ("E5", 0, 1.0), ("A5", 1, .9), ("C6", 2, .8), ("B5", 3, .7),
    ("A5", 4, .9), ("E5", 5, .7), ("G5", 6, .8), ("F5", 7.5, .6),
    ("E5", 8, .9), ("D5", 9, .7), ("C5", 10, .8), ("D5", 11, .6),
    ("E5", 12, 1.0), ("A4", 14, .7),
    ("E5", 16, .9), ("A5", 17, .8), ("C6", 18, .8), ("B5", 19, .7),
    ("A5", 20.2, .8), ("G5", 21.4, .7), ("E5", 22.7, .7),
    ("D5", 24.1, .6), ("C5", 25.6, .6), ("B4", 27.2, .5), ("A4", 29.0, .55),
]
# Une note grave par mesure, plus discrète.
BASSES = [("A3", 0), ("F3", 4), ("C4", 8), ("E3", 12), ("A3", 16), ("F3", 20), ("D3", 24), ("A3", 28.9)]


def theme():
    duree = 34 * TEMPS + 0.7
    piste = np.zeros((int(duree * SR), 2))
    for nom, temps, force in MELODIE:
        poser(piste, boite_a_musique(note(nom), 2.4, force), 0.7 + temps * TEMPS, 1.0, -0.15)
    for nom, temps in BASSES:
        poser(piste, boite_a_musique(note(nom), 3.0, 0.5), 0.7 + temps * TEMPS, 0.55, 0.2)
    # le mécanisme : un léger cliquetis au début, comme quand on remonte la boîte
    t = np.arange(int(0.6 * SR)) / SR
    tic = np.zeros_like(t)
    for k in range(6):
        i = int(k * 0.09 * SR)
        tic[i:i + 300] += np.random.default_rng(k).standard_normal(300) * np.exp(-np.arange(300) / 60)
    poser(piste, tic * 0.15, 0.0, 1.0, 0.1)
    ecrire("theme_aube", reverb_circulaire(piste, 2.4, 0.3), 0.7)


if __name__ == "__main__":
    theme()
