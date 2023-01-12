import sys
import esper
import utils
import pygame
import pygame_gui
import pygame_menu

from utils.consts import FPS, RESOLUTION

from animation import (
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
)
from location import (
    InitLocationProcessor,
    LocationInitRequest,
    SpawnPoint,
    SpawnablePositioningProcessor,
)
from event import EventProcessor
from bind import BindingProcessor
from ui import UiDrawingProcessor
from creature import PlayerMarker
from camera import CameraProcessor
from render import RenderProcessor
from roof import RoofTogglingProcessor
from chrono import DayNightCyclingProcessor
from object import SolidGroup, SolidGroupingProcessor
from movement import MovementProcessor, RotationProcessor
from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor
# from inventory import InventoryProcessr

PROCESSORS = (
    EventProcessor,
    InitLocationProcessor,
    SpawnablePositioningProcessor,
    BindingProcessor,
    SolidGroupingProcessor,
    MovementProcessor,
    RotationProcessor,
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
    CameraProcessor,
    RoofTogglingProcessor,
    RenderProcessor,
    DayNightCyclingProcessor,
    UiDrawingProcessor,
    # InventoryProcessr,
)

CHUNK_LOADER_PROCESSORS = (
    ChunkUnloadingProcessor,
    ChunkLoadingProcessor,
)


def fill_world(world: esper.World):
    world.create_entity(LocationInitRequest("test"))

    sprite_groups = world.create_entity(SolidGroup())
    player = utils.make.creature(
        world,
        "player",
        SpawnPoint("player"),
        PlayerMarker(),
        extra_parts={"legs"},
        surface_preprocessor=lambda s: pygame.transform.rotate(
            pygame.transform.scale2x(s), 90
        ),
    )


def run(screen: pygame.surface.Surface):
    clock = pygame.time.Clock()
    uimanager = pygame_gui.UIManager(screen.get_size())

    world = esper.World()

    fill_world(world)

    for processor in PROCESSORS:
        world.add_processor(processor())

    chunkloader = esper.World()

    for processor in CHUNK_LOADER_PROCESSORS:
        chunkloader.add_processor(processor())

    running = [True]
    while running[0]:
        world.process(
            dt=clock.tick(FPS),
            screen=screen,
            uimanager=uimanager,
            running=running,
        )
        chunkloader.process(RESOLUTION, world)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")

    if "--debug" in sys.argv:
        run(screen)
    else:
        menu = pygame_menu.Menu(
            "Corpse inc.",
            *RESOLUTION,
            center_content=False,
            theme=utils.make.menu_theme(),
        )

        menu.add.button("Играть", lambda: run(screen))
        menu.add.button("Выйти", pygame_menu.events.EXIT)

        menu.mainloop(screen)

    pygame.quit()
