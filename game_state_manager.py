

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
      elif selected_action == "exit":
          self.game_loop.running = False

  def handle_playing_state(self):
      self.game_loop.update_game()
      self.game_loop.draw_game()

  def handle_death_animation_state(self):
      self.game_loop.death_animation()

  def handle_death_screen_state(self):
      self.game_loop.death_screen()
