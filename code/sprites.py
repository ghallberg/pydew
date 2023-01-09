from random import randint, choice
from typing import Union, Callable

import pygame

from settings import LAYERS, APPLE_POS
from timer import Timer


class GenericSprite(pygame.sprite.Sprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], surf: pygame.Surface,
                 groups: Union[pygame.sprite.Group, list[pygame.sprite.Group], pygame.sprite.AbstractGroup], z: int):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Interactable(GenericSprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], size: Union[pygame.math.Vector2, tuple[int, int]],
                 groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]], name: str):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups, LAYERS['main'])
        self.name = name


class Water(GenericSprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]],
                 frames: list[pygame.Surface], groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]]):
        # Animation setup
        self.frames = frames
        self.frame_index = 0

        # Sprite setup
        self.z = LAYERS['water']
        super().__init__(pos=pos,
                         surf=self.frames[self.frame_index],
                         groups=groups,
                         z=self.z)

    def animate(self, dt: float):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt) -> None:
        self.animate(dt)


class WildFlower(GenericSprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]],
                 surf: pygame.Surface, groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]]):
        super().__init__(pos=pos, surf=surf, groups=groups, z=LAYERS['main'])
        self.hitbox = self.rect.copy().inflate((-20, -self.rect.height * 0.9))


class Particle(GenericSprite):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

        mask_surface = pygame.mask.from_surface(self.image).to_surface()
        mask_surface.set_colorkey((0, 0, 0))
        self.image = mask_surface

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(GenericSprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], surf: pygame.Surface,
                 groups: Union[pygame.sprite.Group, list[pygame.sprite.Group]], name: str, player_add: Callable):
        super().__init__(pos, surf, groups, LAYERS['main'])
        self.all_sprites = self.groups()[0]

        # Tree Attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(f'../graphics/stumps/{name.lower()}.png').convert_alpha()
        self.invul_timer = Timer(200)

        # Apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def damage(self):
        self.health -= 1

        # Remove a random apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            random_apple.kill()
            Particle(pos=(random_apple.rect.left,
                          random_apple.rect.top),
                     surf=self.apple_surf,
                     groups=self.all_sprites,
                     z=LAYERS['fruit'])
            self.player_add('apple')
        self.invul_timer.activate()

    def check_death(self):
        if self.health <= 0:
            Particle(pos=self.rect.topleft, surf=self.image, groups=self.all_sprites, z=LAYERS['fruit'], duration=250)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.player_add('wood')
            self.alive = False

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                GenericSprite(pos=(x, y),
                              surf=self.apple_surf,
                              groups=[self.apple_sprites, self.all_sprites],
                              z=LAYERS['fruit'])

    def update(self, dt: float) -> None:
        if self.alive:
            self.check_death()
