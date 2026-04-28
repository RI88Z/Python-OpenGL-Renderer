import ctypes

import numpy as np
from OpenGL.GL import *


class Mesh:
    def __init__(self, vertices: np.ndarray, indices: np.ndarray, textures: list):
        self.vertices = vertices
        self.indices = indices
        self.textures = textures  # Lista słowników: [{'id': int, 'type': str}]

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        self._setup_mesh()

    def _setup_mesh(self):
        glBindVertexArray(self.VAO)

        # Ładowanie wierzchołków
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(
            GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW
        )

        # Ładowanie indeksów (EBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW
        )

        stride = 8 * self.vertices.itemsize

        # 1. Pozycje wierzchołków
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

        # 2. Wektory normalne
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(3 * self.vertices.itemsize),
        )

        # 3. Współrzędne tekstur
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(
            2,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(6 * self.vertices.itemsize),
        )

        glBindVertexArray(0)

    def draw(self, shader):
        # Bindowanie odpowiednich tekstur do jednostek
        diffuse_nr = 1
        specular_nr = 1

        for i, texture in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)  # Aktywacja odpowiedniego Texture Unit
            name = texture["type"]
            number = ""

            if name == "texture_diffuse":
                number = str(diffuse_nr)
                diffuse_nr += 1
            elif name == "texture_specular":
                number = str(specular_nr)
                specular_nr += 1

            # Przekazanie do shadera
            shader.set_int(f"material.{name}{number}", i)
            glBindTexture(GL_TEXTURE_2D, texture["id"])

        # Rysowanie siatki
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Zresetowanie aktywnej tekstury do domyślnej
        glActiveTexture(GL_TEXTURE0)
