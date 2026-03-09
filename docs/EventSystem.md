# Event System

The PyGAE event system provides decoupled communication between game systems using a central message bus.

It is built on top of the pygame event queue but adds:

- Subscription management
- Event routing
- Deterministic event processing
- Engine lifecycle integration

The system is composed of two primary components:

| Component | Purpose |
| --- | --- |
| `IMessageBus` | Central event dispatcher used by the engine and game objects |
| `IEventGateway` | Adapter that connects the bus to the pygame event queue |


---

## Architecture

The event system separates event transport from event routing.

```
GameObject / Engine
        │
        ▼
   IMessageBus
        │
        ▼
   IEventGateway
        │
        ▼
   pygame.event queue
```


This design provides several benefits:

- Decouples the engine from pygame
- Makes the event system easier to test
- Allows alternate event gateways if needed

---

## Core Interface

### IMessageBus

The message bus is the central hub for all engine events.

| Method | Called By | Description |
| --- | --- | --- |
| `subscribe(event_id, handler)` | Game Objects | Register a handler for an event type |
| `unsubscribe(subscription_id)` | Game Objects | Remove a previously registered subscription |
| `publish(event)` | Game Objects/Engine | Broadcast an event |
| `process_events()` | Engine | Dispatch events to subscribers |


### IEventGateway

The gateway acts as a thin wrapper around the pygame event system.

| Method | Called By | Description |
| --- | --- | --- |
| `get()` | MessageBus | Retrieve pending pygame events |
| `post(event)` | MessageBus | Push an event to the pygame queue |
| `pump()` | Engine | Flush pending OS events |

---

## Event Lifecycle

Events pass through several stages before reaching subscribers.

```
publish(event)
      │
      ▼
pygame.event queue
      │
      ▼
MessageBus.process_events()
      │
      ▼
subscriber handlers
```

### 1. Event Publication

Events are published through the message bus.

```python
bus.publish(event)
```

Internally this forwards the event to the `IEventGateway`.

```python
pygame.event.post(event)
```

At this point the event enters the pygame event queue.

### 2. Event Collection

When the engine calls:

```python
bus.process_events()
```

The message bus retrieves events from the gateway.

```python
events = pygame.event.get()
```

### 3. Event Dispatch

Each event is delivered to all registered handlers.

```python
for handler in handlers[event.type]:
    handler(event)
```

Handlers are executed synchronously during `process_events()`.

---

## Subscriptions

Handlers subscribe to events using the event ID.

```python
sub_id = bus.subscribe(EVENT_ID, handler)
```

Internally the message bus stores:

```
SubscriptionId -> (EventId, Handler)
```

and also maintains a lookup table:

```
EventId -> [Handlers]
```

This allows efficient dispatch to all listeners of a specific event.

---

## Unsubscribing

Subscriptions are removed using the returned subscription ID.

```python
bus.unsubscribe(sub_id)
```

Removing a subscription prevents further event delivery.

---

## Integration with GameObject

Game objects typically interact with the event system through helper methods rather than accessing the bus directly.

__Example:__

```python
self.subscribe(PYGAE_DAMAGE_EVENT, self._on_damage)
```

Internally this registers the handler with the message bus.

Incoming events are then queued inside the object and processed during:

```python
GameObject.process_events()
```

This design ensures event handling occurs at a deterministic point in the frame lifecycle.

---

## Engine Event Loop

A typical frame executes the following order:

```python
event_bus.process_events()
scene_manager.process_events()
scene_manager.fixed_update(fixed_delta) # Called zero or more per frame with fixed delta
scene_manager.update(delta)             # Called once per frame with eplased delta
scene_manager.render(surface, alpha)
```

This ordering ensures:

1. Events are collected first
2. Game objects process them safely
3. Updates occur afterward

---

## Example

### Subscribing to an Event

```python
class Player(GameObject):

    def on_load(self):
        self.subscribe(DAMAGE_EVENT, self._on_damage)

    def _on_damage(self, event):
        self.health -= event.amount
```

### Publishing an Event

```python
damage_event = make_damage_event(amount=10)
self.publish(damage_event)
```

---

## Design Notes

The event system provides:

- Loose coupling between systems
- Centralized event routing
- Deterministic event delivery
- Integration with the pygame event queue

Because events pass through pygame's queue, the system can handle both:

- Engine/game events
- Native pygame input events
- using the same mechanism.

---

## Summary

| Component | Responsibility |
| --- | --- |
| `IEventGateway` | Interface to pygame's event system |
| `MessageBus` | Event subscription and dispatch |
| `GameObject` | Event consumption |
| `SceneManager` | Scene lifecycle management |

Together these systems form the core runtime architecture of PyGAE.
