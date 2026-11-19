"""Rend les documents des Semeurs (tools/affiches/*.html) en PNG pour le jeu (assets/affiches/).

Chaque document est une page HTML/SVG (papier, encre, aquarelle, typographie) ; Chrome sans fenêtre
en fait une capture à la taille indiquée ci-dessous. Le fond hors de la feuille est transparent
(deux captures, sur noir et sur blanc).

Lancer :  python tools/affiches/rendre.py            (tous)
          python tools/affiches/rendre.py ordre_ysolde (un seul)
Les polices viennent de Google Fonts : il faut Internet au moment du rendu.
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES = os.path.join(RACINE, "tools", "affiches")
SORTIE = os.path.join(RACINE, "assets", "affiches")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# nom -> (largeur, hauteur) en pixels
DOCUMENTS = {
    "mode_emploi": (1200, 1700),
    "ordre_ysolde": (1400, 1000),
    "page_7": (1100, 1400),
    "cahier_passages": (1800, 1150),
    "releves_iris": (1200, 760),
}


def _capture(source_html: str, fond: str, taille: tuple, sortie: str) -> np.ndarray:
    """Une capture du document sur un fond uni (« #000 » ou « #fff »)."""
    with open(source_html, encoding="utf-8") as f:
        html = f.read()
    html = html.replace("</head>", f"<style>html, body {{ background: {fond} !important; }}</style></head>", 1)
    temp = os.path.join(SOURCES, "_rendu_temp.html")   # à côté, pour que commun.css se charge
    with open(temp, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--force-device-scale-factor=1", f"--window-size={taille[0]},{taille[1]}",
            "--virtual-time-budget=8000", f"--screenshot={sortie}", "file:///" + temp.replace("\\", "/"),
        ], check=True, capture_output=True)
    finally:
        os.remove(temp)
    return np.asarray(Image.open(sortie).convert("RGB")).astype(np.float32)


def rendre(nom: str, taille: tuple) -> None:
    """Deux captures, sur noir et sur blanc : leur différence donne la transparence exacte
    (bords déchirés, ombres), sans toucher à l'encre."""
    source = os.path.join(SOURCES, nom + ".html")
    sortie = os.path.join(SORTIE, nom + ".png")
    noir = _capture(source, "#000", taille, sortie)
    blanc = _capture(source, "#fff", taille, sortie)
    alpha = np.clip(1.0 - (blanc - noir).mean(axis=2) / 255.0, 0.0, 1.0)
    a = np.maximum(alpha, 1e-3)[..., None]
    couleur = np.clip(noir / a, 0, 255)
    rgba = np.dstack([couleur, alpha * 255.0]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(sortie)
    print("affiche :", os.path.relpath(sortie, RACINE))


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    noms = sys.argv[1:] or list(DOCUMENTS)
    for n in noms:
        rendre(n, DOCUMENTS[n])
