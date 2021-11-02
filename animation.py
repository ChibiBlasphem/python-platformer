import pygame
from typing import List
from dataclasses import dataclass


@dataclass
class Animation:
    frames: List[pygame.Surface]
    speed: float
    position: float = 0

    def update(self):
        self.position += self.speed
        has_finished = self.position >= len(self.frames)
        if has_finished:
            self.position = 0
        return has_finished

    def get_frame(self):
        return self.frames[int(self.position)]
