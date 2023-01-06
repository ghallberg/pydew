import pygame

from overlay import Overlay
from player import Player
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import GenericSprite


class Level:
    def __init__(self):
        # Fetch display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.all_sprites = CameraGroup()

        self.player = None
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self) -> None:
        self.player = Player((640, 360), self.all_sprites)
        ground = GenericSprite(pos=pygame.math.Vector2(0, 0),
                               surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
                               groups=self.all_sprites,
                               z=LAYERS['ground'])

    def run(self, dt) -> None:
        self.display_surface.fill('black')
        self.all_sprites.update(dt)
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            sprites_to_draw = [sprite for sprite in self.sprites() if sprite.z == layer]
            for sprite in sprites_to_draw:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)
