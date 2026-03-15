import math
import random
import sys

import pygame
from pygame.math import Vector2, Vector3

from camera import Camera
from world import World, Planet, Drone

screen_dims = Vector2(1600, 800)

world_dims = Vector2(screen_dims * 10)
world_center = world_dims / 2

camera = Camera(screen_dims.x, screen_dims.y)
camera.position = world_center
world = World()


def main() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(screen_dims)
    pygame.display.set_caption("Space Explorer")

    spawn_planets(10_000)

    # Create first drone
    d = Drone()
    d.pos = world_center
    target = world.pop_nearest_planet(d.pos)
    d.set_course(target)
    world.add_drone(d)

    is_panning = False
    last_mouse = Vector2(0, 0)
    zoom_min = 0.2
    zoom_max = 5.0

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2 or event.button == 3:
                    is_panning = True
                    last_mouse = Vector2(event.pos)
                if event.button == 4:
                    zoom_at(Vector2(event.pos), 1.1, zoom_min, zoom_max)
                if event.button == 5:
                    zoom_at(Vector2(event.pos), 1 / 1.1, zoom_min, zoom_max)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2 or event.button == 3:
                    is_panning = False
            if event.type == pygame.MOUSEMOTION and is_panning:
                mouse = Vector2(event.pos)
                delta = mouse - last_mouse
                camera.position -= delta / camera.zoom
                last_mouse = mouse
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    zoom_at(camera.center, 1.1, zoom_min, zoom_max)
                if event.key == pygame.K_MINUS:
                    zoom_at(camera.center, 1 / 1.1, zoom_min, zoom_max)
        delta = clock.tick(60) / 1000
        screen.fill((0, 0, 0))
        tick(delta, world)
        draw(screen, world)
        pygame.display.flip()


def spawn_planets(count: int) -> None:
    for i in range(count):
        color = Vector3(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pos = Vector2(random.uniform(0, world_dims.x), random.uniform(0, world_dims.y))
        planet = Planet(color, pos)
        world.add_planet(planet)


def tick(delta: float, world: World) -> None:
    for drone in world.drones:
        if not drone.target_pos or not drone.target_planet:
            continue
        drone.pos = drone.pos.move_towards(drone.target_pos, drone.speed * delta)
        if drone.pos == drone.target_pos and len(world.available_planets) > 0:
            drone.target_planet.explored = True
            # Replicate and find next planet
            replicant = drone.replicate()
            world.add_drone(replicant)
            find_next_planet(drone, world)
            find_next_planet(replicant, world)
    world.drones.flush()


def find_next_planet(drone: Drone, world: World):
    target = world.pop_nearest_planet(drone.pos)
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


ship_shape = [Vector2(0, -5), Vector2(-2, 2), Vector2(0, 1), Vector2(2, 2)]


def draw_ship(screen, drone: Drone) -> None:
    scale = 5 * camera.zoom
    direction = drone.target_pos - drone.pos

    # Angle from direction to up vector as our shape faces up by default
    angle = direction.angle_to(Vector2(0, -1))
    # at destination set to look north/up
    if not direction.length() > 0:
        angle = 90 * math.pi // 180

    transformed = []
    for vert in ship_shape:
        v = vert.rotate(-angle)
        v *= scale
        v += drone.pos
        transformed.append(camera.world_to_screen(v))

    # draw the transformed ship shape
    pygame.draw.polygon(screen, drone.color, transformed, max(1, int(scale // 2)))

    # Draw line to destination
    pygame.draw.line(screen, drone.color, camera.world_to_screen(drone.pos), camera.world_to_screen(drone.target_pos),
                     2)


def draw_planet(screen, planet: Planet) -> None:
    pos = camera.world_to_screen(planet.pos)
    radius = max(1, int(planet.radius * camera.zoom))
    pygame.draw.circle(screen, planet.color, pos, radius)


def zoom_at(screen_pos: Vector2, factor: float, zoom_min: float, zoom_max: float) -> None:
    before = camera.screen_to_world(screen_pos)
    camera.zoom = max(zoom_min, min(zoom_max, camera.zoom * factor))
    after = camera.screen_to_world(screen_pos)
    camera.position += before - after


if __name__ == '__main__':
    main()
