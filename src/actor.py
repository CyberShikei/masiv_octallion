import math
import random
import pygame

from typing import List
from position import Position
from graphics import VectoredGraphic


class Hitbox(Position):
    _width = 0
    _height = 0

    def __init__(self, x, y, width=0, height=0, id="Hitbox"):
        super().__init__(x, y, id=id)
        self._width = width
        self._height = height

    def is_colliding(self, other):
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

    def draw(self, screen, offset=(0, 0), hitboxes=True):
        vect_graphic = self.rendered_graphic()
        self._width = vect_graphic.width()
        self._height = vect_graphic.height()
        vect_graphic.draw(screen, offset=offset)
        if hitboxes:
            # pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width(), self.height()), 1)
            vect_graphic.draw_hitbox(
                screen=screen,
                offset=offset,
                x=self.x , y=self.y,
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
        self._facing = facing
        self._command: Position = Position(0, 0)

    def rendered_graphic(self):
        return VectoredGraphic(self, facing=self._facing)

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

    def look_at(self, position: Position):
        self._facing = position

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

    def take_step(self):
        target = self._facing
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
        # other = self._facing
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

    def move(self, offset=(0, 0)):
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

            self.take_step()

    def give_command(self, pos, offset=(0, 0)):
        self._command = Position(
            pos.x + offset[0], pos.y + offset[1], id=pos.id)
        self.look_at(self._command)


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


class MobileActor(Actor):
    def __init__(self,
                 x,
                 y,
                 facing: Position = Position(0, 0),
                 id="MobileActor",
                 health=100,
                 attack=10,
                 speed=1,
                 vision=100,
                 hostile=False,
                 agro=False,

                 width=32,
                 height=32
                 ):
        super().__init__(x, y, facing=facing, id=id, health=health,
                         attack=attack, speed=speed, vision=vision, hostile=hostile, agro=agro,
                         width=width, height=height)
# Player class


class PlayerActor(Actor):
    def __init__(self,
                 x, y,
                 id="Player",
                 width=32,
                 height=32
                 ):
        super().__init__(x, y, facing=Position(0, 0), id=id,
                         health=100, speed=2, width=width, height=height)

    def check_move(self, camera_offset=(0, 0)):
        # if mouse left click
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = get_mouse_position()
            self.moving = True
            self.give_command(mouse_pos, offset=camera_offset)


def get_mouse_position():
    x, y = pygame.mouse.get_pos()
    return Position(x, y)

    # Enemy class


class NPCActor(Actor):
    def __init__(self, x, y,
                 id="NPC",
                 health=100,
                 speed=1,
                 vision=100,
                 hostile=False,
                 agro=False,

                 width=32,
                 height=32
                 ):
        super().__init__(x, y, id=id, health=health, speed=speed,
                         vision=vision, hostile=hostile, agro=agro, width=width, height=height)

    def check_move(self):
        if self.agro:
            self.moving = True


class ActorsActions:
    def __init__(self, actors: List[Actor] = []):
        self.actors = actors

    def create_player(self):
        self.actors = [PlayerActor(100, 100)]

    def get_player(self) -> PlayerActor:
        return self.actors[0]

    def draw(self, screen, offset=(0, 0)):
        for actor in self.actors:
            actor.draw(screen, offset=offset)

    def destroy(self, actor: Actor):
        if actor.health <= 0:
            self.actors.remove(actor)

    def make_moves(self):
        for actor in self.actors:
            actor.check_move()
            actor.move()

    def actors_in_vision(self, player, camera_offset=(0, 0)):
        for actor in self.actors:
            if actor.check_actor_in_vision(player) and actor.hostile:
                print(f"{actor.id} saw you vision")
                actor.agro = True
                actor.give_command(player)

    def extend(self, actors: List[Actor]):
        self.actors.extend(actors)

    def append(self, actor: Actor):
        self.actors.append(actor)

    def get(self, index):
        return self.actors[index]

    def clear(self):
        self.actors.clear()

    def __iter__(self):
        return iter(self.actors)
    # TODO: Render Shape Sizes
    # TODO: Complete check if actor is in vision
