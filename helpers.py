from typing import List
from os import walk
from csv import reader

import pygame

from settings import tile_size


def load_image(path: str):
    return pygame.image.load(path).convert_alpha()


def load_multiple_image(paths: List[str]) -> List[pygame.Surface]:
    return list(map(load_image, paths))


def import_folder(path: str):
    surfaces = []

    for _, _, filenames in walk(path):
        for filename in filenames:
            surface = load_image(f"{path}/{filename}")
            surfaces.append(surface)

    return surfaces


def import_tileset(path: str):
    surface = load_image(path).convert_alpha()
    x_count = surface.get_width() // tile_size
    y_count = surface.get_height() // tile_size

    tileset = []
    for row in range(y_count):
        y_position = row * tile_size
        for col in range(x_count):
            x_position = col * tile_size

            tile = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)
            tile.blit(surface, (0, 0), (x_position, y_position, tile_size, tile_size))
            tileset.append(tile)

    return tileset


def import_csv_layout(path: str):
    layout = []
    with open(path) as map:
        csv_reader = reader(map, delimiter=",")
        for row in csv_reader:
            layout.append(list(row))
    return layout
