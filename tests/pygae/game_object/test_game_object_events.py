from pygame.event import Event
from pygae.core.event import PYGAE_OBJECT_ADD, PYGAE_OBJECT_KILL, PYGAE_OBJECT_SPAWN
from pygae.core.types import IEventGateway
from fakes import SimpleGameObject


def test_spawn_kill_and_set_events(
    game_object: SimpleGameObject, event_gateway: IEventGateway
):
    # given a game object and a child
    events: list[Event] = []
    child = SimpleGameObject()

    # when spawing child
    game_object.spawn_child(child)

    # then an add event is raised
    events.extend(event_gateway.get())
    assert PYGAE_OBJECT_ADD in [e.type for e in events]

    # when calling process events
    game_object.process_events()

    # then an spawn event is raised
    events.extend(event_gateway.get())
    assert PYGAE_OBJECT_SPAWN in [e.type for e in events]

    # when calling kill on child
    child.kill()

    # when process events is called
    game_object.process_events()

    # then a kill event is raised
    events.extend(event_gateway.get())
    assert PYGAE_OBJECT_KILL in [e.type for e in events]

    # Then all events should hold references to child
    for e in events:
        if e.type == PYGAE_OBJECT_ADD:
            assert e.game_object == child
        elif e.type == PYGAE_OBJECT_SPAWN:
            assert e.game_object == child
        elif e.type == PYGAE_OBJECT_KILL:
            assert e.game_object == child
