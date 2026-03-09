from pygame import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.event import Event
from pygae.typing import IInputService, IMessageBus
from pygae.value_object.input_binding import DEVICE_MOUSE


def test_pressed_buttons_for_existing_keyboard_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.process_events()
    assert input_service.pressed("JUMP") == 1


def test_pressed_buttons_for_existing_mouse_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=1, device=DEVICE_MOUSE)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(MOUSEBUTTONDOWN, button=1))
    message_bus.process_events()
    assert input_service.pressed("JUMP") == 1


def test_pressed_action_on_multiple_budings_sum(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    mouse = make_binding(id=1, device=DEVICE_MOUSE)
    keyboard = make_binding(id=111)
    input_service.bind("JUMP", [mouse, keyboard])
    message_bus.publish(Event(MOUSEBUTTONDOWN, button=1))
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.process_events()
    assert input_service.pressed("JUMP") == 2


def test_released_buttons_for_existing_keyboard_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(KEYUP, key=111))
    message_bus.process_events()
    assert input_service.released("JUMP") == 1


def test_released_buttons_for_existing_mouse_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=1, device=DEVICE_MOUSE)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(MOUSEBUTTONUP, button=1))
    message_bus.process_events()
    assert input_service.released("JUMP") == 1


def test_released_action_on_multiple_budings_sum(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    mouse = make_binding(id=1, device=DEVICE_MOUSE)
    keyboard = make_binding(id=111)
    input_service.bind("JUMP", [mouse, keyboard])
    message_bus.publish(Event(MOUSEBUTTONUP, button=1))
    message_bus.publish(Event(KEYUP, key=111))
    message_bus.process_events()
    assert input_service.released("JUMP") == 2


def test_held_buttons_for_existing_keyboard_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.process_events()
    assert input_service.held("JUMP")


def test_unheld_buttons_for_existing_keyboard_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=111)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(KEYDOWN, key=111))
    message_bus.publish(Event(KEYUP, key=111))
    message_bus.process_events()
    assert not input_service.held("JUMP")


def test_held_buttons_for_existing_mouse_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=1, device=DEVICE_MOUSE)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(MOUSEBUTTONDOWN, button=1))
    message_bus.process_events()
    assert input_service.held("JUMP")


def test_unheld_buttons_for_existing_keyboard_binding(
    input_service: IInputService, message_bus: IMessageBus, make_binding
):
    ib = make_binding(id=1, device=DEVICE_MOUSE)
    input_service.bind("JUMP", ib)
    message_bus.publish(Event(MOUSEBUTTONDOWN, button=1))
    message_bus.publish(Event(MOUSEBUTTONUP, button=1))
    message_bus.process_events()
    assert not input_service.held("JUMP")
