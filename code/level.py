import pygame
import pytmx

from overlay import Overlay
from player import Player
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from sprites import GenericSprite, Water, WildFlower, Tree
from support import import_images_from_folder


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
        tmx_data = pytmx.util_pygame.load_pygame('../data/map.tmx')

        # House
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                GenericSprite((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                GenericSprite((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        # Fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            GenericSprite((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        # Water
        water_frames = import_images_from_folder('../graphics/water/')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)

        # WildFlower
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, self.all_sprites)

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, self.all_sprites, obj.name)

        self.player = Player((640, 360), self.all_sprites)
        GenericSprite(pos=pygame.math.Vector2(0, 0),
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
            sprites_to_draw = [sprite for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.y) if sprite.z == layer]
            for sprite in sprites_to_draw:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)
