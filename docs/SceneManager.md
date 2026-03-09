# SceneManager

`SceneManager` controls the active scene in the PyGAE engine and manages scene transitions.

A scene is any object implementing `IGameObject`, typically a subclass of `GameObject`.

The scene manager ensures that scenes are __spawned, killed, and activated safely__ during the engine lifecycle.

Only __one__ scene may be active at a time.

Scene transitions are deferred and processed during `process_events()` to ensure deterministic behavior.

---

## Overview

The `SceneManager` is responsible for:

- Managing the active scene
- Performing safe scene transitions
- Driving the top-level lifecycle of the scene
- Publishing scene lifecycle events

The `SceneManager` is registered in the IOC container as a __singleton service__.

---

## Core Interface

These methods define the engine entry points for scene management.

| Method | Called By | Description |
| ----------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `set_scene(scene)` | User/Game Logic | Requests a scene transition. |
| `process_events()` | Engine | Processes scene transitions and event propagation. |
| `fixed_update(fixed_delta)` | Engine | Updates the active scene on a fixed timestep. |
| `update(delta)` | Engine | Updates the active scene. |
| `render(surface, alpha)` | Engine | Renders the active scene. |

---

## Scene Transition Lifecycle

Scene transitions occur in __three__ stages and are always processed during `process_events()`.

Calling `set_scene()` does not immediately change the active scene.

Instead, the new scene is stored as a pending scene.

### 1. Requesting a Scene Transition

Game logic requests a new scene:

```python
scene_manager.set_scene(MainMenuScene())
```

This sets the scene as the pending scene.

### 2. Transition Processing

During the next call to process_events() the scene manager performs the transition.

```
process_events()
 └─ transition_scene()
     ├─ kill_active_scene()
     ├─ spawn_pending_scene()
     └─ activate_pending_scene()
```

### 3. Kill Current Scene

If a scene is currently active:

```python
scene.kill()
scene.on_unload()
```

The manager then publishes a _OBJECT_KILL_ event.

This allows other systems to react to scene removal.

### 4. Spawn New Scene

The pending scene is initialized:

```python
scene.set_service_locator(locator)
scene.on_load()
scene.spawn()
```

The manager then publishes a _OBJECT_SPAWN_ event.

### 5. Activate the Scene

The pending scene becomes the new active scene.

The manager publishes a _SCENE_SET_ event and replaces the `old_scene` with the `new_scene`.

---

## Frame Lifecycle

Once a scene is active, the scene manager forwards lifecycle calls to it.

Each frame typically executes:

```python
process_events()
fixed_update(fixed_delta)
update(delta)
render(surface, alpha)
```

### process_events()

```
SceneManager.process_events
 ├─ handle pending scene transition
 └─ active_scene.process_events()
 ```

### fixed_update()

```
SceneManager.update
 └─ active_scene.fixed_update(fixed_delta)
 ```

### update()

```
SceneManager.update
 └─ active_scene.update(delta)
 ```

### render()

```
SceneManager.render
 └─ active_scene.render(surface, alpha)
```

---

## Scene Structure

Scenes are typically implemented as a `GameObject` containing other objects.

Example:

```
class MainMenuScene(GameObject):

    def on_load(self):
        self.spawn_child(MenuUI())

    def _pre_render(self, surface, alpha):
        surface.fill((0, 0, 0))
```

---

## Example Usage

```
scene_manager = container.get(ISceneManager)

scene_manager.set_scene(MainMenuScene())

while running:

    scene_manager.process_events()
    scene_manager.fixed_update(fixed_delta)
    scene_manager.update(delta)
    scene_manager.render(screen, alpha)
```

---

## Scene Events

The scene manager publishes events during transitions.

| Event | Description |
| --- | --- |
| `PYGAE_OBJECT_KILL` | Active scene is being destroyed |
| `PYGAE_OBJECT_SPAWN` | Pending scene has been spawned |
| `PYGAE_SCENE_SET` | Scene transition completed |

These events allow other systems to react to scene changes.

---

## Design Notes

The scene manager ensures that:

- Scene transitions occur at a deterministic point in the frame
- Scenes receive proper load and unload lifecycle calls
- Scene activation is atomic
- Only one scene is active at a time

This keeps scene transitions predictable and avoids mid-frame mutation of the scene graph.
