import pygame
from load_image import LoadImage
import sys

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (1080, 720))
death_screen = pygame.transform.scale(LoadImage.death_screen, (1080, 720))


class AfterDeath:
    def __init__(self, screen, background, restart_button, exit_button):
        self.exit_button_rect = None
        self.restart_button_rect = None
        self.screen = screen
        self.background = background
        self.restart_button = pygame.transform.scale(restart_button, (200, 210))
        self.exit_button = pygame.transform.scale(exit_button, (200, 210))
        self.restart_button_scaled = self.restart_button.copy()
        self.exit_button_scaled = self.exit_button.copy()
        self.selected_button = None
        self.button_hover_scale = 1.1
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.restart_button_rect.collidepoint(mouse_pos):
                    return "restart"
                elif self.exit_button_rect.collidepoint(mouse_pos):
                    return "exit"
        return None

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Check if the rectangles are initialized before drawing
        if self.restart_button_rect is not None:
            self.screen.blit(self.restart_button_scaled, self.restart_button_rect.topleft)

        if self.exit_button_rect is not None:
            self.screen.blit(self.exit_button_scaled, self.exit_button_rect.topleft)

        pygame.display.flip()

    def run(self):
        self.restart_button_rect = self.restart_button.get_rect(topleft=(70, 500))
        self.exit_button_rect = self.exit_button.get_rect(topright=(1000, 500))

        selected_action = None

        while selected_action is None:
            selected_action = self.handle_events()

            x, y = pygame.mouse.get_pos()
            if self.restart_button_rect.collidepoint(x, y):
                self.selected_button = "restart"
                self.restart_button_scaled = pygame.transform.scale(self.restart_button, (
                    int(self.restart_button.get_width() * self.button_hover_scale),
                    int(self.restart_button.get_height() * self.button_hover_scale)))
            elif self.exit_button_rect.collidepoint(x, y):
                self.selected_button = "exit"
                self.exit_button_scaled = pygame.transform.scale(self.exit_button, (
                    int(self.exit_button.get_width() * self.button_hover_scale),
                    int(self.exit_button.get_height() * self.button_hover_scale)))
            else:
                self.selected_button = None
                self.restart_button_scaled = self.restart_button.copy()
                self.exit_button_scaled = self.exit_button.copy()

            self.draw()

        return selected_action
