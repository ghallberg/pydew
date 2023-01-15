from random import randint

import pygame
import pytmx

from overlay import Overlay
from player import Player
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, PLAYER_TOOL_OFFSET, DEBUG
from sky import Rain, Sky
from soil import SoilLayer
from sprites import GenericSprite, Water, WildFlower, Tree, Interactable, Particle
from support import import_images_from_folder
from transition import Transition
from menu import Menu


class Level:
    def __init__(self):
        # Fetch display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interactable_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # Sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # Shop
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.05)

        self.bg_music = pygame.mixer.Sound('../audio/music.mp3')
        self.bg_music.set_volume(0.01)
        self.bg_music.play(loops=-1)

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
            GenericSprite((x*TILE_SIZE, y*TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], LAYERS['main'])

        # Water
        water_frames = import_images_from_folder('../graphics/water/')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)

        # WildFlower
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos=(obj.x, obj.y),
                 surf=obj.image,
                 groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                 name=obj.name,
                 player_add=self.player_add)

        # Collision Tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            GenericSprite(pos=(x * TILE_SIZE, y * TILE_SIZE),
                          surf=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=self.collision_sprites, z=LAYERS['main'])

        # Player / Interactables
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(pos=(obj.x, obj.y),
                                     group=self.all_sprites,
                                     tree_sprites=self.tree_sprites,
                                     interactable_sprites=self.interactable_sprites,
                                     soil_layer=self.soil_layer,
                                     collision_sprites=self.collision_sprites,
                                     toggle_shop = self.toggle_shop)
            if obj.name == 'Bed' or obj.name == 'Trader':
                Interactable(pos=(obj.x, obj.y), size=(obj.width, obj.height), groups=self.interactable_sprites, name=obj.name)
            if obj.name == 'Trader':
                Interactable(pos=(obj.x, obj.y), size=(obj.width, obj.height), groups=self.interactable_sprites, name=obj.name)

        # Ground
        GenericSprite(pos=pygame.math.Vector2(0, 0),
                      surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
                      groups=self.all_sprites,
                      z=LAYERS['ground'])

    def player_add(self, item: str, amount: int = 1):
        self.player.item_inventory[item] += amount
        self.success.play()
        if DEBUG:
            print(self.player.item_inventory)

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        # Plants
        self.soil_layer.update_plants()

        # Trees in apples
        for tree in self.tree_sprites.sprites():
            if tree.alive:
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()

        # Water on soil
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # Sky
        self.sky.reset_start_color()

    def plant_collision(self):
        if self.soil_layer.plant_sprites.sprites():
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(pos=plant.rect.topleft, surf=plant.image, groups=self.all_sprites, z=LAYERS['main'])
                    row = plant.rect.centery // TILE_SIZE
                    col = plant.rect.centerx // TILE_SIZE
                    self.soil_layer.grid[row][col].remove('P')

    def run(self, dt) -> None:
        # Drawing
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        # self.all_sprites.update(dt)

        # Update
        if self.shop_active:
            self.menu.update()
        else:
            self.plant_collision()
            self.all_sprites.update(dt)
        
        # Overlay
        self.overlay.display()

        # Weather
        if self.raining and not self.shop_active:
            self.rain.update()

        # Transition
        self.sky.display(dt)
        if self.player.sleep:
            self.transition.play()
        


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

                if DEBUG:
                    # Debug stuff
                    if sprite == player:
                        pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                        hitbox_rect = player.hitbox.copy()
                        hitbox_rect.center = offset_rect.center
                        pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                        target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                        pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
