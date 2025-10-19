from settings import *
from loaders import *
from timers import Timer

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
    def __init__(self, pos, player, groups):
        super().__init__(groups)

        self.frames = frames_loader("images", "boss")
        self.image = self.frames["front"][0]
        self.rect = self.image.get_frect(center = pos)

        self.player = player

        self.state = "front"
        self.previous_state = "front"
        self.last_frame_state = "front"
        self.state_changed = False

        self.frame_index = 0
        self.anim_length = 0

        self.jump_speed = -2000
        self.dt = 0

        self.idle_timer = Timer(duration = 3000,
                                autostart = True,
                                repeat = True,
                                reusable = True,
                                end_func = self.pick_idle)
        
        self.jump_timer = Timer(duration = 10000,
                                autostart = True,
                                repeat = True,
                                repeat_cd = 10000,
                                reusable = True,
                                end_func = self.jump)
        
        self.middair_timer = Timer(duration = 3000,
                                reusable = True,
                                end_func = self.land)
        
        self.timers = [self.idle_timer, self.jump_timer, self.middair_timer]

    def animate(self, dt, loop = False):
        if (self.frame_index == 0):
            self.anim_length = len(self.frames[self.state])

        self.frame_index += BOSS_ANIMS[self.state][0] * dt
        if loop:
            self.frame_index %= self.anim_length

        if (self.frame_index >= self.anim_length):
            if loop:
                self.frame_index = 0
            else:
                self.state = self.previous_state
                self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]

    def find_landing(self):
        return pygame.Vector2(randint(3 * TILE_SIZE, 29 * TILE_SIZE), randint(3 * TILE_SIZE, 29 * TILE_SIZE)) 

    def jump(self):
        if self.state != "jump":
            self.state = "jump"
            self.middair_timer.start()
        
        self.jump_dest = self.find_landing()
    
    def land(self):
        self.rect.center = self.jump_dest

    def pick_idle(self):
        if self.state == "front":
            self.state = choice(["lick", "blink"])

    def update_state(self):
        if self.state != self.last_frame_state:
            self.state_changed = True
        else:
            self.state_changed = False

        if self.state_changed:
            self.previous_state = self.last_frame_state

    def update(self, dt):
        self.dt = dt

        if self.middair_timer.active:
            self.rect.centery += self.jump_speed * self.dt

        self.update_state()
        for timer in self.timers:
            if self.middair_timer.active:
                self.middair_timer.update()
            else:
                timer.update()
        self.animate(dt, BOSS_ANIMS[self.state][1])

        self.last_frame_state = self.state
        