// Blocs de terrain : dessus en herbe tachetée (ou chemin), côtés en pierre à strates.
// Grisé tant que la zone est endormie.
shader_type spatial;
render_mode specular_disabled;

uniform int mode : hint_enum("Herbe", "Chemin", "Pierre") = 0;
uniform vec3 grass : source_color = vec3(0.612, 0.69, 0.494);
uniform vec3 grass_dark : source_color = vec3(0.557, 0.643, 0.463);
uniform vec3 grass_light : source_color = vec3(0.667, 0.733, 0.557);
uniform vec3 dirt : source_color = vec3(0.788, 0.737, 0.624);
uniform vec3 stone : source_color = vec3(0.725, 0.651, 0.545);
uniform vec3 stone_dark : source_color = vec3(0.557, 0.494, 0.427);

#include "res://assets/shaders/toon_light.gdshaderinc"
#include "res://assets/shaders/wake.gdshaderinc"

varying vec3 wpos;
varying vec3 wnrm;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	if (reveal_hidden(wpos, CAMERA_POSITION_WORLD, FRAGCOORD.xy)) {
		discard;
	}
	vec3 c;
	if (wnrm.y > 0.5 && mode != 2) {
		float n = noise(wpos.xz * 0.55) * 0.65 + noise(wpos.xz * 2.2) * 0.35;
		c = mix(grass_dark, grass, smoothstep(0.3, 0.5, n));
		c = mix(c, grass_light, smoothstep(0.62, 0.75, n));
		if (mode == 1) {
			c = mix(dirt, c, smoothstep(0.62, 0.7, noise(wpos.xz * 2.3)));
		}
	} else {
		float band = step(0.5, fract(wpos.y * 1.6 + noise(wpos.xz * 1.7) * 0.3));
		c = mix(stone, stone_dark, band * 0.35 + noise(wpos.xz * 2.0 + wpos.y) * 0.25);
	}
	float w = wake_amount(wpos);
	float mist = mist_amount(wpos, w);
	ALBEDO = apply_wake(c, w) * (1.0 - mist);
	EMISSION = mist_tint() * mist;
	ROUGHNESS = 1.0;
}
