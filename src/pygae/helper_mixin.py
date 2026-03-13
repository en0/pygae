from abc import ABC, abstractmethod
from typing import TypeVar

from pygame import mouse
from pygae.typing import IGameObject
from pygae.value_object.input_binding import (
    AXIS_MOUSE_X,
    AXIS_MOUSE_Y,
    AXIS_MOUSE_DX,
    AXIS_MOUSE_DY,
    DEVICE_KEYBOARD,
    DEVICE_MOUSE,
    TYPE_AXIS,
    TYPE_BUTTON,
)
from pygame.event import Event
from pyioc3.interface import Container
from pygae.typing import (
    EventHandler,
    EventId,
    IMessageBus,
    InputBinding,
    SubscriptionId,
    IInputService,
    ISceneManager,
)


SERVICE_T = TypeVar("SERVICE_T", bound=object)


class HelperMixin(ABC):
    def get_service(self, interface: type[SERVICE_T]) -> SERVICE_T:
        """
        Retrieve a service instance from the object's service locator.

        Args:
            interface (type): The service interface or class to retrieve.

        Returns:
            SERVICE_T: An instance of the requested service.

        Raises:
            RuntimeError: If the service locator has not been set on this object.

        Example:
            bus = game_object.get_service(IMessageBus)
        """
        if self._service:
            return self._service.get(interface)
        raise RuntimeError(
            "Service locator not set! Make sure set_locator is called on object."
        )

    def subscribe(self, event_id: EventId, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event for this object.

        The handler will be called when the event occurs. The subscription
        is automatically tracked and removed when the object is killed.

        Args:
            event_id (EventId): The ID of the event to subscribe to.
            handler (EventHandler): The function to handle the event.

        Example:
            def on_hit(event):
                print("Hit!", event.damage)
            game_object.subscribe(HIT_EVENT, on_hit)
        """
        bus = self.get_service(IMessageBus)
        sub_id = bus.subscribe(event_id, self._enque_event)
        self._subscriptions.append(sub_id)
        self._event_handlers.setdefault(event_id, []).append(handler)

    def publish(self, event: Event) -> None:
        """
        Publish an event to the global message bus.

        Args:
            event (Event): The event to publish.

        Example:
            game_object.publish(pygame.event.Event(PYGAE_SCENE_KILL, scene=self))
        """
        bus = self.get_service(IMessageBus)
        bus.publish(event)

    def set_scene(self, scene: IGameObject) -> None:
        """
        Queue a new scene to become the active scene.

        This method delegates to the engine's scene manager. The scene
        transition does not happen immediately; it will be processed
        on the next call to the engine's event loop.

        Args:
            scene (IGameObject): The scene object to set as active.

        Example:
            title_scene = TitleScene()
            game.set_scene(title_scene)
        """
        scene_manager = self.get_service(ISceneManager)
        scene_manager.set_scene(scene)

    def disable_action(self, action: str) -> None:
        """
        Disable an input action.

        When disabled, the action will no longer report input states
        such as pressed, released, or held until it is re-enabled.

        Args:
            action (str): The name of the action to disable.

        Example:
            game.disable_action("jump")
        """
        input = self.get_service(IInputService)
        input.disable(action)

    def enable_action(self, action: str) -> None:
        """
        Enable an input action.

        Re-enables an action that was previously disabled so that
        it can again report input states.

        Args:
            action (str): The name of the action to enable.

        Example:
            game.enable_action("jump")
        """
        input = self.get_service(IInputService)
        input.enable(action)

    def bind_keyboard_button(self, action: str, key: int) -> None:
        """
        Bind a keyboard key to an input action.

        This creates a button binding that triggers the specified
        action when the given keyboard key is pressed.

        Args:
            action (str): The name of the action to bind.
            key (int): The keyboard key code to associate with the action.

        Example:
            game.bind_keyboard_button("jump", KEY_SPACE)
        """
        input = self.get_service(IInputService)
        binding = InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, id=key)
        input.bind(action, binding)

    def bind_mouse_button(self, action: str, key: int) -> None:
        """
        Bind a mouse button to an input action.

        This creates a button binding that triggers the specified
        action when the given mouse button is pressed.

        Args:
            action (str): The name of the action to bind.
            key (int): The mouse button identifier.

        Example:
            game.bind_mouse_button("shoot", 1)
        """
        input = self.get_service(IInputService)
        binding = InputBinding(TYPE_BUTTON, DEVICE_MOUSE, id=key)
        input.bind(action, binding)

    def bind_mouse_xy(self, x_action: str, y_action: str) -> None:
        """
        Bind mouse position axes to input actions.

        This maps the mouse's absolute X and Y position to two
        separate input actions.

        Args:
            x_action (str): The action that receives the mouse X value.
            y_action (str): The action that receives the mouse Y value.

        Example:
            game.bind_mouse_xy("mouse_x", "mouse_y")
        """
        input = self.get_service(IInputService)
        x_binding = InputBinding(TYPE_AXIS, DEVICE_MOUSE, id=AXIS_MOUSE_X)
        y_binding = InputBinding(TYPE_AXIS, DEVICE_MOUSE, id=AXIS_MOUSE_Y)
        input.bind(x_action, x_binding)
        input.bind(y_action, y_binding)

    def bind_mouse_dxy(self, dx_action: str, dy_action: str) -> None:
        """
        Bind mouse movement delta axes to input actions.

        This maps the mouse's relative movement (delta X and delta Y)
        to two separate input actions.

        Args:
            dx_action (str): The action that receives horizontal mouse movement.
            dy_action (str): The action that receives vertical mouse movement.

        Example:
            game.bind_mouse_dxy("look_x", "look_y")
        """
        input = self.get_service(IInputService)
        dx_binding = InputBinding(TYPE_AXIS, DEVICE_MOUSE, id=AXIS_MOUSE_DX)
        dy_binding = InputBinding(TYPE_AXIS, DEVICE_MOUSE, id=AXIS_MOUSE_DY)
        input.bind(dx_action, dx_binding)
        input.bind(dy_action, dy_binding)

    def unbind_action(self, action: str) -> None:
        """
        Remove all input bindings associated with an action.

        After unbinding, the action will no longer receive input
        from any devices until new bindings are added.

        Args:
            action (str): The name of the action to unbind.

        Example:
            game.unbind_action("jump")
        """
        input = self.get_service(IInputService)
        input.unbind(action)

    def input_pressed(self, action: str) -> int:
        """
        Get the number of times an action was pressed during the current frame.

        A press is recorded whenever the input bound to the action transitions
        from an inactive state to an active state. Multiple presses can occur
        within a single frame if the input device generates multiple transitions.

        Args:
            action (str): The action to query.

        Returns:
            int: The number of press events recorded for the action during
            the current frame (0..n).

        Example:
            if game.input_pressed("jump") > 0:
                player.jump()

            # Handle multiple presses in a single frame
            presses = game.input_pressed("fire")
            for _ in range(presses):
                player.shoot()
        """
        input = self.get_service(IInputService)
        return input.pressed(action)

    def input_released(self, action: str) -> int:
        """
        Get the number of times an action was released during the current frame.

        A release is recorded whenever the input bound to the action transitions
        from an active state to an inactive state. Multiple releases can occur
        within a single frame if the input device generates multiple transitions.

        Args:
            action (str): The action to query.

        Returns:
            int: The number of release events recorded for the action during
            the current frame (0..n).

        Example:
            if game.input_released("charge") > 0:
                player.stop_charging()
        """
        input = self.get_service(IInputService)
        return input.released(action)

    def input_held(self, action: str) -> bool:
        """
        Check if an action is currently being held.

        Args:
            action (str): The action to query.

        Returns:
            bool: True, if the action is currently active,
                  otherwise False.

        Example:
            if game.input_held("move_left"):
                player.move_left()
        """
        input = self.get_service(IInputService)
        return input.held(action)

    def get_input_vector(self, action_x: str, action_y: str) -> tuple[float, float]:
        """
        Retrieve a 2D vector composed of two input actions.

        This is commonly used for movement input where one
        action represents horizontal input and the other
        represents vertical input.

        Args:
            action_x (str): The action providing the X component.
            action_y (str): The action providing the Y component.

        Returns:
            tuple[float, float]: A vector containing the combined input values.

        Example:
            movement = game.get_input_vector("move_x", "move_y")
            player.move(movement)
        """
        input = self.get_service(IInputService)
        return input.get_vector(action_x, action_y)

    def hide_mouse(self) -> None:
        """
        Hide the mouse.
        """
        _ = mouse.set_visible(False)

    def show_mouse(self) -> None:
        """
        Unhide the mouse.
        """
        _ = mouse.set_visible(True)

    @property
    @abstractmethod
    def _service(self) -> Container | None:
        ...

    @property
    @abstractmethod
    def _subscriptions(self) -> list[SubscriptionId]:
        ...

    @property
    @abstractmethod
    def _event_handlers(self) -> dict[EventId, list[EventHandler]]:
        ...

    @abstractmethod
    def _enque_event(self, event: Event) -> None:
        ...
