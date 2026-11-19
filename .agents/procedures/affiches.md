# Affiches et documents des Semeurs

- Sources : `tools/affiches/*.html` (papier, encre, aquarelle ; style commun dans `commun.css`).
- Rendu en PNG transparent : `python tools/affiches/rendre.py` (tous) ou `python tools/affiches/rendre.py ordre_ysolde` (un seul). Utilise Chrome headless (`C:\Program Files\Google\Chrome\Application\chrome.exe`) et Google Fonts : il faut Internet.
- Sortie : `assets/affiches/*.png`. Pour un nouveau document, ajouter son nom et sa taille dans `DOCUMENTS` de `rendre.py`.
- Textes : reprendre ceux des docs d'île (ILE_0X) ; pas de texte inventé sans validation.
