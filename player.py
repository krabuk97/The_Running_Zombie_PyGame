import pygame
import random
from menu import Menu
from load_image import LoadImage
import math

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.score = 0
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

        self.speed = 10
        self.jump_power = 15
        self.jump_velocity = 0
        self.is_jumping = False
        self.animation_delay = 5
        self.animation_counter = 0
        self.facing_left = False
        self.health = 10
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
        self.weapons = pygame.sprite.Group()
        self.target_position = None

    def add_weapon(self, weapon):
        self.weapons.add(weapon)
    
    def update(self, camera_x):
        keys = pygame.key.get_pressed()
        any_key_pressed = any(keys)

        if not self.is_dying:
            self.handle_movement()
            self.handle_jumping()
            self.animate_idle() if not any_key_pressed and not self.is_jumping else self.animate()

        self.update_attributes()
        self.weapons.update(camera_x)

    def set_target_position(self, position):
        self.target_position = position

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

                # Zwiększenie prędkości w zależności od odległości
                speed_factor = 1 + (distance / 100)

                # Oddzielne składowe prędkości dla kierunków X i Y
                speed_x = dx * self.speed * speed_factor
                speed_y = dy * self.speed * speed_factor

                # Poruszanie postacią w kierunkach X i Y
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
            self.jump_velocity -= 1
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

        self.weapons.draw(screen)


player_instance = Player()

target_position = (500, 300)
player_instance.set_target_position(target_position)

menu_instance = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)

while True:
    selected_action = menu_instance.handle_events()
    if selected_action == "start":
        break
    menu_instance.draw()
    pygame.display.flip()
