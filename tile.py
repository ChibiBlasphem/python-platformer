import pygame

from animation import Animation
from helpers import import_folder, load_image


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()
        surf = pygame.Surface((size, size))
        surf = surf.convert_alpha()
        surf.fill((0, 0, 0, 0))
        self.image = surf
        self.rect = self.image.get_rect(topleft=position)

    def update(self, x_shift):
        self.rect.x += x_shift


class StaticTile(Tile):
    def __init__(self, position, size, tile_surf):
        super().__init__(position, size)
        self.image = tile_surf


class CrateTile(StaticTile):
    def __init__(self, position, size):
        crate_surf = load_image("./graphics/terrain/crate.png")
        super().__init__(position, size, crate_surf)
        self.rect = self.image.get_rect(
            bottomleft=(position[0], position[1] + size))


class AnimatedTile(Tile):
    def __init__(self, position, size, path):
        super().__init__(position, size)
        self.animation = Animation(import_folder(path), 0.15)
        self.image = self.animation.get_frame()

    def update(self, x_shift):
        self.animation.update()
        self.image = self.animation.get_frame()
        return super().update(x_shift)


class CoinTile(AnimatedTile):
    def __init__(self, position, size, coin_type):
        coin_path = "./graphics/coins/silver" if coin_type == "1" else "./graphics/coins/gold"
        super().__init__(position, size, coin_path)

        self.value = 1 if coin_type == "1" else 5
        center = position + pygame.math.Vector2(size, size) / 2
        self.rect = self.image.get_rect(center=center)


class PalmTile(AnimatedTile):
    def get_palm_info(palm_type):
        if palm_type == "0":
            path = "./graphics/terrain/palm_small"
            offset = 38
        elif palm_type == "1":
            path = "./graphics/terrain/palm_large"
            offset = 68
        else:
            path = "./graphics/terrain/palm_bg"
            offset = 64
        return path, offset

    def __init__(self, position, size, palm_type):
        path, offset = PalmTile.get_palm_info(palm_type)

        super().__init__(position, size, path)
        self.rect.topleft -= pygame.math.Vector2(0, offset)
