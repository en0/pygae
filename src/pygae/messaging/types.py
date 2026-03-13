from abc import ABC, abstractmethod
from pygame.event import Event
from typing import Callable
from uuid import UUID

SubscriptionId = UUID
EventId = int
EventHandler = Callable[[Event], None]
EventHandlerFilter = Callable[[Event], bool]


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
