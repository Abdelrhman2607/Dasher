from settings import *
from timers import *

class AfterImageTrail(pygame.sprite.Sprite):
    def __init__(self, sprite, fade_speed, groups):
        super().__init__(groups)

        self.sprite = sprite
        self.fade_speed = fade_speed

        self.image = self.sprite.image.copy()
        self.rect = self.sprite.rect.copy()

        self.alpha_value = 200

    def update(self, dt):
        self.image.set_alpha(self.alpha_value)
        self.alpha_value -= self.fade_speed * dt

        if self.alpha_value <= 0:
            self.kill()


class Pulse(pygame.sprite.Sprite):
    def __init__(self, origin, max_radius, speed, color, groups):
        super().__init__(groups)
        self.image = pygame.Surface((max_radius * 2 , max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_frect(center = origin)
        self.max_radius = max_radius
        self.speed = speed
        self.color = color
        self.radius = 0

    def draw(self): #Keep in mind group draw vs sprite draw
        self.image.fill((0, 0, 0, 0)) 
        pygame.draw.circle(self.image, self.color, (self.image.get_width()/2, self.image.get_height()/2), self.radius, 15)

    def update(self, dt):
        if self.radius < self.max_radius:
            self.radius += int(self.speed * dt)
        else:
            self.kill()

        self.draw()

class AttackWarning(Pulse):
    def draw(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.image.get_width()/2, self.image.get_height()/2), self.max_radius, 5)
        pygame.draw.circle(self.image, self.color, (self.image.get_width()/2, self.image.get_height()/2), self.radius, 15)