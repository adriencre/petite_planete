// Métal patiné du robot : laiton clair, taches de vert-de-gris et de rouille douce, rayures.
shader_type spatial;
#include "res://shaders/bruit.gdshaderinc"

uniform vec3 laiton : source_color = vec3(0.88, 0.73, 0.58);
uniform vec3 vert_de_gris : source_color = vec3(0.58, 0.80, 0.71);
uniform vec3 rouille : source_color = vec3(0.84, 0.58, 0.50);
uniform float quantite_patine : hint_range(0.0, 1.0) = 0.42;
uniform float quantite_rouille : hint_range(0.0, 1.0) = 0.3;
uniform float echelle = 6.0;

varying vec3 p_local;

void vertex() {
	p_local = VERTEX;
}

void fragment() {
	vec3 q = p_local * echelle;
	float n = fbm3(q);
	float n2 = fbm3(q * 2.7 + 13.0);
	float patine = smoothstep(1.0 - quantite_patine, 1.08 - quantite_patine, n);
	float rou = smoothstep(1.0 - quantite_rouille, 1.06 - quantite_rouille, n2) * (1.0 - patine);
	float rayure = smoothstep(0.985, 1.0, sin(q.x * 9.0 + q.y * 3.0 + n * 6.0)) * step(0.55, n2);
	vec3 c = laiton * (0.9 + 0.2 * n2);
	c = mix(c, rouille, rou * 0.8);
	c = mix(c, vert_de_gris, patine);
	c = mix(c, vec3(1.0, 0.95, 0.88), rayure * 0.6);
	ALBEDO = c;
	METALLIC = mix(0.5, 0.0, max(patine, rou));
	ROUGHNESS = mix(0.42, 0.85, max(patine, rou));
}
