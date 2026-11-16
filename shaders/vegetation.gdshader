// Brins d'herbe et fleurs (MultiMesh) : vent doux, couleur assortie aux taches du sol.
// Couleur de sommet alpha = 0 -> brin d'herbe ; alpha = 1 -> tête de fleur (couleur de l'instance).
shader_type spatial;
render_mode cull_disabled;
#include "res://shaders/bruit.gdshaderinc"

uniform vec3 herbe_a : source_color = vec3(0.55, 0.80, 0.36);
uniform vec3 herbe_b : source_color = vec3(0.84, 0.86, 0.42);
uniform vec3 herbe_c : source_color = vec3(0.34, 0.68, 0.48);
uniform vec3 ombre_pied : source_color = vec3(0.26, 0.48, 0.34);
uniform vec3 eclat_pointe : source_color = vec3(1.0, 0.95, 0.65);
uniform float vent : hint_range(0.0, 1.0) = 0.18;
uniform float vitesse_vent = 1.2;
uniform float nuit : hint_range(0.0, 1.0) = 0.0;
uniform vec3 lueur_pointe : source_color = vec3(0.2, 0.95, 0.8);

varying float h;
varying vec3 origine;

void vertex() {
	h = UV.y;
	origine = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float w = sin(TIME * vitesse_vent + origine.x * 0.5 + origine.z * 0.3)
			+ 0.4 * sin(TIME * vitesse_vent * 2.3 + origine.x * 1.7);
	VERTEX.x += w * vent * h * h;
	VERTEX.z += w * vent * 0.4 * h * h;
	NORMAL = vec3(0.0, 1.0, 0.0);
}

void fragment() {
	float n1 = fbm3(origine * 0.22);
	vec3 grass = mix(herbe_a, herbe_b, smoothstep(0.45, 0.68, n1));
	grass = mix(grass, herbe_c, smoothstep(0.5, 0.72, fbm3(origine * 0.1 + 7.0)));
	vec3 brin = mix(ombre_pied, grass, smoothstep(0.0, 0.6, h));
	brin = mix(brin, eclat_pointe, smoothstep(0.75, 1.0, h) * 0.35);
	ALBEDO = mix(brin, COLOR.rgb, COLOR.a);
	ROUGHNESS = 0.9;
	BACKLIGHT = vec3(0.35, 0.4, 0.2) * h;
	float n_lueur = step(0.82, fract(sin(dot(floor(origine.xz * 3.0), vec2(12.9, 78.2))) * 43758.5));
	EMISSION = (lueur_pointe * smoothstep(0.7, 1.0, h) * n_lueur * 0.9 + COLOR.rgb * COLOR.a * 0.5) * nuit;
}
