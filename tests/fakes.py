from typing import final, override
from pygame.event import Event

from pygae.game_object import GameObject
from pygae.typing import IEventGateway


@final
class EventQueueFake(IEventGateway):
    def __init__(self):
        self._q: list[Event] = list()

    @override
    def pump(self):
        self._q.clear()

    @override
    def get(self) -> list[Event]:
        ret = self._q.copy()
        self.pump()
        return ret

    @override
    def post(self, event: Event) -> None:
        self._q.append(event)


class SimpleGameObject(GameObject):
    ...
