// Post-effet plein écran : les zones autour des lanternes éteintes sont « endormies » (grises, ternes).
// Quand une lanterne fleurit, son rayon d'éveil grandit : vague de couleur avec un front doré.
shader_type spatial;
render_mode unshaded, depth_test_disabled, depth_draw_never, cull_disabled, fog_disabled, skip_vertex_transform;

uniform sampler2D ecran : hint_screen_texture, filter_linear;
uniform sampler2D profondeur : hint_depth_texture, filter_nearest;
// xyz = centre, w = rayon de la zone endormie
uniform vec4 zones[4];
// rayon déjà réveillé de chaque zone (0 = endormie, >= rayon zone = réveillée)
uniform float eveils[4];
uniform int nombre_zones = 0;
uniform vec3 couleur_sommeil : source_color = vec3(0.78, 0.76, 0.84);
uniform float force_sommeil : hint_range(0.0, 1.0) = 0.82;
uniform vec3 couleur_front : source_color = vec3(1.0, 0.8, 0.45);
uniform float largeur_front = 1.4;
uniform float lueur_front = 0.55;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

void fragment() {
	vec3 c = texture(ecran, SCREEN_UV).rgb;
	float d = texture(profondeur, SCREEN_UV).r;
	if (d > 0.00001 && nombre_zones > 0) {
		vec4 vue = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, d, 1.0);
		vue.xyz /= vue.w;
		vec3 monde = (INV_VIEW_MATRIX * vec4(vue.xyz, 1.0)).xyz;
		float sommeil = 0.0;
		float front = 0.0;
		for (int i = 0; i < 4; i++) {
			if (i >= nombre_zones) break;
			float dist = distance(monde.xz, zones[i].xz);
			float dans_zone = 1.0 - smoothstep(zones[i].w - 3.0, zones[i].w, dist);
			float pas_reveille = smoothstep(eveils[i] - 0.6, eveils[i] + 0.6, dist);
			sommeil = max(sommeil, dans_zone * pas_reveille);
			float actif = step(0.01, eveils[i]) * (1.0 - step(zones[i].w, eveils[i]));
			front = max(front, actif * dans_zone * exp(-pow((dist - eveils[i]) / largeur_front, 2.0)));
		}
		float g = dot(c, vec3(0.3, 0.59, 0.11));
		vec3 gris = vec3(g) * couleur_sommeil * 1.1;
		c = mix(c, gris, sommeil * force_sommeil);
		c += couleur_front * front * lueur_front;
	}
	ALBEDO = c;
}
