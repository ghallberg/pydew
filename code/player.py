import pygame

from support import import_images_from_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        # Animation setup
        self.animations = self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # Movement attributes
        self.direction = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    @staticmethod
    def import_assets() -> dict[str: list[pygame.Surface]]:
        animations = {'up': [], 'down': [], 'left': [], 'right': [],
                      'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                      'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                      'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                      'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

        for animation in animations:
            full_path = '../graphics/character/' + animation
            animations[animation] = import_images_from_folder(full_path)
        return animations

    def input(self) -> None:
        keys = pygame.key.get_pressed()

        # Vertical movement
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, dt) -> None:
        # Normalize the vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        # Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt) -> None:
        self.input()
        self.move(dt)
