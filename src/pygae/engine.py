import pygame

from sys import stderr
from typing import override
from abc import ABC, abstractmethod
from collections import deque
from pygame.event import Event
from pygame.time import Clock
from pyioc3.autowire import AutoWireContainerBuilder
from pyioc3.interface import Container

from pygae.event import make_quit_event
from pygae.helper_mixin import HelperMixin
from pygae.typing import (
    EventHandler,
    EventId,
    IInputService,
    IMessageBus,
    ISceneManager,
    SubscriptionId,
)


class GameEngine(HelperMixin, ABC):
    """
    Base class for building pygae game or simulation engine.

    Provides a structured main loop with event processing, update, and render cycles,
    as well as hooks for client code to extend behavior at key points. Handles integration
    with the scene manager, message bus, and a service locator.

    Class Members:
        SCREEN_SIZE (tuple[int, int]): Default window size for the game surface (width, height).
        MAX_FRAMERATE (int | float): Target frames per second for the main loop. Default: 144
        FIXED_DT (float): Fixed rate for calls to update_fixed. Default: 1/60
        MAX_FRAME_TIME (float): Maximum frame duration used to clamp delta time. Default 0.25

    Main responsibilities:
        - Initialize Pygame and services
        - Run a stable main loop with event processing, updates, and rendering
        - Provide lifecycle hooks (_pre_frame, _post_frame, _on_load, _on_unload)
        - Allow client code to enqueue events or quit the engine gracefully

    Example:
        from typing import override
        from pygae.engine import GameEngine

        class MyGame(GameEngine):

            SCREEN_SIZE: tuple[int, int] = (1024, 768)
            MAX_FRAMERATE: int = 144

            @override
            def _on_load(self) -> None:
                print("Game initializing...")
                # Set up scenes, services, initial game objects here
                # self.set_scene(TitleScene())

            @override
            def _pre_frame(self) -> None:
                # Optional: logic to execute at the start of every frame
                pass

            @override
            def _post_frame(self) -> None:
                # Optional: logic to execute at the end of every frame
                pass

            @override
            def _on_unload(self) -> None:
                # Optional: cleanup resources before quitting
                print("Game shutting down...")


        if __name__ == "__main__":
            game = MyGame()
            game.run()
    """

    SCREEN_SIZE: tuple[int, int] = (800, 600)
    FIXED_DT: float = 1 / 60
    MAX_FRAMERATE: int = 144
    MAX_FRAME_TIME: float = 0.25

    def __init__(
        self,
        *,
        service_scan_path: list[str] | None = None,
        services: dict[type, type] | None = None,
    ):
        modules: list[str] = ["pygae.service"]
        if service_scan_path:
            modules.extend(service_scan_path)
        srvloc_ioc = AutoWireContainerBuilder(modules)
        for anno, impl in (services or {}).items():
            srvloc_ioc.bind(anno, impl, "SINGLETON")
        self.__service: Container | None = srvloc_ioc.build()
        self.__subscriptions: list[SubscriptionId] = list()
        self.__event_handlers: dict[EventId, list[EventHandler]] = dict()
        self._is_running: bool = False
        self._watch_dog_frame_alert: bool = False
        self._pending_events: deque[Event] = deque()
        self._bus: IMessageBus = self.__service.get(IMessageBus)
        self._scene: ISceneManager = self.__service.get(ISceneManager)
        self._input: IInputService = self.__service.get(IInputService)

    # Mixin Abstracts
    @property
    @override
    def _service(self) -> Container | None:
        return self.__service

    @property
    @override
    def _subscriptions(self) -> list[SubscriptionId]:
        return self.__subscriptions

    @property
    @override
    def _event_handlers(self) -> dict[EventId, list[EventHandler]]:
        return self.__event_handlers

    @override
    def _enque_event(self, event: Event) -> None:
        self._pending_events.append(event)

    # Core functionality

    def _get_ticks(self) -> float:
        return pygame.time.get_ticks() / 1000.0

    def _set_watch_dog_frame_alert(self, alarm_state: bool, frame_time: float):
        if alarm_state and not self._watch_dog_frame_alert:
            print(
                f"Watchdog: frame time exceeded MAX_FRAME_TIME ({frame_time:.3f}s)",
                file=stderr,
            )
        self._watch_dog_frame_alert = alarm_state

    def _quit_handler(self, _: Event):
        self._is_running = False

    def _load(self) -> None:
        _ = pygame.init()
        self._on_load()
        self.subscribe(pygame.QUIT, self._quit_handler)

    def _unload(self) -> None:
        for sub_id in self._subscriptions:
            self._bus.unsubscribe(sub_id)
        self._on_unload()
        pygame.quit()

    def _process_events(self) -> None:
        self._bus.process_events()
        while self._pending_events:
            event = self._pending_events.popleft()
            for handler in self._event_handlers.get(event.type, []):
                handler(event)
        self._scene.process_events()

    def _fixed_update(self, delta: float) -> None:
        self._scene.fixed_update(delta)
        self._input.clear_edge_inputs()

    def _update(self, delta: float) -> None:
        self._input.clear_relative_axes()
        self._scene.update(delta)

    def _render(self, surface: pygame.Surface, alpha: float) -> None:
        self._scene.render(surface, alpha)
        pygame.display.flip()

    def quit(self) -> None:
        """
        Request the engine to stop running.

        This method publishes a quit event into the global event bus,
        which will be handled by the engine to exit the main loop
        gracefully.

        Notes:
            - Can be called by client code to stop the game.
            - Internally, the engine listens for this event and sets `_is_running` to False during the next frame.
            - The current frame runs to completion before `_is_running` is evaluated.
        """
        self.publish(make_quit_event())

    def run(self):
        """
        Start the main game loop.

        This method initializes the engine, prepares the scene and services,
        and enters the main loop where events are processed, the simulation
        advances, and rendering occurs. The loop continues until the engine
        is stopped (e.g., via a quit event).

        Lifecycle order:
            1. `_load()` is called before the loop starts.
            2. For each frame:
                a. `_pre_frame()` is called.
                b. `_process_events()` processes queued events.
                c. `_fixed_update(delta)` is called zero or more times using
                a fixed timestep (`FIXED_DT`) to advance the simulation.
                d. `_update(delta)` is called once with the real frame time.
                e. `_render(surface, alpha)` is called once to render the
                current frame. The `alpha` value represents the fraction
                of the next simulation step and may be used for interpolation.
                f. `_post_frame()` is called after rendering.
            3. `_unload()` is called after the loop exits.

        Timing model:
            - Simulation logic runs at a fixed timestep (`FIXED_DT`) to ensure
            stable and deterministic updates.
            - Frame updates and rendering occur once per frame and may run
            at a variable rate, optionally capped by `MAX_FRAMERATE`.
            - Large frame delays are clamped by `MAX_FRAME_TIME` to prevent
            excessive simulation catch-up.

        Notes:
            - Clients should not override this method. Use the hooks instead.
        """
        self._load()
        self._is_running = True
        surface: pygame.Surface = self._get_root_surface()
        clock = Clock()
        accumulator = 0.0
        prev_time = self._get_ticks()
        while self._is_running:
            now = self._get_ticks()
            frame_time = now - prev_time
            prev_time = now
            self._set_watch_dog_frame_alert(
                frame_time > self.MAX_FRAME_TIME, frame_time
            )
            frame_time = min(frame_time, self.MAX_FRAME_TIME)
            accumulator += frame_time
            self._pre_frame()
            self._process_events()
            while accumulator >= self.FIXED_DT:
                self._fixed_update(self.FIXED_DT)
                accumulator -= self.FIXED_DT
            self._update(frame_time)
            alpha = accumulator / self.FIXED_DT
            self._render(surface, alpha)
            self._post_frame()
            _ = clock.tick(self.MAX_FRAMERATE)
        self._unload()

    # Optional Lifecycle hooks

    def _get_root_surface(self) -> pygame.Surface:
        """
        Create and return the root Pygame display surface.

        Returns:
            pygame.Surface: The main drawing surface for the game.

        Notes:
            - Called internally by the engine during run().
            - Can be overridden by subclasses to customize the display mode (e.g., fullscreen, different resolution).
            - You can adust the screen size by setting self.SCREEN_SIZE before this method is called.
        """
        return pygame.display.set_mode(self.SCREEN_SIZE)

    def _pre_frame(self) -> None:
        """
        Optional hook called at the start of each frame.

        Subclasses may override this to execute logic before event processing,
        update, and rendering for the current frame. Useful for debugging,
        logging, or temporary logic during development.

        Notes:
            - Called internally by the engine.
            - does not affect frame lifecycle unless overridden.
        """
        ...

    def _post_frame(self) -> None:
        """
        Optional hook called at the end of each frame.

        Subclasses may override this to execute logic after event processing,
        update, and rendering for the current frame. Useful for cleanup,
        logging, or temporary post-frame logic.

        Notes:
            - Called internally by the engine.
            - does not affect frame lifecycle unless overridden.
        """
        ...

    def _on_unload(self) -> None:
        """
        Optional hook called when the engine is shutting down.

        Subclasses may override this to clean up resources, save state,
        or perform other tasks before Pygame quits.

        Notes:
            - Called internally after the main loop exits.
            - Subclasses should not call this directly.
        """
        ...

    # Required Lifecycle hooks

    @abstractmethod
    def _on_load(self) -> None:
        """
        Required hook called when the engine initializes.

        Subclasses **must** implement this method to set up game-specific
        state, initialize services, or create the initial scene.

        Notes:
            - Called internally before the main loop starts.
            - Should not call run() or other lifecycle methods directly.
        """
        ...
