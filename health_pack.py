import pygame
import random
from player import Player



width, height = 1080, 720

screen = pygame.display.set_mode((width, height))

class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y, all_sprites):
        super().__init__()
        self.image = pygame.image.load('image/health_pack.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.take = False
        self.speed = 4
        self.all_sprites = all_sprites

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def random_health_pack(self):
        health_pack_x = random.randint(0, width - self.rect.width)
        health_pack_y = 0
        health_pack = HealthPack(health_pack_x, health_pack_y, self.all_sprites)
        self.all_sprites.add(health_pack)

    def collect(self, player):
        if player.health < 100:
            player.health += 50
            if player.health > 100:
                player.health = 100
            self.take = True

    def update(self, camera_x):
        if self.take:
            self.kill()
        else:
            self.rect.y += self.speed

            if self.rect.bottom > height:
                self.rect.bottom = height

            hits = pygame.sprite.spritecollide(self, self.all_sprites, False)
            for hit in hits:
                if not self.take and isinstance(hit, Player):
                    self.collect(hit)
