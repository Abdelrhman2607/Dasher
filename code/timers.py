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

        self.active = False
        self.in_cooldown = False

        if self.autostart:
            self.start()

    def start(self):
        self.active = True
        if self.start_func:
            self.start_func()
        self.start_time = pygame.time.get_ticks()

    def end(self):
        self.active = False
        if self.end_func:
            self.end_func()
        self.end_time = pygame.time.get_ticks()

        if not(self.reusable) and not(self.repeat):
            del self

    # def extend(self, extension):
    #     self.start_time -= extension
    #     self.end_time -= extension

    def update(self):
        if self.active:
            if (pygame.time.get_ticks() - self.start_time >= self.duration) and not(self.in_cooldown):
                self.end()
                if self.repeat:
                    self.in_cooldown = True

        if self.in_cooldown:
            if pygame.time.get_ticks() - self.end_time >= self.repeat_cd:
                self.in_cooldown = False
                self.start()
