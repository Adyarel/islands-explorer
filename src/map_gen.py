import time

import noise
import numpy

from src.constants import *
from src.utils.physics import Pos
from src.utils.utils import get_starting_pos_chunk, get_masked_by_height

INSTANCE = None


def get_map_instance(seed=0):
    global INSTANCE
    print("get_map_instance")

    if INSTANCE is None:
        print("if")
        INSTANCE = Map(seed)
    return INSTANCE


class Map:
    """class to regroup the block of map """

    def __init__(self, seed=0):
        """DON'T CALL THE CONSTRUCTOR, call get_map_instance instead"""

        if seed == 0:
            self.seed = int(time.time()) % 2 ** 16
        else:
            self.seed = seed

        self.colors_by_height = numpy.zeros((256, 3), dtype=numpy.uint8)
        self.create_colors()

        self.map_blocks = {}

    def create_colors(self):
        # couleur unie pour les profondeurs
        for i in range(0, deepsea_level):
            self.colors_by_height[i] = color_deep_sea

        # couleur qui change graduellement proches des côtes
        a = deepsea_level
        b = deepsea_level + 1 / 2 * (sea_level - deepsea_level)
        c = sea_level
        fa = color_deep_sea
        fb = [0, 0, 0]
        for i in range(3):
            fb[i] = color_deep_sea[i] + 1 / 2 * (color_sea[i] - color_deep_sea[i])
        fc = color_sea
        color = [0, 0, 0]
        for i in range(deepsea_level, sea_level):
            for j in range(3):
                color[j] = (i - b) * (i - c) / ((a - b) * (a - c)) * fa[j] + \
                           (i - a) * (i - c) / ((b - a) * (b - c)) * fb[j] + \
                           (i - a) * (i - b) / ((c - a) * (c - b)) * fc[j]
            self.colors_by_height[i] = color

        # couleur unie pour la plage
        for i in range(sea_level, sand_level):
            self.colors_by_height[i] = color_sand

        # couleur qui change graduellement pour les collines
        color = [0, 0, 0]
        a = sand_level
        b = sand_level + 1 / 2 * (grass_level - sand_level)
        c = grass_level
        fa = color_grass
        fb = [0, 0, 0]
        for i in range(3):
            fb[i] = color_grass[i] + 1 / 2 * (color_dirt[i] - color_grass[i])
        fc = color_dirt
        for i in range(sand_level, grass_level):
            for j in range(3):
                color[j] = (i - b) * (i - c) / ((a - b) * (a - c)) * fa[j] + \
                           (i - a) * (i - c) / ((b - a) * (b - c)) * fb[j] + \
                           (i - a) * (i - b) / ((c - a) * (c - b)) * fc[j]
            self.colors_by_height[i] = color

        # couleur unie pour les montagnes
        for i in range(grass_level, 256):
            self.colors_by_height[i] = color_dirt

    # --- full chunk related ---

    def get_map_block_colored(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].colored_map

    def get_map_block_masked(self, block_starting_pos: Pos) -> numpy.array:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].mask_map

    # --- pixel related ---
    def get_height_pixel(self, pos: Pos) -> int:
        starting_pos = get_starting_pos_chunk(pos)
        if not starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[starting_pos.get_tuple()] = Chunk(starting_pos, self)
        chunk = self.map_blocks[starting_pos.get_tuple()]
        return chunk.height_map[int(pos.x % chunk_block_size), int(pos.y % chunk_block_size)]

    def get_color_by_height(self, height):
        return self.colors_by_height[height]

    def is_chunk_exist(self, starting_pos: Pos):
        return starting_pos.get_tuple() in self.map_blocks


demult = 1
identity = numpy.ones((demult, demult), dtype=numpy.uint8)


class Chunk:
    """block of the gmap"""

    def __init__(self, starting_pos: Pos, gmap: Map):
        """generate terrain by block"""
        self.gmap = gmap
        self.starting_pos = starting_pos

        self.height_map = numpy.zeros((chunk_block_size, chunk_block_size), numpy.uint8)
        self.colored_map = numpy.zeros((chunk_block_size, chunk_block_size, 3), numpy.uint8)
        self.mask_map = numpy.zeros((chunk_block_size, chunk_block_size, 4), numpy.uint8)
        self.generate_terrain()

    def generate_terrain(self):

        for i in range(0, chunk_block_size, demult):
            for j in range(0, chunk_block_size, demult):
                new_i = i + self.starting_pos.x
                new_j = j + self.starting_pos.y

                height = 0.8 * noise.pnoise3(new_i / perlin_1_scale, new_j / perlin_1_scale,
                                             self.gmap.seed,
                                             octaves=perlin_1_octaves,
                                             persistence=perlin_1_persistence,
                                             lacunarity=perlin_1_lacunarity,
                                             repeatx=10000000, repeaty=10000000, base=0)
                height += 0.2 * noise.pnoise3(new_i / perlin_2_scale, new_j / perlin_2_scale,
                                              self.gmap.seed,
                                              octaves=perlin_2_octaves,
                                              persistence=perlin_2_persistence,
                                              lacunarity=perlin_2_lacunarity,
                                              repeatx=10000000, repeaty=10000000, base=0)

                self.height_map[i: i + demult, j: j + demult] = int((height + 1) * 128) * identity
        for i in range(chunk_block_size):
            for j in range(chunk_block_size):
                self.colored_map[i, j] = self.gmap.get_color_by_height(self.height_map[i, j])
                self.mask_map[i, j] = get_masked_by_height(self.height_map[i, j])
        """print("Chunk ", self.starting_pos, ": min moy max")
        print(numpy.min(self.height_map))
        print(numpy.sum(self.height_map) / Chunk.block_size ** 2)
        print(numpy.max(self.height_map))"""

    def __str__(self):
        return "Chunk: " + str(self.starting_pos)


class SpawnPoint:
    """donne un endroit de spawn pour les bateaux"""

    def __init__(self, gmap: Map):
        self.map = gmap
        self.given_spawn_points = []

    def get_spawn_point_near(self, pos: Pos) -> Pos:
        """obtention d'un point de spawn au hasard"""
        found = False
        actual_pos = pos - Pos(100, 0)
        while not found or actual_pos in self.given_spawn_points:
            c_actual_pos = actual_pos.x + 1j * actual_pos.y
            c_actual_pos *= 1 + 0.5j
            actual_pos = Pos(c_actual_pos.real, c_actual_pos.imag)
            if self.map.get_height_pixel(actual_pos) + sand_level < 2 * sea_level:
                found = True
        self.given_spawn_points.append(actual_pos)
        return actual_pos
