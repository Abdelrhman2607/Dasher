from settings import *

class Timer:
    def __init__(self, duration, repeat = False, repeat_cd = 0, autostart = False, reusable = False, start_func = None, end_func = None):
        self.duration = duration

        self.repeat = repeat
        self.repeat_cd = repeat_cd
        
        self.autostart = autostart
        self.reusable = reusable

        self.start_func = start_func
        self.end_func = end_func

        self.start_time = 0
        self.end_time = 0
        self.pause_time = 0

        self.extended = False
        self.extended_duration = self.duration

        self.paused = False
        self.active = False
        self.in_cooldown = False

        if self.autostart:
            self.start()

    def start(self):
        if not(self.in_cooldown):
            self.active = True
            if self.start_func:
                self.start_func()
            self.start_time = pygame.time.get_ticks()

    def end(self):
        if self.end_func:
            self.end_func()
        self.end_time = pygame.time.get_ticks()

        self.reset()

        if not(self.reusable) and not(self.repeat):
            del self

    def toggle_pause(self):
        if not self.paused:
            self.pause_time = pygame.time.get_ticks()
            self.paused = True
        else:
            paused_duration = pygame.time.get_ticks() - self.pause_time
            self.start_time += paused_duration
            self.paused = False
    
    def extend(self, extension): #can only be used once per timer lifetime (or until reset)
        if not self.extended:
            self.extended_duration = self.duration + extension
            self.extended = True

    def reset(self):
        self.start_time = 0
        self.end_time = 0
        self.pause_time = 0

        self.extended = False
        self.extended_duration = self.duration

        self.paused = False
        self.active = False
        self.in_cooldown = False

    def update(self):
        if self.active and not(self.paused):
            if (pygame.time.get_ticks() - self.start_time >= (self.duration if not(self.extended) else self.extended_duration)) and not(self.in_cooldown):
                self.end()
                if self.repeat:
                    self.in_cooldown = True

        if self.in_cooldown:
            if pygame.time.get_ticks() - self.end_time >= self.repeat_cd:
                self.in_cooldown = False
                self.start()
