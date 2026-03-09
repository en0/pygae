# GameObject

`GameObject` is the base class for all runtime objects in the PyGAE engine.

It provides hierarchical composition, lifecycle management, event handling, and propagation of update and rendering calls.

Game objects form a tree structure, where parent objects manage the lifecycle and execution of their children.

---

## Overview

A `GameObject` provides:

- Parent/child hierarchy
- Spawn/kill lifecycle management
- Event subscription and publishing
- Engine-driven process_events, update, and render propagation
- Optional lifecycle hooks for subclass behavior

Game objects are typically managed by a Scene, which itself is usually a `GameObject`.

---

## Core Interface

These methods are part of the engine lifecycle. Most of them are not intended to be called directly by user code.

| Method                              | Called By         | Description |
| ----------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| set_service_locator(locator)        | Engine            | Injects the IOC service container used for retrieving engine services. |
| spawn()                             | Engine            | Marks the object as alive and activates it. Called when the object enters the scene hierarchy. |
| kill()                              | User/Game Logic   | Marks the object for removal and cleans up subscriptions. The parent removes the object during the next process_events() call. |
| is_alive()                          | User/Engine       | Returns whether the object is currently alive. |
| spawn_child(child)                  | User/Game Logic   | Adds a child object to this object. The child will spawn during the next process_events() cycle. |
| get_children(include_pending=False) | User/Engine       | Returns an iterator of child objects. |
| notify(event)                       | Engine/User       | Queues an event for processing by this object during process_events(). |
| process_events()                    | Engine            | Processes queued events, manages spawn/kill transitions, and propagates event processing to children. |
| fixed_update(fixed_delta)                       | Engine            | Updates the object on a fixed timestep and propagates updates to children. |
| update(delta)                       | Engine            | Updates the object and propagates updates to children. |
| render(surface, alpha)                     | Engine            | Renders the object and propagates rendering to children. Provides interpolation factor (`alpha`). |


---

## Helper Methods

These methods are safe for user code and provide convenience access to common functionality.

| Method | Called By | Description |
| ----------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| get_service(interface) | User | Retrieves a service from the IOC container. |
| subscribe(event_id, handler) | User | Subscribes this object to an event. Handlers are executed during process_events(). |
| publish(event) | User | Publishes an event to the global message bus. |
| skip_child_processing(...) | User | Controls whether lifecycle calls propagate to children. |


### skip_child_processing

```python
skip_child_processing(
    *,
    process_events: bool | None = None,
    fixed_update: bool | None = None,
    update: bool | None = None,
    render: bool | None = None
)
```

Allows an object to selectively disable propagation of lifecycle calls to its children.

Example:

```python
self.skip_child_processing(render=True)
```

This prevents children from being rendered while still allowing updates.

---

## Lifecycle Hooks

Hooks allow subclasses to inject behavior without overriding the engine lifecycle methods.

These methods are called internally by the engine.

| Hook | Called By | Description |
| ----------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| _pre_fixed_update(fixed_delta) | Engine | Called before children are updated. |
| _post_fixed_update(fixed_delta) | Engine | Called after children are updated. |
| _pre_update(delta) | Engine | Called before children are updated. |
| _post_update(delta) | Engine | Called after children are updated. |
| _pre_render(surface, alpha) | Engine | Called before children render. |
| _post_render(surface, alpha) | Engine | Called after children render. |

These hooks allow subclass behavior while preserving the correct update and rendering order.

Example:

```python
class Player(GameObject):

    def _pre_fixed_update(self, delta: float):
        self._prev_position = self.position.copy()
        self.position += self.velocity * delta

    def _pre_render(self, surface, alpha: float):
        surface.blit(self.sprite, self.position)
        render_pos = self._prev_position.lerp(self.position, alpha)
        surface.blit(self.sprite, render_pos)
```

---

## Spawn / Kill Lifecycle

Objects enter and exit the scene through the spawn/kill lifecycle.

### Spawning

1. A parent calls:

```python
spawn_child(child)
```

2. The child is placed into the parent's pending spawn queue.
3. During the next `process_events()` call:

```python
child.on_load()
child.spawn()
```

4. The child is moved into the parent's active child list.
5. An OBJECT_SPAWN event is published.

### Killing

1. Game logic calls:

```python
object.kill()
```

2. The object is marked as not alive.
3. All event subscriptions are unsubscribed and cleared.
4. All pending events are dropped
5. During the parent's next process_events() call:

```python
child.on_unload()
```

6. The child is removed from the parent's active children.
7. An OBJECT_KILL event is published.

---

## Update Lifecycle

The engine drives the update lifecycle each frame.

```python
process_events()
fixed_update(fixed_delta)
update(delta)
render(surface)
```

### process_events()

1. Remove dead children
2. Spawn pending children
3. Process queued events
4. For each child, call `child.process_events()`

### fixed_update()

1. Call `_pre_fixed_update(fixed_delta)`
2. For each child, call `child.fixed_update(fixed_delta)`
3. Call `_post_fixed_update(fixed_delta)`

### update()

1. Call `_pre_update(delta)`
2. For each child, call `child.update(delta)`
3. Call `_post_update(delta)`

### render()

1. Call `_pre_render(surface)`
2 For each child, call `child.render(surface)`
3. Call `_post_render(surface)`

---

## Event Handling

Events are delivered through the global message bus.

Objects can subscribe to events:

```python
self.subscribe(DAMAGE_EVENT, self.on_damage)
```

Incoming events are queued and processed during `process_events()`.

This ensures event handling occurs at a __deterministic point in the frame.__

---

## Example GameObject

```
class Player(GameObject):

    def on_load(self):
        self.health = 100

    def _pre_update(self, delta: float):
        if self.health <= 0:
            self.kill()

    def _pre_render(self, surface, alpha):
        surface.blit(self.sprite, self.position)
```

---

## Design Notes

The `GameObject` system is designed to provide:
- Deterministic execution order
- Safe lifecycle transitions
- Hierarchical composition
- Frame-stable event processing

The engine maintains strict control of lifecycle entry points while allowing subclass behavior through hooks and helpers.
