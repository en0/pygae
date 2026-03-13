import pytest

from pygae.messaging import IMessageBus
from fakes import SimpleGameObject


def test_get_service_raises_exception_if_locator_unset():
    go = SimpleGameObject()
    with pytest.raises(RuntimeError):
        _ = go.get_service(IMessageBus)


def test_get_service_raises_exception_if_service_not_found(
    game_object: SimpleGameObject,
):
    with pytest.raises(KeyError):
        _ = game_object.get_service(int)


def test_can_use_service_locator(
    game_object: SimpleGameObject, message_bus: IMessageBus
):
    assert game_object.get_service(IMessageBus) == message_bus
