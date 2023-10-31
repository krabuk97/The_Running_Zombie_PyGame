import pygame


width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

class Gui:
  def __init__(self, player):
      self.player = player
      self.health_bar_full = player.health_bar_full
      self.health_bar_width = self.health_bar_full.get_width()
      self.health_bar_rect = self.health_bar_full.get_rect(topleft=(50, 50))

  def calculate_health_bar_width(self):
      health_percent = max(0, self.player.health) / 100.0
      return int(health_percent * self.health_bar_width)

  def draw_health_bar(self):
      health_bar_width = self.calculate_health_bar_width()

      health_bar_cropped = pygame.Surface((health_bar_width, self.health_bar_rect.height))
      health_bar_cropped.blit(self.health_bar_full, (0, 0), (0, 0, health_bar_width, self.health_bar_rect.height))

      screen.blit(health_bar_cropped, self.health_bar_rect.topleft)