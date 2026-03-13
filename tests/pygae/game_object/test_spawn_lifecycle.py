from unittest.mock import Mock
from pygae.core.types import IEventGateway, IGameObject
from fakes import SimpleGameObject


def test_adding_child_with_spawn_child_queues_it_in_pending_spawn(
    game_object: SimpleGameObject,
):
    # Given an initialized game object and a child
    child = Mock(spec=IGameObject)

    # when adding a child
    game_object.spawn_child(child)

    # then child is visible in _pending_spawn list
    assert list(game_object._pending_spawn) == [child]


def test_process_events_moves_pending_spawns_into_active_children_and_calls_on_load(
    game_object: SimpleGameObject,
):
    # Given an initialized game object and a child added to the game object
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    # when calling process_events
    game_object.process_events()

    # then child should be in _active_child list
    assert list(game_object._active_children) == [child]
    assert list(game_object._pending_spawn) == []


def test_spawning_children_have_lifecycle_functions_called(
    game_object: SimpleGameObject,
):
    # Given an initialized game object and a child added to the game object
    ivocation_order = []
    child = Mock(spec=IGameObject)
    child.set_service_locator.side_effect = lambda _: ivocation_order.append("locator")
    child.spawn.side_effect = lambda: ivocation_order.append("spawn")
    child.on_load.side_effect = lambda: ivocation_order.append("load")
    game_object.spawn_child(child)

    # when calling process_events
    game_object.process_events()

    # then child should be in _active_child list
    assert ivocation_order == ["locator", "load", "spawn"]


def test_call_to_spawn_sets_alive_state():
    # Given an uninitialized game object
    game_object = SimpleGameObject()

    # when spawn is called
    game_object.spawn()

    # then is_alive() is true
    assert game_object.is_alive()
