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


def get_camera_offset(player):
    # Center the player on the screen
    offset_x = player.center().x - SCREEN_WIDTH // 2
    offset_y = player.center().y - SCREEN_HEIGHT // 2

    # Clamp the offset so the camera doesn't show outside the world
    offset_x = max(0, min(offset_x, WORLD_WIDTH - SCREEN_WIDTH))
    offset_y = max(0, min(offset_y, WORLD_HEIGHT - SCREEN_HEIGHT))

    return (offset_x, offset_y)


def main():
    spider_path = "spider"
    tree_path = "tree"
    clock = pygame.time.Clock()

    # spawn trees
    trees = []
    num_trees = 100
    for _ in range(num_trees):
        x = random.randint(0, WORLD_WIDTH)
        y = random.randint(0, WORLD_HEIGHT)
        trees.append(Boundry(x, y, id=tree_path))

    game = Map(WORLD_WIDTH, WORLD_HEIGHT, boundries=trees)

    running = True
    ticker = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Updating
        camera_offset = get_camera_offset(game.get_player())
        game.take_move(tick=ticker, camera_offset=camera_offset, screen_dimensions=(SCREEN_WIDTH, SCREEN_HEIGHT))

        # Drawing
        screen.fill(WHITE)

        game.draw(screen, camera_offset)

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
