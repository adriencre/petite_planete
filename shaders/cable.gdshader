// Câble du robot : gaine sombre, pulsations dorées qui voyagent quand la lumière passe.
shader_type spatial;
render_mode cull_disabled;

uniform vec3 gaine : source_color = vec3(0.30, 0.27, 0.36);
uniform vec3 or_pulse : source_color = vec3(1.0, 0.78, 0.4);
// 0 = rien ne passe, 1 = plein flux
uniform float flux : hint_range(0.0, 1.0) = 0.0;
// +1 : du robot vers la lanterne (allumer) ; -1 : de la lanterne vers le robot (reprendre)
uniform float sens = 1.0;
uniform float vitesse = 1.3;
uniform float nombre_pulses = 5.0;

void fragment() {
	float bord = 1.0 - abs(UV.x * 2.0 - 1.0);
	ALBEDO = gaine * (0.55 + 0.45 * bord);
	float p = fract(UV.y * nombre_pulses - TIME * vitesse * sens);
	float pulse = smoothstep(0.0, 0.06, p) * (1.0 - smoothstep(0.06, 0.28, p));
	EMISSION = or_pulse * (pulse * 4.0 + 0.4) * flux * smoothstep(0.2, 0.8, bord);
	ROUGHNESS = 0.5;
}
