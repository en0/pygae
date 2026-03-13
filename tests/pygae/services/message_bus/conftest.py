import pytest

from unittest.mock import Mock
from pygame import USEREVENT

from pygae.service.message_bus import MessageBus
from pygae.messaging import EventHandler, EventId


@pytest.fixture
def event_id() -> EventId:
    return USEREVENT + 100


@pytest.fixture
def handler_1() -> EventHandler:
    return Mock(spec=EventHandler)


@pytest.fixture
def sub_1(message_bus: MessageBus, event_id: EventId, handler_1: EventHandler):
    return message_bus.subscribe(event_id, handler_1)


@pytest.fixture
def handler_2() -> EventHandler:
    return Mock(spec=EventHandler)


@pytest.fixture
def sub_2(message_bus: MessageBus, event_id: EventId, handler_2: EventHandler):
    return message_bus.subscribe(event_id, handler_2)
