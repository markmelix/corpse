import pygame
import esper
import pytmx
import pyscroll
from meta import Id
import utils

from enum import IntEnum, auto
from dataclasses import dataclass as component

from items import Item
from render import Renderable
from object import Invisible, ObjectNotFoundError, Size, Solid


class Layer(IntEnum):
    """Каждая локация имеет три слоя: земля, объекты и крыши. На земле
    расположены тайлы травы, дорог и т. п. На слое объектов расположены все
    существа, объекты и предметы. На слое с крышами расположены крыши строений."""

    # Порядок имеет значение!
    Ground = auto()
    Objects = auto()
    Creatures = auto()
    Roofs = auto()

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s: str):
        return cls[utils.snake_to_camel_case(s)]


@component
class Location:
    map: pytmx.TiledMap
    renderer: pyscroll.BufferedRenderer
    sprites: pyscroll.PyscrollGroup


@component
class LocationInitRequest:
    """Запрос на инициализацию локации. id - строковый идентификатор
    локации для нахождения её .tmx файла."""

    id: str


@component
class Position:
    location: int
    coords: pygame.Vector2
    layer: Layer = Layer.Objects


class SpawnPoint:
    def __init__(self, name: str):
        self.name = name


class InitLocationProcessor(esper.Processor):
    """Инициализирует локации."""

    def _fill_objects(self, tilemap: pytmx.TiledMap, location: int):
        from movement import Direction

        for group in tilemap.objectgroups:
            for object in group:
                object: pytmx.TiledObject

                entity = self.world.create_entity(
                    Position(
                        location,
                        pygame.Vector2(object.as_points[1]),
                        Layer.from_str(group.name),
                    ),
                    Size(object.width, object.height),
                    Renderable(),
                )

                if not object.visible:
                    self.world.add_component(entity, Invisible())

                if object.image is not None:
                    self.world.add_component(
                        entity, utils.animation_from_surface(object.image)
                    )

                if object.rotation != 0:
                    self.world.add_component(
                        entity,
                        Direction(angle=object.rotation),
                    )

                if object.properties.get("is_solid", False):
                    self.world.add_component(entity, Solid())

                if object.properties.get("is_item", False):
                    self.world.add_component(entity, Item())

    def _make_location(self, location: int, location_id: str):
        tilemap = pytmx.load_pygame(utils.ResourcePath.location_tilemap(location_id))

        self._fill_objects(tilemap, location)

        renderer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tilemap),
            size=utils.CAMERA_SIZE,
            zoom=utils.CAMERA_ZOOM,
        )

        sprites = pyscroll.PyscrollGroup(map_layer=renderer)

        return Location(tilemap, renderer, sprites)

    def process(self, location=None, **_):
        for entity, request in self.world.get_component(LocationInitRequest):
            location = self._make_location(entity, request.id)
            self.world.add_component(entity, location)
            self.world.add_component(entity, Id(request.id))
            self.world.remove_component(entity, LocationInitRequest)


class SpawnablePositioningProcessor(esper.Processor):
    def process(self, **_):
        location_id, location = utils.location(self, id=True)

        for ent, point in self.world.get_component(SpawnPoint):
            if self.world.has_component(ent, Position):
                continue

            for group in location.map.objectgroups:
                for object in group:
                    object: pytmx.TiledObject
                    if object.name == point.name:
                        layer = Layer.from_str(group.name)
                        break
                    object = None
                else:
                    continue
                break

            if not object:
                raise ObjectNotFoundError(f"Объект с именем {point.name} не найден")

            coords = pygame.Vector2(object.as_points[0])

            self.world.add_component(ent, Position(location_id, coords, layer))
