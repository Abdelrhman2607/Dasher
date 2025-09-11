from settings import *
from timers import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surf = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.shaking = False
        self.shake_intensity = 0

        self.camera_rect = pygame.FRect(CAMERA_RECT_PADDINGS["left"],
                                   CAMERA_RECT_PADDINGS["top"],
                                   WINDOW_WIDTH - (CAMERA_RECT_PADDINGS["right"] + CAMERA_RECT_PADDINGS["left"]),
                                   WINDOW_HEIGHT - (CAMERA_RECT_PADDINGS["bottom"] + CAMERA_RECT_PADDINGS["top"])
                                   )
    
    def draw(self, target):
        #camera box
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom
        
        self.offset.x = self.camera_rect.left - CAMERA_RECT_PADDINGS["left"]
        self.offset.y = self.camera_rect.top - CAMERA_RECT_PADDINGS["top"]

        if self.shaking:
            self.offset.x += randint(-self.shake_intensity, self.shake_intensity)
            self.offset.y += randint(-self.shake_intensity, self.shake_intensity)

        self.ground_sprites = []
        self.normal_sprites = []

        for sprite in self:
            if hasattr(sprite, "ground") and  sprite.ground:
                self.ground_sprites.append(sprite)

            else:
                self.normal_sprites.append(sprite)

        for sprite in self.ground_sprites:
            self.display_surf.blit(sprite.image, sprite.rect.topleft - self.offset)

        for sprite in sorted(self.normal_sprites, key = lambda sprite: sprite.rect.centery):
            self.display_surf.blit(sprite.image, sprite.rect.topleft - self.offset)

        if hasattr(self, "shake_timer"):    
            self.shake_timer.update()


    def screen_shake(self, duration, intensity):
        self.shake_intensity = intensity
        self.shake_timer = Timer(duration = duration,
                                 autostart = True,
                                 start_func = lambda: setattr(self, "shaking", True),
                                 end_func = lambda: setattr(self, "shaking", False))
