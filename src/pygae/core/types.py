from abc import ABC, abstractmethod
from collections.abc import Iterable
from pygame import Surface
from pygame.event import Event
from pyioc3.interface import Container
from typing import Callable

EventId = int
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
