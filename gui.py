import pygame
import time

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")


class Gui:
    def __init__(self, player, bomb_button_positions, bomb_types):
        self.player = player
        self.health_bar_full = player.health_bar_full
        self.health_bar_width = self.health_bar_full.get_width()
        self.health_bar_rect = self.health_bar_full.get_rect(topleft=(50, 50))
        self.player.score = 0
        self.time_passed = time.time()
        self.bomb_button_positions = bomb_button_positions
        self.bomb_types = bomb_types
        self.selected_bomb_color = (255, 255, 255)

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

    def draw_bomb_buttons(self, selected_bomb):
        for index, (position, bomb_type) in enumerate(zip(self.bomb_button_positions, self.bomb_types)):

            image_path = f"image/{bomb_type}.png"
            bomb_image = pygame.image.load(image_path).convert_alpha()
            bomb_image = pygame.transform.scale(bomb_image, (50, 50))

            if selected_bomb == bomb_type:
                bomb_image.fill(self.selected_bomb_color, special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(bomb_image, (position[0], position[1]))

    def calculate_point_score(self):
        current_time = time.time()
        if current_time - self.time_passed >= 1:
            self.player.score += 1
            self.time_passed = current_time
        return self.player.score

