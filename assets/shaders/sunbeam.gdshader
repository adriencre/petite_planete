// Rayon de soleil qui perce la brume : cône lumineux doux, poussières qui scintillent.
// Non affecté par la brume du sommeil (c'est la seule chose vivante au début).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

uniform vec4 color : source_color = vec4(1.0, 0.86, 0.6, 1.0);
uniform float intensity = 0.55;

void fragment() {
	float along = UV.y;                                   // 0 en haut, 1 au sol
	float ends = smoothstep(0.0, 0.35, along) * (1.0 - smoothstep(0.92, 1.0, along));
	float edge = pow(clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), 1.6);
	float streaks = 0.75 + 0.25 * sin(UV.x * 40.0 + TIME * 0.6) * sin(UV.y * 9.0 - TIME * 0.9);
	ALBEDO = color.rgb * intensity * ends * edge * streaks;
}
