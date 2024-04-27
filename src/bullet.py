import pygame
from src.utils.physics import Dot, Force, Pos, Speed


class Bullet(pygame.sprite.Sprite):
    bullet_image = pygame.transform.scale(pygame.image.load("assets/images/bullet.png"), (15, 15))

    def __init__(self, screen: pygame.Surface, shooter_boat, boat_pos: Pos, speed: Speed, *groups):
        """Initialisation du boulet, qui aura une vitesse constante"""
        super().__init__(*groups)
        self.screen = screen
        self.shooter_boat = shooter_boat

        pos = Pos(boat_pos.x + 16 * speed.x / speed.get_norm(), boat_pos.y + 16 * speed.y / speed.get_norm())
        self.dot = Dot(pos, speed, 0.1)
        self.image = Bullet.bullet_image
        self.rect = Bullet.bullet_image.get_rect()
        self.rect.center = (self.dot.pos.x, self.dot.pos.y)
        self.mask = pygame.mask.from_surface(self.image)

    def run(self, time_step, camera_pos: Pos):
        """opérations à effectuer à chaque tick"""
        self.dot.run(Force(0, 0), time_step)
        self.rect.center = (self.dot.pos.x - camera_pos.x, self.dot.pos.y - camera_pos.y)

    def __str__(self):
        return str(self.__class__) + ": \n" \
               + "\tx_speed= " + str(self.dot.speed.x) + "\n" \
               + "\ty_speed= " + str(self.dot.speed.y)
