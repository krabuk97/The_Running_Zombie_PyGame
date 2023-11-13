import pygame
import random
import sys
from pygame.locals import *
from LoadImage import LoadImage
from gui import Gui
from afterdeath import AfterDeath
from menu import Menu

pygame.init()

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Ładowanie i skalowanie obrazów
        self.walk_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (100, 100))
                            for filename in LoadImage.playerwalk]
        self.death_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (100, 100))
                             for filename in LoadImage.playerdie]
        self.playerstand_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (100, 100))
                                   for filename in LoadImage.playerstand]

        self.image_index = 0
        self.image = self.walk_images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (width // -10, height - 2)

        # Atrybuty gracza
        self.speed = 1.5
        self.jump_power = 15
        self.jump_velocity = 0
        self.is_jumping = False
        self.animation_delay = 5
        self.animation_counter = 0
        self.facing_left = False
        self.health = 100
        self.heart = 3
        self.is_dying = False
        self.idle_timer = 0
        self.idle_animation_delay = 50
        self.damage = 10
        self.health_bar_full = LoadImage.healthbar.copy()
        self.health_bar_width = self.health_bar_full.get_width()
        self.invincible = False
        self.frozen = False
        self.burn = False
        self.poison = False
        self.frozen_duration = 0
        self.slow_duration = 0
        self.burn_duration = 0
        self.poison_duration = 0
        self.poison_counter = 0

    def update(self, camera_x):
        keys = pygame.key.get_pressed()
        any_key_pressed = any(keys)

        if not self.is_dying:
            self.handle_movement(keys)
            self.handle_jumping(keys)
            self.animate_idle() if not any_key_pressed and not self.is_jumping else self.animate()

        self.update_attributes()

    def handle_movement(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_left = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_left = False

    def handle_jumping(self, keys):
        if keys[pygame.K_SPACE]:
            if not self.is_jumping:
                self.is_jumping = True
                self.jump_velocity = self.jump_power

        if self.is_jumping:
            self.jump_velocity -= 1
            self.rect.y -= self.jump_velocity

            if self.rect.y >= height - self.rect.height:
                self.is_jumping = False
        elif self.rect.y < height - self.rect.height:
            self.jump_velocity -= 1
            self.rect.y -= self.jump_velocity

    def update_attributes(self):
        # Inne aktualizacje atrybutów gracza
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))

        if self.health < 0:
            self.health = 0

        if self.invincible:
            self.health = 20000

        if self.rect.bottom > height:
            self.rect.bottom = height

        if self.frozen:
            self.handle_frozen()

        if self.poison:
            self.handle_poison()

        if self.burn:
            self.handle_burn()

        if self.slow_duration > 0:
            self.speed = 0.5
            self.slow_duration -= 1
        else:
            self.speed = 1.5

        if self.health <= 0:
            self.is_dying = True

    def handle_frozen(self):
        self.frozen_duration += 1
        if self.frozen_duration >= 180:
            self.frozen_duration = 0
            self.frozen = False

    def handle_poison(self):
        self.poison_counter += 1
        if self.poison_counter >= 180:
            self.poison_counter = 0
            self.poison = False

    def handle_burn(self):
        self.burn_duration += 1
        if self.burn_duration >= 180:
            self.burn_duration = 0
            self.burn = False

    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
            self.animation_counter = 0
            self.image_index = (self.image_index + 1) % len(self.walk_images)
            self.image = self.walk_images[self.image_index]

            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)

    def animate_idle(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
            self.animation_counter = 0
            self.image_index = (self.image_index + 1) % len(self.playerstand_images)
            self.image = self.playerstand_images[self.image_index]

            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)

    def animate_death(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
            self.animation_counter = 0
            self.image_index = (self.image_index + 1) % len(self.death_images)
            self.image = self.death_images[self.image_index]

            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

menu_instance = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button, LoadImage.restart_button)

while True:
    selected_action = menu_instance.handle_events()
    if selected_action == "start":
        break
    menu_instance.draw()
    pygame.display.flip()

menu_instance = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button, LoadImage.restart_button)
player = Player()
gui = Gui(player)

# Set the game icon and background
pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (width, height))
death_screen = pygame.transform.scale(LoadImage.death_screen, (width, height))

# Create sprite groups
bombs_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class Bombs(pygame.sprite.Sprite):
    def __init__(self, player, bomb_type, x, y):
        super().__init__()

        if bomb_type == "nuke":
            self.image = pygame.image.load("image/bomb_nuke.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        elif bomb_type == "regular":
            self.image = pygame.image.load("image/bomb_reg.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        elif bomb_type == "frozen":
            self.image = pygame.image.load("image/frozen_bomb.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        elif bomb_type == "fire":
            self.image = pygame.image.load("image/bomb_fire.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        elif bomb_type == "poison":
            self.image = pygame.image.load("image/poison_bomb.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 5)
        self.player = player
        self.bomb_type = random.choice(["regular", "nuke", "frozen", "poison", "burn"])
        self.explosion_type = None

    def create_explosion(self, explosion_type):
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type)
        explosion_group.add(explosion)

    def update(self, camera_x):
        self.rect.y += self.speed
        if self.rect.top > height + 10 or self.rect.left < -25 or self.rect.right > width + 20:
            self.rect.x = random.randint(0, width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(1, 5)
            self.bomb_type = random.choice(["regular", "nuke", "frozen", "poison", "burn"])

        # Always create an explosion when a bomb updates
        self.create_explosion(self.explosion_type)

        if pygame.sprite.spritecollide(self.player, bombs_group, True):
            if self.bomb_type == "regular":
                self.explosion_type = "normal"
            elif self.bomb_type == "nuke":
                self.explosion_type = "nuke"
            elif self.bomb_type == "frozen":
                self.explosion_type = "frozen"
            elif self.bomb_type == "poison":
                self.explosion_type = "poison"
            elif self.bomb_type == "fire":
                self.explosion_type = "burn"

            self.create_explosion(self.explosion_type)

    def explode(self):
        explosion_type = "nuke" if self.bomb_type == "nuke" else "normal"
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type)
        explosion_group.add(explosion)

        if self.bomb_type == "regular":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "normal")
            explosion_group.add(explosion)

        if self.bomb_type == "frozen":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "frozen")
            explosion_group.add(explosion)

        if self.bomb_type == "fire":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "burn")
            explosion_group.add(explosion)

        if self.bomb_type == "poison":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, "poison")
            explosion_group.add(explosion)

        self.kill()


class HealthPack(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('image/health_pack.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
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
        self.all_sprites.add(health_pack)

    def collect(self, player):
        if player.health < 100:
            player.health += 50
            if player.health > 100:
                player.health = 100
            self.take = True

    def update(self, camera_x):
        if not self.take:
            self.rect.y += self.speed

            if self.rect.bottom > height:
                self.rect.bottom = height


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

        elif explosion_type == "poison":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.poison_bomb
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 0

        elif explosion_type == "burn":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.burn
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 0

        else:
            raise ValueError(f"Unknown explosion_type: {explosion_type}")
            
            self.images = []  # You might want to provide a default value here

        self.image_index = 0

        if self.images and len(self.images) > 0:
            self.rect = self.images[0].get_rect(center=(x, y))
            self.image = self.images[self.image_index]
        else:
            self.rect = pygame.Rect(x, y, 0, 0)
            self.image = pygame.Surface((0, 0))

    def update(self, camera_x):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]

        if self.rect.bottom < height and self.animation_counter >= len(self.images) - 1 and not self.finished:
            self.finished = True
            self.handle_collisions()
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - game_loop.camera_x, self.rect.y))

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
                elif self.explotsion_type == "nuke":
                    self.player.health -= self.damage_amount
                    self.damage_amount = 50
                elif self.explosion_type == "frozen":
                    self.player.frozen = True
                    self.player.frozen_duration = 5
                elif self.explosion_type == "poison":
                    self.player.poison = True
                    self.player.poison_duration = 5
                elif self.explosion_type == "burn":
                    self.player.burn = True
                    self.player.burn_duration = 10
                else:
                    self.player.health -= self.damage_amount
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0
                    self.player.slow_start_x = self.player.rect.centerx
                    self.player.slow_start_y = self.player.rect.centery


class GameLoop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1080, 720))
        pygame.display.set_caption("The Running Zombie")
        self.player = Player()
        self.gui = Gui(self.player)
        self.menu = Menu(self.screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button,
                          LoadImage.restart_button)
        self.background1 = pygame.transform.scale(pygame.image.load("image/background.jpg").convert_alpha(), (1080, 720))
        self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
        self.background3 = pygame.transform.scale(pygame.image.load("image/city_1.jpeg").convert_alpha(), (1080, 720))
        self.background4 = pygame.transform.scale(pygame.image.load("image/city_after.png").convert_alpha(), (1080, 720))
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
        self.score_to_change_background1 = 3
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

        if current_time - self.last_health_pack_time >= self.health_pack_interval:
            if random.random() < 0.02:
                health_pack = HealthPack(random.randint(0, width - 30), 0)
                self.all_sprites.add(health_pack)
                self.health_packs_group.add(health_pack)
                self.last_health_pack_time = current_time

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

        for explosion in explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                explosion_group.add(explosion)
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

        for explosion in explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                explosion_group.add(explosion)
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
            explosion_group.add(explosion)
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
    