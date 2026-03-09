from unittest.mock import Mock

from pygame import Surface
from pygae.typing import IGameObject
from fakes import SimpleGameObject


def test_process_events_propagates_to_children(game_object: SimpleGameObject):
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.process_events()

    child.process_events.assert_called_once()


def test_update_propogates_to_children(game_object: SimpleGameObject):
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.process_events()
    game_object.update(42)

    child.update.assert_called_once_with(42)


def test_render_propogates_to_children(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.render.assert_called_once_with(surface, 0.16)


def test_process_event_skip_flags_set_to_false(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.skip_child_processing(
        process_events=False,
        update=False,
        render=False,
    )

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.process_events.assert_called_once()
    child.update.assert_called_once_with(42)
    child.render.assert_called_once_with(surface, 0.16)


def test_process_event_skip_flags(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.skip_child_processing(
        process_events=True,
        update=False,
        render=False,
    )

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.process_events.assert_not_called()
    child.update.assert_called_once_with(42)
    child.render.assert_called_once_with(surface, 0.16)


def test_update_skip_flags(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.skip_child_processing(
        process_events=False,
        update=True,
        render=False,
    )

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.process_events.assert_called_once()
    child.update.assert_not_called()
    child.render.assert_called_once_with(surface, 0.16)


def test_render_skip_flags(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.skip_child_processing(
        process_events=False,
        update=False,
        render=True,
    )

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.process_events.assert_called_once()
    child.update.assert_called_once_with(42)
    child.render.assert_not_called()


def test_skip_all(game_object: SimpleGameObject):
    surface = Mock(spec=Surface)
    child = Mock(spec=IGameObject)
    game_object.spawn_child(child)

    game_object.skip_child_processing(
        process_events=True,
        update=True,
        render=True,
    )

    game_object.process_events()
    game_object.update(42)
    game_object.render(surface, 0.16)

    child.process_events.assert_not_called()
    child.update.assert_not_called()
    child.render.assert_not_called()
