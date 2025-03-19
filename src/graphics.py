from position import Position
import math
import pygame

class Graphic:
    def __init__(self,
                 image: str,
                 scale: int = 1,
                 id: str = "Graphic",
                 ):
        self.id = id
        self.set_image(image, scale)

    def _draw(self, screen, position: Position, offset=(0, 0)):
        screen.blit(self.image, (position.x - self.image.get_width() //
                    2 - offset[0], position.y - self.image.get_height() // 2 - offset[1]))
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
        super().__init__(
            image=f"public/sprites/{self.id}.png", scale=scale, id=self.id)

    def draw(self, screen, offset=(0, 0)):
        self._face_direction(self.face)
        super()._draw(position=self.posistion, screen=screen, offset=offset)

    def _face_direction(self, posistion: Position):
        angle = math.atan2(posistion.y - self.posistion.y,
                           posistion.x - self.posistion.x)
        super().rotate_image(angle)
