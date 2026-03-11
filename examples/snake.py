from collections import deque
from random import randint
from typing import NamedTuple, final, override
from pygae import GameEngine, GameObject, IGameObject, IInputService
from pygame import K_DOWN, K_LEFT, K_RETURN, K_RIGHT, K_UP, K_a, K_d, K_s, K_w, Rect, Surface, Vector2, draw
from pygame.font import SysFont

from pygae.value_object import InputBinding
from pygae.value_object.input_binding import DEVICE_KEYBOARD, TYPE_BUTTON


T_FACING = int
LEFT: T_FACING = 0
UP: T_FACING = 1
RIGHT: T_FACING = 2
DOWN: T_FACING = 3


@final
class Config(NamedTuple):
    update_hz: float = 10
    max_framerate: int = 144
    boundary: Rect = Rect(0, 0, 1280, 1024)


@final
class PlayScene(GameObject):

    SNAKE_COLOR = "#234111"
    FRUIT_COLOR = "#431111"
    FRUTE_SPAWN_TICK = 20

    def __init__(self) -> None:
        super().__init__()
        self.tile_x: int
        self.tile_y: int
        self.facing: T_FACING
        self.world_boundary = Rect(0, 0, 50, 35)
        self.prev_snake: list[tuple[float, float]]
        self.snake: deque[tuple[int, int]]
        self.fruit: set[tuple[int, int]]
        self.fruit_spawn_cooldown = -1

    @override
    def on_load(self) -> None:
        # load the game details and compute the world boundary
        config = self.get_service(Config)
        boundary = config.boundary.copy()
        self.tile_x = boundary.width // self.world_boundary.width
        self.tile_y = boundary.height // self.world_boundary.height

        # Reset the game
        cx, cy = self.world_boundary.center
        self.fruit = set()
        self.prev_snake = []
        self.snake = deque(maxlen=5)
        self.snake.append((cx, cy))
        self.facing = 0

    def _world2screen(self, x: int = 0, y: int = 0) -> tuple[float, float]:
        # Convert from the world tile to the screen pixel
        return x*self.tile_x, y*self.tile_y

    def _spawn_fruit(self):
        # We attempt to spawn fruit 10 times.
        # and we only allow 3 total fruits at any moment
        if len(self.fruit) > 2: return
        for _ in range(10):

            # Pick a random spawn location
            pos = (
                randint(0, self.world_boundary.width - 1),
                randint(0, self.world_boundary.height - 1)
            )

            # Make sure it's a valid spot.
            if pos not in set(self.snake) and pos not in self.fruit:
                self.fruit.add(pos)
                break

    def game_over(self):
        self.set_scene(TitleScene())

    @override
    def _post_fixed_update(self, delta: float) -> None:

        # Store previous location for render interpolation
        self.prev_snake = [self._world2screen(x=x, y=y) for x,y in self.snake]

        # Attempt to spawn new fruit
        self.fruit_spawn_cooldown = (self.fruit_spawn_cooldown + 1) % self.FRUTE_SPAWN_TICK
        if self.fruit_spawn_cooldown == 0:
            self._spawn_fruit()

        # Find the next snake position considering inputs
        x, y = self.snake[0]
        if self.facing in (LEFT, RIGHT) and self.input_pressed("UP"):
            self.facing = UP
        elif self.facing in (LEFT, RIGHT) and self.input_pressed("DOWN"):
            self.facing = DOWN
        elif self.facing in (UP, DOWN) and self.input_pressed("LEFT"):
            self.facing = LEFT
        elif self.facing in (UP, DOWN) and self.input_pressed("RIGHT"):
            self.facing = RIGHT

        # Move head of snake forward
        if self.facing == LEFT: x -= 1
        elif self.facing == UP: y -= 1
        elif self.facing == RIGHT: x += 1
        elif self.facing == DOWN: y += 1

        # Check for food collisions
        if (x, y) in self.fruit:
            self.snake = deque(self.snake, maxlen=(self.snake.maxlen or 1) + 1)
            self.fruit.remove((x, y))
        elif len(self.snake) == self.snake.maxlen:
            # Pop off the tail to fix the tail collsion check
            _ = self.snake.pop()

        # Check for self-collsion and out-of-bounds
        if (x, y) in self.snake:
            self.game_over()
        elif x < 0:
            self.game_over()
        elif x >= self.world_boundary.width:
            self.game_over()
        elif y < 0:
            self.game_over()
        elif y >= self.world_boundary.height:
            self.game_over()

        # Set the next snake position
        else:
            self.snake.appendleft((x, y))

    @override
    def _post_render(self, surface: Surface, alpha: float) -> None:
        _ = surface.fill("black")

        # Draw Snake
        for (wx, wy), (lx, ly) in zip(self.snake, self.prev_snake):
            sx, sy = self._world2screen(wx, wy)
            lsx, lsy = Vector2(lx, ly).lerp((sx, sy), alpha)
            # Make each tile just slightly bigger to avoid lines
            render_pos = (lsx-1, lsy-1, self.tile_x+2, self.tile_y+2)
            _ = draw.rect(surface, self.SNAKE_COLOR, render_pos)

        # Draw Fruit
        for wx, wy in self.fruit:
            sx, sy = self._world2screen(wx, wy)
            # Make fruit just slightly smaller so it looks like it fits in the snake
            render_pos = (sx+2, sy+2, self.tile_x-4, self.tile_y-4)
            _ = draw.rect(surface, self.FRUIT_COLOR, render_pos)


@final
class TitleScene(GameObject):

    TITLE: str = "Snake"
    TITLE_COLOR: str = "#432322"
    PROMPT_COLOR: str = "#232243"

    def __init__(self) -> None:
        super().__init__()
        self.title_sprite: Surface
        self.title_sprite_position: tuple[float, float]
        self.prompt_sprite: Surface
        self.prompt_sprite_position: tuple[float, float]
        self.blink: int = 0

    @override
    def on_load(self) -> None:
        boundary = self.get_service(Config).boundary

        # Render title text text
        title_font = SysFont("arial", 100)
        self.title_sprite = title_font.render(self.TITLE, True, self.TITLE_COLOR)
        sprite_rect = self.title_sprite.get_bounding_rect()
        sprite_rect.center = boundary.center
        sprite_rect.top -= 50
        self.title_sprite_position = sprite_rect.topleft

        # Render title prompt
        prompt_font = SysFont("arial", 35)
        self.prompt_sprite = prompt_font.render("[Press Enter]", True, self.PROMPT_COLOR)
        prompt_rect = self.prompt_sprite.get_bounding_rect()
        prompt_rect.center = sprite_rect.center
        prompt_rect.top += 20 + (boundary.bottom - sprite_rect.bottom) // 2
        self.prompt_sprite_position = prompt_rect.topleft

    @override
    def _post_fixed_update(self, delta: float) -> None:
        if self.input_pressed("PLAY"):
            self.set_scene(PlayScene())

    @override
    def _post_render(self, surface: Surface, alpha: float) -> None:
        _ = surface.fill("black")
        _ = surface.blit(self.title_sprite, self.title_sprite_position)
        self.blink += 1
        if self.blink < 100:
            _ = surface.blit(self.prompt_sprite, self.prompt_sprite_position)
        self.blink %= 200


@final
class SnakeGame(GameEngine):

    @override
    def _on_load(self) -> None:

        # Load config and set the scene.
        config = self.get_service(Config)
        self.SCREEN_SIZE = config.boundary.bottomright
        self.FIXED_DT = 1/config.update_hz
        self.MAX_FRAMERATE = config.max_framerate
        self.set_scene(TitleScene())

        # Bind all the keys
        self.get_service(IInputService).set_map({
            "PLAY": InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_RETURN),
            "UP": [
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_w),
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_UP),
            ],
            "DOWN": [
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_s),
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_DOWN),
            ],
            "LEFT": [
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_a),
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_LEFT),
            ],
            "RIGHT": [
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_d),
                InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=K_RIGHT),
            ],
        })


if __name__ == "__main__":
    # Load game, inject config service
    SnakeGame(services={
        Config: Config
    }).run()
