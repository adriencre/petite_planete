// Bords de l'écran qui s'assombrissent (bleu-gris froid) quand la batterie du robot faiblit.
shader_type canvas_item;

uniform float strength = 0.0;
uniform vec3 tint : source_color = vec3(0.12, 0.13, 0.2);

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float d = length(p * vec2(1.0, 0.8));
	float v = smoothstep(0.25, 1.0, d) * clamp(strength * 1.5, 0.0, 0.9);
	COLOR = vec4(tint, v);
}
