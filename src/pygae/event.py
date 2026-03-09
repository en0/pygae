from pygame import USEREVENT, QUIT
from pygame.event import Event

from pygae.typing import IGameObject

PYGAE_SCENE_SET = USEREVENT + 10_000
PYGAE_OBJECT_ADD = USEREVENT + 20_000
PYGAE_OBJECT_SPAWN = USEREVENT + 30_000
PYGAE_OBJECT_KILL = USEREVENT + 40_000


def make_scene_set_event(
    old_scene: IGameObject | None, new_scene: IGameObject
) -> Event:
    return Event(PYGAE_SCENE_SET, old_scene=old_scene, new_scene=new_scene)


def make_object_add_event(game_object: IGameObject) -> Event:
    return Event(PYGAE_OBJECT_ADD, game_object=game_object)


def make_object_spawn_event(game_object: IGameObject) -> Event:
    return Event(PYGAE_OBJECT_SPAWN, game_object=game_object)


def make_object_kill_event(game_object: IGameObject) -> Event:
    return Event(PYGAE_OBJECT_KILL, game_object=game_object)


def make_quit_event() -> Event:
    return Event(QUIT)
