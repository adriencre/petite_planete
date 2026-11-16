// Terrain : herbe sur les faces plates (taches de couleurs), roche en strates sur les pentes, mousse entre les deux.
shader_type spatial;
#include "res://shaders/bruit.gdshaderinc"

group_uniforms Herbe;
uniform vec3 herbe_a : source_color = vec3(0.55, 0.80, 0.36);
uniform vec3 herbe_b : source_color = vec3(0.84, 0.86, 0.42);
uniform vec3 herbe_c : source_color = vec3(0.34, 0.68, 0.48);
uniform float limite_herbe : hint_range(0.0, 1.0) = 0.62;
group_uniforms Roche;
uniform vec3 roche_a : source_color = vec3(0.86, 0.55, 0.52);
uniform vec3 roche_b : source_color = vec3(0.94, 0.72, 0.56);
uniform vec3 roche_c : source_color = vec3(0.97, 0.88, 0.79);
uniform vec3 roche_creux : source_color = vec3(0.60, 0.43, 0.56);
uniform float echelle_strates = 0.22;
group_uniforms Sable;
uniform vec3 sable : source_color = vec3(0.97, 0.86, 0.72);
uniform vec3 sable_mouille : source_color = vec3(0.86, 0.70, 0.62);
uniform float hauteur_sable = -10.0;
group_uniforms Mousse;
uniform vec3 mousse : source_color = vec3(0.47, 0.64, 0.40);
group_uniforms Nuit;
uniform float nuit : hint_range(0.0, 1.0) = 0.0;
uniform vec3 lueur_mousse : source_color = vec3(0.15, 0.9, 0.75);

varying vec3 wpos;
varying vec3 wnorm;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnorm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	float n1 = fbm3(wpos * 0.22);
	float n2 = fbm3(wpos * 1.4);
	// roche : strates horizontales ondulées
	float s = wpos.y * echelle_strates + n1 * 1.2;
	float band = fract(s);
	vec3 rock = mix(roche_a, roche_b, smoothstep(0.3, 0.45, band));
	rock = mix(rock, roche_c, smoothstep(0.78, 0.86, band));
	rock *= 0.9 + 0.2 * hash3(vec3(floor(s)));
	rock = mix(rock, roche_creux, (1.0 - smoothstep(0.25, 0.5, n2)) * 0.55);
	// herbe : grandes taches de couleurs
	vec3 grass = mix(herbe_a, herbe_b, smoothstep(0.45, 0.68, n1));
	grass = mix(grass, herbe_c, smoothstep(0.5, 0.72, fbm3(wpos * 0.1 + 7.0)));
	grass *= 0.85 + 0.3 * n2;
	float up = wnorm.y + (n2 - 0.5) * 0.4;
	float g = smoothstep(limite_herbe - 0.05, limite_herbe + 0.05, up);
	float m = smoothstep(0.2, 0.45, up) * (1.0 - g) * smoothstep(0.4, 0.6, n2);
	vec3 col = mix(rock, mousse, m * 0.85);
	col = mix(col, grass, g);
	float hs = hauteur_sable + (n2 - 0.5) * 0.6;
	vec3 sand = mix(sable_mouille, sable, smoothstep(hs - 1.6, hs - 0.6, wpos.y)) * (0.92 + 0.16 * n2);
	ALBEDO = mix(sand, col, smoothstep(hs - 0.2, hs + 0.25, wpos.y));
	EMISSION = lueur_mousse * m * nuit * 0.8;
	ROUGHNESS = 0.95;
}
