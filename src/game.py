import datetime
import time

import numpy
import pygame
from src.map_gen import Map, Chunk
from src.physics import Pos


class Game:
    def __init__(self, screen_size: tuple):

        pygame.init()

        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        self.map = Map(128, 8)
        self.camera_pos = Pos(0, 0)
        pygame.display.set_caption("Island Explorer", "island-explorer-icon")
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))

    def run(self):

        last_frame = 0

        run = True

        while run:

            time_step = time.time() - last_frame
            last_frame = time.time()

            # --- Update map ---

            self.display_map()

            # print fps
            font = pygame.font.Font(None, 24)
            fps_value = 0
            if time_step != 0:
                fps_value = 1 / time_step
            text = font.render("FPS: " + str(int(fps_value)), 1, (255, 255, 255))
            self.screen.blit(text, (0, 0))

            # --- Apply update on screen ---

            pygame.display.flip()

            # --- EVENTS ---

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

        pygame.quit()

    def display_map(self):

        colormap = numpy.zeros((self.screen_size[0], self.screen_size[1], 3))

        for i in range(0, self.screen_size[0] - Chunk.block_size, Chunk.block_size):
            for j in range(0, self.screen_size[1] - Chunk.block_size, Chunk.block_size):
                colormap[i:i + Chunk.block_size, j:j + Chunk.block_size] = self.map.get_map_block_colored(Pos(i, j))

        image = pygame.surfarray.make_surface(colormap)
        rect = image.get_rect()
        self.screen.blit(image, rect)
