import pygame

from player import Player


class Level:
    display_surface: pygame.Surface
    player: Player
    all_sprites: pygame.sprite.Group

    def __init__(self):
        # Fetch display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        self.player = Player((640, 360), self.all_sprites)

    def run(self, dt) -> None:
        self.display_surface.fill('black')
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)
