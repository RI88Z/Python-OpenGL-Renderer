import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Shader:
    def __init__(self, vertex_path: str, fragment_path: str):
        with open(vertex_path, "r") as f:
            vertex_src = f.read()
        with open(fragment_path, "r") as f:
            fragment_src = f.read()

        self.ID = self._compile_and_link(vertex_src, fragment_src)

    def _compile_and_link(self, v_src, f_src):
        vertex_shader = compileShader(v_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(f_src, GL_FRAGMENT_SHADER)

        shader_program = compileProgram(vertex_shader, fragment_shader, validate=False)

        # glDeleteShader(vertex_shader)
        # glDeleteShader(fragment_shader)

        return shader_program

    def use(self):
        glUseProgram(self.ID)

    def set_int(self, name: str, value: int):
        glUniform1i(glGetUniformLocation(self.ID, name), value)

    def set_float(self, name: str, value: float):
        glUniform1f(glGetUniformLocation(self.ID, name), value)

    def set_vec3(self, name: str, value: glm.vec3):
        glUniform3fv(glGetUniformLocation(self.ID, name), 1, glm.value_ptr(value))

    def set_mat4(self, name: str, value: glm.mat4):
        glUniformMatrix4fv(
            glGetUniformLocation(self.ID, name), 1, GL_FALSE, glm.value_ptr(value)
        )
