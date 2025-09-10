#version 130

uniform float peak_temp;

out vec4 frag_color;

void main() {
    vec4 base_color = vec4(0.8, 0.8, 1.0, 0.3); // Semi-transparent bluish bubble
    vec4 emission_color = vec4(0.0, 0.0, 0.0, 0.0);

    // Emit light when temperature is high
    if (peak_temp > 50000.0) {
        float emission_intensity = (peak_temp - 50000.0) / 100000.0;
        emission_color = vec4(1.0, 0.8, 0.5, 1.0) * emission_intensity;
    }

    frag_color = base_color + emission_color;
}
