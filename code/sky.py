import random
from random import randint

import pygame

from settings import LAYERS
from sprites import GenericSprite
from support import import_images_from_folder


class Drop(GenericSprite):
    def __init__(self, surf, pos, moving, groups, z):
        super().__init__(pos, surf, groups, z)

        # Animation attributes
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        curr_time = pygame.time.get_ticks()
        if curr_time - self.start_time > self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_images_from_folder('../graphics/rain/drops')
        self.rain_floor = import_images_from_folder('../graphics/rain/floor')

        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()

    def create_floor(self):
        Drop(surf=random.choice(self.rain_floor),
             pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
             moving=False,
             groups=self.all_sprites,
             z=LAYERS['rain floor'])

    def create_drops(self):
        Drop(surf=random.choice(self.rain_drops),
             pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
             moving=True,
             groups=self.all_sprites,
             z=LAYERS['rain drops'])

    def update(self):
        self.create_drops()
        self.create_floor()
