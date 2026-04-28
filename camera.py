import glm


class Camera:
    def __init__(
        self,
        position=glm.vec3(0.0, 0.0, 3.0),
        up=glm.vec3(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
    ):
        # Atrybuty kamery
        self.position = position
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.world_up = up

        # Kąty Eulera
        self.yaw = yaw
        self.pitch = pitch

        # Opcje kamery
        self.movement_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.fov = 45.0

        self.update_camera_vectors()

    def get_view_matrix(self):
        """Zwraca macierz widoku (View Matrix) za pomocą funkcji LookAt."""
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_projection_matrix(self, width, height):
        """Zwraca macierz rzutowania perspektywicznego."""
        return glm.perspective(glm.radians(self.fov), width / height, 0.1, 100.0)

    def process_keyboard(self, direction, delta_time):
        """Przesuwa kamerę na podstawie danych z klawiatury."""
        velocity = self.movement_speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        """Obraca kamerę na podstawie ruchu myszy."""
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        # Zabezpieczenie przed zjawiskiem Gimbal Lock i wykręceniem karku
        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def update_camera_vectors(self):
        """Przelicza nowe wektory kierunkowe Front, Right i Up."""
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

        # Przeliczenie Right i Up poprzez iloczyn wektorowy (Cross Product)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))
