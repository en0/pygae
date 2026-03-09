from pygame import MOUSEMOTION
from pygame.event import Event
from pygae.typing import IInputService, IMessageBus
from pygae.value_object.input_binding import (
    AXIS_MOUSE_DX,
    AXIS_MOUSE_DY,
    AXIS_MOUSE_X,
    AXIS_MOUSE_Y,
    DEVICE_MOUSE,
    TYPE_AXIS,
)


def test_get_value_for_mouse_x(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    message_bus.publish(Event(MOUSEMOTION, pos=(111, 222), rel=(11, 22)))
    ib = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_X)
    input_service.bind("ACTION", ib)
    message_bus.process_events()
    assert input_service.get_value("ACTION") == 111.0


def test_get_value_for_mouse_y(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    message_bus.publish(Event(MOUSEMOTION, pos=(111, 222), rel=(11, 22)))
    ib = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_Y)
    input_service.bind("ACTION", ib)
    message_bus.process_events()
    assert input_service.get_value("ACTION") == 222.0


def test_get_value_for_mouse_dx(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    message_bus.publish(Event(MOUSEMOTION, pos=(111, 222), rel=(11, 22)))
    ib = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_DX)
    input_service.bind("ACTION", ib)
    message_bus.process_events()
    assert input_service.get_value("ACTION") == 11.0


def test_get_value_for_mouse_dy(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    message_bus.publish(Event(MOUSEMOTION, pos=(111, 222), rel=(11, 22)))
    ib = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_DY)
    input_service.bind("ACTION", ib)
    message_bus.process_events()
    assert input_service.get_value("ACTION") == 22.0


def test_get_vector_for_mouse(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    message_bus.publish(Event(MOUSEMOTION, pos=(111, 222), rel=(11, 22)))
    ib_x = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_X)
    ib_y = make_binding(type=TYPE_AXIS, device=DEVICE_MOUSE, id=AXIS_MOUSE_Y)
    input_service.bind("ACTION_X", ib_x)
    input_service.bind("ACTION_Y", ib_y)
    message_bus.process_events()
    assert input_service.get_vector("ACTION_X", "ACTION_Y") == (111.0, 222.0)
