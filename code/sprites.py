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
#TODO fix boss visibility after weak boss hit
class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups):
        super().__init__(groups)
        
        self.frames = frames_loader("images", "boss")
        self.image = self.frames["front"][0]
        self.rect = self.image.get_frect(center = pos)
        self.group = groups

        player.boss = self
        self.player = player
        self.hidden = False
        self.weak_boss = None

        self.state = "front"
        self.previous_state = "front"
        self.last_frame_state = "front"
        self.state_changed = False

        self.frame_index = 0
        self.anim_length = 0

        self.jump_dest = (0,0)
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
        self.middair_timer.active = False

    def pick_idle(self):
        if self.state == "front":
            self.state = choice(["lick", "blink"])

    def check_fish(self):
        if self.player.fish_count == 3 and self.weak_boss == None:
            if self.middair_timer.active:
                self.land()
            for timer in self.timers:
                timer.toggle_pause()
            
            self.hidden = True
            self.weak_boss = WeakBoss(self, self.rect.center, self.player, self.group)

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

        self.check_fish()
        self.update_state()
        for timer in self.timers:
            if self.middair_timer.active:
                self.middair_timer.update()
            else:
                timer.update()
        if not(self.hidden):
            self.animate(dt, BOSS_ANIMS[self.state][1])

        self.last_frame_state = self.state
        

class WeakBoss(pygame.sprite.Sprite):
    def __init__(self, boss, pos, player, groups):
        super().__init__(groups)

        self.frames = frames_loader("images", "boss")
        self.image = self.frames["stunned"][0]
        self.rect = self.image.get_frect(center = pos)

        player.weak_boss = self
        self.boss = boss
        self.player = player

        self.state = "weaken"

        self.frame_index = 0
        self.anim_length = 0

        self.idle_timer = Timer(duration = 5000, repeat = True, end_func = lambda: setattr(self, "state", "stun_blink"))
        
    def weaken_anim(self, dt):
        if self.frame_index == 0:
            self.anim_length = len(self.frames[self.state])

        if self.frame_index < self.anim_length - 1:
            self.frame_index += BOSS_ANIMS[self.state][0] * dt
        else:
            self.idle_timer.start()
            self.state = "stunned"
            self.frame_index = 0

    def idle_anim(self, dt):
        if self.frame_index == 0:
            self.anim_length = len(self.frames[self.state])

        if self.frame_index < self.anim_length - 1:
            self.frame_index += BOSS_ANIMS[self.state][0] * dt
        else:
            self.state = "stunned"
            self.frame_index = 0

    def get_hit(self):
        self.boss.image = self.boss.frames["front"][0]
        self.boss.hidden = False
        self.boss.weak_boss = None
        for timer in self.boss.timers:
                timer.toggle_pause()
        
        self.kill()

    def update(self, dt):
        self.idle_timer.update()

        if self.state == "weaken":
            self.weaken_anim(dt)
            self.image = self.frames[self.state][int(self.frame_index)]

        elif self.state == "stun_blink":
            self.idle_anim(dt)
            self.image = self.frames[self.state][int(self.frame_index)]

        else:
            self.image = self.frames[self.state][0]

       