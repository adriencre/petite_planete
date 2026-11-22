"""Bruitages de la Colonie (île 3), par synthèse, dans assets/audio/.

Lancer :  python tools/audio/sons_ile_03.py

- porte_bloquee : on pousse la porte de l'étage d'Aube, elle cogne deux fois contre la barre.
- barre : la barre de bois qu'on soulève de ses crochets et qu'on pose contre le mur.
"""
import numpy as np

from generer_sons import SR, ecrire, filtre_spectral, reverb_circulaire

rng = np.random.default_rng(31)


def coup_de_bois(force=1.0, grave=95.0):
    """Un choc sourd de bois massif : un corps grave qui s'éteint vite et un claquement filtré."""
    d = 0.5
    t = np.arange(int(d * SR)) / SR
    corps = np.sin(2 * np.pi * grave * t) * np.exp(-t * 22) + 0.5 * np.sin(2 * np.pi * grave * 2.3 * t) * np.exp(-t * 35)
    claque = filtre_spectral(rng.standard_normal(len(t)), f_bas=300, f_haut=2500) * np.exp(-t * 60) * 0.5
    return (corps + claque) * force


def porte_bloquee():
    piste = np.zeros(int(1.6 * SR))
    for debut, force in ((0.0, 1.0), (0.32, 0.7)):
        c = coup_de_bois(force)
        i = int(debut * SR)
        piste[i:i + len(c)] += c
    # le cliquetis de la barre dans ses crochets
    t = np.arange(int(0.3 * SR)) / SR
    cliquetis = filtre_spectral(rng.standard_normal(len(t)), f_bas=1500, f_haut=6000) * np.exp(-t * 25) * 0.15
    i = int(0.05 * SR)
    piste[i:i + len(cliquetis)] += cliquetis
    ecrire("porte_bloquee", reverb_circulaire(piste, 1.2, 0.2), 0.7)


def barre():
    d = 2.4
    piste = np.zeros(int(d * SR))
    # la barre glisse hors des crochets : un frottement de bois qui monte
    t = np.arange(int(0.7 * SR)) / SR
    frottement = filtre_spectral(rng.standard_normal(len(t)), f_bas=200, f_haut=1800)
    frottement *= np.sin(np.pi * t / t[-1]) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    piste[:len(frottement)] += frottement * 0.35
    # posée contre le mur : deux petits chocs
    for debut, force in ((1.55, 0.6), (1.72, 0.3)):
        c = coup_de_bois(force, 140.0)
        i = int(debut * SR)
        piste[i:i + len(c)] += c[:len(piste) - i]
    ecrire("barre", reverb_circulaire(piste, 1.0, 0.18), 0.6)


if __name__ == "__main__":
    porte_bloquee()
    barre()
