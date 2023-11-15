import random
import pygame
from load_image import LoadImage
from gui import Gui
from menu import Menu
from player import Player

pygame.init()

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (width, height))
death_screen = pygame.transform.scale(LoadImage.death_screen, (width, height))

bombs_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

menu_instance = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)
player = Player()
gui = Gui(player)

class Bombs(pygame.sprite.Sprite):
    def __init__(self, player, bomb_type, x, y, current_background):
        super().__init__()

        self.player = player
        self.bomb_type = bomb_type
        self.explosion_type = None
        self.exploded = False
        self.current_background = current_background

        self.load_bomb_image()

        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.reset_bomb()

    def load_bomb_image(self):
        if self.bomb_type == "nuke":
            self.image = pygame.image.load("image/bomb_nuke.png").convert_alpha()
        elif self.bomb_type == "regular":
            self.image = pygame.image.load("image/bomb_reg.png").convert_alpha()
        elif self.bomb_type == "frozen":
            self.image = pygame.image.load("image/frozen_bomb.png").convert_alpha()
        elif self.bomb_type == "fire":
            self.image = pygame.image.load("image/bomb_fire.png").convert_alpha()
        elif self.bomb_type == "poison":
            self.image = pygame.image.load("image/poison_bomb.png").convert_alpha()

    def create_explosion(self, explosion_type):
        if explosion_type is not None:
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type)
            explosion_group.add(explosion)

    def update(self, camera_x, current_location):
        if not self.exploded:
            self.rect.y += self.speed

            if self.rect.bottom >= height:
                self.exploded = True
                self.explode()
                self.kill()

            if self.rect.bottom > height:
                self.rect.bottom = height

            self.check_background_and_spawn(current_location)

    def check_background_and_spawn(self, current_location):
        if current_location == "background1":
            if self.bomb_type == "regular":
                self.create_explosion("normal")
        elif current_location == "background2":
            if self.bomb_type == "regular" or self.bomb_type == "fire":
                self.create_explosion("normal")

            if self.bomb_type == "fire":
                self.create_explosion("burn")
        elif current_location == "background3":
            pass

    def reset_bomb(self):
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 5)

    def explode(self):
        explosion_type = "nuke" if self.bomb_type == "nuke" else "normal"

        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type)
        explosion_group.add(explosion)

        if self.current_background == "background1":
            # Tło 1 - dodatkowe zachowanie dla tego tła
            if self.bomb_type == "regular":
                explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "normal")
                explosion_group.add(explosion)
        elif self.current_background == "background2":
            # Tło 2 - dodatkowe zachowanie dla tego tła
            if self.bomb_type == "regular" or self.bomb_type == "fire":
                explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "normal")
                explosion_group.add(explosion)

            if self.bomb_type == "fire":
                explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "burn")
                explosion_group.add(explosion)

        elif self.bomb_type == "frozen":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "frozen")
            explosion_group.add(explosion)
        elif self.bomb_type == "poison":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "poison")
            explosion_group.add(explosion)

        self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, player, explosion_type):
        super().__init__()

        self.player = player
        self.explosion_type = explosion_type
        self.animation_delay = 100
        self.animation_counter = 0
        self.animation_start_time = pygame.time.get_ticks()
        self.finished = False
        self.distance_threshold = 0
        self.damage_amount = 0
        self.images = []
        self.camera_x = 0

        self.load_explosion_images()

        self.image_index = 0

        if self.images and len(self.images) > 0:
            self.rect = self.images[0].get_rect(center=(x, y))
            self.image = self.images[self.image_index]
        else:
            self.rect = pygame.Rect(x, y, 0, 0)
            self.image = pygame.Surface((0, 0))

    def load_explosion_images(self):
        if self.explosion_type == "normal" or self.explosion_type == "regular":
            explosion_images = LoadImage.explosion_files
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 5
        elif self.explosion_type == "nuke":
            explosion_images = LoadImage.nuke
            size = (300, 300)
            self.distance_threshold = 250
            self.damage_amount = 50
        elif self.explosion_type == "frozen":
            explosion_images = LoadImage.frozen_bomb
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "poison":
            explosion_images = LoadImage.poison_bomb
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "burn" or self.explosion_type == "fire":
            explosion_images = LoadImage.burn
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        else:
            raise ValueError(f"Unknown explosion_type: {self.explosion_type}")

        self.images = [
            pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), size)
            for image_path in explosion_images
        ]

    def update(self, camera_x):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]

        if self.rect.bottom > height:
            self.rect.bottom = height

        if self.rect.bottom < height and self.animation_counter >= len(self.images) - 1 and not self.finished:
            self.finished = True
            self.handle_collisions()
            self.kill()

        if self.finished and self.rect.bottom >= height:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - self.camera_x, self.rect.y))

    def handle_collisions(self):
        if self.player:
            player_rect = self.player.rect
            player_center_x = player_rect.centerx
            player_bottom = player_rect.bottom

            distance_squared = (player_center_x - self.rect.centerx) ** 2 + (player_bottom - self.rect.bottom) ** 2

            if distance_squared <= self.distance_threshold ** 2:
                if self.explosion_type == "normal":
                    self.player.health -= self.damage_amount
                    self.damage_amount = 10
                    self.kill()
                elif self.explosion_type == "nuke":
                    self.player.health -= self.damage_amount
                    self.damage_amount = 50
                    self.kill()
                elif self.explosion_type == "frozen":
                    self.player.frozen = True
                    self.player.frozen_duration = 5
                    self.kill()
                elif self.explosion_type == "poison":
                    self.player.poison = True
                    self.player.poison_duration = 5
                    self.kill()
                elif self.explosion_type == "burn":
                    self.player.burn = True
                    self.player.burn_duration = 10
                    self.kill()
                else:
                    self.player.health -= self.damage_amount
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0


class KineticWeapon(pygame.sprite.Sprite):
    def __init__(self, x, y, player, all_sprites, weapons_group):
        super().__init__()
        self.image = pygame.image.load("image/vork.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group

    def update(self, camera_x):
        # Symulacja ruchu balistycznego widła
        self.rect.y += 5  # Przykładowa prędkość opadania, dostosuj do własnych potrzeb

        # Sprawdzenie, czy widło koliduje z graczem
        if self.rect.colliderect(self.player.rect):
            # Dodaj widło do grupy sprite'ów gracza
            self.player.add_weapon(self)
            # Usuń widło z grupy sprite'ów widł
            self.weapons_group.remove(self)
            self.all_sprites.remove(self)

        # Sprawdzenie, czy widło wyleciało poza ekran, jeśli tak, usuń je
        if self.rect.y > 720:
            self.kill()


if __name__ == "__main__":
    from game_loop import GameLoop

    game_loop = GameLoop()
    game_loop.run()
