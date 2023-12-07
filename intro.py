import pygame
import imageio
import numpy as np
from PIL import Image
import pygame.mixer


width, height = 1080, 720


class Intro:
    def __init__(self, screen, intro_file_path, intro_sound_path):
        pygame.mixer.init()
        self.intro_sound = pygame.mixer.Sound(intro_sound_path)

        self.screen = screen
        self.intro_file_path = intro_file_path
        self.intro_frames = []
        self.current_frame = 0
        self.clock = pygame.time.Clock()
        self.intro_finished = False
        self.sound_played = False

        self.intro_finished_event = pygame.event.Event(pygame.USEREVENT + 1)

    def play_intro(self):
        self.load_intro()

        while not self.intro_finished:
            self.handle_events()
            self.draw_intro()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.time.delay(2000)
        self.game_state = "menu"
        self.kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.intro_finished = True

    def load_intro(self):
        with imageio.get_reader(self.intro_file_path) as reader:
            for frame in reader:
                img = Image.fromarray(frame)
                img = img.rotate(-90, expand=True)
                img = img.resize((720, 1080), Image.LANCZOS)
                frame = np.array(img)
                self.intro_frames.append(frame)

        pygame.time.delay(5000)
        self.intro_sound.play()

    def draw_intro(self):
        try:
            frame = self.intro_frames[self.current_frame]

            frame = np.fliplr(frame)

            x_offset = 0
            y_offset = 0

            frame_surface = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame_surface, (x_offset, y_offset))
            self.current_frame += 1

            if self.current_frame >= len(self.intro_frames):
                self.intro_finished = True
                pygame.event.post(self.intro_finished_event)
        except IndexError:
            self.intro_finished = True

    def kill(self):
        pygame.mixer.stop()
