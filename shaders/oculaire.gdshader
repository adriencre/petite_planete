shader_type canvas_item;

void fragment() {
	float rayon = length(UV - vec2(0.5)) * 2.0;
	vec3 vue = texture(TEXTURE, UV).rgb;
	float bord = smoothstep(0.77, 0.985, rayon);
	vec3 image = mix(vue, vec3(0.035, 0.052, 0.055), bord);
	float laiton = smoothstep(0.973, 0.978, rayon) * (1.0 - smoothstep(0.983, 0.99, rayon));
	image = mix(image, vec3(0.48, 0.36, 0.23), laiton);
	COLOR = vec4(image, (1.0 - smoothstep(0.991, 0.997, rayon)) * COLOR.a);
}
