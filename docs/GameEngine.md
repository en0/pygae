# GameEngine

The `GameEngine` class provides a minimal Python game loop and lifecycle management for Pygame-based
projects. It integrates service location, messaging, and scene management to provide a structured
environment for building games, simulations, or interactive applications.

---

## Class Attributes


| Name | Type | Description |
| --- | --- | --- |
| `SCREEN_SIZE` | `tuple[int, int]` | The default window size for the game display. Can be overridden in a subclass. |
| `FRAMERATE` | `int` | Target frames per second for the game loop. Can be overridden in a subclass. |


---

## Example Usage

```python
import pygame
from pygae.engine import GameEngine
from pygae.typing import IGameObject

class MyGame(GameEngine):

    SCREEN_SIZE = (1024, 768)
    FRAMERATE = 60

    def _on_load(self) -> None:
        print("Game initializing...")
        # Set up scenes, services, initial game objects here
        # self.set_scene(TitleScene())

    def _pre_frame(self) -> None:
        # Optional: logic to execute at the start of every frame
        pass

    def _post_frame(self) -> None:
        # Optional: logic to execute at the end of every frame
        pass

    def _on_unload(self) -> None:
        print("Game shutting down...")

if __name__ == "__main__":
    game = MyGame()
    game.run()
```

---

## Core Interface

These methods are primarily called by the engine, not by client code:


| Method | Description | Called By |
| --- | --- | ---  |
| `run()` | Starts the game loop, initializes Pygame, loads scenes, processes events, updates, and renders frames until the game quits. | Client |
| `_get_root_surface()` | Returns the Pygame display surface used for rendering. | Engine |
| `_process_events()` | Collects pending events and dispatches them to the active scene and message bus. | Engine |
| `_fixed_update(fixed_delta: float)` | Advances the active scene using a fixed timestep (`fixed_delta`) for deterministic calculations. May be called zero or more times per frame. | Engine |
| `_update(delta: float)` | Updates the active scene. delta is the time since the last frame in seconds. | Engine |
| `_render(surface: pygame.Surface, alpha: float)` | Renders the active scene onto the provided surface. | Engine |

---

## Helpers (callable by clients)


| Method | Description |
| --- | --- |
| `set_scene(scene: IGameObject)` | Sets the pending scene. The scene transition will be processed on the next call to _process_events. |
| `quit()` | Publishes a quit event to the message bus, signaling the engine to stop running. |

---

## Optional Hooks

Clients can override these hooks to inject custom logic without modifying the engine loop:


| Method | Description |
| --- | --- |
| `_pre_frame()` | Called at the start of each frame, before scene events and updates. Useful for temporary debugging, counters, or frame-specific logic. |
| `_post_frame()` | Called at the end of each frame, after scene updates and rendering. Useful for logging, overlays, or debug output. |
| `_on_unload()` | Called when the engine is shutting down, just before Pygame quits. Useful for resource cleanup. |


---

## Required Hooks

Clients must implement these hooks in subclasses:


| Method | Description |
| --- | --- |
| `_on_load()` | Called during engine initialization, before entering the main loop. Use this to set up scenes, services, and initial game objects. |


---

## Lifecycle

### Engine Loop

1. `_on_load()` — Initialize resources, scenes, and services.
2. Main loop (while `_is_running`):
  a. `_pre_frame()` — Optional per-frame start logic.
  b. `_process_events()` — Collect and dispatch events to scenes and message bus.
  c. `_update(fixed_delta)` — Advance the active scene using a fixed timestep. Called zero or more times per frame.
  d. `_update(delta)` — Update active scene with frame delta.
  e. `_render(surface, alpha)` — Render active scene.
  f. `_post_frame()` — Optional per-frame end logic.
3. `_on_unload()` — Clean up resources and exit.

### Scene Lifecycle

Scene management is delegated to the `ISceneManager`:

1. `set_scene(scene)` — Queue a scene change.
2. `_process_events()` handles:
  a. Killing the current scene (calls `kill()` and `on_unload()`).
  b. Spawning the pending scene (calls `set_service_locator()`, `on_load()`, `spawn()`).
  c. Activating the new scene.

### Frame Timing

- The engine measures elapsed time each frame using `_get_ticks()`.
- **Simulation updates** (`_fixed_update`) run at a **constant timestep** (`FIXED_DT`) and may execute zero or more times per frame, ensuring deterministic physics and gameplay logic.
- **Per-frame updates** (`_update`) run once per frame using the actual elapsed time (`delta`) for frame-dependent logic such as animations, UI, and camera movement.
- **Rendering** (`_render`) occurs once per frame and can be capped at a target `MAX_FRAMERATE`; an interpolation factor (`alpha`) is provided to smooth visuals between fixed simulation steps.
- This design decouples simulation from rendering, allowing consistent simulation speed even if the frame rate varies, while optionally limiting render updates to reduce CPU/GPU load.
