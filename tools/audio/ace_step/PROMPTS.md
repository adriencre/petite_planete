# Musique de l'île 1 — génération sur AceStep.io

Le jeu joue 4 couches en boucle, synchronisées (scripts/ambiance_sonore.gd) :
chaque petite lanterne allumée en ajoute une, la grande lanterne ajoute la nappe.

## Étape 1 — le morceau complet (Créer → Personnalisé)

**Reference Audio** : rien.

**Styles** (à coller tel quel, ~480/1000) :

```
gentle acoustic folk ambient, instrumental, 72 BPM, D major, 4/4, slow and steady tempo, soft fingerpicked acoustic guitar, warm felt piano, delicate music box melody, quiet banjo plucks, distant soft harmonica, airy warm synth pad, campfire under the stars, lonely and peaceful, nostalgic, sense of wonder, space exploration, intimate close-mic recording, warm and cozy, calm, no drums, no percussion, no vocals, no singing, seamless loop
```

**Genre** : clique `Folk` (et `Ambiance` si c'est un genre cliquable).

**Paroles** : efface le texte d'exemple, désactive « Génération IA », et mets juste :

```
[instrumental]
```

**Durée** : `2m` (120 s).

**Réglages avancés** :
- Qualité : `Élevé`
- Graine : vide pour les premiers essais ; quand une version te plaît, note sa graine.
- `Hi-Fi` si tu as assez de crédits, sinon `Standard`.

Génère 2 ou 3 fois (2 versions à chaque fois), garde la meilleure.
Ce qu'on cherche : calme du début à la fin, sans montée ni batterie, et sans
fin marquée (pour que la boucle passe bien).
Télécharge-la → `entree/complet.wav` (ou .mp3).

## Étape 2 — les couches (Transformer → Pistes / « Obtenir les pistes »)

Donne `complet` à « Obtenir les pistes » : ça sépare le morceau en pistes
(guitare, piano, autres…) qui restent parfaitement calées entre elles.
Télécharge toutes les pistes dans `entree/` en gardant leur nom.
Je les regroupe ensuite en 4 couches :
1. guitare (1re lanterne)
2. + piano (2e lanterne)
3. + boîte à musique / mélodie (3e lanterne)
4. + nappe, harmonica, le reste (grande lanterne)

Si « Pistes » coûte trop cher ou ne donne rien d'utile, dépose seulement
`complet` : je fabrique les couches moi-même par filtrage.

## Ensuite

Dis à Claude que les fichiers sont dans `tools/audio/ace_step/entree/` :
il coupe des boucles sans raccord audible, égalise le volume, puis remplace
`assets/audio/musique_couche_1..4.wav` (les anciens fichiers sont gardés de côté).

---

# Variante : Suno (Create → Custom)

**Style of Music** :

```
gentle acoustic folk ambient, instrumental, 72 BPM, D major, slow and steady, soft fingerpicked acoustic guitar, warm felt piano, delicate music box melody, quiet banjo plucks, distant soft harmonica, airy warm pad, campfire under the stars, lonely and peaceful, nostalgic, sense of wonder, space exploration, intimate close-mic, cozy lo-fi warmth, calm and even dynamics, seamless loop
```

**Exclude styles** (Advanced Options) :

```
drums, percussion, vocals, singing, choir, bass drop, build-up, epic, orchestral hit, electric guitar
```

**Advanced Options** : Weirdness ~35 %, Style Influence ~70 %.

**Instrumental** : activé. (Pour mieux guider la structure, laisse-le
désactivé et colle ces « paroles » qui ne sont que des balises :)

```
[Instrumental]
[Intro: solo fingerpicked acoustic guitar, soft]
[Verse: guitar and felt piano]
[Melody: music box joins, gentle]
[Bridge: warm pad and distant harmonica]
[Verse: guitar, piano, music box together]
[Outro: back to solo guitar, fading into the intro]
```

**Titre** : Ile 1 - Le Reveil

Couches : dans le menu « … » du titre → Get Stems (Get Full Stems : une piste
par instrument, abonnement payant) → tout télécharger dans `entree/`.
