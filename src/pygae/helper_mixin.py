from abc import ABC, abstractmethod
from typing import TypeVar
from pygame.event import Event
from pyioc3.interface import Container
from pygae.typing import EventHandler, EventId, IMessageBus, SubscriptionId


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
