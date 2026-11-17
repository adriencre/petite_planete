// Un croquis du carnet : une « photo » propre du lieu (carnet.gd : caméra dédiée, sans brume),
// redessinée à l'encre brune sur papier crème. Pour rester lisible :
// - les contours sont cherchés sur une image adoucie (pas de traits parasites dans l'herbe) ;
// - le lavis est réduit à trois tons (lumière, mi-teinte, ombre), comme un dessin à l'aquarelle sépia ;
// - les bords se fondent dans la page.
shader_type canvas_item;

uniform vec3 papier : source_color = vec3(0.97, 0.93, 0.84);
uniform vec3 encre : source_color = vec3(0.33, 0.24, 0.17);
uniform float force_traits : hint_range(0.0, 8.0) = 2.6;
uniform float seuil_traits : hint_range(0.0, 1.0) = 0.28;
uniform float lavis : hint_range(0.0, 1.0) = 0.55;

float lum(sampler2D tex, vec2 uv) {
	return dot(texture(tex, uv).rgb, vec3(0.3, 0.59, 0.11));
}

// luminosité adoucie : moyenne sur une petite croix
float douce(sampler2D tex, vec2 uv, vec2 p) {
	return (lum(tex, uv) * 2.0 + lum(tex, uv + vec2(p.x, 0.0)) + lum(tex, uv - vec2(p.x, 0.0))
		+ lum(tex, uv + vec2(0.0, p.y)) + lum(tex, uv - vec2(0.0, p.y))) / 6.0;
}

void fragment() {
	vec2 p = TEXTURE_PIXEL_SIZE * 2.0;
	float tl = douce(TEXTURE, UV + vec2(-p.x, -p.y), p);
	float t  = douce(TEXTURE, UV + vec2(0.0, -p.y), p);
	float tr = douce(TEXTURE, UV + vec2(p.x, -p.y), p);
	float l  = douce(TEXTURE, UV + vec2(-p.x, 0.0), p);
	float r  = douce(TEXTURE, UV + vec2(p.x, 0.0), p);
	float bl = douce(TEXTURE, UV + vec2(-p.x, p.y), p);
	float b  = douce(TEXTURE, UV + vec2(0.0, p.y), p);
	float br = douce(TEXTURE, UV + vec2(p.x, p.y), p);
	float gx = (tr + 2.0 * r + br) - (tl + 2.0 * l + bl);
	float gy = (bl + 2.0 * b + br) - (tl + 2.0 * t + tr);
	float trait = smoothstep(seuil_traits, seuil_traits + 0.25, length(vec2(gx, gy)) * force_traits);
	// lavis en trois tons
	float ici = douce(TEXTURE, UV, p * 0.5);
	float ton = ici > 0.62 ? 1.0 : (ici > 0.38 ? 0.62 : 0.3);
	vec3 col = mix(papier, mix(encre, papier, ton), lavis);
	col = mix(col, encre, trait * 0.9);
	// les bords se fondent dans la page, un peu irréguliers
	float irreg = 0.02 * sin(UV.y * 40.0) + 0.02 * sin(UV.x * 33.0);
	float bord = smoothstep(0.0, 0.09, min(min(UV.x, 1.0 - UV.x), min(UV.y, 1.0 - UV.y)) + irreg);
	COLOR = vec4(mix(papier, col, bord), 1.0);
}
