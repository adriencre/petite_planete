// Les Lueurs : la vie de la planète, invisible tant qu'il y a de la lumière.
// Elles n'apparaissent que dans la brume (zones endormies) et seulement quand l'antenne du robot faiblit
// (global « lueur_vision », piloté par sa batterie).
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled;

uniform vec3 color_a : source_color = vec3(0.35, 1.0, 0.85);
uniform vec3 color_b : source_color = vec3(0.55, 0.6, 1.0);
uniform float intensity = 1.6;
uniform bool billboard = true;
uniform bool round_sprite = true; // particule ronde et douce (sinon : surface pleine)
uniform float flow = 0.0;         // > 0 : lueur qui court le long d'un ruban (UV.x)
uniform float weave = 0.0;        // > 0 : surface tissée de fils de lumière (nombre de fils)
uniform bool ash = false;         // « cendre » : maison effondrée du désert gris (gris, sans pulsation)
uniform bool everywhere = false;  // visible aussi dans les zones éveillées (pour les cendres)
uniform bool editor_preview = false; // visible dans l'éditeur (décors à placer à la main)

#include "res://assets/shaders/wake.gdshaderinc"

varying vec3 wpos;
varying float seed;

void vertex() {
	if (billboard) {
		MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
		MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0, 0, 0), vec4(0, length(MODEL_MATRIX[1].xyz), 0, 0), vec4(0, 0, length(MODEL_MATRIX[2].xyz), 0), vec4(0, 0, 0, 1));
	}
	wpos = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	if (!billboard) {
		wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	}
	seed = fract(sin(dot(wpos.xz, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	float fog = everywhere ? 1.0 : 1.0 - smoothstep(0.3, 0.7, wake_amount(wpos));
	float k = lueur_vision * fog;
	if (editor_preview && wake_enabled < 0.5) {
		k = 1.0; // dans l'éditeur : on voit ce qu'on place
	}
	if (k < 0.002) {
		discard;
	}
	float shape = 1.0;
	if (round_sprite) {
		float d = length(UV - 0.5) * 2.0;
		shape = pow(clamp(1.0 - d, 0.0, 1.0), 1.8);
	}
	if (flow > 0.0) {
		float across = 1.0 - abs(UV.y * 2.0 - 1.0);
		shape = smoothstep(0.0, 0.8, across) * (0.45 + 0.55 * pow(0.5 + 0.5 * sin(UV.x * 40.0 - TIME * flow), 3.0));
	}
	if (weave > 0.0) {
		vec2 g = abs(fract(UV * vec2(weave, weave * 0.6)) - 0.5) * 2.0;
		float threads = max(1.0 - smoothstep(0.0, 0.3, g.x), 1.0 - smoothstep(0.0, 0.3, g.y));
		shape *= 0.22 + 0.78 * threads;
	}
	float pulse = ash ? 0.55 : 0.7 + 0.3 * sin(TIME * (1.2 + seed * 1.5) + seed * 30.0);
	vec3 c = ash ? vec3(0.42, 0.45, 0.52) : mix(color_a, color_b, seed);
	ALBEDO = c * shape * pulse * k * intensity;
}
