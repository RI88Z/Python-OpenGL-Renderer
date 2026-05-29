#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoords;

out vec2 TexCoords;
out vec3 LightingColor;

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

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform Light lights[MAX_LIGHTS];
uniform int numLights;
uniform vec3 viewPos;

vec3 calcLight(Light light, vec3 norm, vec3 fragPos, vec3 viewDir) {
    vec3 lightDir;
    float attenuation = 1.0;
    float intensity = 1.0;

    if (light.type == 1) {
        lightDir = normalize(-light.direction);
    } else {
        lightDir = normalize(light.position - fragPos);
        float dist = length(light.position - fragPos);
        attenuation = 1.0 / (light.constant + light.linear * dist + light.quadratic * dist * dist);
    }

    if (light.type == 2) {
        float theta = dot(lightDir, normalize(-light.direction));
        float epsilon = light.cutOff - light.outerCutOff;
        intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    }

    float diff = max(dot(norm, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);

    vec3 ambient = 0.2 * light.color;
    vec3 diffuse = diff * light.color;
    vec3 specular = 0.5 * spec * light.color;

    return (ambient + (diffuse + specular) * intensity) * attenuation;
}

void main() {
    vec3 FragPos = vec3(model * vec4(aPos, 1.0));
    vec3 Normal = mat3(transpose(inverse(model))) * aNormal;
    gl_Position = projection * view * vec4(FragPos, 1.0);
    TexCoords = aTexCoords;

    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    vec3 result = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        result += calcLight(lights[i], norm, FragPos, viewDir);
    }

    LightingColor = result;
}
