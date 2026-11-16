// Mer turquoise : clair et écume près des rochers, profond au large, petites vagues.
shader_type spatial;
render_mode specular_schlick_ggx;

uniform sampler2D profondeur_ecran : hint_depth_texture, filter_linear;
uniform vec3 eau_profonde : source_color = vec3(0.10, 0.52, 0.66);
uniform vec3 eau_claire : source_color = vec3(0.36, 0.88, 0.80);
uniform vec3 ecume : source_color = vec3(1.0, 0.97, 0.95);
uniform float largeur_eau_claire = 7.0;
uniform float largeur_ecume = 1.1;
uniform float force_vagues : hint_range(0.0, 0.5) = 0.1;
uniform float vitesse : hint_range(0.0, 2.0) = 0.35;
uniform float brillance : hint_range(0.0, 1.0) = 0.35;
uniform float reflet : hint_range(0.0, 1.0) = 0.15;
group_uniforms Nuit;
uniform float nuit : hint_range(0.0, 1.0) = 0.0;
uniform vec3 eau_nuit : source_color = vec3(0.02, 0.06, 0.16);
uniform vec3 lueur_nuit : source_color = vec3(0.2, 1.0, 0.85);

void fragment() {
	vec3 wpos = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 p = wpos.xz;
	float t = TIME * vitesse;
	vec3 n = vec3(
		sin(p.x * 0.35 + t) * 0.6 + sin((p.x + p.y) * 0.9 + t * 1.7) * 0.4,
		1.0 / max(force_vagues, 0.001),
		cos(p.y * 0.3 + t * 1.2) * 0.6 + sin((p.x - p.y) * 0.7 - t) * 0.4);
	NORMAL = normalize((VIEW_MATRIX * vec4(normalize(n), 0.0)).xyz);

	float d = textureLod(profondeur_ecran, SCREEN_UV, 0.0).r;
	vec4 fond = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, d, 1.0);
	fond.xyz /= fond.w;
	float ecart = max(VERTEX.z - fond.z, 0.0);

	vec3 col = mix(eau_claire, eau_profonde, smoothstep(0.0, largeur_eau_claire, ecart));
	float vague = sin(ecart * 5.0 - TIME * 1.5 + sin(p.x * 0.7) * 2.0) * 0.5 + 0.5;
	float e = 1.0 - smoothstep(0.0, largeur_ecume, ecart);
	e = max(e * e, step(0.75, vague) * (1.0 - smoothstep(0.0, largeur_ecume * 2.5, ecart)) * 0.8);
	col = mix(col, ecume, e);
	ALBEDO = mix(col, eau_nuit, nuit);
	EMISSION = lueur_nuit * e * nuit * 1.5;
	ROUGHNESS = brillance;
	SPECULAR = reflet;
}
