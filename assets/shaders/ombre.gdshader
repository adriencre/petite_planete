// Matériau du monde de l'ombre : couleur unie, éclairage doux (ombres bleu nuit) et parties lumineuses.
// Pas de grisé « île endormie » : ce monde-là est vivant justement quand l'île dort.
// Par objet (réglé par OmbreObjet) :
//   reveal : 0 = invisible, 1 = là (apparition en pointillé doux entre les deux) ;
//   ash    : 1 = cendre grise, éteinte (la cicatrice d'une lanterne allumée).
shader_type spatial;
render_mode specular_disabled;

uniform vec3 albedo : source_color = vec3(1.0);
uniform float emission_strength = 0.0;
uniform vec3 shadow_tint : source_color = vec3(0.22, 0.26, 0.5);

instance uniform float reveal = 1.0;
instance uniform float ash = 0.0;

float bayer(vec2 frag_coord) {
	const float m[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	ivec2 i = ivec2(mod(floor(frag_coord / 2.0), 4.0));
	return (m[i.x + i.y * 4] + 0.5) / 16.0;
}

void fragment() {
	if (reveal < 0.999 && reveal <= bayer(FRAGCOORD.xy)) {
		discard;
	}
	float grey = dot(albedo, vec3(0.3, 0.55, 0.15));
	vec3 col = mix(albedo, vec3(grey) * vec3(0.62, 0.62, 0.68), ash);
	ALBEDO = col;
	EMISSION = albedo * emission_strength * (1.0 - ash);
	ROUGHNESS = 1.0;
}

void light() {
	float l = clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION;
	float t = smoothstep(0.02, 0.45, l);
	DIFFUSE_LIGHT += LIGHT_COLOR / PI * mix(shadow_tint * 0.5, vec3(1.0), t);
}
