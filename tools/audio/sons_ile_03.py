"""Bruitages de la Colonie (île 3), par synthèse, dans assets/audio/.

Lancer :  python tools/audio/sons_ile_03.py

- porte_bloquee : on pousse la porte de l'étage d'Aube, elle cogne deux fois contre la barre.
- barre : la barre de bois qu'on soulève de ses crochets et qu'on pose contre le mur.
- carillon : le carillon des marées du quai, trois tubes qui sonnent au plus haut de la marée (G3).
- cloche : la cloche-relais au pied de l'écluse, une seule note, plus grave.
- chaine : une vanne-guillotine de l'écluse qu'on lève ou qu'on baisse (chaîne et poulie).
- eau_sas : l'eau de la citerne qui remplit un sas (grondement doux qui monte puis s'apaise).
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


def tube(freq, duree, force=1.0):
    """Un tube de carillon : partiels inharmoniques, attaque nette, longue résonance."""
    t = np.arange(int(duree * SR)) / SR
    son = np.zeros_like(t)
    for rapport, gain, amorti in ((1.0, 1.0, 1.1), (2.76, .5, 2.0), (5.40, .25, 3.5), (8.93, .12, 5.0)):
        son += gain * np.sin(2 * np.pi * freq * rapport * t) * np.exp(-t * amorti)
    attaque = np.minimum(1.0, t / 0.004)
    return son * attaque * force


def carillon():
    piste = np.zeros(int(6.5 * SR))
    # trois tubes, du plus aigu au plus grave, puis les trois ensemble
    for debut, freq, force in ((0.0, 784.0, 1.0), (0.55, 659.3, .9), (1.1, 523.3, .9),
                               (2.2, 784.0, .6), (2.2, 659.3, .6), (2.2, 523.3, .7)):
        c = tube(freq, 4.0, force)
        i = int(debut * SR)
        piste[i:i + len(c)] += c[:len(piste) - i]
    ecrire("carillon", reverb_circulaire(piste, 2.4, 0.3), 0.75)


def cloche():
    piste = np.zeros(int(5.0 * SR))
    for debut in (0.0, 1.6):
        c = tube(392.0, 3.4, 1.0 if debut == 0 else .7)
        i = int(debut * SR)
        piste[i:i + len(c)] += c[:len(piste) - i]
    ecrire("cloche", reverb_circulaire(piste, 2.0, 0.3), 0.7)


def chaine():
    d = 2.6
    t = np.arange(int(d * SR)) / SR
    piste = np.zeros(len(t))
    # les maillons qui passent sur la poulie : petits chocs métalliques réguliers
    for k in range(int(d * 11)):
        debut = k / 11 + rng.uniform(-.01, .01)
        if debut > d - .2:
            break
        n = int(.06 * SR)
        tt = np.arange(n) / SR
        choc = filtre_spectral(rng.standard_normal(n), f_bas=1200, f_haut=5000) * np.exp(-tt * 70)
        choc += .4 * np.sin(2 * np.pi * rng.uniform(900, 1300) * tt) * np.exp(-tt * 40)
        i = int(debut * SR)
        piste[i:i + n] += choc * rng.uniform(.4, .8)
    # le grincement grave de la vanne dans sa rainure
    grince = filtre_spectral(rng.standard_normal(len(t)), f_bas=90, f_haut=500) * .35
    piste += grince * np.sin(np.pi * t / d) ** 2
    ecrire("chaine", reverb_circulaire(piste, 1.0, 0.2), 0.55)


def eau_sas():
    d = 6.0
    t = np.arange(int(d * SR)) / SR
    enveloppe = np.minimum(1.0, t / 1.2) * np.minimum(1.0, (d - t) / 2.0)
    gronde = filtre_spectral(rng.standard_normal(len(t)), f_bas=60, f_haut=700) * enveloppe
    clapot = filtre_spectral(rng.standard_normal(len(t)), f_bas=800, f_haut=3500) * enveloppe * .25
    clapot *= .6 + .4 * np.sin(2 * np.pi * 3.1 * t)
    ecrire("eau_sas", reverb_circulaire(gronde + clapot, 1.5, 0.25), 0.6)


if __name__ == "__main__":
    porte_bloquee()
    barre()
    carillon()
    cloche()
    chaine()
    eau_sas()
