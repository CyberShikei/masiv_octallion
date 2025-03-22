import pygame
import random

from game import Map
from actor import Boundry

# Initialize Pygame
pygame.init()
#
# # Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("masiv_octallion")

WORLD_WIDTH, WORLD_HEIGHT = 1600, 1200
#
FPS_CAP = 60
#
# # Colors
WHITE = (255, 255, 255)
# RED = (255, 0, 0)
# BLUE = (0, 0, 255)

# Main game loop
# Camera function


def main():
    clock = pygame.time.Clock()

    game = Map(WORLD_WIDTH, WORLD_HEIGHT)

    running = True
    ticker = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Updating
        game.take_move(tick=ticker, screen_dimensions=(SCREEN_WIDTH, SCREEN_HEIGHT))

        # Drawing
        screen.fill(WHITE)

        game.draw(screen)

        pygame.display.flip()
        #print(ticker)
        clock.tick(FPS_CAP)  # 60 FPS

        if ticker // 60 == 1:
            ticker = 1
        else:
            ticker += 1

    pygame.quit()


if __name__ == "__main__":
    main()
