import pygame
import random
import math

from enum import Enum
from typing import Tuple, List

from graphics import VectoredGraphic
from actor import Boundry, Position, ActorsActions, PlayerActor, Actor, NPCActor, Hitbox


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
        self.create_player()

        self.enemies: ActorsActions = ActorsActions([])
        self.fov_enemies: ActorsActions = ActorsActions([])
        # self.actors = {
        #        'players': ActorsActions(actors['players']),
        #        'enemies': ActorsActions(actors['enemies'])
        #        }
        self.generate_border_walls()
        self.generate_random_walls()
        self.generate_enemies()

    def create_player(self):
        self.players.create_player()

    def get_player(self) -> PlayerActor:
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

            enemy = NPCActor(x, y, id="spider", health=100, speed=1, vision=100, hostile=True)
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

    def take_move(self, tick=0, camera_offset=(0, 0), screen_dimensions=(800, 400)):
        player = self.get_player()
        #print(f"Player {player}")
        player.check_move(camera_offset=camera_offset)
        self._check_boundry_collisions(player)
        self._check_enemies(player, offset=camera_offset)
        player.move()
        
        if tick % 20 == 0:
            self._check_enemies_in_fov(player, offset=camera_offset, screen_dimensions=screen_dimensions)
            self._check_objects_in_fov(
                player, offset=camera_offset, screen_dimensions=screen_dimensions)

    def fov(self, player, offset=(0, 0), screen_dimensions=(800, 400), excess=0.5):
        # screen_dimensions = (screen_dimensions[0] * (1 + excess) // 2, screen_dimensions[1] *(1 + excess))
        fov_actor = Hitbox(
            x=offset[0],  # + screen_dimensions[0]//2,
            y=offset[1],  # + screen_dimensions[1]//2,
            width=screen_dimensions[0],
            height=screen_dimensions[1])
        return fov_actor

    def _check_objects_in_fov(self, player, offset=(0, 0), screen_dimensions=(800, 400)):
        self.fov_boundries.clear()
        for actor in self.boundries:
            if actor.is_colliding(self.fov(player, offset, screen_dimensions)):
                self.fov_boundries.append(actor)
    
    def _check_enemies_in_fov(self, player, offset=(0, 0), screen_dimensions=(800, 400)):
        self.fov_enemies.clear()
        for actor in self.get_enemies():
            if actor.is_colliding(self.fov(player, offset, screen_dimensions)):
                self.fov_enemies.append(actor)

    def _check_enemies(self, player, offset=(0, 0)):
        #for enemy in self.fov_enemies:
        #    enemy.check_player_in_vision(player, camera_offset=offset)
        #    self._check_boundry_collisions(enemy)
        #    enemy.move()

        self.fov_enemies.actors_in_vision(player, camera_offset=offset)
        self.fov_enemies.make_moves()

    def _check_boundry_collisions(self, actor):
        for bound in self.fov_boundries:
            if bound.is_colliding(actor):
                bound.knock_back(actor)

    def draw(self, screen, camera_offset=(0, 0)):
        self.players.draw(screen, offset=camera_offset)
        self.fov_enemies.draw(screen, offset=camera_offset)
        self.fov_boundries.draw(screen, offset=camera_offset)

# Combat function


def check_combat(player, enemy):
    distance = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
    if distance < player.radius() + enemy.radius():
        enemy.health -= player.attack
        if enemy.health <= 0:
            return True  # Enemy defeated
    return False
