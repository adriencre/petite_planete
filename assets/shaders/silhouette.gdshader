// Silhouette du robot : visible seulement quand le décor le cache.
// Posé en « material_overlay » sur les pièces du robot.
shader_type spatial;
render_mode unshaded, depth_draw_never, depth_test_inverted, cull_back, skip_vertex_transform, blend_mix;

uniform vec4 color : source_color = vec4(0.93, 0.9, 0.84, 0.55);
uniform float push_to_camera = 0.75; // évite que le robot se « cache » lui-même

void vertex() {
	VERTEX = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	VERTEX += normalize(-VERTEX) * push_to_camera;
	NORMAL = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	ALBEDO = color.rgb;
	ALPHA = color.a;
}
