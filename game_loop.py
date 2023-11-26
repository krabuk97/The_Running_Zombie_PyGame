import random
import pygame
import sys
from after_death import AfterDeath
from player import Player
from gui import Gui
from load_image import LoadImage
from menu import Menu
from weapons import Explosion, HealthPack, BombsManager, KineticWeapon, Rocket, SelectedBomb, Bombs
from player import player_instance


width, height = 1080, 720
screen = pygame.display.set_mode((width, height))
bomb_types = ["rocket", "nuke", "regular", "frozen", "fire", "poison", "vork"]


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
        self.gui = Gui(self.player, bomb_button_positions, bomb_types)
        self.bombs_manager = BombsManager(self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group,
                                          self.weapons_group, bomb_types)
        self.explosion_group = pygame.sprite.Group()
        self.menu = Menu(self.screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)
        self.after_death_instance = AfterDeath(
            self.screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button
        )
        self.background1 = pygame.transform.scale(
            pygame.image.load("image/background.jpg").convert_alpha(), (1080, 720)
        )
        self.background2 = pygame.transform.scale(pygame.image.load("image/farm_d.jpeg").convert_alpha(), (1080, 720))
        self.background3 = pygame.transform.scale(pygame.image.load("image/city_n.jpeg").convert_alpha(), (1080, 720))
        self.background4 = pygame.transform.scale(pygame.image.load("image/pr_n.jpeg").convert_alpha(), (1080, 720))
        self.background5 = pygame.transform.scale(pygame.image.load("image/wolf.jpg").convert_alpha(), (1080, 720))
        self.background6 = pygame.transform.scale(pygame.image.load("image/nuke_map.jpg").convert_alpha(), (1080, 720))
        self.background7 = pygame.transform.scale(pygame.image.load("image/swamp.jpeg").convert_alpha(), (1080, 720))
        self.death_animation_started = False
        self.running = True
        self.clock = pygame.time.Clock()
        self.camera_x = 0
        self.game_state = "menu"
        self.death_animation_duration = 5000
        self.death_animation_start_time = 3000
        self.current_background_index = 0
        self.score_to_change_background = 10
        self.current_background = None
        self.background_changed = False
        self.time_of_death = 0
        self.health_pack = None
        self.target_group = pygame.sprite.Group()
        self.selected_bomb_type = None

    def start_game(self):
        self.player = Player()
        self.gui = Gui(self.player, bomb_button_positions, bomb_types)
        self.bombs_group = pygame.sprite.Group()
        self.health_packs_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.health_pack = HealthPack(self.player, self.all_sprites)
        self.health_packs_group.add(self.health_pack)
        self.all_sprites.add(self.player, self.health_pack)

        self.game_state = "playing"
        self.background_changed = False

    def run(self):
        while self.running:
            self.handle_clicks()
            self.update_game()
            self.draw_game()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_clicks(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # LMB pressed
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if self.selected_bomb_type:
                    # Throw the selected bomb
                    if self.selected_bomb_type == "rocket":
                        new_rocket = Rocket(self.player, self.all_sprites, self.weapons_group, self.target_group, mouse_x, mouse_y,
                                            bomb_type="rocket", scale_factor=0.3)
                        new_rocket.launch(self.player, mouse_x, mouse_y)
                        self.bombs_group.add(new_rocket)
                    elif self.selected_bomb_type == "vork":
                        new_bomb = KineticWeapon(self.player, self.all_sprites, self.weapons_group, mouse_x, mouse_y)
                        self.bombs_group.add(new_bomb)
                    else:
                        new_bomb = Bombs(self.player, self.selected_bomb_type, (mouse_x, mouse_y))
                        self.bombs_group.add(new_bomb)

            elif event.type == pygame.KEYDOWN:
                # Handle key presses to select bomb types
                if event.key == pygame.K_0:
                    self.selected_bomb_type = "rocket"
                elif event.key == pygame.K_6:
                    self.selected_bomb_type = "vork"
                elif event.key == pygame.K_1:
                    self.selected_bomb_type = "nuke"
                elif event.key == pygame.K_2:
                    self.selected_bomb_type = "regular"
                elif event.key == pygame.K_3:
                    self.selected_bomb_type = "frozen"
                elif event.key == pygame.K_4:
                    self.selected_bomb_type = "fire"
                elif event.key == pygame.K_5:
                    self.selected_bomb_type = "poison"

    def handle_menu_state(self):
        selected_action = self.menu.handle_events()
        if selected_action == "start":
            self.start_game()
            self.game_state = "playing"
        elif selected_action == "exit":
            self.running = False

    def handle_playing_state(self):
        self.update_game()
        self.draw_game()

    def handle_death_animation_state(self):
        self.death_animation()

    def handle_death_screen_state(self):
        selected_action = self.after_death_instance.run()
        if selected_action == "restart":
            self.start_game()
        elif selected_action == "exit":
            self.running = False
        else:
            self.after_death_instance.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def update_game(self):
        self.all_sprites.update(self.camera_x)
        self.bombs_group.update(self.camera_x)
        self.bombs_manager.update()
        self.update_background()
        self.handle_death()

        if self.current_background:
            self.camera_x = max(
                0,
                min(int(self.player.rect.x - (self.screen.get_width() // 2)),
                    int(self.current_background.get_width() - self.screen.get_width())),
            )

        if self.player.score == 10 and not self.background_changed:
            print("Changing Background")
            self.update_background()
            self.background_changed = True

        self.health_packs_group.update(self.camera_x)
        if self.health_pack and self.health_pack.has_changed_position:
            health_pack_position = (self.health_pack.rect.x, self.health_pack.rect.y)
            player_instance.set_target_position(health_pack_position)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.screen, self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        player_instance.update(self.camera_x)

        if self.death_animation_started:
            self.death_animation()

        self.health_packs_group.draw(self.screen)
        self.all_sprites.update(self.camera_x)
        self.gui.draw_health_bar()
        self.gui.draw_point_score()
        self.all_sprites.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(60)

        if not self.running:
            self.after_death_instance.draw()
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

        if self.death_animation_started and self.game_state == "death_animation":
            self.death_animation_started = False
            self.game_state = "death_screen"

        if self.game_state == "death_screen":
            self.death_screen()

    def restart_game(self):
        self.player.rect.x = 50
        self.player.rect.y = height - 100
        self.all_sprites.empty()
        self.bombs_group.empty()
        self.health_packs_group.empty()

        self.bombs_manager = BombsManager(
            self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group, self.current_background,
            self.kinetic_weapons_group
        )
        self.background_changed = False

    def draw_game(self):
        self.screen.blit(self.background1, (-self.camera_x, 0))

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            bomb.draw(self.screen, self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)
            explosion.draw(self.screen)

        for health_pack in self.health_packs_group:
            health_pack.draw(self.screen, self.all_sprites)

        self.bombs_group.draw(self.screen)
        self.explosion_group.draw(self.screen)
        self.health_packs_group.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)

        player_instance.draw(screen)

        gui.draw_point_score()
        gui.draw_bomb_buttons(selected_bomb)

        pygame.display.flip()
        self.clock.tick(60)

    def update_background(self):
        if self.game_state == "death_screen" and not self.background_changed:
            backgrounds = [self.background1, self.background2, self.background3, self.background4, self.background5,
                           self.background6, self.background7]

            self.current_background_index = (self.current_background_index + 1) % len(backgrounds)
            self.current_background = backgrounds[self.current_background_index]
            print(f"Changed background to {self.current_background_index}")

            self.background_changed = True
        else:
            self.background_changed = False

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
        selected_action = self.after_death_instance.run()
        if selected_action == "restart":
            self.start_game()
        elif selected_action == "exit":
            self.running = False
        else:
            self.after_death_instance.draw()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    player = Player()
    bomb_button_positions = [
        (1020, 50),
        (1020, 150),
        (1020, 250),
        (1020, 350),
        (1020, 450),
        (1020, 550),
        (1020, 650),
    ]
    bomb_types = ["rocket", "bomb_nuke", "bomb_reg", "frozen_bomb", "bomb_fire", "poison_bomb", "vork"]

    selected_bomb = SelectedBomb()
    gui = Gui(player, bomb_button_positions, bomb_types)

    game_loop = GameLoop()
    game_loop.run()
