from unittest.mock import Mock

from pygae.core.types import IGameObject
from fakes import SimpleGameObject


def test_get_children_returns_active(game_object: SimpleGameObject):
    children = [
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
    ]

    for child in children:
        game_object.spawn_child(child)

    game_object.process_events()

    assert list(game_object.get_children()) == children


def test_get_children_returns_active_and_pending(game_object: SimpleGameObject):
    children = [
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
    ]

    for child in children:
        game_object.spawn_child(child)

    game_object.process_events()

    more_children = [
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
        Mock(spec=IGameObject),
    ]

    for child in more_children:
        game_object.spawn_child(child)

    assert list(game_object.get_children(True)) == children + more_children
