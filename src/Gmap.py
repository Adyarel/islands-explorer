import time
from typing import Tuple

import numpy

from src.chunk import Chunk
from src.constants import deepsea_level, sea_level, sand_level, grass_level, color_deep_sea, color_sea, color_sand, \
    color_grass, color_dirt, chunk_block_size
from src.utils.physics import Pos
from src.utils.utils import get_starting_pos_chunk


class Gmap:
    """class to regroup the block of gmap """

    def __init__(self, seed=0):
        """DON'T CALL THE CONSTRUCTOR, call get_map_instance instead"""

        if seed == 0:
            self.seed: int = int(time.time()) % 2 ** 16
        else:
            self.seed: int = seed

        self.colors_by_height: numpy.ndarray = numpy.zeros((256, 3), dtype=numpy.uint8)
        self.create_colors()

        self.map_blocks: dict = {}

    def create_colors(self) -> None:
        # couleur unie pour les profondeurs
        for i in range(0, deepsea_level):
            self.colors_by_height[i] = color_deep_sea

        # couleur qui change graduellement proches des côtes
        a: int = deepsea_level
        b: int = int(deepsea_level + 1 / 2 * (sea_level - deepsea_level))
        c: int = sea_level
        fa: Tuple[int, int, int] = color_deep_sea
        fb: list[int, int, int] = [0, 0, 0]
        for i in range(3):
            fb[i] = color_deep_sea[i] + 1 / 2 * (color_sea[i] - color_deep_sea[i])
        fc = color_sea
        color: list[int, int, int] = [0, 0, 0]
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
        b = int(sand_level + 1 / 2 * (grass_level - sand_level))
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

    def get_map_block_colored(self, block_starting_pos: Pos) -> numpy.ndarray:
        if not block_starting_pos.get_tuple() in self.map_blocks:
            self.map_blocks[block_starting_pos.get_tuple()] = Chunk(block_starting_pos, self)
        return self.map_blocks[block_starting_pos.get_tuple()].colored_map

    def get_map_block_masked(self, block_starting_pos: Pos) -> numpy.ndarray:
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


INSTANCE: Gmap = None


def get_map_instance(seed: int = 0) -> Gmap:
    global INSTANCE
    if INSTANCE is None:
        INSTANCE = Gmap(seed)
    return INSTANCE
