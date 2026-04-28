#version 330 core
out vec4 FragColor;
in vec2 TexCoords;
in vec3 LightingColor;

struct Material {
    sampler2D texture_diffuse1;
};
uniform Material material;

void main() {
    FragColor = vec4(LightingColor * vec3(texture(material.texture_diffuse1, TexCoords)), 1.0);
}