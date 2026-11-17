// Rivière et cascades low-poly (maquette.gd : « Riviere », « Cascades »), accordées à la mer
// (mer_facettes.gdshader) : turquoise pastel, facettes qui frémissent, écume blanche.
// - Rivière (chute = false) : UV.x = à travers le lit (0..1) ; le courant descend vers le sud (+Z).
//   Plus profonde au milieu, claire et écumeuse sur les berges ; des traînées d'écume filent avec le courant.
// - Cascade (chute = true) : UV.y = de haut (0) en bas (1). Des filets d'eau qui tombent vite, une lèvre
//   blanche en haut, de l'écume en bas. COLOR.r = 0 pour le voile du fond, 1 pour le voile de devant.
// Pas « unshaded » : la brume (brouillard de distance) la recouvre comme le reste.
shader_type spatial;
render_mode blend_mix, cull_disabled, specular_schlick_ggx, depth_draw_always;

uniform bool chute = false;
uniform vec3 eau_claire : source_color = vec3(0.62, 0.91, 0.88);
uniform vec3 eau_profonde : source_color = vec3(0.40, 0.76, 0.84);
uniform vec3 ecume : source_color = vec3(1.0, 0.97, 0.95);
uniform float vitesse = 0.8;
uniform float opacite : hint_range(0.0, 1.0) = 0.9;
uniform float frisson : hint_range(0.0, 0.3) = 0.05;
uniform float lueur : hint_range(0.0, 1.0) = 0.25;

varying vec3 monde;
varying float couche;

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
	return bruit(p) * 0.55 + bruit(p * 2.1 + 3.7) * 0.3 + bruit(p * 4.3 + 9.1) * 0.15;
}

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	couche = COLOR.r;
	float t = TIME * vitesse;
	if (chute) {
		// le voile tremble un peu vers l'avant
		VERTEX.z += sin(w.y * 3.0 + t * 4.0 + w.x * 2.0) * frisson;
	} else {
		VERTEX.y += (sin(w.x * 2.3 + t * 1.3) * 0.5 + sin(w.z * 1.7 - t * 2.1) * 0.5) * frisson;
	}
	monde = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// facettes : une normale plate par triangle
	NORMAL = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	float t = TIME * vitesse;
	vec3 col;
	float e;
	float a = opacite;
	if (chute) {
		float v = UV.y;
		// des filets qui tombent : bruit très étiré vers le bas
		float filets = fbm(vec2(UV.x * 9.0 + couche * 4.0, v * 1.2 - t * (2.2 + couche * 0.8)));
		col = mix(eau_claire, eau_profonde, 0.35 + 0.3 * filets);
		e = smoothstep(0.55, 0.75, filets) * 0.8;
		e = max(e, 1.0 - smoothstep(0.0, 0.12, v));          // la lèvre blanche en haut
		e = max(e, smoothstep(0.78, 1.0, v));                 // l'écume en bas
		a = mix(opacite, opacite * 0.55, couche);             // le voile de devant est plus léger
	} else {
		float travers = abs(UV.x - 0.5) * 2.0;                // 0 au milieu, 1 sur la berge
		col = mix(eau_profonde, eau_claire, smoothstep(0.2, 0.95, travers));
		// des traînées d'écume qui filent avec le courant
		float trainees = fbm(vec2(monde.x * 1.4, monde.z * 0.35 - t * 1.2));
		e = smoothstep(0.66, 0.74, trainees) * 0.7;
		// les berges : une frange d'écume qui ondule
		float berge = smoothstep(0.78, 0.94, travers + (bruit(vec2(monde.z * 1.5 - t, UV.x * 3.0)) - 0.5) * 0.12);
		e = max(e, berge);
	}
	ALBEDO = mix(col, ecume, e);
	EMISSION = ALBEDO * lueur;     // reste claire et vive, même à l'ombre des falaises
	ROUGHNESS = mix(0.25, 0.9, e);
	SPECULAR = 0.45;
	ALPHA = mix(a, 1.0, e * 0.8);
}
