import sys
import math
import esper
import pygame

from animation import Animation
from creature import PlayerMarker


FPS = 60

RESOLUTION = 640, 640
CAMERA_SIZE = RESOLUTION

# TODO: Баг: при изменении данной константы система rotation.RotationProcessor
# неправильно вращает спрайты.
CAMERA_ZOOM = 1

PLAYER_SPEED = 3

_cache = {}


def init_resources_path() -> str:
    res = "/".join(__file__.split("/")[:-2]) + "/resources"
    if sys.platform not in {"linux", "darwin"} and res.startswith("/"):
        return res[1:]
    return res


RESOURCES = init_resources_path()


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return f"{RESOURCES}/world/{location_id}.tmx"

    @classmethod
    def frame(
        cls,
        object_id: str,
        idx: int,
        part_type: str | None = None,
        part_state: str | None = None,
    ) -> str:
        s = f"{RESOURCES}/frames/{object_id}"

        if part_type:
            s += f"/{part_type}"

        if part_state:
            s += f"/{part_state}"

        return f"{s}/{idx}.png"


def animation_from_surface(surface: pygame.surface.Surface) -> Animation:
    return Animation(frames=(surface,))


def surface_from_animation(animation: Animation) -> pygame.surface.Surface:
    return animation.frames[animation._frame]


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError("Object of type Location expected")

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile


def sprite(
    image: pygame.surface.Surface | None = None,
    rect: pygame.rect.Rect | None = None,
    mask: pygame.mask.Mask | None = None,
) -> pygame.sprite.Sprite:
    sprite = pygame.sprite.Sprite()

    if image:
        sprite.image = image
    if rect:
        sprite.rect = rect
    if mask:
        sprite.mask = mask

    return sprite


def player(processor, *components, id=False, cache=True):
    world: esper.World = processor.world

    if id and cache:
        key = "player_entity_id"

    if len(components) == 1:
        comps = world.get_components(PlayerMarker, *components)[0]

        if cache and id and _cache.get(key, None) is None:
            _cache[key] = comps[0]

        return (comps[0], comps[1][1]) if id else comps[1][1]
    elif len(components) != 0:
        comps = world.get_components(PlayerMarker, *components)[0]

        if cache and id and _cache.get(key, None) is None:
            _cache[key] = comps[0]

        return (comps[0], comps[1][1:]) if id else comps[1][1:]
    elif cache:
        if _cache.get(key, None) is None:
            _cache[key] = world.get_component(PlayerMarker)[0][0]

        return _cache[key]


def player_from_world(world, *components, id=False):
    fake_processor = esper.Processor()
    fake_processor.world = world
    return player(fake_processor, *components, id=id, cache=False)


def location(processor, player_position=None):
    from location import Location, Position

    world: esper.World = processor.world

    if player_position is not None:
        return world.component_for_entity(player_position.location, Location)

    return world.component_for_entity(player(processor, Position).location, Location)


def vector_angle(vector: pygame.Vector2) -> float:
    return vector.as_polar()[1]


def snake_to_camel_case(snake_case_string: str) -> str:
    return "".join(c.title() for c in snake_case_string.split("_"))


def rotate_point(origin, point, angle):
    """Поворачивает точку (point) против часовой стрелки на заданный в градусах
    угол (angle) вокруг заданной точки (origin)."""

    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy
