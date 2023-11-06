import pygame
from LoadImage import LoadImage

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))

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
        self.player.slow_start_x_velocity = self.player.jump_velocity
        
        if explosion_type == "normal":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.explosion_files
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 5

        elif explosion_type == "nuke":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.nuke
            ]
            self.images = [
                pygame.transform.scale(image, (300, 300)) for image in self.images
            ]
            self.distance_threshold = 250
            self.damage_amount = 50

        elif explosion_type == "frozen":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.frozen_bomb
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 0

        else:
            self.images = []
        
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, camera_x):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]
            self.handle_collisions()

        if self.rect.bottom > height:
            self.rect.bottom = height

        if self.animation_counter >= len(self.images) - 1:
            if not self.finished:
                self.finished = True
                self.kill()

    def handle_collisions(self):
        if self.player:
            player_rect = self.player.rect
            player_center_x = player_rect.centerx
            player_bottom = player_rect.bottom

            if (player_center_x - self.rect.centerx) ** 2 + (
                    player_bottom - self.rect.bottom) ** 2 <= self.distance_threshold ** 2:
                if self.explosion_type == "frozen":
                    self.player.frozen = True
                    self.player.frozen_duration = 0
                else:
                    self.player.health -= self.damage_amount
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0
                    self.player.slow_start_x = self.player.rect.centerx
                    self.player.slow_start_y = self.player.rect.centery
                    self.player.slow_start_x_velocity = self.player.x_velocity
                    self.player.slow_start_y_velocity = self.player.y_velocity
                    self.player.x_velocity = 0

    def draw(self, screen, explosion_type, images):
        screen.blit(self.image, self.rect)
