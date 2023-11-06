import pygame
import random
from explosion import Explosion

width, height = 1080, 720

bombs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
    

class Bombs(pygame.sprite.Sprite):

    def __init__(self, player, bomb_type, x, y):
      super().__init__()
    
      if bomb_type == "nuke":
        self.image = pygame.image.load("image/bomb_nuke.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
      elif bomb_type == "regular":
        self.image = pygame.image.load("image/bomb_reg.png").convert_alpha()
      elif bomb_type == "frozen":
        self.image = pygame.image.load("image/frozen_bomb.png").convert_alpha()
    
      self.image = pygame.transform.scale(self.image, (60, 60))
      self.rect = self.image.get_rect()
      self.rect.centerx = x
      self.rect.top = y
      self.speed = 4
      self.exploded = False
      self.player = player
      self.bomb_type = bomb_type
    
    def update(self, camera_x):
      if not self.exploded:
        self.rect.y += self.speed
    
        if self.rect.bottom >= height:
          self.exploded = True
          self.explode()
    
        if self.rect.bottom > height:
          self.rect.bottom = height
    
    def random_bomb(self):
      bomb_x = random.randint(0, width - self.rect.width)
      bomb_y = 0
      bomb_type = "regular" if random.random() < 0.8 else "nuke" or "frozen"
      bomb = Bombs(self.player, bomb_type, bomb_x, bomb_y)
      all_sprites.add(bomb)
      bombs_group.add(bomb)
    
    def explode(self):
      explosion_type = "nuke" if self.bomb_type == "nuke" else "normal"
      explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                            explosion_type)
      all_sprites.add(explosion)
    
      if self.bomb_type == "regular":
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                              "normal")
        all_sprites.add(explosion)
    
      if self.bomb_type == "frozen":
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                              "frozen")
        all_sprites.add(explosion)
    
      self.kill()
      bombs_group.add(explosion)


class HealthPack(pygame.sprite.Sprite):

    def __init__(self, x, y):
      super().__init__()
      self.image = pygame.image.load('image/health_pack.png').convert_alpha()
      self.image = pygame.transform.scale(self.image, (60,60))
      self.rect = self.image.get_rect()
      self.rect.topleft = (x, y)
      self.take = False
      self.speed = 4

    def draw(self, screen):
      screen.blit(self.image, self.rect)

    def random_health_pack(self):
      health_pack_x = random.randint(0, width - self.rect.width)
      health_pack_y = 0
      health_pack = HealthPack(health_pack_x, health_pack_y)
      all_sprites.add(health_pack)

    def collect(self, player):
      player.health += 0.5
      if player.health > 1.0:
        player.health = 1.0
      self.kill()

    def update(self, camera_x):
      if not self.take:
        self.rect.y += self.speed

        if self.rect.bottom > height:
          self.rect.bottom = height
