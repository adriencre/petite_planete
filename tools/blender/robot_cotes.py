# Cotes du robot « Graine », relevées sur concept/robot_graine_{face,profil,dos}.png
# (1,90 m au sommet de la tête ; ~1,36 mm/px). Blender : Z haut, le robot regarde -Y,
# sa DROITE est en -X (côté « _D » : enrouleur de câble).
from mathutils import Vector as V

PIVOTS = {
    "Bassin": V((0, 0, 1.12)), "Torse": V((0, 0, 1.2)), "Tete": V((0, -0.01, 1.66)),
    "Epaule_D": V((-0.21, 0.0, 1.52)), "Coude_D": V((-0.245, 0.01, 1.215)), "Poignet_D": V((-0.255, -0.01, 0.905)),
    "Epaule_G": V((0.21, 0.0, 1.52)), "Coude_G": V((0.245, 0.01, 1.215)), "Poignet_G": V((0.255, -0.01, 0.905)),
    "Hanche_D": V((-0.072, 0.0, 1.08)), "Genou_D": V((-0.07, -0.01, 0.735)), "Cheville_D": V((-0.068, 0.02, 0.14)),
    "Hanche_G": V((0.072, 0.0, 1.08)), "Genou_G": V((0.07, -0.01, 0.735)), "Cheville_G": V((0.068, 0.02, 0.14)),
}
PARENT = {"Bassin": "Robot", "Torse": "Bassin", "Tete": "Torse",
          "Epaule_D": "Torse", "Coude_D": "Epaule_D", "Poignet_D": "Coude_D",
          "Epaule_G": "Torse", "Coude_G": "Epaule_G", "Poignet_G": "Coude_G",
          "Hanche_D": "Bassin", "Genou_D": "Hanche_D", "Cheville_D": "Genou_D",
          "Hanche_G": "Bassin", "Genou_G": "Hanche_G", "Cheville_G": "Genou_G"}

# volumes principaux (centre, demi-axes x, y, z)
TETE = (V((0, -0.025, 1.795)), (0.118, 0.13, 0.108))
TORSE = (V((0, 0.0, 1.45)), (0.135, 0.1, 0.17))
JUPE = (V((0, 0.0, 1.2)), (0.115, 0.09, 0.3))
EPAULE_R = 0.075
MAIN_LONG = 0.22
PIED = dict(long_avant=0.24, long_arriere=0.08, larg=0.055, haut=0.07)
