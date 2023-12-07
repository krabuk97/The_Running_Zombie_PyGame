import pygame
import random
from player import Player

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))

health_packs_group = pygame.sprite.Group()

class HealthPack(pygame.sprite.Sprite):
    max_health_packs = 5

    def __init__(self, x, y, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.image = pygame.image.load('image/health_pack.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.take = False
        self.speed = 4
        self.spawn_interval = 5000
        self.spawn_timer = random.randint(0, self.spawn_interval)
        self.has_changed_position = False
        self.player = Player()
        self.current_health_packs = 0
        self.all_sprites = all_sprites

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def random_health_pack(self, camera_x):
        if self.spawn_timer <= 0 and self.current_health_packs < self.max_health_packs:
            x = random.randint(50, width - 50) + camera_x
            y = 0
            health_pack = HealthPack(x, y, self.all_sprites)
            self.all_sprites.add(health_pack)
            self.current_health_packs += 1
            self.spawn_timer = self.spawn_interval

    def collect(self, player):
        if player.health < 100:
            player.health += 50
            if player.health > 100:
                player.health = 100
            self.take = True
            self.current_health_packs -= 1

    def update(self, camera_x):
        self.random_health_pack(camera_x)

        if self.take:
            self.kill()
        else:
            self.rect.y += self.speed

            if self.rect.bottom > height:
                self.kill()

            hits = pygame.sprite.spritecollide(self, self.all_sprites, False)
            for hit in hits:
                if not self.take and isinstance(hit, Player):
                    self.collect(hit)

        self.spawn_timer -= pygame.time.get_ticks() % self.spawn_interval

        if self.has_changed_position:
            health_pack_position = (self.rect.x, self.rect.y)
            self.player.target_position
          
first_health_pack = HealthPack(random.randint(50, width - 50), 0, health_packs_group)
health_packs_group.add(first_health_pack)
