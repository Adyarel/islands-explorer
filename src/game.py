import pygame


class Game:
    def __init__(self, screen_size: tuple):

        pygame.init()

        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Island Explorer", "island-explorer-icon")
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))

    def run(self):

        run = True

        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

        pygame.quit()
