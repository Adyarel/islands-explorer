import pygame
from src.boat import Boat
from src.utils.physics import Speed, Pos


class Player(Boat):

    boat_1_image: pygame.surface.Surface = pygame.image.load("assets/images/boat_friendly.png")
    boat_2_image: pygame.surface.Surface = pygame.image.load("assets/images/boat_enemy.png")

    def __init__(self, screen: pygame.Surface, pos: Pos, speed: Speed, mass: float, max_power: float, boat_image: pygame.surface.Surface):
        super().__init__(screen, pos, speed, mass, max_power, boat_image)

    def run(self, time_step: float, camera_pos: Pos) -> None:
        if time_step < 0.2:
            super().run(time_step, camera_pos)

    def rotate(self, angle: float, time_step: float) -> None:
        if time_step < 0.2:
            super().rotate(angle, time_step)
