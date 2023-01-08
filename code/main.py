import os
import sys

import pygame

from level import Level
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('pydew')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()


if __name__ == '__main__':
    lines = 0
    for filename in os.listdir('./'):
        try:
            with open(filename) as file:
                linecount = len(file.readlines())
                print(filename, linecount)
                lines += linecount
        except PermissionError:
            pass
    print('Full Linecount:', lines)
    game = Game()
    game.run()
