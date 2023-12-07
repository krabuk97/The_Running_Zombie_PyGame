import pygame
import time
from bomb_manager import SelectedBomb

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]


class Gui:
    def __init__(self, player, bomb_button_positions, bomb_types):
        self.player = player
        self.screen = screen
        self.health_bar_full = player.health_bar_full
        self.health_bar_width = self.health_bar_full.get_width()
        self.health_bar_rect = self.health_bar_full.get_rect(topleft=(50, 50))
        self.player.score = 0
        self.time_passed = time.time()
        self.bomb_button_positions = bomb_button_positions
        self.bomb_types = bomb_types
        self.selected_bomb_color = (255, 255, 255)
        self.selected_bomb = SelectedBomb()
        self.exit_button_image = pygame.transform.scale(
            pygame.image.load("image/exit_button.png").convert_alpha(), (50, 50)
        )

    def draw_exit_button(self):
        self.screen.blit(self.exit_button_image, (10, 10))

    def handle_exit_button_click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        exit_button_rect = pygame.Rect(10, 10, 50, 50)

        if exit_button_rect.collidepoint(mouse_x, mouse_y):
            print("Exit button clicked")
            self.player.is_dying = True
            self.game_state = "menu"
            self.game_loop.handle_menu_state()

    def calculate_health_bar_width(self):
        health_percent = max(0, self.player.health) / 100.0
        return int(health_percent * self.health_bar_width)

    def draw_health_bar(self):
        health_bar_width = self.calculate_health_bar_width()
        health_bar_cropped = pygame.transform.smoothscale(self.health_bar_full, (health_bar_width, self.health_bar_rect.height))
        screen.blit(health_bar_cropped, self.health_bar_rect.topleft)

    def draw_point_score(self):
        point_score_text = pygame.font.Font(None, 36).render(f"Time: {self.calculate_point_score()}", 1,
                                                             (255, 255, 255))
        screen.blit(point_score_text, (width - point_score_text.get_width() - 100, 50))

    def draw_bomb_buttons(self):
        for index, (position, bomb_type) in enumerate(zip(self.bomb_button_positions, self.bomb_types)):
            image_path = f"image/{bomb_type}.png"
            bomb_image = pygame.image.load(image_path).convert_alpha()
            bomb_image = pygame.transform.scale(bomb_image, (50, 50))

            if self.selected_bomb == bomb_type:
                bomb_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)

            self.screen.blit(bomb_image, (position[0], position[1]))

    def handle_bomb_button_click(self, mouse_x, mouse_y):
        for index, (position, bomb_type) in enumerate(zip(self.bomb_button_positions, self.bomb_types)):
            button_rect = pygame.Rect(position[0], position[1], 50, 50)

            if button_rect.collidepoint(mouse_x, mouse_y):
                print(f"Bomb button {bomb_type} clicked")
                self.selected_bomb = bomb_type

    def calculate_point_score(self):
        current_time = time.time()
        if current_time - self.time_passed >= 1:
            self.player.score += 1
            self.time_passed = current_time
        return self.player.score
