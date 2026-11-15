// Racine lumineuse : l'énergie court le long du ruban jusqu'à « progress ».
shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, shadows_disabled;

uniform vec4 color : source_color = vec4(1.0, 0.82, 0.5, 1.0);
uniform float progress = 0.0;

void fragment() {
	float filled = 1.0 - smoothstep(progress - 0.03, progress, UV.x);
	float across = smoothstep(0.0, 0.7, 1.0 - abs(UV.y * 2.0 - 1.0));
	float flow = 0.55 + 0.45 * sin(UV.x * 70.0 - TIME * 5.0);
	float spark = (1.0 - smoothstep(0.0, 0.04, abs(UV.x - progress))) * step(progress, 0.995) * 2.5;
	ALBEDO = color.rgb * (filled * flow + spark) * across * 1.4;
}
