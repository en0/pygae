# InputService

`InputService` manages all player input in the PyGAE engine. It abstracts hardware inputs (keyboard, mouse, future joystick) into high-level actions that the game can query.

This service tracks **pressed, released, held, analog, and vector inputs**, supports **runtime re-binding**, and integrates with the engine's **message bus** for deterministic event handling.

---

## Overview

The `InputService` is responsible for:

- Maintaining the state of all input actions
- Allowing querying of actions in a high-level way
- Supporting runtime action-to-hardware binding changes
- Clearing edge-triggered and relative inputs each frame
- Integrating with the engine's message bus for event handling

The service is registered in the IOC container as a **singleton**.

---

## Core Interface

| Method | Called By | Description |
| ------ | ---------- | ----------- |
| `pressed(action)` | Game Logic | Returns how many times an action was pressed since the last fixed update. |
| `released(action)` | Game Logic | Returns how many times an action was released since the last fixed update. |
| `held(action)` | Game Logic | Returns whether an action is currently held down. |
| `get_value(action)` | Game Logic | Returns the analog value for an action (1.0 for digital held buttons, 0.0 otherwise). |
| `get_vector(x_action, y_action)` | Game Logic | Combines two actions into a 2D `tuple[float,float]` value. |
| `set_map(binding_map)` | Game Logic | Replace all action-to-input bindings with a new map. |
| `bind(action, bindings)` | Game Logic | Assign one or more bindings to a single action. |
| `unbind(action)` | Game Logic | Remove all bindings for a specific action. |
| `get_bindings(action)` | Game Logic | Retrieve all bindings associated with an action. |
| `disable(actions)` | Game Logic | Temporarily disable one or more actions (bindings remain). |
| `enable(actions)` | Game Logic | Re-enable previously disabled actions. |
| `clear_edge_inputs()` | Engine/Frame | Reset pressed/released counts for all actions. |
| `clear_relative_axes()` | Engine/Frame | Reset accumulated relative axis values (mouse delta, scroll). |

---

## Input Lifecycle

`InputService` operates in a **frame-based cycle** integrated with the engine:

```
_engine fixed update → InputService pressed/released/held query
_engine update → InputService get_value/get_vector query
_post fixed update → InputService clear_edge_inputs()
_post frame update → InputService clear_relative_axes()
```

### Event Handling

InputService subscribes to relevant Pygame events when a binding is set:

- **Keyboard buttons:** `KEYDOWN`, `KEYUP`
- **Mouse buttons:** `MOUSEBUTTONDOWN`, `MOUSEBUTTONUP`
- **Mouse motion:** `MOUSEMOTION`
- **Mouse wheel:** `MOUSEWHEEL`

Handlers update internal state:

```python
# Example: keyboard key press
pressed, released, held = self._keyboard_states[key]
self._keyboard_states[key] = (pressed + 1, released, True)
```

All input states are stored separately for buttons and axes. Edge states (`pressed`, `released`) are reset after each fixed update. Relative axes (`DX`, `DY`, scroll) are reset each frame.

---

## Binding Management

`InputBinding` objects map hardware inputs to high-level action names.

- **Attributes**: `type`, `device`, `id`, `mods`, `joy_id`
- **Supported devices**: keyboard, mouse (joystick planned)
- **Supported input types**: button, axis

Bindings can be managed dynamically:

```python
# Replace all bindings
input_service.set_map({
    "jump": [InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_SPACE)],
    "look_x": [InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MOUSE_DX)],
})

# Bind a new action
input_service.bind("fire", InputBinding(TYPE_BUTTON, DEVICE_MOUSE, 1))

# Disable an action
input_service.disable("fire")
```

---

## Example Usage

```python
input_service: IInputService = service_locator.get(IInputService)

# Define actions and bindings
input_service.set_map({
    "move_x": [InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MOUSE_DX)],
    "move_y": [InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MOUSE_DY)],
    "jump": [InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_SPACE)],
})

# Game loop query
if input_service.pressed("jump"):
    player.jump()

movement = input_service.get_vector("move_x", "move_y")
player.move(movement)
```

---

## Frame Clearing

To ensure deterministic input behavior, transient input states are cleared at specific points in the engine lifecycle.

### Edge Inputs

Edge-triggered inputs such as `pressed` and `released` are cleared **after each fixed simulation step**.

```python
input_service.clear_edge_inputs()
```

This occurs at the end of the engine's `_fixed_update()` stage.

Because fixed updates may run multiple times per frame, this guarantees that edge events are processed **at most once** in any given frame, preventing the same press or release from being consumed repeatedly.

### Relative Axes

Relative axes (mouse movement deltas and scroll offsets) are cleared **once per rendered frame before the variable `update()` step**.

```python
input_service.clear_relative_axes()
```

This occurs at the start of the engine's `_update()` stage.

### Behavior During Catch-Up Frames

If the engine performs multiple `fixed_update()` calls within a single frame (for example, when catching up after a lag spike), **relative axis values remain unchanged across those simulation steps**.

Example frame timeline:

```
_process_events()

_fixed_update()  # step 1 (same mouse delta)
 └─ clear_edge_inputs()

_fixed_update()  # step 2 (same mouse delta)
 └─ clear_edge_inputs()

_fixed_update()  # step 3 (same mouse delta)
 └─ clear_edge_inputs()

_update()
 ├─ clear_relative_axes()
 └─ scene.update()

_render()
```

This behavior ensures:

- Edge-triggered inputs are handled deterministically per simulation step
- Relative inputs are sampled once per frame
- Catch-up frames do not amplify mouse movement or scroll input
- Input remains stable even during temporary frame stalls

---

## Design Notes

- Input state is **centralized** and **deterministic**
- Supports **dynamic rebinding** at runtime without disrupting current state
- Edge-triggered and relative inputs are **explicitly cleared** for predictable behavior
- Fully integrated with the **engine's event bus** for message-driven input processing
- Designed for **high-level action abstraction** rather than direct key polling
