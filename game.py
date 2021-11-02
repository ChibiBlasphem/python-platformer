from enum import IntEnum

import pygame

from level import Level
from overworld import Overworld
from ui import UI


class GameState(IntEnum):
    OVERWORLD = 1
    LEVEL = 2


class Game:
    max_level = 0
    max_health = 100
    current_health = 100
    coins = 0

    def __init__(self, surface: pygame.Surface):
        self.display_surface = surface
        self.ui = UI(surface)

        self.level_bg_music = pygame.mixer.Sound("./audio/level_music.wav")
        self.level_bg_music.set_volume(0.1)
        self.overworld_bg_music = pygame.mixer.Sound("./audio/overworld_music.wav")
        self.overworld_bg_music.set_volume(0.1)

        self.__create_overworld(0)

    def run(self):
        if self.state == GameState.OVERWORLD:
            self.overworld.run()
        else:
            self.__check_game_over()
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)

    def __create_level(self, current_level):
        self.level = Level(current_level, self.display_surface,
                           create_overworld=self.__create_overworld, change_coins=self.__change_coins, change_health=self.__change_health)
        self.overworld_bg_music.stop()
        self.level_bg_music.play(loops=-1)
        self.state = GameState.LEVEL

    def __create_overworld(self, current_level, new_max_level=None):
        if new_max_level != None and new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(
            current_level, self.max_level, self.display_surface, create_level=self.__create_level)
        self.level_bg_music.stop()
        self.overworld_bg_music.play(loops=-1)
        self.state = GameState.OVERWORLD

    def __change_coins(self, amount: int):
        self.coins += amount

    def __change_health(self, amount: int):
        self.current_health = max(
            0, min(self.max_health, self.current_health + amount))

    def __check_game_over(self):
        if self.current_health <= 0:
            self.max_level = 0
            self.coins = 0
            self.current_health = self.max_health
            self.__create_overworld(0)
