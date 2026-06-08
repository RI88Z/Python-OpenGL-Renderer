import argparse
from dataclasses import dataclass

import glfw
import glm

from renderer import Camera, Light, LightManager
from renderer.light import DIRECTIONAL, POINT, SPOT


@dataclass
class AppState:
    camera: Camera
    lights: LightManager
    last_x: float = 640
    last_y: float = 360
    first_mouse: bool = True
    current_shader_type: str = "PHONG"
    toon_bands: int = 4
    prev_right_bracket_pressed: bool = False
    prev_left_bracket_pressed: bool = False


LIGHT_TYPES = {"POINT": POINT, "DIRECTIONAL": DIRECTIONAL, "SPOT": SPOT}
LIGHT_NAMES = ("POINT", "DIRECTIONAL", "SPOT")


def log_selected(state):
    if not state.lights.lights:
        print("No lights")
        return
    light = state.lights.lights[state.lights.selected]
    p = light.position
    print(
        f"Light {state.lights.selected + 1}/{len(state.lights.lights)}: "
        f"{LIGHT_NAMES[light.type]} at ({p.x:.1f}, {p.y:.1f}, {p.z:.1f})"
    )


def mouse_callback(state, window, xpos, ypos):
    if state.first_mouse:
        state.last_x, state.last_y = xpos, ypos
        state.first_mouse = False
    xoffset = xpos - state.last_x
    yoffset = state.last_y - ypos
    state.last_x, state.last_y = xpos, ypos
    state.camera.process_mouse_movement(xoffset, yoffset)


def key_callback(state, window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_L:
        state.lights.add(Light(position=glm.vec3(state.camera.position)))
    elif key == glfw.KEY_K:
        state.lights.remove_selected()
    elif key == glfw.KEY_N:
        state.lights.select_next()
    elif key == glfw.KEY_T:
        state.lights.cycle_type()
    else:
        return
    log_selected(state)


def process_input(state, window, delta_time):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        state.camera.process_keyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        state.camera.process_keyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        state.camera.process_keyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        state.camera.process_keyboard("RIGHT", delta_time)

    if glfw.get_key(window, glfw.KEY_1) == glfw.PRESS:
        state.current_shader_type = "PHONG"
    if glfw.get_key(window, glfw.KEY_2) == glfw.PRESS:
        state.current_shader_type = "GOURAUD"
    if glfw.get_key(window, glfw.KEY_3) == glfw.PRESS:
        state.current_shader_type = "TOON"

    rb = glfw.get_key(window, glfw.KEY_RIGHT_BRACKET) == glfw.PRESS
    lb = glfw.get_key(window, glfw.KEY_LEFT_BRACKET) == glfw.PRESS
    if rb and not state.prev_right_bracket_pressed:
        state.toon_bands = min(16, state.toon_bands + 1)
        print(f"Toon bands: {state.toon_bands}")
    if lb and not state.prev_left_bracket_pressed:
        state.toon_bands = max(1, state.toon_bands - 1)
        print(f"Toon bands: {state.toon_bands}")
    state.prev_right_bracket_pressed = rb
    state.prev_left_bracket_pressed = lb

    move = glm.vec3(0.0, 0.0, 0.0)
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        move.x -= 1.0
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        move.x += 1.0
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        move.z -= 1.0
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        move.z += 1.0
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        move.y += 1.0
    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        move.y -= 1.0
    if glm.length(move) > 0.0:
        state.lights.move_selected(move * delta_time * 2.0)


def parse_args():
    parser = argparse.ArgumentParser(description="3D Model Viewer")

    model = parser.add_argument_group("Model")
    model.add_argument("--model", required=True, help="model file path")

    texture = parser.add_argument_group("Textures")
    texture.add_argument("--diffuse", default=None, help="diffuse texture path")
    texture.add_argument("--specular", default=None, help="specular texture path")

    light = parser.add_argument_group("Lights")
    light.add_argument(
        "--light",
        choices=("NONE", "POINT", "DIRECTIONAL", "SPOT"),
        default="POINT",
        help="light type",
    )
    light.add_argument(
        "--light-pos",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        default=[1.2, 1.0, 2.0],
        help="light position",
    )
    light.add_argument(
        "--light-dir",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        default=[-0.2, -1.0, -0.3],
        help="light direction",
    )
    light.add_argument(
        "--light-color",
        nargs=3,
        type=float,
        metavar=("R", "G", "B"),
        default=[1.0, 1.0, 1.0],
        help="light color",
    )

    cam_group = parser.add_argument_group("Camera")
    cam_group.add_argument(
        "--cam-pos",
        nargs=3,
        type=float,
        default=[0.0, 0.0, 5.0],
        metavar=("X", "Y", "Z"),
        help="camera position",
    )
    cam_group.add_argument("--speed", type=float, default=2.5, help="camera speed")
    cam_group.add_argument("--fov", type=float, default=45.0, help="field of view")
    cam_group.add_argument("--far", type=float, default=1000.0, help="far clipping")

    s = parser.add_argument_group("Shaders")
    s.add_argument(
        "--shader",
        choices=("PHONG", "GOURAUD", "TOON"),
        default="PHONG",
        help="shader type",
    )

    parser.add_argument("--rotate", action="store_true", help="rotate object")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)

    return parser.parse_args()
