import math
import random
import pygame

from typing import List
from position import Position
from graphics import VectoredGraphic


class Hitbox(Position):
    _width = 0
    _height = 0
    _vissable = True

    def __init__(self, x, y, width=0, height=0, id="Hitbox", vissable=True):
        super().__init__(x, y, id=id)
        self._width = width
        self._height = height
        self._vissable = vissable
        self._adjustment = (0, self.height()//2 - self.height()//4)

    def _adjusted_x(self):
        return self.x + self._adjustment[0]

    def _adjusted_y(self):
        return self.y + self._adjustment[1]

    def is_colliding(self, other):
        if self._vissable:
            return (
                self._adjusted_x() < other._adjusted_x() + other.width() and
                self._adjusted_x() + self.width() > other._adjusted_x() and
                self._adjusted_y() < other._adjusted_y() + other.height() and
                self._adjusted_y() + self.height() > other._adjusted_y()
            )
        else:
            return (
                self.x < other.x + other.width() and
                self.x + self.width() > other.x and
                self.y < other.y + other.height() and
                self.y + self.height() > other.y
            )

    def width(self):
        return self._width

    def height(self):
        return self._height

    def draw(self, screen, offset=(0, 0), hitboxes=False):
        vect_graphic = self.rendered_graphic()
        self._width = vect_graphic.width()
        self._height = vect_graphic.width()//2
        vect_graphic.draw(screen, offset=offset)
        if hitboxes:
            # pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width(), self.height()), 1)
            vect_graphic.draw_hitbox(
                screen=screen,
                offset=offset,
                x=self._adjusted_x(), y=self._adjusted_y(),
                width=self.width(), height=self.height())


class Actor(Hitbox):
    def __init__(self,
                 x, y,
                 facing: Position = Position(0, 0),
                 id="Actor",
                 health=1,
                 attack=0,
                 speed=0,
                 vision=100,
                 hostile=False,
                 agro=False,
                 width=32,
                 height=32,
                 ):
        Hitbox.__init__(self, x, y, width, height, id)
        self.health = health
        self.speed = speed
        self.attack = attack
        self.vision = self.radius() + vision
        self.hostile = hostile
        self.agro = agro

        self.moving = False
        # innit hitbox
        self._command: Position = Position(0, 0)

    def start_moving(self):
        self.moving = True

    def stop_moving(self):
        self.moving = False

    def rendered_graphic(self):
        return VectoredGraphic(self)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def radius(self):
        return self.width() // 2

    def center(self):
        cent = Position(self.x + self.width() // 2,
                        self.y + self.height() // 2)
        return cent

    # def colliding(self, other, offset=0):
    #     distance = math.sqrt((self.x - other.x + offset) **
    #                          2 + (self.y - other.y + offset)**2)
    #     return distance < self.radius()  # + other.radius()

    # def is_hitbox_colliding(self, other):
    #     return self.hitbox.is_colliding(other)

    # def _calc_hitbox(self):
    #    self.hitbox = Hitbox(self.x - 100, self.y, self.width(), self.height())

    def get_angle_on(self, other):
        angle = math.atan2(other.y - self.y, other.x - self.x)
        return angle

    def knock_back(self, other):
        other.step_away_from(self)

    def get_target(self):
        return self._command

    def take_step(self):
        target = self.get_target()
        if target is None:
            return
        dx = target.x - self.x
        dy = target.y - self.y

        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed
            self.y += dy * self.speed

    def step_away_from(self, other):
        if other is None and self.moving is False:
            return
        dx = other.x - self.x
        dy = other.y - self.y

        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.x -= dx * self.speed
            self.y -= dy * self.speed

    def check_actor_in_vision(self, actor):
        distance = math.sqrt((self.x - actor.x)**2 + (self.y - actor.y)**2)
        if distance < self.vision:
            return True
        if distance > self.vision:
            return False

    def move(self):
        if self.moving is True:
            # self._calc_hitbox()  # offset=(0, self.width() // -2))
            if (
                    self.x <= self._command.x + self.radius()
                and self.x >= self._command.x - self.radius()
                and self.y <= self._command.y + self.radius()
                and self.y >= self._command.y - self.radius()
            ):
                print(f"Arrived at {self._command.id}")
                self.give_command(self)  # Position(0, 0))
                self.moving = False

            print(f"{self.id} is moving towards {self._command.id}")

            self.take_step()

    def give_command(self, pos):
        self.start_moving()
        self._command = Position(
            pos.x, pos.y, id=pos.id)


class Boundry(Actor):
    def __init__(self,
                 x,
                 y,
                 facing: Position = Position(0, 0),
                 id="Boundry",
                 width=32,
                 height=32
                 ):
        super().__init__(x, y, facing=facing, id=id, width=width, height=height)


# class MobileActor(Actor):
#     def __init__(self,
#                  x,
#                  y,
#                  facing: Position = Position(0, 0),
#                  id="MobileActor",
#                  health=100,
#                  attack=10,
#                  speed=1,
#                  vision=100,
#                  hostile=False,
#                  agro=False,
#
#                  width=32,
#                  height=32
#                  ):
#         super().__init__(x, y, facing=facing, id=id, health=health,
#                          attack=attack, speed=speed, vision=vision, hostile=hostile, agro=agro,
#                          width=width, height=height)
# # Player class
#
#
# class PlayerActor(Actor):
#     def __init__(self,
#                  x, y,
#                  id="Player",
#                  width=32,
#                  height=32
#                  ):
#         super().__init__(x, y, facing=Position(0, 0), id=id,
#                          health=100, speed=2, width=width, height=height)
#
#     # Enemy class
#
#
# class NPCActor(Actor):
#     def __init__(self, x, y,
#                  id="NPC",
#                  health=100,
#                  speed=1,
#                  vision=100,
#                  hostile=False,
#                  agro=False,
#
#                  width=32,
#                  height=32
#                  ):
#         super().__init__(x, y, id=id, health=health, speed=speed,
#                          vision=vision, hostile=hostile, agro=agro, width=width, height=height)
#     #
#     # def check_move(self):
#     #     if self.agro:
#     #         self.moving = True


class ActorsActions:
    def __init__(self, actors: List[Actor] = []):
        self.actors: List[Actor] = actors

    def checks(self, other) -> None:
        for hostile in other.actors:
            self.actors_in_vision(hostile)

    def create_player(self):
        try:
            self.actors = [Actor(100, 100)]
            return True
        except:
            return False

    def get_player(self) -> Actor:
        return self.actors[0]

    def draw(self, screen, offset=(0, 0)):
        for actor in self.actors:
            actor.draw(screen, offset=offset)

    def destroy(self, actor: Actor):
        if actor.health <= 0:
            self.actors.remove(actor)

    def actors_in_vision(self, player: Actor):
        for actor in self.actors:
            if actor.check_actor_in_vision(player) and actor.hostile:
                print(f"{actor.id} saw you vision")
                actor.agro = True
                actor.give_command(player)
            if actor.agro:
                actor.start_moving()
            actor.move()

    def extend(self, actors: List[Actor]):
        self.actors.extend(actors)

    def append(self, actor: Actor):
        self.actors.append(actor)

    def get(self, index) -> Actor:
        return self.actors[index]

    def clear(self):
        self.actors.clear()

    def __iter__(self):
        return iter(self.actors)
    # TODO: Render Shape Sizes
    # TODO: Complete check if actor is in vision
