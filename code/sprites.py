from settings import *
from loaders import *
from timers import Timer
from vfx import Pulse

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
    def __init__(self, game, pos, player, explosions, groups):
        super().__init__(groups)
        self.game = game

        self.frames = frames_loader("images", "boss")
        self.image = self.frames["front"][0]
        self.rect = self.image.get_frect(center = pos)
        self.group = groups
        self.explosion_sfx = explosions

        self.health = 100
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

        self.warning_pulses = []

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
        
        self.explosion_timer = Timer(duration = 500,
                                autostart = True,
                                repeat = True,
                                reusable = True,
                                end_func = self.attack_explosion)
        
        self.spike_timer = Timer(duration = 250,
                                autostart = True,
                                repeat = True,
                                reusable = True,
                                end_func = self.attack_spike)
        
        self.timers = [self.idle_timer, self.jump_timer, self.middair_timer, self.explosion_timer, self.spike_timer]

    def set_health(self, value):
        self.health = value
        self.game.boss_health_bar.flash()

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
        try:
            self.image = self.frames[self.state][int(self.frame_index)]
        except IndexError:
            self.image = self.frames["front"][0]

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
            self.state = choice(["lick", "blink", "fins"])

    def check_fish(self):
        if self.player.fish_count == 3 and self.weak_boss == None:
            if self.middair_timer.active:
                self.land()
            for timer in self.timers:
                timer.toggle_pause()
            
            self.hidden = True
            self.weak_boss = WeakBoss(self, self.rect.center, self.player, self.group)

    def attack_explosion(self):
        attack_pos = (self.player.rect.centerx + choice([-100, 0, 100]), self.player.rect.centery + choice([-100, 0, 100]))
        self.warning_pulses.append(Pulse(attack_pos, 50, 200, (92,32,66), self.game.vfx_sprites))

    def check_explosions(self):
        for pulse in self.warning_pulses:
            if pulse.radius >= pulse.max_radius:
                Explosion(self.frames["explosion"], pulse.rect.center, self.game.attack_sprites)
                choice(self.explosion_sfx).play()
                self.warning_pulses.remove(pulse)

    def attack_spike(self):
        Spike(self.frames["spike"][0], self.rect.center, self.player, self.game.attack_sprites)

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
        self.check_explosions()
        self.update_state()
        for timer in self.timers:
            if self.middair_timer.active:
                self.middair_timer.update()
            else:
                timer.update()
        if not(self.hidden):
            self.animate(dt, BOSS_ANIMS[self.state][1])

        self.last_frame_state = self.state

class Spike(pygame.sprite.Sprite):
    def __init__(self, img, pos, target, groups):
        super().__init__(groups)

        self.image = img
        self.rect = self.image.get_frect(center = pos)
        
        self.speed = 1500
        self.damage = 10

        self.target = target.rect.center
        self.angle = round(degrees(atan2(self.target[1] - self.rect.center[1], -(self.target[0] - self.rect.center[0]))))
        self.direction = pygame.Vector2((self.target[0] - self.rect.center[0], (self.target[1] - self.rect.center[1]))).normalize()
        
        self.image = pygame.transform.rotozoom(self.image, self.angle + 90, 1.5)
        self.rect = self.image.get_frect(center = pos)

        self.exist_timer = Timer(5000, autostart = True)

    def update(self, dt):
        self.rect.centerx += self.speed * dt * self.direction.x
        self.rect.centery += self.speed * dt * self.direction.y

        self.exist_timer.update()
        if not(self.exist_timer.active):
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, frames, target, groups):
        super().__init__(groups)
        
        self.frames = frames
        self.target = target
        self.damage = 20
        
        self.frame_index = 0
        self.length = len(self.frames)

        self.image = self.frames[0]
        self.rect = self.image.get_frect(center = target)

    def update(self, dt):
        self.frame_index += BOSS_ANIMS["explosion"][0] * dt
        if self.frame_index >= self.length:
            self.kill()
            return

        self.image = pygame.transform.rotozoom(self.frames[int(self.frame_index)],0, 2)
        self.rect = self.image.get_frect(center = self.target)
        self.mask = pygame.mask.from_surface(self.image)
        

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
        self.boss.set_health(self.boss.health - 34)
        self.player.invul_timer.start()
        self.boss.image = self.boss.frames["front"][0]
        self.boss.hidden = False
        self.boss.weak_boss = None
        for timer in self.boss.timers:
                timer.toggle_pause()
        self.boss.jump()
        
        self.kill()

    def update(self, dt):
        self.idle_timer.update()

        if self.state == "weaken":
            self.weaken_anim(dt)
            try:
                self.image = self.frames[self.state][int(self.frame_index)]
            except IndexError:
                self.image = self.frames[self.state][0]

        elif self.state == "stun_blink":
            self.idle_anim(dt)
            try:
                self.image = self.frames[self.state][int(self.frame_index)]
            except IndexError:
                self.image = self.frames[self.state][0]

        else:
            self.image = self.frames[self.state][0]

       