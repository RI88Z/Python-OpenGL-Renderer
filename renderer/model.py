import numpy as np
from OpenGL.GL import *
from PIL import Image

from .mesh import Mesh


class Model:
    def __init__(self, obj_path, diffuse_path=None, specular_path=None):
        self.meshes = []
        self._load_model(obj_path, diffuse_path, specular_path)

    def _load_model(self, path, diffuse_path, specular_path):
        temp_vertices = []
        temp_uvs = []
        temp_normals = []

        vertex_data = []
        indices = []

        unique_vertices = {}

        print(f"Loading model: {path}...")
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue

                if parts[0] == "v":
                    temp_vertices.append([float(x) for x in parts[1:4]])
                elif parts[0] == "vt":
                    temp_uvs.append([float(x) for x in parts[1:3]])
                elif parts[0] == "vn":
                    temp_normals.append([float(x) for x in parts[1:4]])
                elif parts[0] == "f":
                    face_vertices = parts[1:]
                    for i in range(1, len(face_vertices) - 1):
                        triangle = [
                            face_vertices[0],
                            face_vertices[i],
                            face_vertices[i + 1],
                        ]

                        for vertex_str in triangle:
                            if vertex_str not in unique_vertices:
                                v_idx, vt_idx, vn_idx = [
                                    int(x) - 1 if x else -1
                                    for x in (vertex_str + "//").split("/")[:3]
                                ]

                                pos = (
                                    temp_vertices[v_idx]
                                    if v_idx != -1
                                    else [0.0, 0.0, 0.0]
                                )
                                uv = temp_uvs[vt_idx] if vt_idx != -1 else [0.0, 0.0]
                                norm = (
                                    temp_normals[vn_idx]
                                    if vn_idx != -1
                                    else [0.0, 0.0, 0.0]
                                )

                                unique_vertices[vertex_str] = len(unique_vertices)
                                vertex_data.extend(pos + norm + uv)

                            indices.append(unique_vertices[vertex_str])

        np_vertices = np.array(vertex_data, dtype=np.float32)
        np_indices = np.array(indices, dtype=np.uint32)

        textures = []
        if diffuse_path:
            diff_id = self._load_texture(diffuse_path)
            textures.append({"id": diff_id, "type": "texture_diffuse"})
        if specular_path:
            spec_id = self._load_texture(specular_path)
            textures.append({"id": spec_id, "type": "texture_specular"})

        self.meshes.append(Mesh(np_vertices, np_indices, textures))
        print("Model loaded successfully.")

    def _load_texture(self, path):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            img = Image.open(path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = img.convert("RGBA").tobytes()

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                img.width,
                img.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                img_data,
            )
            glGenerateMipmap(GL_TEXTURE_2D)
            print(f"Loaded texture: {path}")
        except Exception as e:
            print(f"Failed to load texture {path}: {e}")

        return texture_id

    def draw(self, shader):
        for mesh in self.meshes:
            mesh.draw(shader)
