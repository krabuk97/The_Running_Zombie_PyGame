import pygame
import random
from load_image import LoadImage
import math
from player import Player

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)


class ZombieFriend(Player):
    def __init__(self):
        Player.__init__(self)
        self.score = 0
        self.walk_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (200, 200))
                            for filename in LoadImage.zombie_friend_walk]
        self.death_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (200, 200))
                             for filename in LoadImage.zombie_friend_dead]
        self.playerstand_images = [pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (200, 200))
                                   for filename in LoadImage.zombie_friend_idle]

        self.image_index = 0
        self.image = self.walk_images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)
        self.speed = 5
        self.jump_power = 0
        self.is_jumping = False
        self.jump_velocity = 0
        self.animation_delay = 5
        self.animation_counter = 0
        self.facing_left = False
        self.health = 1000
        self.is_dying = False
        self.idle_timer = 0
        self.idle_animation_delay = 50
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
        self.weapons = pygame.sprite.Group()
        self.target_position = None

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        if self.health <= 0:
            self.is_dying = True
            self.animate_death()

    def update(self, camera_x, bombs_group, kinetic_weapons_group):
        keys = pygame.key.get_pressed()
        any_key_pressed = any(keys)

        if not self.is_dying:
            if not any_key_pressed and not self.is_jumping:
                self.avoid_dangers(bombs_group, kinetic_weapons_group)
            else:
                self.handle_movement()
                self.handle_jumping()

            self.animate_idle() if not any_key_pressed and not self.is_jumping else self.animate()

        self.update_attributes()
        self.weapons.update(camera_x, bombs_group, kinetic_weapons_group)

    def avoid_dangers(self, bombs_group, kinetic_weapons_group):
        nearest_danger = self.find_nearest_danger(bombs_group, kinetic_weapons_group)

        if nearest_danger:
            self.move_away_from_danger(nearest_danger)

    def find_nearest_danger(self, *danger_groups):
        nearest_danger = None
        min_distance = float('inf')

        for group in danger_groups:
            for danger in group:
                distance = math.sqrt((self.rect.centerx - danger.rect.centerx) ** 2 +
                                     (self.rect.centery - danger.rect.centery) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_danger = danger

        return nearest_danger

    def move_away_from_danger(self, danger):
        dx = danger.rect.centerx - self.rect.centerx
        dy = danger.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            dx /= distance
            dy /= distance

            new_x = self.rect.x - dx * self.speed
            new_y = self.rect.y - dy * self.speed

            self.rect.x = max(0, min(new_x, width - self.rect.width))
            self.rect.y = max(0, min(new_y, height - self.rect.height))

    def handle_movement(self):
        if self.target_position:
            target_x, target_y = self.target_position
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y

            distance = math.sqrt(dx ** 2 + dy ** 2)

            threshold_distance = 5

            if distance > threshold_distance:
                dx /= distance
                dy /= distance

                speed_factor = 1 + (distance / 100)

                speed_x = dx * self.speed * speed_factor
                speed_y = dy * self.speed * speed_factor

                self.rect.x += speed_x
                self.rect.y += speed_y

    def handle_jumping(self):
        if not self.is_jumping and random.randint(1, 100) == 1:
            self.is_jumping = True
            self.jump_velocity = self.jump_power

        if self.is_jumping:
            self.jump_velocity -= 1
            self.rect.y -= self.jump_velocity

            if self.rect.y >= height - self.rect.height:
                self.is_jumping = False
        elif self.rect.y < height - self.rect.height:
            self.jump_velocity -= 2
            self.rect.y -= self.jump_velocity

    def update_attributes(self):
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
            current_image = self.walk_images[self.image_index]
            self.image = pygame.transform.flip(current_image, self.facing_left, False)

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


zombie_friend = ZombieFriend()
