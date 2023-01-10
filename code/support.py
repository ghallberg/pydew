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


def import_folder_dict(path: str) -> dict[str: pygame.Surface]:
    res = {}
    for _, __, files in walk(path):
        for filename in files:
            name = filename.split('.')[0]
            image = pygame.image.load(path + '/' + filename).convert_alpha()
            res[name] = image
    return res


def increment_and_modulo(x: int, mod: int) -> int:
    return (x + 1) % mod
