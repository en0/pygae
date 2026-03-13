from abc import ABC, abstractmethod
from collections.abc import Iterable
from pygame import Surface
from pygame.event import Event
from pyioc3.interface import Container
from typing import Callable
from uuid import UUID

from pygae.value_object import InputBinding


SubscriptionId = UUID
EventId = int
EventHandler = Callable[[Event], None]
EventHandlerFilter = Callable[[Event], bool]
EventConstructor = Callable[[Event], Event]
EventFilter = Callable[[Event], bool]


class IEventGateway(ABC):
    """
    Interface to internal pygame event bus.
    """

    @abstractmethod
    def get(self) -> list[Event]:
        """
        Get pending events.

        Returns:
            A list of events
        """
        ...

    @abstractmethod
    def post(self, event: Event) -> None:
        """
        Post an event

        Args:
            event (Event): The event to post
        """
        ...

    @abstractmethod
    def pump(self) -> None:
        """
        Discard pending events
        """
        ...


class IGameObject(ABC):
    """
    Interface representing a Game Object.
    A GameObject is the fundamental unit of behavior and state.
    """

    @abstractmethod
    def set_service_locator(self, locator: Container) -> None:
        """
        Sets the service locator for the game object.

        This method allows the game object to access various services
        required for its operation.

        Args:
            locator (Container): The service locator that provides access.
        """
        ...

    @abstractmethod
    def spawn(self) -> None:
        """
        Initializes and activates the game object in the game world.

        This method is responsible for spawning the object with its
        initial properties and adding it to game systems.
        """
        ...

    @abstractmethod
    def kill(self) -> None:
        """
        Deactivates and disposes of the game object.

        This method is called when the game object needs to be removed
        from the game world, triggering any cleanup operations as necessary.

        Calling this method will cascade through children.
        """
        ...

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Indicates whether the game object is still active or not.

        Returns:
            bool: True if the object is alive. Else, False.
        """
        ...

    @abstractmethod
    def spawn_child(self, child: "IGameObject") -> None:
        """
        Add the given object as a child to this object.

        The child will be spawned at the beginning of the next call to
        process_events.

        The child becomes part of this object's hierarchy and will
        automatically participate in updates, render, and event
        processing.

        Args:
            child (IGameObject): The IGameObject to attach.
        """
        ...

    @abstractmethod
    def get_children(self, include_pending: bool = False) -> Iterable["IGameObject"]:
        """
        Retrives child objects of this object.

        Args:
            include_pending (bool): Include objects pending spawn

        Returns:
            Iterable of IGameObjects that directly belong to this
            object.
        """
        ...

    @abstractmethod
    def notify(self, event: Event) -> None:
        """
        Publishes an event to this game object.

        This method allows the game object to receive and process events
        that are relevant to its state or behavior.

        Args:
            event (Event): The event to be published to the game object.
        """
        ...

    @abstractmethod
    def process_events(self) -> None:
        """
        Process pending events for this game object.

        This method causes the game object to invoke handlers for all
        pending events.
        """
        ...

    @abstractmethod
    def fixed_update(self, delta: float) -> None:
        """
        Advance the game object's simulation state.

        This method is called after `process_events` and may execute
        zero or more times per rendered frame using a fixed timestep.
        It should contain deterministic simulation logic such as physics,
        movement integration, and gameplay state updates that benefit from
        stable, fixed-duration steps.

        Args:
            delta (float): The fixed simulation timestep in fractional seconds.
        """
        ...

    @abstractmethod
    def update(self, delta: float) -> None:
        """
        Perform per-frame updates for the game object.

        This method is called after `process_events` and after all
        `fixed_update` calls for the current frame have completed.
        It executes exactly once per rendered frame and is intended for
        frame-dependent logic such as animations, camera adjustments,
        UI updates, or other visual effects.

        Args:
            delta (float): The elapsed real time since the previous frame,
                in fractional seconds.
        """
        ...

    @abstractmethod
    def render(self, surface: Surface, alpha: float) -> None:
        """
        Render the current game object to the given surface.

        This method is called after update.

        Args:
            surface (Surface): A pygame surface.
            alpha (float): Interpolation factor between current and next frame.
        """
        ...

    def on_load(self) -> None:
        """
        Called during the loading phase of this object.

        This method is called before spawn() and can be used
        to set initial state, allocate resources, create sub-components.
        """
        ...

    def on_unload(self) -> None:
        """
        Called after the object at the end of the objects lifcycle.

        This method is called at the cleanup state of a killed object.
        This method can be used to clean up allocated resource.
        """
        ...


class IMessageBus(ABC):
    """
    Interface representing a messaging bus for handling events and subscriptions.
    This serves as a central hub for communication between different components
    of the game.
    """

    @abstractmethod
    def subscribe(
        self,
        event_id: EventId,
        handler: EventHandler,
        filter: EventHandlerFilter | None = None,
    ) -> SubscriptionId:
        """
        Subscribes a handler to a specific event type.

        This method associates an event handler with a particular event ID,
        allowing the handler to be notified when the event occurs.

        Args:
            event_id (EventId): The ID of the event to subscribe to.
            handler (EventHandler): The function or callable that will handle the event.
            filter (Callable): An optional filter predicate.

        Returns:
            SubscriptionId: A unique identifier for the subscription.
        """
        ...

    @abstractmethod
    def unsubscribe(self, subscription_id: SubscriptionId) -> None:
        """
        Unsubscribes a handler from receiving updates for an event.

        This method removes the subscription associated with the given
        subscription ID, preventing the handler from receiving any further
        notifications.

        Args:
            subscription_id (SubscriptionId): The unique identifier of the subscription
                                              to be removed.
        """
        ...

    @abstractmethod
    def publish(self, event: Event) -> None:
        """
        Publishes an event to the message bus.

        This method broadcasts an event to all subscribed handlers,
        allowing them to process the event and act accordingly.

        Args:
            event (Event): The event to be published.
        """
        ...

    @abstractmethod
    def process_events(self) -> None:
        """
        Collect events and updates subscribers.

        This method should be called to ensure that the event bus
        processes any queued events and notifies the relevant subscribers
        of those events.
        """
        ...


class ISceneManager(ABC):
    """
    This interface provides a way to process scenes and allow for scene transitions.
    """

    @abstractmethod
    def set_scene(self, scene: IGameObject) -> None:
        """
        Replace the active scene with the given scene.

        This method does not immediately change the active scene. The
        transition is queued and will be processed on the next call
        to process_events.

        This method does not affect the scene chain.

        Args:
            scene (IGameObject): The scene to replace the current active scene.
        """
        ...

    @abstractmethod
    def process_events(self) -> None:
        """
        Process pending events for the active scene.

        This method takes the following actions:
            - Check for pending scene transition.
            - If a scene transition is pending:
                - Kill the current scene.
                - Spawn the target scene.
                - Set target as the active scene.
            - Call process_events on the active scene.
        """
        ...

    @abstractmethod
    def fixed_update(self, delta: float) -> None:
        """
        Call fixed-update on the active scene.

        Args:
            delta (float): The fixed simulation timestep in fractional seconds.
        """
        ...

    @abstractmethod
    def update(self, delta: float) -> None:
        """
        Call update on the active scene.

        Args:
            delta (float): Duration of the last frame in fractional seconds.
        """
        ...

    @abstractmethod
    def render(self, surface: Surface, alpha: float) -> None:
        """
        Call render on the active scene.

        Args:
            surface (Surface): A pygame surface.
            alpha (float): Interpolation factor between current and next frame.
        """
        ...


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
