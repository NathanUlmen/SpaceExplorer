package main

import "core:fmt"
import "core:math/rand"
import rl "vendor:raylib"


Vec2 :: [2]f32

Game :: struct {
    ships : [dynamic]Ship,
    stars: [dynamic]Star
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

TOTAL_STARS :: 100;

WORLD_DIMS :: Vec2{1000, 1000}

SCREEN_DIMS :: Vec2{1920, 1080}

main :: proc() {
    rl.InitWindow(i32(SCREEN_DIMS.x), i32(SCREEN_DIMS.y), "Space Probes")

    game := Game{}
    init_game(&game)

    add_ship(&game, {100, 100}, rl.Color{255, 0, 0, 255})

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

        update(game)

        draw(game)
    }

    rl.CloseWindow()
}

update :: proc(game: ^Game) {

}

draw :: proc(game: ^Game) {
    rl.BeginDrawing()
    rl.ClearBackground(rl.BLACK)

    for ship in game.ships {
        rl.DrawCircle(i32(ship.pos.x), i32(ship.pos.y), 10, ship.color)
    }

    for star in game.stars {
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
    append(&game.stars, Star{
        pos = pos,
        color = color,
        radius = radius
    }) 
}
