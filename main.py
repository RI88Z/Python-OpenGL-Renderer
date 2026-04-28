import glfw
import glm
from OpenGL.GL import *

from camera import Camera
from model import Model
from shader import Shader
from window import Window

# Globalne
camera = Camera(position=glm.vec3(0.0, 0.0, 5.0))
last_x, last_y = 640, 360
first_mouse = True
current_shader_type = "PHONG"


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y
    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False
    xoffset = xpos - last_x
    yoffset = last_y - ypos
    last_x, last_y = xpos, ypos
    camera.process_mouse_movement(xoffset, yoffset)


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


def main():
    app_window = Window(1280, 720, "Przeglądarka Modeli 3D - Klawisze 1, 2, 3")
    glfw.set_cursor_pos_callback(app_window.window, mouse_callback)
    glEnable(GL_DEPTH_TEST)

    # Inicjalizacja Shaderów z plików
    shaders = {
        "PHONG": Shader("shaders/phong.vert", "shaders/phong.frag"),
        "GOURAUD": Shader("shaders/gouraud.vert", "shaders/gouraud.frag"),
        "TOON": Shader("shaders/toon.vert", "shaders/toon.frag"),
    }

    my_model = Model("cube.obj", diffuse_path="diffuse.jpg")

    light_pos = glm.vec3(1.2, 1.0, 2.0)
    light_color = glm.vec3(1.0, 1.0, 1.0)

    last_frame = 0.0

    print("--- System Uruchomiony ---")
    print("Klawisze 1-3: Zmiana cieniowania")
    print("WSAD: Ruch, Mysz: Rozglądanie")

    while app_window.is_open():
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(app_window.window, delta_time)

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        active_shader = shaders[current_shader_type]
        active_shader.use()

        # Macierze
        projection = camera.get_projection_matrix(app_window.width, app_window.height)
        view = camera.get_view_matrix()
        model_mat = glm.mat4(1.0)
        # Opcjonalnie: obracanie modelu w czasie
        model_mat = glm.rotate(
            model_mat, float(glfw.get_time()) * 0.5, glm.vec3(0.0, 1.0, 0.0)
        )

        active_shader.set_mat4("projection", projection)
        active_shader.set_mat4("view", view)
        active_shader.set_mat4("model", model_mat)

        # Światło
        active_shader.set_vec3("lightPos", light_pos)
        active_shader.set_vec3("lightColor", light_color)
        active_shader.set_vec3("viewPos", camera.position)

        my_model.draw(active_shader)

        app_window.swap_buffers_and_poll()

    app_window.terminate()


if __name__ == "__main__":
    main()
