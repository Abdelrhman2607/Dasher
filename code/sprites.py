from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, image, ground, collide, groups):
        super().__init__(groups)

        self.image = image
        self.rect = self.image.get_frect(topleft = (x, y))
        self.ground = ground
        self.collide = collide

class Fish(pygame.sprite.Sprite):
    def __init__(self, pos, image, number,groups):
        super().__init__(groups)

        self.image = image
        self.rect = self.image.get_frect(center = pos)

        self.number = number

class Boss(pygame.sprite.Sprite):
    pass
        