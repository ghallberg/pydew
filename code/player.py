import pygame

from settings import LAYERS, PLAYER_TOOL_OFFSET
from soil import SoilLayer
from support import import_images_from_folder, increment_and_modulo
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], group: pygame.sprite.Group, collision_sprites: pygame.sprite.Group,
                 tree_sprites: pygame.sprite.Group, interactable_sprites: pygame.sprite.Group, soil_layer: SoilLayer):
        super().__init__(group)

        # Animation setup
        self.animations = self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # Movement attributes
        self.direction = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 250

        # Collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126, -70))

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
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

        # Seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # Inventory
        self.item_inventory = {
            'wood':   0,
            'apple':  0,
            'corn':   0,
            'tomato': 0,
        }

        # Interactables
        self.tree_sprites = tree_sprites
        self.interactable_sprites = interactable_sprites
        self.sleep = False
        self.soil_layer = soil_layer

    def use_tool(self) -> None:
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            pass

    def set_target_pos(self) -> None:
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

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

        if not self.timers['tool use'].active and not self.sleep:
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

        if keys[pygame.K_RETURN]:
            collided_interaction_sprite = pygame.sprite.spritecollide(sprite=self, group=self.interactable_sprites, dokill=False)
            if collided_interaction_sprite and collided_interaction_sprite[0].name == 'Trader':
                pass
            if collided_interaction_sprite and collided_interaction_sprite[0].name == 'Bed':
                self.status = 'left_idle'
                self.sleep = True

    def set_status(self) -> None:
        # Set idle status if player isn't moving
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction: str) -> None:
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt: float) -> None:
        # Normalize the vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt: float) -> None:
        self.input()
        self.set_status()
        self.update_timers()
        self.set_target_pos()

        self.move(dt)
        self.animate(dt)

