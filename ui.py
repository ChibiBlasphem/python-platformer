import pygame

from helpers import load_image, load_multiple_image


class UI:
    def __init__(self, surface: pygame.Surface):
        self.display_surface = surface
        self.__load_resources()

    def __load_resources(self):
        self.health_bar, self.coin = load_multiple_image([
            "./graphics/ui/health_bar.png",
            "./graphics/ui/coin.png"
        ])
        self.font = pygame.font.Font("./graphics/ui/ARCADEPI.TTF", 30)
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))

    def show_health(self, current_health: int, full_health: int):
        self.display_surface.blit(self.health_bar, (20, 10))
        health_bar_width = current_health / full_health * 152
        health_bar_rect = pygame.Rect((54, 39), (health_bar_width, 4))
        pygame.draw.rect(self.display_surface, "#dc4949", health_bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_text = self.font.render(str(amount), False, "#33323d")
        coin_text_rect = coin_text.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery))
        self.display_surface.blit(coin_text, coin_text_rect)
