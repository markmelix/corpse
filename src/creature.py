import esper
import utils
import pygame

from typing import Optional
from dataclasses import dataclass as component


@component
class Creature:
    pass


@component
class Health:
    value: float = 100
    max: float = 100


@component
class DeadMarker:
    pass


@component
class Damage:
    value: float


@component
class DamagedMarker:
    pass


@component
class DamageLocker:
    delay: int
    _delay: Optional[int] = None


@component
class DamageLock:
    pass


@component
class DamageRequest:
    sender: int
    reciever: int
    damage: float


class DamageDelayingProcessor(esper.Processor):
    def process(self, dt=None, **_):
        for ent, (blocker, _) in self.world.get_components(DamageLocker, DamageLock):
            if not blocker._delay:
                blocker._delay = blocker.delay
                continue

            if blocker._delay > 0:
                blocker._delay -= dt
            else:
                self.world.remove_component(ent, DamageLock)
                blocker._delay = blocker.delay


class DamageMakingProcessor(esper.Processor):
    def process(self, **_):
        for ent, req in self.world.get_component(DamageRequest):
            self.world.remove_component(ent, DamageRequest)

            if self.world.has_component(req.sender, DamageLock) or not (
                health := self.world.try_component(req.reciever, Health)
            ):
                continue

            health.value -= req.damage
            self.world.add_component(req.reciever, DamagedMarker())

            if self.world.has_component(req.sender, DamageLocker):
                self.world.add_component(req.sender, DamageLock())


class DamageMarkerRemovingProcessor(esper.Processor):
    def process(self, **_):
        for ent, _ in self.world.get_component(DamagedMarker):
            self.world.remove_component(ent, DamagedMarker)


@component
class PlayerMarker:
    pass


CREATURES = {}


def init_creatures_registry(world: esper.World):
    from ai import Enemy
    from movement import Velocity

    if not (player := utils.get.player(world)):
        raise PlayerUninitialized("Игрок не инициализирован")

    registry = {
        "zombie": (
            Damage(5),
            DamageLocker(50),
            Enemy(player),
            Velocity(pygame.Vector2(0), 3),
        )
    }

    for key, val in registry.items():
        CREATURES[key] = val


class CreatureError(Exception):
    pass


class CreatureNotFoundError(CreatureError):
    pass


class PlayerUninitialized(CreatureError):
    pass
