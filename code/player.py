import pygame

from support import import_images_from_folder, increment_and_modulo
from timer import Timer


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

        # Timers
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200),
        }

        # Tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # Seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self) -> None:
        pass

    def use_seed(self) -> None:
        pass

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

    def animate(self, dt: float) -> None:
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self) -> None:
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active:
            # Vertical movement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            # Horizontal movement
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # Tool usage
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Change tool
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index = increment_and_modulo(self.tool_index, len(self.tools))
                self.selected_tool = self.tools[self.tool_index]

            # Seed usage
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # Change seed
            if keys[pygame.K_w] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index = increment_and_modulo(self.seed_index, len(self.seeds))
                self.selected_seed = self.seeds[self.seed_index]

    def set_status(self) -> None:
        # Set idle status if player isn't moving
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def move(self, dt: float) -> None:
        # Normalize the vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        # Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def update(self, dt: float) -> None:
        self.input()
        self.set_status()
        self.move(dt)
        self.animate(dt)
        self.update_timers()
