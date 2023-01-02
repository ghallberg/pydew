from os import walk

import pygame


def import_images_from_folder(path: str) -> list[pygame.Surface]:
    surface_list = []

    for _, __, image_files in walk(path):
        for image in image_files:
            full_path = path + '/' + image
            image = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image)

    return surface_list
