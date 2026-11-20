// La mer autour de l'île (maquette.gd : « Mer »), low-poly à facettes, turquoise pastel (DA v6).
// - Le plan est découpé en petites cases et ondule doucement ; chaque facette prend sa propre lumière.
// - Près des côtes (carte des côtes floutée, `cote`), l'eau devient claire et l'écume vient
//   battre le rivage en vagues qui avancent vers la terre.
// - Là où l'eau touche une falaise ou un rocher (profondeur), un liseré d'écume.
// - Au loin, elle se fond dans la brume (brouillard de distance).
shader_type spatial;
render_mode blend_mix, depth_draw_always, cull_back, specular_schlick_ggx;

uniform sampler2D profondeur : hint_depth_texture, filter_linear;
// Carte des côtes : 1 sur la terre, 0 au large, floutée (un halo autour de l'île).
uniform sampler2D cote : filter_linear, repeat_disable;
// xy = coin de la carte (x, z), zw = sa taille (m).
uniform vec4 cote_rect = vec4(-60.0, -54.0, 120.0, 108.0);
uniform vec4 abri_maree = vec4(0.0);

uniform vec3 eau_profonde : source_color = vec3(0.30, 0.66, 0.79);
uniform vec3 eau_claire : source_color = vec3(0.58, 0.90, 0.86);
uniform vec3 ecume : source_color = vec3(1.0, 0.97, 0.94);
uniform float hauteur_vagues : hint_range(0.0, 1.0) = 0.22;
uniform float vitesse : hint_range(0.0, 3.0) = 0.6;
uniform float opacite : hint_range(0.0, 1.0) = 0.93;
uniform float brillance : hint_range(0.0, 1.0) = 0.3;
// Écume au contact des falaises (m).
uniform float largeur_contact = 0.5;
// Nombre de vagues d'écume qui viennent battre la côte, et leur vitesse.
uniform float vagues_cote = 3.0;
uniform float vitesse_cote = 0.35;

varying vec3 monde;
varying float pres_cote;
varying vec2 plan_local;

float onde(vec3 w, float t) {
	return sin(w.x * 0.35 + t) * 0.5 + sin(w.z * 0.42 + t * 1.3) * 0.35 + sin((w.x + w.z) * 0.8 - t * 1.7) * 0.15;
}

float lire_cote(vec2 xz) {
	vec2 uv = (xz - cote_rect.xy) / cote_rect.zw;
	if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) return 0.0;
	return texture(cote, uv).r;
}

void vertex() {
	plan_local = VERTEX.xz;
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	pres_cote = lire_cote(w.xz);
	// la houle s'apaise près du rivage
	VERTEX.y += onde(w, TIME * vitesse) * hauteur_vagues * (1.0 - 0.6 * smoothstep(0.2, 0.6, pres_cote));
	monde = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	if (all(greaterThanEqual(plan_local, abri_maree.xy)) && all(lessThan(plan_local, abri_maree.zw))) {
		discard;
	}
	// facettes : une normale plate par triangle
	NORMAL = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));

	float c = lire_cote(monde.xz);
	vec3 col = mix(eau_profonde, eau_claire, smoothstep(0.04, 0.45, c));

	// les vagues d'écume qui avancent vers la côte, dans le halo
	float bande = fract(c * vagues_cote * 2.5 - TIME * vitesse_cote + sin(monde.x * 0.3 + monde.z * 0.2) * 0.08);
	float dans_halo = smoothstep(0.12, 0.3, c) * (1.0 - smoothstep(0.55, 0.62, c));
	float e = step(0.86, bande) * dans_halo * 0.85;
	// le bord du rivage : une frange d'écume continue
	e = max(e, smoothstep(0.42, 0.52, c) * 0.9);

	// liseré au contact des falaises et des rochers (profondeur de ce qu'il y a sous l'eau)
	float d = texture(profondeur, SCREEN_UV).r;
	vec4 fond = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, d, 1.0);
	fond.xyz /= fond.w;
	float ecart = max(VERTEX.z - fond.z, 0.0);
	e = max(e, 1.0 - smoothstep(0.0, largeur_contact, ecart));

	ALBEDO = mix(col, ecume, e);
	ROUGHNESS = mix(brillance, 0.9, e);
	SPECULAR = 0.45;
	ALPHA = mix(opacite, 1.0, e);
}
