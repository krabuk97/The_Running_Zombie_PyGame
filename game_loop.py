import pygame
import sys
from after_death import AfterDeath
from player import Player, ZombieFriend
from gui import Gui
from load_image import LoadImage
from menu import Menu
from weapons import Explosion, HealthPack, BombsManager, KineticWeapon, Rocket, SelectedBomb, Bombs
from level import Level


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
        self.screen = pygame.display.set_mode((1080, 720))
        pygame.display.set_caption("The Running Zombie")
        self.selected_bomb_type = None
        self.current_level_number = 4
        self.current_level = Level(self.current_level_number, "playing")
        self.start_x = 0
        self.start_y = 0
        self.player = Player()
        self.zombie_friend = ZombieFriend()
        self.bomb_button_positions = [
            (1020, 50),
            (1020, 150),
            (1020, 250),
            (1020, 350),
            (1020, 450),
            (1020, 550),
            (1020, 650),
        ]
        bomb_types = ["rocket", "bomb_nuke", "bomb_reg", "frozen_bomb", "bomb_fire", "poison_bomb", "vork"]

        self.selected_bomb = SelectedBomb()
        self.gui = Gui(self.player, self.bomb_button_positions, bomb_types)
        self.bombs_manager = BombsManager(self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group, self.weapons_group, bomb_types)
        self.explosion_group = pygame.sprite.Group()
        self.menu = Menu(self.screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button)
        self.after_death = AfterDeath(
            self.screen, LoadImage.death_screen, LoadImage.restart_button, LoadImage.exit_button
        )
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
        self.friend_appeared = False

    def start_game(self, x, y):
        self.game_state = "playing"
        self.background_changed = False

        self.player = Player()
        self.all_sprites.empty()
        self.bombs_group.empty()
        self.health_packs_group.empty()

        self.all_sprites.add(self.player)

        self.health_pack = HealthPack(x, y, self.all_sprites)
        self.health_packs_group.add(self.health_pack)
        self.all_sprites.add(self.player, self.health_pack)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw_game()
            self.update_game(self.camera_x)
            pygame.display.flip()
            clock.tick(60)

            if not self.running:
                self.after_death.draw()
                pygame.display.flip()
                pygame.time.delay(3000)
                pygame.quit()
                sys.exit()

            if self.player.score == 100:
                self.death_screen()

            if self.should_change_level():
                self.load_level()

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.handle_bomb_placement(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                self.handle_bomb_selection(event.key)

    def handle_bomb_placement(self, mouse_x, mouse_y):
        if self.selected_bomb_type:
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

    def handle_bomb_selection(self, key):
        bomb_mapping = {
            pygame.K_0: "rocket",
            pygame.K_6: "vork",
            pygame.K_1: "nuke",
            pygame.K_2: "regular",
            pygame.K_3: "frozen",
            pygame.K_4: "fire",
            pygame.K_5: "poison",
        }

        if key in bomb_mapping:
            self.selected_bomb_type = bomb_mapping[key]

    def handle_menu_state(self):
        selected_action = self.menu.handle_events()
        if selected_action == "start":
            self.start_game()
            self.game_state = "playing"
        elif selected_action == "exit":
            self.running = False

    def handle_playing_state(self):
        if self.current_level_number in [4, 5, 6, 7] and not self.friend_appeared:
            self.zombie_friend = ZombieFriend()
            self.zombie_friend.set_target_position((width - 100, height - 100))
            self.friend_appeared = True

        self.draw_game()
        self.update_game(self.camera_x)

    def handle_death_animation_state(self):
        self.death_animation()

    def handle_death_screen_state(self):
        selected_action = self.after_death.run()
        if selected_action == "restart":
            self.restart_game()
            self.start_game()
        elif selected_action == "exit":
            self.running = False
        else:
            self.after_death.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def draw_game(self):
        current_background = self.current_level.get_current_background()
        self.screen.blit(current_background, (-self.camera_x, 0))

        self.all_sprites.draw(self.screen)

        if self.game_state == "playing":
            self.gui.draw_health_bar()
            self.gui.draw_point_score()
            self.gui.draw_bomb_buttons(self.selected_bomb_type)
            self.gui.draw_exit_button()

        for bomb in self.bombs_group:
            bomb.draw(self.screen, self.camera_x)

        for explosion in self.explosion_group:
            explosion.draw(self.screen)

        for health_pack in self.health_packs_group:
            health_pack.draw(self.screen, self.all_sprites)

        self.player.draw(self.screen)

        if self.zombie_friend:
            self.zombie_friend.draw(self.screen)
        self.gui.draw_point_score()
        self.gui.draw_bomb_buttons(self.selected_bomb_type)

    def update_game(self, camera_x):
        self.current_level.update_background()

        if self.current_background:
            self.camera_x = max(
                0,
                min(int(self.player.rect.x - (self.screen.get_width() // 2)),
                    int(self.current_background.get_width() - self.screen.get_width())),
            )

        if self.player.is_dying and not self.background_changed:
            print("Changing Background")
            self.current_level.update_background()
            self.background_changed = True

        self.all_sprites.update(self.camera_x)

        self.health_packs_group.update(self.camera_x)

        self.bombs_group.update(self.camera_x)

        self.bombs_manager.update()

        self.handle_death()

        if self.zombie_friend:
            self.zombie_friend.update(camera_x)
            self.all_sprites.add(self.zombie_friend)

        self.health_packs_group.update(self.camera_x)

        if self.health_pack and self.health_pack.has_changed_position:
            health_pack_position = (self.health_pack.rect.x, self.health_pack.rect.y)
            self.player.set_target_position(health_pack_position)

        for bomb in self.bombs_group:
            bomb.update(self.camera_x)
            if bomb.rect.colliderect(self.player.rect):
                explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, self.player, bomb.bomb_type)
                self.explosion_group.add(explosion)

        for explosion in self.explosion_group:
            explosion.update(self.camera_x)

        self.player.update(self.camera_x)

        if self.death_animation_started:
            self.death_animation()

        self.all_sprites.update(self.camera_x)
        self.gui.draw_health_bar()
        self.gui.draw_point_score()
        self.all_sprites.draw(self.screen)

        if self.player.score == 100:
            self.death_screen()

        if self.should_change_level():
            self.load_level()

        pygame.display.flip()
        self.clock.tick(60)

    def load_level(self):
        if self.zombie_friend:
            self.zombie_friend.rect.bottomleft = (width // + 10, height - 10)
            self.zombie_friend.set_target_position((width - 100, height - 100))

        self.current_level_number += 1
        self.background_changed = False
        self.current_background_index = 0
        self.update_background()

        pygame.display.flip()
        pygame.time.delay(2000)
    def setup_zombie_friend(self):
        self.zombie_friend = ZombieFriend()

        if self.zombie_friend:
            self.zombie_friend.rect.bottomleft = (width // + 10, height - 2)
            self.zombie_friend.set_target_position((width - 100, height - 100))

    def setup_zombie_friend(self):
        self.zombie_friend = ZombieFriend()

        if self.zombie_friend:
            self.zombie_friend.rect.bottomleft = (width // + 10, height - 2)
            self.zombie_friend.set_target_position((width - 100, height - 100))

    def update_background(self):
        if self.game_state == "death_screen" and not self.background_changed:
            self.current_level.update_background()
            print(f"Changed background to {self.current_background_index}")
            self.background_changed = True
        else:
            self.background_changed = False

    def should_change_level(self):
        return self.player.is_dying

    def restart_game(self):
        self.background_changed = False
        self.player.rect.x = 50
        self.player.rect.y = height - 100
        self.all_sprites.empty()
        self.bombs_group.empty()
        self.health_packs_group.empty()

        self.all_sprites.add(self.player)
        self.health_pack = HealthPack(self.all_sprites, self.player)
        self.health_packs_group.add(self.health_pack)
        self.all_sprites.add(self.health_pack)

        self.bombs_manager = BombsManager(
            self.player, self.all_sprites, self.bombs_group, self.kinetic_weapons_group,
            self.current_level.get_current_background(),
            self.kinetic_weapons_group
        )

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
            self.player.animate_death()
    
    def death_screen(self):
        selected_action = self.after_death.run()
        if selected_action == "restart":
            self.start_game()
        elif selected_action == "exit":
            self.running = False
        else:
            self.after_death.draw()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    player = Player()
    game_loop = GameLoop()
    game_loop.run()
