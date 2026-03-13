from collections.abc import Iterable
from typing import override
from pygame import (
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    MOUSEWHEEL,
)
from pygame.event import Event
from pyioc3.autowire import bind

from pygae.typing import EventHandler, EventId, IInputService, IMessageBus
from pygae.value_object import InputBinding
from pygae.value_object.input_binding import (
    AXES,
    AXES_REL,
    AXIS_MOUSE_DX,
    AXIS_MOUSE_DY,
    AXIS_MOUSE_X,
    AXIS_MOUSE_Y,
    AXIS_MWHEEL_DX,
    AXIS_MWHEEL_DY,
    DEVICE_KEYBOARD,
    DEVICE_MOUSE,
    TYPE_AXIS,
    TYPE_BUTTON,
)


@bind(IInputService, "SINGLETON", lambda c: c)
class InputService(IInputService):
    @staticmethod
    def _as_list(o: InputBinding | list[InputBinding]) -> list[InputBinding]:
        if isinstance(o, list):
            return o
        else:
            return [o]

    def __init__(self, message_bus: IMessageBus):
        self._bus: IMessageBus = message_bus
        self._bindings: dict[str, list[InputBinding]] = dict()
        self._disabled_actions: set[str] = set()
        self._keyboard_states: dict[int, tuple[int, int, bool]] = dict()
        self._mouse_button_states: dict[int, tuple[int, int, bool]] = dict()
        self._mouse_axes: list[float] = [0] * (max(AXES) + 1)

        # Map binding types/devices to source events and handlers.
        # System subscribes when it has a valid binding.
        self._subscribed_events: set[int] = set()
        self._event_handler_map: dict[
            str, dict[str, list[tuple[EventId, EventHandler]]]
        ] = {
            TYPE_BUTTON: {
                DEVICE_KEYBOARD: [
                    (KEYDOWN, self._keydown_event_handler),
                    (KEYUP, self._keyup_event_handler),
                ],
                DEVICE_MOUSE: [
                    (MOUSEBUTTONDOWN, self._mousebuttondown_event_handler),
                    (MOUSEBUTTONUP, self._mousebuttonup_event_handler),
                ],
            },
            TYPE_AXIS: {
                DEVICE_MOUSE: [
                    (MOUSEMOTION, self._mousemotion_event_handler),
                    (MOUSEWHEEL, self._mousewheel_event_handler),
                ],
            },
        }

    def _ensure_subscriptions(self, binding: InputBinding):
        spec = self._event_handler_map.get(binding.type, {}).get(binding.device, [])

        for event_id, handler in spec:
            if event_id not in self._subscribed_events:
                self._subscribed_events.add(event_id)
                _ = self._bus.subscribe(event_id, handler)

    def _keydown_event_handler(self, event: Event) -> None:
        key: int | None = getattr(event, "key", None)
        if key is None:
            return
        pressed, released, _ = self._keyboard_states.setdefault(key, (0, 0, False))
        self._keyboard_states[key] = (pressed + 1, released, True)

    def _keyup_event_handler(self, event: Event) -> None:
        key: int | None = getattr(event, "key", None)
        if key is None:
            return
        pressed, released, _ = self._keyboard_states.setdefault(key, (0, 0, False))
        self._keyboard_states[key] = (pressed, released + 1, False)

    def _mousebuttondown_event_handler(self, event: Event) -> None:
        button: int | None = getattr(event, "button", None)
        if button is None:
            return
        pressed, release, _ = self._mouse_button_states.setdefault(
            button, (0, 0, False)
        )
        self._mouse_button_states[button] = (pressed + 1, release, True)

    def _mousebuttonup_event_handler(self, event: Event) -> None:
        button: int | None = getattr(event, "button", None)
        if button is None:
            return
        pressed, release, _ = self._mouse_button_states.setdefault(
            button, (0, 0, False)
        )
        self._mouse_button_states[button] = (pressed, release + 1, False)

    def _mousemotion_event_handler(self, event: Event) -> None:
        pos: tuple[int, int] | None = getattr(event, "pos", None)
        if pos is not None:
            self._mouse_axes[AXIS_MOUSE_X] = float(pos[0])
            self._mouse_axes[AXIS_MOUSE_Y] = float(pos[1])
        rel: tuple[int, int] | None = getattr(event, "rel", None)
        if rel is not None:
            self._mouse_axes[AXIS_MOUSE_DX] += float(rel[0])
            self._mouse_axes[AXIS_MOUSE_DY] += float(rel[1])

    def _mousewheel_event_handler(self, event: Event) -> None:
        dx = float(getattr(event, "precise_x", getattr(event, "x", 0)))
        dy = float(getattr(event, "precise_y", getattr(event, "y", 0)))
        self._mouse_axes[AXIS_MWHEEL_DX] += dx
        self._mouse_axes[AXIS_MWHEEL_DY] += dy

    def _get_button_state_for_binding(
        self, binding: InputBinding, state_index: int
    ) -> int | bool:
        states = {
            DEVICE_KEYBOARD: self._keyboard_states,
            DEVICE_MOUSE: self._mouse_button_states,
        }.get(binding.device, {})
        return states.get(binding.id, (0, 0, False))[state_index]

    @override
    def pressed(self, action: str) -> int:
        if action in self._disabled_actions:
            return 0
        ret = 0
        for binding in self._bindings.get(action, []):
            if binding.type != TYPE_BUTTON:
                continue
            ret += self._get_button_state_for_binding(binding, 0)
        return ret

    @override
    def released(self, action: str) -> int:
        if action in self._disabled_actions:
            return 0
        ret = 0
        for binding in self._bindings.get(action, []):
            if binding.type != TYPE_BUTTON:
                continue
            ret += self._get_button_state_for_binding(binding, 1)
        return ret

    @override
    def held(self, action: str) -> bool:
        if action in self._disabled_actions:
            return False
        ret = False
        for binding in self._bindings.get(action, []):
            if binding.type != TYPE_BUTTON:
                continue
            ret |= bool(self._get_button_state_for_binding(binding, 2))
        return ret

    @override
    def get_value(self, action: str) -> float:
        if action in self._disabled_actions:
            return 0
        for binding in self._bindings.get(action, []):
            if binding.type == TYPE_AXIS and binding.device == DEVICE_MOUSE:
                return self._mouse_axes[binding.id]
        return 0

    @override
    def get_vector(self, x_action: str, y_action: str) -> tuple[float, float]:
        return (self.get_value(x_action), self.get_value(y_action))

    @override
    def set_map(
        self, binding_map: dict[str, InputBinding | list[InputBinding]]
    ) -> None:
        for action, bindings in binding_map.items():
            self.bind(action, bindings)

    @override
    def bind(self, action: str, bindings: InputBinding | list[InputBinding]) -> None:
        self.unbind(action)
        for binding in self._as_list(bindings):
            self._ensure_subscriptions(binding)
            self._bindings.setdefault(action, []).append(binding)

    @override
    def unbind(self, action: str) -> None:
        if action in self._bindings:
            del self._bindings[action]

    @override
    def get_bindings(self, action: str) -> Iterable[InputBinding]:
        return self._bindings.get(action, []).copy()

    @override
    def disable(self, actions: str | list[str]) -> None:
        a = actions if isinstance(actions, list) else [actions]
        self._disabled_actions.update(a)

    @override
    def enable(self, actions: str | list[str]) -> None:
        a = actions if isinstance(actions, list) else [actions]
        self._disabled_actions.difference_update(a)

    @override
    def clear_edge_inputs(self) -> None:
        for key, (_, _, held) in self._keyboard_states.items():
            self._keyboard_states[key] = (0, 0, held)
        for button, (_, _, held) in self._mouse_button_states.items():
            self._mouse_button_states[button] = (0, 0, held)

    @override
    def clear_relative_axes(self) -> None:
        for axis in AXES_REL:
            self._mouse_axes[axis] = 0
