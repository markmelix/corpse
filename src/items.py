from dataclasses import dataclass as component
from creature import Creature
import pygame
import esper
from render import Renderable
import utils


class ItemsProcessor(esper.Processor):
    def process(self, **_):

        from location import Position
        from creature import Creature

        for creature, (_, creature_render) in self.world.get_components(Creature, Renderable):
            creature_sprite = utils.player(self, Renderable).sprite
            if creature_sprite is None:
                continue

            for item, (_, item_render) in self.world.get_components(Item, Renderable):
                item_sprite = render.sprite
                if item_sprite is None:
                    continue

                if pygame.sprite.collide_mask(creature_sprite, item_sprite):
                    self.world.creature_entity(HandleItemRequest(creature, item))
                    


class ItemsGroupingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        from render import Renderable

        items_group = utils.items_group(self).group
        for _, (render, _) in self.world.get_components(Renderable, Item):
            if render.sprite is not None and render.sprite not in items_group:
                items_group.add(render.sprite)


@component
class ItemsGroup:
    group: pygame.sprite.Group = pygame.sprite.Group()


# default component for all item
@component
class Item:
    pass


@component
class HandleItemRequest:
    entity_id: int
    item_id: int


@component
class About:
    name: str
    description: str


@component
class Position:
    location: int
    coords: pygame.math.Vector2


@component
class Durability:
    times: int


# component for consumables
@component
class ConsumptionComment:
    comments: tuple[str]


@component
class HealRequest:
    creature: int
    amount: int


@component
class SaturateRequest:
    creature: int
    amount: int


@component
class DamageRequest:
    creature: int
    amount: int


# component for weapon
@component
class FireWeapon:
    power: float
    range: int


@component
class EdgedWeapon:
    range: int


@component
class Magazine:
    ammo: int
    current: int
    max: int
    damage: int


@component
class Ammo:
    id: int
    damage: int


@component
class Armor:
    resistance: float
