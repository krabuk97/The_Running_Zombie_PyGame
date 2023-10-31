import pygame


class Props(pygame.sprite.Sprite):
  def __init__(self, x, y, props_type, props_direction, camera_x):
      pygame.sprite.Sprite.__init__(self) 

      if props_type == "half_car":
          self.image = pygame.image.load("image/props/half_car.png")
      elif props_type == "moon_cross":
          self.image = pygame.image.load("image/props/moon_cross.png")
          self.image = pygame.transform.flip(self.image, True, False)

      self.rect = self.image.get_rect()
      self.rect.center = (x - camera_x, y)

      self.props_type = props_type
      self.props_direction = props_direction