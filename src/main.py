import pygame
import random
import math

from enum import Enum
from typing import Tuple

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("masiv_octallion")

FPS_CAP = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()


class Position:
    def __init__(self, x, y, id="Posistion"):
        self.x = x
        self.y = y
        self.id = id


class Graphic:
    def __init__(self,
                 image: str,
                 scale: int = 1,
                 id: str = "Graphic",
                 ):
        self.id = id
        self.set_image(image, scale)

    def _draw(self, position: Position):
        screen.blit(self.image, (position.x - self.image.get_width() //
                    2, position.y - self.image.get_height() // 2))
# Actor class

    def scale_image(self, scale):
        self.image = pygame.transform.scale(
            self.image, (self.image.get_width() * scale, self.image.get_height() * scale))

    def set_image(self, image, scale=1):
        try:
            self.image = pygame.image.load(image)
        except:
            self.image = pygame.image.load("public/sprites/default.png")
            self.scale_image(scale)

    def rotate_image(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

    def width(self):
        return self.image.get_width()

    def height(self):
        return self.image.get_height()


class VectoredGraphic(Graphic):
    def __init__(self,
                 position: Position,
                 scale=1,
                 facing: Position = Position(0, 0),
                 ):
        self.posistion = position
        self.id = position.id
        self.face = facing
        super().__init__(image=f"public/sprites/{self.id}.png", scale=scale)

    def draw(self):
        self._face_direction(self.face)
        super()._draw(self.posistion)

    def _face_direction(self, posistion: Position):
        angle = math.atan2(posistion.y - self.posistion.y,
                           posistion.x - self.posistion.x)
        super().rotate_image(angle)


class Actor(Position):
    def __init__(self,
                 x, y,
                 facing: Position = Position(0, 0),
                 id="Actor",
                 health=1,
                 speed=0,
                 width=32,
                 height=32,
                 ):
        super().__init__(x, y, id)
        self.health = health
        self.speed = speed
        self.moving = False

        self._width = width
        self._height = height
        self._facing = facing
        self._calc_hitbox()

    def draw(self):
        vect_graphic = VectoredGraphic(self, facing=self._facing)
        vect_graphic.draw()

    def width(self):
        return self._width

    def height(self):
        return self._height

    def radius(self):
        return self.width() // 2

    def look_at(self, position: Position):
        self._facing = position

    def colliding(self, other, offset=0):
        distance = math.sqrt((self.x - other.x + offset) **
                             2 + (self.y - other.y + offset)**2)
        return distance < self.radius()  # + other.radius()

    def is_hitbox_coliding(self, other, offset=0):
        return (
            self.hitbox[0] < other.hitbox[2] + offset and
            self.hitbox[2] > other.hitbox[0] - offset and
            self.hitbox[1] < other.hitbox[3] + offset and
            self.hitbox[3] > other.hitbox[1] - offset
        )

    def _calc_hitbox(self, offset=0):
        self.hitbox = (
            self.x - self.radius() + offset,
            self.y - self.radius() + offset,
            self.x + self.radius() + offset,
            self.y + self.radius() + offset
        )

    def get_angle_on(self, other):
        angle = math.atan2(other.y - self.y, other.x - self.x)
        return angle

    def knock_back(self, other):
        other.step_away_from(self)
        
    def take_step(self, target):
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


class Boundry(Actor):
    def __init__(self, x, y, facing: Position = Position(0, 0), id="Boundry"):
        super().__init__(x, y, facing=facing, id=id)

class MobileActor(Actor):
    def __init__(self,
                 x,
                 y,
                 facing: Position = Position(0, 0),
                 id="MobileActor",
                 health=100,
                 attack=10,
                 speed=1,
                 ):
        super().__init__(x, y, facing=facing, id=id, health=health, speed=speed)
        self.attack = attack
        self._command: Position = Position(0, 0)

    # TODO: Move to higher order so destroys get handled by the handler
    def destroy(self):
        self.health = 0
        self.moving = False

    def move(self):
        if self.health <= 0:
            self.destroy()
            return
        if self.moving is True:
            # print(f"Moving Toward {self._command.id}, ({
            #      self._command.x}, {self._command.y})")
            self.take_step(self._command)
            self._calc_hitbox()

            if (
                self.x <= self._command.x + self.radius()
                    and self.x >= self._command.x - self.radius()
                    and self.y <= self._command.y + self.radius()
                    and self.y >= self._command.y - self.radius()
            ):
                self.give_command(Position(0, 0))
                self.moving = False

    def give_command(self, pos):
        self._command = pos
# Player class


class Player(MobileActor):
    def __init__(self, x, y, id="Player"):
        super().__init__(x, y, facing=Position(0, 0), id=id, health=100, speed=2)

    def check_move(self):
        # if mouse left click
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = get_mouse_position()
            self.moving = True
            self.look_at(mouse_pos)
            self.give_command(mouse_pos)


def get_mouse_position():
    x, y = pygame.mouse.get_pos()
    return Position(x, y)

# Enemy class


class Enemy(MobileActor):
    def __init__(self, x, y,
                 id="Enemy",
                 health=100,
                 speed=1,
                 vision=100,
                 ):
        super().__init__(x, y, id=id, health=health, speed=speed)
        self.vision = self.radius() + vision

    def check_player_in_vision(self, player):
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        if distance < self.vision:
            self.moving = True
            self.give_command(player)
            check_combat(player, self)
        if distance > self.vision * 2:
            self.moving = False


wall_path = "wall1"


class Map:
    def __init__(self,
                 width,
                 height,
                 boundries=[],
                 actors={
                     'players': [], 'enemies': []
                 }
                 ):
        self.width = width
        self.height = height

        self.boundries = boundries
        self.actors = actors
        self.generate_border_walls()
        self.generate_random_walls()

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

    def take_move(self, tick=0):
        for player in self.actors['players']:
            player.check_move()
            self._check_boundry_collisions(player)
            self._check_enemies(player)
            player.move()

    def _check_enemies(self, player):
        for enemy in self.actors['enemies']:
            enemy.check_player_in_vision(player)
            # check_combat(player, enemy)
            self._check_boundry_collisions(enemy)
            enemy.move()

    def _check_boundry_collisions(self, actor):
        for bound in self.boundries:
            if bound.is_hitbox_coliding(actor):
                bound.knock_back(actor)

    def draw(self):
        for boundry in self.boundries:
            vect_graphic = VectoredGraphic(
                position=boundry
            )
            vect_graphic.draw()
        for _, actors in self.actors.items():
            for actor in actors:
                vect_graphic = VectoredGraphic(
                    position=actor
                )
                vect_graphic.draw()


# Combat function


def check_combat(player, enemy):
    distance = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
    if distance < player.radius() + enemy.radius():
        enemy.health -= player.attack
        if enemy.health <= 0:
            return True  # Enemy defeated
    return False

# Main game loop


def main():
    spider_path = "spider"
    tree_path = "tree"
    clock = pygame.time.Clock()
    player1 = Player(WIDTH // 2, HEIGHT // 2,
                     id="player")
    enemy = Enemy(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        id=spider_path
    )

    num_enemies = 5
    enemies = []

    for _ in range(num_enemies):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        enemies.append(Enemy(x, y, id=spider_path))

    # spawn trees
    trees = []
    num_trees = 20
    for _ in range(num_trees):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        trees.append(Boundry(x, y, id=tree_path))

    map = Map(WIDTH, HEIGHT, boundries=trees, actors={
              'players': [player1], 'enemies': enemies})

    running = True
    ticker = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        map.take_move(tick=ticker)

        # Drawing
        screen.fill(WHITE)

        map.draw()

        pygame.display.flip()
        print(ticker)
        clock.tick(FPS_CAP)  # 60 FPS

        if ticker // 60 == 1:
            ticker = 1
        else:
            ticker += 1

    pygame.quit()


if __name__ == "__main__":
    main()
