import pygame
import sys
from settings import *
from game import Game

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('gray')
    game.run()

    pygame.display.update()
    clock.tick(60)
