from settings import *
from statistics import mode, StatisticsError
from timers import *
from loaders import *
from math import atan2, degrees
from UI import FishCounter


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, collision_sprites, groups):
        super().__init__(groups)
        self.col_sprites = [sprite for sprite in collision_sprites if sprite.collide]

        self.frames = frames_loader("images", "player")

        self.image = self.frames["front"][0]
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.inflate(-30,-90)

        self.previous_directions = []
        self.direction = pygame.Vector2()
        self.speed = 300

        self.animation_speed = 15
        self.frame_index = 0
        self.state = "front"

        self.boss = None
        self.weak_boss = None

        self.fish_count = 0

        self.dash_max_duration = 1500
        self.dash_speed = 1500
        self.direction_lock = False

        self.dash_timer_ended = False
        self.dash_timer_started = False
        self.dash_timer = Timer(self.dash_max_duration,
                                reusable = True,
                                start_func = lambda: setattr(self, "dash_timer_started", True),
                                end_func = lambda: setattr(self, "dash_timer_ended", True))

    def animate(self, dt):
        if self.state == "dashing":
            self.animation_speed = 30

        elif self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'

        elif self.direction.y != 0:
            self.state = 'front' if self.direction.y > 0 else 'back'

        if self.direction or (self.state == "dashing"): #second condition for still dashing to animate
            self.frame_index = self.frame_index + (dt * self.animation_speed)
        else:
            self.frame_index = 0


        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        self.animation_speed = 15

        self.dash_rotation()

    def dash_rotation(self):
        original_image = self.image.copy()
        try:
            direction = pygame.Vector2(mode(self.previous_directions))
        except  StatisticsError:
            direction = pygame.Vector2(0,-1)

        angle = degrees(atan2(direction.x, -1 * direction.y)) * -1
 
        if self.state == "dashing":
            self.image = pygame.transform.rotozoom(original_image, angle, 1)

    def input(self):
        # movement
        held_keys = pygame.key.get_pressed()
        pressed_keys = pygame.key.get_just_pressed()

        if not(self.direction_lock):
            self.direction.x = held_keys[pygame.K_d] - held_keys[pygame.K_a]
            self.direction.y = held_keys[pygame.K_s] - held_keys[pygame.K_w]

            self.direction = self.direction.normalize() if self.direction else self.direction

        #dashing
        if pressed_keys[pygame.K_SPACE]:
            if held_keys[pygame.K_SPACE]:
                if not(self.dash_timer_started):
                    self.dash_timer.start()
                    self.state, self.direction_lock = "dashing", True
        
        if not(held_keys[pygame.K_SPACE]) and self.state == "dashing":
            self.dash_timer.end()
            self.dash_timer_ended = False
            self.dash_timer_started = False
            self.state, self.direction_lock = "front", False


        if self.dash_timer_ended:
            self.dash_timer_ended = False
            self.dash_timer_started = False
            self.state, self.direction_lock = "front", False
            

    def move(self,dt):
        if self.state == "dashing":
            if self.direction:     
                dx = dt * self.dash_speed * self.direction.x
                dy = dt * self.dash_speed * self.direction.y

            else:
                try:
                    dx = dt * self.dash_speed * pygame.Vector2(mode(self.previous_directions)).x
                    dy = dt * self.dash_speed * pygame.Vector2(mode(self.previous_directions)).y

                except StatisticsError: #handling when the player hasn't moved at all yet
                    dx = dt * self.dash_speed * pygame.Vector2(0,-1).x
                    dy = dt * self.dash_speed * pygame.Vector2(0,-1).y
       
        else:
            dx = dt * self.speed * self.direction.x
            dy= dt * self.speed * self.direction.y


        self.hitbox.centerx += dx
        if abs(dx) > 0.5:
            self.collision("X", dx)
            self.boss_collision("X", dx)
            
        self.hitbox.centery += dy
        if abs(dy) > 0.5:
            self.collision("Y", dy)
            self.boss_collision("Y", dy)

        self.rect.center = self.hitbox.center

        if self.direction: # store last 3 directions for still dashing to allow diagonal still dashing (too sensitive to use just one direction)
                self.previous_directions.append(tuple(self.direction))

        if len(self.previous_directions) > 3:
            self.previous_directions.pop(0)


    def collision(self, direction, delta):
        for sprite in self.col_sprites:
            if self.hitbox.colliderect(sprite.rect):
                if (direction == "X"):
                    if (delta > 0):
                        self.hitbox.right = sprite.rect.left
                    elif (delta < 0):
                        self.hitbox.left = sprite.rect.right
                if (direction == "Y"):
                    if (delta > 0):
                        self.hitbox.bottom = sprite.rect.top
                    elif (delta < 0):
                        self.hitbox.top = sprite.rect.bottom

    def boss_collision(self, direction, delta):
        for sprite in [self.boss, self.weak_boss]:
            if sprite == None:
                continue
            
            if self.hitbox.colliderect(sprite.rect):
                    if (direction == "X"):
                        if (delta > 0):
                            self.hitbox.right = sprite.rect.left
                        elif (delta < 0):
                            self.hitbox.left = sprite.rect.right
                    if (direction == "Y"):
                        if (delta > 0):
                            self.hitbox.bottom = sprite.rect.top
                        elif (delta < 0):
                            self.hitbox.top = sprite.rect.bottom
            if sprite == self.weak_boss:
                pass

    def update(self, dt):
        
        self.input()
        
        self.move(dt)

        self.animate(dt)

        self.dash_timer.update()


        