package main

import "core:fmt"
import "core:math/rand"
import "core:math/linalg"
import rl "vendor:raylib"


Vec2 :: [2]f32

Game :: struct {
    ships : [dynamic]Ship,
    virgin_stars: [dynamic]Star,
    visited: [dynamic]Star
}

Ship :: struct {
    color : rl.Color,
    pos : Vec2,
    dir : f32, //direction in degrees
    target_pos : Vec2,
    target_star : ^Star
}

Star :: struct {
    color : rl.Color,
    pos : Vec2,
    radius : f32,
    visited: bool
}

TOTAL_STARS :: 50_000;

SCREEN_DIMS :: Vec2{1920, 1080}

WORLD_DIMS :: Vec2{9000, 9000}



MOVE_SPEED :: 100

main :: proc() {
    rl.InitWindow(i32(SCREEN_DIMS.x), i32(SCREEN_DIMS.y), "Space Probes")

    game := Game{}
    init_game(&game)


    loop(&game)
}

init_game :: proc(game: ^Game) {
    create_stars(game)
    add_ship(game, {WORLD_DIMS.x / 2, WORLD_DIMS.y / 2}, rl.RED)
}

create_stars :: proc(game: ^Game) {
    for i in 0 ..< TOTAL_STARS {
        x := rand.float32_range(0, WORLD_DIMS.x)
        y := rand.float32_range(0, WORLD_DIMS.y)
        radius := rand.float32_range(10, 40)
        color := rl.Color{
            u8(rand.uint32_range(0, 255)), 
            u8(rand.uint32_range(0, 255)), 
            u8(rand.uint32_range(0, 255)), 
            255
        }
        add_star(game, {x, y}, color, radius)
    }
}

loop :: proc(game: ^Game) {
    for !rl.WindowShouldClose() {

        update(game, rl.GetFrameTime())
        fmt.println("FPS:", rl.GetFPS(), "frame time:", rl.GetFrameTime() * 1000, "ms")

        draw(game)

    }

    rl.CloseWindow()
}

update :: proc(game: ^Game, deltaT: f32) {
    for &ship in game.ships {
        if ship.target_star == nil {
            find_nearest_star(game, &ship)
        }
        travel(game, deltaT, &ship)
        distance := abs(linalg.length(ship.target_pos - ship.pos))
        if distance <= 1 {
            append(&game.visited, ship.target_star^)
            unordered_remove(&game.virgin_stars, star_index(game, ship.target_star))
            ship.target_star = nil
        }
    }
}

find_nearest_star :: proc(game: ^Game, ship: ^Ship) {
    nearest_star: ^Star
    nearest: f32 = 0xFFFFFFF
    for &star in game.virgin_stars {
        dist := linalg.length(star.pos - ship.pos)
        if dist < nearest {
            nearest_star = &star;
            nearest = dist
        }
    }
    ship.target_star = nearest_star
    ship.target_pos = nearest_star.pos
}

travel :: proc(game: ^Game, deltaT: f32, ship: ^Ship) {
    pos_delta := linalg.normalize(ship.target_pos - ship.pos)
    ship.pos += pos_delta * MOVE_SPEED * deltaT
}

draw :: proc(game: ^Game) {
    rl.BeginDrawing()
    rl.ClearBackground(rl.BLACK)

    for ship in game.ships {
        rl.DrawCircle(i32(ship.pos.x), i32(ship.pos.y), 10, ship.color)
    }

    for star in game.virgin_stars {
        rl.DrawCircle(i32(star.pos.x), i32(star.pos.y), star.radius, star.color)
    }

    rl.EndDrawing()
}

add_ship :: proc(game: ^Game, pos : Vec2, color : rl.Color) {
    append(&game.ships, Ship{
        color = color,
        pos = pos,
        dir = 90,
        target_pos = {0,0},
    })
}

add_star :: proc(game: ^Game, pos : Vec2, color : rl.Color, radius : f32) {
    append(&game.virgin_stars, Star{
        pos = pos,
        color = color,
        radius = radius
    }) 
}

star_index :: proc(game: ^Game, to_remove: ^Star) -> int {
    for &star, index in game.virgin_stars {
        if &star == to_remove {
            return index
        }
    }
    return -1;
}
