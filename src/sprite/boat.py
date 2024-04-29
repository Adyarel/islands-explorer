import math

import pygame
from src.sprite.bullet import Bullet
from src.terrain.Gmap import get_map_instance
from src.utils.physics import Dot, Pos, Speed, Force
from src.constants import *


class Boat(pygame.sprite.Sprite):
    boat_bot_image = pygame.image.load("assets/images/boat_bot.png")

    def __init__(self, screen: pygame.surface.Surface,
                 pos: Pos, speed: Speed, mass: float, max_power: float = 1000,
                 boat_image: pygame.surface.Surface = boat_bot_image, *groups):
        """création du bateau, orientation en radians"""

        super().__init__(*groups)

        # boat's mechanics constants
        self.max_power: float = max_power
        self.coeff_water_friction: float = 5
        self.coeff_sand_friction: float = 3000
        self.coeff_swivel: float = 1e-3

        # boat's mechanics related
        self.engine_power: float = 0
        self.dot: Dot = Dot(pos, speed, mass)
        self.orientation: float = self.dot.speed.get_orientation()
        if self.orientation is None:
            self.orientation = 0

        # pygame's related
        self.screen: pygame.surface.Surface = screen
        self.size_image: Tuple[int, int] = (48, 16)
        self.base_image: pygame.surface.Surface = pygame.transform.scale(boat_image, self.size_image)
        self.image: pygame.surface.Surface = self.base_image
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = (self.dot.pos.x, self.dot.pos.y)
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)

        self.map_data = get_map_instance()

        # game's mechanics related
        self.max_health: float = 100
        self.health: float = self.max_health
        self.bullets_damage: float = 5
        self.bullet_speed_norm: float = 300

    def rotate(self, angle: float, time_step: float) -> None:
        """lorsque le bateau tourne, il conserve sa vitesse
        le bateau tourne moins vite lorsqu'il est à l'arrêt"""

        # bloque la rotation du bateau s'il n'est pas dans l'eau
        height_level: int = self.map_data.get_height_pixel(self.dot.pos)
        if height_level > sea_level:
            return

        speed_norm: float = self.dot.speed.get_norm()
        if speed_norm != 0:
            self.orientation += angle * time_step
        else:
            self.orientation += 0.4 * angle * time_step
        self.dot.speed.x = math.cos(self.orientation) * speed_norm * (1 - self.coeff_swivel * abs(angle))
        self.dot.speed.y = math.sin(self.orientation) * speed_norm * (1 - self.coeff_swivel * abs(angle))

    def set_engine_power(self, power: float) -> None:
        """régulateur sur la puissance afin de ne pas dépasser le max"""
        if - self.max_power <= power <= self.max_power:
            self.engine_power = power

    def run(self, time_step: float, camera_pos: Pos) -> None:
        """opérations à effectuer à chaque tick"""
        # calcul des forces en présence et application de la seconde loi de Newton
        speed_norm: float = self.dot.speed.get_norm()
        height_level: int = self.map_data.get_height_pixel(self.dot.pos)
        resultant: Force = self.calcul_resultante()

        # block the boat in the land if it goes to
        if height_level >= sea_level and speed_norm <= 20:
            self.dot.speed.x = 0
            self.dot.speed.y = 0
            resultant = Force(0, 0)

        if height_level >= sand_level:
            self.dot.speed.x *= 0.5
            self.dot.speed.y *= 0.5
            resultant = Force(0, 0)

        self.dot.run(resultant, time_step)

        if speed_norm < 5 and self.engine_power < 0:
            self.dot.speed = Speed(0, 0)

        self.image = pygame.transform.rotate(self.base_image, -self.orientation * 180 / math.pi)
        self.rect = self.image.get_rect()
        self.rect.center = (self.dot.pos.x - camera_pos.x, self.dot.pos.y - camera_pos.y)
        self.screen.blit(self.image, self.rect)
        self.display_health(camera_pos)

    def calcul_resultante(self) -> Force:
        """calcul des forces à appliquer au bateau"""
        sand_friction_force: Force = Force(0, 0)
        water_friction_force: Force = Force(0, 0)

        speed_norm: float = self.dot.speed.get_norm()
        height_level: float = self.map_data.get_height_pixel(self.dot.pos)

        # forces dépendantes de la vitesse, ainsi, pas de calcul si la vitesse est nulle donc l'orientation none
        temp_orientation: float = self.dot.speed.get_orientation()
        if temp_orientation is not None:
            if temp_orientation % math.pi != self.orientation % math.pi:
                if speed_norm > 1:
                    self.orientation = temp_orientation
            # freinage du bateau en raison des frottements de l'eau
            water_friction_force = -self.coeff_water_friction * speed_norm * Force(math.cos(temp_orientation),
                                                                                   math.sin(temp_orientation))

            # si le bateau est trop proche du sable, il s'enlisse
            coeff_resistance_sand = (height_level - sea_level) * self.coeff_sand_friction
            if coeff_resistance_sand > 0:
                sand_friction_force = -coeff_resistance_sand * Force(math.cos(temp_orientation),
                                                                     math.sin(temp_orientation))

        # force motrice
        engine_force: Force = self.engine_power * Force(math.cos(self.orientation),
                                                        math.sin(self.orientation))

        return engine_force + water_friction_force + sand_friction_force

    def fire(self, direction_left: bool) -> Bullet:
        """création d'un boulet de canon, celui-ci est renvoyé afin de constituer une liste de tous les boulets"""
        if direction_left:
            bullet_speed = self.bullet_speed_norm * Speed(math.cos(self.orientation - math.pi / 2),
                                                          math.sin(self.orientation - math.pi / 2))
        else:
            bullet_speed = self.bullet_speed_norm * Speed(math.cos(self.orientation + math.pi / 2),
                                                          math.sin(self.orientation + math.pi / 2))
        bullet: Bullet = Bullet(self.screen, self, Pos(self.dot.pos.x, self.dot.pos.y), bullet_speed)
        return bullet

    def take_damage(self, damage_points: float) -> None:
        self.health -= damage_points
        if not self.is_still_alive():
            self.kill()

    def is_still_alive(self) -> bool:
        if self.health <= 0:
            return False
        return True

    def display_health(self, camera_pos: Pos) -> None:
        """affiche la barre de vie juste au dessus du bateau"""
        if self.alive():
            back_rect = pygame.rect.Rect(0, 0, 40, 10)
            back_rect.center = (self.dot.pos.x - camera_pos.x, self.dot.pos.y - camera_pos.y - self.rect.height / 2 - 8)
            pygame.draw.rect(self.screen, black, back_rect)

            front_rect = pygame.rect.Rect(back_rect.x + 1, back_rect.y + 1, 38 * self.health / self.max_health, 8)
            pygame.draw.rect(self.screen, green, front_rect)
