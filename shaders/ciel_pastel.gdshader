// Ciel pastel : dégradé + soleil + grande planète. Tout est réglable dans l'inspecteur.
shader_type sky;
#include "res://shaders/bruit.gdshaderinc"

group_uniforms Degrade;
uniform vec3 couleur_haut : source_color = vec3(0.60, 0.53, 0.84);
uniform vec3 couleur_milieu : source_color = vec3(0.96, 0.68, 0.76);
uniform vec3 couleur_horizon : source_color = vec3(1.0, 0.83, 0.64);
uniform vec3 couleur_bas : source_color = vec3(0.80, 0.78, 0.88);
uniform float hauteur_milieu : hint_range(0.01, 0.5) = 0.14;
uniform float hauteur_haut : hint_range(0.1, 1.0) = 0.6;

group_uniforms Soleil;
uniform float taille_soleil : hint_range(0.99, 0.99999) = 0.9993;
uniform float halo_soleil : hint_range(0.0, 2.0) = 0.6;

group_uniforms Nuages;
uniform vec3 nuage_lumiere : source_color = vec3(1.0, 0.88, 0.80);
uniform vec3 nuage_ombre : source_color = vec3(0.80, 0.62, 0.82);
uniform float nuage_couverture : hint_range(0.0, 1.0) = 0.48;
uniform float nuage_douceur : hint_range(0.01, 0.5) = 0.18;
uniform float nuage_echelle = 1.6;
uniform float nuage_vitesse = 0.01;

group_uniforms Etoiles;
uniform float etoiles : hint_range(0.0, 1.0) = 0.0;

group_uniforms Planete;
uniform vec3 planete_direction = vec3(-0.5, 0.3, -0.8);
uniform float planete_taille : hint_range(0.02, 0.6) = 0.17;
uniform vec3 planete_couleur_a : source_color = vec3(0.86, 0.62, 0.82);
uniform vec3 planete_couleur_b : source_color = vec3(0.68, 0.58, 0.88);
uniform float planete_bandes : hint_range(1.0, 40.0) = 11.0;
uniform float planete_brume : hint_range(0.0, 1.0) = 0.35;

void sky() {
	vec3 d = EYEDIR;
	float h = d.y;
	vec3 col;
	if (h >= 0.0) {
		col = mix(couleur_horizon, couleur_milieu, smoothstep(0.0, hauteur_milieu, h));
		col = mix(col, couleur_haut, smoothstep(hauteur_milieu, hauteur_haut, h));
	} else {
		col = mix(couleur_horizon, couleur_bas, smoothstep(0.0, 0.12, -h));
	}

	// planète (dessinée avant le soleil)
	vec3 pd = normalize(planete_direction);
	float ang = acos(clamp(dot(d, pd), -1.0, 1.0));
	if (ang < planete_taille * 1.05) {
		vec3 right = normalize(cross(pd, vec3(0.0, 1.0, 0.0)));
		vec3 up = cross(right, pd);
		vec2 uv = vec2(dot(d, right), dot(d, up)) / sin(planete_taille);
		float r = length(uv);
		float bandes = sin(uv.y * planete_bandes + sin(uv.x * 3.0) * 1.2) * 0.5 + 0.5;
		vec3 pc = mix(planete_couleur_a, planete_couleur_b, bandes);
		vec3 n = normalize(vec3(uv, sqrt(max(0.0, 1.0 - r * r))));
		float lit = 0.45 + 0.55 * clamp(dot(n, normalize(vec3(0.7, -0.1, 0.6))), 0.0, 1.0);
		pc *= lit;
		pc = mix(pc, col, planete_brume);
		float alpha = 1.0 - smoothstep(0.985, 1.0, r);
		col = mix(col, pc, alpha);
	}

	// étoiles (la nuit)
	if (etoiles > 0.0 && h > 0.0) {
		vec3 cell = floor(d * 220.0);
		float r = hash3(cell);
		float star = step(0.985, r) * smoothstep(0.0, 0.15, h);
		float tw = 0.6 + 0.4 * sin(TIME * 2.0 + r * 50.0);
		col += vec3(0.85, 0.9, 1.0) * star * tw * etoiles * 1.5;
	}

	// nuages : projetés sur un plan, plus denses près de l'horizon
	if (h > 0.0) {
		vec2 uv = d.xz / (h + 0.1) * nuage_echelle + vec2(TIME * nuage_vitesse, 0.0);
		vec3 q = vec3(uv.x, 0.0, uv.y);
		float n = fbm3(q);
		float c = smoothstep(nuage_couverture, nuage_couverture + nuage_douceur, n);
		c *= smoothstep(0.0, 0.06, h) * (1.0 - smoothstep(0.3, 0.65, h));
		vec3 vers_soleil = vec3(LIGHT0_DIRECTION.x, 0.0, LIGHT0_DIRECTION.z) * 0.15;
		float relief = clamp((n - fbm3(q + vers_soleil)) * 6.0 + 0.5, 0.0, 1.0);
		float face_soleil = max(dot(normalize(d.xz), normalize(LIGHT0_DIRECTION.xz)), 0.0);
		vec3 cc = mix(nuage_ombre, nuage_lumiere, relief);
		cc = mix(cc, LIGHT0_COLOR * 1.1, face_soleil * relief * 0.25);
		col = mix(col, cc, c * 0.92);
	}

	if (LIGHT0_ENABLED) {
		float s = max(dot(d, LIGHT0_DIRECTION), 0.0);
		col += LIGHT0_COLOR * smoothstep(taille_soleil, taille_soleil + 0.0002, s) * 2.0;
		col += LIGHT0_COLOR * (pow(s, 48.0) * 0.4 + pow(s, 6.0) * 0.12) * halo_soleil;
	}
	COLOR = col;
}
