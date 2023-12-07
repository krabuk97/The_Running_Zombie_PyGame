import random
import pygame
from load_image import LoadImage
from menu import Menu
from player import Player 
from zombie_friend import ZombieFriend
from weapons import KineticWeapon, Rocket, Bombs


pygame.init()

width, height = 1080, 720
bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
player = Player()
zombie_friend = ZombieFriend()
pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (width, height))
death_screen = pygame.transform.scale(LoadImage.death_screen, (width, height))

bombs_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

menu = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)


class BombsManager:
  def __init__(self, player, all_sprites, bombs_group, kinetic_weapons_group, weapons_group, bomb_types):
      self.player = player
      self.all_sprites = all_sprites
      self.weapons_group = weapons_group
      self.bombs_group = bombs_group
      self.bomb_types = bomb_types
      self.zombie_friend = zombie_friend
      self.selected_bomb = SelectedBomb(bomb_types)
      self.weapons_group = pygame.sprite.Group()
      self.kinetic_weapons_group = pygame.sprite.Group()
      self.kinetic_weapons_group = kinetic_weapons_group
      self.bomb_counts = {"rocket": 5, "nuke": 5, "regular": 5, "frozen": 5, "fire": 5, "poison": 5, "vork": 5}

      kinetic_weapon_x = 100
      kinetic_weapon_y = 0
      self.spawn_kinetic_weapons(kinetic_weapon_x, kinetic_weapon_y)
      self.kinetic_weapon_spawn_chance = 10
      self.last_spawn_time = {bomb_type: 0 for bomb_type in self.bomb_types}
      self.spawn_delay = {bomb_type: 0 for bomb_type in self.bomb_types}
      self.camera_x = 0
      self.kinetic_weapon_spawn_chance = 10
      self.selected_bomb_type = None
      self.is_bomb_selected = False
      self.mouse_position = (0, 0)

  def update_mouse_position(self, mouse_pos):
      self.mouse_position = mouse_pos

  def select_bomb(self, bomb_type):
      self.selected_bomb_type = bomb_type
      self.is_bomb_selected = True

  def get_selected_bomb(self):
      return self.selected_bomb.get_selected_bomb()

  def get_bomb_count(self, bomb_type):
      return self.bomb_counts.get(bomb_type, 0)

  def spawn_bomb(self, bomb_type, mouse_position):
      x, y = mouse_position
      if bomb_type == "vork":
          self.spawn_kinetic_weapons(x, y)
      else:
          if pygame.time.get_ticks() - self.last_spawn_time[bomb_type] >= self.spawn_delay[bomb_type]:
              if bomb_type == "rocket":
                  self.spawn_rocket(x, y)
              else:
                  bomb = Bombs(self.player, bomb_type, mouse_position)
                  self.all_sprites.add(bomb)
                  self.bombs_group.add(bomb)
              self.last_spawn_time[bomb_type] = pygame.time.get_ticks()

  def spawn_kinetic_weapons(self, x, y):
      if self.selected_bomb.get_selected_bomb() == "vork":
          kinetic_weapon = KineticWeapon(self.player, self.all_sprites, self.weapons_group, x, y)
          self.kinetic_weapons_group.add(kinetic_weapon)
          self.all_sprites.add(kinetic_weapon)

  def spawn_rocket(self, x, y):
      rocket = Rocket(self.player, self.all_sprites, self.weapons_group, x, y)
      rocket.launch(self.player)
      self.all_sprites.add(rocket)
      self.weapons_group.add(rocket)

  def update(self):
      for bomb in self.bombs_group:
          bomb.update(self.camera_x)

      if self.is_bomb_selected:
          if self.selected_bomb_type == "rocket":
              x, y = self.mouse_position
              self.spawn_rocket(x, y)
          elif self.selected_bomb_type == "vork":
              x = random.randint(0, 1080)
              y = random.randint(0, 720)
              self.spawn_kinetic_weapons(x, y)
          else:
              x, y = self.mouse_position
              self.spawn_bomb(self.selected_bomb_type, (x, y))

          self.is_bomb_selected = False

      if self.zombie_friend:
          zombie_hit = pygame.sprite.spritecollide(self.zombie_friend, self.bombs_group, False)
          for bomb in zombie_hit:
              bomb.handle_explosion_collision()


class SelectedBomb:
  def __init__(self, bomb_type=None):
      self.bomb_type = bomb_type

  def select_bomb(self, bomb_type):
      self.bomb_type = bomb_type

  def get_selected_bomb(self):
      return self.bomb_type