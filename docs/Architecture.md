# Engine Architecture

PyGAE is built around a small set of core systems that manage game objects, scenes, events, and player input.
Together these systems drive the runtime lifecycle of the engine.

The primary components are:

| Component | Responsibility |
| --- | --- |
| GameObject | Base object for all entities in the game world |
| SceneManager | Controls the active scene |
| MessageBus | Event distribution and communication |
| EventGateway | Bridge to the pygame event system |
| InputService | High-level action-based input system |

---

## System Overview

The runtime flow of the engine looks like this:

```
Engine Loop
    │
    ▼
MessageBus.process_events()
    │
    ▼
InputService (event handlers update input state)
    │
    ▼
SceneManager.process_events()
    │
    ▼
Active Scene (GameObject tree)
    ├─ process_events()
    ├─ fixed_update(fixed_delta)
    ├─ update(delta)
    └─ render(surface, alpha)
```

The `SceneManager` controls the top-level scene, while each scene manages its own GameObject hierarchy.

The `InputService` listens to hardware events and converts them into high-level **actions** that game logic can query.

---

## GameObject Hierarchy

All gameplay objects inherit from `GameObject`.

Objects are organized into a tree structure.

```
Scene
 ├─ Player
 │   └─ Weapon
 ├─ Enemy
 └─ UI
```

Lifecycle calls propagate through the tree:

```python
process_events()
fixed_update()
update()
render()
```

Each object can `spawn` or `kill` children safely during the event phase.

---

## Scene Management

The `SceneManager` ensures that only one scene is active at a time.

Scene transitions are deferred and processed during `process_events()`.

```
set_scene(new_scene)
      │
      ▼
next frame
      │
      ▼
kill old scene
spawn new scene
activate new scene
```

This prevents mid-frame mutations of the scene graph.

---

## Event System

The `MessageBus` provides a central messaging system used by both the engine and game objects.

Events flow through the system like this:

```
publish(event)
      │
      ▼
pygame event queue
      │
      ▼
EventGateway
      │
      ▼
MessageBus.process_events()
      │
      ▼
subscribed handlers
```

Game objects typically subscribe to events using helper methods provided by `GameObject`.

The `InputService` also subscribes to these events to update hardware input state.

### Deterministic Event Processing

Although the `MessageBus` invokes handlers immediately during `process_events()`,
`GameObject` instances do **not process events directly inside those handlers**.

Instead, the base `GameObject` handler **queues incoming events internally**.

Example flow:

```
MessageBus.process_events()
      │
      ▼
GameObject event handler
      │
      ▼
event added to GameObject queue
```

The queued events are later processed when the object's own lifecycle method runs:

```
SceneManager.process_events()
      │
      ▼
Active Scene
      │
      ▼
GameObject.process_events()
      │
      ▼
child GameObject.process_events()
```

This ensures that events propagate through the scene graph in a **deterministic tree order**, rather than the order in which handlers happened to subscribe to the `MessageBus`.

### Why This Matters

Without this queueing step, event handlers would run in **subscription order**, which may vary depending on initialization order.

By deferring processing to `GameObject.process_events()`:

- Events are handled in **scene hierarchy order**
- Parent objects process events **before their children**
- Event handling remains **deterministic across runs**

This design keeps gameplay logic predictable while still allowing the `MessageBus` to operate as a global communication system.

---

## Input System

The `InputService` provides a high-level abstraction over hardware input devices.

Instead of directly responding to raw keyboard or mouse events, game code queries **actions** defined by input bindings.

Example:

```python
input_service.set_map({
    "jump": InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_SPACE),
    "fire": InputBinding(TYPE_BUTTON, DEVICE_MOUSE, 1),
})
```

Game logic then interacts with these actions:

```python
if input_service.pressed("jump"):
    player.jump()
```

### Responsibilities

The input system:

- Translates raw hardware events into **action states**
- Maintains button states (`pressed`, `released`, `held`)
- Tracks analog values and relative axes
- Supports runtime rebinding of controls
- Integrates with the engine event system

### Input Query Model

Game code interacts with input through the following query types:

| Query | Description |
|---|---|
| `pressed(action)` | Number of presses since the last simulation step |
| `released(action)` | Number of releases since the last simulation step |
| `held(action)` | Whether the action is currently held |
| `get_value(action)` | Analog value of an action |
| `get_vector(x, y)` | Combine two actions into a vector |

This action-based approach decouples gameplay logic from specific hardware inputs.

---

## Frame Lifecycle

Each frame executes the following high-level order:

```python
event_bus.process_events()
scene_manager.process_events()

# simulation step(s)
scene_manager.fixed_update(fixed_delta)   # may run multiple times
input_service.clear_edge_inputs()

# frame update
input_service.clear_relative_axes()
scene_manager.update(delta)

scene_manager.render(surface, alpha)
```

This ordering ensures:

- Hardware events are processed
- Input state is updated
- Scene transitions occur safely
- Simulation steps run deterministically
- Frame-level input is reset before update
- Rendering occurs last

---

## Input Timing Semantics

Different input states persist for different durations within the frame lifecycle.

| Input State | Lifetime | Cleared |
|---|---|---|
| `pressed` / `released` | simulation step | after each `fixed_update()` |
| `held` | continuous | never cleared |
| relative axes (mouse delta, scroll) | render frame | before `update()` |

This design ensures that:

- Button edges are processed once per simulation step
- Relative input such as mouse movement is sampled once per frame
- Catch-up frames do not amplify mouse input

---

## Summary

PyGAE's architecture emphasizes:

- Deterministic lifecycle execution
- Hierarchical object composition
- Decoupled communication through events
- Action-based input abstraction
- Safe scene transitions

These systems form the minimal core needed to build structured games while remaining lightweight and easy to extend.
