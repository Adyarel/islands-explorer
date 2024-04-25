import time
import numpy
import pygame

from src.boat import Boat
from src.utils import make_surface_rgba
from src.player import Player
from src.map_gen import *
from src.physics import Pos, Speed


class Game:
    def __init__(self, screen_size: tuple):

        pygame.init()

        # --- screen ---
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Island Explorer", "island-explorer-icon")
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))

        # --- Map ---
        self.map = Map(135, 8)

        # --- Camera ---
        self.camera_pos = Pos(0, 0)
        self.camera_moving_speed = 50  # pixels /s

        # --- inputs ---
        self.key_pressed = {pygame.K_z: False,
                            pygame.K_q: False,
                            pygame.K_s: False,
                            pygame.K_d: False,
                            pygame.K_o: False,
                            pygame.K_k: False,
                            pygame.K_l: False,
                            pygame.K_m: False,
                            }

    def run(self):

        # --- boats ---
        spawnpoints = SpawnPoint(self.map)

        player = Player(self.screen, spawnpoints.get_spawn_point_near(Pos(0, 0)), Speed(0, 0),
                        mass=10, max_power=2000, boat_image=Player.boat_1_image)

        enemy = Boat(self.screen, spawnpoints.get_spawn_point_near(Pos(0, 0)), Speed(0, 0),
                     mass=10, max_power=2000, boat_image=Player.boat_2_image)

        player_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()

        player_group.add(player)
        enemy_group.add(enemy)

        # --- start game ---

        self.camera_pos = player.dot.pos - Pos(self.screen_size[0] / 2, self.screen_size[1] / 2)

        last_frame = 0

        run = True

        while run:

            time_step = time.time() - last_frame
            last_frame = time.time()

            # --- Update map ---

            background = self.get_map_bg()
            self.screen.blit(background.image, background.rect)
            for x in player_group:
                x.run(time_step, self.map, self.camera_pos)
            for x in enemy_group:
                x.run(time_step, self.map, self.camera_pos)
            # print fps

            font = pygame.font.Font(None, 24)
            fps_value = 0
            if time_step != 0:
                fps_value = 1 / time_step
            text = font.render("FPS: " + str(int(fps_value)), 1, (255, 255, 255))
            self.screen.blit(text, (0, 0))

            # --- Move cam ---

            if self.key_pressed[pygame.K_o]:
                self.camera_pos.y -= self.camera_moving_speed * time_step
            if self.key_pressed[pygame.K_k]:
                self.camera_pos.x -= self.camera_moving_speed * time_step
            if self.key_pressed[pygame.K_l]:
                self.camera_pos.y += self.camera_moving_speed * time_step
            if self.key_pressed[pygame.K_m]:
                self.camera_pos.x += self.camera_moving_speed * time_step

            # --- Move boat ---

            if self.key_pressed[pygame.K_z] and not self.key_pressed[pygame.K_s]:
                player.set_engine_power(player.max_power)
            elif self.key_pressed[pygame.K_s] and not self.key_pressed[pygame.K_z]:
                player.set_engine_power(-player.max_power)
            else:
                player.set_engine_power(0)
            print(player.engine_power)

            if self.key_pressed[pygame.K_q]:
                player.rotate(-1, time_step, self.map)
            if self.key_pressed[pygame.K_d]:
                player.rotate(1, time_step, self.map)

            # --- move bullets ---

            for bullet in bullet_group:
                bullet.run(time_step, self.camera_pos)
                self.screen.blit(bullet.image, bullet.rect)

                if pygame.sprite.spritecollide(bullet, player_group, False):
                    if pygame.sprite.spritecollide(bullet, player_group, False, pygame.sprite.collide_mask):
                        player.take_damage(bullet.shooter_boat.bullets_damage)
                        bullet.kill()

                if pygame.sprite.spritecollide(bullet, enemy_group, False):
                    if pygame.sprite.spritecollide(bullet, enemy_group, False, pygame.sprite.collide_mask):
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

        pygame.quit()

    def get_map_bg(self):

        cbs = Chunk.block_size
        cam_pos = Pos(int(self.camera_pos.x), int(self.camera_pos.y))

        # first, get the chunk we need to draw bg
        chunks_needed = []
        i = 0
        while ((cam_pos.x + cbs * i) // cbs) * cbs < cam_pos.x + self.screen_size[0]:
            chunks_needed.append([])
            j = 0
            while ((cam_pos.y + cbs * j) // cbs) * cbs < cam_pos.y + self.screen_size[1]:
                chunks_needed[i] += [Pos(((cam_pos.x + cbs * i) // cbs) * cbs,
                                         ((cam_pos.y + cbs * j) // cbs) * cbs)]
                j += 1
            i += 1

        # then, make a huge map made of the chunks

        bigcolormap = numpy.zeros((len(chunks_needed) * cbs, len(chunks_needed[0]) * cbs, 3), numpy.uint8)
        bigmaskmap = numpy.zeros((len(chunks_needed) * cbs, len(chunks_needed[0]) * cbs, 4), numpy.uint8)

        for i in range(len(chunks_needed)):
            for j in range(len(chunks_needed[i])):
                bigcolormap[i * cbs: (i + 1) * cbs, j * cbs: (j + 1) * cbs] = \
                    self.map.get_map_block_colored(chunks_needed[i][j])
                bigmaskmap[i * cbs: (i + 1) * cbs, j * cbs: (j + 1) * cbs] = \
                    self.map.get_map_block_masked(chunks_needed[i][j])

        # finally, reduce to the screen size

        colormap = bigcolormap[cam_pos.x % cbs: cam_pos.x % cbs + self.screen_size[0],
                   cam_pos.y % cbs: cam_pos.y % cbs + self.screen_size[1]]
        maskmap = bigmaskmap[cam_pos.x % cbs: cam_pos.x % cbs + self.screen_size[0],
                  cam_pos.y % cbs: cam_pos.y % cbs + self.screen_size[1]]

        image = pygame.surfarray.make_surface(colormap)
        mask = pygame.mask.from_surface(make_surface_rgba(maskmap))
        rect = image.get_rect()
        return BackGround(image, mask, rect)


class BackGround(pygame.sprite.Sprite):

    def __init__(self, image, mask, rect):
        self.image = image
        self.mask = mask
        self.rect = rect
