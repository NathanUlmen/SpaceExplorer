import math
import random
import sys

import pygame
from pygame.math import Vector2, Vector3

from camera import Camera
from world import World, Planet, Drone

dimensions = Vector2(1600, 800)

camera = Camera(dimensions.x, dimensions.y)
world = World()


def main() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(dimensions)
    pygame.display.set_caption("Space Explorer")

    spawn_planets(1000)

    # Create first drone
    d = Drone()
    target = world.nearest_planet(d.pos)
    d.set_course(target)
    world.add_drone(d)

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        delta = clock.tick(60) / 1000
        screen.fill((0, 0, 0))
        tick(delta, world)
        draw(screen, world)
        pygame.display.flip()


def spawn_planets(count: int) -> None:
    for i in range(count):
        color = Vector3(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pos = Vector2(random.uniform(0, dimensions.x), random.uniform(0, dimensions.y))
        planet = Planet(color, pos)
        world.add_planet(planet)


def tick(delta: float, world: World) -> None:
    for drone in world.drones:
        if not drone.target_pos or not drone.target_planet:
            continue
        drone.pos = drone.pos.move_towards(drone.target_pos, drone.speed * delta)
        if drone.pos == drone.target_pos:
            drone.target_planet.explored = True
            # Replicate and find next planet
            replicant = drone.replicate()
            world.add_drone(replicant)
            find_next_planet(drone, world)
            find_next_planet(replicant, world)
    world.drones.flush()


def find_next_planet(drone: Drone, world: World):
    target = world.nearest_planet(drone.pos)
    if not target:
        return
    drone.target_planet = target
    target.explored = True
    drone.target_pos = target.pos


def draw(screen, world) -> None:
    for drone in world.drones:
        draw_ship(screen, drone)
    for planet in world.planets:
        draw_planet(screen, planet)


def draw_ship(screen, ship: Drone) -> None:
    scale = 5
    shape = [Vector2(0, -5), Vector2(-2, 2), Vector2(0, 1), Vector2(2, 2)]

    direction = ship.target_pos - ship.pos

    # Angle from direction to up vector as our shape faces up by default
    angle = direction.angle_to(Vector2(0, -1))
    # at destination set to look north/up
    if not direction.length() > 0:
        angle = 90 * math.pi // 180

    transformed = []
    for vert in shape:
        v = vert.rotate(-angle)
        v *= scale
        v += ship.pos
        transformed.append(v)

    pygame.draw.polygon(screen, ship.color, transformed, scale // 2)


def draw_planet(screen, planet: Planet) -> None:
    pygame.draw.circle(screen, planet.color, planet.pos, planet.radius)


if __name__ == '__main__':
    main()
