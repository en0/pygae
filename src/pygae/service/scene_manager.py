from typing import override

from pygame import Surface
from pyioc3.autowire import bind
from pyioc3.interface import Container
from pygae.typing import IGameObject, IMessageBus, ISceneManager
from pygae import event


@bind(ISceneManager, "SINGLETON", lambda e: e)
class SceneManager(ISceneManager):
    def __init__(self, message_bus: IMessageBus, locator: Container) -> None:
        self._bus: IMessageBus = message_bus
        self._locator: Container = locator
        self._pending_scene: IGameObject | None = None
        self._active_scene: IGameObject | None = None

    def _kill_active(self):
        if not self._active_scene:
            return
        self._active_scene.kill()
        self._active_scene.on_unload()
        kill_event = event.make_object_kill_event(self._active_scene)
        self._bus.publish(kill_event)

    def _spawn_pending(self):
        if not self._pending_scene:
            return
        self._pending_scene.set_service_locator(self._locator)
        self._pending_scene.on_load()
        self._pending_scene.spawn()
        spawn_event = event.make_object_spawn_event(self._pending_scene)
        self._bus.publish(spawn_event)

    def _activate_pending(self):
        if not self._pending_scene:
            return
        set_event = event.make_scene_set_event(self._active_scene, self._pending_scene)
        self._active_scene = self._pending_scene
        self._bus.publish(set_event)
        self._pending_scene = None

    def _transition_scene(self):
        self._kill_active()
        self._spawn_pending()
        self._activate_pending()

    @override
    def set_scene(self, scene: IGameObject) -> None:
        self._pending_scene = scene

    @override
    def process_events(self) -> None:
        if self._pending_scene:
            self._transition_scene()
        if self._active_scene:
            self._active_scene.process_events()

    @override
    def fixed_update(self, delta: float) -> None:
        if self._active_scene:
            self._active_scene.fixed_update(delta)

    @override
    def update(self, delta: float) -> None:
        if self._active_scene:
            self._active_scene.update(delta)

    @override
    def render(self, surface: Surface, alpha: float) -> None:
        if self._active_scene:
            self._active_scene.render(surface, alpha)
