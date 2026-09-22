package main

import "core:fmt"
import "core:log"
import "core:math/linalg"
import "core:math/rand"
import rl "vendor:raylib"


Vec2 :: [2]f32

Line :: struct {
	start: Vec2,
	end:   Vec2,
}

Game :: struct {
	camera:        rl.Camera2D,
	ships:         [dynamic]Ship,
	virgin_stars:  [dynamic]Star,
	visited_stars: [dynamic]Star,
	lines:         [dynamic]^Line,
}

Ship :: struct {
	color:       rl.Color,
	pos:         Vec2,
	dir:         f32, //direction in degrees
	target_pos:  Vec2,
	line:        ^Line,
	target_star: ^Star,
}

Star :: struct {
	color:   rl.Color,
	pos:     Vec2,
	radius:  f32,
	visited: bool,
}

TOTAL_STARS :: 10_000

SCREEN_DIMS :: Vec2{1920, 1080}

WORLD_DIMS :: Vec2{10_000, 10_000}

MOVE_SPEED :: 100

CAMERA_SPEED :: 400

main :: proc() {
	rl.InitWindow(i32(SCREEN_DIMS.x), i32(SCREEN_DIMS.y), "Space Probes")

	context.logger = log.create_console_logger()
	game := Game{}
	defer {
		delete(game.virgin_stars)
		delete(game.ships)
		delete(game.visited_stars)
		delete(game.lines)
	}
	init_game(&game)


	loop(&game)
}

init_game :: proc(game: ^Game) {
	create_stars(game)
	add_ship(game, {WORLD_DIMS.x / 2, WORLD_DIMS.y / 2}, rl.RED)
	ship := game.ships[0]
	ship.line = new(Line)
	append(&game.lines, ship.line)
	log.info("Init Successful")
}

create_stars :: proc(game: ^Game) {
	for i in 0 ..< TOTAL_STARS {
		x := rand.float32_range(0, WORLD_DIMS.x)
		y := rand.float32_range(0, WORLD_DIMS.y)
		radius := rand.float32_range(10, 40)
		color := rl.Color {
			u8(rand.uint32_range(100, 255)),
			u8(rand.uint32_range(100, 255)),
			u8(rand.uint32_range(100, 255)),
			255,
		}
		add_star(game, {x, y}, color, radius)
	}
}

loop :: proc(game: ^Game) {
	frame_counter: u64 = 0
	total_time: f32 = 0
	defer {
		log.info("frame_counter={", frame_counter, "}total_time={", total_time * 1000, "ms}")
		byte_size := size_of(game.virgin_stars)
	}
	for !rl.WindowShouldClose() {

		update(game, rl.GetFrameTime())

		draw(game)
		total_time += rl.GetFrameTime()
		frame_counter += 1

	}

	rl.CloseWindow()
}

update :: proc(game: ^Game, deltaT: f32) {
	handle_input(game, deltaT)
	for &ship in game.ships {
		if ship.target_star == nil {
			find_nearest_star(game, &ship)
			new_line := new(Line)
			append(&game.lines, new_line)
			ship.line = new_line
			log.info("Here!")
			ship.line.start = ship.pos
		}

		travel(game, deltaT, &ship)
		distance := abs(linalg.length(ship.target_pos - ship.pos))

		if distance <= 1 {
			replicate_ship(game, ship)
			ship.target_star = nil
			ship.line = nil
		}

	}

	replicate_ship :: proc(game: ^Game, ship: Ship) {
		new_ship: Ship = {
			color = ship.color,
			pos   = ship.pos,
			dir   = ship.dir,
		}
		append(&game.ships, new_ship)
	}
}

ZOOM_SPEED :: 1

handle_input :: proc(game: ^Game, deltaT: f32) {
	if rl.IsKeyDown(.W) do game.camera.offset.y += CAMERA_SPEED * deltaT
	if rl.IsKeyDown(.S) do game.camera.offset.y -= CAMERA_SPEED * deltaT
	if rl.IsKeyDown(.D) do game.camera.offset.x -= CAMERA_SPEED * deltaT
	if rl.IsKeyDown(.A) do game.camera.offset.x += CAMERA_SPEED * deltaT
	if rl.IsKeyDown(.E) do game.camera.zoom += ZOOM_SPEED * deltaT
	if rl.IsKeyDown(.Q) do game.camera.zoom -= ZOOM_SPEED * deltaT
}


find_nearest_star :: proc(game: ^Game, ship: ^Ship) {
	nearest_star: ^Star
	nearest: f32 = 0xFFFFFFFF
	nearest_index := 0
	for &star, index in game.virgin_stars {
		dist := linalg.length(star.pos - ship.pos)
		if dist < nearest {
			nearest_star = &star
			nearest = dist
			nearest_index = index
		}
	}
	ship.target_star = nearest_star
	ship.target_pos = nearest_star.pos
	append(&game.visited_stars, ship.target_star^)
	unordered_remove(&game.virgin_stars, nearest_index)
}

travel :: proc(game: ^Game, deltaT: f32, ship: ^Ship) {
	pos_delta := linalg.normalize(ship.target_pos - ship.pos)
	ship.pos += pos_delta * MOVE_SPEED * deltaT
	ship.line.end = ship.pos
}

draw :: proc(game: ^Game) {
	rl.BeginMode2D(game.camera)
	defer rl.EndDrawing()

	rl.ClearBackground(rl.BLACK)

	for star in game.virgin_stars {
		rl.DrawCircle(i32(star.pos.x), i32(star.pos.y), star.radius, star.color)
	}

	for star in game.visited_stars {
		rl.DrawCircle(i32(star.pos.x), i32(star.pos.y), star.radius, star.color)
	}

	for ship in game.ships {
		rl.DrawCircle(i32(ship.pos.x), i32(ship.pos.y), 10, ship.color)
	}

	for line in game.lines {
		rl.DrawLine(
			i32(line.start.x),
			i32(line.start.y),
			i32(line.end.x),
			i32(line.end.y),
			rl.RAYWHITE,
		)
	}

}

add_ship :: proc(game: ^Game, pos: Vec2, color: rl.Color) {
	append(&game.ships, Ship{color = color, pos = pos, dir = 90, target_pos = {0, 0}})
}

add_star :: proc(game: ^Game, pos: Vec2, color: rl.Color, radius: f32) {
	append(&game.virgin_stars, Star{pos = pos, color = color, radius = radius})
}
