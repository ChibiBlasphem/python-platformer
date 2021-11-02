import pygame
from helpers import import_folder
from animation import Animation


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, position, path):
        super().__init__()

        animation_frames = import_folder(f"./graphics/{path}")
        self.animation = Animation(frames=animation_frames, speed=0.15)
        self.image = self.animation.get_frame()
        self.rect = self.image.get_rect(center=position)

    def update(self, x_shift):
        has_finished = self.animation.update()
        if has_finished:
            self.kill()
        else:
            self.image = self.animation.get_frame()
            self.rect.x += x_shift
