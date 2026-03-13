from unittest.mock import Mock
from pygame import USEREVENT
from pygame.event import Event
from pygae.messaging import EventHandler, IMessageBus
from fakes import SimpleGameObject


def test_process_events_executes_subscription_handlers(
    game_object: SimpleGameObject, message_bus: IMessageBus
):
    # given an initialized game object with a subscription to an event
    event_id = USEREVENT + 1
    event = Event(event_id)
    handler = Mock(spec=EventHandler)
    game_object.subscribe(event_id, handler)

    # And an event in the queue
    game_object.publish(event)
    message_bus.process_events()

    # when calling process_events
    game_object.process_events()

    # then handler is called
    handler.assert_called_once_with(event)


def test_process_events_executes_subscription_handlers_on_local_events(
    game_object: SimpleGameObject, message_bus: IMessageBus
):
    # given an initialized game object with a subscription to an event
    event_id = USEREVENT + 1
    event = Event(event_id)
    handler = Mock(spec=EventHandler)
    game_object.subscribe(event_id, handler)

    # And a local event in the queue
    game_object.notify(event)

    # when calling process_events
    game_object.process_events()

    # then handler is called
    handler.assert_called_once_with(event)


def test_pending_events_are_cleared_when_kill_is_called(game_object: SimpleGameObject):
    # given an initialized game object with a subscription to an event
    event_id = USEREVENT + 1
    event = Event(event_id)
    handler = Mock(spec=EventHandler)
    game_object.subscribe(event_id, handler)

    # And a local event in the queue
    game_object.notify(event)

    # when calling kill before next process events
    game_object.kill()
    game_object.process_events()

    # then handler is never called
    handler.assert_not_called()


def test_subscriptions_are_removed_when_kill_is_called(game_object: SimpleGameObject):
    # given an initialized game object with a subscription to an event
    event_id = USEREVENT + 1
    handler = Mock(spec=EventHandler)
    game_object.subscribe(event_id, handler)

    # when calling kill before next process events
    game_object.kill()

    # then handler is never called
    assert list(game_object._subscriptions) == []


def test_event_handlers_are_removed_when_kill_is_called(game_object: SimpleGameObject):
    # given an initialized game object with a subscription to an event
    event_id = USEREVENT + 1
    handler = Mock(spec=EventHandler)
    game_object.subscribe(event_id, handler)

    # when calling kill before next process events
    game_object.kill()

    # then handler is never called
    assert list(game_object._event_handlers.keys()) == []
