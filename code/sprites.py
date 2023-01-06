from typing import Union

import pygame

from settings import LAYERS


class GenericSprite(pygame.sprite.Sprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], surf: pygame.Surface, groups: pygame.sprite.Group, z: int):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


class Water(GenericSprite):
    def __init__(self, pos, frames, groups):
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
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], surf: pygame.Surface, groups: pygame.sprite.Group):
        super().__init__(pos=pos, surf=surf, groups=groups, z=LAYERS['main'])

class Tree(GenericSprite):
    def __init__(self, pos: Union[pygame.math.Vector2, tuple[int, int]], surf: pygame.Surface, groups: pygame.sprite.Group, name: str):
        super().__init__(pos, surf, groups, LAYERS['main'])


