// Rivière et cascade low-poly : bandes claires qui défilent dans le sens du courant (UV.y).
shader_type spatial;
render_mode blend_mix, cull_disabled, unshaded;

uniform vec3 eau : source_color = vec3(0.45, 0.80, 0.92);
uniform vec3 ecume : source_color = vec3(0.92, 0.98, 1.0);
uniform float vitesse = 0.6;
uniform float bandes = 6.0;
uniform float opacite = 0.85;

void fragment() {
	float v = fract(UV.y * bandes - TIME * vitesse + sin(UV.x * 6.0) * 0.08);
	float trait = step(0.82, v);
	ALBEDO = mix(eau, ecume, trait);
	ALPHA = opacite;
}
