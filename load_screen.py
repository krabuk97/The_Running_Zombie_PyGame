import pygame

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))

class LoadScreen:
    def __init__(self):
        self.load_screen_image = pygame.transform.scale(pygame.image.load("image/load_screen1.jpeg").convert_alpha(), (1080, 720))

    def show_load_screen(self, screen):
        screen.blit(self.load_screen_image, (0, 0))
        pygame.display.flip()