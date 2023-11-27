import random
import pygame
from load_image import LoadImage
from menu import Menu
from player import Player
import math

pygame.init()

width, height = 1080, 720
bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
player = Player()
pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (width, height))
death_screen = pygame.transform.scale(LoadImage.death_screen, (width, height))

bombs_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

menu_instance = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)


class BombsManager:
    def __init__(self, player, all_sprites, bombs_group, kinetic_weapons_group, weapons_group, bomb_types):
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.bombs_group = bombs_group
        self.bomb_types = bomb_types
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


class SelectedBomb:
    def __init__(self, bomb_type=None):
        self.bomb_type = bomb_type

    def select_bomb(self, bomb_type):
        self.bomb_type = bomb_type

    def get_selected_bomb(self):
        return self.bomb_type


class Bombs(pygame.sprite.Sprite):
    def __init__(self, player, bomb_type, mouse_position):
        super().__init__()

        self.player = player
        self.bomb_type = bomb_type
        self.explosion_type = None
        self.exploded = False
        self.image = pygame.Surface((1, 1))
        self.load_bomb_image()
        self.speed = 10
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.mouse_position = mouse_position
        x, y = self.mouse_position
        self.reset_bomb(start_x=x, start_y=0, speed=2)
        self.time_since_landing = 0

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

    def update(self, camera_x):
        if not self.exploded:
            self.rect.y += self.speed

            if self.rect.bottom >= height:
                self.time_since_landing += 1

            if self.time_since_landing >= 300:
                self.exploded = True
                self.explode()

            if self.rect.bottom > height:
                self.rect.bottom = height

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def reset_bomb(self, start_x, start_y, speed):
        self.rect.x = start_x
        self.rect.y = start_y
        self.speed = speed
        self.exploded = False

    def explode(self):
        explosion_type = "nuke" if self.bomb_type == "nuke" else "normal"

        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type)
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
        target_size = None

        if self.explosion_type == "normal" or self.explosion_type == "regular":
            explosion_images = LoadImage.explosion_files
            target_size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 5
        elif self.explosion_type == "rocket":
            explosion_images = LoadImage.explosion_files
            target_size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 5
        elif self.explosion_type == "nuke":
            explosion_images = LoadImage.nuke
            target_size = (300, 300)
            self.distance_threshold = 250
            self.damage_amount = 50
        elif self.explosion_type == "frozen":
            explosion_images = LoadImage.frozen_bomb
            target_size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "poison":
            explosion_images = LoadImage.poison_bomb
            target_size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "burn" or self.explosion_type == "fire":
            explosion_images = LoadImage.burn
            target_size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "vork":
            if hasattr(LoadImage, "vork_explosion"):
                explosion_images = LoadImage.vork_explosion
                target_size = (150, 150)
                self.distance_threshold = 0
                self.damage_amount = 0
            else:
                return
        else:
            raise ValueError(f"Unknown explosion_type: {self.explosion_type}")

        original_images = [
            pygame.image.load(image_path).convert_alpha()
            for image_path in explosion_images
        ]

        self.images = [
            pygame.transform.smoothscale(img, target_size)
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
                if self.explosion_type == "normal":
                    self.damage_amount = 10
                elif self.explosion_type == "nuke":
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
                elif self.explosion_type == "rocket":
                    self.damage_amount = 10
                else:
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0

                self.player.health -= self.damage_amount
                self.kill()

    def reset_bomb(self):
        self.animation_counter = 0
        self.finished = False


class KineticWeapon(pygame.sprite.Sprite):
    def __init__(self, player, all_sprites, weapons_group, x, y, bomb_type="vork"):
        super().__init__()
        self.original_image = pygame.image.load("image/vork.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (50, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()

        self.rect.x = 1020
        self.rect.y = random.randint(50, 720)

        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.bomb_type = bomb_type

        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        self.angle = math.atan2(dy, dx)

        self.speed = 5
        self.gravity = 0.1
        self.vertical_speed = 0

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def update(self, camera_x):
        self.vertical_speed += self.gravity  # Apply gravity
        dx = self.speed * math.cos(self.angle)
        dy = self.vertical_speed

        self.rect.x += dx
        self.rect.y += dy

        if self.rect.y > height - self.rect.height:
            self.rect.y = height - self.rect.height
            self.vertical_speed = 0

        rotated_image = pygame.transform.rotate(self.original_image, math.degrees(self.angle))
        self.rect = rotated_image.get_rect(center=self.rect.center)
        self.image = rotated_image

        if self.rect.colliderect(self.player.rect):
            self.player.health -= 10
            self.kill()

        if self.rect.y == height - self.rect.height:
            self.speed = 0


class Rocket(pygame.sprite.Sprite):
    def __init__(self, player, all_sprites, weapons_group, target_group, x, y, bomb_type="rocket", scale_factor=0.3):
        super().__init__()
        self.original_image = pygame.image.load("image/rocket.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (100, 100))
        self.image = self.original_image.copy()
        self.speed = 1.5
        self.explosion_radius = 50
        self.radius = 20
        self.rect = self.image.get_rect(topleft=(x, y))
        self.camera_x = 0
        self.target = None
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.bomb_type = bomb_type
        self.target_group = target_group

        all_sprites.add(self)
        weapons_group.add(self)

    
    def launch(self, player, start_x, start_y):
        self.rect.x, self.rect.y = start_x, start_y
        self.target = player.rect
        dx = self.target.centerx - self.rect.centerx
        dy = self.target.centery - self.rect.centery
        self.rotate_towards_target(dx, dy)

    def rotate_towards_target(self, dx, dy, scale_factor=0.5):
        dx = self.target.centerx - self.rect.centerx
        dy = self.target.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        rotated_image = pygame.transform.rotate(self.original_image, math.degrees(angle))
        self.image = pygame.transform.scale(rotated_image, (100, 100))
        self.rect = self.image.get_rect(center=self.rect.center)

    def explode(self):
        print("Rocket exploded!")
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type="normal")
        self.all_sprites.add(explosion)
        self.weapons_group.remove(self)

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def update(self, camera_x):
        if not self.target:
            return

        dx = self.target.centerx - self.rect.centerx
        dy = self.target.centery - self.rect.centery

        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance

        dx *= self.speed
        dy *= self.speed

        self.rect.x += dx
        self.rect.y += dy

        self.rotate_towards_target(dx, dy)

        if pygame.sprite.spritecollide(self, self.target_group, False):
            print("Rocket collided with target!")
            self.explode()
            self.kill()

        if self.rect.bottom >= height and width:
            print("Rocket hit the ground!")
            self.explode()
            self.kill()


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
        self.spawn_timer = random.randint(0, self.spawn_interval)  # Randomize initial timer
        self.has_changed_position = False
        self.player_instance = Player()
        self.current_health_packs = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def random_health_pack(self):
        if self.spawn_timer <= 0 and self.current_health_packs < self.max_health_packs:
            health_pack_x = random.randint(0, width - self.rect.width)
            health_pack_y = 0
            health_pack = HealthPack(health_pack_x, health_pack_y, self.all_sprites)
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
        self.random_health_pack()

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

        self.spawn_timer -= pygame.time.get_ticks() % self.spawn_interval  # Use modulo for resetting timer

        if self.has_changed_position:
            health_pack_position = (self.rect.x, self.rect.y)
            self.player_instance.set_target_position(health_pack_position)
