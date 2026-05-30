#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

struct Material {
    sampler2D texture_diffuse1;
};

struct Light {
    int type;
    vec3 position;
    vec3 direction;
    vec3 color;
    float constant;
    float linear;
    float quadratic;
    float cutOff;
    float outerCutOff;
};

#define MAX_LIGHTS 16

uniform Material material;
uniform Light lights[MAX_LIGHTS];
uniform int numLights;
uniform vec3 viewPos;
uniform int toonBands;

vec3 calcLight(Light light, vec3 norm, vec3 viewDir, vec3 color) {
    vec3 lightDir;
    float attenuation = 1.0;
    float spotIntensity = 1.0;

    if (light.type == 1) {
        lightDir = normalize(-light.direction);
    } else {
        lightDir = normalize(light.position - FragPos);
        float dist = length(light.position - FragPos);
        attenuation = 1.0 / (light.constant + light.linear * dist + light.quadratic * dist * dist);
    }

    if (light.type == 2) {
        float theta = dot(lightDir, normalize(-light.direction));
        float epsilon = light.cutOff - light.outerCutOff;
        spotIntensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    }

    float intensity = max(dot(norm, lightDir), 0.0);
    float quantized = ceil(intensity * float(toonBands)) / float(toonBands);

    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    float specular = (intensity > 0.0 && spec > 0.5) ? 0.8 : 0.0;

    return (light.color * color * quantized + specular * light.color) * spotIntensity * attenuation;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 color = vec3(texture(material.texture_diffuse1, TexCoords));

    vec3 result = color * 0.1;
    for (int i = 0; i < numLights; i++) {
        result += calcLight(lights[i], norm, viewDir, color);
    }

    FragColor = vec4(result, 1.0);
}
