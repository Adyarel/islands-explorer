from time import time as t, sleep
import pygame

from src.utils.background import get_map_bg
from src.boat import Boat
from src.player import Player
from src.map_gen import *
from src.utils.physics import Pos, Speed


class Game:
    def __init__(self, screen_size: tuple):

        self.start_time = t()
        print("init pygame ... ")
        pygame.display.init()
        pygame.font.init()
        print("pygame initialized in", t() - self.start_time, "s")
        self.already_start = False

        # --- screen ---
        print("init screen")
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Island Explorer", "island-explorer-icon")
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))

        # --- Map ---
        print("init map")
        self.map = get_map_instance()
        print("seed:", self.map.seed)

        # --- Camera ---
        self.camera_pos = Pos(0, 0)

        # --- inputs ---
        self.key_pressed = {pygame.K_z: False,
                            pygame.K_q: False,
                            pygame.K_s: False,
                            pygame.K_d: False}

    def run(self):

        print("init game")

        # --- boats ---
        spawn_points = SpawnPoint(self.map)

        player = Player(self.screen, spawn_points.get_spawn_point_near(Pos(0, 0)), Speed(0, 0),
                        mass=10, max_power=2000, boat_image=Player.boat_1_image)

        enemy = Boat(self.screen, spawn_points.get_spawn_point_near(Pos(0, 0)), Speed(0, 0),
                     mass=10, max_power=2000, boat_image=Player.boat_2_image)

        print("given spawn points:")
        for x in spawn_points.given_spawn_points:
            print("\t", x)

        player_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()

        player_group.add(player)
        enemy_group.add(enemy)

        enemy.orientation = -0.8

        # --- start game ---

        self.camera_pos = player.dot.pos - Pos(self.screen_size[0] / 2, self.screen_size[1] / 2)

        last_frame = 0

        run = True

        while run:

            time_step = t() - last_frame
            last_frame = t()

            # --- Update map ---

            background = get_map_bg(self)
            self.screen.blit(background.image, background.rect)
            for x in player_group:
                x.run(time_step, self.camera_pos)
            for x in enemy_group:
                x.run(time_step, self.camera_pos)

            # --- print fps ---

            font = pygame.font.Font(None, 24)
            fps_value = 0
            if time_step != 0:
                fps_value = 1 / time_step
            text = font.render("FPS: " + str(int(fps_value)), 1, (255, 255, 255))
            self.screen.blit(text, (0, 0))

            # --- Move cam ---

            if player.dot.pos.x - self.camera_pos.x < self.screen_size[0] * 13 / 32:
                self.camera_pos.x = player.dot.pos.x - self.screen_size[0] * 13 / 32
            elif player.dot.pos.x - self.camera_pos.x > self.screen_size[0] * 19 / 32:
                self.camera_pos.x = player.dot.pos.x - self.screen_size[0] * 19 / 32
            if player.dot.pos.y - self.camera_pos.y < self.screen_size[1] * 7 / 18:
                self.camera_pos.y = player.dot.pos.y - self.screen_size[1] * 7 / 18
            elif player.dot.pos.y - self.camera_pos.y > self.screen_size[1] * 11 / 18:
                self.camera_pos.y = player.dot.pos.y - self.screen_size[1] * 11 / 18

            # --- Move boat ---

            if self.key_pressed[pygame.K_z] and not self.key_pressed[pygame.K_s]:
                player.set_engine_power(player.max_power)
            elif self.key_pressed[pygame.K_s] and not self.key_pressed[pygame.K_z]:
                player.set_engine_power(-player.max_power)
            else:
                player.set_engine_power(0)

            if self.key_pressed[pygame.K_q]:
                player.rotate(-1, time_step)
            if self.key_pressed[pygame.K_d]:
                player.rotate(1, time_step)

            # --- move enemies ---

            for x in enemy_group:
                if int(t() * 100) % 100 == 0:
                    bullet_group.add(x.fire(True))

            # --- move bullets ---

            for bullet in bullet_group:
                bullet.run(time_step, self.camera_pos)
                self.screen.blit(bullet.image, bullet.rect)

                if pygame.sprite.spritecollide(bullet, player_group, False):
                    if pygame.sprite.spritecollide(bullet, player_group, False, pygame.sprite.collide_mask):
                        if player_group not in pygame.sprite.Sprite.groups(bullet.shooter_boat):
                            player.take_damage(bullet.shooter_boat.bullets_damage)
                            bullet.kill()

                if pygame.sprite.spritecollide(bullet, enemy_group, False):
                    if pygame.sprite.spritecollide(bullet, enemy_group, False, pygame.sprite.collide_mask):
                        if enemy_group not in pygame.sprite.Sprite.groups(bullet.shooter_boat):
                            enemy.take_damage(bullet.shooter_boat.bullets_damage)
                            bullet.kill()

            pygame.sprite.spritecollide(background, bullet_group, True, pygame.sprite.collide_mask)

            # --- Apply update on screen ---

            pygame.display.flip()

            # --- EVENTS ---

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    self.key_pressed[event.key] = True

                if event.type == pygame.KEYUP:
                    self.key_pressed[event.key] = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        bullet_group.add(player.fire(True))
                    if event.button == pygame.BUTTON_RIGHT:
                        bullet_group.add(player.fire(False))

            # --- print time for first frame ---
            if not self.already_start:
                print("first frame after", t() - self.start_time, "s")
                self.already_start = True

            # --- block at 60fps ---
            if t() - last_frame < 1/60:
                sleep(1/60 - t() + last_frame)

        print("quit game")
        pygame.quit()
