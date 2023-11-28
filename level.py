import pygame
from player import Player

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))


class Level:
    def __init__(self, level_number, game_state="playing"):
        self.level_number = level_number
        self.game_state = game_state
        self.player = Player()
        self.level_number = level_number
        self.screen = screen
        self.background1 = pygame.transform.scale(pygame.image.load("image/background.jpg").convert_alpha(), (1080, 720))
        self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
        self.background3 = pygame.transform.scale(pygame.image.load("image/city_n.jpeg").convert_alpha(), (1080, 720))
        self.background4 = pygame.transform.scale(pygame.image.load("image/pr_n.jpeg").convert_alpha(), (1080, 720))
        self.background5 = pygame.transform.scale(pygame.image.load("image/wolf.jpg").convert_alpha(), (1080, 720))
        self.background6 = pygame.transform.scale(pygame.image.load("image/nuke_map.jpg").convert_alpha(), (1080, 720))
        self.background7 = pygame.transform.scale(pygame.image.load("image/swamp.jpeg").convert_alpha(), (1080, 720))

        self.current_background_index = 0
        self.current_background = self.background1
        self.background_changed = False

    def update_background(self):
        if self.game_state == "death_screen" and not self.background_changed:
            backgrounds = [self.background1, self.background2, self.background3, self.background4, self.background5,
                           self.background6, self.background7]

            self.current_background_index = (self.current_background_index + 1) % len(backgrounds)
            self.current_background = backgrounds[self.current_background_index]
            print(f"Changed background to {self.current_background_index}")

            self.background_changed = True
        else:
            self.background_changed = False

    def get_current_background(self):
        if self.level_number == 1:
            return self.background1
        elif self.level_number == 2:
            return self.background2
        elif self.level_number == 3:
            return self.background3
        elif self.level_number == 4:
            return self.background4
        elif self.level_number == 5:
            return self.background5
        elif self.level_number == 6:
            return self.background6
        elif self.level_number == 7:
            return self.background7
        else:
            return pygame.Surface((1080, 720))

    def should_change_level(self):
        return self.player.is_dying

    def load_level(self):
        self.screen.blit(self.get_load_screen(), (0, 0))
        pygame.display.flip()
        pygame.time.delay(2000)

        self.level_number += 1
        self.background_changed = False
        self.current_background_index = 0
        self.current_background = self.background1

    def get_load_screen(self):
        load_screen_image = pygame.transform.scale(pygame.image.load("image/load_screen1.jpeg").convert_alpha(), (1080, 720))
        return load_screen_image