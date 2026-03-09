from unittest.mock import Mock

from pyioc3.interface import Container
from pygae.typing import IGameObject, ISceneManager


def test_set_scene_allows_transition(scene_manager: ISceneManager):
    # Given an initial active scene
    first_scene = Mock(spec=IGameObject)
    second_scene = Mock(spec=IGameObject)
    scene_manager.set_scene(first_scene)
    scene_manager.process_events()  # activate the first scene

    # When a second scene is set
    scene_manager.set_scene(second_scene)
    scene_manager.process_events()  # process the transition

    # Then the first scene should be killed
    first_scene.kill.assert_called_once()

    # And the second scene should be spawned
    second_scene.spawn.assert_called_once()

    # And process_events should be called on the new active scene
    second_scene.process_events.assert_called_once()


def test_set_scene_queues_transition_without_immediate_activation(
    scene_manager: ISceneManager,
):
    # Given an initial active scene
    first_scene = Mock(spec=IGameObject)
    second_scene = Mock(spec=IGameObject)
    scene_manager.set_scene(first_scene)

    # When a new scene is set, but before process_events is called
    scene_manager.set_scene(second_scene)

    # Then the first scene should not be killed yet
    first_scene.kill.assert_not_called()

    # And the second scene should not be spawned yet
    second_scene.spawn.assert_not_called()

    # And process_events should not have been called on the second scene
    second_scene.process_events.assert_not_called()


def test_process_events_calls_process_events_on_active_scene(
    scene_manager: ISceneManager,
):
    # Given an initial active scene
    scene = Mock(spec=IGameObject)
    scene_manager.set_scene(scene)

    # When calling process_events
    scene_manager.process_events()

    # Then process events is delegated to the current scene.
    scene.process_events.assert_called_once()


def test_update_delegates_to_active_scene(scene_manager: ISceneManager):
    # Given an active scene
    active_scene = Mock(spec=IGameObject)
    scene_manager.set_scene(active_scene)
    scene_manager.process_events()  # activate the scene

    # When update is called
    delta = 0.016
    scene_manager.update(delta)

    # Then the active scene's update should be called with delta
    active_scene.update.assert_called_once_with(delta)


def test_render_delegates_to_active_scene(scene_manager: ISceneManager):
    # Given an active scene
    active_scene = Mock(spec=IGameObject)
    scene_manager.set_scene(active_scene)
    scene_manager.process_events()  # activate the scene

    # When render is called
    surface = Mock()  # can be any pygame Surface or mock
    scene_manager.render(surface, 0.16)

    # Then the active scene's render should be called with the surface
    active_scene.render.assert_called_once_with(surface, 0.16)


def test_methods_do_nothing_when_no_active_scene(scene_manager: ISceneManager):
    # Given no active scene has been set
    # (scene_manager is in its initial state)

    # When process_events, update, and render are called
    try:
        scene_manager.process_events()
        scene_manager.update(0.016)  # delta can be any float
        surface = object()  # mock or dummy surface
        scene_manager.render(surface, 0.16)
    except Exception as e:
        assert False, f"Method raised an exception when no active scene: {e}"

    # Then no exception is raised and the methods complete safely
    # (we're not checking calls here, just safety)


def test_set_service_locator_attached_on_spawn(
    scene_manager: ISceneManager, ioc: Container
):
    # Given a new scene
    scene = Mock(spec=IGameObject)

    # When the scene is set and processed
    scene_manager.set_scene(scene)
    scene_manager.process_events()  # triggers _spawn_pending

    # Then the scene should have received the service locator
    scene.set_service_locator.assert_called_once_with(ioc)


def test_locator_set_before_spawn(scene_manager: ISceneManager):
    # Given a scene and a way to track method invocation order...
    invocation_order = []
    scene = Mock(spec=IGameObject)

    def set_locator(locator):
        invocation_order.append("set_locator")

    scene.set_service_locator.side_effect = set_locator

    def spawn_side_effect():
        invocation_order.append("spawn")

    scene.spawn.side_effect = spawn_side_effect

    # When
    scene_manager.set_scene(scene)
    scene_manager.process_events()

    # then invocation order should set_locator first
    assert ["set_locator", "spawn"] == invocation_order


def test_on_load_is_called_before_spawn(scene_manager: ISceneManager):
    # Given a scene and a way to track method invocation order...
    invocation_order = []
    scene = Mock(spec=IGameObject)

    def load_side_effect():
        invocation_order.append("load")

    scene.on_load.side_effect = load_side_effect

    def spawn_side_effect():
        invocation_order.append("spawn")

    scene.spawn.side_effect = spawn_side_effect

    # When
    scene_manager.set_scene(scene)
    scene_manager.process_events()

    # then invocation order should set_locator first
    assert ["load", "spawn"] == invocation_order


def test_on_unload_is_called_after_kill(scene_manager: ISceneManager):
    # Given an active scene
    invocation_order = []
    scene1 = Mock(spec=IGameObject)
    scene2 = Mock(spec=IGameObject)
    scene_manager.set_scene(scene1)
    scene_manager.process_events()

    def kill_side_effect():
        invocation_order.append("kill")

    scene1.kill.side_effect = kill_side_effect

    def unload_side_effect():
        invocation_order.append("unload")

    scene1.on_unload.side_effect = unload_side_effect

    # When
    scene_manager.set_scene(scene2)
    scene_manager.process_events()

    # then invocation order should set_locator first
    assert ["kill", "unload"] == invocation_order
