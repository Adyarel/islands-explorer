import pygame
from src.utils.physics import Dot, Force, Pos, Speed


class Bullet(pygame.sprite.Sprite):
    bullet_image = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (15, 15))

    def __init__(self, screen: pygame.surface.Surface, shooter_boat, boat_pos: Pos, speed: Speed, *groups):
        """Initialisation du boulet, qui aura une vitesse constante"""
        super().__init__(*groups)
        self.screen: pygame.surface.Surface = screen
        self.shooter_boat = shooter_boat

        pos: Pos = Pos(boat_pos.x + 16 * speed.x / speed.get_norm(), boat_pos.y + 16 * speed.y / speed.get_norm())
        self.dot = Dot(pos, speed, 0.1)
        self.image: pygame.surface.Surface = Bullet.bullet_image
        self.rect: pygame.rect.Rect = Bullet.bullet_image.get_rect()
        self.rect.center = (self.dot.pos.x, self.dot.pos.y)
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)

    def run(self, time_step, camera_pos: Pos) -> None:
        """opérations à effectuer à chaque tick"""
        self.dot.run(Force(0, 0), time_step)
        try:
            self.rect.center = (self.dot.pos.x - camera_pos.x, self.dot.pos.y - camera_pos.y)
        except TypeError as exception:
            print(exception, "\n", exception.args)

    def __str__(self) -> str:
        return str(self.__class__) + ": \n" \
               + "\tx_speed= " + str(self.dot.speed.x) + "\n" \
               + "\ty_speed= " + str(self.dot.speed.y)
