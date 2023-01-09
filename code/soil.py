from typing import Union

import pygame
from pytmx.util_pygame import load_pygame

from settings import LAYERS
from settings import TILE_SIZE, DEBUG


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class SoilLayer:
    def __init__(self, all_sprites: pygame.sprite.Group):
        # Sprite Groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # Graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')

        self.grid = self.create_soil_grid()
        if DEBUG:
            for row in self.grid:
                print(row)
        self.hit_rects = self.create_hit_rects()
        if DEBUG:
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

    def create_hit_rects(self):
        hit_rects = []
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'F' in cell:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    hit_rects.append(rect)
        return hit_rects

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    # self.create_soil_tiles()
                    SoilTile(pos=(rect.x, rect.y), surf=self.soil_surf, groups=[self.all_sprites, self.soil_sprites])

    # TODO Do we actually need this? Seems ineficcient to recreate all the soil tiles every time. Might be used for reset after sleep?
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if 'X' in cell:
                    SoilTile(pos=(col_index*TILE_SIZE, row_index*TILE_SIZE),
                             surf=self.soil_surf,
                             groups=[self.all_sprites, self.soil_sprites])
