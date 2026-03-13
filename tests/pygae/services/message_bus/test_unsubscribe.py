from unittest.mock import Mock

from pygae.service.message_bus import MessageBus
from pygae.messaging import EventHandler, EventId, SubscriptionId


def test_unsubscribe_removes_subscription(
    message_bus: MessageBus, sub_1: SubscriptionId
):
    # given an existing subscription
    # when used to unsubscribe
    message_bus.unsubscribe(sub_1)

    # then the subscription is removed from internal state
    assert (
        sub_1 not in message_bus._subscriptions
    ), "Subscription still exists in internal state."


def test_unsubscribe_removes_handler(
    message_bus: MessageBus,
    sub_1: SubscriptionId,
    event_id: EventId,
):
    # given an subscription to an existing subscription
    # when used to unsubscribe
    message_bus.unsubscribe(sub_1)

    # then the handler is removed from internal state
    assert (
        message_bus._handlers[event_id] == []
    ), "Subscription still exists in internal state."


def test_unsubscribe_from_non_existant_subscription_is_sliently_ignored(
    message_bus: MessageBus,
    sub_1: SubscriptionId,
):
    # given an subscription to an existing subscription and we have unsubscribed from that subscription
    message_bus.unsubscribe(sub_1)

    # when attempt to unsubscribe again,
    message_bus.unsubscribe(sub_1)

    # then the system ignores the request (does not raise)
    assert True


def test_unsubscribe_from_one_handler_where_multiple_handlers_exist(
    message_bus: MessageBus, event_id: EventId
):
    # given 2 handlers and 1 event id with 2 different subscriptions
    handler1 = Mock(spec=EventHandler)
    handler2 = Mock(spec=EventHandler)
    sub1 = message_bus.subscribe(event_id, handler1)
    sub2 = message_bus.subscribe(event_id, handler2)

    # when unsubscribing from sub1
    message_bus.unsubscribe(sub1)

    # then sub2 should still exist and handler2 should still be installed
    assert sub1 not in message_bus._subscriptions, "Sub1 is still subscribed"
    assert sub2 in message_bus._subscriptions, "Sub2 is no longer subscribed"
    assert event_id in message_bus._handlers, "Event handlers not installed"
    assert (
        handler1 not in message_bus._handlers[event_id]
    ), "Handler1 is still installed"
    assert handler2 in message_bus._handlers[event_id], "Handler2 is not installed"
