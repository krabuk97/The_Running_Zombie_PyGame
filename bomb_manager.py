import random
import pygame
from weapons import Bombs

width, height = 1080, 720
screen = pygame.display.set_mode((width, height))

class BombsManager:
    def __init__(self, player, all_sprites, bombs_group, kinetic_weapons_group):
        self.player = player
        self.all_sprites = all_sprites
        self.bombs_group = bombs_group
        self.bomb_types = ["regular", "nuke", "frozen", "fire", "poison"]
        self.last_spawn_time = {bomb_type: 0 for bomb_type in self.bomb_types}
        self.spawn_delay = {bomb_type: 0 for bomb_type in self.bomb_types}
        self.camera_x = 0
        self.kinetic_weapons_group = kinetic_weapons_group

    def spawn_bomb(self, bomb_type):
        if pygame.time.get_ticks() - self.last_spawn_time[bomb_type] >= self.spawn_delay[bomb_type]:
            bomb = Bombs(self.player, bomb_type, random.randint(0, width), 0)
            self.all_sprites.add(bomb)
            self.bombs_group.add(bomb)
            self.last_spawn_time[bomb_type] = pygame.time.get_ticks()
            # Dostosuj opóźnienie według potrzeb
            self.spawn_delay[bomb_type] = random.randint(2500, 8000)

    def spawn_kinetic_weapons(self):
        # Dodaj kod do losowego rzucania widłami
        if random.randint(0, 100) < self.kinetic_weapon_spawn_chance:
            kinetic_weapon_x = random.randint(0, width)
            kinetic_weapon_y = 0
            kinetic_weapon = KineticWeapon(kinetic_weapon_x, kinetic_weapon_y, self.player, "explosion_type")
            self.kinetic_weapons_group.add(kinetic_weapon)
            self.all_sprites.add(kinetic_weapon)
            
    def update(self, current_location):
        for bomb in self.bombs_group:
            bomb.update(self.camera_x, current_location)

        self.spawn_kinetic_weapons()
