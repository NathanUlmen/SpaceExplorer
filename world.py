import sys

from pygame.math import Vector2, Vector3

from data_structures import KdTree, AABB, StagedCollection


class Planet:
    def __init__(self, color: Vector3, pos: Vector2 = Vector2(0, 0), radius: float = 10):
        self.color = color
        self.pos = pos
        self.radius = radius
        self.explored = False


class Drone:
    def __init__(self):
        self.speed = 100
        self.pos = Vector2()
        self.target_pos = Vector2()
        self.target_planet = None
        self.color = Vector3(200, 155, 200)

    def replicate(self):
        d = Drone()
        d.pos = self.pos.copy()
        d.target_pos = self.target_pos.copy()
        d.color = self.color.copy()
        d.target_planet = None
        return d

    def set_course(self, planet : Planet) -> None:
        self.target_planet = planet
        self.target_pos = planet.pos


class World:
    def __init__(self):
        self.available_planets = []
        self.planets = []
        self.drones = StagedCollection()

    def add_drone(self, drone: Drone):
        self.drones.stage_append(drone)

    def add_planet(self, planet: Planet):
        self.planets.append(planet)
        self.available_planets.append(planet)

    def nearest_planet(self, position: Vector2) -> Planet | None:
        if len(self.available_planets) == 0:
            return None
        smallest_dist = sys.maxsize
        target = None
        for planet in self.available_planets:
            distance = (position - planet.pos).length()
            if smallest_dist > distance:
                smallest_dist = distance
                target = planet
        self.available_planets.remove(target)
        return target
