from unittest.mock import Mock
from pygae.core.types import IEventGateway, IGameObject
from pygae.core.event import PYGAE_SCENE_SET, PYGAE_OBJECT_SPAWN, PYGAE_OBJECT_KILL
from pygae import ISceneManager


def test_set_scene_records_events(
    scene_manager: ISceneManager, event_gateway: IEventGateway
):
    # Given an initial active scene
    scene_a = Mock(spec=IGameObject)
    scene_b = Mock(spec=IGameObject)
    scene_manager.set_scene(scene_a)
    scene_manager.process_events()  # activate scene A
    event_gateway.pump()

    # When a new scene is set
    scene_manager.set_scene(scene_b)
    scene_manager.process_events()  # process transition

    # Then events should be recorded in the gateway
    events = event_gateway.get()
    types = [e.type for e in events]

    assert PYGAE_OBJECT_KILL in types
    assert PYGAE_OBJECT_SPAWN in types
    assert PYGAE_SCENE_SET in types

    # And the correct scenes are attached
    for e in events:
        try:
            if e.type == PYGAE_OBJECT_KILL:
                assert e.game_object is scene_a
            elif e.type == PYGAE_OBJECT_SPAWN:
                assert e.game_object is scene_b
            elif e.type == PYGAE_SCENE_SET:
                assert e.old_scene is scene_a
                assert e.new_scene is scene_b
        except AttributeError as exc:
            assert False, f"Event missing expected attribute: {exc}"
