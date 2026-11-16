// Créature de la brume : translucide, phosphorescente, bord lumineux (fresnel).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never;

uniform vec3 couleur : source_color = vec3(0.3, 1.0, 0.85);
uniform vec3 coeur : source_color = vec3(0.7, 0.6, 1.0);
uniform float apparition : hint_range(0.0, 1.0) = 0.0;
uniform float intensite = 1.6;

void fragment() {
	float fres = pow(1.0 - abs(dot(NORMAL, VIEW)), 2.0);
	float pulse = 0.8 + 0.2 * sin(TIME * 2.0 + UV.y * 6.0);
	vec3 c = mix(coeur * 0.35, couleur, fres) * pulse * intensite;
	ALBEDO = c * apparition;
}
