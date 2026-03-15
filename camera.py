from pygame import Vector2


class Camera:
    def __init__(self, width, height):
        self.position = Vector2(0, 0)
        self.zoom = 1.0
        self.center = Vector2(width / 2, height / 2)

    def world_to_screen(self, pos: Vector2) -> Vector2:
        return (pos - self.position) * self.zoom + self.center

    def screen_to_world(self, pos: Vector2) -> Vector2:
        return (pos - self.center) / self.zoom + self.position
