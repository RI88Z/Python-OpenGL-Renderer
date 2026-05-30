#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;

struct Material {
    sampler2D texture_diffuse1;
    sampler2D texture_specular1;
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
uniform int hasSpecular;

vec3 calcLight(Light light, vec3 norm, vec3 viewDir, vec3 color, float specMap) {
    vec3 lightDir;
    float attenuation = 1.0;
    float intensity = 1.0;

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
        intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    }

    float diff = max(dot(norm, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16.0);

    vec3 ambient = 0.2 * light.color * color;
    vec3 diffuse = diff * light.color * color;
    vec3 specular = 0.5 * spec * specMap * light.color;

    return (ambient + (diffuse + specular) * intensity) * attenuation;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 color = vec3(texture(material.texture_diffuse1, TexCoords));
    float specMap = 1.0;
    if (hasSpecular == 1) {
        specMap = texture(material.texture_specular1, TexCoords).r;
    }

    vec3 result = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        result += calcLight(lights[i], norm, viewDir, color, specMap);
    }

    FragColor = vec4(result, 1.0);
}
