from pygame import Vector2


class Camera:
    def __init__(self, width, height):
        self.position = Vector2(0, 0)
        self.zoom = 1
        self.center = Vector2(width / 2, height / 2)