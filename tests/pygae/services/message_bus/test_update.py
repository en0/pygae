from pygame.event import Event
from pygae.service.message_bus import MessageBus
from pygae.typing import EventHandler, EventId, SubscriptionId


def test_update_does_not_call_installed_handlers_when_no_event_matches(
    message_bus: MessageBus,
    sub_1: SubscriptionId,
    handler_1: EventHandler,
):
    # given an existing subscription
    _ = sub_1

    # when calling update without matching events
    message_bus.process_events()

    # then the handler is not called
    assert not handler_1.called


def test_update_calls_installed_handlers_when_event_matches(
    message_bus: MessageBus,
    sub_1: SubscriptionId,
    event_id: EventId,
    handler_1: EventHandler,
):
    # given an existing subscription and an event enqueued
    _ = sub_1
    message_bus.publish(Event(event_id))

    # when calling update without matching events
    message_bus.process_events()

    # then the handler is not called
    assert handler_1.called
