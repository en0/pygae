from collections import deque
from random import randint
from typing import NamedTuple, final, override
from pygae import GameEngine, GameObject, IGameObject
from pygame import K_DOWN, K_LEFT, K_RETURN, K_RIGHT, K_UP, Rect, Surface, Vector2, draw
from pygame.font import SysFont


@final
class Config(NamedTuple):
    update_hz: float = 10
    max_framerate: int = 144
    boundary: Rect = Rect(0, 0, 1280, 1024)


@final
class PlayScene(GameObject):

    SNAKE_COLOR = "#234111"
    FRUIT_COLOR = "#431111"

    def __init__(self) -> None:
        super().__init__()
        self.tile_x: int
        self.tile_y: int
        self.facing: int
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
        self.fruit = set()
        self.prev_snake = []
        self.snake = deque(maxlen=5)
        self.snake.append(self.world_boundary.center)
        self.facing = 0

    def _world2screen(self, x: int = 0, y: int = 0) -> tuple[float, float]:
        # Convert from the world tile to the screen pixel
        return x*self.tile_x, y*self.tile_y

    def _spawn_fruit(self, attempt: int = 0):
        # We attempt to spawn fruit 10 times.
        # and we only allow 3 total fruites at any moment
        if attempt > 10 or len(self.fruit) > 2: return

        # Pick a random fruit location
        x = randint(0, self.world_boundary.width - 1)
        y = randint(0, self.world_boundary.height - 1)

        # Make sure it's a vaid spot.
        # If not, make another attempt
        if (x, y) in self.snake or (x, y) in self.fruit:
            self._spawn_fruit(attempt+1)
        else:
            self.fruit.add((x, y))

    def game_over(self):
        self.set_scene(TitleScene())

    @override
    def _post_fixed_update(self, delta: float) -> None:

        # Store previous location for render interpolation
        self.prev_snake = [self._world2screen(x=x, y=y) for x,y in self.snake]

        # Attempt to spawn new fruit
        self.fruit_spawn_cooldown = (self.fruit_spawn_cooldown + 1) % 20
        if self.fruit_spawn_cooldown == 0:
            self._spawn_fruit()

        # Find the next snake position considering inputs
        x, y = self.snake[0]
        if self.facing in (0, 2) and self.input_pressed("UP"): self.facing = 1
        elif self.facing in (0, 2) and self.input_pressed("DOWN"): self.facing = 3
        elif self.facing in (1, 3) and self.input_pressed("LEFT"): self.facing = 0
        elif self.facing in (1, 3) and self.input_pressed("RIGHT"): self.facing = 2
        if self.facing == 0: x -= 1
        elif self.facing == 1: y -= 1
        elif self.facing == 2: x += 1
        elif self.facing == 3: y += 1

        # Check for food collisions
        # If so, grow the ring-buffer by 1 item to allow for new snake segment
        # And remove the fruit from the list of fruits
        if (x, y) in self.fruit:
            self.snake = deque(self.snake.copy(), maxlen=(self.snake.maxlen or 1) + 1)
            self.fruit.remove((x, y))

        # Check for self-collsion
        if (x, y) in self.snake:
            self.game_over()

        # Set the next snake position
        self.snake.appendleft((x, y))

        # Check for boundary collisions
        if x < 0: self.game_over()
        if x >= self.world_boundary.width: self.game_over()
        if y < 0: self.game_over()
        if y >= self.world_boundary.height: self.game_over()

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
        self.play_scene: IGameObject = PlayScene()
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
            self.set_scene(self.play_scene)

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
        self.bind_keyboard_button("UP", K_UP)
        self.bind_keyboard_button("DOWN", K_DOWN)
        self.bind_keyboard_button("LEFT", K_LEFT)
        self.bind_keyboard_button("RIGHT", K_RIGHT)
        self.bind_keyboard_button("PLAY", K_RETURN)


if __name__ == "__main__":
    # Load game, inject config service
    SnakeGame(services={
        Config: Config
    }).run()
