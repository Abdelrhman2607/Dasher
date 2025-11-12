from settings import *
from timers import Timer

class PauseMenu:
    def __init__(self, font_path, width, height, text_height, title, *messages):
        self.display_surf = pygame.display.get_surface()

        self.width = width
        self.height = height
        self.text_height = text_height

        self.rect = pygame.FRect((WINDOW_WIDTH - self.width)/2, (WINDOW_HEIGHT - self.height)/2, self.width, self.height)

        self.font = pygame.font.Font(font_path, text_height)
        self.title_font = pygame.font.Font(font_path, int(text_height * 2))

        self.title_surf = self.title_font.render(title, True, 'black')
        self.title_rect = self.title_surf.get_frect()

        self.messages = []
        self.messages.append([self.title_surf, self.title_rect])

        for message in messages:
            text_surf = self.font.render(message, True, 'black')
            text_rect = text_surf.get_frect()
            
            self.messages.append([text_surf, text_rect])
        
        for message, i in zip(self.messages, range(4)):
            match i:
                case 0:
                    message[1] = message[1].move_to(center = (self.rect.centerx, self.rect.centery - 65))
                case 1:
                    message[1] = message[1].move_to(center = (self.rect.centerx, self.rect.centery - 25))
                case 2:
                    message[1] = message[1].move_to(topleft = (self.rect.left + 30, self.rect.centery + 5))
                case 3:
                    message[1] = message[1].move_to(topleft = (self.rect.left + 37, self.rect.centery + 45))


    def draw(self):
        pygame.draw.rect(self.display_surf, 'red', self.rect.inflate(10,10), 10, 15)
        pygame.draw.rect(self.display_surf,'white', self.rect, 0, 10)
        
        for message in self.messages:
            self.display_surf.blit(message[0], message[1])
    
    def volume_input(self):
        pass

class StartMenu:
    def __init__(self, font_path):
        self.font = pygame.font.Font(font_path, 50)
        self.display_surf = pygame.display.get_surface()
        self.active = True

        self.text_surf = self.font.render("Press Enter to Start", True, 'black')
        self.text_rect = self.text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT * 3/4))

    def draw(self):
        # self.display_surf.fill("black")
        self.display_surf.blit(self.text_surf, self.text_rect)

    def input(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_RETURN]:
            self.active = False

class Slider:
    def __init__(self, pos, length, min, max):
        self.display_surf = pygame.display.get_surface()

        self.pos = pos
        self.length = length
        self.min = min
        self.max = max

        self.bar_surf = pygame.Surface((self.length, 10))
        self.bar_rect = self.bar_surf.get_frect(topleft = pos)

        self.circle_surf = pygame.Surface((30,30), flags = pygame.SRCALPHA)
        self.circle_rect = self.circle_surf.get_frect(center = self.bar_rect.midright)

        self.magnitude = self.max
        self.clicked = False

    def draw(self):
        pygame.draw.rect(self.bar_surf, 'black', (0,0, self.length, 10))
        pygame.draw.circle(self.circle_surf, 'green', (15, 15), 15)
        
        self.display_surf.blit(self.bar_surf, self.bar_rect)
        self.display_surf.blit(self.circle_surf, self.circle_rect)

    def input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicks = pygame.mouse.get_pressed()
    
        if self.circle_rect.collidepoint(mouse_pos) and mouse_clicks[0] and not(self.clicked):
            self.clicked = True

        if self.clicked and mouse_clicks[0]:
            self.circle_rect.centerx = mouse_pos[0]

            if self.circle_rect.centerx >= self.bar_rect.right:
                self.circle_rect.centerx = self.bar_rect.right

            if self.circle_rect.centerx <= self.bar_rect.left:
                self.circle_rect.centerx = self.bar_rect.left
        
        else:
            self.clicked = False

    def calculate(self):
        value = (self.circle_rect.centerx - self.bar_rect.left) / 250

        if value <= 0:
            self.magnitude = 0.0
            return

        min_val = 0.01  
        max_val = 1.0    

        log_min = log(min_val)
        log_max = log(max_val)
        volume = exp(log_min + (log_max - log_min) * value)

        self.magnitude = round(volume, 2)

    def update(self):
        self.draw()
        self.input()
        self.calculate()
        
class Pointer:
    def __init__(self, color, tracker, target_point, camera_offset):

        self.tracker = tracker
        self.target_point = target_point
        self.offset = camera_offset
        self.color = color

        self.display_surf = pygame.display.get_surface()
        self.original_pointer_surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT * 4), pygame.SRCALPHA)
        self.pointer_width = self.original_pointer_surf.get_width()
        self.pointer_height = self.original_pointer_surf.get_height()

        self.pointer_surf = pygame.transform.rotozoom(self.original_pointer_surf, 0, 1)
        self.anchor = self.tracker.rect

        triangle_points = [(self.pointer_width / 6,self.pointer_height / 4),
                           (self.pointer_width * 5/6, self.pointer_height / 4),
                           (self.pointer_width/2, self.pointer_height / 6)]
        
        pygame.draw.polygon(self.original_pointer_surf, "black", triangle_points, 5)
        pygame.draw.polygon(self.original_pointer_surf, self.color, triangle_points)

    def rotate(self):
        self.pointer_surf = pygame.transform.rotozoom(self.original_pointer_surf, self.angle + 90, 1)
        self.pointer_rect = self.pointer_surf.get_frect(center = self.anchor.center)

    def update(self):
        self.angle = round(degrees(atan2(self.target_point[1] - self.anchor[1], -(self.target_point[0] - self.anchor[0]))))
        self.rotate()

    def draw(self):
        self.pointer_rect.x -= self.offset.x
        self.pointer_rect.y -= self.offset.y
        self.display_surf.blit(self.pointer_surf, self.pointer_rect)

class BossPointer(Pointer):
    def __init__(self, color, tracker, target_obj, camera_offset):

        self.tracker = tracker
        self.target = target_obj
        self.offset = camera_offset
        self.color = color

        self.display_surf = pygame.display.get_surface()
        self.original_pointer_surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT * 4), pygame.SRCALPHA)
        self.pointer_width = self.original_pointer_surf.get_width()
        self.pointer_height = self.original_pointer_surf.get_height()

        self.pointer_surf = pygame.transform.rotozoom(self.original_pointer_surf, 0, 1)
        self.anchor = self.tracker.rect

        triangle_points = [(self.pointer_width / 6,self.pointer_height / 4),
                           (self.pointer_width * 5/6, self.pointer_height / 4),
                           (self.pointer_width/2, self.pointer_height / 6)]
        
        pygame.draw.polygon(self.original_pointer_surf, "black", triangle_points, 5)
        pygame.draw.polygon(self.original_pointer_surf, self.color, triangle_points)

    def update(self):
        self.angle = round(degrees(atan2(self.target.rect.centery - self.anchor[1], -(self.target.rect.centerx - self.anchor[0]))))
        self.rotate()

class HealthBar:
    def __init__(self, color, max, length, height, pos):
        self.display_surf = pygame.display.get_surface()
        self.base_color = color
        self.color = color
        self.max = max
        self.length = length
        self.height = height

        self.frame_rect = pygame.FRect(pos[0], pos[1], self.length, self.height)

        self.flash_timer = Timer(200, reusable = True,
                                 start_func = lambda: setattr(self, "color", "red"),
                                 end_func = lambda: setattr(self, "color", self.base_color))

    def draw(self, current_value):
        pygame.draw.rect(self.display_surf, "black", self.frame_rect, 0, 15)
        pygame.draw.rect(self.display_surf, "white", self.frame_rect.inflate(-10,-10), 0, 15)

        self.health_rect = pygame.FRect(self.frame_rect.left + 10, self.frame_rect.top + 10, (current_value/self.max)*(self.length - 20), self.height - 20)
        pygame.draw.rect(self.display_surf, self.color, self.health_rect, 0, 5)

    def flash(self):
        self.flash_timer.start()

    def update(self, current_value):
        self.draw(current_value)
        self.flash_timer.update()

class FishCounter:
    def __init__(self):
        self.display_surf = pygame.display.get_surface()
        self.circle_colors = ["red", "yellow", "green"]
        self.radius = 25

        self.image = pygame.Surface((200,75), pygame.SRCALPHA)
        self.rect = self.image.get_frect(topleft = (10,10))

    def draw(self):

        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, "black", (0, 0, self.image.get_width(), self.image.get_height()), 0, 15)
        pygame.draw.rect(self.image, "white", (5, 5, self.image.get_width() - 10, self.image.get_height() - 10), 0, 10)

        for i in range(self.fish_count):
            x = 35 + (i * self.radius * 2.5)

            pygame.draw.circle(self.image, self.circle_colors[self.fish_count - 1], (x, self.image.get_height()/2), self.radius)
        
        self.display_surf.blit(self.image, self.rect)

    def update(self, fish_count):
        self.fish_count = fish_count
        self.draw()