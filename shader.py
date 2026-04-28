import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Shader:
    def __init__(self, vertex_src: str, fragment_src: str):
        """Kompiluje shadery i linkuje je w program."""
        self.ID = self._compile_and_link(vertex_src, fragment_src)

    def _compile_and_link(self, v_src, f_src):
        # Kompilacja Shaderów
        vertex_shader = compileShader(v_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(f_src, GL_FRAGMENT_SHADER)

        # Linkowanie programu
        shader_program = compileProgram(vertex_shader, fragment_shader)

        # Czyszczenie pamięci (shadery są już w programie)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program

    def use(self):
        """Aktywuje program shadera."""
        glUseProgram(self.ID)

    # --- Metody ustawiające Uniformy ---
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
