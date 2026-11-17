"""Fabrique tous les sons de l'île 1 par synthèse (numpy seul), dans assets/audio/.

Lancer :  python tools/audio/generer_sons.py

- Ambiance (boucles sans couture, tout est calculé « en cercle ») : vent, vagues.
- Oiseaux : quelques chants courts, joués au hasard.
- Musique : un morceau calme en ré majeur, 72 bpm, 8 mesures, découpé en 4 couches de même durée qui
  se superposent (chaque lanterne allumée en ajoute une) :
    couche_1 accords de piano, couche_2 arpège, couche_3 mélodie (boîte à musique), couche_4 nappe.
- Effets : clic de la prise, allumage d'une lanterne, recharge, luciole, page, extinction du robot.

Tout est en WAV 16 bits, 44,1 kHz, stéréo.
"""
import os
import wave
import numpy as np

SR = 44100
DOSSIER = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "audio")
rng = np.random.default_rng(7)

BPM = 72
TEMPS = 60.0 / BPM
MESURE = 4 * TEMPS
LONGUEUR_MUSIQUE = 8 * MESURE          # ≈ 26,7 s


# ------------------------------------------------------------------ outils

def ecrire(nom, signal, volume=0.9):
    """signal : (n,) mono ou (n, 2) stéréo, en float. Normalisé puis écrit en 16 bits."""
    if signal.ndim == 1:
        signal = np.stack([signal, signal], axis=1)
    crete = np.max(np.abs(signal)) or 1.0
    s = np.clip(signal / crete * volume, -1, 1)
    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, nom + ".wav")
    with wave.open(chemin, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((s * 32767).astype("<i2").tobytes())
    print(f"{nom}.wav  {len(signal) / SR:5.1f} s")


def note(nom):
    """'D4' -> fréquence (A4 = 440 Hz)."""
    noms = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    lettre, octave = nom[:-1], int(nom[-1])
    return 440.0 * 2 ** ((noms[lettre] + 12 * (octave - 4)) / 12)


def filtre_spectral(x, f_bas=None, f_haut=None, pente=1.0):
    """Filtre en fréquence (circulaire : la boucle reste sans couture). f_bas = passe-haut, f_haut = passe-bas."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if f_haut:
        g /= (1 + (f / f_haut) ** (2 * pente))
    if f_bas:
        g *= 1 - 1 / (1 + (f / f_bas) ** (2 * pente))
    if x.ndim == 2:
        g = g[:, None]
    return np.fft.irfft(X * g, n=len(x), axis=0)


def bruit_rose(n, canaux=2):
    X = np.fft.rfft(rng.standard_normal((n, canaux)), axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = 1
    return np.fft.irfft(X / np.sqrt(f)[:, None], n=n, axis=0)


def reverb_circulaire(x, duree=2.8, mouille=0.35):
    """Réverbération par convolution circulaire avec une réponse de bruit qui décroît : la queue
    de fin de boucle retombe au début, la boucle reste parfaite."""
    n = len(x)
    t = np.arange(min(int(duree * SR), n)) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        r = rng.standard_normal(len(t)) * np.exp(-t * 6.9 / duree)
        r = filtre_spectral(r, f_haut=5000)
        ir[:len(t), c] = r
    ir /= np.sqrt(np.sum(ir ** 2, axis=0))
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    sec = x
    hum = np.fft.irfft(np.fft.rfft(x, axis=0) * np.fft.rfft(ir, axis=0), n=n, axis=0)
    return sec * (1 - mouille) + hum * mouille * 3.0


def poser(piste, son, debut_s, gain=1.0, pan=0.0):
    """Ajoute `son` (mono) dans `piste` (stéréo, circulaire) à `debut_s`, panoramique -1..1."""
    n = len(piste)
    i0 = int(debut_s * SR) % n
    idx = (np.arange(len(son)) + i0) % n
    g = np.array([np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))])
    np.add.at(piste, idx, son[:, None] * g[None, :] * gain)


# ------------------------------------------------------------------ instruments

def piano(freq, duree=3.5, force=1.0):
    """Piano doux : harmoniques qui s'éteignent d'autant plus vite qu'elles sont hautes, léger marteau."""
    t = np.arange(int(duree * SR)) / SR
    s = np.zeros_like(t)
    for k in range(1, 9):
        fk = freq * k * np.sqrt(1 + 0.0004 * k * k)        # légère inharmonicité
        if fk > 12000:
            break
        amp = (0.6 ** (k - 1)) * (1.0 if k > 1 else 1.2)
        s += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + 0.55 * k) * (0.8 + freq / 900))
    attaque = np.minimum(t / 0.004, 1.0)
    marteau = rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.04
    fin = np.minimum((duree - t) / 0.3, 1.0)
    return (s * attaque + marteau) * fin * force * 0.3


def boite_a_musique(freq, duree=2.5, force=1.0):
    """Cloche douce : partiels inharmoniques de lame, décroissance rapide."""
    t = np.arange(int(duree * SR)) / SR
    s = np.zeros_like(t)
    for ratio, amp, dec in [(1.0, 1.0, 2.2), (2.76, 0.35, 5.0), (5.40, 0.12, 9.0), (8.93, 0.05, 14.0)]:
        s += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t * dec)
    attaque = np.minimum(t / 0.002, 1.0)
    fin = np.minimum((duree - t) / 0.2, 1.0)
    return s * attaque * fin * force * 0.25


def nappe(freqs, duree, n_total):
    """Nappe chaude : sinus désaccordés, attaque et relâche lentes, filtrée."""
    t = np.arange(int(duree * SR)) / SR
    s = np.zeros((len(t), 2))
    for f in freqs:
        for c, det in enumerate([-0.12, 0.12]):
            fr = f * 2 ** (det / 12)
            s[:, c] += np.sin(2 * np.pi * fr * t) + 0.25 * np.sin(2 * np.pi * fr * 2 * t + 0.3)
    env = np.minimum(t / 1.5, 1.0) * np.minimum((duree - t) / 1.5, 1.0)
    return s * env[:, None] * 0.12


# ------------------------------------------------------------------ musique

ACCORDS = [                         # 2 mesures chacun
    ["D3", "A3", "E4", "F#4"],      # Ré maj9
    ["B2", "F#3", "D4", "E4"],      # Si m7 (add11)
    ["G2", "D3", "F#4", "B4"],      # Sol maj7
    ["A2", "E3", "B3", "F#4"],      # La 6sus2
]
MELODIE = [                          # (temps depuis le début, note, durée en temps) — ré pentatonique
    (0, "F#5", 2), (2, "A5", 1), (3, "B5", 1), (4, "A5", 3), (7.5, "F#5", 0.5),
    (8, "E5", 2), (10, "F#5", 1), (11, "D5", 1), (12, "E5", 4),
    (16, "D5", 2), (18, "E5", 1), (19, "F#5", 1), (20, "B5", 2), (22, "A5", 2),
    (24, "F#5", 1.5), (25.5, "E5", 0.5), (26, "D5", 1), (27, "E5", 1), (28, "D5", 4),
]


def musique():
    n = int(LONGUEUR_MUSIQUE * SR)
    couches = {k: np.zeros((n, 2)) for k in (1, 2, 3, 4)}
    for i, acc in enumerate(ACCORDS):
        debut = i * 2 * MESURE
        # couche 1 : l'accord, roulé doucement, puis un rappel plus léger à la 2e mesure
        for j, nm in enumerate(acc):
            poser(couches[1], piano(note(nm), 5.0, 0.9), debut + j * 0.06, pan=-0.3 + 0.2 * j)
            poser(couches[1], piano(note(nm), 4.0, 0.45), debut + MESURE + 2 * TEMPS + j * 0.05, pan=-0.3 + 0.2 * j)
        # couche 2 : arpège en croches, une octave au-dessus
        haut = [note(x) * 2 for x in acc[1:]] + [note(acc[1]) * 4]
        motif = [0, 1, 2, 3, 2, 1, 2, 1]
        for m in range(2):
            for k, idx in enumerate(motif):
                force = 0.55 if k % 2 == 0 else 0.4
                poser(couches[2], piano(haut[idx], 2.0, force), debut + m * MESURE + k * TEMPS / 2, pan=0.35)
        # couche 4 : la nappe, un accord tenu sur 2 mesures
        poser_nappe = nappe([note(x) for x in acc], 2 * MESURE + 1.0, n)
        i0 = int(debut * SR)
        idx = (np.arange(len(poser_nappe)) + i0) % n
        np.add.at(couches[4], idx, poser_nappe)
    # couche 3 : la mélodie, à la boîte à musique
    for (t0, nm, d) in MELODIE:
        poser(couches[3], boite_a_musique(note(nm), 2.5 + d * 0.3, 0.9), t0 * TEMPS, pan=0.1)
    # réverbération (circulaire) et écriture
    reglages = {1: (2.6, 0.35, 0.8), 2: (2.2, 0.4, 0.55), 3: (3.2, 0.45, 0.6), 4: (3.5, 0.3, 0.5)}
    for k, (duree, mouille, vol) in reglages.items():
        ecrire(f"musique_couche_{k}", reverb_circulaire(couches[k], duree, mouille), vol)


# ------------------------------------------------------------------ ambiance

def vent():
    d = 24.0
    n = int(d * SR)
    t = np.arange(n) / SR
    x = filtre_spectral(bruit_rose(n), f_bas=120, f_haut=900)
    # rafales : des oscillations lentes qui bouclent (nombre entier de cycles sur la boucle)
    rafales = 0.55 + 0.25 * np.sin(2 * np.pi * 2 * t / d) + 0.15 * np.sin(2 * np.pi * 5 * t / d + 1.3) + 0.08 * np.sin(2 * np.pi * 11 * t / d + 0.4)
    sifflement = filtre_spectral(bruit_rose(n), f_bas=900, f_haut=2500) * (0.25 * np.clip(rafales - 0.6, 0, 1))[:, None]
    ecrire("vent", x * rafales[:, None] + sifflement, 0.7)


def vagues():
    d = 20.0
    n = int(d * SR)
    t = np.arange(n) / SR
    fond = filtre_spectral(bruit_rose(n), f_bas=60, f_haut=500) * 0.35
    ressac = np.zeros(n)
    for i in range(4):                           # 4 vagues par boucle
        centre = (i + 0.3 + 0.2 * rng.random()) * d / 4
        dt = ((t - centre + d / 2) % d) - d / 2   # distance circulaire
        ressac += np.exp(-np.where(dt < 0, (dt / 1.6) ** 2, (dt / 2.6) ** 2)) * (0.8 + 0.4 * rng.random())
    eau = filtre_spectral(bruit_rose(n), f_bas=250, f_haut=4000)
    ecrire("vagues", fond + eau * (0.15 + ressac)[:, None], 0.75)


def oiseaux():
    for i in range(4):
        sons = []
        nb = rng.integers(2, 5)
        for k in range(nb):
            d = rng.uniform(0.08, 0.2)
            t = np.arange(int(d * SR)) / SR
            f0 = rng.uniform(2600, 4200)
            balayage = f0 * (1 + rng.uniform(-0.35, 0.45) * (t / d) ** rng.uniform(0.5, 2))
            phase = 2 * np.pi * np.cumsum(balayage) / SR
            vibrato = 1 + 0.03 * np.sin(2 * np.pi * rng.uniform(20, 40) * t)
            env = np.sin(np.pi * t / d) ** 1.5
            sons.append(np.sin(phase * vibrato) * env)
            sons.append(np.zeros(int(rng.uniform(0.04, 0.12) * SR)))
        s = np.concatenate(sons)
        s = np.concatenate([s, np.zeros(int(0.4 * SR))])
        ecrire(f"oiseau_{i + 1}", reverb_circulaire(s, 0.8, 0.25), 0.5)


# ------------------------------------------------------------------ effets

def effets():
    # le clic de la fiche dans la prise
    t = np.arange(int(0.12 * SR)) / SR
    clic = rng.standard_normal(len(t)) * np.exp(-t * 180) * 0.6 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120)
    ecrire("clic", filtre_spectral(clic, f_bas=400, f_haut=6000), 0.6)
    # l'allumage d'une lanterne : un arpège de cloches qui monte, sur une nappe
    s = np.zeros(int(4.0 * SR))
    for k, nm in enumerate(["D5", "F#5", "A5", "D6", "E6"]):
        b = boite_a_musique(note(nm), 3.0, 0.8)
        i0 = int(k * 0.22 * SR)
        s[i0:i0 + len(b)] += b[:len(s) - i0]
    t = np.arange(len(s)) / SR
    s += sum(np.sin(2 * np.pi * note(x) * t) for x in ["D4", "A4"]) * np.minimum(t / 0.8, 1) * np.exp(-t * 0.9) * 0.05
    ecrire("allumage", reverb_circulaire(np.concatenate([s, np.zeros(int(1.5 * SR))]), 2.5, 0.4), 0.75)
    # la recharge : un son qui monte doucement
    d = 2.5
    t = np.arange(int(d * SR)) / SR
    f = 220 * 2 ** (t / d * 1.5)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * 0.2
    s *= np.minimum(t / 0.3, 1) * np.minimum((d - t) / 0.4, 1)
    ecrire("recharge", reverb_circulaire(np.concatenate([s, np.zeros(SR)]), 1.8, 0.35), 0.55)
    # la luciole : un petit scintillement
    s = np.zeros(int(1.2 * SR))
    for k, nm in enumerate(["A6", "D7", "F#7"]):
        b = boite_a_musique(note(nm), 0.8, 0.5)
        i0 = int(k * 0.07 * SR)
        s[i0:i0 + len(b)] += b
    ecrire("luciole", reverb_circulaire(s, 1.2, 0.4), 0.45)
    # la page : un froissement de papier
    d = 0.5
    t = np.arange(int(d * SR)) / SR
    s = filtre_spectral(rng.standard_normal(len(t)), f_bas=1500, f_haut=7000) * np.sin(np.pi * t / d) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t))
    ecrire("page", s, 0.4)
    # l'extinction du robot : un son qui descend et s'éteint
    d = 2.2
    t = np.arange(int(d * SR)) / SR
    f = 440 * 2 ** (-t / d * 2.2)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4) + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t * 2.2) * 0.3
    ecrire("extinction", reverb_circulaire(np.concatenate([s, np.zeros(SR)]), 2.0, 0.35), 0.55)


if __name__ == "__main__":
    vent()
    vagues()
    oiseaux()
    effets()
    musique()
