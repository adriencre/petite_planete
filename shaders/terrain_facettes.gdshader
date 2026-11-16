// Terrain low-poly DA v6 : aplats par case (herbe / sable), strates nettes sur les falaises, liseré de mousse sous chaque rebord.
shader_type spatial;

uniform vec3 herbe_a : source_color = vec3(0.62, 0.82, 0.42);
uniform vec3 herbe_b : source_color = vec3(0.54, 0.77, 0.40);
uniform vec3 herbe_c : source_color = vec3(0.70, 0.85, 0.46);
uniform vec3 sable_a : source_color = vec3(0.93, 0.84, 0.70);
uniform vec3 sable_b : source_color = vec3(0.89, 0.79, 0.66);
uniform vec3 roche_a : source_color = vec3(0.88, 0.60, 0.56);
uniform vec3 roche_b : source_color = vec3(0.94, 0.74, 0.60);
uniform vec3 roche_c : source_color = vec3(0.96, 0.86, 0.76);
uniform vec3 mousse : source_color = vec3(0.47, 0.66, 0.40);
uniform float taille_case = 6.0;
uniform float hauteur_niveau = 2.5;
uniform float hauteur_sable = 1.0;   // sous cette hauteur, le dessus est du sable
uniform float epaisseur_mousse = 0.3;

varying vec3 wpos;
varying vec3 wnorm;

float hash2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnorm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	vec3 col;
	if (wnorm.y > 0.5) {
		// dessus : une teinte unie par demi-case, choisie au hasard parmi 3
		float h = hash2(floor(wpos.xz / (taille_case * 0.5)));
		if (wpos.y < hauteur_sable)
			col = h < 0.5 ? sable_a : sable_b;
		else
			col = h < 0.33 ? herbe_a : (h < 0.66 ? herbe_b : herbe_c);
	} else {
		// falaise : 3 strates par niveau, couleurs nettes
		float y = (wpos.y - 0.6) / hauteur_niveau;
		float bande = floor(y * 3.0);
		float k = mod(bande, 3.0);
		col = k < 0.5 ? roche_a : (k < 1.5 ? roche_b : roche_c);
		// liseré de mousse juste sous le rebord de chaque niveau
		if (fract(y) * hauteur_niveau > hauteur_niveau - epaisseur_mousse && wpos.y > hauteur_sable)
			col = mousse;
		// facettes : léger décalage par face pour lire les angles
		col *= 0.94 + 0.12 * hash2(floor(wpos.xz * 0.5) + bande);
	}
	ALBEDO = col;
	ROUGHNESS = 1.0;
}
