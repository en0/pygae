from unittest.mock import Mock
from pygae.core.event import PYGAE_OBJECT_KILL, PYGAE_SCENE_SET, PYGAE_OBJECT_SPAWN
from pygae.core.types import IEventGateway, IGameObject
from pygae import ISceneManager


def test_multiple_rapid_set_scene_calls_only_activates_last(
    scene_manager: ISceneManager,
):
    # Given an initial active scene
    scene_a = Mock(spec=IGameObject)
    scene_b = Mock(spec=IGameObject)
    scene_c = Mock(spec=IGameObject)
    scene_d = Mock(spec=IGameObject)

    # Activate scene A
    scene_manager.set_scene(scene_a)
    scene_manager.process_events()  # scene A becomes active

    # When multiple scenes are set rapidly
    scene_manager.set_scene(scene_b)
    scene_manager.set_scene(scene_c)
    scene_manager.set_scene(scene_d)

    # And process_events is called
    scene_manager.process_events()

    # Then the first scene should be killed
    scene_a.kill.assert_called_once()

    # And only the last scene should be spawned
    scene_b.spawn.assert_not_called()
    scene_c.spawn.assert_not_called()
    scene_d.spawn.assert_called_once()

    # And process_events should be called on the last scene
    scene_b.process_events.assert_not_called()
    scene_c.process_events.assert_not_called()
    scene_d.process_events.assert_called_once()


def test_sequential_set_scene_transitions(scene_manager: ISceneManager):
    # Given an initial active scene
    scene_a = Mock(spec=IGameObject)
    scene_b = Mock(spec=IGameObject)
    scene_c = Mock(spec=IGameObject)

    # Activate scene A
    scene_manager.set_scene(scene_a)
    scene_manager.process_events()  # scene A becomes active

    # When scene B is set
    scene_manager.set_scene(scene_b)
    scene_manager.process_events()  # process transition to B

    # Then scene A should be killed, scene B spawned, and process_events called on B
    scene_a.kill.assert_called_once()
    scene_b.spawn.assert_called_once()
    scene_b.process_events.assert_called_once()

    # When scene C is set
    scene_manager.set_scene(scene_c)
    scene_manager.process_events()  # process transition to C

    # Then scene B should be killed, scene C spawned, and process_events called on C
    scene_b.kill.assert_called_once()
    scene_c.spawn.assert_called_once()
    scene_c.process_events.assert_called_once()


def test_full_scene_lifecycle_order(
    scene_manager: ISceneManager, event_gateway: IEventGateway
):
    # --- Given ---
    # Create two mock scenes
    scene_a = Mock(spec=IGameObject)
    scene_b = Mock(spec=IGameObject)

    # Track invocation order
    invocation_order = []

    # Track lifecycle methods on scene A
    scene_a.kill.side_effect = lambda: invocation_order.append("scene_a.kill")
    scene_a.spawn.side_effect = lambda: invocation_order.append("scene_a.spawn")
    scene_a.process_events.side_effect = lambda: invocation_order.append(
        "scene_a.process_events"
    )
    scene_a.set_service_locator.side_effect = lambda locator: invocation_order.append(
        "scene_a.set_locator"
    )

    # Track lifecycle methods on scene B
    scene_b.kill.side_effect = lambda: invocation_order.append("scene_b.kill")
    scene_b.spawn.side_effect = lambda: invocation_order.append("scene_b.spawn")
    scene_b.process_events.side_effect = lambda: invocation_order.append(
        "scene_b.process_events"
    )
    scene_b.set_service_locator.side_effect = lambda locator: invocation_order.append(
        "scene_b.set_locator"
    )

    # --- When ---
    # Activate first scene
    scene_manager.set_scene(scene_a)
    scene_manager.process_events()
    event_gateway.pump()  # clear initial events

    # Transition to second scene
    scene_manager.set_scene(scene_b)
    scene_manager.process_events()

    # --- Then ---
    # Check that the service locator is set before spawn on scene B
    expected_order = [
        "scene_a.set_locator",  # first scene gets locator
        "scene_a.spawn",  # first scene spawns
        "scene_a.process_events",  # first scene processes events
        "scene_a.kill",  # first scene killed when switching
        "scene_b.set_locator",  # locator attached before spawn
        "scene_b.spawn",  # second scene spawns
        "scene_b.process_events",  # second scene processes events
    ]
    assert invocation_order == expected_order

    # --- And --- check events are published correctly
    events = event_gateway.get()
    event_types = [e.type for e in events]
    # Scene B transition should publish: kill (scene A), spawn (scene B), set (scene B)
    assert PYGAE_OBJECT_KILL in event_types
    assert PYGAE_OBJECT_SPAWN in event_types
    assert PYGAE_SCENE_SET in event_types
