import pygame
from load_image import LoadImage
from bomb_manager import BombsManager

pygame.init()

width, height = 1080, 720
bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]

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
all_sprites = pygame.sprite.Group()
kinetic_weapons_group = pygame.sprite.Group()
weapons_group = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    TARGET_SIZE = (150, 150)

    def __init__(self, x, y, player, explosion_type, damage_amount=0):
        super().__init__()

        self.player = player
        self.damage_amount = damage_amount
        self.all_sprites = all_sprites
        self.bombs_group = bombs_group
        self.kinetic_weapons_group = kinetic_weapons_group
        self.weapons_group = weapons_group
        self.bomb_types = bomb_types
        self.bombs_manager = BombsManager(self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group,
                                          self.weapons_group, self.bomb_types)
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
        if self.explosion_type == "normal" or self.explosion_type == "regular" or self.explosion_type == "rocket":
            explosion_images = LoadImage.explosion_files
            self.distance_threshold = 90
            self.damage_amount = 10 if self.explosion_type == "normal" else 50
        elif self.explosion_type == "nuke":
            explosion_images = LoadImage.nuke
            self.distance_threshold = 250
            self.damage_amount = 50
        elif self.explosion_type == "frozen":
            explosion_images = LoadImage.frozen_bomb
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "poison":
            explosion_images = LoadImage.poison_bomb
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "burn" or self.explosion_type == "fire":
            explosion_images = LoadImage.burn
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "vork" and hasattr(LoadImage, "vork_explosion"):
            explosion_images = LoadImage.vork_explosion
            self.distance_threshold = 0
            self.damage_amount = 0
        else:
            print(f"Unknown explosion_type: {self.explosion_type}")
            return

        original_images = [
            pygame.image.load(image_path).convert_alpha()
            for image_path in explosion_images
        ]

        self.images = [
            pygame.transform.smoothscale(img, Explosion.TARGET_SIZE)
            for img in original_images
        ]

    def update(self, camera_x):
        self.camera_x = camera_x
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]

        self.rect.x = self.rect.x - self.camera_x

        if self.rect.bottom > height:
            self.rect.bottom = height
            self.kill()

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

            distance_squared = (player_center_x - self.rect.centerx) ** 2 + (
                    player_bottom - self.rect.bottom) ** 2

            if distance_squared <= self.distance_threshold ** 2:
                self.handle_player_collision()

            bombs_hit = pygame.sprite.spritecollide(self, self.bombs_group, False)
            for bomb in bombs_hit:
                if bomb != self:
                    bomb.handle_explosion_collision()

    def handle_player_collision(self):
        if self.explosion_type == "frozen":
            self.player.frozen = True
            self.player.frozen_duration = 5
        elif self.explosion_type == "poison":
            self.player.poison = True
            self.player.poison_duration = 5
        elif self.explosion_type == "burn":
            self.player.burn = True
            self.player.burn_duration = 10
        elif self.explosion_type == "vork":
            self.player.slow_duration = 420
            self.player.slow_start_time = pygame.time.get_ticks()
            self.player.slow_counter = 0

        self.player.health -= self.damage_amount
        self.kill()

    def handle_explosion_collision(self):
        self.kill()

    def reset_bomb(self):
        self.animation_counter = 0
        self.finished = False
