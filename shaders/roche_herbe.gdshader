// Terrain : herbe sur les faces plates (taches de couleurs), roche en strates sur les pentes, mousse entre les deux.
shader_type spatial;
#include "res://shaders/bruit.gdshaderinc"

group_uniforms Herbe;
uniform vec3 herbe_a : source_color = vec3(0.55, 0.80, 0.36);
uniform vec3 herbe_b : source_color = vec3(0.84, 0.86, 0.42);
uniform vec3 herbe_c : source_color = vec3(0.34, 0.68, 0.48);
uniform float limite_herbe : hint_range(0.0, 1.0) = 0.62;
group_uniforms Roche;
uniform vec3 roche_a : source_color = vec3(0.86, 0.55, 0.52);
uniform vec3 roche_b : source_color = vec3(0.94, 0.72, 0.56);
uniform vec3 roche_c : source_color = vec3(0.97, 0.88, 0.79);
uniform vec3 roche_creux : source_color = vec3(0.60, 0.43, 0.56);
uniform float echelle_strates = 0.22;
// Relief : normal map de pierre photoscannée (Poly Haven, CC0) en triplanar, la couleur reste procédurale.
uniform sampler2D roche_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float echelle_relief = 0.35;
uniform float force_relief : hint_range(0.0, 1.0) = 1.0;
// Facettes : normale par triangle (rendu taillé, low-poly), bruit et relief atténués.
uniform bool facettes = false;
uniform float intensite_relief : hint_range(0.5, 3.0) = 1.8;
group_uniforms Sable;
uniform vec3 sable : source_color = vec3(0.97, 0.86, 0.72);
uniform vec3 sable_mouille : source_color = vec3(0.86, 0.70, 0.62);
uniform float hauteur_sable = -10.0;
group_uniforms Mousse;
uniform vec3 mousse : source_color = vec3(0.47, 0.64, 0.40);
group_uniforms Nuit;
uniform float nuit : hint_range(0.0, 1.0) = 0.0;
uniform vec3 lueur_mousse : source_color = vec3(0.15, 0.9, 0.75);

varying vec3 wpos;
varying vec3 wnorm;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnorm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

// Normale tangente lue dans la texture (z reconstruit : marche aussi si Godot l'a compressée en RG).
vec3 lire_normale(vec2 uv) {
	vec2 xy = (texture(roche_normal, uv).xy * 2.0 - 1.0) * intensite_relief;
	xy /= max(1.0, length(xy));
	return vec3(xy, sqrt(max(1.0 - dot(xy, xy), 0.0)));
}

// Triplanar « whiteout » (Ben Golus) : renvoie la normale monde perturbée.
vec3 relief_triplanar(vec3 p, vec3 n) {
	vec3 bl = pow(abs(n), vec3(4.0));
	bl /= bl.x + bl.y + bl.z;
	vec3 sg = sign(n);
	vec2 uvx = p.zy; uvx.x *= sg.x;
	vec2 uvy = p.xz; uvy.x *= sg.y;
	vec2 uvz = p.xy; uvz.x *= -sg.z;
	vec3 tx = lire_normale(uvx); tx.x *= sg.x;
	vec3 ty = lire_normale(uvy + 0.37); ty.x *= sg.y;
	vec3 tz = lire_normale(uvz + 0.71); tz.x *= -sg.z;
	tx = vec3(tx.xy + n.zy, abs(tx.z) * n.x);
	ty = vec3(ty.xy + n.xz, abs(ty.z) * n.y);
	tz = vec3(tz.xy + n.xy, abs(tz.z) * n.z);
	return normalize(tx.zyx * bl.x + ty.xzy * bl.y + tz * bl.z);
}

void fragment() {
	vec3 nb = normalize(wnorm);
	if (facettes) {
		vec3 fn = normalize(cross(dFdx(wpos), dFdy(wpos)));
		nb = dot(fn, nb) < 0.0 ? -fn : fn;
	}
	vec3 rn = relief_triplanar(wpos * echelle_relief, nb);
	float creux = clamp(dot(rn, nb), 0.0, 1.0); // 1 = lisse, moins = fissure
	float n1 = fbm3(wpos * 0.22);
	float n2 = mix(fbm3(wpos * 1.4), 0.5, facettes ? 0.8 : 0.0); // facettes : aplats propres
	// roche : strates horizontales ondulées
	float s = wpos.y * echelle_strates + n1 * (facettes ? 0.15 : 1.2); // facettes : strates droites
	float band = fract(s);
	float flou = facettes ? 0.0 : 1.0; // facettes : bords de strates nets
	vec3 rock = mix(roche_a, roche_b, smoothstep(0.37 - 0.07 * flou, 0.38 + 0.07 * flou, band));
	rock = mix(rock, roche_c, smoothstep(0.815 - 0.035 * flou, 0.825 + 0.035 * flou, band));
	rock *= 0.9 + 0.2 * hash3(vec3(floor(s)));
	rock = mix(rock, roche_creux, (1.0 - smoothstep(0.25, 0.5, n2)) * 0.55);
	rock = mix(rock, roche_creux, (1.0 - smoothstep(0.8, 0.99, creux)) * 0.6 * force_relief * (facettes ? 0.0 : 1.0)); // fissures teintées lavande, jamais grises
	// herbe : grandes taches de couleurs
	vec3 grass = mix(herbe_a, herbe_b, smoothstep(0.45, 0.68, n1));
	grass = mix(grass, herbe_c, smoothstep(0.5, 0.72, fbm3(wpos * 0.1 + 7.0)));
	grass *= 0.85 + 0.3 * n2;
	float up = nb.y + (n2 - 0.5) * 0.4;
	float g = smoothstep(limite_herbe - 0.05, limite_herbe + 0.05, up);
	float m = smoothstep(0.2, 0.45, up) * (1.0 - g) * smoothstep(0.4, 0.6, n2);
	vec3 col = mix(rock, mousse, m * 0.85);
	col = mix(col, grass, g);
	float hs = hauteur_sable + (n2 - 0.5) * 0.6;
	vec3 sand = mix(sable_mouille, sable, smoothstep(hs - 1.6, hs - 0.6, wpos.y)) * (0.92 + 0.16 * n2);
	float terre = smoothstep(hs - 0.2, hs + 0.25, wpos.y);
	ALBEDO = mix(sand, col, terre);
	EMISSION = lueur_mousse * m * nuit * 0.8;
	ROUGHNESS = 0.95 - 0.12 * creux * (1.0 - g); // arêtes un peu plus polies que les fissures
	// relief seulement sur la roche (pas sous l'herbe ni sur le sable)
	float r = facettes ? 0.0 : force_relief * (1.0 - g) * terre;
	NORMAL = normalize((VIEW_MATRIX * vec4(normalize(mix(nb, rn, r)), 0.0)).xyz);
}
