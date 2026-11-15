// Eau calme : plus claire près des rives, deux liserés d'écume qui suivent la côte.
// La carte des distances à la côte est fournie par scripts/water_foam.gd.
// Endormie : plate, grise, sans écume.
shader_type spatial;
render_mode unshaded;

uniform vec3 deep : source_color = vec3(0.416, 0.624, 0.741);
uniform vec3 shallow : source_color = vec3(0.549, 0.749, 0.812);
uniform vec3 foam : source_color = vec3(0.886, 0.945, 0.933);
uniform float foam_width = 0.12;
uniform float ring_distance = 0.42;
uniform sampler2D dist_tex : filter_linear, repeat_disable, hint_default_white;
uniform vec4 rect = vec4(-50.0, -50.0, 100.0, 100.0);
uniform float max_dist = 8.0;

#include "res://assets/shaders/wake.gdshaderinc"

void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float awake = wake_amount(w);
	float d = texture(dist_tex, (w.xz - rect.xy) / rect.zw).r * max_dist;
	// endormie : pas d'ondulation ni d'écume
	d += (sin(w.x * 2.3 + TIME * 0.8) * 0.02 + sin(w.z * 1.9 - TIME * 0.6) * 0.02 + sin(TIME * 0.7) * 0.015) * awake;
	vec3 c = mix(shallow, deep, smoothstep(0.0, 1.6, d));
	float edge = 1.0 - smoothstep(foam_width, foam_width + 0.03, d);
	float ring = smoothstep(ring_distance - 0.03, ring_distance, d) * (1.0 - smoothstep(ring_distance + 0.06, ring_distance + 0.09, d));
	c = mix(c, foam, max(edge, ring * 0.8) * smoothstep(0.5, 0.9, awake));
	ALBEDO = mix(apply_wake(c, awake), mist_tint(), mist_amount(w, awake));
}
