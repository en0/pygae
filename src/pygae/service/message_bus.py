from typing import override
from uuid import uuid4
from pyioc3.autowire import bind
from pygame.event import (
    Event,
    get as _get_events,
    post as _post_event,
    pump as _pump_event,
)

from pygae.typing import (
    EventHandlerFilter,
    IEventGateway,
    IMessageBus,
    SubscriptionId,
    EventId,
    EventHandler,
)


@bind(IEventGateway, "SINGLETON", lambda e: e)
class PygameEventGateway(IEventGateway):
    @override
    def get(self) -> list[Event]:
        return _get_events()

    @override
    def post(self, event: Event) -> None:
        _ = _post_event(event)

    @override
    def pump(self) -> None:
        _pump_event()


@bind(IMessageBus, "SINGLETON", lambda e: e)
class MessageBus(IMessageBus):
    def __init__(self, gw: IEventGateway):
        self._gw: IEventGateway = gw
        self._subscriptions: dict[SubscriptionId, tuple[EventId, EventHandler]] = dict()
        self._handlers: dict[EventId, list[EventHandler]] = dict()

    def _make_filtered_handler(
        self, filter: EventHandlerFilter, handler: EventHandler
    ) -> EventHandler:
        def _wrapped(event: Event):
            if filter(event):
                handler(event)

        return _wrapped

    @override
    def subscribe(
        self,
        event_id: EventId,
        handler: EventHandler,
        filter: EventHandlerFilter | None = None,
    ) -> SubscriptionId:
        _handler = self._make_filtered_handler(filter, handler) if filter else handler
        subid = uuid4()
        self._subscriptions[subid] = (event_id, _handler)
        self._handlers.setdefault(event_id, []).append(_handler)
        return subid

    @override
    def unsubscribe(self, subscription_id: SubscriptionId) -> None:
        if subscription_id in self._subscriptions:
            event_id, handler = self._subscriptions[subscription_id]
            del self._subscriptions[subscription_id]
            self._handlers[event_id].remove(handler)

    @override
    def publish(self, event: Event) -> None:
        self._gw.post(event)

    @override
    def process_events(self) -> None:
        for event in self._gw.get():
            for handler in self._handlers.get(event.type, []):
                handler(event)
