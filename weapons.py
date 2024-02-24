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
all_sprites = pygame.sprite.Group()

menu = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)


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
        self.damage_amount = 0

    def load_bomb_image(self):
        if self.bomb_type == "nuke":
            self.image = pygame.image.load("image/nuke.png").convert_alpha()
        elif self.bomb_type == "regular":
            self.image = pygame.image.load("image/regular.png").convert_alpha()
        elif self.bomb_type == "frozen":
            self.image = pygame.image.load("image/frozen.png").convert_alpha()
        elif self.bomb_type == "fire":
            self.image = pygame.image.load("image/fire.png").convert_alpha()
        elif self.bomb_type == "poison":
            self.image = pygame.image.load("image/poison.png").convert_alpha()

    def update(self, camera_x):
        if not self.exploded:
            self.rect.y += self.speed

            if self.rect.bottom >= height:
                self.time_since_landing += 1
            if self.time_since_landing >= 180:
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
        from explosion import Explosion
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type, damage_amount=self.damage_amount)
        explosion_group.add(explosion)
        self.handle_explosion_collision()

        self.kill()

    def handle_explosion_collision(self):
        player_collision = pygame.sprite.spritecollide(self, [self.player], False)
        if player_collision:
            for player in player_collision:
                if player and not player.is_dying:
                    player.take_damage(self.damage_amount)


class KineticWeapon(pygame.sprite.Sprite):
    def __init__(self, player, all_sprites, weapons_group, x, y, bomb_type="vork"):
        super().__init__()
        self.original_image = pygame.image.load("image/vork.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (50, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()

        self.rect.x = 1020
        self.rect.y = random.randint(50, height // 2)

        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.bomb_type = bomb_type

        self.speed = 10
        self.gravity = 0.07
        self.vertical_speed = 0

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def update(self, camera_x):
        self.vertical_speed += self.gravity

        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.angle = math.atan2(dy, dx)

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
        self.speed = 0.5
        self.acceleration = 0.1
        self.max_speed = 5.0
        self.explosion_radius = 50
        self.radius = 20
        self.rect = self.image.get_rect(topleft=(x, y))
        self.target = None
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.bomb_type = bomb_type
        self.target_group = target_group
        self.upward_velocity = 0
        self.launch_phase = 0
        self.upward_duration = 500
        self.horizontal_duration = 100
        self.horizontal_velocity = 0

        all_sprites.add(self)
        weapons_group.add(self)

    def launch(self, player, start_x, start_y):
        self.rect.x, self.rect.y = start_x, start_y
        self.target = player.rect
        self.upward_velocity = -3
        self.launch_phase = 0

    def rotate_towards_target(self, dx, dy, scale_factor=0.5):
        if self.launch_phase == 1:
            angle = math.atan2(dy, dx)
            rotated_image = pygame.transform.rotate(self.original_image, math.degrees(angle))
            self.image = pygame.transform.scale(rotated_image, (100, 100))
            self.rect = self.image.get_rect(center=self.rect.center)
        elif self.launch_phase == 0:  # Rotate during the upward phase as well
            upward_angle = math.atan2(-self.upward_velocity, self.horizontal_velocity)
            rotated_image = pygame.transform.rotate(self.original_image, math.degrees(upward_angle))
            self.image = pygame.transform.scale(rotated_image, (100, 100))
            self.rect = self.image.get_rect(center=self.rect.center)

    def explode(self):
        print("Rocket exploded!")
        from explosion import Explosion
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player, explosion_type="normal")
        self.all_sprites.add(explosion)
        self.weapons_group.remove(self)

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

    def update(self):
        if not self.target:
            return

        dx = self.target.centerx - self.rect.centerx
        dy = self.target.centery - self.rect.centery

        distance = math.sqrt(dx ** 2 + dy ** 2)

        if self.launch_phase == 0:
            self.rect.y += self.upward_velocity
            if self.rect.y <= self.target.centery - self.upward_duration:
                self.upward_velocity = 0
                self.launch_phase = 1
                self.rotate_towards_target(dx, dy)

        elif self.launch_phase == 1:
            if distance > 0:
                dx /= distance
                dy /= distance

            self.horizontal_velocity += self.acceleration
            self.horizontal_velocity = min(self.horizontal_velocity, self.max_speed)

            dx *= self.horizontal_velocity
            dy *= self.horizontal_velocity

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