# Audio — musique et sons

## Musique (ACE-Step en ligne)
- Pas d'install locale (disque C: plein) : l'utilisateur génère sur **acemusic.ai / AceStep.io** (ou Suno).
- L'agent écrit les prompts dans `tools/audio/ace_step/PROMPTS.md` ; l'utilisateur dépose les fichiers téléchargés dans `tools/audio/ace_step/entree/` ; l'agent les boucle et normalise en `assets/audio/musique_couche_1..4.wav`.
- 4 couches synchronisées jouées par `scripts/ambiance_sonore.gd` : chaque petite lanterne allumée ajoute une couche, la grande lanterne ajoute la nappe. Garder ce principe.
- Style : « doux chill à la Outer Wilds » — folk acoustique, feu de camp, pas de batterie, pas de voix.

## Bruitages
- Générés par `tools/audio/generer_sons.py` → `assets/audio/*.wav` (allumage, recharge, page, clic, oiseaux, vent, vagues…). Lus via `scripts/sons.gd`.
- Bus audio : `default_bus_layout.tres` : `Master`, `Musique`, `Ambiance` (vent et vagues), `Effets` (bruitages) — réglables dans `scenes/ui/reglages.tscn`.
