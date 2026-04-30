import sys

import glfw
from OpenGL.GL import *


class Window:
    def __init__(self, width=1280, height=720, title="3D Model Viewer"):
        self.width = width
        self.height = height

        if not glfw.init():
            sys.exit("Error: failed to initialize GLFW.")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.width, self.height, title, None, None)
        if not self.window:
            glfw.terminate()
            sys.exit("Error: failed to create GLFW window.")

        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self._framebuffer_size_callback)

        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def _framebuffer_size_callback(self, window, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def is_open(self):
        return not glfw.window_should_close(self.window)

    def swap_buffers_and_poll(self):
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def terminate(self):
        glfw.terminate()
