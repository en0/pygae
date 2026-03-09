from pygame import K_SPACE, Rect, Surface, Vector2, draw, mouse
from typing import final, override

import pygame
from pygame.event import set_grab
from pygae.engine import GameEngine
from pygae.game_object import GameObject
from pygae.typing import IInputService
from random import random, seed

from pygae.value_object import InputBinding
from pygae.value_object.input_binding import AXIS_MOUSE_X, AXIS_MOUSE_Y, DEVICE_MOUSE, TYPE_AXIS


SCREEN_SIZE = (1280, 1024)
WIND_X = 50
WIND_Y = 0.0
DRAG_XY = 0.99
GRAVITY = Vector2(0, 800)
DAMPING = 0.99


@final
class Circle(GameObject):

    def __init__(self, box: "Box", position: Vector2, velocity: Vector2 | None = None) -> None:
        super().__init__()
        self.position = position
        self.velocity = velocity or Vector2(0, 0)
        self._prev_position = position.copy()
        self.size = Vector2(50, 50)
        self.box: "Box" = box

    @override
    def _pre_fixed_update(self, delta: float) -> None:

        box_half_x = self.box.size.x // 2
        box_half_y = self.box.size.y // 2
        min_x = self.box.position.x - box_half_x
        max_x = self.box.position.x + box_half_x - self.size.x
        min_y = self.box.position.y - box_half_y
        max_y = self.box.position.y + box_half_y - self.size.y

        self._prev_position = self.position.copy()
        self.velocity.x *= 1.0 - DRAG_XY * delta
        self.velocity.y *= 1.0 - DRAG_XY * delta
        self.velocity.x += WIND_X * delta
        self.velocity.y += WIND_Y * delta
        self.velocity += GRAVITY * delta
        self.position += self.velocity * delta

        if self.position.x < min_x:
            self.position.x = min_x
            self.velocity.x = -self.velocity.x * DAMPING + self.box.velocity.x

        elif self.position.x > max_x:
            self.position.x = max_x
            self.velocity.x = -self.velocity.x * DAMPING + self.box.velocity.x

        if self.position.y < min_y:
            self.position.y = min_y
            self.velocity.y = -self.velocity.y * DAMPING + self.box.velocity.y

        elif self.position.y > max_y:
            self.position.y = max_y
            self.velocity.y = -self.velocity.y * DAMPING + self.box.velocity.y

    @override
    def _post_render(self, surface: Surface, alpha: float):
        render_pos = self._prev_position.lerp(self.position, alpha)
        center = (render_pos + self.size / 2)
        _ = draw.circle(surface, "#8a322a", (int(center.x), int(center.y)), int(self.size.x / 2))
        _ = draw.circle(surface, "#362511", (int(center.x), int(center.y)), int(self.size.x / 2), width=2)


@final
class Box(GameObject):

    def __init__(self) -> None:
        super().__init__()
        self.sensitivity = 1.0
        self.position = Vector2(0, 0)
        self.size = Vector2(350, 350)
        self._prev_position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self._input: IInputService

    @override
    def on_load(self) -> None:
        self._input = self.get_service(IInputService)

    @override
    def _pre_fixed_update(self, delta: float) -> None:
        self._prev_position = self.position.copy()

        if look := self._input.get_vector("LOOK_X", "LOOK_Y"):
            self.position = look

        self.velocity = (self.position - self._prev_position) / delta
        if self._input.pressed("SPAWN"):
            self.spawn_child(Circle(self, self.position.copy(), self.velocity.copy()))
            if len(list(self.get_children(True))) > 10:
                next(self.get_children(), None).kill()

    @override
    def _post_render(self, surface: Surface, alpha: float):
        render_pos = self._prev_position.lerp(self.position, alpha)
        rect = Rect(0, 0, self.size.x, self.size.y)
        rect.center = int(render_pos.x), int(render_pos.y)
        _ = draw.rect(surface, "#3333aa", rect, width=3, border_radius=10)


@final
class WindParticle(GameObject):
    def __init__(self, position: Vector2, velocity: Vector2, lifetime: float = 1.0, color: str = "white", size: float = 2):
        super().__init__()
        self.position = position.copy()
        self._prev_position = position.copy()
        self.velocity = velocity.copy()
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.size = size

    @override
    def _pre_fixed_update(self, delta: float):
        self._prev_position = self.position.copy()
        self.position += self.velocity * delta
        self.age += delta
        if self.age >= self.lifetime:
            self.kill()  # remove particle when lifetime expires

    @override
    def _post_render(self, surface: Surface, alpha: float):
        render_pos = self._prev_position.lerp(self.position, alpha)
        _ = draw.circle(surface, self.color, (int(render_pos.x), int(render_pos.y)), self.size)


@final
class WindEmitter(GameObject):
    def __init__(self, area: Rect, wind: Vector2, rate: int = 5):
        super().__init__()
        self.area = area          # Rect(x, y, w, h)
        self.wind = wind          # Vector2(x, y)

    @override
    def _pre_fixed_update(self, delta: float):
        if random() < 0.1:
            # Random position inside area
            x = self.area.x + random() * self.area.width
            y = self.area.y + random() * self.area.height
            pos = Vector2(x, y)

            # Random velocity around wind vector
            vel = Vector2(self.wind.x + (random()-0.5)*50,
                          self.wind.y + (random()-0.5)*50)

            particle = WindParticle(pos, vel, lifetime=0.8 + random()*0.5, color="#333333", size=2)
            self.spawn_child(particle)


@final
class TitleScene(GameObject):

    @override
    def on_load(self) -> None:
        wind_emitter = WindEmitter(Rect(0, 0, *SCREEN_SIZE), Vector2(WIND_X, WIND_Y))
        box = Box()
        box.position = Vector2(200, 200)
        self.spawn_child(wind_emitter)
        self.spawn_child(box)

    @override
    def _pre_render(self, surface: Surface, alpha: float):
        _ = surface.fill("black")


@final
class MyGame(GameEngine):

    SCREEN_SIZE = SCREEN_SIZE

    @override
    def _get_root_surface(self) -> pygame.Surface:
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        try:
            #flags |= pygame.SCALED | pygame.FULLSCREEN
            surface = pygame.display.set_mode(self.SCREEN_SIZE, flags)
        except Exception:
            surface = pygame.display.set_mode(self.SCREEN_SIZE, flags)

        pygame.display.set_caption("suff and things")
        return surface

    @override
    def _on_load(self) -> None:
        _ = mouse.set_visible(True)
        set_grab(True)

        input_service: IInputService = self.get_service(IInputService)

        input_service.set_map({
            "SPAWN": InputBinding("button", "keyboard", K_SPACE),
            "LOOK_X": InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MOUSE_X),
            "LOOK_Y": InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MOUSE_Y),
        })

        self.set_scene(TitleScene())


if __name__ == "__main__":
    seed(100)
    game = MyGame()
    game.run()
