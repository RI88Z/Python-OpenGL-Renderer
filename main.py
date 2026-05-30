from functools import partial

import glfw
import glm
from OpenGL.GL import (
    glEnable,
    glClear,
    glClearColor,
    GL_DEPTH_TEST,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
)

from renderer.utils import (
    LIGHT_TYPES,
    AppState,
    mouse_callback,
    key_callback,
    process_input,
    parse_args,
)
from renderer import Camera, Light, LightManager, Model, Shader, Window


def main():
    args = parse_args()

    state = AppState(
        camera=Camera(position=glm.vec3(0.0, 0.0, 5.0)),
        lights=LightManager(),
        current_shader_type=args.shader,
    )
    app_window = Window(args.width, args.height, "3D Model Viewer - keys 1, 2, 3")
    glfw.set_cursor_pos_callback(app_window.window, partial(mouse_callback, state))
    glfw.set_key_callback(app_window.window, partial(key_callback, state))
    glEnable(GL_DEPTH_TEST)

    shaders = {
        "PHONG": Shader("shaders/phong.vert", "shaders/phong.frag"),
        "GOURAUD": Shader("shaders/gouraud.vert", "shaders/gouraud.frag"),
        "TOON": Shader("shaders/toon.vert", "shaders/toon.frag"),
    }
    marker_shader = Shader("shaders/marker.vert", "shaders/marker.frag")

    state.camera.position = glm.vec3(*args.cam_pos)
    state.camera.movement_speed = args.speed
    state.camera.fov = args.fov
    state.camera.far = args.far
    state.camera.update_camera_vectors()

    my_model = Model(args.model, diffuse_path=args.diffuse, specular_path=args.specular)
    marker_model = Model("assets/models/sphere.obj")

    if args.light != "NONE":
        state.lights.add(
            Light(
                light_type=LIGHT_TYPES[args.light],
                position=glm.vec3(*args.light_pos),
                direction=glm.vec3(*args.light_dir),
                color=glm.vec3(*args.light_color),
            )
        )

    last_frame = 0.0

    print("Keys 1-3: switch shading model (Phong/Gouraud/Toon)")
    print(
        "If Toon Shader is selected use '[' key to level down and ']' key to level up"
    )
    print("WSAD: move, Mouse: look around")
    print("L: add light, K: remove light, N: next light, T: change light type")
    print("Arrows: move light on X/Z, E/Q: move light up/down")
    print("The bigger white marker is the selected light")

    while app_window.is_open():
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(state, app_window.window, delta_time)

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        active_shader = shaders[state.current_shader_type]
        active_shader.use()

        projection = state.camera.get_projection_matrix(
            app_window.width, app_window.height
        )
        view = state.camera.get_view_matrix()
        model_mat = glm.mat4(1.0)
        if args.rotate:
            model_mat = glm.rotate(
                model_mat, float(glfw.get_time()) * 0.5, glm.vec3(0.0, 1.0, 0.0)
            )

        active_shader.set_mat4("projection", projection)
        active_shader.set_mat4("view", view)
        active_shader.set_mat4("model", model_mat)
        state.lights.apply(active_shader)
        active_shader.set_vec3("viewPos", state.camera.position)
        if state.current_shader_type == "TOON":
            active_shader.set_int("toonBands", state.toon_bands)

        my_model.draw(active_shader)

        marker_shader.use()
        marker_shader.set_mat4("projection", projection)
        marker_shader.set_mat4("view", view)
        for i, light in enumerate(state.lights.lights):
            marker_mat = glm.translate(glm.mat4(1.0), light.position)
            scale = 0.16 if i == state.lights.selected else 0.08
            marker_mat = glm.scale(marker_mat, glm.vec3(scale, scale, scale))
            marker_shader.set_mat4("model", marker_mat)
            color = (
                glm.vec3(1.0, 1.0, 1.0) if i == state.lights.selected else light.color
            )
            marker_shader.set_vec3("markerColor", color)
            marker_model.draw(marker_shader)

        app_window.swap_buffers_and_poll()

    app_window.terminate()


if __name__ == "__main__":
    main()
