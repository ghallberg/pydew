import pygame

from settings import LAYERS


class GenericSprite(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.math.Vector2, surf: pygame.Surface, groups: pygame.sprite.Group, z: int = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
