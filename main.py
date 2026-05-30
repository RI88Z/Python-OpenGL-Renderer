import argparse

import glfw
import glm
from OpenGL.GL import *

from renderer import Camera, Light, LightManager, Model, Shader, Window
from renderer.light import DIRECTIONAL, POINT, SPOT

camera = Camera(position=glm.vec3(0.0, 0.0, 5.0))
lights = LightManager()
last_x, last_y = 640, 360
first_mouse = True
current_shader_type = "PHONG"

LIGHT_TYPES = {"POINT": POINT, "DIRECTIONAL": DIRECTIONAL, "SPOT": SPOT}
LIGHT_NAMES = ("POINT", "DIRECTIONAL", "SPOT")


def log_selected():
    if not lights.lights:
        print("No lights")
        return
    light = lights.lights[lights.selected]
    p = light.position
    print(
        f"Light {lights.selected + 1}/{len(lights.lights)}: "
        f"{LIGHT_NAMES[light.type]} at ({p.x:.1f}, {p.y:.1f}, {p.z:.1f})"
    )


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y
    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False
    xoffset = xpos - last_x
    yoffset = last_y - ypos
    last_x, last_y = xpos, ypos
    camera.process_mouse_movement(xoffset, yoffset)


def key_callback(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_L:
        lights.add(Light(position=glm.vec3(camera.position)))
    elif key == glfw.KEY_K:
        lights.remove_selected()
    elif key == glfw.KEY_N:
        lights.select_next()
    elif key == glfw.KEY_T:
        lights.cycle_type()
    else:
        return
    log_selected()


def process_input(window, delta_time):
    global current_shader_type
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard("RIGHT", delta_time)

    if glfw.get_key(window, glfw.KEY_1) == glfw.PRESS:
        current_shader_type = "PHONG"
    if glfw.get_key(window, glfw.KEY_2) == glfw.PRESS:
        current_shader_type = "GOURAUD"
    if glfw.get_key(window, glfw.KEY_3) == glfw.PRESS:
        current_shader_type = "TOON"

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
        lights.move_selected(move * delta_time * 2.0)


def parse_args():
    parser = argparse.ArgumentParser(description="3D Model Viewer")

    model = parser.add_argument_group("Model")
    model.add_argument("--model", required=True, help="model file path")

    texture = parser.add_argument_group("Textures")
    texture.add_argument("--diffuse", required=True, help="diffuse texture path")
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


def main():
    args = parse_args()

    global current_shader_type
    current_shader_type = args.shader
    app_window = Window(args.width, args.height, "3D Model Viewer - keys 1, 2, 3")
    glfw.set_cursor_pos_callback(app_window.window, mouse_callback)
    glfw.set_key_callback(app_window.window, key_callback)
    glEnable(GL_DEPTH_TEST)

    shaders = {
        "PHONG": Shader("shaders/phong.vert", "shaders/phong.frag"),
        "GOURAUD": Shader("shaders/gouraud.vert", "shaders/gouraud.frag"),
        "TOON": Shader("shaders/toon.vert", "shaders/toon.frag"),
    }
    marker_shader = Shader("shaders/marker.vert", "shaders/marker.frag")

    camera.position = glm.vec3(*args.cam_pos)
    camera.movement_speed = args.speed
    camera.fov = args.fov
    camera.far = args.far
    camera.update_camera_vectors()

    my_model = Model(args.model, diffuse_path=args.diffuse, specular_path=args.specular)
    marker_model = Model("assets/models/sphere.obj")

    if args.light != "NONE":
        lights.add(
            Light(
                light_type=LIGHT_TYPES[args.light],
                position=glm.vec3(*args.light_pos),
                direction=glm.vec3(*args.light_dir),
                color=glm.vec3(*args.light_color),
            )
        )

    last_frame = 0.0

    print("Keys 1-3: switch shading model (Phong/Gouraud/Toon)")
    print("WSAD: move, Mouse: look around")
    print("L: add light, K: remove light, N: next light, T: change light type")
    print("Arrows: move light on X/Z, E/Q: move light up/down")
    print("The bigger white marker is the selected light")

    while app_window.is_open():
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(app_window.window, delta_time)

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        active_shader = shaders[current_shader_type]
        active_shader.use()

        projection = camera.get_projection_matrix(app_window.width, app_window.height)
        view = camera.get_view_matrix()
        model_mat = glm.mat4(1.0)
        if args.rotate:
            model_mat = glm.rotate(
                model_mat, float(glfw.get_time()) * 0.5, glm.vec3(0.0, 1.0, 0.0)
            )

        active_shader.set_mat4("projection", projection)
        active_shader.set_mat4("view", view)
        active_shader.set_mat4("model", model_mat)
        lights.apply(active_shader)
        active_shader.set_vec3("viewPos", camera.position)

        my_model.draw(active_shader)

        marker_shader.use()
        marker_shader.set_mat4("projection", projection)
        marker_shader.set_mat4("view", view)
        for i, light in enumerate(lights.lights):
            marker_mat = glm.translate(glm.mat4(1.0), light.position)
            scale = 0.16 if i == lights.selected else 0.08
            marker_mat = glm.scale(marker_mat, glm.vec3(scale, scale, scale))
            marker_shader.set_mat4("model", marker_mat)
            color = glm.vec3(1.0, 1.0, 1.0) if i == lights.selected else light.color
            marker_shader.set_vec3("markerColor", color)
            marker_model.draw(marker_shader)

        app_window.swap_buffers_and_poll()

    app_window.terminate()


if __name__ == "__main__":
    main()
