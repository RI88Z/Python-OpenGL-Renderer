#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

struct Material {
    sampler2D texture_diffuse1;
};

uniform Material material;
uniform vec3 lightPos;
uniform vec3 lightColor;

void main() {
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float intensity = max(dot(norm, lightDir), 0.0);
    
    // Cel-shading (progowanie)
    float bands = 4.0;
    float quantizedIntensity = ceil(intensity * bands) / bands;
    if (quantizedIntensity < 0.1) quantizedIntensity = 0.1;

    vec3 color = vec3(texture(material.texture_diffuse1, TexCoords));
    FragColor = vec4(lightColor * color * quantizedIntensity, 1.0);
}