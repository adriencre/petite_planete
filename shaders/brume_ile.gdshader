// La brume de l'île (brouillard volumétrique, sur un grand FogVolume posé par maquette.gd).
// Elle couvre toute l'île, plus épaisse près du sol, et dérive lentement en nappes.
// Les lanternes allumées la chassent : là où leur zone est réveillée, la brume se retire.
// Les zones et leur éveil sont les mêmes que pour zone_endormie.gdshader (poussés par zone_endormie.gd).
shader_type fog;

// xyz = centre, w = rayon de la zone ; eveils = rayon déjà réveillé (0 = endormie)
uniform vec4 zones[4];
uniform float eveils[4];
uniform int nombre_zones = 0;

uniform float densite : hint_range(0.0, 4.0) = 0.16;
// Hauteur (m) au-dessus du sol sur laquelle la brume s'amincit : une couche épaisse au ras du sol.
uniform float hauteur : hint_range(0.2, 10.0) = 1.4;
// Hauteur du sol de chaque case (maquette.gd : une texel par case, R = hauteur / sol_max).
uniform sampler2D sol : filter_nearest, repeat_disable;
// xy = coin nord-ouest de la carte (x, z), zw = taille de la carte (m).
uniform vec4 sol_rect = vec4(-36.0, -30.0, 72.0, 60.0);
uniform float sol_max = 20.0;
uniform vec3 couleur : source_color = vec3(0.84, 0.8, 0.9);
// Petite lueur propre, pour qu'elle reste pâle et pastel même à l'ombre.
uniform vec3 lueur : source_color = vec3(0.17, 0.15, 0.21);
uniform float echelle_nappes = 0.09;
uniform vec2 vent = vec2(0.25, 0.08);
// La bulle de l'antenne du robot (brume_batterie.gd) : xyz = le robot, w = rayon (0 = pas de bulle).
uniform vec4 robot = vec4(0.0);
// La bulle de la lanterne de proue de la barque (barque.gd : bulle_lanterne) : pareil.
uniform vec4 barque = vec4(0.0);
// Ce qui reste de brume dans une zone réveillée (0 = air clair).
uniform float reste_eveil : hint_range(0.0, 1.0) = 0.06;

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float bruit(vec3 x) {
	vec3 i = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash(i + vec3(0, 0, 0)), hash(i + vec3(1, 0, 0)), f.x),
	               mix(hash(i + vec3(0, 1, 0)), hash(i + vec3(1, 1, 0)), f.x), f.y),
	           mix(mix(hash(i + vec3(0, 0, 1)), hash(i + vec3(1, 0, 1)), f.x),
	               mix(hash(i + vec3(0, 1, 1)), hash(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

float nappes(vec3 p) {
	vec3 q = p * echelle_nappes + vec3(vent.x, 0.02, vent.y) * TIME * 0.4;
	float n = bruit(q) * 0.55 + bruit(q * 2.1 + 3.7) * 0.3 + bruit(q * 4.3 + 9.1) * 0.15;
	return smoothstep(0.3, 0.7, n);
}

void fog() {
	vec3 p = WORLD_POSITION;
	// combien ce point est réveillé par une lanterne
	float reveil = 0.0;
	for (int i = 0; i < 4; i++) {
		if (i >= nombre_zones) break;
		float dist = distance(p.xz, zones[i].xz);
		float dans_zone = 1.0 - smoothstep(zones[i].w - 3.0, zones[i].w, dist);
		float eveille = 1.0 - smoothstep(eveils[i] - 1.5, eveils[i] + 1.5, dist);
		reveil = max(reveil, dans_zone * eveille);
	}
	vec2 uv = (p.xz - sol_rect.xy) / sol_rect.zw;
	float sol_ici = (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) ? 0.0 : texture(sol, uv).r * sol_max;
	float h = exp(-max(p.y - sol_ici, 0.0) / hauteur);
	// bords du volume : la brume s'efface doucement
	float bord = min(min(UVW.x, 1.0 - UVW.x), min(UVW.z, 1.0 - UVW.z));
	float fondu = smoothstep(0.0, 0.12, bord) * smoothstep(0.0, 0.1, 1.0 - UVW.y);
	float d = densite * h * (0.4 + 0.6 * nappes(p)) * fondu;   // un fond partout : un vrai brouillard, pas des trous
	// la lumière de l'antenne repousse la brume autour du robot
	float bulle = robot.w > 0.0 ? smoothstep(robot.w * 0.55, robot.w, distance(p.xz, robot.xz)) : 1.0;
	// et la lanterne de proue autour de la barque
	bulle *= barque.w > 0.0 ? smoothstep(barque.w * 0.55, barque.w, distance(p.xz, barque.xz)) : 1.0;
	DENSITY = d * mix(1.0, reste_eveil, reveil) * bulle;
	ALBEDO = couleur;
	EMISSION = lueur;
}
