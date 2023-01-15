import random
from typing import Union, Callable

import pygame
from pytmx.util_pygame import load_pygame

from settings import LAYERS, TILE_SIZE, DEBUG, GROW_SPEED
from support import import_folder_dict, import_images_from_folder


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type: str, groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]], soil: pygame.sprite.Sprite, check_watered: Callable):
        # General setup
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = import_images_from_folder(f'../graphics/fruit/{self.plant_type}')
        self.soil = soil
        self.check_watered = check_watered

        # Plant growing attributes
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[self.plant_type]
        self.harvestable = False

        # Graphics
        self.image = self.frames[self.age]
        self.y_offset = -16 if self.plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(x=0, y=self.y_offset))
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate((-26, -self.rect.height * 0.4))
            if self.age > self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(x=0, y=self.y_offset))


class SoilLayer:
    def __init__(self, all_sprites: pygame.sprite.Group, collision_sprites: pygame.sprite.Group):
        # Sprite Groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # Graphics
        self.soil_surfs = import_folder_dict('../graphics/soil')
        self.water_surfs = import_images_from_folder('../graphics/soil_water')

        self.grid = self.create_soil_grid()
        self.hit_rects = self.create_hit_rects()

        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.01)
        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.plant_sound.set_volume(0.01)

        if DEBUG:
            for row in self.grid:
                print(row)
            print(self.hit_rects)

    @staticmethod
    def create_soil_grid():
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE
        grid = [[[] for _ in range(h_tiles)] for __ in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            grid[y][x].append('F')
        return grid

    def create_hit_rects(self) -> list[pygame.Rect]:
        hit_rects = []
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'F' in cell:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    hit_rects.append(rect)
        return hit_rects

    def get_hit(self, target_pos: pygame.math.Vector2) -> None:
        for rect in self.hit_rects:
            if rect.collidepoint(target_pos):
                self.hoe_sound.play()
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, target_pos: pygame.math.Vector2) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                WaterTile(pos=soil_sprite.rect.topleft, surf=random.choice(self.water_surfs), groups=[self.all_sprites, self.water_sprites])

    def water_all(self):
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    WaterTile(pos=(x, y), surf=random.choice(self.water_surfs), groups=[self.all_sprites, self.water_sprites])

    def remove_water(self) -> None:
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, pos: tuple[int, int]) -> bool:
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        return 'W' in cell

    def plant_seed(self, target_pos: pygame.math.Vector2, selected_seed: str) -> None:
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.plant_sound.play()
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(plant_type=selected_seed,
                          soil=soil_sprite,
                          groups=[self.all_sprites, self.plant_sprites, self.collision_sprites],
                          check_watered=self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell:
                    top = 'X' in self.grid[row_index-1][col_index]
                    bottom = 'X' in self.grid[row_index+1][col_index]
                    left = 'X' in row[col_index-1]
                    right = 'X' in row[col_index+1]

                    tile_type = 'o'

                    if all([top, bottom, left, right]):
                        tile_type = 'x'

                    # Horizontals
                    if left and not any([top, right, bottom]):
                        tile_type = 'r'
                    if right and not any([top, left, bottom]):
                        tile_type = 'l'
                    if right and left and not any([top, bottom]):
                        tile_type = 'lr'

                    # Verticals
                    if top and not any([right, left, bottom]):
                        tile_type = 'b'
                    if bottom and not any([right, left, top]):
                        tile_type = 't'
                    if bottom and top and not any([right, left]):
                        tile_type = 'tb'

                    # Corners
                    if left and bottom and not any([top, right]):
                        tile_type = 'tr'
                    if right and bottom and not any([top, left]):
                        tile_type = 'tl'
                    if left and top and not any([bottom, right]):
                        tile_type = 'br'
                    if right and top and not any([bottom, left]):
                        tile_type = 'bl'

                    # T shapes
                    if all([top, bottom, right]) and not left:
                        tile_type = 'tbr'
                    if all([top, bottom, left]) and not right:
                        tile_type = 'tbl'
                    if all([top, left, right]) and not bottom:
                        tile_type = 'lrb'
                    if all([left, bottom, right]) and not top:
                        tile_type = 'lrt'

                    SoilTile(pos=(col_index*TILE_SIZE, row_index*TILE_SIZE),
                             surf=self.soil_surfs[tile_type],
                             groups=[self.all_sprites, self.soil_sprites])
