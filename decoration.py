from enum import Enum
import pygame
from random import choice, randint

from helpers import import_folder, load_multiple_image
from settings import vertical_tile_count, tile_size, screen_width
from tile import AnimatedTile, StaticTile


class SkyStyle(Enum):
    OVERWORLD = 1
    LEVEL = 2


class Sky:
    def __init__(self, horizon, style=SkyStyle.LEVEL):
        top, middle, bottom = load_multiple_image([
            "./graphics/decoration/sky/sky_top.png",
            "./graphics/decoration/sky/sky_middle.png",
            "./graphics/decoration/sky/sky_bottom.png",
        ])

        self.horizon = horizon
        self.top = pygame.transform.scale(top, (screen_width, tile_size))
        self.middle = pygame.transform.scale(middle, (screen_width, tile_size))
        self.bottom = pygame.transform.scale(bottom, (screen_width, tile_size))

        self.style = style
        if self.style == SkyStyle.OVERWORLD:
            palm_surfaces = import_folder("./graphics/overworld/palms")
            self.palms = []

            for surface in [choice(palm_surfaces) for _ in range(10)]:
                x_position = randint(0, screen_width)
                y_position = self.horizon * tile_size + randint(50, 100)
                rect = surface.get_rect(midbottom=(x_position, y_position))
                self.palms.append((surface, rect))

            clouds_surfaces = import_folder("./graphics/overworld/clouds")
            self.clouds = []

            for surface in [choice(clouds_surfaces) for _ in range(10)]:
                x_position = randint(0, screen_width)
                y_position = randint(0, self.horizon * tile_size - 100)
                rect = surface.get_rect(midbottom=(x_position, y_position))
                self.clouds.append((surface, rect))

    def draw(self, surface):
        for row in range(vertical_tile_count):
            y_position = row * tile_size
            if row < self.horizon:
                surf = self.top
            elif row > self.horizon:
                surf = self.bottom
            else:
                surf = self.middle
            surface.blit(surf, (0, y_position))

        if self.style == SkyStyle.OVERWORLD:
            for palm in self.palms:
                surface.blit(palm[0], palm[1])
            for cloud in self.clouds:
                surface.blit(cloud[0], cloud[1])


class Water:
    def __init__(self, top, level_width):
        water_start = -screen_width
        water_tile_width = 192
        tiles_count = (level_width + 2 * screen_width) // water_tile_width

        self.group = pygame.sprite.Group()
        for tile_number in range(tiles_count):
            x_position = tile_number * water_tile_width + water_start
            tile = AnimatedTile((x_position, top), 192, "./graphics/decoration/water")
            self.group.add(tile)

    def draw(self, surface, x_shift):
        self.group.update(x_shift)
        self.group.draw(surface)


class Clouds:
    def __init__(self, horizon, level_width, clouds_count):
        cloud_surfaces = import_folder("./graphics/decoration/clouds")
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon * tile_size

        self.group = pygame.sprite.Group()
        for _ in range(clouds_count):
            cloud_surf = choice(cloud_surfaces)
            x_position = randint(min_x, max_x)
            y_position = randint(min_y, max_y)
            tile = StaticTile((x_position, y_position), 0, cloud_surf)
            self.group.add(tile)

    def draw(self, surface, x_shift):
        self.group.update(x_shift)
        self.group.draw(surface)
