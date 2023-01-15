import pygame
from player import Player
from typing import Callable
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, SALE_PRICES, PURCHASE_PRICES
from timer import Timer

class Menu:
    def __init__(self, player: Player, toggle_menu: Callable) -> None:
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) -1
        self.text_surfs = self.setup_text_surfs()

        self.width = 400
        self.space = 5
        self.padding = 4
        self.total_height = self.set_total_height()
        
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.menu_left = SCREEN_WIDTH / 2 - self.width / 2
        self.main_rect = pygame.Rect(self.menu_left, self.menu_top, self.width, self.total_height)

        self.index = 0
        self.timer = Timer(200)

        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')
    
    def display_money(self):
        text_surf = self.font.render(f"${self.player.money}", False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))

        pygame.draw.rect(surface=self.display_surface, color='White', rect=text_rect.inflate(10, 10), border_radius=4)
        self.display_surface.blit(text_surf, text_rect)

    def setup_text_surfs(self) -> list[pygame.Surface]:
        text_surfs = []
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            text_surfs.append(text_surf)
        return text_surfs

    def set_total_height(self) -> int:
        total_height = 0
        for surf in self.text_surfs:
            total_height += surf.get_height() + (self.padding * 2)
        total_height += (len(self.text_surfs) - 1) * self.space
        return total_height

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()
        
        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.options) -1
                self.timer.activate()
            if keys[pygame.K_DOWN]:
                self.index += 1
                if self.index > len(self.options) - 1:
                    self.index = 0
                self.timer.activate()
            if keys[pygame.K_SPACE]:
                self.timer.activate()
                current_item = self.options[self.index]

                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= seed_price

    def show_entry(self, text_surf: pygame.Surface, top: int, amount: int, selected: bool) -> None:
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height())
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        text_rect = text_surf.get_rect(midleft=(self.main_rect.left+20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(bg_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        
        if selected:
            pygame.draw.rect(self.display_surface, 'Black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left+150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left+150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self) -> None:
        self.input()
        self.display_money()
        for index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[index]
            self.show_entry(text_surf=text_surf, top=top, amount=amount, selected=self.index==index)
            
        