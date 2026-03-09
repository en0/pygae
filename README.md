# PyGAE

A PyGame engine focused on deterministic simulation processing and easy-to-understand game-object
lifecycle. PyGAE is designed for developers who want predictable simulation updates, clean lifecycle
hooks, and a simple framework for building games or simulations without fighting the engine.

## Key Features

- Deterministic Simulation – Fixed timestep updates ensure consistent behavior across runs.
- GameObject Lifecycle Hooks – Optional, easy-to-override hooks for pre/post update, render, and fixed updates.
- Service Locator / Dependency Injection – Centralized system for accessing engine-wide services (input, messaging, scene management) without tight coupling.
- Lightweight Event System – Subscribe to and handle events easily within game objects.
- Typed, Pythonic Codebase – Type hints, Mypy-ready, and fully linted with Ruff and Black.
- Easy-to-Understand Architecture – Designed to be readable, maintainable, and easily extended for custom gameplay or simulation mechanics.

_More information in the [docs](docs/Architecture.md)._

## Installation

### Use directly from Git

```bash
pip install git+https://github.com/en0/pygae.git
```

This will install PyGAE as a package you can import in your Python projects.

### Development Setup

__Clone the repository and install dependencies for development:__

```bash
git clone https://github.com/en0/pygae.git
cd pygae
uv install --dev
pre-commit install
```

This sets up pre-commit hooks for Black, Ruff, Mypy, and optional docstring validation.

__Run all checks manually with:__

```bash
uv run pre-commit run --all-files
```

__Run tests:__

```bash
uv run pytest -q --tb=short --maxfail=1 --disable-warnings --no-header --no-summary
```

## Quick Start / Hello World

```python
from pygame import Surface, Vector2, draw
from pygae.engine import GameEngine
from pygae.game_object import GameObject

@final
class Circle(GameObject):
    def __init__(self, position: Vector2) -> None:
        super().__init__()
        self.position = position
        self._prev_position = position.copy()

    @override
    def _pre_fixed_update(self, delta: float) -> None:
        self._prev_position = self.position.copy()
        self.velocity += GRAVITY * delta
        self.position += self.velocity * delta

    @override
    def _post_render(self, surface: Surface, alpha: float):
        render_pos = self._prev_position.lerp(self.position, alpha)
        _ = draw.circle(surface, "#8a322a", (int(render_pos.x), int(render_pos.y)), int(self.size.x / 2))
        _ = draw.circle(surface, "#362511", (int(render_pos.x), int(render_pos.y)), int(self.size.x / 2), width=2)

class TitleScene(GameObject):
    @override
    def on_load(self) -> None:
        self.spawn_child(Circle())

    @override
    def _pre_render(self, surface: Surface, alpha: float):
        _ = surface.fill("black")

class MyGame(GameEngine):
    @override
    def _on_load(self) -> None:
        self.set_scene(TitleScene())

if __name__ == "__main__":
    MyGame().run()
```

- Shows how to create a simple game object, a scene, and run the engine.
- Demonstrates the pre/post update hooks, rendering interpolation, and object spawning.

## Requirements

- Python 3.13+
- PyGame 2.6.1+

## Contributing

- Follow the lifecycle hook conventions for GameObjects.
- Pre-commit checks are mandatory to keep the code consistent.

## License

MIT License — see LICENSE file.
