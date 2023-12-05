import pygame
import imageio
import numpy as np
from PIL import Image

width, height = 1080, 720

class Intro:
    def __init__(self, screen, intro_file_path):
        self.screen = screen
        self.intro_file_path = intro_file_path
        self.intro_frames = []
        self.current_frame = 0
        self.clock = pygame.time.Clock()
        self.intro_finished = False

    def load_intro(self):
        self.intro_frames = []
        with imageio.get_reader(self.intro_file_path) as reader:
            for frame in reader:
                img = Image.fromarray(frame)
                img = img.rotate(-90, expand=True)
                img = img.resize((720, 1080), Image.LANCZOS)  # Use LANCZOS for antialiasing
                frame = np.array(img)
                self.intro_frames.append(frame)

    def play_intro(self):
        self.load_intro()

        while not self.intro_finished:
            self.handle_events()
            self.draw_intro()
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.intro_finished = True

    def draw_intro(self):
        try:
            frame = self.intro_frames[self.current_frame]

            # Calculate the position to center the frame on the screen
            x_offset = 20  # Adjust the horizontal offset as needed
            y_offset = 20   # Adjust the vertical offset as needed

            frame_surface = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame_surface, (x_offset, y_offset))
            self.current_frame += 1
        except IndexError:
            self.intro_finished = True
