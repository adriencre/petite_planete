// Les racines lumineuses de la grande lanterne (maquette.gd : _racines ; racine_lumineuse.gd).
// Écorce low-poly à facettes ; des veines en spirale qui s'allument en or quand la lumière monte.
// UV.x = le long de la racine : 0 à la petite lanterne, 1 à la grande. UV.y = le tour de la racine.
// `lumiere` = jusqu'où la lumière est montée depuis la petite lanterne (0 = éteinte, 1 = toute la racine).
shader_type spatial;
render_mode cull_disabled;

uniform vec3 ecorce : source_color = vec3(0.62, 0.47, 0.40);
uniform vec3 ecorce_claire : source_color = vec3(0.80, 0.66, 0.54);
uniform vec3 couleur_or : source_color = vec3(1.0, 0.76, 0.38);
uniform float lumiere : hint_range(0.0, 1.0) = 0.0;
uniform float energie = 5.0;
// Une très faible lueur au repos : on devine qu'elles peuvent s'allumer.
uniform float veille : hint_range(0.0, 0.3) = 0.08;

float hash(float n) {
	return fract(sin(n * 127.1) * 43758.5453);
}

void fragment() {
	// facettes : une normale plate par triangle
	NORMAL = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	float le_long = UV.x;
	float autour = UV.y;
	// l'écorce : chaque anneau un peu plus clair ou plus sombre
	float anneau = hash(floor(le_long * 60.0));
	vec3 col = mix(ecorce, ecorce_claire, 0.25 + 0.5 * anneau);
	// les veines : deux spirales fines qui courent le long de la racine
	// (elles ondulent et s'amincissent par endroits, comme de vraies veines)
	float ondule = sin(le_long * 45.0) * 0.06 + sin(le_long * 13.0 + autour * 6.283) * 0.04;
	float s = fract(autour * 2.0 + le_long * 5.0 + ondule);
	float epaisseur = 0.035 + 0.03 * (0.5 + 0.5 * sin(le_long * 23.0));
	float veine = 1.0 - smoothstep(epaisseur, epaisseur + 0.04, abs(s - 0.5));
	// jusqu'où la lumière est montée, avec un front plus vif
	float allume = 1.0 - smoothstep(lumiere - 0.015, lumiere + 0.015, le_long);
	allume *= step(0.001, lumiere);
	float front = exp(-pow((le_long - lumiere) / 0.03, 2.0)) * step(0.001, lumiere) * (1.0 - step(0.999, lumiere));
	// toute la racine allumée : des pulsations filent vers la grande lanterne
	float pulsation = smoothstep(0.85, 1.0, fract(le_long * 2.5 - TIME * 0.45)) * step(0.999, lumiere);
	float lueur = veine * (veille + allume * (0.7 + 0.8 * pulsation)) + front * (0.6 + veine);
	ALBEDO = mix(col, couleur_or, allume * (veine * 0.6 + 0.12));   // allumée, toute l'écorce se réchauffe un peu
	EMISSION = couleur_or * energie * lueur;
	ROUGHNESS = 0.9;
}
