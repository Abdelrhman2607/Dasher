from settings import *
from player import *
from timers import *
from vfx import *
from groups import *
from UI import *
from sprites import *
from pytmx.util_pygame import load_pygame

class Game:                     
    def __init__(self):
        pygame.init()
        pygame.mixer.set_num_channels(16)

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dasher")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_path = join("data", "fonts", "DroplineRegular-Wpegz.otf")
        self.title_font = pygame.font.Font(self.font_path, 50)
        self.pause_msg_font = pygame.font.Font(self.font_path, 25)
        self.pause_msg = self.pause_msg_font.render("Press 'P' to pause", True, "black")

        self.state = "start"
        self.previous_state = "start"
        
        self.start_menu = StartMenu(self, self.font_path)
        self.logo = pygame.image.load(join("images", "logo.png")).convert_alpha()

        self.bg = pygame.image.load(join("images", "bg.png")).convert_alpha()
        self.bg_speed = 25
        self.bg_x = 0

        self.lose_bg = pygame.image.load(join("images", "lose.png")).convert_alpha()
        self.lose_bg_speed = 150
        self.lose_bg_y = -WINDOW_HEIGHT

        self.pause_menu = PauseMenu(self.font_path, 500, 200 , 30, "PAUSED", "Press 'P' to unpause", "BGM volume:", "SFX volume:")
        self.bgm_volume_slider = Slider((self.pause_menu.rect.left + 200, self.pause_menu.rect.centery + 25), 250, 0, 1)
        self.sfx_volume_slider = Slider(((self.pause_menu.rect.left + 200, self.pause_menu.rect.centery + 65)), 250, 0, 1)

        self.all_sprites = AllSprites()
        self.fish_sprites = AllSprites()
        self.vfx_sprites = AllSprites()
        self.attack_sprites = AllSprites()

        self.pointers = []
        self.health_bars = []
        self.fish_counter = FishCounter()

        self.dash_pulse_started = False

        self.collision_sprites = []

        self.fish_img = pygame.image.load(join("images", "power-ups", "fish.png")).convert_alpha()
        self.fish_positions = []
        self.fish_spawn_timer = Timer(duration = 5000,
                                      end_func = self.spawn_fish)

        self.audio = audio_loader("audio")
        self.bgm = self.audio["bgm"]
        self.explosion_sfx = [self.audio["explosion1"], self.audio["explosion2"], self.audio["explosion3"]]
        self.sfx = {
            "dash": self.audio["dash"],
            "pulse": self.audio["pulse"],
            "pickup": self.audio["pickup"],
            "explosion1": self.audio["explosion1"],
            "explosion2": self.audio["explosion2"],
            "explosion3": self.audio["explosion3"]
        }
    
        self.win_frame_index = 0
        self.win_anim_speed = 25
        self.win_audio = self.audio["win"]
        self.win_frames = frames_loader("images", "win")
        self.win_anim_length = len(self.win_frames["win"])
        print(self.win_anim_length)
        self.setup()
        
        self.fish_positions_states = [False] * len(self.fish_positions)
        self.spawn_fish()

    def setup(self):
        self.map = load_pygame(join("data", "map", "map.tmx"))

        for x, y, image in self.map.get_layer_by_name("ground").tiles():
            Sprite(x * TILE_SIZE, y * TILE_SIZE, image, True, False, self.all_sprites)

        for obj in self.map.get_layer_by_name("decor"):
            Sprite(obj.x, obj.y, obj.image, False, True, self.all_sprites)

        for x, y, image in self.map.get_layer_by_name("border").tiles():
            Sprite(x * TILE_SIZE, y * TILE_SIZE, image, False, False, self.all_sprites)
        
        for obj in self.map.get_layer_by_name("collisions"):
            Sprite(obj.x, obj.y, pygame.Surface((obj.width,obj.height), pygame.SRCALPHA), False, True, self.all_sprites)

        for sprite in self.all_sprites:
            if hasattr(sprite, "collide") and sprite.collide:
                self.collision_sprites.append(sprite)

        for obj in self.map.get_layer_by_name("positions"):
            if obj.name == "player":
                self.player_marker = obj
                self.player = Player(self, (obj.x, obj.y), self.collision_sprites, self.all_sprites)
                self.player_health_bar = HealthBar("pink", 100, 200, 30, (10, 90))
                self.health_bars.append(self.player_health_bar)
        
            elif obj.name == "fish":
                self.fish_positions.append(obj)

            elif obj.name == "boss":
                self.boss = Boss(self, (obj.x,obj.y), self.player, self.explosion_sfx, self.all_sprites)
                self.boss_health_bar = HealthBar((92,32,66), 100, 200, 30, (WINDOW_WIDTH - 210, 10))
                self.health_bars.append(self.boss_health_bar)
                self.pointers.append(BossPointer((92,32,66), self.player, self.boss, self.all_sprites.offset))
        
    def bg_scroll(self, dt):
        self.display_surface.blit(self.bg, (self.bg_x,0))
        self.display_surface.blit(self.bg, (self.bg_x - WINDOW_WIDTH,0))
        self.bg_x += dt * self.bg_speed
        self.bg_x %= WINDOW_WIDTH
         
    def menu_input(self):
        pressed_keys = pygame.key.get_just_pressed()

        if pressed_keys[pygame.K_p]:
            if self.state == "paused" and self.previous_state == "start":
                self.previous_state = self.state
                self.state = "start"
            elif self.state == "paused": 
                self.previous_state = self.state   
                self.state = "running"
            else:
                self.previous_state = self.state 
                self.state = "paused"

        if pressed_keys[pygame.K_r] and self.state == "lose":
            self.audio["scrape"].stop()
            self = Game()
            self.run()
            
    def spawn_fish(self):
        if self.player.fish_count < 3:
            available_pos = [pos for pos in self.fish_positions if not(self.fish_positions_states[pos.number])]
            
            if not(available_pos):
                return
    
            else:    
                fish_pos = choice(available_pos)
                Fish((fish_pos.x, fish_pos.y), self.fish_img, fish_pos.number, self.fish_sprites)
                self.fish_positions_states[fish_pos.number] = True
    
                self.pointers.append(Pointer( "#FFE2E2", self.player, (fish_pos.x, fish_pos.y), self.all_sprites.offset))
                # print(self.fish_positions_states)
    
    def fish_collision(self):
        collisions = pygame.sprite.spritecollide(self.player, self.fish_sprites, dokill = False)

        if collisions:
            for fish in collisions:
                Pulse(fish.rect.center, 100, 750, "#FFE2E2", self.vfx_sprites)
                self.sfx["pickup"].play()

                self.fish_positions_states[fish.number] = False

                self.player.fish_count = min(self.player.fish_count + 1, 3)
                self.player.set_health(self.player.health + 10)
                
                fish.kill()
                self.fish_spawn_timer.start()
                if self.pointers:
                    self.pointers.pop()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.state == "start":
                self.bg_scroll(dt)
                self.display_surface.blit(self.logo, (WINDOW_WIDTH/3.5, 50))
                self.start_menu.draw()
                self.start_menu.input()

                if not(self.start_menu.active):
                    self.state = "running"
                    self.bgm.play(-1)

            elif self.state == "running":

                if self.player.state == "dashing" and not(hasattr(self, "dash_trail_timer")):
                    #create an after image every {duration} seconds if dashing and not already being created
                    self.dash_trail_timer = Timer(duration = 50,
                                                  repeat = True,
                                                  autostart = True,
                                                  start_func = lambda: AfterImageTrail(self.player, 500, self.all_sprites))

                elif self.player.state == "dashing":
                    self.dash_trail_timer.update()

                    if self.sfx["dash"].get_num_channels() == 0:
                        self.sfx["dash"].play()

                else:
                    self.sfx["dash"].fadeout(100)

                if self.player.state == "dashing":
                    if not(self.dash_pulse_started):
                        Pulse(self.player.rect.center, 150, 2000, "white", self.vfx_sprites)
                        self.sfx["pulse"].play()
                        self.dash_pulse_started = True

                        self.all_sprites.screen_shake(200, 20)
                        self.fish_sprites.screen_shake(200, 20)
                
                else:
                    self.dash_pulse_started = False

                self.fish_spawn_timer.update()
                self.fish_collision()


                # print(self.fish_positions_states)

                self.all_sprites.update(dt)
                self.fish_sprites.update(dt)
                self.vfx_sprites.update(dt)
                self.attack_sprites.update(dt)
                for pointer in self.pointers:
                    pointer.update()

                #grayscale buddy to keep track of the center of the world
                # tester = pygame.sprite.Sprite(self.all_sprites)
                # tester.image = pygame.transform.grayscale(pygame.image.load("images/player/front/0.png")).convert_alpha()
                # tester.rect = tester.image.get_frect(center = CENTER)
 
                self.display_surface.fill("#bbeebb")
                self.all_sprites.draw(target = self.player)
                self.fish_sprites.draw(target = self.player)
                self.vfx_sprites.draw(target = self.player)
                self.attack_sprites.draw(target = self.player)
                for pointer in self.pointers:
                    pointer.draw()
                
                self.player_health_bar.update(self.player.health)
                self.boss_health_bar.update(self.boss.health)

                self.fish_counter.update(self.player.fish_count)

                self.display_surface.blit(self.pause_msg, (WINDOW_WIDTH - 185, WINDOW_HEIGHT - 35))
                
                if self.player.health <= 0:
                    self.state = "lose"
                    self.bgm.fadeout(200)
                    self.audio["scrape"].play()

                elif self.boss.health <= 0:
                    self.state = "win"
                    self.elapsed_time = round(((pygame.time.get_ticks() - self.start_time)/1000), 2)
                    self.win_audio.play()
                # pygame.draw.rect(self.display_surface, "red", pygame.FRect(self.player_marker.x - self.all_sprites.offset.x, self.player_marker.y- self.all_sprites.offset.y, 5,5))

            elif self.state == "paused":
                self.pause_menu.draw()
                
                self.bgm_volume_slider.update()
                self.bgm.set_volume(self.bgm_volume_slider.magnitude)

                self.sfx_volume_slider.update()
                for sound in self.sfx.keys():
                    self.sfx[sound].set_volume(self.sfx_volume_slider.magnitude)
            
            elif self.state == "lose":
                self.display_surface.blit(self.lose_bg, (0, self.lose_bg_y))
                if self.lose_bg_y < 0:
                    self.lose_bg_y += dt * self.lose_bg_speed
                elif self.lose_bg_y >= 0:
                    self.lose_bg_y = 0
                    self.display_surface.blit(self.title_font.render("GAME OVER", True, "black"), (WINDOW_WIDTH/2 - 100, 20))
                    self.display_surface.blit(self.title_font.render("Press 'R' to retry", True, "black"), (WINDOW_WIDTH/2 - 150, WINDOW_HEIGHT-100))

            elif self.state == "win":
                self.win_frame_index += dt * self.win_anim_speed
                if self.win_frame_index <= self.win_anim_length:
                    self.display_surface.blit(self.win_frames["win"][int(self.win_frame_index)], (0,0))
                else:
                    self.display_surface.blit(self.title_font.render("You Win", True, "black"), (WINDOW_WIDTH/2 - 50, 100))
                    self.display_surface.blit(self.title_font.render(f"Time: {self.elapsed_time} seconds", True, "black"), (WINDOW_WIDTH/2 - 150, 300))
                    self.display_surface.blit(self.title_font.render("Press 'R' to retry", True, "black"), (WINDOW_WIDTH/2 - 125, WINDOW_HEIGHT - 300))

            self.menu_input()
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
