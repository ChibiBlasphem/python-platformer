from typing import Dict, Literal
import pygame

from animation import Animation
from helpers import import_folder
from math import sin

player_gravity = 0.8
player_jump_speed = 16


class Player(pygame.sprite.Sprite):
    direction = pygame.math.Vector2(0, 0)
    speed = 8

    animations: Dict[Literal["idle", "run", "fall", "jump"], Animation]
    state = "idle"

    facing_right = True
    on_ground = False
    on_ceiling = False
    on_left = False
    on_right = False

    invincible = False
    invincibility_duration = 600
    hurt_time = 0

    def __init__(self, position, surface):
        super().__init__()

        self.display_surface = surface
        self.__load_resources()

        self.image = self.animations[self.state].get_frame()
        self.rect = self.image.get_rect(topleft=position)
        self.collision_rect = pygame.Rect(self.rect.topleft, (50, self.rect.height))

    def update(self, on_action):
        self.__input(on_action)
        self.state = self.get_state()
        self.__animate()
        self.__animate_run()
        self.__apply_acceleration()
        self.__check_invicibility()

    def get_state(self):
        if self.direction.y < 0:
            return "jump"
        if self.direction.y > 0.8:
            return "fall"

        if self.direction.x != 0:
            return "run"
        return "idle"

    def get_damage(self, change_health):
        if not self.invincible:
            self.hit_sound.play()
            change_health(-10)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()

    def __check_invicibility(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def __animate(self):
        animation = self.animations[self.state]
        animation.update()

        image = animation.get_frame()
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
            self.rect.bottomright = self.collision_rect.bottomright
        else:
            self.rect.bottomleft = self.collision_rect.bottomleft
        self.image = image

        if self.invincible:
            alpha = self.__wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def __animate_run(self):
        if self.state == "run" and self.on_ground:
            self.run_particles_animation.update()
            frame = self.run_particles_animation.get_frame()

            if self.facing_right:
                position = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(frame, position)
            else:
                position = self.rect.bottomright - pygame.math.Vector2(6, 10)
                self.display_surface.blit(pygame.transform.flip(frame, True, False), position)

    def __load_resources(self):
        animations = {}
        for animation in ["idle", "run", "jump", "fall"]:
            animation_frames = import_folder(f"./graphics/character/{animation}")
            animations[animation] = Animation(frames=animation_frames, speed=0.15)
        self.animations = animations

        run_particles = import_folder("./graphics/character/dust_particles/run")
        self.run_particles_animation = Animation(frames=run_particles, speed=0.15)

        self.jump_sound = pygame.mixer.Sound("./audio/effects/jump.wav")
        self.jump_sound.set_volume(0.01)
        self.hit_sound = pygame.mixer.Sound("./audio/effects/hit.wav")
        self.hit_sound.set_volume(0.5)

    def __input(self, on_action):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump_sound.play()
            self.__jump()
            on_action("jump", self.rect.midbottom)

    def __apply_acceleration(self):
        self.direction.y += player_gravity

    def __jump(self):
        self.direction.y = -player_jump_speed

    def __wave_value(self):
        value = sin(pygame.time.get_ticks())
        return 255 if value > 0 else 0
