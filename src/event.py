import esper
import utils
import pygame

import pygame_gui

from movement import Velocity
from creature import PlayerMarker
from item import CollidedItem, TakeItemRequest


class EventProcessor(esper.Processor):
    """Обрабатывает события."""

    def _handle_key_press(self, paused):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            paused[0] = True

        player, vel = utils.get.player(self, Velocity, id=True)

        if pressed[pygame.K_w]:
            vel.vector.y = -vel.value
        if pressed[pygame.K_a]:
            vel.vector.x = -vel.value
        if pressed[pygame.K_s]:
            vel.vector.y = vel.value
        if pressed[pygame.K_d]:
            vel.vector.x = vel.value

        if pressed[pygame.K_e] and (
            item := self.world.try_component(player, CollidedItem)
        ):
            self.world.add_component(player, TakeItemRequest(item.entity))

    def _handle_key_release(self, event: pygame.event.Event):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            if event.key in {pygame.K_w, pygame.K_s}:
                vel.vector.y = 0
            elif event.key in {pygame.K_a, pygame.K_d}:
                vel.vector.x = 0

    def process(self, running=None, uimanager=None, paused=None, events=None, **_):
        ui: pygame_gui.UIManager = uimanager

        self._handle_key_press(paused)

        for event in events:
            ui.process_events(event)

            match event.type:
                case pygame.QUIT:
                    if running is not None:
                        running[0] = False
                    else:
                        pygame.quit()
                case pygame.KEYUP:
                    self._handle_key_release(event)
