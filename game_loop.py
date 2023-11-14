import random
import pygame
import sys
from player import Player
from gui import Gui
from load_image import LoadImage
from menu import Menu
from health_pack import HealthPack
from main import Bombs, Explosion


width, height = 1080, 720

screen = pygame.display.set_mode((width, height))

class GameLoop:
  def __init__(self):
      pygame.init()
      self.player = Player()
      self.screen = pygame.display.set_mode((1080, 720))
      pygame.display.set_caption("The Running Zombie")
      self.gui = Gui(self.player)
      self.explosion_group = pygame.sprite.Group()
      self.menu = Menu(self.screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)
      self.background1 = pygame.transform.scale(pygame.image.load("image/background.jpg").convert_alpha(),
                                                (1080, 720))
      self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
      self.background3 = pygame.transform.scale(pygame.image.load("image/city_1.jpeg").convert_alpha(), (1080, 720))
      self.background4 = pygame.transform.scale(pygame.image.load("image/city_after.png").convert_alpha(),
                                                (1080, 720))
      self.background5 = pygame.transform.scale(pygame.image.load("image/city_n.jpeg").convert_alpha(), (1080, 720))
      self.background6 = pygame.transform.scale(pygame.image.load("image/farm_1.jpeg").convert_alpha(), (1080, 720))
      self.background7 = pygame.transform.scale(pygame.image.load("image/house.png").convert_alpha(), (1080, 720))
      self.background8 = pygame.transform.scale(pygame.image.load("image/pr_n.jpeg").convert_alpha(), (1080, 720))
      self.background9 = pygame.transform.scale(pygame.image.load("image/forest.jpg").convert_alpha(), (1080, 720))
      self.background10 = pygame.transform.scale(pygame.image.load("image/wolf.jpg").convert_alpha(), (1080, 720))
      self.background11 = pygame.transform.scale(pygame.image.load("image/nuke_map.jpg").convert_alpha(), (1080, 720))
      self.bombs_group = pygame.sprite.Group()
      self.all_sprites = pygame.sprite.Group()
      self.health_packs_group = pygame.sprite.Group()
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

  def start_game(self):
      self.player = Player()
      self.gui = Gui(self.player)
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

          if self.game_state == "menu":
              selected_action = self.menu.handle_events()
              if selected_action == "start":
                  self.start_game()
              elif selected_action == "exit":
                  self.running = False
          elif self.game_state == "playing":
              self.play_game()
          elif self.game_state == "death_animation":
              self.death_animation()
          elif self.game_state == "death_screen":
              self.death_screen()

  def change_background(self):
      backgrounds = [self.background1, self.background2, self.background3, self.background4, self.background5,
                     self.background6, self.background7, self.background8, self.background9, self.background10,
                     self.background11]

      self.background_changed = False

      current_background_index = backgrounds.index(self.background1)
      new_background_index = (current_background_index + 1) % len(backgrounds)
      self.background1 = backgrounds[new_background_index]
      for i in range(1, len(backgrounds)):
          index = (new_background_index + i) % len(backgrounds)
          setattr(self, f'background{i + 1}', backgrounds[index])

      self.camera_x = 0

  def play_game(self):
      self.update_game()
      self.draw_game()
      current_time = pygame.time.get_ticks()

      if self.player.score % 10 == 0 and self.player.score > 0 and not self.background_changed:
          self.change_background()
          self.background_changed = True
      elif self.player.score % 10 != 0:
          self.background_changed = False

      if self.player.score == self.score_to_change_background1:
          self.screen.blit(self.background3, (-self.camera_x, 0))

      if random.randint(0, 100) < self.health_pack_spawn_chance:
          health_pack_x = random.randint(0, width - self.health_pack_width)
          health_pack_y = 0
          health_pack = HealthPack(health_pack_x, health_pack_y, self.all_sprites)  # Pass self.all_sprites
          self.health_packs_group.add(health_pack)
          self.all_sprites.add(health_pack)

      if self.player.health <= 0:
          self.player.is_dying = True
          self.time_of_death = pygame.time.get_ticks()

      for health_pack in self.health_packs_group:
          health_pack.update(self.camera_x)
          if health_pack.rect.top > height:
              health_pack.kill()

      collected_health_packs = pygame.sprite.spritecollide(self.player, self.health_packs_group, True)
      for health_pack in collected_health_packs:
          health_pack.collect(self.player)

      if not self.death_animation_started:
          if pygame.time.get_ticks() - self.last_bomb_spawn_time >= self.bomb_spawn_delay:
              bomb_regular = Bombs(self.player, "regular", random.randint(0, width), 0)
              self.all_sprites.add(bomb_regular)
              self.bombs_group.add(bomb_regular)
              self.last_bomb_spawn_time = pygame.time.get_ticks()
              self.bomb_spawn_delay = random.randint(2500, 4000)

      if pygame.time.get_ticks() - self.last_nuke_spawn_time >= self.nuke_spawn_delay:
          bomb_nuke = Bombs(self.player, "nuke", random.randint(0, width), 0)
          self.all_sprites.add(bomb_nuke)
          self.bombs_group.add(bomb_nuke)
          self.last_nuke_spawn_time = pygame.time.get_ticks()
          self.nuke_spawn_delay = random.randint(4000, 7000)

      if pygame.time.get_ticks() - self.last_frozen_spawn_time >= self.frozen_spawn_delay:
          bomb_frozen = Bombs(self.player, "frozen", random.randint(0, width), 0)
          self.all_sprites.add(bomb_frozen)
          self.bombs_group.add(bomb_frozen)
          self.last_frozen_spawn_time = pygame.time.get_ticks()
          self.frozen_spawn_delay = random.randint(5000, 8000)

      if pygame.time.get_ticks() - self.last_fire_spawn_time >= self.fire_spawn_delay:
          bomb_fire = Bombs(self.player, "fire", random.randint(0, width), 0)
          self.all_sprites.add(bomb_fire)
          self.bombs_group.add(bomb_fire)
          self.last_fire_spawn_time = pygame.time.get_ticks()
          self.fire_spawn_delay = random.randint(5000, 8000)

      if pygame.time.get_ticks() - self.last_poison_spawn_time >= self.poison_spawn_delay:
          bomb_poison = Bombs(self.player, "poison", random.randint(0, width), 0)
          self.all_sprites.add(bomb_poison)
          self.bombs_group.add(bomb_poison)
          self.last_poison_spawn_time = pygame.time.get_ticks()
          self.poison_spawn_delay = random.randint(5000, 8000)

      self.camera_x = max(
          0,
          min(int(self.player.rect.x - (width // 2)),
              int(self.background1.get_width() - width))
      )
      self.screen.blit(self.background1, (-self.camera_x, 0))

      if self.death_animation_started:
          if pygame.time.get_ticks() - self.death_animation_start_time >= self.death_animation_duration:
              self.running = False

      self.health_packs_group.update(self.camera_x)

      for explosion in self.explosion_group:
          explosion.update(self.camera_x)
          explosion.draw(self.screen)

      for bomb in self.bombs_group:
          bomb.update(self.camera_x)
          if bomb.rect.colliderect(self.player.rect):
              explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
              self.explosion_group.add(explosion)
          self.screen.blit(bomb.image, (bomb.rect.x - self.camera_x, bomb.rect.y))

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
          self.screen.blit(death_screen, (0, 0))
          pygame.display.flip()
          pygame.time.delay(3000)
          pygame.quit()
          sys.exit()

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
