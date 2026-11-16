"""Assemble référence | modèle | superposition pour chaque vue (lancer avec le Python système)."""
import sys
from PIL import Image, ImageChops, ImageOps

CONCEPT = r"C:/Users/adrie/OneDrive/Bureau/petite-planete-v5/concept/robot_graine_%s.png"
DOSSIER = sys.argv[1] if len(sys.argv) > 1 else "."
LARG = 384  # largeur de chaque panneau

for vue in ("face", "profil", "dos"):
    ref = Image.open(CONCEPT % vue).convert("RGBA")
    mod = Image.open("%s/rendu_%s.png" % (DOSSIER, vue)).convert("RGBA")
    fond = Image.new("RGBA", ref.size, (238, 230, 236, 255))
    mod_sur_fond = Image.alpha_composite(fond, mod)
    # superposition : référence pâlie + contour du modèle en violet
    pale = Image.blend(ref, Image.new("RGBA", ref.size, (255, 255, 255, 255)), 0.45)
    alpha = mod.split()[3]
    bord = ImageChops.difference(alpha, alpha.resize((alpha.width // 2, alpha.height // 2)).resize(alpha.size))
    contour = alpha.point(lambda a: 255 if a > 20 else 0)
    contour = ImageChops.difference(contour, contour.transform(contour.size, Image.AFFINE, (1, 0, 2, 0, 1, 2)))
    violet = Image.new("RGBA", ref.size, (120, 40, 200, 255))
    sup = pale.copy()
    sup.paste(violet, (0, 0), contour)
    h = int(ref.height * LARG / ref.width)
    panneaux = [im.resize((LARG, h)) for im in (ref, mod_sur_fond, sup)]
    out = Image.new("RGBA", (LARG * 3, h), (255, 255, 255, 255))
    for i, p in enumerate(panneaux):
        out.paste(p, (i * LARG, 0))
    out.convert("RGB").save("%s/comparaison_%s.png" % (DOSSIER, vue))
print("assemblé")
