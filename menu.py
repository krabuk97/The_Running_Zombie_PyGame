import pygame
import sys
from load_image import LoadImage

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))


class Menu:
    def __init__(self, screen, menu_image, start_button_image, exit_button_image):
        self.screen = screen
        self.menu_image = pygame.transform.scale(LoadImage.menu_image, (1080, 720))
        self.start_button_image = pygame.transform.scale(LoadImage.start_button, (200, 210))
        self.exit_button_image = pygame.transform.scale(LoadImage.exit_button, (200, 210))
        self.menu_image = pygame.transform.scale(menu_image, (1080, 720))
        self.start_button_image = pygame.transform.scale(start_button_image, (200, 210))
        self.exit_button_image = pygame.transform.scale(exit_button_image, (200, 210))
        self.start_button_rect = self.start_button_image.get_rect(topleft=(70, 500))
        self.exit_button_rect = self.exit_button_image.get_rect(topright=(1000, 500))
        self.selected_button = None
        self.button_hover_scale = 1.1
        self.start_button_scaled = self.start_button_image.copy()
        self.exit_button_scaled = self.exit_button_image.copy()

    def draw(self):
        self.screen.blit(self.menu_image, (0, 0))
        self.screen.blit(self.start_button_scaled, self.start_button_rect.topleft)
        self.screen.blit(self.exit_button_scaled, self.exit_button_rect.topleft)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if self.start_button_rect.collidepoint(x, y):
                    self.selected_button = "start"
                    self.start_button_scaled = pygame.transform.scale(self.start_button_image, (
                        int(self.start_button_image.get_width() * self.button_hover_scale),
                        int(self.start_button_image.get_height() * self.button_hover_scale)))
                elif self.exit_button_rect.collidepoint(x, y):
                    self.selected_button = "exit"
                    self.exit_button_scaled = pygame.transform.scale(self.exit_button_image, (
                        int(self.exit_button_image.get_width() * self.button_hover_scale),
                        int(self.exit_button_image.get_height() * self.button_hover_scale)))
                else:
                    self.selected_button = None
                    self.start_button_scaled = self.start_button_image.copy()
                    self.exit_button_scaled = self.exit_button_image.copy()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if self.start_button_rect.collidepoint(x, y):
                    return "start"
                elif self.exit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()
        return None
