import glm

POINT = 0
DIRECTIONAL = 1
SPOT = 2

MAX_LIGHTS = 16


class Light:
    def __init__(
        self,
        light_type=POINT,
        position=glm.vec3(0.0, 0.0, 0.0),
        direction=glm.vec3(0.0, -1.0, 0.0),
        color=glm.vec3(1.0, 1.0, 1.0),
        cut_off=12.5,
        outer_cut_off=17.5,
    ):
        self.type = light_type
        self.position = glm.vec3(position)
        self.direction = glm.vec3(direction)
        self.color = glm.vec3(color)
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032
        self.cut_off = cut_off
        self.outer_cut_off = outer_cut_off

    def apply(self, shader, index):
        name = f"lights[{index}]"
        shader.set_int(f"{name}.type", self.type)
        shader.set_vec3(f"{name}.position", self.position)
        shader.set_vec3(f"{name}.direction", self.direction)
        shader.set_vec3(f"{name}.color", self.color)
        shader.set_float(f"{name}.constant", self.constant)
        shader.set_float(f"{name}.linear", self.linear)
        shader.set_float(f"{name}.quadratic", self.quadratic)
        shader.set_float(f"{name}.cutOff", glm.cos(glm.radians(self.cut_off)))
        shader.set_float(f"{name}.outerCutOff", glm.cos(glm.radians(self.outer_cut_off)))


class LightManager:
    def __init__(self):
        self.lights = []
        self.selected = 0

    def add(self, light):
        if len(self.lights) >= MAX_LIGHTS:
            return
        self.lights.append(light)
        self.selected = len(self.lights) - 1

    def remove_selected(self):
        if not self.lights:
            return
        self.lights.pop(self.selected)
        self.selected = max(0, self.selected - 1)

    def select_next(self):
        if self.lights:
            self.selected = (self.selected + 1) % len(self.lights)

    def cycle_type(self):
        if self.lights:
            light = self.lights[self.selected]
            light.type = (light.type + 1) % 3

    def move_selected(self, offset):
        if self.lights:
            self.lights[self.selected].position += offset

    def apply(self, shader):
        shader.set_int("numLights", len(self.lights))
        for i, light in enumerate(self.lights):
            light.apply(shader, i)
