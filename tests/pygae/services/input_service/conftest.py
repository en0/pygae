import pytest

from pygame import K_SPACE, KEYDOWN
from pygame.event import Event
from typing import Callable

from pygae.input import InputBinding
from pygae.input import (
    TYPE_BUTTON,
    DEVICE_KEYBOARD,
)


@pytest.fixture
def make_binding() -> Callable[[], InputBinding]:
    def _wrapped(**kwargs) -> InputBinding:
        kwargs.setdefault("type", TYPE_BUTTON)
        kwargs.setdefault("device", DEVICE_KEYBOARD)
        kwargs.setdefault("id", K_SPACE)
        return InputBinding(**kwargs)

    return _wrapped


@pytest.fixture
def space_press_event() -> Event:
    return Event(KEYDOWN, key=K_SPACE)
