import pygame
from pygame import K_SPACE, Rect, Surface, draw, mouse
from pygame.event import set_grab
from random import random, seed
from typing import final, override

from pygae import GameEngine, GameObject, IInputService
from pygae.math import Vec2
from pygae.value_object.input_binding import InputBinding, AXIS_MOUSE_X, AXIS_MOUSE_Y, DEVICE_MOUSE, TYPE_AXIS


SCREEN_SIZE = (1280, 1024)
WIND_X = 50
WIND_Y = 0.0
DRAG_XY = 0.99
GRAVITY = Vec2(0, 800)
DAMPING = 0.99


@final
class Circle(GameObject):

    def __init__(self, box: "Box", position: Vec2, velocity: Vec2 | None = None) -> None:
        super().__init__()
        self.position = position
        self.velocity = velocity or Vec2(0, 0)
        self._prev_position = position
        self.size = Vec2(50, 50)
        self.box: "Box" = box

    @override
    def _pre_fixed_update(self, delta: float) -> None:

        half_box = self.box.size // 2
        pos_min = self.box.position - half_box
        pos_max = self.box.position + half_box - self.size

        self._prev_position = self.position

        # Apply drag, wind, and gravity
        drag_factor = 1.0 - DRAG_XY * delta
        wind = Vec2(WIND_X, WIND_Y) * delta
        self.velocity = self.velocity * drag_factor + wind + GRAVITY * delta
        self.position += self.velocity * delta

        # Collision with box boundaries
        if self.position.x < pos_min.x:
            self.position = Vec2(pos_min.x, self.position.y)
            self.velocity = Vec2(-self.velocity.x * DAMPING + self.box.velocity.x, self.velocity.y)
        elif self.position.x > pos_max.x:
            self.position = Vec2(pos_max.x, self.position.y)
            self.velocity = Vec2(-self.velocity.x * DAMPING + self.box.velocity.x, self.velocity.y)

        if self.position.y < pos_min.y:
            self.position = Vec2(self.position.x, pos_min.y)
            self.velocity = Vec2(self.velocity.x, -self.velocity.y * DAMPING + self.box.velocity.y)
        elif self.position.y > pos_max.y:
            self.position = Vec2(self.position.x, pos_max.y)
            self.velocity = Vec2(self.velocity.x, -self.velocity.y * DAMPING + self.box.velocity.y)

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
        self.position = Vec2(0, 0)
        self.size = Vec2(350, 350)
        self._prev_position = Vec2(0, 0)
        self.velocity = Vec2(0, 0)
        self._input: IInputService

    @override
    def on_load(self) -> None:
        self._input = self.get_service(IInputService)

    @override
    def _pre_fixed_update(self, delta: float) -> None:
        self._prev_position = self.position

        if look := Vec2.as_vec2(self._input.get_vector("LOOK_X", "LOOK_Y")):
            self.position = look

        self.velocity = (self.position - self._prev_position) / delta
        if self._input.pressed("SPAWN"):
            self.spawn_child(Circle(self, self.position, self.velocity))
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
    def __init__(self, position: Vec2, velocity: Vec2, lifetime: float = 1.0, color: str = "white", size: float = 2):
        super().__init__()
        self.position = position
        self._prev_position = position
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.size = size

    @override
    def _pre_fixed_update(self, delta: float):
        self._prev_position = self.position
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
    def __init__(self, area: Rect, wind: Vec2, rate: int = 5):
        super().__init__()
        self.area = area          # Rect(x, y, w, h)
        self.wind = wind          # Vec2(x, y)

    @override
    def _pre_fixed_update(self, delta: float):
        if random() < 0.1:
            # Random position inside area
            x = self.area.x + random() * self.area.width
            y = self.area.y + random() * self.area.height
            pos = Vec2(x, y)

            # Random velocity around wind vector
            vel = Vec2(self.wind.x + (random()-0.5)*50,
                          self.wind.y + (random()-0.5)*50)

            particle = WindParticle(pos, vel, lifetime=0.8 + random()*0.5, color="#333333", size=2)
            self.spawn_child(particle)


@final
class TitleScene(GameObject):

    @override
    def on_load(self) -> None:
        wind_emitter = WindEmitter(Rect(0, 0, *SCREEN_SIZE), Vec2(WIND_X, WIND_Y))
        box = Box()
        box.position = Vec2(200, 200)
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
