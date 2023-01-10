from typing import Union

import pygame
from pytmx.util_pygame import load_pygame

from settings import LAYERS
from settings import TILE_SIZE, DEBUG
from support import import_folder_dict


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
        self.soil_surfs = import_folder_dict('../graphics/soil')

        self.grid = self.create_soil_grid()
        self.hit_rects = self.create_hit_rects()

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
                    self.create_soil_tiles()

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
