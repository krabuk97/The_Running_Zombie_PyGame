import random
import pygame
from load_image import LoadImage
from gui import Gui
from menu import Menu
from player import Player
import math

pygame.init()

width, height = 1080, 720

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

gui = Gui(player)


class BombButton(pygame.sprite.Sprite):
    def __init__(self, image_path, position, size, screen, bomb_type, bomb_count):
        super().__init__()
        original_size = size
        size = (original_size[0] // 2, original_size[1] // 2)

        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), size)
        self.rect = self.image.get_rect(topleft=position)
        self.screen = screen
        self.bomb_type = bomb_type
        self.bomb_count = bomb_count

    def draw(self):
        self.screen.blit(self.image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text = font.render(str(self.bomb_count), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)

    def handle_click(self, bombs_manager):
        if self.bomb_count > 0:
            bombs_manager.spawn_bomb(self.bomb_type)
            self.bomb_count -= 1


        class Bombs(pygame.sprite.Sprite):
            def __init__(self, player, bomb_type, x, y):
                super().__init__()

                self.player = player
                self.bomb_type = bomb_type
                self.explosion_type = None
                self.exploded = False

                self.load_bomb_image()

                self.image = pygame.transform.scale(self.image, (60, 60))
                self.rect = self.image.get_rect()
                self.reset_bomb()

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
                        self.exploded = True
                        self.explode()
                        self.kill()

                    if self.rect.bottom > height:
                        self.rect.bottom = height

            def draw(self, camera_x):
                screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))

            def reset_bomb(self):
                self.rect.x = random.randint(0, width - self.rect.width)
                self.rect.y = random.randint(-100, -40)
                self.speed = random.randint(1, 5)

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
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 5
        elif self.explosion_type == "nuke":
            explosion_images = LoadImage.nuke
            size = (300, 300)
            self.distance_threshold = 250
            self.damage_amount = 50
        elif self.explosion_type == "frozen":
            explosion_images = LoadImage.frozen_bomb
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "poison":
            explosion_images = LoadImage.poison_bomb
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        elif self.explosion_type == "burn" or self.explosion_type == "fire":
            explosion_images = LoadImage.burn
            size = (150, 150)
            self.distance_threshold = 90
            self.damage_amount = 0
        else:
            raise ValueError(f"Unknown explosion_type: {self.explosion_type}")

        original_images = [
            pygame.image.load(image_path).convert_alpha()
            for image_path in explosion_images
        ]

        # Skalowanie z utrzymaniem proporcji
        self.images = [
            pygame.transform.smoothscale(img, target_size)
            for img in original_images
        ]
    
    def update(self, camera_x):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]

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
                    self.player.health -= self.damage_amount
                    self.damage_amount = 10
                    self.kill()
                elif self.explosion_type == "nuke":
                    self.player.health -= self.damage_amount
                    self.damage_amount = 50
                    self.kill()
                elif self.explosion_type == "frozen":
                    self.player.frozen = True
                    self.player.frozen_duration = 5
                    self.kill()
                elif self.explosion_type == "poison":
                    self.player.poison = True
                    self.player.poison_duration = 5
                    self.kill()
                elif self.explosion_type == "burn":
                    self.player.burn = True
                    self.player.burn_duration = 10
                    self.kill()
                else:
                    self.player.health -= self.damage_amount
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0

    def reset_bomb(self):
        self.animation_counter = 0
        self.finished = False


class KineticWeapon(pygame.sprite.Sprite):
    def __init__(self, x, y, player, all_sprites, weapons_group):
        super().__init__()
        self.image = pygame.image.load("image/vork.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group

    def update(self, camera_x):
        self.rect.y += 5
        self.rect.x -= camera_x
        
        if self.rect.colliderect(self.player.rect):
            self.player.add_weapon(self)
            self.weapons_group.remove(self)
            self.all_sprites.remove(self)

        if self.rect.y > 720:
            self.kill()


class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, player, all_sprites, weapons_group):
        super().__init__()
        self.original_image = pygame.image.load("image/rocket.png").convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.all_sprites = all_sprites
        self.weapons_group = weapons_group
        self.speed = 5
        self.target = player.rect
        self.explosion_radius = 50
        self.radius = 20  # Dodany atrybut promienia

    def update(self, camera_x):
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

        if self.rect.colliderect(self.target):
            self.explode()
            self.kill()

    def rotate_towards_target(self, dx, dy):
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def explode(self):
        for weapon in self.weapons_group:
            # Zmieniona funkcja collide_circle na collide_rect z promieniem
            if pygame.sprite.collide_rect(self, weapon):
                self.all_sprites.remove(self)
                self.weapons_group.remove(self)
                print("Rocket exploded!")
                

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


if __name__ == "__main__":
    from game_loop import GameLoop

    game_loop = GameLoop()
    game_loop.run()
