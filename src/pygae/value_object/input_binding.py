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
