// Vision du robot (plein écran) : trouble quand la batterie baisse, paupière pour la bascule N.
shader_type canvas_item;

uniform sampler2D ecran : hint_screen_texture, filter_linear_mipmap;
uniform float trouble : hint_range(0.0, 1.0) = 0.0;
uniform float paupiere : hint_range(0.0, 1.0) = 0.0;
uniform vec3 teinte_trouble : source_color = vec3(0.62, 0.72, 0.95);
uniform float vignette : hint_range(0.0, 1.0) = 0.3;

float h(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

void fragment() {
	vec2 uv = SCREEN_UV;
	// grésillement : bandes horizontales qui sautent
	float bande = floor(uv.y * 90.0);
	float actif = step(0.9 - trouble * 0.35, h(vec2(bande * 0.37, floor(TIME * 12.0))));
	uv.x += (h(vec2(bande, floor(TIME * 20.0))) - 0.5) * 0.014 * trouble * actif;
	float lod = trouble * 2.5;
	vec3 c;
	c.r = textureLod(ecran, uv + vec2(0.004 * trouble, 0.0), lod).r;
	c.g = textureLod(ecran, uv, lod).g;
	c.b = textureLod(ecran, uv - vec2(0.004 * trouble, 0.0), lod).b;
	float g = dot(c, vec3(0.3, 0.59, 0.11));
	c = mix(c, vec3(g) * teinte_trouble * 1.15, trouble * 0.7);
	c *= 1.0 - trouble * 0.25;
	c += (h(uv * vec2(800.0, 450.0) + fract(TIME)) - 0.5) * 0.08 * trouble;
	// vignette
	vec2 d = SCREEN_UV - 0.5;
	float vig = 1.0 - smoothstep(0.3 - trouble * 0.15, 0.85, length(d * vec2(1.0, 0.8)));
	c *= mix(1.0, vig, vignette + trouble * 0.5);
	// paupière : deux arcs qui se rejoignent
	float arc = 1.0 - 4.0 * d.x * d.x;
	float haut = paupiere * (0.5 + 0.09 * arc);
	float bas = 1.0 - paupiere * (0.5 + 0.06 * arc);
	float ouvert = smoothstep(haut - 0.015, haut + 0.015, SCREEN_UV.y) * (1.0 - smoothstep(bas - 0.015, bas + 0.015, SCREEN_UV.y));
	COLOR = vec4(c * ouvert, 1.0);
}
