"""Ébauche du motif du Phare à partir des premières notes de la couche 3 du Réveil."""
import argparse
from pathlib import Path
import sys
import wave

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generer_sons import MELODIE, SR, note, piano, poser, reverb_circulaire

TEMPS = 1.0
DUREE = 32


def corde(nom, duree, phase):
    t = np.arange(round(duree * SR)) / SR
    attaque = np.sin(np.minimum(t / 1.35, 1) * np.pi / 2)
    relache = np.sin(np.minimum((duree - t) / 1.7, 1) * np.pi / 2)
    vibrato = 0.35 * np.sin(2 * np.pi * 4.3 * t + phase)
    voix = 2 * np.pi * note(nom) * t + vibrato + phase
    son = np.sin(voix) + 0.31 * np.sin(2 * voix) + 0.10 * np.sin(3 * voix)
    return son * attaque * relache * 0.13


def couches():
    pistes = [np.zeros((round(DUREE * SR), 2)) for _ in range(4)]
    for temps, nom, duree in MELODIE[:12]:
        grave = nom[:-1] + str(int(nom[-1]) - 1)
        poser(pistes[0], piano(note(grave), 2.0 + duree * 0.45, 0.48), temps * TEMPS, pan=-0.08)
    accords = (("D2", "A2", "E3"), ("B1", "F#2", "D3"), ("G2", "D3", "F#3"), ("A2", "E3", "B3"))
    for i, (basse, quinte, couleur) in enumerate(accords):
        debut = i * 8 * TEMPS
        poser(pistes[1], piano(note(quinte), 5.2, 0.28), debut + 0.12, pan=0.12)
        poser(pistes[2], corde(basse, 8.9, 0.5), debut, gain=0.48, pan=-0.25)
        poser(pistes[2], corde(quinte, 8.0, 1.6), debut + 0.5, gain=0.23, pan=0.2)
        poser(pistes[3], corde(couleur, 7.0, 2.3), debut + 1.2, gain=0.38, pan=0.38)
    return [reverb_circulaire(piste, duree=2.6, mouille=0.26) for piste in pistes]


def ecrire(chemin, signal):
    with wave.open(str(chemin), "wb") as wav:
        wav.setparams((2, 2, SR, 0, "NONE", "not compressed"))
        wav.writeframes((np.clip(signal, -1, 1) * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("sortie", type=Path)
    args = cli.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)
    for i, piste in enumerate(couches(), 1):
        ecrire(args.sortie / f"phare_couche_{i}.wav", piste)
