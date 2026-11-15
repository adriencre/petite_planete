// Matériau de base des décors et du robot : une couleur unie + éclairage doux.
// Grisé tant que la zone est endormie (sauf si wake_affected = false, ex. le robot).
shader_type spatial;
render_mode specular_disabled;

uniform vec3 albedo : source_color = vec3(1.0);
uniform float emission_strength = 0.0;

#include "res://assets/shaders/toon_light.gdshaderinc"
#include "res://assets/shaders/wake.gdshaderinc"

varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	if (reveal_hidden(wpos, CAMERA_POSITION_WORLD, FRAGCOORD.xy)) {
		discard;
	}
	float w = wake_amount(wpos);
	float mist = mist_amount(wpos, w);
	ALBEDO = apply_wake(albedo, w) * (1.0 - mist);
	EMISSION = albedo * emission_strength * w + mist_tint() * mist;
	ROUGHNESS = 1.0;
}
