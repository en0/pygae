from unittest.mock import Mock

from pygame import K_1, K_SPACE
from pygame.event import Event
from pygae.service.message_bus import MessageBus
from pygae.typing import EventHandler, EventId


def test_can_subscribe_to_event(message_bus: MessageBus):
    subid = message_bus.subscribe(100, Mock())
    assert subid, "No subscription id returned"


def test_subscribing_creates_subscription_entry(
    message_bus: MessageBus,
    event_id: EventId,
    handler_1: EventHandler,
):
    # given an event and hander
    # when used to create a new subscription
    subid = message_bus.subscribe(event_id, handler_1)

    # then event and handler should exist in the internal state
    assert subid in message_bus._subscriptions, "No subscription created"
    assert message_bus._subscriptions[subid] == (
        event_id,
        handler_1,
    ), "Internal state doesn't match expected."


def test_subscribing_creates_event_handler_entry(
    message_bus: MessageBus,
    event_id: EventId,
    handler_1: EventHandler,
):
    # given an event and hander
    # when used to create a new subscription
    _ = message_bus.subscribe(event_id, handler_1)

    # then event and handler should exist in the internal state
    assert event_id in message_bus._handlers, "No handler created"
    assert message_bus._handlers[event_id] == [handler_1], "Handler not installed."


def test_subscribing_multiple_handlers_on_same_event_tracks_both_handlers(
    message_bus: MessageBus,
    event_id: EventId,
    handler_1: EventHandler,
    handler_2: EventHandler,
):
    # given 1 event and 2 handlers
    # when subscribing multiple handlers for the same event
    _ = message_bus.subscribe(event_id, handler_1)
    _ = message_bus.subscribe(event_id, handler_2)

    # then event and handler should exist in the internal state
    assert event_id in message_bus._handlers, "No handler created"
    assert len(message_bus._handlers[event_id]) == 2, "Handler count is not correct."


def test_subscribe_to_filtered_handler(
    message_bus: MessageBus, event_id: EventId, handler_1: EventHandler
):
    event = Event(event_id, key=K_SPACE)
    _ = message_bus.subscribe(event_id, handler_1, filter=lambda e: e.key == K_SPACE)
    _ = message_bus.publish(event)
    message_bus.process_events()
    handler_1.assert_called_once_with(event)


def test_subscribe_to_filtered_handler_filters(
    message_bus: MessageBus, event_id: EventId, handler_1: EventHandler
):
    event = Event(event_id, key=K_1)
    _ = message_bus.subscribe(event_id, handler_1, filter=lambda e: e.key == K_SPACE)
    _ = message_bus.publish(event)
    message_bus.process_events()
    handler_1.assert_not_called()
