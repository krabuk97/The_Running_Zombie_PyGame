import random
import pygame
import sys
from after_death import AfterDeath
from player import Player
from gui import Gui
from load_image import LoadImage
from menu import Menu
from weapons import Explosion, HealthPack, BombButton, BombsManager, SelectedBomb


width, height = 1080, 720
screen = pygame.display.set_mode((width, height))
bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]



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
        self.kinetic_weapons_group = pygame.sprite.Group()
        self.weapons_group = pygame.sprite.Group()
        self.health_packs_group = pygame.sprite.Group()
        self.player = Player()
        self.screen = pygame.display.set_mode((1080, 720))
        pygame.display.set_caption("The Running Zombie")
        self.gui = Gui(self.player)
        self.bombs_manager = BombsManager(self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group, self.weapons_group, bomb_types)
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
            self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group, self.background1, self.kinetic_weapons_group
        )
        self.death_animation_started = False
        self.last_health_pack_time = 0
        self.health_pack_interval = 10000
        self.running = True
        self.clock = pygame.time.Clock()
        self.camera_x = 0
        self.game_state = "menu"
        self.death_animation_duration = 5000
        self.death_animation_start_time = 3000
        self.new_background_index = 0
        self.current_background_index = 0
        self.score_to_change_background = 10
        self.current_background = None
        self.background_changed = False
        self.time_of_death = 0
        self.health_pack_spawn_chance = 1
        self.health_pack_width = 10
        self.new_background_index = 0
        bomb_buttons = pygame.sprite.Group()
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

        selected_bomb = SelectedBomb()

    def start_game(self):
        self.player = Player()
        self.gui = Gui(self.player)
        self.bombs_group = pygame.sprite.Group()
        self.health_packs_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.game_state = "playing"
        self.health_pack_spawn_chance = 1
        self.health_pack_width = 10
        self.health_packs_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

    def run(self):
        while self.running:
            self.handle_clicks()
            self.spawn_health_packs()
            self.update_game()
            self.draw_game()
            self.game_state_manager.handle_state()
            pygame.display.flip()
            self.clock.tick(60)

    def update_game(self):
        self.all_sprites.update(self.camera_x)
        self.bombs_manager.update()
        self.update_background()
        self.handle_death()
        self.bomb_buttons.update()
        self.camera_x = max(
            0,
            min(int(self.player.rect.x - (self.screen.get_width() // 2)),
                int(self.background1.get_width() - self.screen.get_width())),
        )

        if self.player.score % 10 == 0 and not self.background_changed:
            print("Changing Background")
            self.update_background()
            self.background_changed = True

        self.health_packs_group.update(self.camera_x)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.screen, self.camera_x)

            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        self.draw_bombs()

        self.draw_kinetic_weapons()
        self.update_kinetic_weapons(self.camera_x)

        if self.death_animation_started:
            self.death_animation()

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
            self.screen.blit(self.after_death_instance.run(), (0, 0))
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

    def draw_game(self):
        self.screen.blit(self.background1, (-self.camera_x, 0))

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.screen, self.camera_x)

            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for health_pack in self.health_packs_group:
            health_pack.draw(self.screen)

        for button in self.bomb_buttons:
            button.draw(self.screen)

        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)

        self.gui.draw_health_bar()
        self.gui.draw_point_score(self.screen)

        pygame.display.flip()
        self.clock.tick(60)

    def handle_clicks(self):
        self.handle_mouse_clicks()
        self.spawn_health_packs()
        self.handle_death()

    def handle_mouse_clicks(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.bomb_buttons:
                    if button.rect.collidepoint(event.pos):
                        button.handle_click(self.bombs_manager)

        selected_bomb_type = self.bombs_manager.get_selected_bomb()
        if selected_bomb_type:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.bombs_manager.spawn_bomb(selected_bomb_type, x=mouse_x, y=mouse_y)

    def update_background(self):
        if self.game_state == "death_screen" and not self.background_changed:
            backgrounds = [self.background1, self.background2, self.background3, self.background4, self.background5,
                           self.background6, self.background7]

            self.current_background_index = (self.current_background_index + 1) % len(backgrounds)
            self.current_background = backgrounds[self.current_background_index]
            print(f"Changed background to {self.current_background_index}")

            # Reset the flag to indicate that the background has been updated
            self.background_changed = True
        else:
            # Reset the flag to indicate that the background doesn't need to be updated
            self.background_changed = False
            
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

    def handle_death(self):
        if self.player.health <= 0:
            self.player.is_dying = True
            self.time_of_death = pygame.time.get_ticks()

        if self.player.is_dying and not self.death_animation_started:
            self.death_animation_started = True
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
