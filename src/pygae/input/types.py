from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

TYPE_BUTTON = "button"
TYPE_AXIS = "axis"

DEVICE_KEYBOARD = "keyboard"
DEVICE_MOUSE = "mouse"
DEVICE_JOYSTICK = "joystick"

AXIS_MOUSE_X = 0
AXIS_MOUSE_Y = 1
AXIS_MOUSE_DX = 2
AXIS_MOUSE_DY = 3
AXIS_MWHEEL_DX = 4
AXIS_MWHEEL_DY = 5

TYPES = [TYPE_BUTTON, TYPE_AXIS]
DEVICES = [DEVICE_KEYBOARD, DEVICE_MOUSE]  # , DEVICE_JOYSTICK
AXES = [
    AXIS_MOUSE_X,
    AXIS_MOUSE_Y,
    AXIS_MOUSE_DX,
    AXIS_MOUSE_DY,
    AXIS_MWHEEL_DX,
    AXIS_MWHEEL_DY,
]
AXES_REL = [AXIS_MOUSE_DX, AXIS_MOUSE_DY, AXIS_MWHEEL_DX, AXIS_MWHEEL_DY]


@dataclass(frozen=True)
class InputBinding:
    """
    Represents a binding from a hardware input to an action.

    Attributes:
        type (str): The kind of input: "button" or "axis".
        device (str): The device type: "keyboard", "mouse", "joystick".
        id (int): The identifier of the input. For buttons/axes, use pygame constants or numeric indices.
        joy_id (int | None): joystick ID (for joystick-specific inputs).
        mods (int | None): joystick ID (for joystick-specific inputs).
    """

    type: str
    device: str
    id: int
    mods: int | None = None
    joy_id: int | None = None

    def __post_init__(self):
        # Validate joystick
        if self.device == DEVICE_JOYSTICK:
            raise NotImplementedError("Joystick bindings are not yet implemented.")

        # Validate type
        if self.type not in (TYPES):
            raise ValueError(f"Invalid input binding type: {self.type}")

        # Validate device
        if self.device not in (DEVICES):
            raise ValueError(f"Invalid device type: {self.device}")

        # Validate required fields
        if self.id is None:
            raise ValueError(f"{self.type.capitalize()} bindings must have an 'id'")

        # Validate mouse Axis
        if (
            self.device == DEVICE_MOUSE
            and self.type == TYPE_AXIS
            and self.id not in AXES
        ):
            _axes = ", ".join([str(x) for x in AXES])
            raise ValueError(f"Invalid id for axis: {self.id}. Use one of {_axes}")


class IInputService(ABC):
    """
    Interface for the input service in PyGAE.

    Responsibilities:
        - Maintain the current state of all actions (pressed, released, held, analog value, vector)
        - Allow game code to query actions in a high-level way
        - Support runtime configuration of action-to-input bindings
        - Integrate cleanly with the engine's MessageBus filtered subscription system
    """

    @abstractmethod
    def pressed(self, action: str) -> int:
        """
        Returns the number of times the action was pressed (triggered) since the last fixed_update.

        Non-existant actions are treated as valid but never "pressed".

        Args:
            action (str): The name of the action to query.

        Returns:
            int: Count of presses for this frame/fixed_update step.
        """
        ...

    @abstractmethod
    def released(self, action: str) -> int:
        """
        Returns the number of times the action was released since the last fixed_update.

        Non-existant actions are treated as valid but never "released".

        Args:
            action (str): The name of the action to query.

        Returns:
            int: Count of releases for this frame/fixed_update step.
        """
        ...

    @abstractmethod
    def held(self, action: str) -> bool:
        """
        Returns whether the action is currently held down.

        Non-existant actions are treated as valid but never "held".

        Args:
            action (str): The name of the action to query.

        Returns:
            bool: True if the action is currently held, False otherwise.
        """
        ...

    @abstractmethod
    def get_value(self, action: str) -> float:
        """
        Returns the analog value of the action (e.g., joystick axis).

        For digital buttons, this returns 1.0 if held, 0.0 if not.

        Non-existant actions are treated as valid but always return 0.0

        Args:
            action (str): The name of the action to query.

        Returns:
            float: Current value of the action.
        """
        ...

    @abstractmethod
    def get_vector(self, x_action: str, y_action: str) -> tuple[float, float]:
        """
        Returns a 2D vector combining two actions.

        Non-existant actions are treated as valid but always return 0.0

        Args:
            x_action (str): Action name for the horizontal axis.
            y_action (str): Action name for the vertical axis.

        Returns:
            tuple[float, float]: Combined (x, y) value.
        """
        ...

    @abstractmethod
    def set_map(
        self, binding_map: dict[str, InputBinding | list[InputBinding]]
    ) -> None:
        """
        Sets or Replace the entire set of bindings for all actions.

        All bindings are cleared before the given map is processed.

        Args:
            binding_map (dict): A map of binding arrays.

        Example:
            {
                "jump": [ InputBinding(...) ],
                "fire": [ InputBinding(...) ],
                ...
            }
        """
        ...

    @abstractmethod
    def bind(self, action: str, bindings: InputBinding | list[InputBinding]) -> None:
        """
        Set or replace the bindings for a given action.

        Args:
            action (str): The action name.
            bindings (InputBinding | list): One or more InputBinding objects to associate with the action.
        """
        ...

    @abstractmethod
    def unbind(self, action: str) -> None:
        """
        Remove all bindings associated with an action.

        Args:
            action (str): The action name.
        """
        ...

    @abstractmethod
    def get_bindings(self, action: str) -> Iterable[InputBinding]:
        """
        Get all bindings associated with an action.

        Args:
            action (str): The action name.

        Returns:
            Iterable of InputBinding objects.
        """
        ...

    @abstractmethod
    def disable(self, actions: str | list[str]) -> None:
        """
        Disable one or more actions.

        Disabled actions will maintain their bindings but will not update states.

        Unrecognized actions will be ignored.

        Args:
            actions (str | list[str]): One or more actions to be disabled.
        """
        ...

    @abstractmethod
    def enable(self, actions: str | list[str]) -> None:
        """
        Enable one or more actions.

        Unrecognized actions will be ignored.

        Args:
            actions (str | list[str]): One or more actions to be enabled.
        """
        ...

    @abstractmethod
    def clear_edge_inputs(self) -> None:
        """
        Clear all edge-triggered input states, such as pressed and released counts
        for buttons or keys.

        This should be called once per frame, after all fixed update steps, to ensure
        that edge events fire only once per frame. Persistent state such as held buttons
        or analog values remains unchanged.
        """
        ...

    @abstractmethod
    def clear_relative_axes(self) -> None:
        """
        Clear accumulated relative input values, such as mouse movement deltas
        or scroll wheel offsets.

        This should be called once per frame, after all fixed update steps, to reset
        relative axes for the next frame. Persistent state such as absolute positions
        or held analog values remains unchanged.
        """
        ...
