import random
import pygame
import sys
from after_death import AfterDeath
from player import Player
from gui import Gui
from load_image import LoadImage
from menu import Menu
from health_pack import HealthPack
from main import Bombs, Explosion
from after_death import AfterDeath
from bomb_manager import BombsManager
from game_state_manager import GameStateManager
from main import KineticWeapon


width, height = 1080, 720

screen = pygame.display.set_mode((width, height))

class GameLoop:
    def __init__(self):
      pygame.init()
      self.all_sprites = pygame.sprite.Group()
      self.bombs_group = pygame.sprite.Group()
      self.health_packs_group = pygame.sprite.Group()
      self.player = Player()
      self.screen = pygame.display.set_mode((1080, 720))
      pygame.display.set_caption("The Running Zombie")
      self.gui = Gui(self.player)
      self.explosion_group = pygame.sprite.Group()
      self.menu = Menu(self.screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)
      self.after_death_instance = AfterDeath(screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button, current_location=self.current_location)
      self.bombs_manager = BombsManager(self.player, self.all_sprites, self.bombs_group)
      self.game_state_manager = GameStateManager(self)
      self.background1 = pygame.transform.scale(pygame.image.load("image/background.jpg").convert_alpha(),
                                                (1080, 720))
      self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
      self.background3 = pygame.transform.scale(pygame.image.load("image/city_n.jpeg").convert_alpha(), (1080, 720))
      self.background4 = pygame.transform.scale(pygame.image.load("image/pr_n.jpeg").convert_alpha(), (1080, 720))
      self.background5 = pygame.transform.scale(pygame.image.load("image/wolf.jpg").convert_alpha(), (1080, 720))
      self.background6 = pygame.transform.scale(pygame.image.load("image/nuke_map.jpg").convert_alpha(), (1080, 720))
      self.background7 = pygame.transform.scale(pygame.image.load("image/swamp.jpeg").convert_alpha(), (1080, 720))
      
      self.death_animation_started = False
      self.last_health_pack_time = 0
      self.health_pack_interval = 10000
      self.running = True
      self.clock = pygame.time.Clock()
      self.camera_x = 0
      self.death_animation_duration = 5000
      self.death_animation_start_time = 3000
      self.background_changed = False
      self.score_to_change_background1 = 10
      self.start_game()
      self.time_of_death = 0
      self.current_location = None
      self.kinetic_weapons_group = pygame.sprite.Group()
    
    def start_game(self):
      self.player = Player()
      self.gui = Gui(self.player)
      self.death_screen = self.after_death_instance
      self.bombs_group = pygame.sprite.Group()
      self.health_packs_group = pygame.sprite.Group()
      self.all_sprites = pygame.sprite.Group()
      self.all_sprites.add(self.player)
      self.last_bomb_spawn_time = pygame.time.get_ticks()
      self.bomb_spawn_delay = random.randint(2500, 4000)
      self.last_nuke_spawn_time = pygame.time.get_ticks()
      self.nuke_spawn_delay = random.randint(4000, 7000)
      self.last_frozen_spawn_time = pygame.time.get_ticks()
      self.frozen_spawn_delay = random.randint(4000, 7000)
      self.last_fire_spawn_time = pygame.time.get_ticks()
      self.fire_spawn_delay = random.randint(4000, 7000)
      self.last_poison_spawn_time = pygame.time.get_ticks()
      self.poison_spawn_delay = random.randint(4000, 7000)
      self.game_state = "playing"
      self.health_pack_spawn_chance = 1
      self.health_pack_width = 10
      self.health_packs_group = pygame.sprite.Group()
      self.all_sprites = pygame.sprite.Group()
      self.all_sprites.add(self.player)
      self.last_bomb_spawn_time = pygame.time.get_ticks()
      self.bomb_spawn_delay = random.randint(2500, 4000)
    
    def run(self):
      while self.running:
          self.handle_events()
          self.game_state_manager.handle_state()
    
    def play_game(self):
      self.update_game()
      self.draw_game()
    
      if self.player.score % 10 == 0 and self.player.score > 0 and not self.background_changed:
          self.change_background()
          self.background_changed = True
      elif self.player.score % 10 != 0:
          self.background_changed = False
    
      if self.player.score == self.score_to_change_background1:
          self.screen.blit(self.background1, (-self.camera_x, 0))
    
      self.spawn_health_packs()
    
      if not self.death_animation_started:
          self.bombs_manager.update()
    
      self.camera_x = max(
          0,
          min(int(self.player.rect.x - (width // 2)),
              int(self.background1.get_width() - width))
      )
      self.screen.blit(self.background1, (-self.camera_x, 0))
    
      if self.death_animation_started:
          self.death_animation()
    
      self.health_packs_group.update(self.camera_x)
    
      for explosion in self.explosion_group:
          explosion.update(self.camera_x)
          explosion.draw(self.screen)
    
      self.draw_bombs()
      self.update_kinetic_weapons()
      self.draw_kinetic_weapons()
    
      self.health_packs_group.draw(self.screen)
    
      self.all_sprites.update(self.camera_x)
      self.player.update(self.camera_x)
      self.gui.draw_health_bar()
      self.gui.draw_point_score(self.screen)
      self.all_sprites.draw(self.screen)
      self.player.draw(self.screen)
    
      pygame.display.flip()
      self.clock.tick(60)
    
      if not self.running:
          self.screen.blit(self.death_screen, (0, 0))
          pygame.display.flip()
          pygame.time.delay(3000)
          pygame.quit()
          sys.exit()

    def update_kinetic_weapons(self):
        self.kinetic_weapons_group.update(self.camera_x)

        collisions = pygame.sprite.spritecollide(self.player, self.kinetic_weapons_group, True)
        for kinetic_weapon in collisions:

    def draw_kinetic_weapons(self):
        for kinetic_weapon in self.kinetic_weapons_group:
            kinetic_weapon.update(self.camera_x)
            self.screen.blit(kinetic_weapon.image, (kinetic_weapon.rect.x - self.camera_x, kinetic_weapon.rect.y))
    
    def change_background(self):
          backgrounds = [self.background1, self.background2, self.background3, self.background4, self.background5,
                         self.background6, self.background7]

          self.background_changed = False

          current_background_index = backgrounds.index(self.background1)
          new_background_index = (current_background_index + 1) % len(backgrounds)
          self.background1 = backgrounds[new_background_index]
          for i in range(1, len(backgrounds)):
              index = (new_background_index + i) % len(backgrounds)
              setattr(self, f'background{i + 1}', backgrounds[index])

          self.camera_x = 0
          self.bombs_manager.current_background = f'background{new_background_index + 1}'
          self.background_changed = True
    
    def spawn_health_packs(self):
        if random.randint(0, 100) < self.health_pack_spawn_chance:
            health_pack_x = random.randint(0, width - self.health_pack_width)
            health_pack_y = 0
            health_pack = HealthPack(health_pack_x, health_pack_y, self.all_sprites)
            self.health_packs_group.add(health_pack)
            self.all_sprites.add(health_pack)
    
    def draw_bombs(self):
        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)
            
            self.screen.blit(bomb.image, (bomb.rect.x - self.camera_x, bomb.rect.y))

    def update_game(self):
      # Aktualizacja obiektów gry
      self.all_sprites.update(self.camera_x)
      self.player.update(self.camera_x)
      self.bombs_group.update(self.camera_x)
      self.health_packs_group.update(self.camera_x)
    
    def draw_game(self):
      # Rysowanie obiektów gry
      self.screen.blit(self.background1, (-self.camera_x, 0))
    
      for explosion in self.explosion_group:
          explosion.update(self.camera_x)
          explosion.draw(self.screen)
    
      for bomb in self.bombs_group:
          bomb.update(self.camera_x)
          if bomb.rect.colliderect(self.player.rect):
              explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
              self.explosion_group.add(explosion)
          self.screen.blit(bomb.image, (bomb.rect.x - self.camera_x, bomb.rect.y))
    
      for health_pack in self.health_packs_group:
          health_pack.draw(self.screen)
    
      self.all_sprites.draw(self.screen)
      self.player.draw(self.screen)
    
      self.gui.draw_health_bar()
      self.gui.draw_point_score(self.screen)
    
      pygame.display.flip()
      self.clock.tick(60)
    
    def handle_death(self):
      if self.player.health <= 0:
          self.player.is_dying = True
          self.time_of_death = pygame.time.get_ticks()
    
      if self.player.is_dying and not self.death_animation_started:
          self.death_animation_started = True
          explosion = Explosion(self.player.rect.centerx, self.player.rect.bottom, self.player, "death")
          self.explosion_group.add(explosion)
          self.game_state = "death_animation"
    
    def death_animation(self):
      current_time = pygame.time.get_ticks()
      if current_time - self.time_of_death >= self.death_animation_duration:
          self.game_state = "death_screen"
    
    def death_screen(self):
      after_death = AfterDeath(self.screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button)
      selected_action = after_death.run()
      if selected_action == "restart":
          self.start_game()
      elif selected_action == "exit":
          self.running = False
    
    def handle_events(self):
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              self.running = False
          elif event.type == pygame.KEYDOWN and self.game_state == "menu":
              self.start_game()


if __name__ == "__main__":
    game_loop = GameLoop()
    game_loop.run()
