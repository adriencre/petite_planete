// Un rayon de lumière doux qui monte d'une source (pierre-soleil…) : un cône additif, plus fort en bas,
// qui s'efface vers le haut et sur ses bords. Il traverse la brume (fog_disabled) : on le voit de loin,
// comme un phare dans le brouillard.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 couleur : source_color = vec3(1.0, 0.75, 0.38);
uniform float intensite = 0.55;
uniform float hauteur = 10.0;
uniform float vitesse_pulse = 1.2;

varying float h;

void vertex() {
	h = clamp(VERTEX.y / hauteur + 0.5, 0.0, 1.0);   // 0 en bas, 1 en haut
}

void fragment() {
	float bords = pow(abs(dot(NORMAL, VIEW)), 1.5);   // doux sur les côtés du cône
	float monte = pow(1.0 - h, 2.2);
	float pulse = 0.85 + 0.15 * sin(TIME * vitesse_pulse + h * 6.0);
	ALBEDO = couleur * intensite * bords * monte * pulse;
}
