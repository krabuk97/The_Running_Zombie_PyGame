import random
import pygame
import sys
from after_death import AfterDeath
from player import Player
from gui import Gui
from load_image import LoadImage
from menu import Menu
from weapons import Bombs, Explosion, KineticWeapon, HealthPack, BombButton

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))


class BombsManager:
    def __init__(self, player, all_sprites, bombs_group, kinetic_weapons_group, background):
        self.player = player
        self.all_sprites = all_sprites
        self.bombs_group = bombs_group
        self.bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]
        self.kinetic_weapons_group = kinetic_weapons_group
        self.bomb_counts = {"rocket": 5, "nuke": 5, "regular": 5, "frozen": 5, "fire": 5, "poison": 5, "vork": 5}

        kinetic_weapon_x = random.randint(0, width)
        kinetic_weapon_y = 0
        kinetic_weapon = KineticWeapon(kinetic_weapon_x, kinetic_weapon_y, self.player, self.all_sprites, self.kinetic_weapons_group)

        self.kinetic_weapons_group.add(kinetic_weapon)
        self.all_sprites.add(kinetic_weapon)

        self.last_spawn_time = {bomb_type: 0 for bomb_type in self.bomb_types}
        self.spawn_delay = {bomb_type: 0 for bomb_type in self.bomb_types}
        self.camera_x = 0
        self.kinetic_weapon_spawn_chance = 10

    def get_bomb_count(self, bomb_type):
        return self.bomb_counts.get(bomb_type, 0)

    def spawn_bomb(self, bomb_type):
        if pygame.time.get_ticks() - self.last_spawn_time[bomb_type] >= self.spawn_delay[bomb_type]:
            bomb = Bombs(self.player, bomb_type, random.randint(0, width), 0)
            self.all_sprites.add(bomb)
            self.bombs_group.add(bomb)
            self.last_spawn_time[bomb_type] = pygame.time.get_ticks()
            self.spawn_delay[bomb_type] = random.randint(2500, 8000)

    def spawn_kinetic_weapons(self):
        if random.randint(0, 100) < self.kinetic_weapon_spawn_chance:
            kinetic_weapon_x = random.randint(0, width)
            kinetic_weapon_y = 0
            kinetic_weapon = KineticWeapon(kinetic_weapon_x, kinetic_weapon_y, self.player, self.all_sprites, self.kinetic_weapons_group)

    def update(self):
        for bomb in self.bombs_group:
            bomb.update(self.camera_x)

        self.spawn_kinetic_weapons()


class GameStateManager:
    def __init__(self, game_loop):
        self.game_loop = game_loop

    def handle_state(self):
        if self.game_loop.game_state == "menu":
            self.handle_menu_state()
        elif self.game_loop.game_state == "playing":
            self.handle_playing_state()
        elif self.game_loop.game_state == "death_animation":
            self.handle_death_animation_state()
        elif self.game_loop.game_state == "death_screen":
            self.handle_death_screen_state()

    def handle_menu_state(self):
        selected_action = self.game_loop.menu.handle_events()
        if selected_action == "start":
            self.game_loop.start_game()
            self.game_loop.game_state = "playing"
        elif selected_action == "exit":
            self.game_loop.running = False

    def handle_playing_state(self):
        self.game_loop.update_game()
        self.game_loop.draw_game()

    def handle_death_animation_state(self):
        self.game_loop.death_animation()

    def handle_death_screen_state(self):
        self.game_loop.death_screen()

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
        self.after_death_instance = AfterDeath(
            self.screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button
        )
        self.kinetic_weapons_group = pygame.sprite.Group()
        self.game_state_manager = GameStateManager(self)
        self.background1 = pygame.transform.scale(
            pygame.image.load("image/background.jpg").convert_alpha(), (1080, 720)
        )
        self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
        self.background3 = pygame.transform.scale(pygame.image.load("image/city_n.jpeg").convert_alpha(), (1080, 720))
        self.background4 = pygame.transform.scale(pygame.image.load("image/pr_n.jpeg").convert_alpha(), (1080, 720))
        self.background5 = pygame.transform.scale(pygame.image.load("image/wolf.jpg").convert_alpha(), (1080, 720))
        self.background6 = pygame.transform.scale(pygame.image.load("image/nuke_map.jpg").convert_alpha(), (1080, 720))
        self.background7 = pygame.transform.scale(pygame.image.load("image/swamp.jpeg").convert_alpha(), (1080, 720))
        self.bombs_manager = BombsManager(
            self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group, self.background1)
        self.death_animation_started = False
        self.last_health_pack_time = 0
        self.health_pack_interval = 10000
        self.running = True
        self.clock = pygame.time.Clock()
        self.camera_x = 0
        self.game_state = "menu"
        self.death_animation_duration = 5000
        self.death_animation_start_time = 3000
        self.background_changed = False
        self.score_to_change_background1 = 100
        self.time_of_death = 0
        self.health_pack_spawn_chance = 1
        self.health_pack_width = 10
        self.new_background_index = 0
        self.bomb_buttons = pygame.sprite.Group()
        bomb_button_positions = [
            (1020, 50),
            (1020, 150),
            (1020, 250),
            (1020, 350),
            (1020, 450),
            (1020, 550),
            (1020, 650),
        ]

        for i, bomb_type in enumerate(["rocket", "bomb_nuke", "bomb_reg", "frozen_bomb", "bomb_fire", "poison_bomb", "vork"]):
            if i < len(bomb_button_positions):
                image_path = f"image/{bomb_type}.png"
                bomb_button = BombButton(image_path, bomb_button_positions[i], (100, 100), self.screen, bomb_type, 0)
                self.bomb_buttons.add(bomb_button)
            else:
                print(f"Warning: Not enough positions for bomb type '{bomb_type}'")
    
    def start_game(self):
        self.player = Player()
        self.gui = Gui(self.player)
        self.bombs_group = pygame.sprite.Group()
        self.health_packs_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.game_state = "playing"
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
        self.health_pack_spawn_chance = 1
        self.health_pack_width = 10
        self.health_packs_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.last_bomb_spawn_time = pygame.time.get_ticks()
        self.bomb_spawn_delay = random.randint(2500, 4000)

    def run(self):
        while self.running:
            self.game_state_manager.handle_state()
            self.play_game()
            pygame.display.flip()
            self.clock.tick(60)

    def play_game(self):
        self.all_sprites.update(self.camera_x)
        self.bombs_manager.update()
        self.update_game()
        self.draw_game()
        self.handle_death()
        self.bomb_buttons.update()
        self.bomb_buttons.draw(self.screen)
        self.handle_clicks()

    def handle_clicks(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.bomb_buttons:
                    if button.rect.collidepoint(event.pos):
                        button.handle_click(self.bombs_manager)

        if self.player.score >= self.score_to_change_background1 and not self.background_changed:
            print("Changing Background")
            self.change_background()
            self.background_changed = True

        print("Player Score:", self.player.score)

        self.spawn_health_packs()

        self.camera_x = max(
            0,
            min(int(self.player.rect.x - (self.screen.get_width() // 2)), int(self.background1.get_width() - self.screen.get_width())),
        )

        if not self.background_changed:
            self.screen.blit(self.background1, (-self.camera_x, 0))

        if self.death_animation_started:
            self.death_animation()

        self.health_packs_group.update(self.camera_x)
        from weapons import Bombs

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        self.draw_bombs()
        self.update_kinetic_weapons(self.camera_x)
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
            self.screen.blit(self.death_screen.run(), (0, 0))
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

    def change_background(self):
        background_names = ["background1", "background2", "background3", "background4", "background5", "background6", "background7"]

        self.new_background_index = (self.new_background_index + 1) % len(background_names)

        new_background_name = background_names[self.new_background_index]

        self.current_background = getattr(LoadImage, new_background_name)

        self.player.score = 0
        self.camera_x = 0
    def update_kinetic_weapons(self, camera_x):
        self.kinetic_weapons_group.update(self.camera_x)

        collisions = pygame.sprite.spritecollide(self.player, self.kinetic_weapons_group, True)
        for kinetic_weapon in collisions:
            self.player.health -= 10
            self.player.add_weapon(kinetic_weapon)
            self.kinetic_weapons_group.remove(kinetic_weapon)

    def draw_kinetic_weapons(self):
        for kinetic_weapon in self.kinetic_weapons_group:
            kinetic_weapon.update(self.camera_x)
            self.screen.blit(kinetic_weapon.image, (kinetic_weapon.rect.x - self.camera_x, kinetic_weapon.rect.y))

    def spawn_health_packs(self):
        if random.randint(0, 100) < self.health_pack_spawn_chance:
            health_pack_x = random.randint(0, self.screen.get_width() - self.health_pack_width)
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
        self.all_sprites.update(self.camera_x)
        self.player.update(self.camera_x)
        self.bombs_group.update(self.camera_x)
        self.health_packs_group.update(self.camera_x)
        
        for button in self.bomb_buttons:
            button.bomb_count = self.bombs_manager.get_bomb_count(button.bomb_type)

    def handle_clicks(self):
        for button in self.bomb_buttons:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                button.handle_click(self.bombs_manager)

    def draw_game(self):
        self.screen.blit(self.background1, (-self.camera_x, 0))

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)
            self.screen.blit(bomb.image, (bomb.rect.x - self.camera_x, bomb.rect.y))

        for health_pack in self.health_packs_group:
            health_pack.draw(self.screen)

        for button in self.bomb_buttons:
            button.draw()

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
        after_death = AfterDeath(
            self.screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button
        )
        selected_action = after_death.run()
        if selected_action == "restart":
            self.start_game()
        elif selected_action == "exit":
            self.running = False


if __name__ == "__main__":
    game_loop = GameLoop()
    game_loop.run()
