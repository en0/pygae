from unittest.mock import Mock
from pygae.event import PYGAE_OBJECT_KILL
from pygae.typing import IEventGateway, IGameObject
from fakes import SimpleGameObject


def test_kill_sets_is_alive_to_false_and_pending_kill_to_true(
    game_object: SimpleGameObject,
):
    # given a initialized game object

    # when calling kill
    game_object.kill()

    # then is alive and pending kill are set
    assert game_object.is_alive() == False


def test_killed_child_remains_in_active_children_until_process_events(
    game_object: SimpleGameObject, event_gateway: IEventGateway
):
    # given a game object with a spawned child
    child = SimpleGameObject()
    child.on_unload = Mock()
    game_object.spawn_child(child)
    game_object.process_events()

    # when calling kill on child
    child.kill()

    # then child remains in _active_children and on_unload is not yet called
    assert list(game_object._active_children) == [child]
    child.on_unload.assert_not_called()

    # when process events is called
    game_object.process_events()

    # then child is removed from active_children
    assert list(game_object._active_children) == []

    # and unload is called
    child.on_unload.assert_called_once()
