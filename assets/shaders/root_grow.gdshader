// Racine qui pousse : le tube n'existe que jusqu'à « growth », s'affine vers la pointe,
// et une lueur dorée court en tête de la pousse puis s'éteint en écorce.
shader_type spatial;
render_mode specular_disabled, cull_disabled;

uniform vec3 bark : source_color = vec3(0.6, 0.47, 0.38);
uniform vec3 glow_color : source_color = vec3(1.0, 0.82, 0.5);
uniform float growth = 1.0;   // 0 = rien, 1 = racine entière
uniform float glow = 0.0;     // lueur générale pendant la croissance

#include "res://assets/shaders/toon_light.gdshaderinc"

varying float along;

void vertex() {
	along = UV.x;
	// derrière le front de pousse la racine a son épaisseur, devant elle se resserre jusqu'à rien
	float thickness = 1.0 - smoothstep(growth - 0.1, growth, along);
	VERTEX -= NORMAL * UV2.x * (1.0 - max(thickness, 0.12));
}

void fragment() {
	if (along > growth + 0.002) {
		discard;
	}
	float front = smoothstep(growth - 0.18, growth, along);
	ALBEDO = mix(bark, glow_color, front * 0.6);
	EMISSION = glow_color * (front * 2.5 + 0.35) * glow;
	ROUGHNESS = 1.0;
}
