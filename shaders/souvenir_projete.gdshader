// Le souvenir de la lampe-mère projeté sur le mur blanc (G3) : la lumière d'une lanterne magique.
// Mélange additif (le noir des images ne projette rien), fondu entre deux tableaux, léger battement de
// la flamme et bord adouci du disque. Piloté par scripts/lampe_mere.gd.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

uniform sampler2D image_a : source_color, filter_linear;
uniform sampler2D image_b : source_color, filter_linear;
uniform float melange : hint_range(0.0, 1.0) = 0.0;
uniform float force : hint_range(0.0, 1.0) = 0.0;
uniform float eclat = 0.85;

void fragment() {
	vec3 a = texture(image_a, UV).rgb;
	vec3 b = texture(image_b, UV).rgb;
	vec3 c = mix(a, b, smoothstep(0.0, 1.0, melange));
	// la flamme de la lampe bat un peu : la projection respire
	float battement = 0.94 + 0.04 * sin(TIME * 5.3) + 0.02 * sin(TIME * 11.7);
	float bord = 1.0 - smoothstep(0.42, 0.5, distance(UV, vec2(0.5)));
	ALBEDO = c * force * eclat * battement * bord;
}
