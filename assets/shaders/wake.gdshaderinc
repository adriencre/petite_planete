// Réveil de l'île : un masque vu de dessus (blanc = éveillé) fourni par scripts/wake/wake_manager.gd.
// Quand wake_enabled = 0 (éditeur, scènes de props), tout est éveillé.
global uniform sampler2D wake_mask;
global uniform vec4 wake_rect;
global uniform float wake_enabled;
global uniform vec3 player_pos;
global uniform vec4 mist_params; // x = début, y = fin (mètres autour du robot), z = intensité
global uniform vec3 mist_color;
global uniform float lueur_vision; // 0 = rien, 1 = les Lueurs sont visibles (batterie presque vide)
global uniform float reveal_strength; // vue en coupe dans les intérieurs (0 = off)

uniform bool wake_affected = true;

float wake_amount(vec3 world_pos) {
	if (!wake_affected || wake_enabled < 0.5) {
		return 1.0;
	}
	vec2 uv = clamp((world_pos.xz - wake_rect.xy) / wake_rect.zw, vec2(0.002), vec2(0.998));
	return texture(wake_mask, uv).r;
}

// Couleur endormie : presque grise, un peu froide et plus sombre.
vec3 sleepy_color(vec3 c) {
	float grey = dot(c, vec3(0.299, 0.587, 0.114));
	return mix(vec3(grey), c, 0.1) * vec3(0.8, 0.84, 0.95) * 0.74;
}

// Mélange endormi/éveillé + liseré lumineux chaud sur le front de la vague.
vec3 apply_wake(vec3 c, float w) {
	vec3 col = mix(sleepy_color(c), c, smoothstep(0.3, 0.7, w));
	// quand on voit les Lueurs, le monde endormi plonge dans la pénombre
	col *= 1.0 - lueur_vision * 0.62 * (1.0 - smoothstep(0.3, 0.7, w));
	// dans le noir complet, l'île passe à la nuit ; les zones éclairées deviennent un désert gris (cicatrices)
	float night = smoothstep(0.3, 0.95, lueur_vision);
	float luma = dot(col, vec3(0.299, 0.587, 0.114));
	col = mix(col, vec3(luma) * vec3(0.78, 0.78, 0.84), night * smoothstep(0.3, 0.7, w) * 0.75);
	col *= mix(vec3(1.0), vec3(0.5, 0.58, 0.86), night);
	float front = smoothstep(0.12, 0.45, w) * (1.0 - smoothstep(0.45, 0.8, w));
	return col + vec3(1.0, 0.86, 0.62) * front * 0.22;
}

// Brume du sommeil : les zones endormies se fondent dans la brume loin du robot.
float mist_amount(vec3 world_pos, float w) {
	if (!wake_affected || wake_enabled < 0.5) {
		return 0.0;
	}
	float d = distance(world_pos.xz, player_pos.xz);
	// dans le noir (monde de l'ombre), la brume s'éclaircit : on voit l'île de nuit
	float clear = 1.0 - 0.6 * smoothstep(0.3, 0.95, lueur_vision);
	return (1.0 - smoothstep(0.2, 0.8, w)) * smoothstep(mist_params.x, mist_params.y, d) * mist_params.z * clear;
}

// Trame régulière 4×4 (par blocs de 2 pixels) : un fondu en pointillé doux plutôt que du bruit.
float bayer_threshold(vec2 frag_coord) {
	const float m[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	ivec2 i = ivec2(mod(floor(frag_coord / 2.0), 4.0));
	return (m[i.x + i.y * 4] + 0.5) / 16.0;
}

// Vue en coupe : dans un intérieur, ce qui se trouve entre la caméra et le robot
// s'efface en pointillé (le sol sous le robot reste toujours visible).
bool reveal_hidden(vec3 world_pos, vec3 cam_pos, vec2 frag_coord) {
	if (!wake_affected || reveal_strength < 0.01) {
		return false;
	}
	if (world_pos.y < player_pos.y + 0.15) {
		return false;
	}
	vec3 head = player_pos + vec3(0.0, 0.9, 0.0);
	vec3 seg = head - cam_pos;
	float t = dot(world_pos - cam_pos, seg) / dot(seg, seg);
	if (t > 0.96) {
		return false;
	}
	float d = distance(world_pos, cam_pos + seg * clamp(t, 0.0, 1.0));
	float k = (1.0 - smoothstep(1.2, 2.1, d)) * reveal_strength;
	return k > bayer_threshold(frag_coord);
}

// Couleur de la brume : grise d'habitude, bleu nuit quand on voit les Lueurs.
vec3 mist_tint() {
	return mix(mist_color, vec3(0.03, 0.05, 0.11), smoothstep(0.0, 0.9, lueur_vision));
}
