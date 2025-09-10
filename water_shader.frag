#version 130

uniform sampler2D reflection_map;
uniform float time;

in vec4 vtx_color;
in vec2 vtx_texcoord;
in vec3 vtx_normal;
in vec3 vtx_position;
in vec3 vtx_eyevec;

out vec4 frag_color;

void main() {
    vec3 normal = normalize(vtx_normal);
    vec3 eyevec = normalize(vtx_eyevec);

    // Fresnel effect
    float fresnel = pow(1.0 - max(0.0, dot(eyevec, normal)), 3.0);
    
    // Simple reflection
    vec3 reflected_direction = reflect(eyevec, normal);
    vec4 reflected_color = texture(reflection_map, reflected_direction.xy * 0.5 + 0.5);

    // Blend between water color and reflected color
    vec4 water_color = vec4(0.0, 0.1, 0.3, 1.0);
    frag_color = mix(water_color, reflected_color, fresnel);
    
    // Simple specular highlight for a dynamic water surface effect
    vec3 light_dir = normalize(vec3(1, 1, 1)); // Assuming a static light
    vec3 halfway_dir = normalize(light_dir + eyevec);
    float spec = pow(max(dot(normal, halfway_dir), 0.0), 32.0);
    frag_color += vec4(spec, spec, spec, 1.0) * 0.5;
}
