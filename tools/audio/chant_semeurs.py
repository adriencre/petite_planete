"""Le chant des Semeurs, version provisoire : le cylindre musical dans le socle de la lampe-mère (G3).

Un chant de chez eux, qu'ils chantaient en plantant le premier arbre rose : une mélodie lente et large,
en ré majeur pentatonique, jouée par le cylindre (timbre de boîte à musique, plus grave que celui d'Aube,
un écho de sa boîte). La vraie musique sera faite sur acemusic.ai (voir .agents/procedures/audio.md)
et remplacera ce fichier en gardant son nom.

Lancer :  python tools/audio/chant_semeurs.py   ->  assets/audio/chant_semeurs.wav
"""
import numpy as np

from generer_sons import SR, boite_a_musique, ecrire, note, poser, reverb_circulaire

BPM = 56
TEMPS = 60.0 / BPM

# (note, début en temps, force) : trois phrases ; la dernière revient à la première et se pose.
MELODIE = [
    ("D5", 0, 1.0), ("E5", 1, .8), ("F#5", 2, .9), ("A5", 3.5, .9),
    ("F#5", 5, .8), ("E5", 6, .7), ("D5", 7, .9),
    ("A4", 8, .8), ("B4", 9, .7), ("D5", 10, .9), ("E5", 11.5, .8),
    ("F#5", 13, .9), ("E5", 14, .7), ("B4", 15, .8),
    ("D5", 16, 1.0), ("E5", 17, .8), ("F#5", 18, .9), ("B5", 19.5, .9),
    ("A5", 21, .9), ("F#5", 22.2, .8), ("E5", 23.4, .7), ("D5", 25, .9),
]
BASSES = [("D3", 0), ("G3", 4), ("D3", 8), ("B2", 12), ("D3", 16), ("G3", 20), ("A3", 23), ("D3", 25)]


def chant():
    duree = 30 * TEMPS + 1.0
    piste = np.zeros((int(duree * SR), 2))
    for nom, temps, force in MELODIE:
        poser(piste, boite_a_musique(note(nom), 3.0, force), 0.8 + temps * TEMPS, 1.0, -0.1)
        # une voix d'octave plus bas, discrète : comme si plusieurs chantaient
        poser(piste, boite_a_musique(note(nom) / 2, 3.0, force * .35), 0.82 + temps * TEMPS, .5, .15)
    for nom, temps in BASSES:
        poser(piste, boite_a_musique(note(nom), 4.0, 0.5), 0.8 + temps * TEMPS, 0.6, 0.2)
    ecrire("chant_semeurs", reverb_circulaire(piste, 3.0, 0.35), 0.8)


if __name__ == "__main__":
    chant()
