import esper
import pygame
import utils

from location import Layer, Position
from object import Invisible
from render import Renderable


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        player_sprite = utils.get.player(self, Renderable).sprite

        for roof, (render, pos) in self.world.get_components(Renderable, Position):
            roof_sprite = render.sprite

            if pos.layer != Layer.Roofs or roof_sprite is None:
                continue

            if pygame.sprite.collide_mask(player_sprite, roof_sprite):
                self.world.add_component(roof, Invisible())
            elif self.world.try_component(roof, Invisible):
                self.world.remove_component(roof, Invisible)
