import pygame
from src.boat import Boat
from src.map_gen import Map
from src.physics import Speed, Pos


class Player(Boat):

    boat_1_image = pygame.image.load("assets/images/boat_friendly.png")
    boat_2_image = pygame.image.load("assets/images/boat_enemy.png")

    def __init__(self, screen: pygame.Surface, map_data: Map, pos: Pos, speed: Speed, mass, max_power, boat_image):
        super().__init__(screen, map_data, pos, speed, mass, max_power, boat_image)

    def run(self, time_step, camera_pos: Pos):
        if time_step < 0.2:
            super().run(time_step, camera_pos)

    def rotate(self, angle, time_step, map_data: Map):
        if time_step < 0.2:
            super().rotate(angle, time_step, map_data)
