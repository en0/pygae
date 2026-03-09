from pyioc3.interface import Container
import pytest

from fakes import SimpleGameObject


@pytest.fixture
def game_object(ioc: Container) -> SimpleGameObject:
    go = SimpleGameObject()
    go.on_load()
    go.spawn()
    go.set_service_locator(ioc)
    return go
