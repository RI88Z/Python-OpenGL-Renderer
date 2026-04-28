import glfw
import glm
from OpenGL.GL import *

from camera import Camera
from model import Model
from shader import Shader
from window import Window

# Zmienne globalne do obsługi myszy (wymagane ze względu na charakter callbacków GLFW)
camera = Camera(position=glm.vec3(0.0, 0.0, 5.0))
last_x, last_y = 640, 360  # Środek ekranu dla 1280x720
first_mouse = True


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # Odwrócone, ponieważ Y rośnie w dół ekranu

    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)


def process_input(window, delta_time):
    """Obsługa klawiatury (WSAD + Escape)."""
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


def main():
    app_window = Window(1280, 720, "Obj Viewer - Etap 1: Architektura")

    # Rejestracja zdarzenia myszy
    glfw.set_cursor_pos_callback(app_window.window, mouse_callback)

    # Włączamy test głębokości (Z-Buffer), absolutnie krytyczne dla grafiki 3D
    glEnable(GL_DEPTH_TEST)

    # Trywialny shader testowy przepuszczający geometrię i malujący ją na pomarańczowo
    test_vertex_shader = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    void main() {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }
    """

    test_fragment_shader = """
    #version 330 core
    out vec4 FragColor;
    void main() {
        FragColor = vec4(1.0, 0.5, 0.2, 1.0);
    }
    """

    shader = Shader(test_vertex_shader, test_fragment_shader)

    delta_time = 0.0
    last_frame = 0.0

    my_model = Model("cube.obj", diffuse_path="diffuse.jpg", specular_path=None)

    # --- PĘTLA RENDEROWANIA ---
    while app_window.is_open():
        # Obliczenie czasu klatki (delta_time)
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        # Wejście
        process_input(app_window.window, delta_time)

        # Renderowanie (czyszczenie buforów koloru i głębokości)
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Aktywacja shadera
        shader.use()

        # Obliczanie macierzy widoku i rzutowania
        projection = camera.get_projection_matrix(app_window.width, app_window.height)
        view = camera.get_view_matrix()
        model = glm.mat4(1.0)  # Na ten moment macierz tożsamościowa

        # Przesyłanie uniformów
        shader.set_mat4("projection", projection)
        shader.set_mat4("view", view)
        shader.set_mat4("model", model)

        my_model.draw(shader)

        # Wymiana buforów i obsługa zdarzeń okna
        app_window.swap_buffers_and_poll()

    app_window.terminate()


if __name__ == "__main__":
    main()
