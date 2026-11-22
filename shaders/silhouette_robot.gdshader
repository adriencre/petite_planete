shader_type spatial;
// La silhouette du robot quand une maison, un toit ou un mur le cache (vue de dessus).
// Posé en `material_overlay` sur ses maillages (joueur.gd) : on compare la profondeur du robot à celle
// de la scène ; là où quelque chose est devant lui (à plus de `marge` m), on dessine une silhouette
// dorée pâle, un peu plus vive sur les bords. Là où il est visible, rien ne change.
render_mode unshaded, depth_test_disabled, depth_draw_never, cull_back, blend_mix, shadows_disabled;

uniform sampler2D profondeur : hint_depth_texture, filter_nearest;
uniform vec4 couleur : source_color = vec4(1.0, 0.86, 0.58, 0.55);
// Écart minimal (m) entre l'obstacle et le robot : ses propres bras ne le cachent pas.
uniform float marge = 0.4;

void fragment() {
	float d = texture(profondeur, SCREEN_UV).r;
	vec4 vue = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, d, 1.0);
	float scene = -vue.z / vue.w;
	float robot = -VERTEX.z;
	if (scene > robot - marge) {
		discard;
	}
	float bord = 1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	ALBEDO = couleur.rgb;
	ALPHA = couleur.a * (0.65 + 0.35 * bord);
}
