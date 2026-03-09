import pytest

from pyioc3.autowire import AutoWireContainerBuilder
from pyioc3.interface import Container

from pygae.game_object import GameObject
from pygae.typing import IEventGateway, IInputService, IMessageBus, ISceneManager

from fakes import EventQueueFake


@pytest.fixture
def ioc() -> Container:
    return (
        AutoWireContainerBuilder("pygae.service")
        .bind(IEventGateway, EventQueueFake, "SINGLETON")
        .build()
    )


@pytest.fixture
def event_gateway(ioc: Container) -> IEventGateway:
    return ioc.get(IEventGateway)


@pytest.fixture
def message_bus(ioc: Container) -> IMessageBus:
    return ioc.get(IMessageBus)


@pytest.fixture
def scene_manager(ioc: Container) -> ISceneManager:
    return ioc.get(ISceneManager)


@pytest.fixture
def input_service(ioc: Container) -> IInputService:
    return ioc.get(IInputService)
