import pygame
import random
import math

from enum import Enum
from typing import Tuple, List

from actor import Boundry, Position, ActorsActions, Actor, Hitbox


wall_path = "wall1"


class Map:
    def __init__(self,
                 width,
                 height,
                 boundries=[]
                 ):
        self.width = width
        self.height = height

        self.boundries: ActorsActions = ActorsActions(boundries)
        self.fov_boundries: ActorsActions = ActorsActions([])

        self.players = ActorsActions([])
        self.players.create_player()

        self.enemies: ActorsActions = ActorsActions([])
        self.fov_enemies: ActorsActions = ActorsActions([])
        # self.actors = {
        #        'players': ActorsActions(actors['players']),
        #        'enemies': ActorsActions(actors['enemies'])
        #        }
        self.generate_border_walls()
        self.generate_random_walls()
        self.generate_enemies()

    def get_player(self) -> Actor:
        player = self.players.get_player()
        return player

    def get_enemies(self):
        return self.enemies

    def generate_enemies(self, num_enemies=20):
        self.enemies.clear()
        for _ in range(num_enemies):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            while self._is_xy_boundry(x, y):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)

            enemy = Actor(x, y, id="spider", health=100,
                          speed=1, vision=100, hostile=True)
            self.enemies.append(enemy)

    def _is_xy_boundry(self, x, y):
        for boundry in self.boundries:
            if boundry.is_colliding(Actor(x, y)):
                return True
        return False

    def generate_border_walls(self):
        walls = []
        px, py = 0, 0

        while px < self.width:
            top_w = Boundry(px, py, facing=Position(0, 1), id=wall_path)
            bot_w = Boundry(px, self.height,
                            facing=Position(0, 1), id=wall_path)
            walls.append(top_w)
            walls.append(bot_w)
            px += walls[0].width() - walls[0].width()//3

        px = 0

        while py < self.height:
            left_w = Boundry(px, py, facing=Position(1, 0), id=wall_path)
            right_w = Boundry(
                self.width, py, facing=Position(1, 0), id=wall_path)
            walls.append(left_w)
            walls.append(right_w)
            py += walls[0].height() - walls[0].height()//3
        self.boundries.extend(walls)

    def generate_random_walls(self):
        for _ in range(10):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            wall = Boundry(x, y, id=wall_path)
            self.boundries.append(wall)

    def take_move(self, tick=0, screen_dimensions=(800, 400)):
        player = self.get_player()
        # print(f"Player {player}")
        # player.check_move(camera_offset=camera_offset)
        cam_offset = get_camera_offset(
            player,
            screen_dimensions=screen_dimensions,
            world_dimensions=(self.width, self.height)
        )
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = get_mouse_position()
            player.start_moving()
            player.give_command(add_offset(
                mouse_pos,
                cam_offset
            ))

        #self._check_boundry_collisions(player)
        #self.fov_enemies.checks(self.players)
        # self._check_enemies(player, offset=camera_offset)
        player.move()

        # if tick % 20 == 0:
        #     self._check_enemies_in_fov(
        #         offset=cam_offset, screen_dimensions=screen_dimensions)
        #     self._check_objects_in_fov(
        #         offset=cam_offset, screen_dimensions=screen_dimensions)

    def fov(self, offset: Position, screen_dimensions=(800, 400), excess=0.5):
        fov_actor = Hitbox(
            x=offset.x - screen_dimensions[0] * (excess/2),
            y=offset.y - screen_dimensions[1] * (excess),
            width=screen_dimensions[0] * (1 + excess),
            height=screen_dimensions[1] * (1 + excess),
            id="none",
            vissable=False)
        return fov_actor

    def _check_objects_in_fov(self, offset: Position, screen_dimensions=(800, 400)):
        self.fov_boundries.clear()
        for actor in self.boundries:
            if actor.is_colliding(self.fov(offset, screen_dimensions)):
                self.fov_boundries.append(actor)

    def _check_enemies_in_fov(self, offset: Position, screen_dimensions=(800, 400)):
        self.fov_enemies.clear()
        for actor in self.get_enemies():
            if actor.is_colliding(self.fov(offset, screen_dimensions)):
                self.fov_enemies.append(actor)

    def _check_boundry_collisions(self, actor):
        for bound in self.fov_boundries:
            if bound.is_colliding(actor):
                bound.knock_back(actor)
            # for enemy in self.fov_enemies:
            #     if bound.is_colliding(enemy):
            #         bound.knock_back(enemy)

    def draw(self, screen):
        cam_offset = get_camera_offset(
            self.get_player(),
            screen_dimensions=(800, 400),
            world_dimensions=(self.width, self.height)
        )
        self.players.draw(screen, offset=cam_offset)
        self.fov_enemies.draw(screen, offset=cam_offset)
        self.fov_boundries.draw(screen, offset=cam_offset)


def get_camera_offset(
        player,
        screen_dimensions=(800, 400),
        world_dimensions=(800, 400)
):
    # Center the player on the screen
    offset_x = player.center().x - screen_dimensions[0] // 2
    offset_y = player.center().y - screen_dimensions[1] // 2

    # Clamp the offset so the camera doesn't show outside the world
    offset_x = max(
        0, min(offset_x, world_dimensions[0] - screen_dimensions[0]))
    offset_y = max(
        0, min(offset_y, world_dimensions[1] - screen_dimensions[1]))

    return Position(offset_x, offset_y)


def add_offset(position, offset: Position = Position(0, 0)):
    return Position(position.x + offset.x, position.y + offset.y)

# Combat function


def get_mouse_position():
    x, y = pygame.mouse.get_pos()
    return Position(x, y, id="Mouse")


def check_combat(player, enemy):
    distance = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
    if distance < player.radius() + enemy.radius():
        enemy.health -= player.attack
        if enemy.health <= 0:
            return True  # Enemy defeated
    return False
