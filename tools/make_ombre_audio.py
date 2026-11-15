# Son de l'ombre (étape 28) : la musique des Lueurs en 3 couches synchronisées + le petit son de verre des mots.
# Usage : python tools/make_ombre_audio.py <racine du projet>
# - music/ombre_layer1.wav : nappe aquatique (on éteint un peu)
# - music/ombre_layer2.wav : mélodie de verre, arpèges en gouttes (vraiment dans le noir)
# - music/ombre_layer3.wav : le peuple — un chœur chaud et grave (quand le peuple est prêt)
# - sfx/glass_word_0..3.wav : un tintement de verre par mot de lumière
import os, sys, wave
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SR = 44100
BPM = 60.0
BAR = 4 * 60.0 / BPM          # 4 s par mesure
BARS = 8
L = BAR * BARS                # boucle de 32 s
TAIL = 4.0
N = int((L + TAIL) * SR)
t = np.arange(N) / SR

# ré lydien, comme le chant des Lueurs (ré, mi, fa#, sol#, la, si, do#)
def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)

# grille d'accords (une par mesure) : Dmaj9, Bm11, Gmaj7#11, Asus2, …
CHORDS = [
    [50, 57, 62, 64, 66, 69],
    [47, 54, 59, 62, 64, 66],
    [43, 50, 57, 61, 62, 68],
    [45, 52, 57, 59, 64, 69],
    [50, 57, 62, 64, 66, 69],
    [42, 49, 54, 57, 61, 64],
    [43, 50, 55, 59, 62, 68],
    [45, 52, 57, 59, 64, 71],
]


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na) ** 2
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def reverb(x, taps=((0.13, 0.42), (0.29, 0.33), (0.41, 0.27), (0.61, 0.2), (0.89, 0.14), (1.31, 0.09))):
    out = x.copy()
    for d, g in taps:
        j = int(d * SR)
        out[j:, 0] += x[:-j, 1] * g
        out[j:, 1] += x[:-j, 0] * g
    return out


def to_loop(x):
    # la queue (réverb après la fin) retombe sur le début : boucle sans couture
    body = x[: int(L * SR)].copy()
    tail = x[int(L * SR):]
    body[: len(tail)] += tail
    return body


def save(path, x, peak):
    x = x / max(1e-9, np.max(np.abs(x))) * peak
    data = (x * 32767).astype("<i2")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("ok", os.path.relpath(path, ROOT))


rng = np.random.default_rng(28)

# ---------- couche 1 : nappe aquatique ----------
x1 = np.zeros((N, 2))
for b, chord in enumerate(CHORDS):
    start = int(b * BAR * SR)
    n = int((BAR + 2.5) * SR)
    tt = np.arange(n) / SR
    e = env(n, 1.6, 2.6)
    for k, m in enumerate(chord[1:]):
        f = hz(m)
        for ch in (0, 1):
            det = 1 + (0.0025 if ch else -0.0025) * (k % 2 * 2 - 1)
            # vibrato lent « sous l'eau »
            ph = 2 * np.pi * f * det * tt + 0.6 * np.sin(2 * np.pi * 0.35 * tt + k + ch)
            s = np.sin(ph) + 0.18 * np.sin(2 * ph)
            seg = s * e * (0.32 / (1 + 0.25 * k))
            end = min(N, start + n)
            x1[start:end, ch] += seg[: end - start]
# un filet de basse très douce
for b, chord in enumerate(CHORDS):
    start = int(b * BAR * SR)
    n = int((BAR + 1.0) * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * hz(chord[0]) * tt) * env(n, 0.8, 1.6) * 0.35
    end = min(N, start + n)
    x1[start:end, 0] += s[: end - start]
    x1[start:end, 1] += s[: end - start]
# bulles : petits glissandos montants, rares
for _ in range(14):
    i = int(rng.uniform(0, L) * SR)
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    f0 = rng.uniform(500, 900)
    s = np.sin(2 * np.pi * (f0 * tt + 2500 * tt * tt)) * np.exp(-tt * 30) * 0.12
    pan = rng.uniform(0.2, 0.8)
    end = min(N, i + n)
    x1[i:end, 0] += s[: end - i] * (1 - pan)
    x1[i:end, 1] += s[: end - i] * pan
save(os.path.join(ROOT, "assets/audio/music/ombre_layer1.wav"), to_loop(reverb(x1)), 0.55)


# ---------- couche 2 : mélodie de verre ----------
def glass(f, dur=2.2, bright=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2)
         + 0.35 * bright * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 7)
         + 0.15 * bright * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 14))
    a = int(0.002 * SR)
    s[:a] *= np.linspace(0, 1, a)
    return s


x2 = np.zeros((N, 2))
# motif : arpège en croches qui descend comme des gouttes, avec des silences
PATTERN = [0, None, 2, 4, None, 3, 1, None]
for b, chord in enumerate(CHORDS):
    top = [m + 12 for m in chord[2:]]   # notes aiguës de l'accord
    for step, idx in enumerate(PATTERN):
        if idx is None or (b % 4 == 3 and step >= 5):
            continue
        m = top[idx % len(top)]
        i = int((b * BAR + step * BAR / 8 + rng.uniform(-0.01, 0.01)) * SR)
        s = glass(hz(m)) * (0.5 if step else 0.7)
        pan = 0.5 + 0.35 * np.sin(step * 1.3 + b)
        end = min(N, i + len(s))
        x2[i:end, 0] += s[: end - i] * (1 - pan)
        x2[i:end, 1] += s[: end - i] * pan
save(os.path.join(ROOT, "assets/audio/music/ombre_layer2.wav"), to_loop(reverb(x2)), 0.5)

# ---------- couche 3 : le peuple (chœur chaud) ----------
x3 = np.zeros((N, 2))
for b, chord in enumerate(CHORDS):
    start = int(b * BAR * SR)
    n = int((BAR + 2.0) * SR)
    tt = np.arange(n) / SR
    e = env(n, 0.9, 2.2)
    for k, m in enumerate(chord[:4]):
        f = hz(m)
        # « voix » : quelques harmoniques avec formant « ou » et léger vibrato
        vib = 0.004 * np.sin(2 * np.pi * 5.0 * tt + k) * np.clip(tt - 0.6, 0, 1)
        ph = 2 * np.pi * f * tt * (1 + vib)
        s = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph) + 0.06 * np.sin(5 * ph)
        for ch in (0, 1):
            seg = s * e * 0.22 * (1.0 if k == 0 else 0.7)
            off = int((0.01 + 0.012 * ch) * SR)
            i = start + off
            end = min(N, i + n)
            x3[i:end, ch] += seg[: end - i]
    # pulsation douce sur les temps 1 et 3 (un cœur qui bat, tout bas)
    for beat in (0, 2):
        i = int((b * BAR + beat * BAR / 4) * SR)
        n2 = int(0.5 * SR)
        tt2 = np.arange(n2) / SR
        s = np.sin(2 * np.pi * hz(chord[0] - 12) * tt2) * np.exp(-tt2 * 8) * 0.5
        end = min(N, i + n2)
        x3[i:end, 0] += s[: end - i]
        x3[i:end, 1] += s[: end - i]
save(os.path.join(ROOT, "assets/audio/music/ombre_layer3.wav"), to_loop(reverb(x3)), 0.5)

# ---------- sfx : le son de verre d'un mot ----------
for k, m in enumerate([86, 88, 90, 93]):   # ré, mi, fa#, la (aigus)
    s = glass(hz(m), dur=1.2, bright=0.8) * 0.8
    n = len(s)
    st = np.zeros((n + int(0.7 * SR), 2))
    st[:n, 0] = s
    st[:n, 1] = s
    st = reverb(st, ((0.07, 0.35), (0.17, 0.25), (0.31, 0.15)))
    save(os.path.join(ROOT, "assets/audio/sfx/glass_word_%d.wav" % k), st, 0.7)
