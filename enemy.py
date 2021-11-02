from random import randint

import pygame

from tile import AnimatedTile


class Enemy(AnimatedTile):
    def __init__(self, position, size):
        super().__init__(position, size, "./graphics/enemy/run")
        self.rect = self.image.get_rect(bottomleft=position + pygame.math.Vector2(0, size))
        self.speed = randint(3, 5)

    def change_orientation(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1

    def move(self):
        self.rect.x += self.speed

    def update(self, x_shift):
        super().update(x_shift)
        self.move()
        self.change_orientation()
