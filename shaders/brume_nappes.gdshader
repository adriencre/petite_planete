// Les nappes de brume au ras du sol (maquette.gd : « BrumeNappes », 3 couches par case).
// Vue de dessus, c'est elles qu'on voit : des voiles pâles qui dérivent, s'effilochent et laissent
// des trouées. Elles s'estompent au contact des objets (pas de coupure nette) et près de la caméra.
// Les lanternes allumées les chassent (zones poussées par zone_endormie.gd, comme brume_ile).
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled;

uniform vec4 zones[4];
uniform float eveils[4];
uniform int nombre_zones = 0;

uniform vec3 couleur : source_color = vec3(0.74, 0.71, 0.83);
// Avant le 2026-11-17 : 0.85, en voile continu presque blanc (4 couches empilées) : l'île paraissait surexposée.
uniform float opacite : hint_range(0.0, 1.0) = 0.3;
// Couverture : seuils du motif (plus bas = moins de trouées). Brume épaisse de l'île 2 : 0.34 / 0.62.
uniform float seuil_bas = 0.46;
uniform float seuil_haut = 0.74;
// Taille des nappes : plus grand = nappes plus petites.
uniform float echelle = 0.22;
uniform vec2 vent = vec2(0.6, 0.2);
// Distance (m) sur laquelle la nappe s'efface quand elle touche un objet ou le sol.
uniform float douceur_contact = 0.9;
// La bulle de l'antenne du robot (brume_batterie.gd) : xyz = le robot, w = rayon (0 = pas de bulle).
uniform vec4 robot = vec4(0.0);
// La bulle de la lanterne de proue de la barque (barque.gd : bulle_lanterne) : pareil.
uniform vec4 barque = vec4(0.0);
// Phare de l'île 2 : origine XZ et direction du balayage multipliée par sa puissance.
uniform vec4 phare_passage = vec4(0.0);
// Centre XZ de l'épave, rayon de la trouée, puissance de 0 à 1.
uniform vec4 phare_epave = vec4(0.0);
// Ce qui reste de brume dans une zone réveillée (0 = air clair).
uniform float reste_eveil : hint_range(0.0, 1.0) = 0.0;

uniform sampler2D profondeur : hint_depth_texture, filter_nearest;

varying vec3 monde;

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float bruit(vec2 x) {
	vec2 i = floor(x);
	vec2 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int i = 0; i < 4; i++) {
		v += a * bruit(p);
		p = p * 2.03 + vec2(1.7, 9.2);
		a *= 0.5;
	}
	return v;
}

void vertex() {
	monde = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float couche = COLOR.r;   // 0, 0.5, 1 : chaque couche a son motif et sa vitesse
	vec2 q = monde.xz * echelle + vent * TIME * (0.05 + 0.035 * couche) + vec2(couche * 7.3, couche * 3.1);
	// le motif se tord lentement sur lui-même, comme de la fumée
	q += vec2(fbm(q * 0.7 + TIME * 0.02), fbm(q * 0.7 - TIME * 0.025)) * 1.2;
	// des nappes denses et de vraies trouées entre elles (avant : un voile continu, qui délavait toute l'île)
	float n = 0.04 + 0.96 * smoothstep(seuil_bas, seuil_haut, fbm(q));

	float reveil = 0.0;
	for (int i = 0; i < 4; i++) {
		if (i >= nombre_zones) break;
		float dist = distance(monde.xz, zones[i].xz);
		float dans_zone = 1.0 - smoothstep(zones[i].w - 3.0, zones[i].w, dist);
		float eveille = 1.0 - smoothstep(eveils[i] - 1.5, eveils[i] + 1.5, dist);
		reveil = max(reveil, dans_zone * eveille);
	}

	// contact doux avec ce qui est derrière (sol, objets, robot)
	float d = texture(profondeur, SCREEN_UV).r;
	vec4 vue = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, d, 1.0);
	vue.xyz /= vue.w;
	float contact = smoothstep(0.0, douceur_contact, VERTEX.z - vue.z);
	// pas de nappe collée à l'objectif
	float pres = smoothstep(0.6, 2.2, -VERTEX.z);
	// bords de la case : fondu (les cases se chevauchent)
	float bord = min(min(UV.x, 1.0 - UV.x), min(UV.y, 1.0 - UV.y));
	float fondu = smoothstep(0.0, 0.18, bord);

	ALBEDO = couleur;
	// la lumière de l'antenne repousse les nappes autour du robot (un bord un peu irrégulier)
	float d_robot = distance(monde.xz, robot.xz) + (n - 0.5) * 0.6;
	float bord_bulle = robot.w > 0.0 ? exp(-pow((d_robot - robot.w * 1.05) / 0.7, 2.0)) * 0.6 : 0.0;   // la brume se tasse sur le bord du rond
	fondu *= robot.w > 0.0 ? smoothstep(robot.w * 0.55, robot.w, d_robot) : 1.0;
	// pareil autour de la lanterne de proue de la barque
	float d_barque = distance(monde.xz, barque.xz) + (n - 0.5) * 0.6;
	bord_bulle = max(bord_bulle, barque.w > 0.0 ? exp(-pow((d_barque - barque.w * 1.05) / 0.7, 2.0)) * 0.6 : 0.0);
	fondu *= barque.w > 0.0 ? smoothstep(barque.w * 0.55, barque.w, d_barque) : 1.0;
	float force_phare = length(phare_passage.zw);
	if (force_phare > 0.001) {
		vec2 vers = phare_passage.zw / force_phare;
		vec2 ecart = monde.xz - phare_passage.xy;
		float avant = dot(ecart, vers);
		float travers = abs(ecart.x * vers.y - ecart.y * vers.x);
		float largeur = 2.2 + 0.036 * max(avant, 0.0);
		float passage = smoothstep(0.0, 4.0, avant) * (1.0 - smoothstep(105.0, 118.0, avant));
		passage *= 1.0 - smoothstep(largeur * 0.75, largeur * 1.4, travers);
		float epave = 1.0 - smoothstep(phare_epave.z * 0.75, phare_epave.z, distance(monde.xz, phare_epave.xy));
		fondu *= 1.0 - max(passage * force_phare, epave * phare_epave.w);
	}
	n = min(n + bord_bulle, 1.0);
	// les couches hautes sont plus légères (la brume s'amincit en montant)
	// COLOR.a : force de la nappe (1 en général ; plus faible là où la brume épaisse déborde sur la mer)
	ALPHA = opacite * mix(1.0, 0.5, couche) * n * contact * pres * fondu * mix(1.0, reste_eveil, reveil) * COLOR.a;
}
