shader_type spatial;
// Mousse d'un ancien corps (calque posé par-dessus la texture du robot, en material_overlay).
// Des plaques de mousse à facettes poussent sur les faces tournées vers le ciel (en coordonnées monde,
// donc là où la pluie tombe sur le corps couché), avec quelques fleurs pâles ; ailleurs un voile ternit
// le crème du robot. Plaques en cellules nettes : ça reste low-poly, jamais « réaliste ».

render_mode blend_mix, cull_back, depth_draw_never;

uniform vec4 mousse_sombre : source_color = vec4(0.42, 0.56, 0.30, 1.0);
uniform vec4 mousse_claire : source_color = vec4(0.62, 0.73, 0.40, 1.0);
uniform vec4 fleur : source_color = vec4(0.96, 0.88, 0.92, 1.0);
uniform vec4 voile : source_color = vec4(0.55, 0.52, 0.42, 1.0);
uniform float couverture : hint_range(0.0, 1.0) = 0.62;   // part des faces hautes couvertes
uniform float taille_plaques = 7.0;                       // plaques par mètre
uniform float force_voile : hint_range(0.0, 1.0) = 0.28;

varying vec3 n_monde;
varying vec3 p_monde;

float hachage(vec3 c) {
	return fract(sin(dot(c, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

void vertex() {
	n_monde = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	p_monde = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float haut = smoothstep(0.15, 0.55, n_monde.y);
	vec3 cellule = floor(p_monde * taille_plaques);
	float h = hachage(cellule);
	float plaque = step(1.0 - couverture, h) * haut;
	// quelques plaques débordent un peu sur les flancs
	plaque = max(plaque, step(0.93, hachage(cellule + 7.0)) * smoothstep(-0.2, 0.2, n_monde.y));
	float claire = step(0.5, hachage(cellule + 3.0));
	vec3 c = mix(mousse_sombre.rgb, mousse_claire.rgb, claire);
	// une fleur pâle dans une plaque sur douze
	float f = step(0.92, hachage(floor(p_monde * taille_plaques * 2.5))) * plaque;
	c = mix(c, fleur.rgb, f);
	ALBEDO = mix(voile.rgb, c, plaque);
	ALPHA = max(plaque, force_voile);
	ROUGHNESS = 1.0;
}
