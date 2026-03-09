from pygame import KEYDOWN
from pygame.event import Event
from pygae.typing import IInputService, IMessageBus


def test_can_disable_action(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.process_events()
    input_service.disable("JUMP")
    assert input_service.pressed("JUMP") == 0


def test_can_reenable_action(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    input_service.disable("JUMP")
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.process_events()
    input_service.enable("JUMP")
    assert input_service.pressed("JUMP") == 1
