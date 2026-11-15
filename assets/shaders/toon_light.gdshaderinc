// Éclairage doux partagé : lumière chaude, ombres teintées lavande.
uniform vec3 shadow_tint : source_color = vec3(0.5, 0.48, 0.75);

void light() {
	float l = clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION;
	float t = smoothstep(0.02, 0.45, l);
	DIFFUSE_LIGHT += LIGHT_COLOR / PI * mix(shadow_tint * 0.4, vec3(1.0), t);
}
