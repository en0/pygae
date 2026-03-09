from abc import ABC
from collections import deque
from collections.abc import Iterable
from itertools import chain
from pygame import Surface
from pygame.event import Event
from pyioc3.interface import Container
from typing import override

from pygae.event import (
    make_object_add_event,
    make_object_kill_event,
    make_object_spawn_event,
)
from pygae.helper_mixin import HelperMixin
from pygae.typing import EventHandler, EventId, IGameObject, IMessageBus, SubscriptionId


class GameObject(HelperMixin, IGameObject, ABC):
    """
    Base class for all game objects in the pygae engine.

    GameObjects provide:
    - Hierarchical parent/child relationships
    - Lifecycle management (spawn, kill, process_events, fixed_update, update, render)
    - Event subscription and publishing via a global message bus
    - Optional hooks for pre/post fixed update, update, and render stages
    - Skip flags to control child propagation

    Lifecycle:
        1. Call `spawn_child()` to queue a child for spawning.
        2. On the next `process_events()` call:
            - Pending children are moved to active children and spawned.
            - Dying children are removed and `on_unload()` is called.
            - Queued events are processed in order.
            - Active children have `process_events()` called unless skipped.
        3. Call `fixed_update(delta)` zero or more times to advance the simulation
        using a fixed timestep.
            - Intended for deterministic simulation logic such as physics,
            movement integration, and gameplay state updates.
            - Child objects receive `fixed_update()` unless propagation is skipped.
        4. Call `update(delta)` once per rendered frame.
            - Intended for frame-dependent logic such as animations, UI updates,
            camera adjustments, and other visual effects.
            - All `fixed_update()` calls for the frame will have completed before
            `update()` is invoked.
            - Child objects receive `update()` unless propagation is skipped.
        5. Call `render(surface, alpha)` to render self and optionally propagate to children.

    Notes:
        - Do not call `spawn()` directly on children; always use `spawn_child()`.
        - Event handlers are automatically unsubscribed when the object is killed.
        - Override `_pre_fixed_update`, `_post_fixed_update`, `_pre_update`,
        `_post_update`, `_pre_render`, `_post_render` to hook into the lifecycle
        without breaking child propagation.

    Example:
        from pygame import Surface

        class Player(GameObject):

            def on_load(self) -> None:
                print("Player loaded")

            def _pre_fixed_update(self, delta: float):
                print("Player physics step")

            def _pre_update(self, delta: float):
                print("Player animation logic")

            def _post_render(self, surface: Surface, alpha: float):
                print("Player post-render overlay")
    """

    def __init__(self) -> None:
        self._is_alive: bool = False
        self._skip_child_process_events: bool = False
        self._skip_child_fixed_update: bool = False
        self._skip_child_update: bool = False
        self._skip_child_render: bool = False
        self._pending_spawn: deque[IGameObject] = deque()
        self._active_children: list[IGameObject] = list()
        self._pending_events: deque[Event] = deque()
        self.__service: Container | None = None
        self.__subscriptions: list[SubscriptionId] = list()
        self.__event_handlers: dict[EventId, list[EventHandler]] = dict()

    # Mixin Abstracts
    @property
    @override
    def _service(self) -> Container | None:
        return self.__service

    @property
    @override
    def _subscriptions(self) -> list[SubscriptionId]:
        return self.__subscriptions

    @property
    @override
    def _event_handlers(self) -> dict[EventId, list[EventHandler]]:
        return self.__event_handlers

    @override
    def _enque_event(self, event: Event) -> None:
        self._pending_events.append(event)

    # Core Interface

    @override
    def set_service_locator(self, locator: Container) -> None:
        self.__service = locator

    @override
    def spawn(self) -> None:
        self._is_alive = True

    @override
    def kill(self) -> None:
        self._is_alive = False

        # Unsubscribe from all events
        bus = self.get_service(IMessageBus)
        for sub_id in self._subscriptions:
            bus.unsubscribe(sub_id)

        # Clear internal subscription/event tracking
        self._subscriptions.clear()
        self._event_handlers.clear()
        self._pending_events.clear()

    @override
    def is_alive(self) -> bool:
        return self._is_alive

    @override
    def spawn_child(self, child: "IGameObject") -> None:
        self._pending_spawn.append(child)
        self.publish(make_object_add_event(child))

    @override
    def get_children(self, include_pending: bool = False) -> Iterable[IGameObject]:
        ret = iter(self._active_children)
        if include_pending:
            ret = chain(ret, self._pending_spawn)
        return ret

    @override
    def notify(self, event: Event) -> None:
        self._enque_event(event)

    @override
    def process_events(self) -> None:
        # remove dieing children
        for child in [c for c in self._active_children if not c.is_alive()]:
            self._active_children.remove(child)
            child.on_unload()
            self.publish(make_object_kill_event(child))

        # Spawn pending children
        while self._pending_spawn:
            child = self._pending_spawn.popleft()
            if self._service:
                child.set_service_locator(self._service)
            child.on_load()
            child.spawn()
            self._active_children.append(child)
            self.publish(make_object_spawn_event(child))

        # Process queued events
        while self._pending_events:
            event = self._pending_events.popleft()
            for handler in self._event_handlers.get(event.type, []):
                handler(event)

        # process child events
        if not self._skip_child_process_events:
            for child in self._active_children:
                child.process_events()

    @override
    def fixed_update(self, delta: float) -> None:
        self._pre_fixed_update(delta)
        if not self._skip_child_fixed_update:
            for child in self._active_children:
                child.fixed_update(delta)
        self._post_fixed_update(delta)

    @override
    def update(self, delta: float) -> None:
        self._pre_update(delta)
        if not self._skip_child_update:
            for child in self._active_children:
                child.update(delta)
        self._post_update(delta)

    @override
    def render(self, surface: Surface, alpha: float) -> None:
        self._pre_render(surface, alpha)
        if not self._skip_child_render:
            for child in self._active_children:
                child.render(surface, alpha)
        self._post_render(surface, alpha)

    # Helper Methods
    def skip_child_processing(
        self,
        *,
        process_events: bool | None = None,
        fixed_update: bool | None = None,
        update: bool | None = None,
        render: bool | None = None
    ) -> None:
        """
        Set flags to skip propagation of lifecycle calls to child objects.

        Args:
            process_events (bool | None): If True, children will skip `process_events`.
            fixed_update (bool | None): If True, children will skip `fixed_update`.
            update (bool | None): If True, children will skip `update`.
            render (bool | None): If True, children will skip `render`.

        Notes:
            - Only affects this object's direct children.
            - None leaves the existing behavior unchanged.

        Example:
            # Skip only rendering of children
            game_object.skip_child_processing(render=True)
        """
        if process_events is not None:
            self._skip_child_process_events = process_events
        if fixed_update is not None:
            self._skip_child_fixed_update = fixed_update
        if update is not None:
            self._skip_child_update = update
        if render is not None:
            self._skip_child_render = render

    # Optional overrides for lifecycle hooks
    def _pre_fixed_update(self, delta: float) -> None:
        """
        Optional hook called at the start of `fixed_update()`.

        Args:
            delta (float): The fixed simulation timestep, in seconds.

        Subclasses may override this method to execute logic before
        child objects are updated during the fixed simulation step.
        The engine guarantees that child `fixed_update()` calls will
        occur after this hook.
        """
        _ = delta

    def _post_fixed_update(self, delta: float) -> None:
        """
        Optional hook called at the end of `fixed_update()`.

        Args:
            delta (float): The fixed simulation timestep, in seconds.

        Subclasses may override this method to execute logic after
        all child objects have completed their `fixed_update()` calls.
        Useful for post-processing or resolving state that depends on
        the results of child simulation updates.
        """
        _ = delta

    def _pre_update(self, delta: float) -> None:
        """
        Optional hook called at the start of `update()`.

        Args:
            delta (float): The time elapsed since the last frame, in seconds.

        Subclasses may override this method to execute logic before
        child objects are updated. The engine guarantees that child
        updates will occur after this hook.
        """
        _ = delta

    def _post_update(self, delta: float) -> None:
        """
        Optional hook called at the end of `update()`.

        Args:
            delta (float): The time elapsed since the last frame, in seconds.

        Subclasses may override this method to execute logic after
        all child objects have been updated. Useful for post-processing
        dependent on children.
        """
        _ = delta

    def _pre_render(self, surface: Surface, alpha: float) -> None:
        """
        Optional hook called at the start of `render()`.

        Args:
            surface (Surface): The Pygame surface to draw onto.
            alpha (float): The interpolation factor between the current and next frame.

        Subclasses may override this method to render content before
        child objects are drawn. The engine guarantees that children
        will render after this hook.
        """
        _, _ = surface, alpha

    def _post_render(self, surface: Surface, alpha: float) -> None:
        """
        Optional hook called at the end of `render()`.

        Args:
            surface (Surface): The Pygame surface to draw onto.
            alpha (float): The interpolation factor between the current and next frame.

        Subclasses may override this method to render content after
        all child objects have been drawn. Useful for overlays,
        debugging visuals, or effects that appear on top of children.
        """
        _, _ = surface, alpha
